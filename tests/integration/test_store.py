"""TC-13 (NFR-06) and schema checks; demo seeding on the fixture (TC-17 core)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from socxai.store.db import MIGRATIONS, connect, migrate, open_store, utc_now
from conftest import load_script

@pytest.fixture
def app(tmp_path: Path):
    conn = open_store(tmp_path / "app.db", "app")
    now = utc_now()
    conn.execute("INSERT INTO users (username, display_name, role, created_at) VALUES "
                 "('a1', 'A', 'analyst', ?)", (now,))
    conn.execute("INSERT INTO incidents VALUES ('1-2', 1, 2, 'InitialAccess', 'T2', ?, 1, 1, '{}', 'dv')",
                 (now,))
    conn.execute("INSERT INTO model_versions VALUES ('v1-lr-dv0000', 'baseline_lr', 'dv', 0.5, '{}', '{}', ?, 1)",
                 (now,))
    yield conn
    conn.close()


def _decision(conn: sqlite3.Connection, **over) -> int:
    now = utc_now()
    row = {"incident_key": "1-2", "version": 1, "is_duplicate": 0, "decision_type": "accept",
           "decided_class": "TP", "reason": "", "suggested_class": "TP", "suggested_confidence": 0.7,
           "model_version": "v1-lr-dv0000", "data_version": "dv", "actor_user_id": 1,
           "actor_role": "analyst", "opened_at": now, "decided_at": now, **over}
    cols = ", ".join(row)
    cur = conn.execute(f"INSERT INTO decision_events ({cols}) VALUES ({', '.join('?' * len(row))})",
                       tuple(row.values()))
    return int(cur.lastrowid or 0)


def test_migrate_is_idempotent_and_versioned(tmp_path: Path) -> None:
    for kind in MIGRATIONS:
        conn = connect(tmp_path / f"{kind}.db")
        assert migrate(conn, kind) == len(MIGRATIONS[kind])  # type: ignore[arg-type]
        assert migrate(conn, kind) == len(MIGRATIONS[kind])  # type: ignore[arg-type]
        assert conn.execute("PRAGMA user_version").fetchone()[0] == len(MIGRATIONS[kind])
        conn.close()
    conn = connect(tmp_path / "app.db")
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    with pytest.raises(ValueError):
        migrate(conn, "nope")  # type: ignore[arg-type]
    conn.execute("PRAGMA user_version = 99")
    with pytest.raises(RuntimeError):
        migrate(conn, "app")
    conn.close()


@pytest.mark.parametrize("table", ["decision_events", "system_events"])
def test_audit_trail_is_append_only(app: sqlite3.Connection, table: str) -> None:
    """TC-13: UPDATE and DELETE abort."""
    if table == "decision_events":
        _decision(app)
    else:
        app.execute("INSERT INTO system_events (ts, event_type) VALUES (?, 'unauthorized')", (utc_now(),))
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        app.execute(f"UPDATE {table} SET id = id")
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        app.execute(f"DELETE FROM {table}")
    assert app.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 1


def test_labels_store_is_append_only(tmp_path: Path) -> None:
    conn = open_store(tmp_path / "labels.db", "labels")
    conn.execute("INSERT INTO training_labels VALUES (1, '1-2', 'TP', 10, 20, 'k1', ?, 'dv')", (utc_now(),))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM training_labels")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO training_labels VALUES (2, '1-2', 'XX', 11, 21, 'k1', 't', 'dv')")
    conn.close()


@pytest.mark.parametrize("over", [
    {"decision_type": "reject", "decided_class": "TP", "reason": "x"},          # reject ⇔ NULL class
    {"decision_type": "reject", "decided_class": None, "reason": "   "},       # reason required
    {"decision_type": "correct", "decided_class": "TP", "reason": "x"},        # same as suggestion
    {"decision_type": "accept", "decided_class": "BP"},                         # accept = suggested
    {"version": None, "is_duplicate": 0},                                       # duplicate ⇔ NULL version
    {"reason": "x" * 2001, "decision_type": "correct", "decided_class": "BP"},  # length cap
    {"opened_at": "2099-01-01T00:00:00.000000Z"},                               # opened ≤ decided
    {"actor_user_id": 999},                                                     # FK
])
def test_decision_constraints(app: sqlite3.Connection, over: dict) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        _decision(app, **over)


def test_version_unique_and_effective_view(app: sqlite3.Connection) -> None:
    _decision(app)
    with pytest.raises(sqlite3.IntegrityError):
        _decision(app)  # same (incident, version)
    _decision(app, version=None, is_duplicate=1)
    _decision(app, version=2, decision_type="correct", decided_class="FP", reason="kanıt")
    eff = app.execute("SELECT version, decided_class FROM v_effective_decision WHERE incident_key='1-2'").fetchall()
    assert [tuple(r) for r in eff] == [(2, "FP")]


def test_single_active_model(app: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        app.execute("INSERT INTO model_versions VALUES ('v2', 'baseline_lr', 'dv', 0.5, '{}', '{}', 't', 1)")


def test_seed_demo_on_fixture(demo) -> None:
    settings, out, _, _ = demo
    assert out["counts"]["incidents"] == 6 and out["counts"]["suggestions"] == 6
    assert out["counts"]["users"] == 4
    conn = connect(settings.app_db)
    try:
        # TC-17 core: class, confidence in [0, 1], active version.
        rows = conn.execute("""SELECT s.*, m.threshold FROM suggestions s
                               JOIN model_versions m ON m.version = s.model_version AND m.is_active = 1""").fetchall()
        assert len(rows) == 6
        for r in rows:
            assert r["predicted_class"] in ("TP", "BP", "FP")
            assert 0.0 <= r["confidence"] <= 1.0
            assert r["needs_review"] == int(r["confidence"] < r["threshold"])
            probs = json.loads(r["probs_json"])
            assert abs(sum(probs.values()) - 1) < 1e-9 and max(probs.values()) == pytest.approx(r["confidence"])
            expl = json.loads(r["explanation_json"])
            assert expl["model_version"] == r["model_version"] and expl["target_class"] == r["predicted_class"]
        assert conn.execute("SELECT count(*) FROM system_events WHERE event_type='model_activated'").fetchone()[0] == 1
        # The GUIDE grade is not stored anywhere in app.db.
        cols = {c["name"] for c in conn.execute("PRAGMA table_info(incidents)").fetchall()}
        assert "grade" not in cols
    finally:
        conn.close()
    assert settings.labels_db.exists() and settings.participants_db.exists()


def test_seed_refuses_existing_db_and_backs_up_on_reset(demo) -> None:
    settings, _, seed, dataset = demo
    with pytest.raises(seed.SeedError, match="exists"):
        seed.seed_demo(settings, n=6, min_review=0, min_wrong=0, dataset_dir=dataset)
    out = seed.seed_demo(settings, n=6, min_review=0, min_wrong=0, dataset_dir=dataset, reset=True)
    assert out["backup"] and Path(out["backup"]).exists()


def test_select_pool_constraints() -> None:
    import pandas as pd
    seed = load_script("seed_demo")
    pool = pd.DataFrame({"category": ["A"] * 6 + ["B"] * 4, "needs_review": [True, False] * 5,
                         "wrong": [False] * 9 + [True]}, index=[f"k{i}" for i in range(10)])
    chosen, info = seed.select_pool(pool, 5, 42, min_review=1, min_wrong=1)
    assert len(chosen) == 5 and info["quotas"] == {"A": 3, "B": 2}
    assert chosen["wrong"].sum() >= 1
    with pytest.raises(seed.SeedError):
        seed.select_pool(pool, 5, 42, min_review=0, min_wrong=2)
    with pytest.raises(seed.SeedError):
        seed.select_pool(pool, 11, 42, min_review=0, min_wrong=0)
