-- participants.db, migration 1. data-design §2.3 (used in weeks 15–16).
-- No identity data; deleting a participant cascades (FR-33). No immutability triggers.

CREATE TABLE participants (
    code            TEXT PRIMARY KEY,
    condition_order TEXT NOT NULL,
    "group"         TEXT NOT NULL CHECK ("group" IN ('student', 'soc')),
    created_at      TEXT NOT NULL
);

CREATE TABLE trials (
    id                 INTEGER PRIMARY KEY,
    code               TEXT NOT NULL REFERENCES participants (code) ON DELETE CASCADE,
    block              INTEGER NOT NULL,
    condition          TEXT NOT NULL CHECK (condition IN ('human', 'ai', 'ai_x')),
    incident_key       TEXT NOT NULL,
    decision           TEXT NOT NULL,
    duration_ms        INTEGER NOT NULL CHECK (duration_ms >= 0),
    ai_suggested_class TEXT NULL,
    ai_correct         INTEGER NULL CHECK (ai_correct IS NULL OR ai_correct IN (0, 1)),
    is_practice        INTEGER NOT NULL DEFAULT 0 CHECK (is_practice IN (0, 1)),
    ts                 TEXT NOT NULL
);

CREATE TABLE questionnaires (
    id         INTEGER PRIMARY KEY,
    code       TEXT NOT NULL REFERENCES participants (code) ON DELETE CASCADE,
    block      INTEGER NOT NULL,
    instrument TEXT NOT NULL CHECK (instrument IN ('SUS', 'NASA_TLX', 'JIAN', 'OPEN')),
    item       TEXT NOT NULL,
    value      TEXT NOT NULL
);
