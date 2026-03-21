"""CLI: load test.csv → infer → write submission.csv."""

from __future__ import annotations

import argparse
from pathlib import Path

from akk2eng.config import (
    BASE_MODEL_ID,
    DEFAULT_MODEL_DIR,
    DEFAULT_SUBMISSION_CSV,
    DEFAULT_TEST_CSV,
)
from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_ID
from akk2eng.pipeline.inference import run_inference
from akk2eng.submission.writer import write_submission


def run_pipeline(
    test_csv: Path,
    submission_csv: Path,
    *,
    model_dir: Path | None = None,
    batch_size: int = 8,
    quiet: bool = False,
) -> None:
    """Load test.csv, run T5 baseline inference, write submission.csv."""
    df = load_csv(test_csv)
    if COL_ID not in df.columns:
        msg = f"test CSV must contain column '{COL_ID}'"
        raise ValueError(msg)
    translations = run_inference(
        df,
        model_dir=model_dir,
        batch_size=batch_size,
        quiet=quiet,
    )
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
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help=(
            "Directory with fine-tuned weights (config.json + tokenizer); "
            f"default {DEFAULT_MODEL_DIR}. If missing, loads base {BASE_MODEL_ID}."
        ),
    )
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--quiet", action="store_true", help="Suppress debug prints")
    args = parser.parse_args()
    run_pipeline(
        args.test_csv,
        args.output,
        model_dir=args.model_dir,
        batch_size=args.batch_size,
        quiet=args.quiet,
    )


if __name__ == "__main__":
    main()
