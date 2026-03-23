"""M08 CLI: alignment-quality v2 builder (strict + semicolon/colon repair)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from akk2eng.config import (
    DEFAULT_ALIGNED_TRAIN_SPLIT_CSV,
    DEFAULT_ALIGNMENT_QUALITY_OUTPUT_DIR,
    DEFAULT_DEV_SPLIT_CSV,
    DEFAULT_POLICY_A_TRAIN_CSV,
    DEFAULT_SENTENCES_AID_CSV,
    DEFAULT_TRAIN_SPLIT_CSV,
)
from akk2eng.data.alignment_quality import AlignmentQualityError, build_alignment_quality_v2


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "M08: build split-safe alignment-quality v2 training CSVs "
            "(strict + narrow ;/: clause resplit repair)"
        ),
    )
    parser.add_argument(
        "--train-split-csv",
        type=Path,
        default=DEFAULT_TRAIN_SPLIT_CSV,
        help=f"Train split only (default: {DEFAULT_TRAIN_SPLIT_CSV})",
    )
    parser.add_argument(
        "--dev-split-csv",
        type=Path,
        default=DEFAULT_DEV_SPLIT_CSV,
        help=f"Dev split for overlap check (default: {DEFAULT_DEV_SPLIT_CSV})",
    )
    parser.add_argument(
        "--sentences-aid-csv",
        type=Path,
        default=DEFAULT_SENTENCES_AID_CSV,
        help=f"OARE sentences aid (default: {DEFAULT_SENTENCES_AID_CSV})",
    )
    parser.add_argument(
        "--m06-baseline-csv",
        type=Path,
        default=DEFAULT_POLICY_A_TRAIN_CSV,
        help=f"M06 Policy A baseline for winner union (default: {DEFAULT_POLICY_A_TRAIN_CSV})",
    )
    parser.add_argument(
        "--strict-baseline-csv",
        type=Path,
        default=DEFAULT_ALIGNED_TRAIN_SPLIT_CSV,
        help=(
            "Optional M04 split-safe strict CSV for early no-op gate fingerprint "
            f"(default: {DEFAULT_ALIGNED_TRAIN_SPLIT_CSV})"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_ALIGNMENT_QUALITY_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_ALIGNMENT_QUALITY_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--no-strict-baseline-compare",
        action="store_true",
        help="Skip M04 strict CSV fingerprint for early no-op gate (not recommended)",
    )
    args = parser.parse_args()

    strict_ref: Path | None = None if args.no_strict_baseline_compare else args.strict_baseline_csv

    try:
        rep = build_alignment_quality_v2(
            args.train_split_csv,
            args.dev_split_csv,
            args.sentences_aid_csv,
            args.output_dir,
            args.m06_baseline_csv,
            strict_baseline_csv=strict_ref,
        )
    except AlignmentQualityError as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)

    print("Wrote:", args.output_dir.resolve())
    print("Candidate A:", rep["output_candidate_a_csv"])
    print("Candidate B:", rep["output_candidate_b_csv"])
    print("strict_row_count:", rep["strict_row_count"])
    print("recovered_row_count:", rep["recovered_row_count"])
    print("early_no_op_stop_recommended:", rep["early_no_op_stop_recommended"])
    no_op_keys = (
        "early_no_op_gate_candidate_a",
        "early_no_op_gate_candidate_b_identical_to_m06_baseline",
    )
    print(json.dumps({k: rep[k] for k in no_op_keys}, indent=2))


if __name__ == "__main__":
    main()
