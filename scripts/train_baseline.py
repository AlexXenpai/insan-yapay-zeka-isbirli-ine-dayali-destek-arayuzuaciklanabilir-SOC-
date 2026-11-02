"""E1: train the baseline on T1, select C and τ on validation, save to the registry.

The locked TEST slice is not read (experiment plan §4).

Usage: python scripts/train_baseline.py [--dataset DIR] [--models DIR]
"""

from __future__ import annotations

import argparse
import json
import logging
import platform
import subprocess
import sys
import time
from importlib import metadata
from pathlib import Path
from typing import Any

import pandas as pd

from socxai import __version__
from socxai.config import SPLIT_RATIOS, Settings
from socxai.data.features import load_features, load_vocab
from socxai.data.guide import compute_data_version, load_manifest
from socxai.model import registry
from socxai.model.baseline import MAX_ITER, choose_threshold, dummy_baselines, evaluate, train

C_GRID: tuple[float, ...] = (0.1, 1.0, 10.0)
SEED = 42
E1_MARGIN = 0.10  # macro-F1 over stratified random (experiment plan §1)
PACKAGES = ("numpy", "pandas", "pyarrow", "duckdb", "scikit-learn", "joblib")

log = logging.getLogger("train_baseline")


def default_dataset_dir(settings: Settings) -> Path:
    version, _ = compute_data_version(settings.guide_train_csv, SPLIT_RATIOS)
    return settings.processed_dir / version


def _labels(dataset_dir: Path, index: pd.Index) -> pd.Series:
    inc = pd.read_parquet(dataset_dir / "incidents.parquet", columns=["incident_key", "grade"])
    y = inc.set_index("incident_key")["grade"].reindex(index)
    if y.isna().any():
        raise ValueError(f"{int(y.isna().sum())} feature rows have no label")
    return y


def _git_commit(cwd: Path) -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=cwd, capture_output=True,
                             text=True, timeout=10, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "uncommitted"


def run(dataset_dir: Path, models_dir: Path) -> dict[str, Any]:
    manifest = load_manifest(dataset_dir)
    vocab = load_vocab(dataset_dir)
    X_tr, X_val = load_features(dataset_dir, "T1"), load_features(dataset_dir, "VAL")
    y_tr, y_val = _labels(dataset_dir, X_tr.index), _labels(dataset_dir, X_val.index)
    sources = vocab.feature_sources()

    t0 = time.perf_counter()
    candidates = []
    for C in C_GRID:
        model = train(X_tr, y_tr, C=C, seed=SEED, feature_sources=sources)
        m = evaluate(model, X_val, y_val)
        log.info("C=%g  val macro-F1=%.4f  accuracy=%.4f", C, m["macro_f1"], m["accuracy"])
        candidates.append((C, model, m))
    # Highest validation macro-F1; ties go to the stronger regularisation (earlier in grid).
    best_C, best, best_val = max(candidates, key=lambda c: (c[2]["macro_f1"], -c[0]))
    train_seconds = time.perf_counter() - t0

    dummies = dummy_baselines(y_tr, y_val, seed=SEED)
    tau, tau_info = choose_threshold(best.predict_proba(X_val), y_val, best.classes_)
    margin = best_val["macro_f1"] - dummies["stratified"]["macro_f1"]

    metrics = {
        "slice": "VAL",
        "model": best_val,
        "train_T1": evaluate(best, X_tr, y_tr),
        "c_grid": [{"C": C, "macro_f1": m["macro_f1"], "accuracy": m["accuracy"]}
                   for C, _, m in candidates],
        "baselines": dummies,
        "e1": {"margin_over_stratified": margin, "required_margin": E1_MARGIN,
               "hypothesis_supported": bool(margin >= E1_MARGIN)},
        "threshold": tau_info,
        "data_version": manifest.data_version,
        "seed": SEED,
    }
    meta = {
        "data_version": manifest.data_version,
        "family": "logistic_regression",
        "code_version": f"socxai {__version__} @ {_git_commit(Path(__file__).resolve().parents[1])}",
        "python": platform.python_version(),
        "packages": {p: metadata.version(p) for p in PACKAGES},
        "settings": {"C": best_C, "C_grid": list(C_GRID), "class_weight": "balanced",
                     "max_iter": MAX_ITER, "solver": "lbfgs", "scaler": "StandardScaler (T1)",
                     "seed": SEED},
        "classes": list(best.classes_),
        "feature_names": best.feature_names,
        "tau": tau,
        "train_slice": "T1", "selection_slice": "VAL", "locked_test_read": False,
        "n_train": int(len(X_tr)), "n_val": int(len(X_val)),
        "train_seconds": round(train_seconds, 2),
        "metrics": metrics,
    }
    version = registry.save(best, meta, models_dir)
    return {"version": version, "dir": str(models_dir / version), **meta}


def main(argv: list[str] | None = None) -> int:
    settings = Settings.from_env()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", type=Path, default=None)
    ap.add_argument("--models", type=Path, default=settings.models_dir)
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        dataset_dir = args.dataset or default_dataset_dir(settings)
        out = run(dataset_dir, args.models)
    except (FileNotFoundError, ValueError) as exc:
        logging.error("%s", exc)
        return 1
    m = out["metrics"]
    print(f"model {out['version']}  (data {out['data_version']}, C={out['settings']['C']}, "
          f"train {out['train_seconds']} s, n_train={out['n_train']}, n_val={out['n_val']})")
    for row in m["c_grid"]:
        print(f"  C={row['C']:<5} val macro-F1={row['macro_f1']:.4f} accuracy={row['accuracy']:.4f}")
    print(f"  baseline LR      val macro-F1={m['model']['macro_f1']:.4f} accuracy={m['model']['accuracy']:.4f}")
    for name, b in m["baselines"].items():
        print(f"  dummy {name:<10} val macro-F1={b['macro_f1']:.4f} accuracy={b['accuracy']:.4f}")
    e1 = m["e1"]
    print(f"  E1 margin over stratified = {e1['margin_over_stratified']:.4f} "
          f"(required {e1['required_margin']}) -> {'supported' if e1['hypothesis_supported'] else 'NOT supported'}")
    t = m["threshold"]
    print(f"  tau={t['tau']:.2f} coverage={t['coverage']:.3f} selective_accuracy="
          f"{t['selective_accuracy']:.3f} target_met={t['target_met']} ({t['rule']})")
    print("  per-class (val): " + json.dumps({c: round(v['f1'], 3) for c, v in m['model']['per_class'].items()}))
    print(f"output: {out['dir']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
