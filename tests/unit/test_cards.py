"""TC-16 (FR-02, AC-02): consistent aliases, sentinels hidden; MITRE name mapping (ADR-0006)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from socxai.data.cards import IDENTITY, AliasBook, build_cards, compute_sentinels
from socxai.data.features import open_dataset
from socxai.data.guide import build_incidents
from socxai.data.mitre import attack_version, load_mitre_names, parse_attack_bundle, write_csv

FIXTURE = Path(__file__).parents[1] / "fixtures" / "guide_mini.csv"


@pytest.fixture
def con(tmp_path: Path):
    m = build_incidents(FIXTURE, tmp_path / "processed")
    c = open_dataset(tmp_path / "processed" / m.data_version)
    yield c
    c.close()


def _raw_rows() -> list[dict[str, str]]:
    with FIXTURE.open(encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if r["IncidentGrade"]]


def test_same_identity_gets_same_alias_across_incidents(con) -> None:
    rows = _raw_rows()
    # Find an AccountObjectId (non-sentinel) used by Users in two in-scope incidents.
    sentinels = compute_sentinels(con, "T1")
    keys_in_scope = {r[0] for r in con.execute("SELECT incident_key FROM incidents").fetchall()}
    by_id: dict[str, set[str]] = {}
    for r in rows:
        key = f"{r['OrgId']}-{r['IncidentId']}"
        if r["EntityType"] == "User" and key in keys_in_scope \
                and r["AccountObjectId"] != sentinels["AccountObjectId"]:
            by_id.setdefault(r["AccountObjectId"], set()).add(key)
    raw_id, keys = next((i, k) for i, k in by_id.items() if len(k) >= 2)
    keys = sorted(keys)[:2]

    book = AliasBook()
    cards = build_cards(con, keys, sentinels, book)
    expected = book.alias("AccountObjectId", raw_id, "Kullanıcı")
    for k in keys:
        aliases = {e["alias"] for e in cards[k]["entities"] if e["entity_type"] == "User"}
        assert expected in aliases
    assert expected.startswith("Kullanıcı-")


def test_sentinel_and_raw_ids_never_appear_in_cards(con) -> None:
    sentinels = compute_sentinels(con, "T1")
    assert sentinels["DeviceId"] == "98799"  # most frequent value in the fixture
    keys = [r[0] for r in con.execute("SELECT incident_key FROM incidents ORDER BY first_seen").fetchall()]
    cards = build_cards(con, keys, sentinels, AliasBook())
    text = json.dumps(cards)
    for raw in sentinels.values():
        assert f'"{raw}"' not in text
    # Typed entities whose identity is the sentinel get no alias.
    sentinel_rows = [r for r in _raw_rows() if r["EntityType"] in IDENTITY
                     and r[IDENTITY[r["EntityType"]][0]] == sentinels[IDENTITY[r["EntityType"]][0]]]
    assert sentinel_rows
    assert any(e["alias"] is None for c in cards.values() for e in c["entities"])
    # No AlertId or raw identity field names leak into the card.
    for f in ("AlertId", "AccountObjectId", "DeviceId", "AlertTitle"):
        assert f not in text


def test_alias_numbering_follows_pool_order_and_is_reloadable(con) -> None:
    sentinels = compute_sentinels(con, "T1")
    keys = [r[0] for r in con.execute("SELECT incident_key FROM incidents ORDER BY first_seen").fetchall()]
    book = AliasBook()
    build_cards(con, keys, sentinels, book)
    pending = book.pending()
    nums: dict[str, list[int]] = {}
    for _, _, alias in pending:
        prefix, _, n = alias.rpartition("-")
        nums.setdefault(prefix, []).append(int(n))
    assert all(v == list(range(1, len(v) + 1)) for v in nums.values())
    # A reloaded book continues numbering and reuses existing aliases.
    again = AliasBook.from_rows(pending)
    f, raw, alias = pending[0]
    assert again.alias(f, raw, alias.rpartition("-")[0]) == alias
    assert again.alias("AccountObjectId", "brand-new", "Kullanıcı") == \
        f"Kullanıcı-{len(nums.get('Kullanıcı', [])) + 1}"


def test_card_shape(con) -> None:
    key = con.execute("SELECT incident_key FROM incidents WHERE n_alerts > 1 LIMIT 1").fetchone()[0]
    card = build_cards(con, [key], compute_sentinels(con), AliasBook(), {"T1566": "Phishing"})[key]
    assert {"incident_key", "category", "first_seen", "n_alerts", "n_evidence", "mitre",
            "entities", "alerts"} <= set(card)
    assert [a["order"] for a in card["alerts"]] == list(range(1, card["n_alerts"] + 1))
    assert sum(e["count"] for e in card["entities"]) == card["n_evidence"]
    assert all("DomainPII" not in v for e in card["entities"] for v in e["last_verdict"])
    for m in card["mitre"]:
        assert m["name"] == ("Phishing" if m["code"] == "T1566" else None)
    with pytest.raises(KeyError):
        build_cards(con, ["9-999999"], {}, AliasBook())


def test_mitre_bundle_parsing_and_csv(tmp_path: Path) -> None:
    bundle = {"type": "bundle", "objects": [
        {"type": "x-mitre-collection", "x_mitre_version": "18.0"},
        {"type": "attack-pattern", "name": "Phishing",
         "external_references": [{"source_name": "mitre-attack", "external_id": "T1566"}]},
        {"type": "attack-pattern", "name": "Spearphishing Link",
         "external_references": [{"source_name": "mitre-attack", "external_id": "T1566.002"}]},
        {"type": "attack-pattern", "name": "Spearphishing Attachment", "revoked": True,
         "external_references": [{"source_name": "mitre-attack", "external_id": "T1193"}]},
        {"type": "attack-pattern", "name": "Old", "x_mitre_deprecated": True,
         "external_references": [{"source_name": "capec", "external_id": "CAPEC-1"},
                                 {"source_name": "mitre-attack", "external_id": "T1999"}]},
        {"type": "malware", "name": "ignored"},
        "not-an-object",
    ]}
    rows = parse_attack_bundle(bundle)
    assert ("T1566.002", "Phishing: Spearphishing Link", "active") in rows
    assert ("T1193", "Spearphishing Attachment", "revoked") in rows
    assert ("T1999", "Old", "deprecated") in rows
    path = tmp_path / "ref" / "mitre_techniques.csv"
    assert write_csv(rows, path, "18.0", "2026-11-02") == 4
    assert path.read_text(encoding="utf-8").startswith("# MITRE ATT&CK Enterprise 18.0, accessed 2026-11-02")
    names = load_mitre_names(path)
    assert names["T1566"] == "Phishing"
    assert names["T1193"] == "Spearphishing Attachment (kullanımdan kalktı)"


def test_missing_mitre_file_gives_empty_mapping(tmp_path: Path) -> None:
    assert load_mitre_names(tmp_path / "absent.csv") == {}


def test_attack_version_collection_then_snapshot_fallback() -> None:
    # STIX 2.1 bundles (attack-stix-data) carry the release in x-mitre-collection.
    assert attack_version({"objects": [{"type": "x-mitre-collection", "x_mitre_version": "18.0"},
                                       {"type": "attack-pattern", "modified": "2026-10-13T17:43:56.655Z"}]}) == "18.0"
    # STIX 2.0 bundles (mitre/cti) do not: fall back to the newest modified date, not x-mitre-matrix's own version.
    bundle = {"objects": [
        {"type": "x-mitre-matrix", "x_mitre_version": "2.0", "modified": "2026-07-31T18:48:31.315Z"},
        {"type": "attack-pattern", "modified": "2026-10-13T17:43:56.655Z"},
        {"type": "attack-pattern", "modified": "not-a-date"},
        "not-an-object",
    ]}
    assert attack_version(bundle) == "snapshot 2026-10-13"
    assert attack_version({"objects": [{"type": "attack-pattern"}]}) == "unknown"
    assert attack_version({}) == "unknown"
