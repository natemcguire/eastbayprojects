import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import app
import build_sync_plan


class SyncPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.environ["EASTBAY_AD_REVIEW_STATE"] = self.temp.name
        app.init_db()
        stamp = app.now()
        with app.connect() as db:
            db.execute(
                "INSERT INTO settings (key,value,updated_at) VALUES (?,?,?)",
                ("google_ads_campaign_id", "test-pmax-campaign", stamp),
            )
            db.execute(
                "INSERT INTO settings (key,value,updated_at) VALUES (?,?,?)",
                ("google_ads_asset_group_id", "test-asset-group", stamp),
            )

    def tearDown(self):
        self.temp.cleanup()

    def add_queued(self, ad_id, kind, payload, creative_path=None, final_status="approved"):
        stamp = app.now()
        with app.connect() as db:
            db.execute(
                """INSERT INTO ads
                   (id,kind,title,campaign,region,aspect_ratio,payload_json,creative_path,status,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?, 'approved',?,?)""",
                (
                    ad_id,
                    kind,
                    ad_id,
                    "Test",
                    "DMV",
                    "1.91:1" if kind == "display" else "responsive search",
                    json.dumps(payload),
                    creative_path,
                    stamp,
                    stamp,
                ),
            )
            db.execute(
                """INSERT INTO sync_jobs
                   (id,ad_id,idempotency_key,status,created_at,updated_at)
                   VALUES (?,?,?,'queued',?,?)""",
                ("job-" + ad_id, ad_id, "upsert:" + ad_id, stamp, stamp),
            )
            if final_status != "approved":
                db.execute("UPDATE ads SET status=? WHERE id=?", (final_status, ad_id))

    def text_payload(self, category, many=False):
        headlines = [f"Headline {number}" for number in range(1, 18 if many else 5)]
        if many:
            headlines += ["headline 1", " Headline   2 "]
        descriptions = [f"Description {number}" for number in range(1, 7 if many else 4)]
        if many:
            descriptions.append("description 1")
        return {
            "category": category,
            "headlines": headlines,
            "descriptions": descriptions,
            "final_url": "https://eastbayprojects.com/contact",
            "display_paths": ["govcon", "websites"],
            "sitelink_details": [
                {"text": "Meet Nate", "final_url": "https://eastbayprojects.com/#about"},
                {"text": "View Portfolio", "final_url": "https://eastbayprojects.com/portfolio.html"},
            ],
        }

    def test_plan_is_safe_deterministic_and_capped(self):
        for index, (category, _) in enumerate(build_sync_plan.CATEGORIES):
            self.add_queued(
                f"text-{index}",
                "text",
                self.text_payload(category, many=index == 0),
            )
        self.add_queued(
            "display-one",
            "display",
            {"headline": "Made in USA", "description": "Senior-led.", "variant": "horizontal"},
            creative_path="made-in-usa/horizontal.png",
        )
        self.add_queued(
            "rejected-text",
            "text",
            self.text_payload(build_sync_plan.CATEGORIES[0][0]),
            final_status="rejected",
        )
        self.add_queued(
            "pending-display",
            "display",
            {"headline": "Pending", "description": "Do not include"},
            creative_path="pending.png",
            final_status="pending_review",
        )

        before = {}
        with app.connect() as db:
            before = {
                row["id"]: row["status"]
                for row in db.execute("SELECT id,status FROM ads ORDER BY id")
            }

        first = Path(self.temp.name) / "sync" / "plan.json"
        second = Path(self.temp.name) / "sync" / "plan-2.json"
        build_sync_plan.write_plan(first)
        build_sync_plan.write_plan(second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(stat.S_IMODE(first.stat().st_mode), 0o600)

        plan = json.loads(first.read_text())
        campaign = plan["text_search"]["campaign"]
        self.assertEqual(campaign["status"], "PAUSED")
        self.assertEqual(len(campaign["ad_groups"]), 4)
        self.assertTrue(all(group["status"] == "PAUSED" for group in campaign["ad_groups"]))
        self.assertEqual(plan["summary"], {
            "queued_approved_jobs": 5,
            "text_rsas": 4,
            "display_assets": 1,
            "search_ad_groups": 4,
        })

        first_rsa = campaign["ad_groups"][0]["responsive_search_ads"][0]
        self.assertEqual(len(first_rsa["headlines"]), 15)
        self.assertEqual(len(first_rsa["descriptions"]), 4)
        self.assertEqual(first_rsa["final_urls"], ["https://eastbayprojects.com/contact"])
        self.assertEqual(first_rsa["sitelinks"][0]["text"], "Meet Nate")
        self.assertEqual(first_rsa["display_paths"], ["govcon", "websites"])
        self.assertEqual(first_rsa["status"], "PAUSED")

        pmax = plan["display_pmax"]
        self.assertEqual(pmax["campaign_id"], "test-pmax-campaign")
        self.assertEqual(pmax["asset_group_id"], "test-asset-group")
        self.assertEqual(pmax["assets"][0]["source_ad_id"], "display-one")

        encoded = first.read_text()
        self.assertNotIn("rejected-text", encoded)
        self.assertNotIn("pending-display", encoded)
        self.assertFalse(plan["safety"]["google_calls"])
        self.assertTrue(plan["safety"]["requires_separate_explicit_sync"])

        with app.connect() as db:
            after = {
                row["id"]: row["status"]
                for row in db.execute("SELECT id,status FROM ads ORDER BY id")
            }
        self.assertEqual(before, after)

    def test_unknown_category_is_rejected(self):
        self.add_queued("bad-category", "text", self.text_payload("unknown"))
        with self.assertRaises(build_sync_plan.PlanError):
            build_sync_plan.build_plan()


if __name__ == "__main__":
    unittest.main()
