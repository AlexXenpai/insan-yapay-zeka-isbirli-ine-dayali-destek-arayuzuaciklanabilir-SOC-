"""TC-18 (FR-25, AC-25), runtime part: the application makes no outbound calls.

Code-inspection part of TC-18 for the runtime package: it imports no network
client. ``scripts/fetch_mitre.py`` is an offline, one-time reference download
(ADR-0006) and is not part of the running system. The web part (banner, no
absolute URLs) is in ``test_web_ui.py``.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
NETWORK_IMPORT = re.compile(r"^\s*(import|from)\s+(urllib\.request|requests|httpx|aiohttp|socket|http\.client)\b",
                            re.M)


def test_runtime_package_imports_no_network_client() -> None:
    offenders = [p.relative_to(ROOT).as_posix() for p in (ROOT / "src" / "socxai").rglob("*.py")
                 if NETWORK_IMPORT.search(p.read_text(encoding="utf-8"))]
    assert offenders == []
