"""Demo scenario (TC-25): open an incident → accept → correct with a reason → history shows both.

By default the scenario runs in-process against a consistent copy of app.db in a
temporary folder, so the real audit trail is untouched. With --base-url it talks
to a running server and its decisions are recorded permanently.

Usage: python scripts/demo_scenario.py [--base-url http://127.0.0.1:8000] [--key ORG-INC]
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import httpx

from socxai.config import Settings

LABELS = {"TP": "Gerçek tehdit", "BP": "Zararsız-beklenen", "FP": "Yanlış alarm"}


class ScenarioError(RuntimeError):
    pass


def _check(cond: bool, message: str) -> None:
    if not cond:
        raise ScenarioError(message)


@contextmanager
def _client(base_url: str | None) -> Iterator[httpx.Client]:
    if base_url:
        with httpx.Client(base_url=base_url, timeout=10.0) as c:
            yield c
        return
    from fastapi.testclient import TestClient

    from socxai.api.app import create_app

    settings = Settings.from_env()
    if not settings.app_db.exists():
        raise ScenarioError(f"{settings.app_db} not found; run scripts/seed_demo.py first")
    with tempfile.TemporaryDirectory(prefix="socxai-demo-") as tmp:
        src = sqlite3.connect(settings.app_db)
        dst = sqlite3.connect(Path(tmp) / "app.db")
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()
        os.environ["SOCXAI_APP_DIR"] = tmp
        try:
            with TestClient(create_app(Settings.from_env())) as c:
                yield c
        finally:
            os.environ.pop("SOCXAI_APP_DIR", None)


def run(client: httpx.Client, key: str | None = None, user: str = "analist1") -> list[str]:
    h = {"X-User": user}
    log: list[str] = []

    def call(method: str, path: str, expected: int, **kw: Any) -> Any:
        r = client.request(method, path, headers=h, **kw)
        _check(r.status_code == expected, f"{method} {path} -> {r.status_code} {r.text[:200]}")
        return r.json()

    if key is None:
        pending = call("GET", "/api/incidents?status=pending", 200)
        _check(bool(pending), "no pending incident in the queue")
        key = pending[0]["key"]
    d = call("GET", f"/api/incidents/{key}", 200)
    s = d["suggestion"]
    _check(s is not None, f"incident {key} has no suggestion")
    top = d["explanation"]["contributions"][0]
    log.append(f"1. olay açıldı: {key} ({d['card']['category']}, {d['card']['n_alerts']} uyarı); "
               f"öneri {LABELS[s['class']]} %{round(s['confidence'] * 100)}"
               f"{' ⚠ inceleme gerekli' if s['needs_review'] else ''}; en büyük katkı {top['feature']} "
               f"({top['contribution']:+.2f})")

    ev1 = call("POST", f"/api/incidents/{key}/decisions", 201,
               json={"type": "accept", "opened_at": d["opened_at"]})["event"]
    log.append(f"2. kabul: v{ev1['version']} → {LABELS[ev1['decided_class']]}")

    other = next(c for c in ("TP", "BP", "FP") if c != s["class"])
    reason = "Kanıt kartında aynı posta kutusu iki uyarıda etkilenmiş; ikinci bakışta sınıf farklı."
    ev2 = call("POST", f"/api/incidents/{key}/decisions", 201,
               json={"type": "correct", "decided_class": other, "reason": reason,
                     "opened_at": d["opened_at"]})["event"]
    log.append(f"3. düzeltme + gerekçe: v{ev2['version']} → {LABELS[ev2['decided_class']]}")

    hist = call("GET", f"/api/incidents/{key}/history", 200)
    versions = [x["version"] for x in hist if x["version"] is not None]
    _check(versions[:2] == [ev2["version"], ev1["version"]], f"unexpected history versions {versions}")
    after = call("GET", f"/api/incidents/{key}", 200)
    _check(after["effective"]["id"] == ev2["id"], "effective decision is not the correction")
    _check(after["history"][1]["decided_class"] == s["class"], "previous decision not visible")
    log.append(f"4. geçmiş: {', '.join(f'v{x}' for x in versions)}; etkin karar v{ev2['version']}, "
               f"önceki karar görünür (v{ev1['version']} {LABELS[ev1['decided_class']]})")
    return log


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", default=None, help="running server; decisions are recorded permanently")
    ap.add_argument("--key", default=None, help="incident key (default: first pending)")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to a legacy code page
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        with _client(args.base_url) as c:
            steps = run(c, args.key)
    except (ScenarioError, httpx.HTTPError, FileNotFoundError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print("\n".join(steps))
    print("OK" + ("" if args.base_url else " (app.db kopyası üzerinde; gerçek denetim izi değişmedi)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
