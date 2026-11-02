"""Seed the demo stores: users, the active model, a 300-incident T2 pool, cards, suggestions.

Pool (decision list item 3): stratified by category in proportion to T2, seed 42,
with at least 30 "needs review" suggestions and at least 30 wrong suggestions.
The GUIDE grade is used for selection only and is not written to app.db.

An existing app.db holds an audit trail and is never deleted: the script stops,
or with --reset moves the old files to app.db.bak-<UTC time>.

Usage: python scripts/seed_demo.py [--n 300] [--seed 42] [--reset]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from socxai.config import SPLIT_RATIOS, Settings
from socxai.data.cards import AliasBook, build_cards, compute_sentinels
from socxai.data.features import load_features, load_vocab, open_dataset, raw_values
from socxai.data.guide import compute_data_version, load_manifest
from socxai.data.mitre import load_mitre_names
from socxai.model import registry
from socxai.model.baseline import needs_review
from socxai.store.db import connect, migrate, utc_now
from socxai.store.suggestions import register_model, score_pool

DEMO_USERS: tuple[tuple[str, str, str], ...] = (
    ("analist1", "Analist 1", "analyst"),
    ("analist2", "Analist 2", "analyst"),
    ("kidemli1", "Kıdemli Analist 1", "senior"),
    ("modelci1", "Model Sorumlusu 1", "model_owner"),
)
MAX_ATTEMPTS = 100

log = logging.getLogger("seed_demo")


class SeedError(RuntimeError):
    pass


def _quotas(counts: pd.Series, n: int) -> dict[str, int]:
    """Largest-remainder allocation of n proportional to ``counts``."""
    exact = counts / counts.sum() * n
    base = np.floor(exact).astype(int)
    rest = n - int(base.sum())
    order = (exact - base).sort_values(ascending=False, kind="stable").index[:rest]
    base[order] += 1
    return {str(k): int(v) for k, v in base.items()}


def select_pool(pool: pd.DataFrame, n: int, seed: int, min_review: int, min_wrong: int
                ) -> tuple[pd.DataFrame, dict[str, Any]]:
    """``pool`` columns: category, needs_review (bool), wrong (bool); index incident_key."""
    if n > len(pool):
        raise SeedError(f"pool has {len(pool)} incidents, {n} requested")
    quotas = _quotas(pool["category"].value_counts().sort_index(), n)
    for attempt in range(MAX_ATTEMPTS):
        rng = np.random.default_rng(seed + attempt)
        parts = []
        for cat, q in quotas.items():
            members = pool.index[pool["category"] == cat]
            parts.extend(rng.choice(members, size=q, replace=False).tolist())
        chosen = pool.loc[parts]
        n_review, n_wrong = int(chosen["needs_review"].sum()), int(chosen["wrong"].sum())
        if n_review >= min_review and n_wrong >= min_wrong:
            return chosen, {"attempt": attempt, "seed_used": seed + attempt, "quotas": quotas,
                            "needs_review": n_review, "wrong": n_wrong}
    raise SeedError(f"no sample met the constraints in {MAX_ATTEMPTS} attempts")


def _backup_existing(app_db: Path) -> Path | None:
    if not app_db.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = app_db.with_name(f"{app_db.name}.bak-{stamp}")
    for suffix in ("", "-wal", "-shm"):
        src = app_db.with_name(app_db.name + suffix)
        if src.exists():
            src.rename(target.with_name(target.name + suffix))
    return target


def seed_demo(settings: Settings, n: int = 300, seed: int = 42, *, reset: bool = False,
              min_review: int = 30, min_wrong: int = 30, dataset_dir: Path | None = None,
              ) -> dict[str, Any]:
    if dataset_dir is None:
        dataset_dir = settings.processed_dir / compute_data_version(settings.guide_train_csv, SPLIT_RATIOS)[0]
    manifest = load_manifest(dataset_dir)
    version = registry.version_name(manifest.data_version)
    model = registry.load(version, settings.models_dir)
    meta = registry.load_meta(version, settings.models_dir)
    tau = float(meta["tau"])
    vocab = load_vocab(dataset_dir)

    X = load_features(dataset_dir, "T2")
    inc = pd.read_parquet(dataset_dir / "incidents.parquet").set_index("incident_key").loc[X.index]
    proba = model.predict_proba(X)
    pred = np.asarray(model.classes_)[proba.argmax(axis=1)]
    pool = pd.DataFrame({"category": inc["category"],
                         "needs_review": needs_review(proba.max(axis=1), tau),
                         "wrong": pred != inc["grade"].to_numpy()}, index=X.index)
    chosen, sel = select_pool(pool, n, seed, min_review, min_wrong)
    # Queue order: first-seen time, then org and incident id; aliases are numbered in this order.
    keys = inc.loc[chosen.index].sort_values(["first_seen", "org_id", "incident_id"]).index.tolist()

    app_db = settings.app_db
    if app_db.exists() and not reset:
        raise SeedError(f"{app_db} exists (audit trail); rerun with --reset to back it up and reseed")
    backup = _backup_existing(app_db) if reset else None

    ds = open_dataset(dataset_dir)
    try:
        sentinels = compute_sentinels(ds, "T1")
        aliases = AliasBook()
        cards = build_cards(ds, keys, sentinels, aliases, load_mitre_names(settings.mitre_csv))
    finally:
        ds.close()

    conn = connect(app_db)
    try:
        migrate(conn, "app")
        now = utc_now()
        conn.execute("BEGIN IMMEDIATE")
        try:
            conn.executemany(
                "INSERT INTO users (username, display_name, role, password_hash, created_at) "
                "VALUES (?, ?, ?, NULL, ?)", [(u, d, r, now) for u, d, r in DEMO_USERS])
            conn.executemany(
                "INSERT INTO incidents (incident_key, org_id, incident_id, category, slice, first_seen, "
                "n_alerts, n_evidence, card_json, data_version) VALUES (?, ?, ?, ?, 'T2', ?, ?, ?, ?, ?)",
                [(k, int(inc.at[k, "org_id"]), int(inc.at[k, "incident_id"]), cards[k]["category"],
                  cards[k]["first_seen"], cards[k]["n_alerts"], cards[k]["n_evidence"],
                  json.dumps(cards[k], ensure_ascii=False), manifest.data_version) for k in keys])
            n_aliases = aliases.save(conn)
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        owner = conn.execute("SELECT id FROM users WHERE role = 'model_owner'").fetchone()["id"]
        register_model(conn, version, "baseline_lr", manifest.data_version, tau,
                       meta["metrics"]["model"], {**meta["settings"], "tau_rule": meta["metrics"]["threshold"]["rule"]},
                       activate=True, actor_user_id=owner)
        X_pool = X.loc[keys]
        n_sugg = score_pool(conn, model, version, X_pool, raw_values(X_pool, vocab))
        counts = {t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
                  for t in ("users", "incidents", "suggestions", "aliases")}
        flagged = conn.execute("SELECT count(*) FROM suggestions WHERE needs_review = 1").fetchone()[0]
    finally:
        conn.close()

    for kind, path in (("labels", settings.labels_db), ("participants", settings.participants_db)):
        c = connect(path)
        try:
            migrate(c, kind)
        finally:
            c.close()

    return {"app_db": str(app_db), "backup": str(backup) if backup else None, "model_version": version,
            "tau": tau, "suggestions_written": n_sugg, "aliases_written": n_aliases,
            "counts": counts, "needs_review": int(flagged), "selection": sel,
            "categories": chosen["category"].value_counts().to_dict(),
            "mitre_names": bool(load_mitre_names(settings.mitre_csv))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--reset", action="store_true", help="back up an existing app.db and reseed")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        out = seed_demo(Settings.from_env(), args.n, args.seed, reset=args.reset)
    except (SeedError, FileNotFoundError, KeyError, ValueError) as exc:
        logging.error("%s", exc)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
