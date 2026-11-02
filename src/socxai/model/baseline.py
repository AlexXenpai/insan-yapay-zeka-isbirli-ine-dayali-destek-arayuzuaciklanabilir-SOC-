"""E1 baseline: StandardScaler + multinomial LogisticRegression (experiment plan §5).

Also holds the evaluation metrics (§2), the dummy baselines (§3) and the
"needs review" threshold rule (FR-04, §2).

Cost: lbfgs on n × d (d = 60) costs O(n·d·k) per iteration for k = 3 classes;
threshold selection sorts nothing, it scans a 62-point grid in O(n) each.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler

from socxai.config import CLASSES, MIN_COVERAGE, TARGET_ACCURACY

MAX_ITER = 2000
# τ grid: 0.34, 0.35, …, 0.95 (experiment plan §2), built from integers to avoid drift.
TAU_GRID: tuple[float, ...] = tuple(k / 100 for k in range(34, 96))


@dataclass
class BaselineModel:
    scaler: StandardScaler
    clf: LogisticRegression
    feature_names: list[str]
    feature_sources: dict[str, tuple[str, str | None]] = field(default_factory=dict)
    background_mean: np.ndarray | None = None  # mean of scaled training features (SHAP baseline)
    version: str | None = None

    @property
    def classes_(self) -> tuple[str, ...]:
        return tuple(str(c) for c in self.clf.classes_)

    def _matrix(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        if isinstance(X, pd.DataFrame):
            missing = [c for c in self.feature_names if c not in X.columns]
            if missing:
                raise ValueError(f"missing feature columns: {missing[:5]}")
            X = X[self.feature_names].to_numpy()
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        if arr.shape[1] != len(self.feature_names):
            raise ValueError(f"expected {len(self.feature_names)} features, got {arr.shape[1]}")
        return arr

    def scaled(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        return np.asarray(self.scaler.transform(self._matrix(X)))

    def predict_proba(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        return np.asarray(self.clf.predict_proba(self.scaled(X)))

    def decision_function(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Per-class logits z_k = w_k · x̃ + b_k (softmax inputs)."""
        return self.clf.decision_function(self.scaled(X))

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        return self.clf.predict(self.scaled(X))


def train(
    X: pd.DataFrame,
    y: Sequence[str] | pd.Series,
    C: float = 1.0,
    seed: int = 42,
    feature_sources: dict[str, tuple[str, str | None]] | None = None,
) -> BaselineModel:
    """Fit the scaler and the classifier on the training slice only (T1)."""
    if len(X) == 0:
        raise ValueError("empty training set")
    labels = np.asarray(y)
    unknown = set(labels) - set(CLASSES)
    if unknown:
        raise ValueError(f"unknown labels: {sorted(unknown)}")
    if set(labels) != set(CLASSES):
        # Explanations index one coefficient row per class (multinomial, k = 3).
        raise ValueError(f"training set must contain every class {CLASSES}")
    names = [str(c) for c in X.columns]
    arr = X.to_numpy(dtype=np.float64)
    scaler = StandardScaler().fit(arr)
    Xs = np.asarray(scaler.transform(arr))
    clf = LogisticRegression(C=C, class_weight="balanced", max_iter=MAX_ITER, random_state=seed,
                             solver="lbfgs")
    clf.fit(Xs, labels)
    return BaselineModel(scaler=scaler, clf=clf, feature_names=names,
                         feature_sources=dict(feature_sources or {}),
                         background_mean=Xs.mean(axis=0))


def metrics_from_predictions(y_true: Any, y_pred: Any) -> dict[str, Any]:
    """Macro-F1, accuracy, per-class P/R/F1 and the confusion matrix (experiment plan §2)."""
    labels = list(CLASSES)
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    return {
        "macro_f1": float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "per_class": {c: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i]),
                          "support": int(s[i])} for i, c in enumerate(labels)},
        "confusion_matrix": {"labels": labels,
                             "matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist()},
        "n": int(len(y_true)),
    }


def evaluate(model: BaselineModel, X: pd.DataFrame, y: Sequence[str] | pd.Series) -> dict[str, Any]:
    return metrics_from_predictions(np.asarray(y), model.predict(X))


def dummy_baselines(y_train: Sequence[str], y_eval: Sequence[str], seed: int = 42) -> dict[str, dict]:
    """Stratified-random and majority-class baselines (experiment plan §3)."""
    out = {}
    Xtr = np.zeros((len(y_train), 1))
    Xev = np.zeros((len(y_eval), 1))
    for strategy in ("stratified", "most_frequent"):
        d = DummyClassifier(strategy=strategy, random_state=seed).fit(Xtr, np.asarray(y_train))
        out[strategy] = metrics_from_predictions(np.asarray(y_eval), d.predict(Xev))
    return out


def needs_review(confidence: float | np.ndarray, tau: float) -> bool | np.ndarray:
    """FR-04: a suggestion whose confidence is below τ is flagged "inceleme gerekli"."""
    result = np.asarray(confidence) < tau
    return bool(result) if result.ndim == 0 else result


def choose_threshold(
    proba: np.ndarray,
    y: Sequence[str] | pd.Series,
    classes: Sequence[str],
    target_acc: float = TARGET_ACCURACY,
    min_coverage: float = MIN_COVERAGE,
    grid: Sequence[float] = TAU_GRID,
) -> tuple[float, dict[str, Any]]:
    """Experiment plan §2 rule, evaluated on the validation slice.

    1. Scan τ over the grid; selective accuracy = accuracy of suggestions with
       confidence ≥ τ, coverage = their share.
    2. Pick the smallest τ whose selective accuracy ≥ ``target_acc``.
    3. If that τ leaves coverage < ``min_coverage`` (or no τ reaches the target),
       pick the largest τ whose coverage is still ≥ ``min_coverage`` and report
       that the target was not met.
    """
    proba = np.asarray(proba, dtype=np.float64)
    y_arr = np.asarray(y)
    if proba.ndim != 2 or proba.shape[0] != len(y_arr) or proba.shape[0] == 0:
        raise ValueError("proba must be a non-empty (n, k) array aligned with y")
    conf = proba.max(axis=1)
    pred = np.asarray(classes)[proba.argmax(axis=1)]
    correct = pred == y_arr
    n = len(y_arr)

    table = []
    for tau in grid:
        mask = conf >= tau
        k = int(mask.sum())
        table.append({"tau": float(tau), "coverage": k / n,
                      "selective_accuracy": float(correct[mask].mean()) if k else None})

    meets = [r for r in table if r["selective_accuracy"] is not None
             and r["selective_accuracy"] >= target_acc]
    chosen = meets[0] if meets else None
    rule = "smallest tau with selective accuracy >= target"
    target_met = chosen is not None and chosen["coverage"] >= min_coverage
    if not target_met:
        covered = [r for r in table if r["coverage"] >= min_coverage]
        chosen = covered[-1] if covered else table[0]
        rule = ("accuracy target unreachable; largest tau with coverage >= minimum" if not meets
                else "coverage fell below minimum; largest tau with coverage >= minimum")
    assert chosen is not None
    info = {
        "tau": chosen["tau"],
        "coverage": chosen["coverage"],
        "selective_accuracy": chosen["selective_accuracy"],
        "target_accuracy": target_acc,
        "min_coverage": min_coverage,
        "target_met": bool(target_met),
        "rule": rule,
        "overall_accuracy": float(correct.mean()),
        "grid": table,
    }
    return float(chosen["tau"]), info
