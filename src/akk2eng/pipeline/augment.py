"""M05 CLI: build split-safe augmented sentence training CSV (alignment expansion)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from akk2eng.config import (
    DEFAULT_AUGMENTATION_OUTPUT_DIR,
    DEFAULT_AUGMENTATION_REPORT_JSON,
    DEFAULT_AUGMENTED_TRAIN_CSV,
    DEFAULT_DEV_SPLIT_CSV,
    DEFAULT_SENTENCES_AID_CSV,
    DEFAULT_TRAIN_SPLIT_CSV,
)
from akk2eng.data.alignment import verify_aligned_no_dev_oare_overlap
from akk2eng.data.augmentation import build_augmented_training_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "M05: deterministic alignment expansion — augmented_train_sentences.csv + report "
            "(train_split + official aid only; use --split-safe for leak checks)"
        ),
    )
    parser.add_argument(
        "--split-safe",
        action="store_true",
        help=(
            "Read train from persisted split only (default: "
            f"{DEFAULT_TRAIN_SPLIT_CSV}); verify zero oare_id overlap vs dev split"
        ),
    )
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=None,
        help=(
            "Training document CSV (default with --split-safe: "
            f"{DEFAULT_TRAIN_SPLIT_CSV}; else must be passed explicitly)"
        ),
    )
    parser.add_argument(
        "--sentences-aid-csv",
        type=Path,
        default=DEFAULT_SENTENCES_AID_CSV,
        help=f"Sentences_Oare_FirstWord_LinNum.csv (default: {DEFAULT_SENTENCES_AID_CSV})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_AUGMENTATION_OUTPUT_DIR,
        help=f"Directory for augmented CSV + report (default: {DEFAULT_AUGMENTATION_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=None,
        help=(
            "Override augmented CSV path (default: "
            f"{DEFAULT_AUGMENTED_TRAIN_CSV.name} under --output-dir)"
        ),
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help=(
            "Override augmentation_report.json path "
            f"(default: {DEFAULT_AUGMENTATION_REPORT_JSON.name})"
        ),
    )
    parser.add_argument(
        "--verify-dev-split-csv",
        type=Path,
        default=None,
        help=(
            "After build, verify no oare_id overlap with this dev split "
            f"(default with --split-safe: {DEFAULT_DEV_SPLIT_CSV})"
        ),
    )
    args = parser.parse_args()

    if args.split_safe and args.train_csv is None:
        train_input = DEFAULT_TRAIN_SPLIT_CSV
    elif args.train_csv is not None:
        train_input = args.train_csv
    else:
        print(
            "ERROR: provide --train-csv or use --split-safe (uses train_split.csv).",
            file=sys.stderr,
        )
        sys.exit(2)

    out_dir = args.output_dir
    out_csv = args.output_csv or (out_dir / DEFAULT_AUGMENTED_TRAIN_CSV.name)
    out_report = args.report_json or (out_dir / DEFAULT_AUGMENTATION_REPORT_JSON.name)

    rep = build_augmented_training_csv(
        train_input,
        args.sentences_aid_csv,
        out_csv,
        out_report,
    )
    print("Train input:", train_input.resolve())
    print("Augmented CSV:", out_csv.resolve())
    print("Report:", out_report.resolve())
    print("docs_strict:", rep.docs_strict, "docs_expanded:", rep.docs_expanded)
    print("rows_strict:", rep.rows_strict, "rows_expanded:", rep.rows_expanded)
    print("augmentation_type_counts:", dict(rep.augmentation_type_counts))
    print("augmented_csv_sha256:", rep.augmented_csv_sha256)

    dev_verify = args.verify_dev_split_csv
    if args.split_safe and dev_verify is None:
        dev_verify = DEFAULT_DEV_SPLIT_CSV
    if dev_verify is not None:
        check = verify_aligned_no_dev_oare_overlap(out_csv, dev_verify)
        print("Dev overlap check:", json.dumps(check, indent=2))
        if not check["passes"]:
            print(
                "ERROR: augmented output shares oare_id with dev split — leakage risk.",
                file=sys.stderr,
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
