"""CLI: load test.csv → infer → write submission.csv."""

from __future__ import annotations

import argparse
from pathlib import Path

from akk2eng.config import DEFAULT_SUBMISSION_CSV, DEFAULT_TEST_CSV
from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_ID
from akk2eng.pipeline.inference import run_inference
from akk2eng.submission.writer import write_submission


def run_pipeline(test_csv: Path, submission_csv: Path) -> None:
    """End-to-end stub pipeline."""
    df = load_csv(test_csv)
    if COL_ID not in df.columns:
        msg = f"test CSV must contain column '{COL_ID}'"
        raise ValueError(msg)
    translations = run_inference(df)
    write_submission(df[COL_ID], translations, submission_csv)


def main() -> None:
    parser = argparse.ArgumentParser(description="akk2eng: build submission.csv from test.csv")
    parser.add_argument(
        "--test-csv",
        type=Path,
        default=DEFAULT_TEST_CSV,
        help=f"Path to test.csv (default: {DEFAULT_TEST_CSV})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SUBMISSION_CSV,
        help=f"Path to write submission.csv (default: {DEFAULT_SUBMISSION_CSV})",
    )
    args = parser.parse_args()
    run_pipeline(args.test_csv, args.output)


if __name__ == "__main__":
    main()
