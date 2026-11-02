"""GUIDE ingestion: incident table, four-slice time-ordered split, evidence table.

Rules: data-design §9.2 (incident table), §9.3 (split, leak checks), §9.7 (data
version). The raw CSV is evidence-level (one row per alert × entity); everything
here runs in DuckDB so the 2.4 GB file is streamed instead of loaded into pandas.

Cost: one CSV scan plus hash aggregations, O(R) time for R rows; the split sorts
the I in-scope incidents, O(I log I). Memory is capped by ``memory_limit`` and
spills to ``temp_directory`` beyond it.
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import duckdb

from socxai import __version__
from socxai.config import CATEGORIES, PIPELINE_VERSION, SLICES, SPLIT_RATIOS, VOCAB_SIZES

log = logging.getLogger(__name__)

GRADE_MAP: dict[str, str] = {
    "TruePositive": "TP",
    "BenignPositive": "BP",
    "FalsePositive": "FP",
}

# Raw columns kept in evidence.parquet: needed by features (§9.4) and case cards (§9.6).
EVIDENCE_COLUMNS: tuple[str, ...] = (
    "AlertId",
    "Category",
    "MitreTechniques",
    "EntityType",
    "EvidenceRole",
    "SuspicionLevel",
    "LastVerdict",
    "Roles",
    "ResourceType",
    "ThreatFamily",
    # Primary identity fields used for aliases (§9.6).
    "AccountObjectId",
    "DeviceId",
    "IpAddress",
    "Url",
    "Sha256",
    "NetworkMessageId",
    "AccountUpn",
    "ApplicationId",
)

REQUIRED_RAW_COLUMNS: frozenset[str] = frozenset(
    {"OrgId", "IncidentId", "Timestamp", "IncidentGrade", *EVIDENCE_COLUMNS}
)


class PipelineError(RuntimeError):
    """Raised when the raw data violates an assumption the pipeline relies on."""


@dataclass(frozen=True)
class Manifest:
    data_version: str
    created_by: str
    params: dict[str, Any]
    inputs: list[dict[str, Any]]
    n_raw_rows: int
    n_incidents: int
    n_evidence_rows: int
    slice_counts: dict[str, dict[str, int]]
    slice_time_ranges: dict[str, dict[str, str]]
    leak_checks: dict[str, bool]
    excluded: dict[str, int] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, text: str) -> "Manifest":
        return cls(**json.loads(text))

    def summary(self) -> str:
        lines = [f"data_version={self.data_version}  incidents={self.n_incidents}  "
                 f"evidence_rows={self.n_evidence_rows}"]
        for s in SLICES:
            counts = self.slice_counts[s]
            total = sum(counts.values())
            share = total / self.n_incidents if self.n_incidents else 0.0
            rng = self.slice_time_ranges[s]
            classes = " ".join(f"{k}={counts.get(k, 0)}" for k in GRADE_MAP.values())
            lines.append(f"  {s:<4} n={total:<7} ({share:6.2%})  {classes}  "
                         f"[{rng['min']} .. {rng['max']}]")
        lines.append("  leak_checks: " + ", ".join(f"{k}={v}" for k, v in self.leak_checks.items()))
        return "\n".join(lines)


def _scalar(con: duckdb.DuckDBPyConnection, sql: str) -> Any:
    row = con.execute(sql).fetchone()
    if row is None:
        raise PipelineError(f"query returned no row: {sql.strip()[:80]}")
    return row[0]


def _validate_ratios(ratios: tuple[float, ...]) -> None:
    if len(ratios) != len(SLICES):
        raise ValueError(f"expected {len(SLICES)} ratios, got {len(ratios)}")
    if any(r <= 0 for r in ratios) or abs(sum(ratios) - 1.0) > 1e-9:
        raise ValueError(f"ratios must be positive and sum to 1, got {ratios}")


def compute_data_version(raw_csv: Path, ratios: tuple[float, ...]) -> tuple[str, list[dict[str, Any]]]:
    """First 12 hex chars of a SHA-256 over input metadata and pipeline parameters (§9.7)."""
    stat = raw_csv.stat()
    inputs = [{"name": raw_csv.name, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}]
    payload = {
        "inputs": inputs,
        "ratios": list(ratios),
        "categories": list(CATEGORIES),
        "vocab_sizes": VOCAB_SIZES,
        "pipeline_version": PIPELINE_VERSION,
        "code_version": __version__,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return digest[:12], inputs


def _sql_list(values: tuple[str, ...]) -> str:
    return ", ".join("'" + v.replace("'", "''") + "'" for v in values)


def _slice_case(n: int, ratios: tuple[float, ...]) -> str:
    """CASE expression mapping a 1-based rank to a slice by cumulative cut points.

    Cut k is round(n * cumulative_ratio_k), so each slice is within one incident
    of its exact share (TC-01).
    """
    cum = 0.0
    parts = []
    for name, r in zip(SLICES[:-1], ratios[:-1]):
        cum += r
        parts.append(f"WHEN rn <= {round(n * cum)} THEN '{name}'")
    return "CASE " + " ".join(parts) + f" ELSE '{SLICES[-1]}' END"


def _connect(work_dir: Path, memory_limit: str, threads: int | None) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    tmp = (work_dir / "duckdb_tmp").as_posix().replace("'", "''")
    con.execute(f"SET memory_limit = '{memory_limit}'")
    con.execute(f"SET temp_directory = '{tmp}'")
    con.execute("SET preserve_insertion_order = false")
    if threads:
        con.execute(f"SET threads = {int(threads)}")
    return con


def _check_columns(con: duckdb.DuckDBPyConnection, csv_sql: str) -> None:
    cols = {r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {csv_sql}").fetchall()}
    missing = sorted(REQUIRED_RAW_COLUMNS - cols)
    if missing:
        raise PipelineError(f"raw CSV is missing columns: {missing}")


def build_incidents(
    raw_csv: Path,
    out_root: Path,
    ratios: tuple[float, float, float, float] = SPLIT_RATIOS,
    *,
    memory_limit: str = "4GB",
    threads: int | None = None,
) -> Manifest:
    """Build ``<out_root>/<data_version>/{incidents,evidence}.parquet`` and ``manifest.json``.

    Raises ``FileNotFoundError`` if the CSV is absent, ``PipelineError`` if the data
    breaks an assumption (missing columns, an incident with several grades, an
    unparsable timestamp, an empty scope or a failed leak check).
    """
    raw_csv = Path(raw_csv)
    if not raw_csv.is_file():
        raise FileNotFoundError(f"raw GUIDE CSV not found: {raw_csv}")
    _validate_ratios(ratios)
    data_version, inputs = compute_data_version(raw_csv, ratios)

    out_dir = Path(out_root) / data_version
    work_dir = Path(out_root) / f".{data_version}.tmp"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    try:
        con = _connect(work_dir, memory_limit, threads)
        try:
            manifest = _run(con, raw_csv, work_dir, ratios, data_version, inputs)
        finally:
            con.close()
        shutil.rmtree(work_dir / "duckdb_tmp", ignore_errors=True)
        if out_dir.exists():
            shutil.rmtree(out_dir)
        work_dir.rename(out_dir)
    except BaseException:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise
    log.info("dataset %s written to %s", data_version, out_dir)
    return manifest


def _run(
    con: duckdb.DuckDBPyConnection,
    raw_csv: Path,
    work_dir: Path,
    ratios: tuple[float, ...],
    data_version: str,
    inputs: list[dict[str, Any]],
) -> Manifest:
    path_sql = raw_csv.as_posix().replace("'", "''")
    # all_varchar: identity fields are opaque IDs; keys are cast explicitly so that a
    # malformed key fails loudly instead of being guessed by type sniffing.
    csv_sql = f"read_csv('{path_sql}', header = true, all_varchar = true)"
    _check_columns(con, csv_sql)

    keep = ", ".join(f'"{c}"' for c in EVIDENCE_COLUMNS)
    log.info("scanning %s", raw_csv)
    con.execute(f"""
        CREATE TEMP TABLE raw_rows AS
        SELECT CAST(OrgId AS BIGINT) AS org_id,
               CAST(IncidentId AS BIGINT) AS incident_id,
               TRY_CAST("Timestamp" AS TIMESTAMP) AS ts,
               "Timestamp" AS ts_raw,
               IncidentGrade AS grade_raw,
               {keep}
        FROM {csv_sql}
    """)
    n_raw = _scalar(con, "SELECT count(*) FROM raw_rows")

    bad_ts = _scalar(con, 
        "SELECT count(*) FROM raw_rows WHERE ts IS NULL AND ts_raw IS NOT NULL"
    )
    if bad_ts:
        raise PipelineError(f"{bad_ts} rows have an unparsable Timestamp")

    grade_values = _sql_list(tuple(GRADE_MAP))
    unknown = con.execute(
        f"SELECT DISTINCT grade_raw FROM raw_rows "
        f"WHERE grade_raw IS NOT NULL AND grade_raw NOT IN ({grade_values})"
    ).fetchall()
    if unknown:
        raise PipelineError(f"unknown IncidentGrade values: {[u[0] for u in unknown]}")

    # Unlabelled rows are dropped (data audit: 0.5 % of rows). A view, not a copy,
    # so the raw rows are held only once (NFR-03).
    con.execute("""
        CREATE TEMP VIEW labelled AS
        SELECT * EXCLUDE (ts_raw) FROM raw_rows WHERE grade_raw IS NOT NULL
    """)
    n_unlabelled_rows = n_raw - _scalar(con, "SELECT count(*) FROM labelled")

    multi = _scalar(con, """
        SELECT count(*) FROM (
            SELECT org_id, incident_id FROM labelled
            GROUP BY ALL HAVING count(DISTINCT grade_raw) > 1)
    """)
    if multi:
        raise PipelineError(f"{multi} incidents carry more than one IncidentGrade")

    # Incident category: most frequent category over distinct alerts, ties -> alphabetical.
    con.execute("""
        CREATE TEMP TABLE inc_category AS
        SELECT org_id, incident_id, Category AS category FROM (
            SELECT org_id, incident_id, Category,
                   row_number() OVER (PARTITION BY org_id, incident_id
                                      ORDER BY count(DISTINCT AlertId) DESC, Category ASC) AS r
            FROM labelled WHERE Category IS NOT NULL
            GROUP BY org_id, incident_id, Category)
        WHERE r = 1
    """)
    grade_case = "CASE grade_raw " + " ".join(
        f"WHEN '{k}' THEN '{v}'" for k, v in GRADE_MAP.items()) + " END"
    con.execute(f"""
        CREATE TEMP TABLE all_incidents AS
        SELECT l.org_id, l.incident_id, c.category,
               any_value({grade_case}) AS grade,
               min(l.ts) AS first_seen,
               count(DISTINCT l.AlertId) AS n_alerts,
               count(*) AS n_evidence
        FROM labelled l LEFT JOIN inc_category c USING (org_id, incident_id)
        GROUP BY l.org_id, l.incident_id, c.category
    """)
    n_labelled_incidents = _scalar(con, "SELECT count(*) FROM all_incidents")

    cats = _sql_list(CATEGORIES)
    n_in_scope = _scalar(con, 
        f"SELECT count(*) FROM all_incidents WHERE category IN ({cats})")
    if n_in_scope < len(SLICES):
        raise PipelineError(f"only {n_in_scope} in-scope incidents; cannot form {len(SLICES)} slices")

    con.execute(f"""
        CREATE TEMP TABLE incidents AS
        SELECT org_id || '-' || incident_id AS incident_key,
               org_id, incident_id, category, grade, first_seen, n_alerts, n_evidence,
               {_slice_case(n_in_scope, ratios)} AS slice
        FROM (SELECT *, row_number() OVER (ORDER BY first_seen, org_id, incident_id) AS rn
              FROM all_incidents WHERE category IN ({cats}))
    """)

    inc_path = (work_dir / "incidents.parquet").as_posix()
    ev_path = (work_dir / "evidence.parquet").as_posix()
    con.execute(f"""
        COPY (SELECT * FROM incidents ORDER BY first_seen, org_id, incident_id)
        TO '{inc_path}' (FORMAT parquet, COMPRESSION zstd)
    """)
    con.execute(f"""
        COPY (SELECT i.incident_key, i.slice, l.ts, l.* EXCLUDE (org_id, incident_id, ts, grade_raw)
              FROM labelled l JOIN incidents i USING (org_id, incident_id))
        TO '{ev_path}' (FORMAT parquet, COMPRESSION zstd)
    """)
    con.execute("DROP VIEW labelled")
    con.execute("DROP TABLE raw_rows")

    n_evidence = _scalar(con, 
        f"SELECT count(*) FROM read_parquet('{ev_path}')")
    slice_counts = _slice_counts(con)
    time_ranges = _time_ranges(con)
    leak_checks = _leak_checks(con, ev_path, n_in_scope)
    failed = [k for k, ok in leak_checks.items() if not ok]
    if failed:
        raise PipelineError(f"leak checks failed: {failed}")

    manifest = Manifest(
        data_version=data_version,
        created_by=f"socxai {__version__} / pipeline {PIPELINE_VERSION}",
        params={
            "ratios": list(ratios),
            "categories": list(CATEGORIES),
            "vocab_sizes": VOCAB_SIZES,
            "order": ["first_seen", "org_id", "incident_id"],
        },
        inputs=inputs,
        n_raw_rows=int(n_raw),
        n_incidents=int(n_in_scope),
        n_evidence_rows=int(n_evidence),
        slice_counts=slice_counts,
        slice_time_ranges=time_ranges,
        leak_checks=leak_checks,
        excluded={
            "unlabelled_rows": int(n_unlabelled_rows),
            "out_of_scope_incidents": int(n_labelled_incidents - n_in_scope),
        },
    )
    (work_dir / "manifest.json").write_text(manifest.to_json(), encoding="utf-8")
    return manifest


def _slice_counts(con: duckdb.DuckDBPyConnection) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {s: {g: 0 for g in GRADE_MAP.values()} for s in SLICES}
    for s, g, n in con.execute(
            "SELECT slice, grade, count(*) FROM incidents GROUP BY ALL").fetchall():
        counts[s][g] = int(n)
    return counts


def _time_ranges(con: duckdb.DuckDBPyConnection) -> dict[str, dict[str, str]]:
    rows = con.execute(
        "SELECT slice, min(first_seen), max(first_seen) FROM incidents GROUP BY slice").fetchall()
    by_slice = {s: {"min": lo.isoformat(), "max": hi.isoformat()} for s, lo, hi in rows}
    missing = [s for s in SLICES if s not in by_slice]
    if missing:
        raise PipelineError(f"empty slices: {missing}")
    return {s: by_slice[s] for s in SLICES}


def _leak_checks(con: duckdb.DuckDBPyConnection, ev_path: str, n_in_scope: int) -> dict[str, bool]:
    """AC-26 checks, evaluated on the written outputs."""
    distinct_keys = _scalar(con, 
        "SELECT count(DISTINCT incident_key) FROM incidents")
    keys_disjoint = distinct_keys == n_in_scope

    bounds = con.execute(
        "SELECT slice, min(first_seen), max(first_seen) FROM incidents GROUP BY slice").fetchall()
    b = {s: (lo, hi) for s, lo, hi in bounds}
    time_ordered = all(b[SLICES[i]][1] <= b[SLICES[i + 1]][0] for i in range(len(SLICES) - 1))

    cats = _sql_list(CATEGORIES)
    scope_only = _scalar(con, 
        f"SELECT count(*) FROM incidents WHERE category NOT IN ({cats}) OR category IS NULL"
    ) == 0

    rows_one_slice = _scalar(con, f"""
        SELECT count(*) FROM (
            SELECT incident_key FROM read_parquet('{ev_path}')
            GROUP BY incident_key HAVING count(DISTINCT slice) > 1)
    """) == 0
    evidence_matches_slice = _scalar(con, f"""
        SELECT count(*) FROM read_parquet('{ev_path}') e JOIN incidents i USING (incident_key)
        WHERE e.slice <> i.slice
    """) == 0

    labelled_only = _scalar(con, 
        "SELECT count(*) FROM incidents WHERE grade IS NULL") == 0

    return {
        "keys_disjoint": bool(keys_disjoint),
        "time_ordered": bool(time_ordered),
        "scope_only": bool(scope_only),
        "rows_in_one_slice": bool(rows_one_slice and evidence_matches_slice),
        "labelled_only": bool(labelled_only),
    }


def load_manifest(dataset_dir: Path) -> Manifest:
    return Manifest.from_json((Path(dataset_dir) / "manifest.json").read_text(encoding="utf-8"))
