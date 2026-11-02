-- app.db, migration 1 (week 5 tables). data-design §2.1, §4.
-- Times are ISO 8601 UTC text in one fixed format (socxai.store.db.utc_now), so text
-- comparison orders them correctly.

CREATE TABLE users (
    id            INTEGER PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    display_name  TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('analyst', 'senior', 'model_owner')),
    password_hash TEXT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE incidents (
    incident_key TEXT PRIMARY KEY,
    org_id       INTEGER NOT NULL,
    incident_id  INTEGER NOT NULL,
    category     TEXT NOT NULL CHECK (category IN ('InitialAccess', 'SuspiciousActivity', 'Exfiltration')),
    slice        TEXT NOT NULL CHECK (slice = 'T2'),
    first_seen   TEXT NOT NULL,
    n_alerts     INTEGER NOT NULL CHECK (n_alerts >= 1),
    n_evidence   INTEGER NOT NULL CHECK (n_evidence >= 1),
    card_json    TEXT NOT NULL,
    data_version TEXT NOT NULL,
    UNIQUE (org_id, incident_id)
);
CREATE INDEX ix_incidents_slice_cat ON incidents (slice, category);

CREATE TABLE model_versions (
    version      TEXT PRIMARY KEY,
    kind         TEXT NOT NULL CHECK (kind IN ('baseline_lr', 'lgbm')),
    data_version TEXT NOT NULL,
    threshold    REAL NOT NULL CHECK (threshold > 0 AND threshold < 1),
    metrics_json TEXT NOT NULL,
    params_json  TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    is_active    INTEGER NOT NULL DEFAULT 0 CHECK (is_active IN (0, 1))
);
CREATE UNIQUE INDEX ux_model_active ON model_versions (is_active) WHERE is_active = 1;

CREATE TABLE suggestions (
    incident_key     TEXT NOT NULL REFERENCES incidents (incident_key),
    model_version    TEXT NOT NULL REFERENCES model_versions (version),
    predicted_class  TEXT NOT NULL CHECK (predicted_class IN ('TP', 'BP', 'FP')),
    confidence       REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    probs_json       TEXT NOT NULL,
    needs_review     INTEGER NOT NULL CHECK (needs_review IN (0, 1)),
    explanation_json TEXT NOT NULL,
    PRIMARY KEY (incident_key, model_version)
);

-- Audit trail (append-only, NFR-06).
CREATE TABLE decision_events (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_key         TEXT NOT NULL REFERENCES incidents (incident_key),
    version              INTEGER NULL CHECK (version IS NULL OR version >= 1),
    is_duplicate         INTEGER NOT NULL CHECK (is_duplicate IN (0, 1)),
    decision_type        TEXT NOT NULL CHECK (decision_type IN ('accept', 'correct', 'reject')),
    decided_class        TEXT NULL CHECK (decided_class IS NULL OR decided_class IN ('TP', 'BP', 'FP')),
    reason               TEXT NOT NULL CHECK (length(reason) <= 2000),
    suggested_class      TEXT NOT NULL CHECK (suggested_class IN ('TP', 'BP', 'FP')),
    suggested_confidence REAL NOT NULL CHECK (suggested_confidence >= 0 AND suggested_confidence <= 1),
    model_version        TEXT NOT NULL REFERENCES model_versions (version),
    data_version         TEXT NOT NULL,
    actor_user_id        INTEGER NOT NULL REFERENCES users (id),
    actor_role           TEXT NOT NULL CHECK (actor_role IN ('analyst', 'senior', 'model_owner')),
    opened_at            TEXT NOT NULL,
    decided_at           TEXT NOT NULL,
    CHECK ((is_duplicate = 1) = (version IS NULL)),
    CHECK ((decision_type = 'reject') = (decided_class IS NULL)),
    CHECK (decision_type = 'accept' OR length(trim(reason)) > 0),
    CHECK (decision_type <> 'correct' OR decided_class <> suggested_class),
    CHECK (decision_type <> 'accept' OR decided_class = suggested_class),
    CHECK (opened_at <= decided_at)
);
CREATE UNIQUE INDEX ux_decision_version ON decision_events (incident_key, version)
    WHERE version IS NOT NULL;
CREATE INDEX ix_decision_incident ON decision_events (incident_key, id);

CREATE TABLE system_events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ts            TEXT NOT NULL,
    event_type    TEXT NOT NULL CHECK (event_type IN
                      ('unauthorized', 'model_activated', 'model_trained', 'precheck_fallback')),
    actor_user_id INTEGER NULL REFERENCES users (id),
    actor_role    TEXT NULL,
    detail_json   TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE aliases (
    field     TEXT NOT NULL,
    raw_value TEXT NOT NULL,
    alias     TEXT NOT NULL UNIQUE,
    PRIMARY KEY (field, raw_value)
);

CREATE TRIGGER decision_events_no_update BEFORE UPDATE ON decision_events
BEGIN SELECT RAISE(ABORT, 'audit trail is append-only'); END;
CREATE TRIGGER decision_events_no_delete BEFORE DELETE ON decision_events
BEGIN SELECT RAISE(ABORT, 'audit trail is append-only'); END;
CREATE TRIGGER system_events_no_update BEFORE UPDATE ON system_events
BEGIN SELECT RAISE(ABORT, 'audit trail is append-only'); END;
CREATE TRIGGER system_events_no_delete BEFORE DELETE ON system_events
BEGIN SELECT RAISE(ABORT, 'audit trail is append-only'); END;

-- Effective decision: the highest version per incident (duplicates carry no version).
CREATE VIEW v_effective_decision AS
SELECT d.* FROM decision_events d
WHERE d.version IS NOT NULL
  AND d.version = (SELECT max(version) FROM decision_events x WHERE x.incident_key = d.incident_key);
