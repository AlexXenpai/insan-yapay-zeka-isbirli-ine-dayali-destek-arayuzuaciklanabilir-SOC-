"""Model suggestions for the incidents in app.db (FR-03, FR-04, FR-05)."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

import numpy as np
import pandas as pd

from socxai.model.baseline import BaselineModel, needs_review
from socxai.model.explain import explain_linear
from socxai.store.db import utc_now


def register_model(conn: sqlite3.Connection, version: str, kind: str, data_version: str,
                   threshold: float, metrics: dict[str, Any], params: dict[str, Any],
                   activate: bool = True, actor_user_id: int | None = None) -> None:
    """Insert a model version; optionally make it the single active one (logged, FR-21)."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute(
            "INSERT INTO model_versions (version, kind, data_version, threshold, metrics_json, "
            "params_json, created_at, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, 0)",
            (version, kind, data_version, float(threshold), json.dumps(metrics), json.dumps(params),
             utc_now()))
        if activate:
            conn.execute("UPDATE model_versions SET is_active = 0 WHERE is_active = 1")
            conn.execute("UPDATE model_versions SET is_active = 1 WHERE version = ?", (version,))
            conn.execute(
                "INSERT INTO system_events (ts, event_type, actor_user_id, detail_json) "
                "VALUES (?, 'model_activated', ?, ?)",
                (utc_now(), actor_user_id, json.dumps({"version": version, "threshold": threshold})))
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise


def score_pool(app_conn: sqlite3.Connection, model: BaselineModel, version: str,
               X: pd.DataFrame, raw: pd.DataFrame) -> int:
    """Write one suggestion per row of ``X`` for ``version``; returns the number written.

    ``X`` holds model inputs (index ``incident_key``); ``raw`` the matching raw values.
    The threshold is the one registered for ``version``.
    """
    row = app_conn.execute("SELECT threshold FROM model_versions WHERE version = ?", (version,)).fetchone()
    if row is None:
        raise KeyError(f"model version {version!r} is not registered")
    tau = float(row["threshold"])
    if not X.index.equals(raw.index):
        raise ValueError("X and raw must share the same index")
    if model.version is None:
        model.version = version

    proba = model.predict_proba(X)
    classes = model.classes_
    records = []
    for i, key in enumerate(X.index):
        p = proba[i]
        k = int(np.argmax(p))
        conf = float(p[k])
        expl = explain_linear(model, X.iloc[i], raw.iloc[i], target_class=classes[k])
        records.append((
            str(key), version, classes[k], conf,
            json.dumps({c: float(p[j]) for j, c in enumerate(classes)}),
            int(needs_review(conf, tau)),
            json.dumps(expl, ensure_ascii=False),
        ))
    app_conn.execute("BEGIN IMMEDIATE")
    try:
        app_conn.executemany(
            "INSERT INTO suggestions (incident_key, model_version, predicted_class, confidence, "
            "probs_json, needs_review, explanation_json) VALUES (?, ?, ?, ?, ?, ?, ?)", records)
        app_conn.execute("COMMIT")
    except BaseException:
        app_conn.execute("ROLLBACK")
        raise
    return len(records)
