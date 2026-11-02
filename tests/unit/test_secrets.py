"""TC-26 (NFR-07): no secrets in the repository's text files; .env stays out of git."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[2]
SKIP_DIRS = {".git", ".venv", "data", "artifacts", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {".py", ".md", ".toml", ".txt", ".json", ".js", ".html", ".css", ".sql", ".csv", ".cfg",
                 ".ini", ".yml", ".yaml", ".env"}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "Anthropic/OpenAI key": re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{20,}\b"),
    "assigned secret": re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"\s]{12,}['\"]"),
}


def _files() -> list[Path]:
    out = []
    for p in ROOT.rglob("*"):
        if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP_DIRS) and p.suffix.lower() in TEXT_SUFFIXES:
            out.append(p)
    return out


def test_no_secret_patterns() -> None:
    findings = []
    for f in _files():
        text = f.read_text(encoding="utf-8", errors="ignore")
        for name, pat in PATTERNS.items():
            if f.name == Path(__file__).name:
                continue  # this file defines the patterns
            for m in pat.finditer(text):
                findings.append(f"{f.relative_to(ROOT).as_posix()}: {name}: {m.group(0)[:12]}…")
    assert findings == []


def test_env_and_data_are_ignored() -> None:
    for path in (".env", "data/app/app.db", "artifacts/models/x/model.joblib", ".venv/x"):
        r = subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT, capture_output=True)
        assert r.returncode == 0, f"{path} is not git-ignored"
