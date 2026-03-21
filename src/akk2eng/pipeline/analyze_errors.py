"""M02-B: error bucketing from dev predictions (observation only — no model changes)."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from akk2eng.config import (
    DEFAULT_ANALYSIS_OUTPUT_DIR,
    DEFAULT_PREDICTIONS_DEV_CSV,
)
from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_OARE_ID, COL_TRANSLATION

# Bucket thresholds (M02-B v1 — document when tuning)
LENGTH_RATIO_TOO_LONG = 1.8
LENGTH_RATIO_TOO_SHORT = 0.5
LOW_OVERLAP_THRESHOLD = 0.2
EMPTY_MAX_TOKENS = 2  # flag when len(tokens) < 3
EXAMPLES_PER_BUCKET = 5
EXAMPLE_MAX_CHARS = 320

PRED_COL = "prediction"
BUCKET_KEYS = (
    "repetition",
    "length_mismatch",
    "low_overlap",
    "empty",
    "numeric_errors",
)


def _tokens(text: str) -> list[str]:
    return str(text).split()


def has_repetition(text: str) -> bool:
    """True if any bigram occurs at least twice (phrase loop / n-gram repetition).

    Token-uniqueness (``len(tokens) != len(set(tokens))``) flags almost all English
    because of repeated function words; bigram recurrence matches M02 intent better.
    """
    tokens = _tokens(text)
    if len(tokens) < 2:
        return False
    bigrams = [tuple(tokens[i : i + 2]) for i in range(len(tokens) - 1)]
    return any(c >= 2 for c in Counter(bigrams).values())


def length_mismatch(pred_tokens: list[str], ref_tokens: list[str]) -> bool:
    """Too long or too short vs reference (skip when reference has no tokens)."""
    if not ref_tokens:
        return False
    ratio = len(pred_tokens) / len(ref_tokens)
    return ratio > LENGTH_RATIO_TOO_LONG or ratio < LENGTH_RATIO_TOO_SHORT


def low_overlap(pred_tokens: list[str], ref_tokens: list[str]) -> bool:
    """Low token-set overlap with reference (skip when reference has no token types)."""
    ref_set = {t for t in ref_tokens if t}
    if not ref_set:
        return False
    pred_set = set(pred_tokens)
    overlap = len(pred_set & ref_set) / len(ref_set)
    return overlap < LOW_OVERLAP_THRESHOLD


def empty_or_near_empty(text: str) -> bool:
    return len(_tokens(text)) < 3


def _digit_groups(text: str) -> list[str]:
    return re.findall(r"\d+(?:\.\d+)?", text)


def numeric_error(reference: str, prediction: str) -> bool:
    """Reference has numbers but prediction omits them or changes count."""
    ref_g = _digit_groups(reference)
    if not ref_g:
        return False
    pred_g = _digit_groups(prediction)
    if not pred_g:
        return True
    return len(pred_g) != len(ref_g)


def _truncate(s: str, max_chars: int = EXAMPLE_MAX_CHARS) -> str:
    s = s.replace("\n", " ").strip()
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 1] + "…"


def classify_row(
    reference: str,
    prediction: str,
) -> dict[str, bool]:
    ref_t = _tokens(reference)
    pred_t = _tokens(prediction)
    return {
        "repetition": has_repetition(prediction),
        "length_mismatch": length_mismatch(pred_t, ref_t),
        "low_overlap": low_overlap(pred_t, ref_t),
        "empty": empty_or_near_empty(prediction),
        "numeric_errors": numeric_error(reference, prediction),
    }


def run_analysis(
    predictions_csv: Path,
    output_dir: Path,
    *,
    examples_per_bucket: int = EXAMPLES_PER_BUCKET,
    quiet: bool = False,
) -> dict[str, Any]:
    """Load predictions_dev-style CSV; write error_buckets.json and bucket_examples.txt."""
    df = load_csv(predictions_csv)
    if PRED_COL not in df.columns or COL_TRANSLATION not in df.columns:
        msg = f"CSV must contain {PRED_COL!r} and {COL_TRANSLATION!r}"
        raise ValueError(msg)

    total = len(df)
    if total == 0:
        msg = "No rows to analyze"
        raise ValueError(msg)

    counts: dict[str, int] = {k: 0 for k in BUCKET_KEYS}
    examples: dict[str, list[tuple[str, str, str]]] = defaultdict(list)

    for idx, row in df.iterrows():
        ref = str(row[COL_TRANSLATION])
        pred = str(row[PRED_COL])
        flags = classify_row(ref, pred)
        row_id = str(row[COL_OARE_ID]) if COL_OARE_ID in df.columns else str(idx)

        for key in BUCKET_KEYS:
            if flags[key]:
                counts[key] += 1
                if len(examples[key]) < examples_per_bucket:
                    examples[key].append((row_id, pred, ref))

    summary: dict[str, Any] = {"total_samples": total}
    for key in BUCKET_KEYS:
        c = counts[key]
        summary[key] = {
            "count": c,
            "percent": round(c / total, 4) if total else 0.0,
        }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "error_buckets.json"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines: list[str] = []
    for key in BUCKET_KEYS:
        title = key.upper()
        lines.append(f"=== {title} ===")
        if not examples[key]:
            lines.append("(no examples in sample cap)")
        for row_id, pred, ref in examples[key]:
            lines.append(f"[ID {row_id}]")
            lines.append(f"PRED: {_truncate(pred)}")
            lines.append(f"REF:  {_truncate(ref)}")
            lines.append("")
        lines.append("")

    txt_path = output_dir / "bucket_examples.txt"
    txt_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    if not quiet:
        print("Wrote", json_path)
        print("Wrote", txt_path)
        print(json.dumps(summary, indent=2))

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="M02-B: bucket errors from dev predictions (observation only)",
    )
    parser.add_argument(
        "--predictions-csv",
        type=Path,
        default=DEFAULT_PREDICTIONS_DEV_CSV,
        help=f"predictions_dev.csv from pipeline.eval (default: {DEFAULT_PREDICTIONS_DEV_CSV})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_ANALYSIS_OUTPUT_DIR,
        help=(
            "Directory for error_buckets.json and bucket_examples.txt "
            f"(default: {DEFAULT_ANALYSIS_OUTPUT_DIR})"
        ),
    )
    parser.add_argument(
        "--examples-per-bucket",
        type=int,
        default=EXAMPLES_PER_BUCKET,
        help="Max example rows to record per bucket in bucket_examples.txt",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    run_analysis(
        args.predictions_csv,
        args.output_dir,
        examples_per_bucket=args.examples_per_bucket,
        quiet=args.quiet,
    )


if __name__ == "__main__":
    main()
