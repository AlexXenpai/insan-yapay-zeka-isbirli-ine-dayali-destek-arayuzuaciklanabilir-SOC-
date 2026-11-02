"""TC-02 (FR-26) and feature construction checks (ADR-0005, data-design §9.4)."""

from __future__ import annotations

import csv
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pytest

from socxai.config import CATEGORIES, VOCAB_SIZES
from socxai.data.features import (
    N_FEATURES,
    OTHER,
    Vocab,
    build_features,
    fit_vocab,
    load_features,
    load_vocab,
    open_dataset,
    raw_values,
    write_features,
)
from socxai.data.guide import build_incidents

FIXTURE = Path(__file__).parents[1] / "fixtures" / "guide_mini.csv"


@pytest.fixture
def dataset(tmp_path: Path) -> Path:
    m = build_incidents(FIXTURE, tmp_path / "processed")
    return tmp_path / "processed" / m.data_version


@pytest.fixture
def con(dataset: Path):
    c = open_dataset(dataset)
    yield c
    c.close()


def _fixture_rows(key: str) -> list[dict[str, str]]:
    org, inc = key.split("-")
    with FIXTURE.open(encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh)
                if r["OrgId"] == org and r["IncidentId"] == inc and r["IncidentGrade"]]


def test_vocab_sizes_and_roundtrip(con: duckdb.DuckDBPyConnection) -> None:
    vocab = fit_vocab(con, "T1")
    assert len(vocab.entity_types) == VOCAB_SIZES["entity"]
    assert len(vocab.roles) <= VOCAB_SIZES["roles"]
    assert len(vocab.techniques) == VOCAB_SIZES["mitre"]
    assert Vocab.from_json(vocab.to_json()) == vocab
    names = vocab.feature_names
    assert len(names) == N_FEATURES == len(set(names))
    assert all(f"cat={c}" in names for c in CATEGORIES)


def test_vocab_is_learned_from_t1_only(con: duckdb.DuckDBPyConnection) -> None:
    """TC-02: T2 values unseen in T1 fall into ``other``; the vocabulary does not change."""
    vocab = fit_vocab(con, "T1")
    before = vocab.to_json()
    t1_types = {r[0] for r in con.execute(
        "SELECT DISTINCT EntityType FROM evidence WHERE slice = 'T1'").fetchall()}
    df = build_features(con, vocab, "T2")
    assert vocab.to_json() == before and fit_vocab(con, "T1") == vocab

    # Expected 'other' count per T2 incident, computed independently.
    expected = dict(con.execute(f"""
        SELECT incident_key,
               count(*) FILTER (WHERE EntityType NOT IN ({", ".join(repr(e) for e in vocab.entity_types)}))
        FROM evidence WHERE slice = 'T2' GROUP BY 1""").fetchall())
    got = np.rint(np.expm1(df[f"entity={OTHER}"].astype(np.float64))).astype(int)
    assert got.to_dict() == expected
    assert sum(expected.values()) > 0, "fixture must exercise the other bucket"
    # A type outside the T1 vocabulary never becomes its own column.
    unseen = {r[0] for r in con.execute(
        "SELECT DISTINCT EntityType FROM evidence WHERE slice = 'T2'").fetchall()} - set(vocab.entity_types)
    assert unseen and not any(f"entity={u}" in df.columns for u in unseen)
    assert t1_types  # T1 non-empty


def test_feature_values_match_raw_rows(con: duckdb.DuckDBPyConnection) -> None:
    vocab = fit_vocab(con, "T1")
    frames = {s: build_features(con, vocab, s) for s in ("T1", "T2", "VAL", "TEST")}
    key, slice_ = next((k, s) for s, f in frames.items() for k in f.index if len(_fixture_rows(k)) >= 3)
    rows = _fixture_rows(key)
    raw = raw_values(frames[slice_].loc[key], vocab)

    assert raw["n_evidence"] == len(rows)
    assert raw["n_alerts"] == len({r["AlertId"] for r in rows})
    assert raw["n_entity_types"] == len({r["EntityType"] for r in rows})
    for e in vocab.entity_types:
        assert raw[f"entity={e}"] == sum(r["EntityType"] == e for r in rows)
    assert raw["role=Related"] == sum(r["EvidenceRole"] == "Related" for r in rows)
    assert raw["verdict=Malicious"] == sum(r["LastVerdict"] == "Malicious" for r in rows)
    assert raw["has_threat_family"] == sum(bool(r["ThreatFamily"]) for r in rows)
    techs = {t for r in rows for t in r["MitreTechniques"].split(";") if t}
    assert raw["n_techniques"] == len(techs)
    for t in vocab.techniques:
        assert raw[f"mitre={t}"] == int(t in techs)
    assert sum(raw[f"cat={c}"] for c in CATEGORIES) == 1


def test_domain_pii_verdicts_are_ignored(con: duckdb.DuckDBPyConnection) -> None:
    vocab = fit_vocab(con, "T1")
    assert not any("DomainPII" in n for n in vocab.feature_names)
    df = pd.concat(build_features(con, vocab, s) for s in ("T1", "T2", "VAL", "TEST"))
    verdict_total = int(raw_values(df, vocab)[[c for c in df.columns if c.startswith("verdict=")]].to_numpy().sum())
    expected = con.execute("SELECT count(*) FROM evidence WHERE LastVerdict IN "
                           "('Suspicious','Malicious','NoThreatsFound')").fetchone()
    assert expected is not None and verdict_total == expected[0]


def test_features_shape_dtype_and_order(con: duckdb.DuckDBPyConnection) -> None:
    vocab = fit_vocab(con, "T1")
    for s in ("T1", "T2", "VAL", "TEST"):
        df = build_features(con, vocab, s)
        keys = [r[0] for r in con.execute(
            f"SELECT incident_key FROM incidents WHERE slice = '{s}' "
            "ORDER BY first_seen, org_id, incident_id").fetchall()]
        assert list(df.index) == keys
        assert df.shape == (len(keys), N_FEATURES)
        assert (df.dtypes == np.float32).all()
        assert np.isfinite(df.to_numpy()).all() and (df.to_numpy() >= 0).all()


def test_feature_sources_cover_every_feature(con: duckdb.DuckDBPyConnection) -> None:
    vocab = fit_vocab(con, "T1")
    src = vocab.feature_sources()
    assert list(src) == vocab.feature_names
    assert src["entity=" + vocab.entity_types[0]] == ("EntityType", vocab.entity_types[0])
    assert src["n_alerts"] == ("AlertId", None)


def test_write_features_skips_locked_test(dataset: Path) -> None:
    vocab = write_features(dataset)
    assert load_vocab(dataset) == vocab
    assert load_features(dataset, "T1").shape[1] == N_FEATURES
    assert not (dataset / "features_TEST.parquet").exists()


def test_open_dataset_requires_built_files(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        open_dataset(tmp_path)
