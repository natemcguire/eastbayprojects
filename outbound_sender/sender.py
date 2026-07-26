#!/usr/bin/env python3
"""Persistent, paused-by-default Gmail draft scheduler for East Bay Projects."""

from __future__ import annotations

import argparse
import base64
import fcntl
import html
import json
import os
import random
import sqlite3
import sys
import time
from collections import Counter
from contextlib import contextmanager
from datetime import date, datetime, time as daytime, timedelta, timezone
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses
from pathlib import Path
from typing import Iterator
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
DEFAULT_STATE = Path.home() / ".local" / "share" / "eastbayprojects" / "outbound-sender"
DEFAULT_MIGRATION = (
    Path.home()
    / ".local"
    / "share"
    / "eastbayprojects"
    / "outbound-migration"
    / "2026-07-25"
)
DEFAULT_ACCOUNT = "nate@eastbayprojects.com"
DEFAULT_TIMEZONE = "America/New_York"
FOOTER_MARKER = "data-eastbay-compliance-footer"
SCHEDULE_CAPS = (10, 15, 20)
STEADY_DAILY_CAP = 25


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime | None = None) -> str:
    return (value or utc_now()).astimezone(timezone.utc).isoformat(timespec="seconds")


def state_dir() -> Path:
    path = Path(os.environ.get("EASTBAY_OUTBOUND_STATE", DEFAULT_STATE)).expanduser()
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path, 0o700)
    return path


def migration_dir() -> Path:
    return Path(os.environ.get("EASTBAY_OUTBOUND_MIGRATION", DEFAULT_MIGRATION)).expanduser()


