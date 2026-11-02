"""Linear SHAP explanations for the baseline (ADR-0003, FR-05, architecture §6).

For a linear logit z_k(x) = b_k + Σ_j w_kj x̃_j over scaled features x̃ and an
independent-feature background with mean μ̃, the exact SHAP values are
φ_j = w_kj (x̃_j − μ̃_j) and the base value is b_k + Σ_j w_kj μ̃_j, so
base + Σφ = z_k(x) holds exactly (AC-05). Cost: O(d) per explanation.
"""

from __future__ import annotations

from typing import Any, TypedDict

import numpy as np
import pandas as pd

from socxai.model.baseline import BaselineModel


class Contribution(TypedDict):
    feature: str
    field: str
    raw_value: float | int
    contribution: float


class Explanation(TypedDict):
    model_version: str | None
    target_class: str
    base_value: float
    output: float
    contributions: list[Contribution]


def explain_linear(
    model: BaselineModel,
    x_raw_row: pd.Series | np.ndarray,
    raw_values: pd.Series | dict[str, Any],
    target_class: str | None = None,
) -> Explanation:
    """Explain one incident.

    ``x_raw_row`` is the model input (transformed features, before scaling);
    ``raw_values`` maps each feature to its value in the raw record (counts,
    0/1). ``target_class`` defaults to the predicted class. Contributions are
    sorted by |φ| descending.
    """
    x = model._matrix(x_raw_row.to_frame().T if isinstance(x_raw_row, pd.Series) else x_raw_row)
    if x.shape[0] != 1:
        raise ValueError("explain_linear explains exactly one row")
    xs = model.scaler.transform(x)[0]
    classes = model.classes_
    proba = model.clf.predict_proba(xs.reshape(1, -1))[0]
    target = target_class if target_class is not None else classes[int(np.argmax(proba))]
    if target not in classes:
        raise ValueError(f"unknown target class {target!r}; expected one of {classes}")
    k = classes.index(target)

    w = np.asarray(model.clf.coef_)[k]
    b = float(np.asarray(model.clf.intercept_)[k])
    mu = model.background_mean if model.background_mean is not None else np.zeros_like(xs)

    phi = w * (xs - mu)
    base = float(b + w @ mu)
    output = float(np.asarray(model.clf.decision_function(xs.reshape(1, -1)))[0][k])

    order = np.argsort(-np.abs(phi), kind="stable")
    contributions: list[Contribution] = []
    for j in order:
        name = model.feature_names[j]
        field = model.feature_sources.get(name, (name, None))[0]
        raw = float(raw_values[name])
        raw_py: float | int = int(raw) if raw.is_integer() else raw
        contributions.append({"feature": name, "field": field, "raw_value": raw_py,
                              "contribution": float(phi[j])})
    return {"model_version": model.version, "target_class": target, "base_value": base,
            "output": output, "contributions": contributions}
