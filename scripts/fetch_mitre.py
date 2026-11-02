"""Download MITRE ATT&CK Enterprise (STIX) once and write the code → name CSV (ADR-0006).

Usage: python scripts/fetch_mitre.py [--from-file PATH]
  --from-file  use an already downloaded enterprise-attack.json instead of the network
"""

from __future__ import annotations

import argparse
import logging
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from socxai.config import Settings
from socxai.data.mitre import attack_version, load_bundle, parse_attack_bundle, write_csv

URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
MAX_BYTES = 200 * 2**20  # the bundle is ~50 MB; refuse anything absurd
TIMEOUT_S = 120


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    req = urllib.request.Request(url, headers={"User-Agent": "socxai-fetch-mitre"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp, tmp.open("wb") as fh:
        total = 0
        while chunk := resp.read(1 << 20):
            total += len(chunk)
            if total > MAX_BYTES:
                raise ValueError(f"download exceeds {MAX_BYTES} bytes")
            fh.write(chunk)
    tmp.replace(dest)


def main(argv: list[str] | None = None) -> int:
    settings = Settings.from_env()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from-file", type=Path, default=None)
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    raw = args.from_file or settings.reference_dir / "raw" / "enterprise-attack.json"
    try:
        if args.from_file is None:
            logging.info("downloading %s", URL)
            download(URL, raw)
        bundle = load_bundle(raw)
        rows = parse_attack_bundle(bundle)
        n = write_csv(rows, settings.mitre_csv, attack_version(bundle), date.today().isoformat())
    except (urllib.error.URLError, OSError, ValueError) as exc:
        logging.error("MITRE fetch failed: %s (cards will show codes only)", exc)
        return 1
    by_status: dict[str, int] = {}
    for _, _, s in rows:
        by_status[s] = by_status.get(s, 0) + 1
    print(f"ATT&CK {attack_version(bundle)}: {n} techniques {by_status} -> {settings.mitre_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
