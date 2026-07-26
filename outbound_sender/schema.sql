PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS queue (
    source_message_id TEXT PRIMARY KEY,
    draft_id TEXT NOT NULL UNIQUE,
    message_id TEXT NOT NULL UNIQUE,
    recipient TEXT,
    scheduled_at_utc TEXT,
    status TEXT NOT NULL CHECK (
        status IN ('blocked', 'pending', 'sending', 'sent', 'skipped', 'failed')
    ),
    prepared INTEGER NOT NULL DEFAULT 0 CHECK (prepared IN (0, 1)),
    attempts INTEGER NOT NULL DEFAULT 0,
    next_attempt_at_utc TEXT,
    sent_message_id TEXT,
    last_error TEXT,
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS queue_due_idx
ON queue(status, scheduled_at_utc, next_attempt_at_utc);

CREATE TABLE IF NOT EXISTS suppressions (
    recipient TEXT PRIMARY KEY,
    reason TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_message_id TEXT,
    event_type TEXT NOT NULL,
    detail TEXT,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (source_message_id) REFERENCES queue(source_message_id)
);
