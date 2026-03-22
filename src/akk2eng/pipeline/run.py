"""CLI: load test.csv → infer → write submission.csv."""

from __future__ import annotations

import argparse
from pathlib import Path

from akk2eng.config import (
    BASE_MODEL_ID,
    DEFAULT_LEXICON_CSV,
    DEFAULT_MODEL_DIR,
    DEFAULT_SUBMISSION_CSV,
    DEFAULT_TEST_CSV,
    DEFAULT_TRAIN_CSV,
    LEXICON_MAX_ENTRIES,
    USE_LEXICON,
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
    use_lexicon: bool | None = None,
    use_normalization: bool | None = None,
    train_csv: Path | None = None,
    lexicon_csv: Path | None = None,
    lexicon_max_entries: int | None = None,
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
        use_lexicon=use_lexicon,
        use_normalization=use_normalization,
        train_csv=DEFAULT_TRAIN_CSV if train_csv is None else train_csv,
        lexicon_csv=lexicon_csv,
        lexicon_max_entries=lexicon_max_entries,
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
    parser.add_argument(
        "--no-lexicon",
        action="store_true",
        help="Disable M02-D lexicon post-processing on predictions",
    )
    parser.add_argument(
        "--no-normalization",
        action="store_true",
        help="Disable M03 transliteration normalization before tokenization",
    )
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=DEFAULT_TRAIN_CSV,
        help=f"train.csv for lexicon filtering (default: {DEFAULT_TRAIN_CSV})",
    )
    parser.add_argument(
        "--lexicon-csv",
        type=Path,
        default=None,
        help=f"eBL lexicon CSV (default: {DEFAULT_LEXICON_CSV})",
    )
    parser.add_argument(
        "--lexicon-max-entries",
        type=int,
        default=None,
        help=f"Lexicon cap (default: {LEXICON_MAX_ENTRIES})",
    )
    args = parser.parse_args()
    run_pipeline(
        args.test_csv,
        args.output,
        model_dir=args.model_dir,
        batch_size=args.batch_size,
        quiet=args.quiet,
        use_lexicon=False if args.no_lexicon else USE_LEXICON,
        use_normalization=False if args.no_normalization else None,
        train_csv=args.train_csv,
        lexicon_csv=args.lexicon_csv,
        lexicon_max_entries=args.lexicon_max_entries,
    )


if __name__ == "__main__":
    main()
