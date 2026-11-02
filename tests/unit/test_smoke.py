"""Import smoke test for the package and its configuration."""

from __future__ import annotations

import math

import socxai
from socxai import config


def test_package_imports_and_config_is_consistent(settings: config.Settings) -> None:
    assert socxai.__version__
    assert config.CLASSES == ("TP", "BP", "FP")
    assert len(config.SLICES) == len(config.SPLIT_RATIOS) == 4
    assert math.isclose(sum(config.SPLIT_RATIOS), 1.0)
    # SOCXAI_DATA_DIR override reaches every data sub-folder.
    assert settings.app_db.parent == settings.data_dir / "app"
    assert settings.processed_dir == settings.data_dir / "processed"
