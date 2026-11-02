-- labels.db, migration 1. data-design §2.2. Written only by review.approve and
-- review.bulk_approve (weeks 9–10); created empty now.

CREATE TABLE training_labels (
    id              INTEGER PRIMARY KEY,
    incident_key    TEXT NOT NULL,
    label           TEXT NOT NULL CHECK (label IN ('TP', 'BP', 'FP')),
    source_event_id INTEGER NOT NULL UNIQUE,
    review_event_id INTEGER NOT NULL UNIQUE,
    approved_by     TEXT NOT NULL,
    approved_at     TEXT NOT NULL,
    data_version    TEXT NOT NULL
);
CREATE INDEX ix_training_labels_incident ON training_labels (incident_key, approved_at);

CREATE TRIGGER training_labels_no_update BEFORE UPDATE ON training_labels
BEGIN SELECT RAISE(ABORT, 'training labels are append-only'); END;
CREATE TRIGGER training_labels_no_delete BEFORE DELETE ON training_labels
BEGIN SELECT RAISE(ABORT, 'training labels are append-only'); END;

-- Latest approved label per incident.
CREATE VIEW v_current_label AS
SELECT t.* FROM training_labels t
WHERE t.id = (SELECT x.id FROM training_labels x WHERE x.incident_key = t.incident_key
              ORDER BY x.approved_at DESC, x.id DESC LIMIT 1);