def db_path() -> Path:
    return state_dir() / "queue.sqlite3"


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(db_path(), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db() -> None:
    with connect() as db:
        db.executescript((ROOT / "schema.sql").read_text())
        db.execute("INSERT OR IGNORE INTO settings(key, value) VALUES ('paused', '1')")
        db.execute("INSERT OR IGNORE INTO settings(key, value) VALUES ('pause_reason', 'not prepared')")


def setting(db: sqlite3.Connection, key: str, default: str = "") -> str:
    row = db.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(db: sqlite3.Connection, key: str, value: str) -> None:
    db.execute(
        """
        INSERT INTO settings(key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )


def record_event(
    db: sqlite3.Connection,
    event_type: str,
    source_message_id: str | None = None,
    detail: str | None = None,
) -> None:
    db.execute(
        """
        INSERT INTO events(source_message_id, event_type, detail, created_at_utc)
        VALUES (?, ?, ?, ?)
        """,
        (source_message_id, event_type, detail, iso_utc()),
    )


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def parsed_addresses(*values: str | None) -> list[str]:
    fields = [value or "" for value in values]
    try:
        pairs = getaddresses(fields, strict=False)
    except TypeError:
        pairs = getaddresses(fields)
    return [address.strip().lower() for _, address in pairs if address.strip()]


def single_recipient(record: dict) -> str | None:
    addresses = parsed_addresses(record.get("to"), record.get("cc"), record.get("bcc"))
    if not addresses:
        return None
    if len(addresses) != 1:
        raise ValueError(
            f"source draft {record['source_message_id']} has {len(addresses)} recipients"
        )
    return addresses[0]


def next_weekday(value: date) -> date:
    while value.weekday() >= 5:
        value += timedelta(days=1)
    return value


def day_capacity(day_index: int) -> int:
    return SCHEDULE_CAPS[day_index] if day_index < len(SCHEDULE_CAPS) else STEADY_DAILY_CAP


def generate_schedule(
    count: int,
    start_date: date,
    timezone_name: str = DEFAULT_TIMEZONE,
) -> list[datetime]:
    """Spread messages across weekday business hours with a deterministic ramp."""
    if count < 0:
        raise ValueError("count must be non-negative")
    zone = ZoneInfo(timezone_name)
    current = next_weekday(start_date)
    remaining = count
    day_index = 0
    scheduled: list[datetime] = []
    while remaining:
        today_count = min(day_capacity(day_index), remaining)
        start_minute = 9 * 60 + 30
        end_minute = 15 * 60 + 30
        span = end_minute - start_minute
        rng = random.Random(f"eastbay:{current.isoformat()}:{today_count}")
        minutes: list[int] = []
        for index in range(today_count):
            midpoint = start_minute + int((index + 0.5) * span / today_count)
            jitter = rng.randint(-3, 3)
            minutes.append(max(start_minute, min(end_minute, midpoint + jitter)))
        for minute in sorted(set(minutes)):
            local = datetime.combine(
                current,
                daytime(hour=minute // 60, minute=minute % 60),
                tzinfo=zone,
            )
            scheduled.append(local.astimezone(timezone.utc))
        if len(minutes) != len(set(minutes)):
            raise RuntimeError("schedule generated duplicate minute slots")
        remaining -= today_count
        day_index += 1
        current = next_weekday(current + timedelta(days=1))
    return scheduled


def migration_records() -> tuple[list[dict], dict[str, dict]]:
    base = migration_dir()
    source = read_jsonl(base / "source_drafts.jsonl")
    progress_rows = read_jsonl(base / "recreate_progress.jsonl")
    progress = {row["source_message_id"]: row for row in progress_rows}
    if len(source) != 400 or len(progress) != 400:
        raise RuntimeError(
            f"expected 400 captured and recreated drafts; found {len(source)} and {len(progress)}"
        )
    return source, progress


def plan_queue(start: date, timezone_name: str) -> dict:
    init_db()
    source, progress = migration_records()
    ready: list[tuple[dict, dict, str]] = []
    skipped: list[tuple[dict, dict]] = []
    seen_recipients: set[str] = set()
    for record in source:
        mapping = progress[record["source_message_id"]]
        recipient = single_recipient(record)
        if recipient is None:
            skipped.append((record, mapping))
            continue
        if recipient in seen_recipients:
            raise RuntimeError(f"duplicate recipient in migration capture: {recipient}")
        seen_recipients.add(recipient)
        ready.append((record, mapping, recipient))

    rng = random.Random("eastbay-outbound-2026-07")
    rng.shuffle(ready)
    slots = generate_schedule(len(ready), start, timezone_name)
    stamp = iso_utc()
    with connect() as db:
        sent = db.execute("SELECT COUNT(*) FROM queue WHERE status = 'sent'").fetchone()[0]
        if sent:
            raise RuntimeError("refusing to re-plan after messages have been sent")
        existing = {
            row["source_message_id"]: row
            for row in db.execute("SELECT * FROM queue").fetchall()
        }
        db.execute("DELETE FROM events")
        db.execute("DELETE FROM queue")
        for (record, mapping, recipient), slot in zip(ready, slots, strict=True):
            prior = existing.get(record["source_message_id"])
            draft_id = prior["draft_id"] if prior else mapping["new_draft_id"]
            message_id = prior["message_id"] if prior else mapping["new_message_id"]
            prepared = prior["prepared"] if prior else 0
            status = "pending" if prepared else "blocked"
            db.execute(
                """
                INSERT INTO queue(
                    source_message_id, draft_id, message_id, recipient, scheduled_at_utc,
                    status, prepared, attempts, created_at_utc, updated_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (
                    record["source_message_id"],
                    draft_id,
                    message_id,
                    recipient,
                    iso_utc(slot),
                    status,
                    prepared,
                    stamp,
                    stamp,
                ),
            )
        for record, mapping in skipped:
            db.execute(
                """
                INSERT INTO queue(
                    source_message_id, draft_id, message_id, recipient, scheduled_at_utc,
                    status, prepared, attempts, last_error, created_at_utc, updated_at_utc
                ) VALUES (?, ?, ?, NULL, NULL, 'skipped', 0, 0, ?, ?, ?)
                """,
                (
                    record["source_message_id"],
                    mapping["new_draft_id"],
                    mapping["new_message_id"],
                    "missing recipient",
                    stamp,
                    stamp,
                ),
            )
        set_setting(db, "paused", "1")
        prepared_count = db.execute(
            "SELECT COUNT(*) FROM queue WHERE recipient IS NOT NULL AND prepared = 1"
        ).fetchone()[0]
        if prepared_count == len(ready):
            set_setting(db, "pause_reason", "replanned; awaiting explicit resume")
        else:
            set_setting(db, "pause_reason", "compliance footer not prepared")
            set_setting(db, "prepared_at_utc", "")
        set_setting(db, "timezone", timezone_name)
        set_setting(db, "start_date", start.isoformat())
        set_setting(db, "planned_at_utc", stamp)
        record_event(db, "queue_planned", detail=f"ready={len(ready)} skipped={len(skipped)}")
    return {
        "planned": len(ready),
        "skipped": len(skipped),
        "start": iso_utc(slots[0]) if slots else None,
        "finish": iso_utc(slots[-1]) if slots else None,
        "paused": True,
    }


def credentials_path(account: str) -> Path:
    configured = os.environ.get("EASTBAY_OUTBOUND_CREDENTIALS")
    if configured:
        return Path(configured).expanduser()
    return (
        Path.home()
        / ".config"
        / "natebot"
        / "workspace-mcp-credentials"
        / f"{account}.json"
    )


def gmail_service(account: str):
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError as error:
        raise RuntimeError(
            "Google API dependencies are missing; run through scripts/run-outbound-sender.sh"
        ) from error
    path = credentials_path(account)
    if not path.is_file():
        raise RuntimeError(f"missing Gmail credentials: {path}")
    credentials = Credentials.from_authorized_user_file(str(path))
    return build("gmail", "v1", credentials=credentials, cache_discovery=False)


def decode_raw(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * ((4 - len(value) % 4) % 4))


def encode_raw(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def footer_text(postal_address: str) -> str:
    return (
        "This is a business solicitation from East Bay Projects.\n"
        f"East Bay Projects · {postal_address}\n"
        'To opt out of future emails, reply "unsubscribe".'
    )


def footer_html(postal_address: str) -> str:
    return (
        f'<div {FOOTER_MARKER}="1" style="margin-top:24px;color:#666;font-size:12px;'
        'line-height:1.45">'
        "This is a business solicitation from East Bay Projects.<br>"
        f"East Bay Projects &middot; {html.escape(postal_address)}<br>"
        'To opt out of future emails, reply &ldquo;unsubscribe&rdquo;.'
        "</div>"
    )


def add_compliance_footer(raw: bytes, postal_address: str, account: str) -> bytes:
    if len(postal_address.strip()) < 8:
        raise ValueError("a complete valid postal address or registered PO Box is required")
    message = BytesParser(policy=policy.default).parsebytes(raw)
    html_added = False
    plain_added = False
    parts = message.walk() if message.is_multipart() else [message]
    for part in parts:
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        content_type = part.get_content_type()
        if content_type not in {"text/plain", "text/html"}:
            continue
        value = part.get_content()
        if isinstance(value, bytes):
            value = value.decode(part.get_content_charset() or "utf-8", "replace")
        if content_type == "text/html":
            if FOOTER_MARKER not in value:
                addition = footer_html(postal_address)
                lower = value.lower()
                body_end = lower.rfind("</body>")
                value = value[:body_end] + addition + value[body_end:] if body_end >= 0 else value + addition
                part.set_content(value, subtype="html", charset="utf-8", cte="quoted-printable")
            html_added = True
        elif value.strip():
            marker = "This is a business solicitation from East Bay Projects."
            if marker not in value:
                value = value.rstrip() + "\n\n" + footer_text(postal_address) + "\n"
                part.set_content(value, subtype="plain", charset="utf-8", cte="quoted-printable")
            plain_added = True
    if not html_added and not plain_added:
        raise ValueError("draft does not contain a non-empty text or HTML body")
    while message.get("List-Unsubscribe") is not None:
        del message["List-Unsubscribe"]
    message["List-Unsubscribe"] = f"<mailto:{account}?subject=unsubscribe>"
    return message.as_bytes(policy=policy.SMTP)


def prepare_queue(postal_address: str, account: str) -> dict:
    init_db()
    service = gmail_service(account)
    prepared = 0
    failures: list[str] = []
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM queue WHERE status = 'blocked' ORDER BY scheduled_at_utc"
        ).fetchall()
    if not rows:
        raise RuntimeError("no blocked queue rows; run plan first")
    for row in rows:
        try:
            draft = service.users().drafts().get(
                userId="me", id=row["draft_id"], format="raw"
            ).execute()
            updated_raw = add_compliance_footer(
                decode_raw(draft["message"]["raw"]), postal_address, account
            )
            response = service.users().drafts().update(
                userId="me",
                id=row["draft_id"],
                body={"message": {"raw": encode_raw(updated_raw)}},
            ).execute()
            with connect() as db:
                db.execute(
                    """
                    UPDATE queue
                    SET message_id = ?, prepared = 1, updated_at_utc = ?
                    WHERE source_message_id = ?
                    """,
                    (response["message"]["id"], iso_utc(), row["source_message_id"]),
                )
                record_event(db, "draft_prepared", row["source_message_id"])
            prepared += 1
        except Exception as error:  # Google API errors are recorded and leave sending paused.
            failures.append(row["source_message_id"])
            with connect() as db:
                db.execute(
                    "UPDATE queue SET last_error = ?, updated_at_utc = ? WHERE source_message_id = ?",
                    (str(error)[:1000], iso_utc(), row["source_message_id"]),
                )
        if prepared and prepared % 25 == 0:
            print(f"prepared={prepared}/{len(rows)}", flush=True)
        time.sleep(0.1)
    with connect() as db:
        if failures:
            set_setting(db, "paused", "1")
            set_setting(db, "pause_reason", f"preparation failed for {len(failures)} drafts")
        else:
            db.execute(
                "UPDATE queue SET status = 'pending', updated_at_utc = ? WHERE status = 'blocked'",
                (iso_utc(),),
            )
            set_setting(db, "postal_address", postal_address)
            set_setting(db, "prepared_at_utc", iso_utc())
            set_setting(db, "pause_reason", "prepared; awaiting explicit resume")
            record_event(db, "queue_prepared", detail=f"count={prepared}")
    if failures:
        raise RuntimeError(f"failed to prepare {len(failures)} drafts")
    return {"prepared": prepared, "paused": True}


def message_labels(service, message_id: str) -> set[str]:
    response = service.users().messages().get(
        userId="me", id=message_id, format="minimal"
    ).execute()
    return set(response.get("labelIds", []))


def reconcile_sending(service) -> int:
    reconciled = 0
    with connect() as db:
        rows = db.execute("SELECT * FROM queue WHERE status = 'sending'").fetchall()
    for row in rows:
        try:
            labels = message_labels(service, row["message_id"])
        except Exception as error:
            with connect() as db:
                db.execute(
                    "UPDATE queue SET last_error = ?, updated_at_utc = ? WHERE source_message_id = ?",
                    (str(error)[:1000], iso_utc(), row["source_message_id"]),
                )
            continue
        with connect() as db:
            if "SENT" in labels:
                db.execute(
                    """
                    UPDATE queue SET status = 'sent', sent_message_id = message_id,
                    last_error = NULL, updated_at_utc = ? WHERE source_message_id = ?
                    """,
                    (iso_utc(), row["source_message_id"]),
                )
                record_event(db, "send_reconciled", row["source_message_id"])
                reconciled += 1
            elif "DRAFT" in labels:
                db.execute(
                    "UPDATE queue SET status = 'pending', updated_at_utc = ? WHERE source_message_id = ?",
                    (iso_utc(), row["source_message_id"]),
                )
    return reconciled


def bounce_count(service, start_date: str) -> int:
    query = (
        "from:(mailer-daemon@googlemail.com OR mailer-daemon@google.com) "
        f"after:{start_date.replace('-', '/')}"
    )
    response = service.users().messages().list(
        userId="me", q=query, maxResults=100, includeSpamTrash=True
    ).execute()
    return len(response.get("messages", []))


def enforce_bounce_guard(service) -> None:
    with connect() as db:
        sent = db.execute("SELECT COUNT(*) FROM queue WHERE status = 'sent'").fetchone()[0]
        start = setting(db, "start_date")
    if sent < 20:
        return
    bounces = bounce_count(service, start)
    if bounces >= 5 or bounces / sent >= 0.05:
        with connect() as db:
            set_setting(db, "paused", "1")
            set_setting(db, "pause_reason", f"bounce guard: {bounces} bounces after {sent} sends")
            record_event(db, "auto_paused_bounces", detail=f"bounces={bounces} sent={sent}")
        raise RuntimeError(f"bounce guard paused sending: {bounces} bounces after {sent} sends")


def enforce_overdue_guard() -> None:
    with connect() as db:
        row = db.execute(
            """
            SELECT scheduled_at_utc FROM queue
            WHERE status = 'pending' AND prepared = 1 AND scheduled_at_utc <= ?
            ORDER BY scheduled_at_utc LIMIT 1
            """,
            (iso_utc(),),
        ).fetchone()
        if not row:
            return
        scheduled = datetime.fromisoformat(row["scheduled_at_utc"])
        overdue = utc_now() - scheduled
        if overdue > timedelta(hours=2):
            reason = "oldest due message is over two hours late; re-plan before resuming"
            set_setting(db, "paused", "1")
            set_setting(db, "pause_reason", reason)
            record_event(db, "auto_paused_overdue", detail=str(overdue))
            raise RuntimeError(reason)


def due_rows(limit: int) -> list[sqlite3.Row]:
    stamp = iso_utc()
    with connect() as db:
        return db.execute(
            """
            SELECT q.* FROM queue q
            LEFT JOIN suppressions s ON s.recipient = q.recipient
            WHERE q.status = 'pending'
              AND q.prepared = 1
              AND q.scheduled_at_utc <= ?
              AND (q.next_attempt_at_utc IS NULL OR q.next_attempt_at_utc <= ?)
              AND s.recipient IS NULL
            ORDER BY q.scheduled_at_utc
            LIMIT ?
            """,
            (stamp, stamp, limit),
        ).fetchall()


@contextmanager
def worker_lock() -> Iterator[None]:
    handle = (state_dir() / "worker.lock").open("w")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise RuntimeError("another outbound worker is running")
    try:
        yield
    finally:
        fcntl.flock(handle, fcntl.LOCK_UN)
        handle.close()


def run_once(account: str, limit: int) -> dict:
    init_db()
    with worker_lock():
        with connect() as db:
            if setting(db, "paused", "1") != "0":
                return {
                    "paused": True,
                    "reason": setting(db, "pause_reason", "unspecified"),
                    "sent": 0,
                }
        service = gmail_service(account)
        reconciled = reconcile_sending(service)
        enforce_bounce_guard(service)
        enforce_overdue_guard()
        sent = 0
        for row in due_rows(limit):
            with connect() as db:
                suppressed = db.execute(
                    "SELECT 1 FROM suppressions WHERE recipient = ?", (row["recipient"],)
                ).fetchone()
                if suppressed:
                    db.execute(
                        "UPDATE queue SET status = 'skipped', last_error = 'suppressed', updated_at_utc = ? WHERE source_message_id = ?",
                        (iso_utc(), row["source_message_id"]),
                    )
                    continue
                db.execute(
                    """
                    UPDATE queue
                    SET status = 'sending', attempts = attempts + 1, updated_at_utc = ?
                    WHERE source_message_id = ? AND status = 'pending'
                    """,
                    (iso_utc(), row["source_message_id"]),
                )
                record_event(db, "send_started", row["source_message_id"])
            try:
                labels = message_labels(service, row["message_id"])
                if "SENT" in labels:
                    response = {"id": row["message_id"]}
                elif "DRAFT" in labels:
                    response = service.users().drafts().send(
                        userId="me", body={"id": row["draft_id"]}
                    ).execute()
                else:
                    raise RuntimeError(f"message labels are neither DRAFT nor SENT: {sorted(labels)}")
                with connect() as db:
                    db.execute(
                        """
                        UPDATE queue SET status = 'sent', sent_message_id = ?,
                        last_error = NULL, next_attempt_at_utc = NULL, updated_at_utc = ?
                        WHERE source_message_id = ?
                        """,
                        (response["id"], iso_utc(), row["source_message_id"]),
                    )
                    record_event(db, "sent", row["source_message_id"])
                sent += 1
            except Exception as error:
                delay = min(3600, 60 * (2 ** min(row["attempts"], 5)))
                retry_at = utc_now() + timedelta(seconds=delay)
                terminal = row["attempts"] + 1 >= 5
                with connect() as db:
                    db.execute(
                        """
                        UPDATE queue SET status = ?, last_error = ?, next_attempt_at_utc = ?,
                        updated_at_utc = ? WHERE source_message_id = ?
                        """,
                        (
                            "failed" if terminal else "pending",
                            str(error)[:1000],
                            iso_utc(retry_at),
                            iso_utc(),
                            row["source_message_id"],
                        ),
                    )
                    record_event(db, "send_failed", row["source_message_id"], str(error)[:1000])
                if terminal:
                    with connect() as db:
                        set_setting(db, "paused", "1")
                        set_setting(db, "pause_reason", "message exhausted five send attempts")
                    raise
        return {"paused": False, "sent": sent, "reconciled": reconciled}


def resume() -> dict:
    init_db()
    with connect() as db:
        blocked = db.execute(
            "SELECT COUNT(*) FROM queue WHERE status = 'blocked' OR (status = 'pending' AND prepared = 0)"
        ).fetchone()[0]
        due = db.execute(
            "SELECT COUNT(*) FROM queue WHERE status = 'pending' AND scheduled_at_utc <= ?",
            (iso_utc(),),
        ).fetchone()[0]
        prepared_at = setting(db, "prepared_at_utc")
        if blocked or not prepared_at:
            raise RuntimeError("queue is not fully prepared with the compliance footer")
        if due:
            raise RuntimeError("schedule contains past-due messages; re-plan before resuming")
        set_setting(db, "paused", "0")
        set_setting(db, "pause_reason", "")
        set_setting(db, "resumed_at_utc", iso_utc())
        record_event(db, "resumed")
    return {"paused": False}


def pause(reason: str) -> dict:
    init_db()
    with connect() as db:
        set_setting(db, "paused", "1")
        set_setting(db, "pause_reason", reason)
        record_event(db, "paused", detail=reason)
    return {"paused": True, "reason": reason}


def suppress(recipient: str, reason: str) -> dict:
    address = recipient.strip().lower()
    if "@" not in address:
        raise ValueError("suppression recipient must be an email address")
    init_db()
    with connect() as db:
        db.execute(
            """
            INSERT INTO suppressions(recipient, reason, created_at_utc) VALUES (?, ?, ?)
            ON CONFLICT(recipient) DO UPDATE SET reason = excluded.reason
            """,
            (address, reason, iso_utc()),
        )
        changed = db.execute(
            """
            UPDATE queue SET status = 'skipped', last_error = 'suppressed',
            updated_at_utc = ? WHERE recipient = ? AND status IN ('blocked', 'pending')
            """,
            (iso_utc(), address),
        ).rowcount
        record_event(db, "recipient_suppressed", detail=f"changed={changed}")
    return {"suppressed": address, "queue_rows_skipped": changed}


def status_report() -> dict:
    init_db()
    with connect() as db:
        counts = {
            row["status"]: row["count"]
            for row in db.execute(
                "SELECT status, COUNT(*) AS count FROM queue GROUP BY status"
            ).fetchall()
        }
        day_rows = db.execute(
            """
            SELECT substr(scheduled_at_utc, 1, 10) AS utc_day, COUNT(*) AS count
            FROM queue WHERE status IN ('blocked', 'pending')
            GROUP BY utc_day ORDER BY utc_day LIMIT 30
            """
        ).fetchall()
        return {
            "paused": setting(db, "paused", "1") != "0",
            "pause_reason": setting(db, "pause_reason"),
            "start_date": setting(db, "start_date"),
            "timezone": setting(db, "timezone", DEFAULT_TIMEZONE),
            "counts": counts,
            "scheduled_by_utc_day": {row["utc_day"]: row["count"] for row in day_rows},
            "suppressions": db.execute("SELECT COUNT(*) FROM suppressions").fetchone()[0],
        }


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account", default=os.environ.get("EASTBAY_OUTBOUND_ACCOUNT", DEFAULT_ACCOUNT))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    plan_parser = sub.add_parser("plan")
    plan_parser.add_argument("--start-date", required=True, type=parse_date)
    plan_parser.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--postal-address", required=True)
    sub.add_parser("resume")
    pause_parser = sub.add_parser("pause")
    pause_parser.add_argument("--reason", default="manually paused")
    run_parser = sub.add_parser("run-once")
    run_parser.add_argument("--limit", type=int, default=int(os.environ.get("EASTBAY_OUTBOUND_MAX_PER_RUN", "1")))
    suppress_parser = sub.add_parser("suppress")
    suppress_parser.add_argument("recipient")
    suppress_parser.add_argument("--reason", default="recipient opted out")
    sub.add_parser("status")
    args = parser.parse_args()

    if args.command == "init":
        init_db()
        result = status_report()
    elif args.command == "plan":
        result = plan_queue(args.start_date, args.timezone)
    elif args.command == "prepare":
        result = prepare_queue(args.postal_address, args.account)
    elif args.command == "resume":
        result = resume()
    elif args.command == "pause":
        result = pause(args.reason)
    elif args.command == "run-once":
        result = run_once(args.account, args.limit)
    elif args.command == "suppress":
        result = suppress(args.recipient, args.reason)
    else:
        result = status_report()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"outbound sender error: {error}", file=sys.stderr)
        raise SystemExit(1)
