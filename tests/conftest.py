"""Shared pytest fixtures."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

from socxai.config import Settings

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).parents[1]


def load_script(name: str) -> ModuleType:
    """Import ``scripts/<name>.py`` as a module."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Settings whose writable folders live under a temporary directory."""
    monkeypatch.setenv("SOCXAI_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("SOCXAI_MODELS_DIR", str(tmp_path / "models"))
    return Settings.from_env()


@pytest.fixture
def real_settings() -> Settings:
    """Default settings; skips the test when the real GUIDE data is absent."""
    s = Settings.from_env()
    if not s.guide_train_csv.exists():
        pytest.skip(f"real GUIDE data not found at {s.guide_train_csv}")
    return s


@pytest.fixture
def demo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Settings, dict, ModuleType, Path]:
    """Fixture dataset → baseline model → seeded demo stores, all under tmp_path."""
    from socxai.data.features import write_features
    from socxai.data.guide import build_incidents

    monkeypatch.setenv("SOCXAI_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("SOCXAI_MODELS_DIR", str(tmp_path / "models"))
    s = Settings.from_env()
    m = build_incidents(FIXTURES_DIR / "guide_mini.csv", s.processed_dir)
    dataset = s.processed_dir / m.data_version
    write_features(dataset)
    load_script("train_baseline").run(dataset, s.models_dir)
    seed = load_script("seed_demo")
    out = seed.seed_demo(s, n=6, seed=42, min_review=0, min_wrong=0, dataset_dir=dataset)
    return s, out, seed, dataset
