"""SQLite connections and forward-only migrations (data-design §5, §8)."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Literal

StoreKind = Literal["app", "labels", "participants"]

# Numbered, forward-only migrations per store; index i is user_version i + 1.
MIGRATIONS: dict[str, tuple[str, ...]] = {
    "app": ("schema_app.sql",),
    "labels": ("schema_labels.sql",),
    "participants": ("schema_participants.sql",),
}


def utc_now() -> str:
    """Current UTC time, ISO 8601 with microseconds and a ``Z`` suffix (fixed width)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def connect(path: Path | str) -> sqlite3.Connection:
    """Open a store: WAL journal, foreign keys on, ``sqlite3.Row`` rows.

    ``isolation_level=None`` leaves transactions explicit (``BEGIN IMMEDIATE`` in
    the decision service, data-design §5). ``":memory:"`` is accepted for tests.
    """
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), isolation_level=None, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if str(path) != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


def migrate(conn: sqlite3.Connection, kind: StoreKind) -> int:
    """Apply missing migrations in order; returns the resulting ``user_version``."""
    if kind not in MIGRATIONS:
        raise ValueError(f"unknown store kind {kind!r}")
    steps = MIGRATIONS[kind]
    current = conn.execute("PRAGMA user_version").fetchone()[0]
    if current > len(steps):
        raise RuntimeError(f"{kind} store is at version {current}, newer than this code ({len(steps)})")
    for i in range(current, len(steps)):
        sql = resources.files("socxai.store").joinpath(steps[i]).read_text(encoding="utf-8")
        # executescript commits any open transaction; wrap the step so it is atomic.
        conn.executescript(f"BEGIN;\n{sql}\nPRAGMA user_version = {i + 1};\nCOMMIT;")
    return len(steps)


def open_store(path: Path | str, kind: StoreKind) -> sqlite3.Connection:
    conn = connect(path)
    try:
        migrate(conn, kind)
    except BaseException:
        conn.close()
        raise
    return conn
