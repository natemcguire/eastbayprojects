#!/usr/bin/env python3
"""Idempotently import private ad drafts from a JSON array."""
import argparse
import json
import sys
from pathlib import Path
from app import connect, init_db, now, notify_pending

def validate(item):
    if not isinstance(item, dict):
        raise ValueError("each item must be an object")
    if item.get("kind") not in {"display", "text"}:
        raise ValueError("kind must be display or text")
    if not item.get("id") or not item.get("title") or not isinstance(item.get("payload"), dict):
        raise ValueError("id, title, and payload are required")

def run(path):
    init_db()
    data=json.loads(Path(path).read_text())
    if not isinstance(data,list):
        raise ValueError("top-level JSON value must be an array")
    inserted=skipped=0
    with connect() as db:
        for item in data:
            validate(item)
            exists=db.execute("SELECT 1 FROM ads WHERE id=?",(item["id"],)).fetchone()
            if exists:
                skipped+=1
                continue
            stamp=now()
            db.execute("""INSERT INTO ads
              (id,kind,title,campaign,region,aspect_ratio,payload_json,creative_path,status,created_at,updated_at)
              VALUES (?,?,?,?,?,?,?,?, 'pending_review',?,?)""",
              (item["id"],item["kind"],item["title"],item.get("campaign",""),item.get("region",""),
               item.get("aspect_ratio",""),json.dumps(item["payload"]),item.get("creative_path"),stamp,stamp))
            notify_pending(item)
            inserted+=1
    print(json.dumps({"inserted":inserted,"skipped":skipped,"source":str(path)}))

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    args=parser.parse_args()
    try:
        run(args.path)
    except (OSError,ValueError,json.JSONDecodeError) as error:
        print(f"import failed: {error}",file=sys.stderr)
        raise SystemExit(2)
