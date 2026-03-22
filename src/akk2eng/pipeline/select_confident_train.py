"""M07 CLI: build confidence_v2-scored expansion pool and cap6/cap10 training CSVs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from akk2eng.config import (
    DEFAULT_AUGMENTED_TRAIN_CSV,
    DEFAULT_CONFIDENCE_OUTPUT_DIR,
    DEFAULT_DEV_SPLIT_CSV,
    DEFAULT_POLICY_A_TRAIN_CSV,
)
from akk2eng.data.confidence import ConfidenceError, run_m07_confidence_build


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "M07: deterministic confidence_v2 scoring on split-safe augmented_train_sentences.csv; "
            "emit scored pool + strict_plus_confv2_cap6/cap10 (M06 winners must survive)."
        ),
    )
    parser.add_argument(
        "--input-augmented-csv",
        type=Path,
        default=DEFAULT_AUGMENTED_TRAIN_CSV,
        help=f"M05 split-safe augmented CSV (default: {DEFAULT_AUGMENTED_TRAIN_CSV})",
    )
    parser.add_argument(
        "--baseline-m06-csv",
        type=Path,
        default=DEFAULT_POLICY_A_TRAIN_CSV,
        help=(
            "M06 Policy A baseline CSV for winner identity "
            f"(default: {DEFAULT_POLICY_A_TRAIN_CSV})"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_CONFIDENCE_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_CONFIDENCE_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--verify-dev-split-csv",
        type=Path,
        default=DEFAULT_DEV_SPLIT_CSV,
        help=f"Dev split for oare_id overlap check (default: {DEFAULT_DEV_SPLIT_CSV})",
    )
    parser.add_argument(
        "--cap6",
        type=int,
        default=6,
        help="Expansion cap for candidate A (default: 6)",
    )
    parser.add_argument(
        "--cap10",
        type=int,
        default=10,
        help="Expansion cap for candidate B (default: 10)",
    )
    args = parser.parse_args()

    try:
        paths = run_m07_confidence_build(
            args.input_augmented_csv,
            args.baseline_m06_csv,
            args.output_dir,
            args.verify_dev_split_csv,
            cap6=args.cap6,
            cap10=args.cap10,
        )
    except ConfidenceError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    print("Scored pool:", paths["scored_pool"].resolve())
    print("Main report:", paths["main_report"].resolve())
    print("Cap6 CSV:", paths["cap6_csv"].resolve())
    print("Cap6 report:", paths["cap6_report"].resolve())
    print("Cap10 CSV:", paths["cap10_csv"].resolve())
    print("Cap10 report:", paths["cap10_report"].resolve())
    summary = json.loads(paths["cap6_report"].read_text(encoding="utf-8"))
    print(
        "cap6 strict / expansion:",
        summary["strict_row_count"],
        summary["cap_metadata"]["expansion_rows_selected"],
        "shortfall:",
        summary["cap_metadata"]["shortfall_vs_cap"],
        "dev_overlap:",
        summary["dev_overlap_oare_ids"],
    )


if __name__ == "__main__":
    main()
