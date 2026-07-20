import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import app
import import_ads

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        os.environ["EASTBAY_AD_REVIEW_STATE"]=self.temp.name
        app.init_db()

    def tearDown(self):
        self.temp.cleanup()

    def test_import_is_idempotent(self):
        source=Path(self.temp.name)/"ads.json"
        source.write_text(json.dumps([{
            "id":"text-one","kind":"text","title":"First","campaign":"Test","region":"DMV",
            "aspect_ratio":"responsive search","payload":{"headline":"Hello","description":"World"}
        }]))
        import_ads.run(source)
        import_ads.run(source)
        with app.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM ads").fetchone()[0],1)

    def test_database_blocks_unapproved_jobs(self):
        stamp=app.now()
        with app.connect() as db:
            db.execute("""INSERT INTO ads
              (id,kind,title,payload_json,status,created_at,updated_at)
              VALUES ('draft','text','Draft','{}','pending_review',?,?)""",(stamp,stamp))
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("""INSERT INTO sync_jobs
                  (id,ad_id,idempotency_key,created_at,updated_at)
                  VALUES ('job','draft','key',?,?)""",(stamp,stamp))

    def test_approved_job_can_be_queued(self):
        stamp=app.now()
        with app.connect() as db:
            db.execute("""INSERT INTO ads
              (id,kind,title,payload_json,status,created_at,updated_at)
              VALUES ('approved','display','Approved','{}','approved',?,?)""",(stamp,stamp))
            db.execute("""INSERT INTO sync_jobs
              (id,ad_id,idempotency_key,created_at,updated_at)
              VALUES ('job','approved','key',?,?)""",(stamp,stamp))
            self.assertEqual(db.execute("SELECT status FROM sync_jobs").fetchone()[0],"queued")

if __name__=="__main__":
    unittest.main()
