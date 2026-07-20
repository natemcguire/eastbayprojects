import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import app
import campaign_review


class CampaignReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.environ["EASTBAY_AD_REVIEW_STATE"] = self.temp.name
        app.init_db()
        self.write_plan("fingerprint-one")
        stamp = app.now()
        with app.connect() as db:
            db.execute(
                """INSERT INTO ads
                   (id,kind,title,payload_json,status,created_at,updated_at)
                   VALUES ('approved-ad','text','Approved','{}','approved',?,?)""",
                (stamp, stamp),
            )
            db.execute(
                """INSERT INTO sync_jobs
                   (id,ad_id,idempotency_key,status,created_at,updated_at)
                   VALUES ('job','approved-ad','key','queued',?,?)""",
                (stamp, stamp),
            )
            db.execute(
                """INSERT INTO ads
                   (id,kind,title,payload_json,status,created_at,updated_at)
                   VALUES ('rejected-ad','text','Rejected','{}','rejected',?,?)""",
                (stamp, stamp),
            )

    def tearDown(self):
        self.temp.cleanup()

    def write_plan(self, fingerprint):
        directory = Path(self.temp.name) / "sync"
        directory.mkdir(parents=True, exist_ok=True)
        plan = {
            "schema_version": 1,
            "mode": "PLAN_ONLY",
            "source_fingerprint": fingerprint,
            "summary": {
                "queued_approved_jobs": 1,
                "text_rsas": 1,
                "display_assets": 0,
                "search_ad_groups": 4,
            },
            "text_search": {
                "campaign": {
                    "name": "Proposed Search",
                    "status": "PAUSED",
                    "ad_groups": [
                        {
                            "category": f"category-{number}",
                            "name": f"Group {number}",
                            "responsive_search_ads": [] if number else [{}],
                        }
                        for number in range(4)
                    ],
                }
            },
            "display_pmax": {"assets": []},
        }
        (directory / "plan.json").write_text(json.dumps(plan, sort_keys=True, indent=2) + "\n")

    def queue_state(self):
        with app.connect() as db:
            return {
                "ads": [tuple(row) for row in db.execute("SELECT id,status FROM ads ORDER BY id")],
                "jobs": [tuple(row) for row in db.execute("SELECT id,status FROM sync_jobs ORDER BY id")],
            }

    def test_defaults_and_deliberate_approval_preserve_asset_queue(self):
        before = self.queue_state()
        current = campaign_review.get_current_review()
        review = current["review"]
        self.assertEqual(review["geography"], "DMV")
        self.assertEqual(review["daily_budget"], "15.00")
        self.assertEqual(review["launch_status"], "PAUSED")
        self.assertEqual(review["decision"], "pending_review")
        self.assertEqual(current["plan"]["summary"]["search_ad_groups"], 4)

        payload = {
            "plan_digest": review["plan_digest"],
            "decision": "approved",
            "geography": "DMV",
            "daily_budget": "15.00",
            "launch_status": "PAUSED",
            "actor": "nate",
        }
        with self.assertRaises(campaign_review.CampaignReviewError):
            campaign_review.decide_campaign(payload)
        with app.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM campaign_review_events").fetchone()[0], 0)

        payload["confirmation"] = campaign_review.CONFIRMATION
        approved = campaign_review.decide_campaign(payload)["review"]
        self.assertEqual(approved["decision"], "approved")
        self.assertEqual(approved["daily_budget_micros"], 15_000_000)
        self.assertEqual(before, self.queue_state())
        with app.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM campaign_review_events").fetchone()[0], 1)

    def test_active_launch_choice_is_explicit_and_audited(self):
        current = campaign_review.get_current_review()["review"]
        result = campaign_review.decide_campaign(
            {
                "plan_digest": current["plan_digest"],
                "decision": "approved",
                "geography": "TEXAS",
                "daily_budget": "25.50",
                "launch_status": "ENABLED",
                "confirmation": campaign_review.CONFIRMATION,
                "actor": "nate",
            }
        )["review"]
        self.assertEqual(result["geography"], "TEXAS")
        self.assertEqual(result["daily_budget"], "25.50")
        self.assertEqual(result["launch_status"], "ENABLED")
        with app.connect() as db:
            event = db.execute(
                "SELECT decision,geography,daily_budget_micros,launch_status FROM campaign_review_events"
            ).fetchone()
        self.assertEqual(tuple(event), ("approved", "TEXAS", 25_500_000, "ENABLED"))
        self.assertEqual(self.queue_state()["jobs"], [("job", "queued")])

    def test_changed_plan_requires_fresh_review(self):
        first = campaign_review.get_current_review()["review"]
        campaign_review.decide_campaign(
            {
                "plan_digest": first["plan_digest"],
                "decision": "rejected",
                "geography": "DMV",
                "daily_budget": "15",
                "launch_status": "PAUSED",
                "confirmation": campaign_review.CONFIRMATION,
            }
        )
        self.write_plan("fingerprint-two")
        second = campaign_review.get_current_review()["review"]
        self.assertNotEqual(first["plan_digest"], second["plan_digest"])
        self.assertEqual(second["decision"], "pending_review")
        self.assertEqual(second["geography"], "DMV")
        self.assertEqual(second["daily_budget"], "15.00")
        self.assertEqual(second["launch_status"], "PAUSED")

    def test_rejects_stale_plan_and_invalid_budget(self):
        current = campaign_review.get_current_review()["review"]
        base = {
            "plan_digest": "stale",
            "decision": "approved",
            "geography": "DMV",
            "daily_budget": "15",
            "launch_status": "PAUSED",
            "confirmation": campaign_review.CONFIRMATION,
        }
        with self.assertRaises(campaign_review.CampaignReviewError):
            campaign_review.decide_campaign(base)
        base["plan_digest"] = current["plan_digest"]
        base["daily_budget"] = "0.50"
        with self.assertRaises(campaign_review.CampaignReviewError):
            campaign_review.decide_campaign(base)


if __name__ == "__main__":
    unittest.main()
