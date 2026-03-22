"""M06 CLI: build gated training CSVs from split-safe M05 augmented output."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from akk2eng.config import (
    DEFAULT_AUGMENTED_TRAIN_CSV,
    DEFAULT_DEV_SPLIT_CSV,
    DEFAULT_SELECTION_OUTPUT_DIR,
)
from akk2eng.data.selection import SelectionError, run_m06_selection


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "M06: deterministic Policy A/B selection on augmented_train_sentences.csv "
            "(confidence gate, relaxed drop, cap, dev overlap verification)"
        ),
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=DEFAULT_AUGMENTED_TRAIN_CSV,
        help=f"Split-safe M05 augmented CSV (default: {DEFAULT_AUGMENTED_TRAIN_CSV})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_SELECTION_OUTPUT_DIR,
        help=f"Directory for policy CSVs + reports (default: {DEFAULT_SELECTION_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--verify-dev-split-csv",
        type=Path,
        default=DEFAULT_DEV_SPLIT_CSV,
        help=f"Dev split for oare_id overlap check (default: {DEFAULT_DEV_SPLIT_CSV})",
    )
    args = parser.parse_args()
    try:
        out_a, rep_a, out_b, rep_b = run_m06_selection(
            args.input_csv,
            args.output_dir,
            args.verify_dev_split_csv,
            write_policy_b=True,
        )
    except SelectionError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    print("Policy A CSV:", out_a.resolve())
    print("Policy A report:", rep_a.resolve())
    summary = json.loads(rep_a.read_text(encoding="utf-8"))
    print(
        "strict:",
        summary["strict_row_count"],
        "expansion:",
        summary["selected_expansion_row_count"],
        "threshold:",
        summary["confidence_threshold_used"],
        "fallback:",
        summary["fallback_threshold_triggered"],
        "dev_overlap:",
        summary["dev_overlap_oare_ids"],
    )
    if out_b and rep_b:
        print("Policy B CSV:", out_b.resolve())
        print("Policy B report:", rep_b.resolve())


if __name__ == "__main__":
    main()
