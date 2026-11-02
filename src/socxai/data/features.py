"""Incident-level features (ADR-0005, data-design §9.4).

Vocabularies (most frequent values) are learned from T1 only and frozen; later
slices map unseen values to the ``other`` bucket. Every feature records its raw
field and value (``Vocab.feature_sources``) so explanations can show the raw
evidence behind a contribution (FR-05).

Cost: one grouped scan of the slice's evidence rows, O(R_slice) time; output is
I_slice × 60 float32.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import duckdb
import numpy as np
import pandas as pd

from socxai.config import CATEGORIES, VOCAB_SIZES

Transform = Literal["onehot", "log1p", "binary"]

EVIDENCE_ROLES: tuple[str, ...] = ("Impacted", "Related")
SUSPICION_LEVELS: tuple[str, ...] = ("Suspicious", "Incriminated")
# DomainPII_* verdicts are ignored (§9.4).
VERDICTS: tuple[str, ...] = ("Suspicious", "Malicious", "NoThreatsFound")
OTHER = "other"
N_FEATURES = 60


def open_dataset(dataset_dir: Path) -> duckdb.DuckDBPyConnection:
    """DuckDB connection with ``incidents`` and ``evidence`` views over a built dataset."""
    d = Path(dataset_dir)
    for name in ("incidents.parquet", "evidence.parquet"):
        if not (d / name).is_file():
            raise FileNotFoundError(f"{d / name} not found; run scripts/build_dataset.py first")
    con = duckdb.connect()
    for name in ("incidents", "evidence"):
        path = (d / f"{name}.parquet").as_posix().replace("'", "''")
        con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{path}')")
    return con


def _q(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _techniques_sql(slice_: str) -> str:
    """Distinct (incident, technique) pairs of a slice; MitreTechniques is ';'-separated."""
    return f"""
        SELECT DISTINCT incident_key, trim(t) AS technique
        FROM (SELECT incident_key, unnest(string_split(MitreTechniques, ';')) AS t
              FROM evidence WHERE slice = {_q(slice_)} AND MitreTechniques IS NOT NULL)
        WHERE trim(t) <> ''
    """


def _top(con: duckdb.DuckDBPyConnection, sql: str, k: int) -> tuple[str, ...]:
    # Ties broken alphabetically so the vocabulary is deterministic.
    rows = con.execute(f"SELECT v FROM ({sql}) ORDER BY n DESC, v ASC LIMIT {int(k)}").fetchall()
    return tuple(r[0] for r in rows)


@dataclass(frozen=True)
class Vocab:
    entity_types: tuple[str, ...]
    roles: tuple[str, ...]
    techniques: tuple[str, ...]
    fitted_on: str = "T1"

    @property
    def feature_names(self) -> list[str]:
        return list(self.feature_sources())

    def feature_sources(self) -> dict[str, tuple[str, str | None]]:
        """Feature → (raw field, raw value); value None means a count/aggregate."""
        src: dict[str, tuple[str, str | None]] = {}
        for c in CATEGORIES:
            src[f"cat={c}"] = ("Category", c)
        src["n_alerts"] = ("AlertId", None)
        src["n_evidence"] = ("Evidence", None)
        src["n_entity_types"] = ("EntityType", None)
        src["n_techniques"] = ("MitreTechniques", None)
        for e in self.entity_types:
            src[f"entity={e}"] = ("EntityType", e)
        src[f"entity={OTHER}"] = ("EntityType", OTHER)
        for r in EVIDENCE_ROLES:
            src[f"role={r}"] = ("EvidenceRole", r)
        for s in SUSPICION_LEVELS:
            src[f"suspicion={s}"] = ("SuspicionLevel", s)
        for v in VERDICTS:
            src[f"verdict={v}"] = ("LastVerdict", v)
        for r in self.roles:
            src[f"roles={r}"] = ("Roles", r)
        src[f"roles={OTHER}"] = ("Roles", OTHER)
        src["has_resource_type"] = ("ResourceType", None)
        src["has_threat_family"] = ("ThreatFamily", None)
        for t in self.techniques:
            src[f"mitre={t}"] = ("MitreTechniques", t)
        return src

    def transforms(self) -> dict[str, Transform]:
        out: dict[str, Transform] = {}
        for name in self.feature_names:
            if name.startswith("cat="):
                out[name] = "onehot"
            elif name.startswith("mitre="):
                out[name] = "binary"
            else:
                out[name] = "log1p"
        return out

    def to_json(self) -> str:
        return json.dumps({
            "fitted_on": self.fitted_on,
            "entity_types": list(self.entity_types),
            "roles": list(self.roles),
            "techniques": list(self.techniques),
        }, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, text: str) -> "Vocab":
        d = json.loads(text)
        return cls(tuple(d["entity_types"]), tuple(d["roles"]), tuple(d["techniques"]),
                   d.get("fitted_on", "T1"))


def fit_vocab(con: duckdb.DuckDBPyConnection, slice: str = "T1") -> Vocab:
    """Learn the top-k vocabularies from one slice (T1 by default, §9.4).

    Entity types and Roles are ranked by evidence-row count; techniques by the
    number of incidents that contain them (the feature is incident-level 0/1).
    """
    s = _q(slice)
    entity = _top(con, f"SELECT EntityType AS v, count(*) AS n FROM evidence "
                       f"WHERE slice = {s} AND EntityType IS NOT NULL GROUP BY 1",
                  VOCAB_SIZES["entity"])
    roles = _top(con, f"SELECT Roles AS v, count(*) AS n FROM evidence "
                      f"WHERE slice = {s} AND Roles IS NOT NULL GROUP BY 1",
                 VOCAB_SIZES["roles"])
    techniques = _top(con, f"SELECT technique AS v, count(*) AS n FROM ({_techniques_sql(slice)}) "
                           f"GROUP BY 1", VOCAB_SIZES["mitre"])
    if not entity:
        raise ValueError(f"slice {slice!r} has no evidence rows; cannot fit a vocabulary")
    return Vocab(entity, roles, techniques, fitted_on=slice)


def build_features(con: duckdb.DuckDBPyConnection, vocab: Vocab, slice: str) -> pd.DataFrame:
    """Feature matrix of one slice: index ``incident_key``, ``vocab.feature_names`` columns.

    Rows follow the split order (first_seen, org_id, incident_id). Values are
    float32 after the per-feature transform (one-hot, log1p of a count, or 0/1).
    """
    s = _q(slice)
    ent_in = ", ".join(_q(e) for e in vocab.entity_types)
    roles_in = ", ".join(_q(r) for r in vocab.roles) or "NULL"

    ev_cols = [
        "count(DISTINCT AlertId) AS \"n_alerts\"",
        "count(*) AS \"n_evidence\"",
        "count(DISTINCT EntityType) AS \"n_entity_types\"",
    ]
    for e in vocab.entity_types:
        ev_cols.append(f"count(*) FILTER (WHERE EntityType = {_q(e)}) AS {_ident('entity=' + e)}")
    ev_cols.append(f"count(*) FILTER (WHERE EntityType IS NOT NULL AND EntityType NOT IN ({ent_in})) "
                   f"AS {_ident('entity=' + OTHER)}")
    for r in EVIDENCE_ROLES:
        ev_cols.append(f"count(*) FILTER (WHERE EvidenceRole = {_q(r)}) AS {_ident('role=' + r)}")
    for lvl in SUSPICION_LEVELS:
        ev_cols.append(f"count(*) FILTER (WHERE SuspicionLevel = {_q(lvl)}) "
                       f"AS {_ident('suspicion=' + lvl)}")
    for v in VERDICTS:
        ev_cols.append(f"count(*) FILTER (WHERE LastVerdict = {_q(v)}) AS {_ident('verdict=' + v)}")
    for r in vocab.roles:
        ev_cols.append(f"count(*) FILTER (WHERE Roles = {_q(r)}) AS {_ident('roles=' + r)}")
    ev_cols.append(f"count(*) FILTER (WHERE Roles IS NOT NULL AND Roles NOT IN ({roles_in})) "
                   f"AS {_ident('roles=' + OTHER)}")
    ev_cols.append("count(*) FILTER (WHERE ResourceType IS NOT NULL) AS \"has_resource_type\"")
    ev_cols.append("count(*) FILTER (WHERE ThreatFamily IS NOT NULL) AS \"has_threat_family\"")

    tech_cols = ["count(*) AS \"n_techniques\""]
    for t in vocab.techniques:
        tech_cols.append(f"CAST(bool_or(technique = {_q(t)}) AS INTEGER) AS {_ident('mitre=' + t)}")

    cat_cols = [f"CAST(i.category = {_q(c)} AS INTEGER) AS {_ident('cat=' + c)}" for c in CATEGORIES]

    sql = f"""
        WITH ev AS (SELECT incident_key, {", ".join(ev_cols)}
                    FROM evidence WHERE slice = {s} GROUP BY incident_key),
             tech AS (SELECT incident_key, {", ".join(tech_cols)}
                      FROM ({_techniques_sql(slice)}) GROUP BY incident_key)
        SELECT i.incident_key, {", ".join(cat_cols)}, ev.* EXCLUDE (incident_key),
               tech.* EXCLUDE (incident_key)
        FROM incidents i
        JOIN ev USING (incident_key)
        LEFT JOIN tech USING (incident_key)
        WHERE i.slice = {s}
        ORDER BY i.first_seen, i.org_id, i.incident_id
    """
    df = con.execute(sql).df().set_index("incident_key")
    names = vocab.feature_names
    df = df.reindex(columns=names).fillna(0)  # incidents without techniques
    transforms = vocab.transforms()
    log_cols = [c for c in names if transforms[c] == "log1p"]
    df[log_cols] = np.log1p(df[log_cols].astype(np.float64))
    df = df.astype(np.float32)
    if df.shape[1] != N_FEATURES:
        raise AssertionError(f"expected {N_FEATURES} features, got {df.shape[1]}")
    return df


def raw_values(features: pd.Series | pd.DataFrame, vocab: Vocab) -> pd.Series | pd.DataFrame:
    """Invert the transforms: counts for log1p features, 0/1 for the rest (FR-05)."""
    transforms = vocab.transforms()
    out = features.astype(np.float64).copy()
    log_cols = [c for c in vocab.feature_names if transforms[c] == "log1p"]
    out[log_cols] = np.rint(np.expm1(out[log_cols]))
    return out.round().astype(np.int64)


def _ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def write_features(dataset_dir: Path, slices: tuple[str, ...] = ("T1", "T2", "VAL")) -> Vocab:
    """Fit the vocabulary on T1 and write ``vocab.json`` and ``features_<slice>.parquet``.

    The locked TEST slice is not featurised here; it is read only for the final
    evaluation (experiment plan).
    """
    d = Path(dataset_dir)
    con = open_dataset(d)
    try:
        vocab = fit_vocab(con, "T1")
        (d / "vocab.json").write_text(vocab.to_json(), encoding="utf-8")
        for s in slices:
            build_features(con, vocab, s).to_parquet(d / f"features_{s}.parquet")
    finally:
        con.close()
    return vocab


def load_features(dataset_dir: Path, slice: str) -> pd.DataFrame:
    return pd.read_parquet(Path(dataset_dir) / f"features_{slice}.parquet")


def load_vocab(dataset_dir: Path) -> Vocab:
    return Vocab.from_json((Path(dataset_dir) / "vocab.json").read_text(encoding="utf-8"))
