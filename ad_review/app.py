#!/usr/bin/env python3
"""Private, loopback-only ad review service for East Bay Projects."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sqlite3
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DEFAULT_STATE = Path.home() / ".local" / "share" / "eastbayprojects" / "ad-review"
ALLOWED_STATUSES = {
    "draft", "pending_review", "approved", "rejected", "queued", "syncing", "synced", "failed"
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def state_dir() -> Path:
    path = Path(os.environ.get("EASTBAY_AD_REVIEW_STATE", DEFAULT_STATE)).expanduser()
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def db_path() -> Path:
    return state_dir() / "review.sqlite3"


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(db_path(), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db() -> None:
    with connect() as db:
        db.executescript((ROOT / "schema.sql").read_text())


def decode_payload(row: sqlite3.Row) -> dict:
    item = dict(row)
    item["payload"] = json.loads(item.pop("payload_json"))
    return item


def seed_db() -> None:
    init_db()
    samples = [
        {
            "id": "display-made-in-usa",
            "kind": "display",
            "title": "Made in USA credibility badge",
            "campaign": "GovCon websites",
            "region": "United States",
            "aspect_ratio": "1.91:1",
            "payload": {
                "headline": "Websites Built in the USA",
                "description": "Senior-led delivery for federal and defense firms.",
                "badge": "MADE IN USA",
                "accent": "#c8750a",
            },
        },
        {
            "id": "display-nova",
            "kind": "display",
            "title": "Northern Virginia regional",
            "campaign": "GovCon websites",
            "region": "Northern Virginia",
            "aspect_ratio": "1:1",
            "payload": {
                "headline": "Built for Northern Virginia Firms",
                "description": "Credibility-first websites for GovCon growth.",
                "badge": "NORTHERN VIRGINIA",
                "accent": "#e8a53a",
            },
        },
        {
            "id": "text-govcon-01",
            "kind": "text",
            "title": "Clear scope, fast delivery",
            "campaign": "GovCon websites",
            "region": "DMV",
            "aspect_ratio": "responsive search",
            "payload": {
                "headline": "Websites for Federal Firms - Clear Scope, Fast Delivery",
                "description": "Websites for GovCon and defense firms that strengthen credibility, recruiting, and growth. Clear deliverables and no agency layers.",
                "display_url": "eastbayprojects.com/government-contractor-websites",
                "sitelinks": ["Meet Nate", "Website Services", "View Portfolio"],
            },
        },
        {
            "id": "text-defense-01",
            "kind": "text",
            "title": "Defense contractor credibility",
            "campaign": "GovCon websites",
            "region": "DMV",
            "aspect_ratio": "responsive search",
            "payload": {
                "headline": "Defense Contractor Website Design | Senior-Led Delivery",
                "description": "Build a credible public presence for buyers, partners, and cleared candidates. Work directly with an experienced engineer.",
                "display_url": "eastbayprojects.com/defense-contractor-websites",
                "sitelinks": ["Start a Project", "View Portfolio", "Meet Nate"],
            },
        },
    ]
    stamp = now()
    with connect() as db:
        for item in samples:
            db.execute(
                """
                INSERT OR IGNORE INTO ads
                  (id, kind, title, campaign, region, aspect_ratio, payload_json, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending_review', ?, ?)
                """,
                (
                    item["id"], item["kind"], item["title"], item["campaign"], item["region"],
                    item["aspect_ratio"], json.dumps(item["payload"]), stamp, stamp,
                ),
            )


def notify_pending(ad: dict) -> None:
    topic = os.environ.get("NTFY_TOPIC_URL", "").rstrip("/")
    if not topic:
        return
    review_base = os.environ.get("EASTBAY_REVIEW_BASE_URL", "").rstrip("/")
    route = "display" if ad["kind"] == "display" else "text"
    headers = {
        "Title": "East Bay ad ready for review",
        "Tags": "art,mag",
        "Priority": "default",
    }
    if review_base:
        headers["Click"] = f"{review_base}/{route}?ad={ad['id']}"
    token = os.environ.get("NTFY_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(topic, data=ad["title"].encode(), headers=headers, method="POST")
    try:
        urllib.request.urlopen(request, timeout=5).read()
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"ntfy delivery failed: {error}", file=sys.stderr)


class Handler(BaseHTTPRequestHandler):
    server_version = "EastBayAdReview/0.1"

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")

    def send_common_headers(self, content_type: str, length: int) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; img-src 'self' data:; script-src 'self'; connect-src 'self'")
        self.end_headers()

    def json_response(self, payload: object, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def error_json(self, message: str, status: int) -> None:
        self.json_response({"error": message}, status)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 1 or length > 65_536:
            raise ValueError("invalid request size")
        value = json.loads(self.rfile.read(length))
        if not isinstance(value, dict):
            raise ValueError("request body must be an object")
        return value

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            return self.json_response({"ok": True, "service": "eastbay-ad-review"})
        if parsed.path == "/api/ads":
            params = parse_qs(parsed.query)
            kind = params.get("kind", [""])[0]
            status = params.get("status", [""])[0]
            clauses, values = [], []
            if kind in {"display", "text"}:
                clauses.append("kind = ?")
                values.append(kind)
            if status in ALLOWED_STATUSES:
                clauses.append("status = ?")
                values.append(status)
            where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
            with connect() as db:
                rows = db.execute(
                    f"SELECT * FROM ads {where} ORDER BY CASE status WHEN 'pending_review' THEN 0 ELSE 1 END, created_at DESC",
                    values,
                ).fetchall()
            return self.json_response({"ads": [decode_payload(row) for row in rows]})
        if parsed.path == "/api/queue":
            with connect() as db:
                rows = db.execute(
                    """SELECT j.*, a.title, a.kind, a.campaign
                       FROM sync_jobs j JOIN ads a ON a.id = j.ad_id
                       ORDER BY j.created_at DESC"""
                ).fetchall()
            return self.json_response({"jobs": [dict(row) for row in rows]})
        if parsed.path.startswith("/creative/"):
            return self.serve_creative(parsed.path.split("/")[-1])
        return self.serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            return self.error_json(str(error), HTTPStatus.BAD_REQUEST)
        if parsed.path == "/api/ads":
            return self.create_ad(payload)
        if parsed.path.startswith("/api/ads/") and parsed.path.endswith("/decision"):
            ad_id = parsed.path.removeprefix("/api/ads/").removesuffix("/decision").strip("/")
            return self.decide(ad_id, payload)
        self.error_json("not found", HTTPStatus.NOT_FOUND)

    def create_ad(self, payload: dict) -> None:
        kind = payload.get("kind")
        title = str(payload.get("title", "")).strip()
        ad_payload = payload.get("payload")
        if kind not in {"display", "text"} or not title or not isinstance(ad_payload, dict):
            return self.error_json("kind, title, and payload are required", HTTPStatus.BAD_REQUEST)
        ad_id = str(payload.get("id") or uuid.uuid4())
        stamp = now()
        item = {
            "id": ad_id,
            "kind": kind,
            "title": title,
            "campaign": str(payload.get("campaign", "")),
            "region": str(payload.get("region", "")),
            "aspect_ratio": str(payload.get("aspect_ratio", "")),
            "payload": ad_payload,
        }
        with connect() as db:
            try:
                db.execute(
                    """INSERT INTO ads
                       (id, kind, title, campaign, region, aspect_ratio, payload_json, creative_path,
                        status, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending_review', ?, ?)""",
                    (
                        ad_id, kind, title, item["campaign"], item["region"], item["aspect_ratio"],
                        json.dumps(ad_payload), payload.get("creative_path"), stamp, stamp,
                    ),
                )
            except sqlite3.IntegrityError:
                return self.error_json("ad id already exists", HTTPStatus.CONFLICT)
        notify_pending(item)
        self.json_response({"ad": item, "status": "pending_review"}, HTTPStatus.CREATED)

    def decide(self, ad_id: str, payload: dict) -> None:
        decision = payload.get("decision")
        if decision not in {"approved", "rejected"}:
            return self.error_json("decision must be approved or rejected", HTTPStatus.BAD_REQUEST)
        stamp = now()
        with connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM ads WHERE id = ?", (ad_id,)).fetchone()
            if not row:
                return self.error_json("ad not found", HTTPStatus.NOT_FOUND)
            if row["status"] == decision:
                return self.json_response({"ad": decode_payload(row), "idempotent": True})
            if row["status"] not in {"pending_review", "rejected"}:
                return self.error_json(f"cannot review an ad in {row['status']}", HTTPStatus.CONFLICT)
            db.execute("UPDATE ads SET status = ?, updated_at = ? WHERE id = ?", (decision, stamp, ad_id))
            db.execute(
                "INSERT INTO review_events (ad_id, decision, actor, note, created_at) VALUES (?, ?, ?, ?, ?)",
                (ad_id, decision, str(payload.get("actor", "nate")), str(payload.get("note", "")), stamp),
            )
            if decision == "approved":
                key = f"upsert_asset:{ad_id}"
                db.execute(
                    """INSERT OR IGNORE INTO sync_jobs
                       (id, ad_id, operation, status, idempotency_key, created_at, updated_at)
                       VALUES (?, ?, 'upsert_asset', 'queued', ?, ?, ?)""",
                    (str(uuid.uuid4()), ad_id, key, stamp, stamp),
                )
            updated = db.execute("SELECT * FROM ads WHERE id = ?", (ad_id,)).fetchone()
        self.json_response({"ad": decode_payload(updated)})

    def serve_creative(self, ad_id: str) -> None:
        with connect() as db:
            row = db.execute("SELECT creative_path FROM ads WHERE id = ?", (ad_id,)).fetchone()
        if not row or not row["creative_path"]:
            return self.send_error(HTTPStatus.NOT_FOUND)
        root = (state_dir() / "creatives").resolve()
        candidate = (root / row["creative_path"]).resolve()
        if root not in candidate.parents or not candidate.is_file():
            return self.send_error(HTTPStatus.NOT_FOUND)
        self.send_file(candidate)

    def serve_static(self, path: str) -> None:
        route = path if path not in {"/", "/display", "/text", "/queue"} else "/index.html"
        candidate = (STATIC / route.lstrip("/")).resolve()
        if STATIC.resolve() not in candidate.parents or not candidate.is_file():
            return self.send_error(HTTPStatus.NOT_FOUND)
        self.send_file(candidate)

    def send_file(self, path: Path) -> None:
        body = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_common_headers(content_type, len(body))
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8765")))
    parser.add_argument("--seed", action="store_true", help="add safe sample review items")
    args = parser.parse_args()
    init_db()
    if args.seed:
        seed_db()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"East Bay ad review listening on http://127.0.0.1:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
