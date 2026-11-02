"""TC-21 (FR-27, AC-27): baseline training writes the required metrics and metadata."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from socxai.config import CLASSES, Settings
from socxai.data.features import write_features
from socxai.data.guide import build_incidents

ROOT = Path(__file__).parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "guide_mini.csv"


def _load_script():
    spec = importlib.util.spec_from_file_location("train_baseline", ROOT / "scripts" / "train_baseline.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _check_artifacts(model_dir: Path, data_version: str) -> dict:
    metrics = json.loads((model_dir / "metrics.json").read_text(encoding="utf-8"))
    meta = json.loads((model_dir / "meta.json").read_text(encoding="utf-8"))
    m = metrics["model"]
    for key in ("macro_f1", "accuracy", "per_class", "confusion_matrix"):
        assert key in m
    assert set(m["per_class"]) == set(CLASSES)
    assert all({"precision", "recall", "f1"} <= set(v) for v in m["per_class"].values())
    assert len(m["confusion_matrix"]["matrix"]) == 3
    assert metrics["data_version"] == meta["data_version"] == data_version
    assert metrics["seed"] == meta["settings"]["seed"] == 42
    assert meta["locked_test_read"] is False
    assert {"python", "packages", "code_version", "tau", "feature_names"} <= set(meta)
    assert 0.34 <= meta["tau"] <= 0.95
    return metrics


def test_train_script_on_fixture(tmp_path: Path) -> None:
    m = build_incidents(FIXTURE, tmp_path / "processed")
    dataset = tmp_path / "processed" / m.data_version
    write_features(dataset)
    out = _load_script().run(dataset, tmp_path / "models")
    _check_artifacts(Path(out["dir"]), m.data_version)
    assert out["version"] == f"v1-lr-{m.data_version[:6]}"


@pytest.mark.realdata
def test_e1_on_real_data(real_settings: Settings) -> None:
    """Checks the artifact written by scripts/train_baseline.py on GUIDE."""
    mod = _load_script()
    dataset = mod.default_dataset_dir(real_settings)
    version = f"v1-lr-{dataset.name[:6]}"
    model_dir = real_settings.models_dir / version
    if not (model_dir / "metrics.json").exists():
        pytest.skip("run scripts/train_baseline.py first")
    metrics = _check_artifacts(model_dir, dataset.name)
    # E1 hypothesis: macro-F1 ≥ stratified random + 0.10.
    assert metrics["model"]["macro_f1"] >= metrics["baselines"]["stratified"]["macro_f1"] + 0.10
