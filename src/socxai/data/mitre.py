"""MITRE ATT&CK technique names (ADR-0006).

``data/reference/mitre_techniques.csv`` starts with one ``#`` comment line
(ATT&CK version and access date), then ``code,name,status`` rows where status is
``active``, ``deprecated`` or ``revoked``.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import date
from pathlib import Path
from typing import Any, Iterable

STATUS_LABELS = {"deprecated": "kullanımdan kalktı", "revoked": "kullanımdan kalktı"}


def load_mitre_names(path: Path) -> dict[str, str]:
    """Code → display name; deprecated/revoked names carry a marker. Missing file → {}."""
    path = Path(path)
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if not ln.startswith("#")]
    names: dict[str, str] = {}
    for row in csv.DictReader(io.StringIO("\n".join(lines))):
        code, name, status = row.get("code"), row.get("name"), row.get("status", "active")
        if not code or not name:
            continue
        label = STATUS_LABELS.get(status or "active")
        names[code] = f"{name} ({label})" if label else name
    return names


def parse_attack_bundle(bundle: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Extract (code, name, status) from a STIX 2.x enterprise-attack bundle.

    Sub-techniques get "Parent: Child" names, as ATT&CK displays them. The bundle
    is treated as data only.
    """
    patterns: dict[str, tuple[str, str, str]] = {}
    for obj in bundle.get("objects", []):
        if not isinstance(obj, dict) or obj.get("type") != "attack-pattern":
            continue
        code = next((r.get("external_id") for r in obj.get("external_references", [])
                     if isinstance(r, dict) and r.get("source_name") == "mitre-attack"), None)
        name = obj.get("name")
        if not isinstance(code, str) or not isinstance(name, str):
            continue
        status = "revoked" if obj.get("revoked") else (
            "deprecated" if obj.get("x_mitre_deprecated") else "active")
        prev = patterns.get(code)
        # Prefer an active object when a code appears more than once.
        if prev is None or (prev[2] != "active" and status == "active"):
            patterns[code] = (code, name.strip(), status)

    out = []
    for code, name, status in patterns.values():
        if "." in code:
            parent = patterns.get(code.split(".", 1)[0])
            if parent:
                name = f"{parent[1]}: {name}"
        out.append((code, name, status))
    return sorted(out)


def attack_version(bundle: dict[str, Any]) -> str:
    """ATT&CK release of the bundle, for the CSV header.

    STIX 2.1 bundles (attack-stix-data) name it in ``x-mitre-collection``. STIX 2.0
    bundles (mitre/cti) carry no release number; ``x-mitre-matrix.x_mitre_version``
    is that object's own version, so it is not used. Instead the newest ``modified``
    date identifies the snapshot. O(n) over the bundle objects.
    """
    objects = [o for o in bundle.get("objects", []) if isinstance(o, dict)]
    for obj in objects:
        if obj.get("type") == "x-mitre-collection" and obj.get("x_mitre_version"):
            return str(obj["x_mitre_version"])
    dates = [m[:10] for o in objects
             if isinstance(m := o.get("modified"), str) and _is_iso_date(m[:10])]
    return f"snapshot {max(dates)}" if dates else "unknown"


def _is_iso_date(s: str) -> bool:
    try:
        date.fromisoformat(s)
    except ValueError:
        return False
    return True


def write_csv(rows: Iterable[tuple[str, str, str]], path: Path, version: str, accessed: str) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        fh.write(f"# MITRE ATT&CK Enterprise {version}, accessed {accessed}. "
                 f"MITRE ATT&CK(R), The MITRE Corporation.\n")
        w = csv.writer(fh)
        w.writerow(["code", "name", "status"])
        w.writerows(rows)
    tmp.replace(path)
    return len(rows)


def load_bundle(path: Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("type") != "bundle":
        raise ValueError(f"{path} is not a STIX bundle")
    return data
