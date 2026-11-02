"""TC-05 (FR-04, AC-04) and the τ selection rule (experiment plan §2)."""

from __future__ import annotations

import numpy as np
import pytest

from socxai.model.baseline import TAU_GRID, choose_threshold, needs_review

CLASSES = ("BP", "FP", "TP")


def test_needs_review_boundary() -> None:
    """TC-05: τ = 0.60; confidence 0.5999 / 0.60 / 0.6001 → 1 / 0 / 0."""
    assert needs_review(0.5999, 0.60) is True
    assert needs_review(0.60, 0.60) is False
    assert needs_review(0.6001, 0.60) is False
    np.testing.assert_array_equal(needs_review(np.array([0.5999, 0.60, 0.6001]), 0.60),
                                  [True, False, False])


def test_grid_is_034_to_095() -> None:
    assert TAU_GRID[0] == 0.34 and TAU_GRID[-1] == 0.95 and len(TAU_GRID) == 62
    assert all(round(b - a, 10) == 0.01 for a, b in zip(TAU_GRID, TAU_GRID[1:]))


def _proba(conf: list[float], pred: list[str]) -> np.ndarray:
    """Rows whose max probability is ``conf`` on class ``pred``; the rest split evenly."""
    out = np.zeros((len(conf), 3))
    for i, (c, p) in enumerate(zip(conf, pred)):
        out[i, :] = (1 - c) / 2
        out[i, CLASSES.index(p)] = c
    return out


def test_smallest_tau_reaching_target() -> None:
    # 10 suggestions: confidences 0.40..0.85; the 5 below 0.60 are wrong, the rest right.
    conf = [0.40, 0.45, 0.50, 0.55, 0.58, 0.60, 0.65, 0.70, 0.80, 0.85]
    y = ["BP"] * 10
    pred = ["FP"] * 5 + ["BP"] * 5
    tau, info = choose_threshold(_proba(conf, pred), y, CLASSES, target_acc=0.80, min_coverage=0.50)
    # At τ=0.55 accuracy is 5/7 < 0.8; at 0.56..0.58 it is 5/6 ≥ 0.8 → smallest is 0.56.
    assert tau == pytest.approx(0.56)
    assert info["target_met"] and info["coverage"] == pytest.approx(0.6)
    assert info["selective_accuracy"] == pytest.approx(5 / 6)


def test_coverage_fallback_when_target_needs_too_high_tau() -> None:
    # Only the two most confident are right: 0.80 accuracy needs τ that covers 20 %.
    conf = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
    pred = ["FP"] * 8 + ["BP"] * 2
    tau, info = choose_threshold(_proba(conf, pred), ["BP"] * 10, CLASSES)
    assert not info["target_met"]
    assert info["coverage"] >= 0.50
    # Largest τ still covering half: confidences ≥ 0.60 are 6/10, ≥ 0.61 are 5/10 → 0.65.
    assert tau == pytest.approx(0.65) and info["coverage"] == pytest.approx(0.5)
    assert "coverage" in info["rule"]


def test_unreachable_target_falls_back_to_coverage() -> None:
    conf = [0.5] * 4
    tau, info = choose_threshold(_proba(conf, ["FP"] * 4), ["BP"] * 4, CLASSES)
    assert not info["target_met"] and "unreachable" in info["rule"]
    assert info["coverage"] >= 0.5 and tau == pytest.approx(0.50)


def test_invalid_inputs_raise() -> None:
    with pytest.raises(ValueError):
        choose_threshold(np.zeros((0, 3)), [], CLASSES)
    with pytest.raises(ValueError):
        choose_threshold(np.full((2, 3), 1 / 3), ["BP"], CLASSES)
