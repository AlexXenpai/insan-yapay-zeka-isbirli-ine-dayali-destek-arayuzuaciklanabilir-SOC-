"""TC-03 (AC-05) and TC-04 (FR-05): linear SHAP explanation; registry round trip."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from socxai.config import CLASSES
from socxai.data.features import load_features, raw_values, write_features
from socxai.data.guide import build_incidents
from socxai.model import registry
from socxai.model.baseline import BaselineModel, evaluate, train
from socxai.model.explain import explain_linear

FIXTURE = Path(__file__).parents[1] / "fixtures" / "guide_mini.csv"


@pytest.fixture(scope="module")
def trained(tmp_path_factory: pytest.TempPathFactory):
    root = tmp_path_factory.mktemp("explain")
    m = build_incidents(FIXTURE, root / "processed")
    d = root / "processed" / m.data_version
    vocab = write_features(d)
    X = pd.concat([load_features(d, s) for s in ("T1", "T2", "VAL")])
    grades = pd.read_parquet(d / "incidents.parquet").set_index("incident_key")["grade"]
    y = grades.reindex(X.index)
    model = train(X, y, C=1.0, seed=42, feature_sources=vocab.feature_sources())
    return model, vocab, X, m.data_version


def test_additivity_on_200_random_inputs(trained) -> None:
    """TC-03: |base + Σφ − logit| ≤ 1e-6 for every class on 200 random incidents."""
    model, vocab, X, _ = trained
    rng = np.random.default_rng(42)
    hi = X.to_numpy().max(axis=0) + 1.0
    rows = rng.uniform(0, 1, size=(200, X.shape[1])) * hi
    for i in range(200):
        x = pd.Series(rows[i], index=X.columns)
        logits = model.decision_function(x.to_frame().T)[0]
        for k, cls in enumerate(model.classes_):
            e = explain_linear(model, x, x, target_class=cls)
            total = e["base_value"] + sum(c["contribution"] for c in e["contributions"])
            assert abs(total - e["output"]) <= 1e-6
            assert abs(e["output"] - logits[k]) <= 1e-9


def test_contributions_sorted_and_linked_to_raw_fields(trained) -> None:
    """TC-04: sorted by |φ| descending; every row has a field and a raw value."""
    model, vocab, X, _ = trained
    key = X.index[0]
    raw = raw_values(X.loc[key], vocab)
    e = explain_linear(model, X.loc[key], raw)
    contrib = e["contributions"]
    assert len(contrib) == len(model.feature_names)
    mags = [abs(c["contribution"]) for c in contrib]
    assert mags == sorted(mags, reverse=True)
    sources = vocab.feature_sources()
    for c in contrib:
        assert c["field"] == sources[c["feature"]][0] and c["field"]
        assert c["raw_value"] == raw[c["feature"]]
        assert isinstance(c["raw_value"], int)
    assert e["target_class"] == model.predict(X.loc[[key]])[0]
    assert e["target_class"] in CLASSES


def test_unknown_target_class_and_wrong_shape_raise(trained) -> None:
    model, vocab, X, _ = trained
    x = X.iloc[0]
    with pytest.raises(ValueError):
        explain_linear(model, x, x, target_class="XX")
    with pytest.raises(ValueError):
        explain_linear(model, X.iloc[:2].to_numpy(), x)
    with pytest.raises(ValueError):
        model.predict_proba(X.drop(columns=X.columns[0]))


def test_train_rejects_bad_labels(trained) -> None:
    _, _, X, _ = trained
    with pytest.raises(ValueError, match="unknown labels"):
        train(X.iloc[:3], ["TP", "BP", "ZZ"])
    with pytest.raises(ValueError, match="every class"):
        train(X.iloc[:2], ["TP", "BP"])
    with pytest.raises(ValueError, match="empty"):
        train(X.iloc[:0], [])


def test_registry_round_trip(trained, tmp_path: Path) -> None:
    model, vocab, X, dv = trained
    meta = {"data_version": dv, "metrics": evaluate(model, X, model.predict(X))}
    version = registry.save(model, meta, tmp_path)
    assert version == f"v1-lr-{dv[:6]}"
    loaded = registry.load(version, tmp_path)
    assert isinstance(loaded, BaselineModel) and loaded.version == version
    np.testing.assert_allclose(loaded.predict_proba(X), model.predict_proba(X))
    assert registry.load_meta(version, tmp_path)["version"] == version
    assert (tmp_path / version / "metrics.json").is_file()
    # Re-saving replaces atomically and leaves no temp folder.
    assert registry.save(model, meta, tmp_path) == version
    assert [p.name for p in tmp_path.iterdir()] == [version]
    with pytest.raises(FileNotFoundError):
        registry.load("v1-lr-000000", tmp_path)
    with pytest.raises(ValueError):
        registry.save(model, {"data_version": dv}, tmp_path)
