PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ads (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('display', 'text')),
  title TEXT NOT NULL,
  campaign TEXT NOT NULL DEFAULT '',
  region TEXT NOT NULL DEFAULT '',
  aspect_ratio TEXT NOT NULL DEFAULT '',
  payload_json TEXT NOT NULL,
  creative_path TEXT,
  status TEXT NOT NULL DEFAULT 'pending_review' CHECK (
    status IN ('draft', 'pending_review', 'approved', 'rejected', 'queued', 'syncing', 'synced', 'failed')
  ),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ads_review_order
  ON ads (kind, status, created_at DESC);

CREATE TABLE IF NOT EXISTS review_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ad_id TEXT NOT NULL REFERENCES ads(id) ON DELETE CASCADE,
  decision TEXT NOT NULL CHECK (decision IN ('approved', 'rejected')),
  actor TEXT NOT NULL DEFAULT 'nate',
  note TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS review_events_ad
  ON review_events (ad_id, created_at DESC);

CREATE TABLE IF NOT EXISTS sync_jobs (
  id TEXT PRIMARY KEY,
  ad_id TEXT NOT NULL REFERENCES ads(id) ON DELETE CASCADE,
  operation TEXT NOT NULL DEFAULT 'upsert_asset',
  status TEXT NOT NULL DEFAULT 'queued' CHECK (
    status IN ('queued', 'syncing', 'synced', 'failed', 'cancelled')
  ),
  attempts INTEGER NOT NULL DEFAULT 0,
  idempotency_key TEXT NOT NULL UNIQUE,
  last_error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS one_active_sync_job_per_ad
  ON sync_jobs(ad_id)
  WHERE status IN ('queued', 'syncing');

CREATE TABLE IF NOT EXISTS sync_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT NOT NULL REFERENCES sync_jobs(id) ON DELETE CASCADE,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  outcome TEXT CHECK (outcome IN ('synced', 'failed', 'skipped')),
  request_fingerprint TEXT,
  external_resource_id TEXT,
  error TEXT
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS protect_unapproved_sync_jobs
BEFORE INSERT ON sync_jobs
WHEN (SELECT status FROM ads WHERE id = NEW.ad_id) != 'approved'
BEGIN
  SELECT RAISE(ABORT, 'only approved ads can enter the sync queue');
END;


CREATE TABLE IF NOT EXISTS campaign_reviews (
  plan_digest TEXT PRIMARY KEY,
  source_fingerprint TEXT NOT NULL,
  geography TEXT NOT NULL DEFAULT 'DMV',
  daily_budget_micros INTEGER NOT NULL DEFAULT 15000000
    CHECK (daily_budget_micros > 0),
  launch_status TEXT NOT NULL DEFAULT 'PAUSED'
    CHECK (launch_status IN ('PAUSED', 'ENABLED')),
  decision TEXT NOT NULL DEFAULT 'pending_review'
    CHECK (decision IN ('pending_review', 'approved', 'rejected')),
  actor TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS campaign_review_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  plan_digest TEXT NOT NULL REFERENCES campaign_reviews(plan_digest) ON DELETE CASCADE,
  decision TEXT NOT NULL CHECK (decision IN ('approved', 'rejected')),
  geography TEXT NOT NULL,
  daily_budget_micros INTEGER NOT NULL,
  launch_status TEXT NOT NULL CHECK (launch_status IN ('PAUSED', 'ENABLED')),
  actor TEXT NOT NULL DEFAULT 'nate',
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS campaign_review_events_plan
  ON campaign_review_events (plan_digest, created_at DESC);
