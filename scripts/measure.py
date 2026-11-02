"""Measurements for NFRs.

  python scripts/measure.py memory -- <script.py> [args...]
      Runs the script in this process and reports its peak working set
      (TC-24, NFR-03: <= 6 GB). Windows only (GetProcessMemoryInfo).

  python scripts/measure.py latency [--n 100]
      Opens n incidents (TC-22, NFR-01: p95 <= 2 s) and records n decisions
      (TC-23, NFR-02: p95 <= 500 ms) through the full ASGI app, in-process, on a
      copy of app.db so the real audit trail is untouched. The HTTP socket layer is
      not included; the server runs on the same machine.
"""

from __future__ import annotations

import argparse
import ctypes
import runpy
import sys
from ctypes import wintypes

PEAK_LIMIT_GB = 6.0
OPEN_P95_LIMIT_S = 2.0
DECISION_P95_LIMIT_S = 0.5


class _ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def peak_memory_gb() -> tuple[float, float]:
    """(peak working set, peak private commit) of the current process, in GiB."""
    if sys.platform != "win32":
        raise OSError("peak memory measurement is implemented for Windows only")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(_ProcessMemoryCounters), wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    counters = _ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return counters.PeakWorkingSetSize / 2**30, counters.PeakPagefileUsage / 2**30


def cmd_memory(script: str, script_args: list[str]) -> int:
    sys.argv = [script, *script_args]
    code: int = 0
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    ws, commit = peak_memory_gb()
    verdict = "OK" if ws <= PEAK_LIMIT_GB else "FAIL"
    print(f"peak_working_set_gb={ws:.2f} peak_commit_gb={commit:.2f} "
          f"limit_gb={PEAK_LIMIT_GB} -> {verdict} (script exit {code})")
    return code if code else (0 if verdict == "OK" else 2)


def _p95(values: list[float]) -> float:
    ordered = sorted(values)
    # Nearest-rank percentile.
    return ordered[max(0, int(-(-0.95 * len(ordered) // 1)) - 1)]


def cmd_latency(n: int) -> int:
    import os
    import sqlite3
    import tempfile
    import time
    from pathlib import Path

    from fastapi.testclient import TestClient

    from socxai.api.app import create_app
    from socxai.config import Settings

    settings = Settings.from_env()
    if not settings.app_db.exists():
        print(f"{settings.app_db} not found; run scripts/seed_demo.py first")
        return 1
    with tempfile.TemporaryDirectory(prefix="socxai-measure-") as tmp:
        src, dst = sqlite3.connect(settings.app_db), sqlite3.connect(Path(tmp) / "app.db")
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()
        os.environ["SOCXAI_APP_DIR"] = tmp
        try:
            with TestClient(create_app(Settings.from_env())) as c:
                h = {"X-User": "analist1"}
                keys = [r["key"] for r in c.get("/api/incidents?status=pending", headers=h).json()][:n]
                if len(keys) < n:
                    print(f"only {len(keys)} pending incidents; measuring those")
                opens, writes, opened = [], [], {}
                for k in keys:
                    t0 = time.perf_counter()
                    r = c.get(f"/api/incidents/{k}", headers=h)
                    opens.append(time.perf_counter() - t0)
                    if r.status_code != 200:
                        print(f"GET {k} -> {r.status_code}")
                        return 1
                    opened[k] = r.json()
                for i, k in enumerate(keys):
                    d = opened[k]
                    other = next(x for x in ("TP", "BP", "FP") if x != d["suggestion"]["class"])
                    body = ({"type": "accept", "opened_at": d["opened_at"]} if i % 3 == 0 else
                            {"type": "correct", "decided_class": other, "reason": f"ölçüm {i}",
                             "opened_at": d["opened_at"]} if i % 3 == 1 else
                            {"type": "reject", "reason": f"ölçüm {i}", "opened_at": d["opened_at"]})
                    t0 = time.perf_counter()
                    r = c.post(f"/api/incidents/{k}/decisions", json=body, headers=h)
                    writes.append(time.perf_counter() - t0)
                    if r.status_code != 201:
                        print(f"POST {k} -> {r.status_code} {r.text[:200]}")
                        return 1
        finally:
            os.environ.pop("SOCXAI_APP_DIR", None)
    ok_open = _p95(opens) <= OPEN_P95_LIMIT_S
    ok_write = _p95(writes) <= DECISION_P95_LIMIT_S
    print(f"open incident (n={len(opens)}): median={sorted(opens)[len(opens) // 2] * 1000:.1f} ms "
          f"p95={_p95(opens) * 1000:.1f} ms max={max(opens) * 1000:.1f} ms "
          f"limit={OPEN_P95_LIMIT_S * 1000:.0f} ms -> {'OK' if ok_open else 'FAIL'}")
    print(f"record decision (n={len(writes)}): median={sorted(writes)[len(writes) // 2] * 1000:.1f} ms "
          f"p95={_p95(writes) * 1000:.1f} ms max={max(writes) * 1000:.1f} ms "
          f"limit={DECISION_P95_LIMIT_S * 1000:.0f} ms -> {'OK' if ok_write else 'FAIL'}")
    return 0 if ok_open and ok_write else 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    mem = sub.add_parser("memory", help="peak memory of a script run in-process")
    mem.add_argument("script")
    mem.add_argument("script_args", nargs=argparse.REMAINDER)
    lat = sub.add_parser("latency", help="p95 of incident opening and decision recording")
    lat.add_argument("--n", type=int, default=100)
    args = ap.parse_args(argv)
    if args.cmd == "memory":
        return cmd_memory(args.script, args.script_args)
    if args.cmd == "latency":
        return cmd_latency(args.n)
    return 1


if __name__ == "__main__":
    sys.exit(main())
