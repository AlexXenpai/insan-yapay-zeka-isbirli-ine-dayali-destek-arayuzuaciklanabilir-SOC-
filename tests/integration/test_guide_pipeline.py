"""TC-01 (FR-26, AC-26): incident table and leak-free four-slice split.

The checks re-derive every property from the written Parquet files instead of
trusting the manifest's own leak checks.
"""

from __future__ import annotations

import csv
from pathlib import Path

import duckdb
import pytest

from socxai.config import CATEGORIES, SLICES, SPLIT_RATIOS, Settings
from socxai.data.guide import (
    Manifest,
    PipelineError,
    build_incidents,
    compute_data_version,
    load_manifest,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "guide_mini.csv"
N_FIXTURE_IN_SCOPE = 40


def _row(con: duckdb.DuckDBPyConnection, sql: str) -> tuple:
    row = con.execute(sql).fetchone()
    assert row is not None, sql
    return row


def _one(con: duckdb.DuckDBPyConnection, sql: str):
    return _row(con, sql)[0]


def assert_split_is_leak_free(dataset_dir: Path, manifest: Manifest) -> None:
    con = duckdb.connect()
    inc = (dataset_dir / "incidents.parquet").as_posix()
    ev = (dataset_dir / "evidence.parquet").as_posix()

    n = _one(con, f"SELECT count(*) FROM '{inc}'")
    assert n == manifest.n_incidents

    # Keys are unique, so slices are pairwise disjoint.
    assert _one(con, f"SELECT count(DISTINCT incident_key) FROM '{inc}'") == n
    for a in SLICES:
        for b in SLICES:
            if a < b:
                overlap = _one(con, f"""
                    SELECT count(*) FROM (SELECT incident_key FROM '{inc}' WHERE slice = '{a}')
                    JOIN (SELECT incident_key FROM '{inc}' WHERE slice = '{b}') USING (incident_key)
                """)
                assert overlap == 0, (a, b)

    # Time order across consecutive slices.
    bounds = dict((s, (lo, hi)) for s, lo, hi in con.execute(
        f"SELECT slice, min(first_seen), max(first_seen) FROM '{inc}' GROUP BY slice").fetchall())
    assert set(bounds) == set(SLICES)
    for prev, nxt in zip(SLICES, SLICES[1:]):
        assert bounds[prev][1] <= bounds[nxt][0], (prev, nxt)

    # Only the three in-scope categories, no unlabelled incident.
    cats = {r[0] for r in con.execute(f"SELECT DISTINCT category FROM '{inc}'").fetchall()}
    assert cats <= set(CATEGORIES)
    grades = {r[0] for r in con.execute(f"SELECT DISTINCT grade FROM '{inc}'").fetchall()}
    assert grades <= {"TP", "BP", "FP"} and None not in grades

    # Slice sizes: within one incident of the exact ratio.
    sizes = dict(con.execute(f"SELECT slice, count(*) FROM '{inc}' GROUP BY slice").fetchall())
    for s, r in zip(SLICES, SPLIT_RATIOS):
        assert abs(sizes[s] - r * n) <= 1, (s, sizes[s], r * n)

    # Every evidence row belongs to an in-scope incident and to that incident's slice.
    mismatched = _one(con, f"""
        SELECT count(*) FROM '{ev}' e LEFT JOIN '{inc}' i USING (incident_key)
        WHERE i.incident_key IS NULL OR e.slice <> i.slice
    """)
    assert mismatched == 0
    assert _one(con, f"SELECT count(*) FROM '{ev}'") == manifest.n_evidence_rows
    assert _one(con, f"SELECT sum(n_evidence) FROM '{inc}'") == manifest.n_evidence_rows
    assert all(manifest.leak_checks.values())
    con.close()


@pytest.fixture
def built(tmp_path: Path) -> tuple[Path, Manifest]:
    out = tmp_path / "processed"
    manifest = build_incidents(FIXTURE, out)
    return out / manifest.data_version, manifest


def test_fixture_split_is_leak_free(built: tuple[Path, Manifest]) -> None:
    dataset_dir, manifest = built
    assert manifest.n_incidents == N_FIXTURE_IN_SCOPE
    assert manifest.excluded["out_of_scope_incidents"] == 4
    assert manifest.excluded["unlabelled_rows"] > 0
    assert_split_is_leak_free(dataset_dir, manifest)
    assert load_manifest(dataset_dir) == manifest
    assert not any(p.name.endswith(".tmp") for p in dataset_dir.parent.iterdir())


def test_incident_category_majority_and_alphabetical_tie(built: tuple[Path, Manifest]) -> None:
    dataset_dir, _ = built
    con = duckdb.connect()
    cat = dict(con.execute(
        f"SELECT incident_key, category FROM '{(dataset_dir / 'incidents.parquet').as_posix()}'"
    ).fetchall())
    assert cat["1-201"] == "SuspiciousActivity"  # 2 alerts vs 1
    assert cat["2-202"] == "Exfiltration"  # 1 vs 1 -> alphabetical first


def test_unlabelled_and_out_of_scope_are_excluded(built: tuple[Path, Manifest]) -> None:
    dataset_dir, _ = built
    con = duckdb.connect()
    inc = (dataset_dir / "incidents.parquet").as_posix()
    keys = {r[0] for r in con.execute(f"SELECT incident_key FROM '{inc}'").fetchall()}
    for k in ("0-301", "1-302", "2-303", "0-401", "1-402", "2-403", "3-404"):
        assert k not in keys
    # Partly unlabelled incident stays, with only its labelled rows and alerts.
    raw = [r for r in csv.DictReader(FIXTURE.open(encoding="utf-8"))
           if r["OrgId"] == "0" and r["IncidentId"] == "204"]
    labelled = [r for r in raw if r["IncidentGrade"]]
    assert 0 < len(labelled) < len(raw)
    n_alerts, n_evidence = _row(con, 
        f"SELECT n_alerts, n_evidence FROM '{inc}' WHERE incident_key = '0-204'")
    assert n_evidence == len(labelled)
    assert n_alerts == len({r["AlertId"] for r in labelled})


def test_ordering_tie_break_by_org_then_incident(built: tuple[Path, Manifest]) -> None:
    dataset_dir, _ = built
    con = duckdb.connect()
    order = [r[0] for r in con.execute(f"""
        SELECT incident_key FROM '{(dataset_dir / 'incidents.parquet').as_posix()}'
        ORDER BY first_seen, org_id, incident_id""").fetchall()]
    assert order.index("0-204") < order.index("3-203")


def test_rebuild_is_deterministic(tmp_path: Path, built: tuple[Path, Manifest]) -> None:
    dataset_dir, manifest = built
    again = build_incidents(FIXTURE, dataset_dir.parent)  # overwrites the same version
    assert again == manifest
    assert compute_data_version(FIXTURE, SPLIT_RATIOS)[0] == manifest.data_version


def test_data_version_depends_on_ratios() -> None:
    v1, _ = compute_data_version(FIXTURE, SPLIT_RATIOS)
    v2, _ = compute_data_version(FIXTURE, (0.4, 0.3, 0.15, 0.15))
    assert v1 != v2 and len(v1) == 12


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        build_incidents(tmp_path / "absent.csv", tmp_path / "out")


@pytest.mark.parametrize("ratios", [(0.5, 0.5), (0.5, 0.2, 0.2, 0.2), (0.6, 0.4, 0.0, 0.0)])
def test_invalid_ratios_raise(tmp_path: Path, ratios: tuple[float, ...]) -> None:
    with pytest.raises(ValueError):
        build_incidents(FIXTURE, tmp_path / "out", ratios)  # type: ignore[arg-type]


def _rewrite(src: Path, dst: Path, mutate) -> None:
    with src.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames or [])
        rows = [mutate(dict(r)) for r in reader]
    fields = [f for f in fields if f in rows[0]]
    with dst.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def test_incident_with_two_grades_raises(tmp_path: Path) -> None:
    flipped = {"done": False}

    def mutate(r: dict) -> dict:
        if r["OrgId"] == "1" and r["IncidentId"] == "201" and not flipped["done"]:
            r["IncidentGrade"] = "FalsePositive"
            flipped["done"] = True
        return r

    bad = tmp_path / "bad.csv"
    _rewrite(FIXTURE, bad, mutate)
    with pytest.raises(PipelineError, match="more than one IncidentGrade"):
        build_incidents(bad, tmp_path / "out")
    assert not any((tmp_path / "out").glob("*")), "failed build must leave no output"


