"""M04 CLI: build sentence-aligned training CSV from official bundle files."""

from __future__ import annotations

import argparse
from pathlib import Path

from akk2eng.config import (
    DEFAULT_ALIGNED_TRAIN_CSV,
    DEFAULT_ALIGNMENT_OUTPUT_DIR,
    DEFAULT_ALIGNMENT_REPORT_JSON,
    DEFAULT_SENTENCES_AID_CSV,
    DEFAULT_TRAIN_CSV,
)
from akk2eng.data.alignment import build_aligned_training_csv, write_baseline_alignment_audit


def main() -> None:
    parser = argparse.ArgumentParser(
        description="M04: deterministic sentence alignment (train.csv + OARE sentences aid)",
    )
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=DEFAULT_TRAIN_CSV,
        help=f"Official train.csv (default: {DEFAULT_TRAIN_CSV})",
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
        default=DEFAULT_ALIGNMENT_OUTPUT_DIR,
        help=f"Directory for aligned CSV + report (default: {DEFAULT_ALIGNMENT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--aligned-csv",
        type=Path,
        default=None,
        help=(
            "Override output aligned CSV path "
            f"(default: {DEFAULT_ALIGNED_TRAIN_CSV.name} under --output-dir)"
        ),
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help=f"Override alignment_report.json path (default: {DEFAULT_ALIGNMENT_REPORT_JSON})",
    )
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="Write baseline_alignment_audit.json only (Phase A data audit)",
    )
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=Path("outputs") / "alignment" / "baseline_alignment_audit.json",
        help="Path for --audit-only JSON",
    )
    args = parser.parse_args()

    out_dir = args.output_dir
    aligned = args.aligned_csv or (out_dir / "aligned_train_sentences.csv")
    report = args.report_json or (out_dir / "alignment_report.json")

    if args.audit_only:
        audit = write_baseline_alignment_audit(
            args.train_csv,
            args.sentences_aid_csv,
            args.audit_output,
        )
        print("Wrote audit:", args.audit_output.resolve())
        print("train_docs_with_aid_rows:", audit["train_docs_with_aid_rows"])
        return

    rep = build_aligned_training_csv(
        args.train_csv,
        args.sentences_aid_csv,
        aligned,
        report,
    )
    print("Aligned CSV:", aligned.resolve())
    print("Report:", report.resolve())
    print("docs_aligned:", rep.docs_aligned, "/", rep.docs_processed)
    print("sentence_pairs:", rep.sentence_pairs)
    print("aligned_csv_sha256:", rep.aligned_csv_sha256)


if __name__ == "__main__":
    main()
