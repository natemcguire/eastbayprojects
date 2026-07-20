#!/usr/bin/env python3
"""Campaign-level review state for a private deterministic sync plan."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app import connect, init_db, now, state_dir

DEFAULT_GEOGRAPHY = "DMV"
DEFAULT_DAILY_BUDGET_MICROS = 15_000_000
DEFAULT_LAUNCH_STATUS = "PAUSED"
CONFIRMATION = "REVIEWED_CAMPAIGN_SETTINGS"
GEOGRAPHIES = {
    "DMV": "Washington, DC, Northern Virginia, and nearby Maryland",
    "NORTHERN_VIRGINIA": "Northern Virginia",
    "WASHINGTON_DC": "Washington, DC",
    "TEXAS": "Texas",
    "BAY_AREA": "Bay Area / San Francisco",
}
LAUNCH_CHOICES = {
    "PAUSED": "Create paused",
    "ENABLED": "Create active",
}


class CampaignReviewError(ValueError):
    pass


def plan_path() -> Path:
    return state_dir() / "sync" / "plan.json"


def load_plan() -> tuple[dict, str]:
    path = plan_path()
    if not path.is_file():
        raise CampaignReviewError("private sync plan is missing; build it before campaign review")
    raw = path.read_bytes()
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as error:
        raise CampaignReviewError("private sync plan is invalid JSON") from error
    if plan.get("mode") != "PLAN_ONLY":
        raise CampaignReviewError("campaign review requires a PLAN_ONLY sync plan")
    if not isinstance(plan.get("summary"), dict):
        raise CampaignReviewError("sync plan summary is missing")
    digest = hashlib.sha256(raw).hexdigest()
    return plan, digest


def format_budget(micros: int) -> str:
    return f"{Decimal(micros) / Decimal(1_000_000):.2f}"


def parse_budget(value: object) -> int:
    try:
        dollars = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise CampaignReviewError("daily budget must be a dollar amount")
    if dollars < Decimal("1.00") or dollars > Decimal("1000.00"):
        raise CampaignReviewError("daily budget must be between $1 and $1,000")
    if dollars.quantize(Decimal("0.01")) != dollars:
        raise CampaignReviewError("daily budget can have at most two decimal places")
    return int(dollars * Decimal(1_000_000))


def decode_review(row, plan: dict) -> dict:
    review = dict(row)
    review["daily_budget"] = format_budget(review["daily_budget_micros"])
    campaign = plan.get("text_search", {}).get("campaign", {})
    ad_groups = campaign.get("ad_groups", [])
    return {
        "review": review,
        "plan": {
            "summary": plan["summary"],
            "search_campaign_name": campaign.get("name", ""),
            "proposed_status": campaign.get("status", "PAUSED"),
            "ad_groups": [
                {
                    "category": group.get("category", ""),
                    "name": group.get("name", ""),
                    "text_rsas": len(group.get("responsive_search_ads", [])),
                }
                for group in ad_groups
            ],
        },
        "options": {
            "geographies": [
                {"value": value, "label": label}
                for value, label in GEOGRAPHIES.items()
            ],
            "launch_statuses": [
                {"value": value, "label": label}
                for value, label in LAUNCH_CHOICES.items()
            ],
        },
    }


def get_current_review() -> dict:
    init_db()
    plan, digest = load_plan()
    fingerprint = str(plan.get("source_fingerprint", ""))
    stamp = now()
    with connect() as db:
        db.execute(
            """INSERT OR IGNORE INTO campaign_reviews
               (plan_digest,source_fingerprint,geography,daily_budget_micros,
                launch_status,decision,created_at,updated_at)
               VALUES (?,?,?,?,'PAUSED','pending_review',?,?)""",
            (
                digest,
                fingerprint,
                DEFAULT_GEOGRAPHY,
                DEFAULT_DAILY_BUDGET_MICROS,
                stamp,
                stamp,
            ),
        )
        row = db.execute(
            "SELECT * FROM campaign_reviews WHERE plan_digest = ?",
            (digest,),
        ).fetchone()
    return decode_review(row, plan)


def decide_campaign(payload: dict) -> dict:
    if payload.get("confirmation") != CONFIRMATION:
        raise CampaignReviewError("confirm that geography, budget, and launch choice were reviewed")
    decision = payload.get("decision")
    if decision not in {"approved", "rejected"}:
        raise CampaignReviewError("decision must be approved or rejected")
    geography = payload.get("geography")
    if geography not in GEOGRAPHIES:
        raise CampaignReviewError("select a supported geography")
    launch_status = payload.get("launch_status")
    if launch_status not in LAUNCH_CHOICES:
        raise CampaignReviewError("launch status must be PAUSED or ENABLED")
    budget_micros = parse_budget(payload.get("daily_budget"))
    get_current_review()
    plan, digest = load_plan()
    if payload.get("plan_digest") != digest:
        raise CampaignReviewError("sync plan changed; reload and review the new plan")
    actor = str(payload.get("actor", "nate")).strip() or "nate"
    stamp = now()
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT * FROM campaign_reviews WHERE plan_digest = ?",
            (digest,),
        ).fetchone()
        if not row:
            raise CampaignReviewError("campaign review record is missing")
        db.execute(
            """UPDATE campaign_reviews
               SET geography=?,daily_budget_micros=?,launch_status=?,
                   decision=?,actor=?,updated_at=?
               WHERE plan_digest=?""",
            (
                geography,
                budget_micros,
                launch_status,
                decision,
                actor,
                stamp,
                digest,
            ),
        )
        db.execute(
            """INSERT INTO campaign_review_events
               (plan_digest,decision,geography,daily_budget_micros,
                launch_status,actor,created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (
                digest,
                decision,
                geography,
                budget_micros,
                launch_status,
                actor,
                stamp,
            ),
        )
        updated = db.execute(
            "SELECT * FROM campaign_reviews WHERE plan_digest = ?",
            (digest,),
        ).fetchone()
    return decode_review(updated, plan)
