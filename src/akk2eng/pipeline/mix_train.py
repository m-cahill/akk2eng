"""M04 CLI: build mixed_train.csv (document + aligned sentence rows)."""

from __future__ import annotations

import argparse
from pathlib import Path

from akk2eng.config import (
    DEFAULT_ALIGNED_TRAIN_CSV,
    DEFAULT_MIXED_TRAIN_CSV,
    DEFAULT_MIXED_TRAIN_STATS_JSON,
    DEFAULT_TRAIN_CSV,
)
from akk2eng.data.mixed_train import build_mixed_train_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "M04: concatenate train.csv + aligned_train_sentences.csv for mixed fine-tuning"
        ),
    )
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=DEFAULT_TRAIN_CSV,
        help=f"Document-level train.csv (default: {DEFAULT_TRAIN_CSV})",
    )
    parser.add_argument(
        "--aligned-csv",
        type=Path,
        default=DEFAULT_ALIGNED_TRAIN_CSV,
        help=f"Sentence-aligned CSV (default: {DEFAULT_ALIGNED_TRAIN_CSV})",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=DEFAULT_MIXED_TRAIN_CSV,
        help=f"Output mixed CSV (default: {DEFAULT_MIXED_TRAIN_CSV})",
    )
    parser.add_argument(
        "--stats-json",
        type=Path,
        default=DEFAULT_MIXED_TRAIN_STATS_JSON,
        help=f"Write composition stats (default: {DEFAULT_MIXED_TRAIN_STATS_JSON})",
    )
    parser.add_argument(
        "--no-stats-json",
        action="store_true",
        help="Do not write stats JSON",
    )
    args = parser.parse_args()
    stats_path = None if args.no_stats_json else args.stats_json
    stats = build_mixed_train_csv(
        args.train_csv,
        args.aligned_csv,
        args.output_csv,
        stats_json=stats_path,
    )
    print("Wrote:", args.output_csv.resolve())
    print(
        "rows: document=",
        stats["document_rows"],
        "aligned=",
        stats["aligned_rows"],
        "total=",
        stats["total_rows"],
    )
    print("aligned_fraction_of_total:", round(stats["aligned_fraction_of_total"], 6))
    if stats_path:
        print("Stats:", stats_path.resolve())


if __name__ == "__main__":
    main()
