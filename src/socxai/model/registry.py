"""Model registry: ``<root>/<version>/{model.joblib, meta.json, metrics.json}``.

Version name: ``v1-lr-<first 6 chars of the data version>`` (decision list item 8).
joblib files are pickles: load only artifacts this project wrote (trust boundary,
architecture §8).
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

import joblib

from socxai.model.baseline import BaselineModel

MODEL_FILE = "model.joblib"
META_FILE = "meta.json"
METRICS_FILE = "metrics.json"


def version_name(data_version: str, family: str = "lr", generation: int = 1) -> str:
    if len(data_version) < 6:
        raise ValueError(f"data version too short: {data_version!r}")
    return f"v{generation}-{family}-{data_version[:6]}"


def save(model: BaselineModel, meta: dict[str, Any], root: Path) -> str:
    """Write the model atomically; ``meta`` must contain ``data_version`` and ``metrics``.

    Re-saving the same version replaces it (training is deterministic, NFR-13).
    """
    for key in ("data_version", "metrics"):
        if key not in meta:
            raise ValueError(f"meta lacks {key!r}")
    version = version_name(meta["data_version"])
    root = Path(root)
    final = root / version
    tmp = root / f".{version}.tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    try:
        model.version = version
        joblib.dump(model, tmp / MODEL_FILE)
        full_meta = {**meta, "version": version}
        (tmp / META_FILE).write_text(json.dumps(full_meta, ensure_ascii=False, indent=2), encoding="utf-8")
        (tmp / METRICS_FILE).write_text(json.dumps(meta["metrics"], ensure_ascii=False, indent=2),
                                        encoding="utf-8")
        if final.exists():
            shutil.rmtree(final)
        os.replace(tmp, final)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return version


def load(version: str, root: Path) -> BaselineModel:
    path = Path(root) / version / MODEL_FILE
    if not path.is_file():
        raise FileNotFoundError(f"model {version!r} not found under {root}")
    model = joblib.load(path)
    if not isinstance(model, BaselineModel):
        raise TypeError(f"{path} does not contain a BaselineModel")
    model.version = version
    return model


def load_meta(version: str, root: Path) -> dict[str, Any]:
    path = Path(root) / version / META_FILE
    if not path.is_file():
        raise FileNotFoundError(f"meta for model {version!r} not found under {root}")
    return json.loads(path.read_text(encoding="utf-8"))
