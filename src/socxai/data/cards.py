"""Case cards with consistent aliases (FR-02, K2, data-design §9.6).

A card shows only structured fields: category, counts, MITRE codes and names,
entities (alias, type, roles, suspicion, verdict) and the alert sequence. Raw
identity values never leave this module; each is replaced by an alias that is
stable across cards (``aliases`` table). A field's most frequent T1 value is
taken to mean "absent" (sentinel) and gets no alias.

Cost: one DuckDB scan of the pool's evidence rows, O(R_pool); aliasing is
O(1) amortised per row with a hash map.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import duckdb
import pandas as pd

# Entity type → (primary identity field, alias prefix) (§9.6).
IDENTITY: dict[str, tuple[str, str]] = {
    "User": ("AccountObjectId", "Kullanıcı"),
    "Machine": ("DeviceId", "Cihaz"),
    "Ip": ("IpAddress", "IP"),
    "Url": ("Url", "URL"),
    "File": ("Sha256", "Dosya"),
    "MailMessage": ("NetworkMessageId", "Posta"),
    "Mailbox": ("AccountUpn", "PostaKutusu"),
    "CloudApplication": ("ApplicationId", "Uygulama"),
}
IDENTITY_FIELDS: tuple[str, ...] = tuple(sorted({f for f, _ in IDENTITY.values()}))
ROW_FIELD_PREFIX = "row:"


def compute_sentinels(con: duckdb.DuckDBPyConnection, slice: str = "T1") -> dict[str, str]:
    """Most frequent value of each identity field in ``slice`` (assumed to mean "absent")."""
    out: dict[str, str] = {}
    for f in IDENTITY_FIELDS:
        row = con.execute(
            f'SELECT "{f}", count(*) AS n FROM evidence WHERE slice = ? AND "{f}" IS NOT NULL '
            f'GROUP BY 1 ORDER BY n DESC, 1 ASC LIMIT 1', [slice]).fetchone()
        if row is not None:
            out[f] = str(row[0])
    return out


@dataclass
class AliasBook:
    """(field, raw value) → alias, numbered per prefix in first-seen order."""

    _by_key: dict[tuple[str, str], str] = field(default_factory=dict)
    _counters: dict[str, int] = field(default_factory=dict)
    _new: list[tuple[str, str, str]] = field(default_factory=list)

    @classmethod
    def from_rows(cls, rows: Iterable[Sequence[str]]) -> "AliasBook":
        book = cls()
        for fld, raw, alias in rows:
            book._by_key[(fld, raw)] = alias
            prefix, _, num = alias.rpartition("-")
            if num.isdigit():
                book._counters[prefix] = max(book._counters.get(prefix, 0), int(num))
        return book

    @classmethod
    def load(cls, conn: sqlite3.Connection) -> "AliasBook":
        return cls.from_rows(tuple(r) for r in conn.execute("SELECT field, raw_value, alias FROM aliases"))

    def alias(self, fld: str, raw: str, prefix: str) -> str:
        key = (fld, raw)
        found = self._by_key.get(key)
        if found is not None:
            return found
        n = self._counters.get(prefix, 0) + 1
        self._counters[prefix] = n
        alias = f"{prefix}-{n}"
        self._by_key[key] = alias
        self._new.append((fld, raw, alias))
        return alias

    def pending(self) -> list[tuple[str, str, str]]:
        return list(self._new)

    def save(self, conn: sqlite3.Connection) -> int:
        """Insert aliases created since load (caller owns the transaction)."""
        conn.executemany("INSERT INTO aliases (field, raw_value, alias) VALUES (?, ?, ?)", self._new)
        n = len(self._new)
        self._new.clear()
        return n


def _iso(ts: Any) -> str:
    return pd.Timestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")


def _clean(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    s = str(value)
    return s or None


def build_cards(
    con: duckdb.DuckDBPyConnection,
    keys: Sequence[str],
    sentinels: dict[str, str],
    aliases: AliasBook,
    mitre_names: dict[str, str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Cards for ``keys``; aliases are numbered in the order of ``keys`` (first-seen in the pool)."""
    if not keys:
        return {}
    mitre_names = mitre_names or {}
    order = pd.DataFrame({"incident_key": list(keys), "pos": range(len(keys))})
    con.register("_card_keys", order)
    try:
        inc = con.execute("""
            SELECT i.incident_key, i.category, i.first_seen, i.n_alerts, i.n_evidence
            FROM incidents i JOIN _card_keys k USING (incident_key) ORDER BY k.pos
        """).df()
        id_cols = ", ".join(f'e."{f}"' for f in IDENTITY_FIELDS)
        ev = con.execute(f"""
            SELECT e.incident_key, e.AlertId, e.ts, e.Category, e.MitreTechniques, e.EntityType,
                   e.EvidenceRole, e.Roles, e.SuspicionLevel, e.LastVerdict, {id_cols}
            FROM evidence e JOIN _card_keys k USING (incident_key)
            ORDER BY k.pos, e.ts, e.AlertId, e.EntityType, e.EvidenceRole, {id_cols}
        """).df()
    finally:
        con.unregister("_card_keys")

    missing = set(keys) - set(inc["incident_key"])
    if missing:
        raise KeyError(f"incidents not in dataset: {sorted(missing)[:5]}")

    cards: dict[str, dict[str, Any]] = {}
    for key, rows in ev.groupby("incident_key", sort=False):
        cards[str(key)] = _card(str(key), rows, sentinels, aliases, mitre_names)
    out: dict[str, dict[str, Any]] = {}
    for rec in inc.itertuples(index=False):
        card = cards[rec.incident_key]
        out[rec.incident_key] = {
            "incident_key": rec.incident_key,
            "category": rec.category,
            "first_seen": _iso(rec.first_seen),
            "n_alerts": int(rec.n_alerts),
            "n_evidence": int(rec.n_evidence),
            **card,
        }
    return out


