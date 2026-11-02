"""Build the processed GUIDE dataset: incidents, four slices, evidence, T1 vocabulary, features.

Usage: python scripts/build_dataset.py [--raw PATH] [--out DIR] [--memory-limit 4GB]
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from socxai.config import Settings
from socxai.data.features import write_features
from socxai.data.guide import PipelineError, build_incidents


def main(argv: list[str] | None = None) -> int:
    settings = Settings.from_env()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", type=Path, default=settings.guide_train_csv)
    ap.add_argument("--out", type=Path, default=settings.processed_dir)
    ap.add_argument("--memory-limit", default="4GB", help="DuckDB memory limit (NFR-03: peak <= 6 GB)")
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    t0 = time.perf_counter()
    try:
        manifest = build_incidents(args.raw, args.out, memory_limit=args.memory_limit)
    except (FileNotFoundError, PipelineError, ValueError) as exc:
        logging.error("%s", exc)
        return 1
    print(manifest.summary())
    dataset_dir = args.out / manifest.data_version
    vocab = write_features(dataset_dir)
    print(f"vocab (T1): {len(vocab.entity_types)} entity types, {len(vocab.roles)} Roles values, "
          f"{len(vocab.techniques)} techniques -> {len(vocab.feature_names)} features")
    print(f"output: {args.out / manifest.data_version}  ({time.perf_counter() - t0:.1f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
