"""Project-wide constants and path settings.

Path defaults are relative to the project root and can be overridden with
``SOCXAI_*`` environment variables (architecture §"Yapılandırma").
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Incident grades (GUIDE): TruePositive, BenignPositive, FalsePositive.
CLASSES: tuple[str, ...] = ("TP", "BP", "FP")

# In-scope incident categories (SRS §3).
CATEGORIES: tuple[str, ...] = ("InitialAccess", "SuspiciousActivity", "Exfiltration")

# Time-ordered four-slice split (ADR-0004): T1 / T2 / validation / locked test.
SLICES: tuple[str, ...] = ("T1", "T2", "VAL", "TEST")
SPLIT_RATIOS: tuple[float, float, float, float] = (0.50, 0.20, 0.15, 0.15)

# Feature vocabulary sizes learned from T1 (data-design §9.4, decision list item 6).
VOCAB_SIZES: dict[str, int] = {"entity": 15, "roles": 7, "mitre": 20}

# Bump when the pipeline's output semantics change; part of the data version (§9.7).
PIPELINE_VERSION: str = "1"

# Threshold selection targets (experiment plan §2).
TARGET_ACCURACY: float = 0.80
MIN_COVERAGE: float = 0.50

# Free-text reason length cap (decision list item 9).
MAX_REASON_CHARS: int = 2000

PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

ENV_PREFIX = "SOCXAI_"


def _env_path(name: str, default: Path) -> Path:
    value = os.environ.get(ENV_PREFIX + name)
    return Path(value).expanduser().resolve() if value else default


@dataclass(frozen=True)
class Settings:
    """Filesystem locations used by the pipeline, the stores and the API."""

    data_dir: Path
    raw_guide_dir: Path
    processed_dir: Path
    reference_dir: Path
    app_dir: Path
    models_dir: Path
    web_dir: Path
    host: str = "127.0.0.1"
    port: int = 8000

    @property
    def app_db(self) -> Path:
        return self.app_dir / "app.db"

    @property
    def labels_db(self) -> Path:
        return self.app_dir / "labels.db"

    @property
    def participants_db(self) -> Path:
        return self.app_dir / "participants.db"

    @property
    def guide_train_csv(self) -> Path:
        return self.raw_guide_dir / "GUIDE_Train.csv"

    @property
    def mitre_csv(self) -> Path:
        return self.reference_dir / "mitre_techniques.csv"

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from defaults, overridden by ``SOCXAI_*`` variables.

        ``SOCXAI_DATA_DIR`` moves every data sub-folder unless that folder has
        its own override.
        """
        data_dir = _env_path("DATA_DIR", PROJECT_ROOT / "data")
        port_raw = os.environ.get(ENV_PREFIX + "PORT", "8000")
        try:
            port = int(port_raw)
        except ValueError as exc:
            raise ValueError(f"{ENV_PREFIX}PORT must be an integer, got {port_raw!r}") from exc
        return cls(
            data_dir=data_dir,
            raw_guide_dir=_env_path("RAW_GUIDE_DIR", data_dir / "raw" / "guide"),
            processed_dir=_env_path("PROCESSED_DIR", data_dir / "processed"),
            reference_dir=_env_path("REFERENCE_DIR", data_dir / "reference"),
            app_dir=_env_path("APP_DIR", data_dir / "app"),
            models_dir=_env_path("MODELS_DIR", PROJECT_ROOT / "artifacts" / "models"),
            web_dir=_env_path("WEB_DIR", PROJECT_ROOT / "web"),
            host=os.environ.get(ENV_PREFIX + "HOST", "127.0.0.1"),
            port=port,
        )