def _card(key: str, rows: pd.DataFrame, sentinels: dict[str, str], aliases: AliasBook,
          mitre_names: dict[str, str]) -> dict[str, Any]:
    # Alerts in time order; AlertId itself is an identifier and is not shown.
    alerts_df = (rows.groupby("AlertId", sort=False)
                 .agg(first_seen=("ts", "min"), category=("Category", "first"))
                 .reset_index().sort_values(["first_seen", "AlertId"]))
    alerts = [{"order": i + 1, "category": _clean(r.category), "first_seen": _iso(r.first_seen)}
              for i, r in enumerate(alerts_df.itertuples(index=False))]

    codes: list[str] = []
    for value in rows["MitreTechniques"].dropna():
        for t in str(value).split(";"):
            t = t.strip()
            if t and t not in codes:
                codes.append(t)
    mitre = [{"code": c, "name": mitre_names.get(c)} for c in sorted(codes)]

    entities: dict[tuple, dict[str, Any]] = {}
    row_counter = 0
    for r in rows.itertuples(index=False):
        etype = _clean(r.EntityType) or "Unknown"
        ident = IDENTITY.get(etype)
        alias: str | None
        if ident:
            fld, prefix = ident
            raw = _clean(getattr(r, fld))
            alias = None if raw is None or raw == sentinels.get(fld) else aliases.alias(fld, raw, prefix)
        else:
            # Types without an identity field are aliased per row (§9.6).
            row_counter += 1
            alias = aliases.alias(ROW_FIELD_PREFIX + etype, f"{key}#{row_counter}", etype)
        verdict = _clean(r.LastVerdict)
        if verdict and verdict.startswith("DomainPII_"):
            verdict = None  # anonymised token, not a readable verdict
        # One entry per entity and evidence role; values seen across its rows are listed.
        sig = (alias, etype, _clean(r.EvidenceRole))
        entry = entities.get(sig)
        if entry is None:
            entry = entities[sig] = {"alias": alias, "entity_type": etype, "evidence_role": sig[2],
                                     "roles": [], "suspicion_level": [], "last_verdict": [],
                                     "count": 0}
        entry["count"] += 1
        for key_, value in (("roles", _clean(r.Roles)), ("suspicion_level", _clean(r.SuspicionLevel)),
                            ("last_verdict", verdict)):
            if value is not None and value not in entry[key_]:
                entry[key_].append(value)
    return {"mitre": mitre, "entities": list(entities.values()), "alerts": alerts}