def test_missing_column_raises(tmp_path: Path) -> None:
    def mutate(r: dict) -> dict:
        r.pop("EntityType")
        return r

    bad = tmp_path / "bad.csv"
    _rewrite(FIXTURE, bad, mutate)
    with pytest.raises(PipelineError, match="missing columns"):
        build_incidents(bad, tmp_path / "out")


def test_unparsable_timestamp_raises(tmp_path: Path) -> None:
    def mutate(r: dict) -> dict:
        if r["IncidentId"] == "101":
            r["Timestamp"] = "not-a-time"
        return r

    bad = tmp_path / "bad.csv"
    _rewrite(FIXTURE, bad, mutate)
    with pytest.raises(PipelineError, match="unparsable Timestamp"):
        build_incidents(bad, tmp_path / "out")


@pytest.mark.realdata
def test_real_guide_split_is_leak_free(real_settings: Settings, tmp_path: Path) -> None:
    """Uses the dataset built by scripts/build_dataset.py; builds it if absent."""
    raw = real_settings.guide_train_csv
    version, _ = compute_data_version(raw, SPLIT_RATIOS)
    dataset_dir = real_settings.processed_dir / version
    if not (dataset_dir / "manifest.json").exists():
        build_incidents(raw, real_settings.processed_dir)
    manifest = load_manifest(dataset_dir)
    assert manifest.data_version == version
    assert_split_is_leak_free(dataset_dir, manifest)
