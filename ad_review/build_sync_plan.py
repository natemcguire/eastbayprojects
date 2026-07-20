#!/usr/bin/env python3
"""Build a deterministic, private Google Ads sync plan without making Google calls."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

from app import connect, init_db, state_dir

SEARCH_CAMPAIGN_NAME = "East Bay Projects - Approved Search Ads"
CATEGORIES = (
    ("govcon_federal_contractor_websites", "GovCon & Federal Contractor Websites"),
    ("defense_credibility_recruiting", "Defense Credibility & Recruiting"),
    ("local_dmv_senior_led_delivery", "DMV Senior-Led Delivery"),
    ("website_modernization", "Website Modernization"),
)
CATEGORY_NAMES = dict(CATEGORIES)


class PlanError(ValueError):
    pass


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def private_setting(key: str) -> str:
    with connect() as db:
        row = db.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    if not row or not str(row["value"]).strip():
        raise PlanError(f"private setting {key!r} is not configured")
    return str(row["value"]).strip()


def unique_strings(values: object, limit: int, field: str) -> list[str]:
    if not isinstance(values, list):
        raise PlanError(f"{field} must be a list")
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        if not isinstance(raw, str):
            raise PlanError(f"{field} entries must be strings")
        value = " ".join(raw.split())
        if not value:
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
        if len(result) == limit:
            break
    return result


def queued_approved_rows() -> list[dict]:
    with connect() as db:
        rows = db.execute(
            """SELECT
                 j.id AS job_id,
                 j.idempotency_key,
                 j.operation,
                 j.status AS job_status,
                 a.id AS ad_id,
                 a.kind,
                 a.title,
                 a.campaign,
                 a.region,
                 a.aspect_ratio,
                 a.payload_json,
                 a.creative_path,
                 a.status AS ad_status
               FROM sync_jobs j
               JOIN ads a ON a.id = j.ad_id
               WHERE j.status = 'queued' AND a.status = 'approved'
               ORDER BY a.kind, a.id, j.id"""
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["payload"] = json.loads(item.pop("payload_json"))
        if item["job_status"] != "queued" or item["ad_status"] != "approved":
            raise PlanError("planner received an unsafe row")
        result.append(item)
    return result


def text_rsa(row: dict) -> dict:
    payload = row["payload"]
    category = payload.get("category")
    if category not in CATEGORY_NAMES:
        raise PlanError(f"{row['ad_id']} has unsupported category {category!r}")
    headlines = payload.get("headlines")
    if headlines is None:
        headlines = [payload.get("headline", "")]
    descriptions = payload.get("descriptions")
    if descriptions is None:
        descriptions = [payload.get("description", "")]
    headlines = unique_strings(headlines, 15, "headlines")
    descriptions = unique_strings(descriptions, 4, "descriptions")
    if len(headlines) < 3:
        raise PlanError(f"{row['ad_id']} needs at least 3 unique headlines")
    if len(descriptions) < 2:
        raise PlanError(f"{row['ad_id']} needs at least 2 unique descriptions")
    final_url = payload.get("final_url")
    if not isinstance(final_url, str) or not final_url.startswith("https://"):
        raise PlanError(f"{row['ad_id']} needs an https final_url")
    sitelinks = payload.get("sitelink_details", payload.get("sitelinks", []))
    if not isinstance(sitelinks, list):
        raise PlanError(f"{row['ad_id']} sitelinks must be a list")
    return {
        "source_ad_id": row["ad_id"],
        "source_job_id": row["job_id"],
        "idempotency_key": row["idempotency_key"],
        "status": "PAUSED",
        "headlines": headlines,
        "descriptions": descriptions,
        "final_urls": [final_url],
        "display_paths": payload.get("display_paths", []),
        "sitelinks": sitelinks,
    }


def display_asset(row: dict) -> dict:
    payload = row["payload"]
    if not row.get("creative_path"):
        raise PlanError(f"{row['ad_id']} has no creative_path")
    return {
        "source_ad_id": row["ad_id"],
        "source_job_id": row["job_id"],
        "idempotency_key": row["idempotency_key"],
        "creative_path": row["creative_path"],
        "aspect_ratio": row["aspect_ratio"],
        "region": row["region"],
        "headline": payload.get("headline", ""),
        "description": payload.get("description", ""),
        "variant": payload.get("variant", ""),
        "dimensions": payload.get("dimensions", ""),
        "sha256": payload.get("sha256", ""),
    }


def build_plan() -> dict:
    init_db()
    pmax_campaign_id = private_setting("google_ads_campaign_id")
    pmax_asset_group_id = private_setting("google_ads_asset_group_id")
    rows = queued_approved_rows()
    grouped = {key: [] for key, _ in CATEGORIES}
    display_assets = []
    source_rows = []
    for row in rows:
        source_rows.append(
            {
                "ad_id": row["ad_id"],
                "job_id": row["job_id"],
                "idempotency_key": row["idempotency_key"],
                "kind": row["kind"],
            }
        )
        if row["kind"] == "text":
            category = row["payload"].get("category")
            rsa = text_rsa(row)
            grouped[category].append(rsa)
        elif row["kind"] == "display":
            display_assets.append(display_asset(row))
        else:
            raise PlanError(f"unsupported kind {row['kind']!r}")
    ad_groups = []
    for category, name in CATEGORIES:
        ads = sorted(grouped[category], key=lambda item: item["source_ad_id"])
        ad_groups.append(
            {
                "category": category,
                "name": name,
                "status": "PAUSED",
                "responsive_search_ads": ads,
            }
        )
    source_rows.sort(key=lambda item: (item["kind"], item["ad_id"], item["job_id"]))
    fingerprint = hashlib.sha256(canonical_json(source_rows).encode()).hexdigest()
    return {
        "schema_version": 1,
        "mode": "PLAN_ONLY",
        "safety": {
            "google_calls": False,
            "database_status_changes": False,
            "requires_separate_explicit_sync": True,
            "source_filter": "ads.status=approved AND sync_jobs.status=queued",
        },
        "source_fingerprint": fingerprint,
        "text_search": {
            "campaign": {
                "name": SEARCH_CAMPAIGN_NAME,
                "status": "PAUSED",
                "ad_groups": ad_groups,
            }
        },
        "display_pmax": {
            "campaign_id": pmax_campaign_id,
            "asset_group_id": pmax_asset_group_id,
            "assets": sorted(display_assets, key=lambda item: item["source_ad_id"]),
        },
        "summary": {
            "queued_approved_jobs": len(rows),
            "text_rsas": sum(len(group["responsive_search_ads"]) for group in ad_groups),
            "display_assets": len(display_assets),
            "search_ad_groups": len(ad_groups),
        },
    }


def write_plan(output: Path | None = None) -> Path:
    plan = build_plan()
    target = output or (state_dir() / "sync" / "plan.json")
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    content = json.dumps(plan, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=".plan-", suffix=".json", dir=target.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        os.chmod(target, 0o600)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="private output path")
    args = parser.parse_args()
    target = write_plan(args.output)
    plan = json.loads(target.read_text())
    print(
        canonical_json(
            {
                "output": str(target),
                "summary": plan["summary"],
                "source_fingerprint": plan["source_fingerprint"],
            }
        )
    )


if __name__ == "__main__":
    main()
