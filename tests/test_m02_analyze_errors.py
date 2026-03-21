"""M02-B: error analysis bucketing."""

from __future__ import annotations

import json
from pathlib import Path

from akk2eng.pipeline.analyze_errors import (
    classify_row,
    has_repetition,
    numeric_error,
    run_analysis,
)


def test_has_repetition_simple() -> None:
    assert has_repetition("foo bar foo bar")
    assert not has_repetition("a b c")
    assert not has_repetition("a b a")


def test_classify_row_repetition_and_numeric() -> None:
    flags = classify_row(
        reference="10 minas of silver",
        prediction="10 minas minas minas",
    )
    assert flags["repetition"] is True
    assert flags["numeric_errors"] is False


def test_numeric_error_missing_digits_in_pred() -> None:
    assert numeric_error("10 minas", "minas of silver")
    assert not numeric_error("no numbers here", "also none")


def test_run_analysis_writes_artifacts(tmp_path: Path) -> None:
    pred_csv = tmp_path / "predictions_dev.csv"
    pred_csv.write_text(
        "oare_id,transliteration,translation,prediction\n"
        "r1,x,one two three,one two one two\n"
        "r2,y,alpha beta gamma delta,hi\n"
        "r3,z,5 shekels,five only\n",
        encoding="utf-8",
    )
    out_dir = tmp_path / "analysis"
    summary = run_analysis(pred_csv, out_dir, examples_per_bucket=3, quiet=True)

    assert summary["total_samples"] == 3
    assert (out_dir / "error_buckets.json").is_file()
    assert (out_dir / "bucket_examples.txt").is_file()

    blob = json.loads((out_dir / "error_buckets.json").read_text(encoding="utf-8"))
    assert blob["total_samples"] == 3
    assert all(k in blob for k in summary if k != "total_samples")

    txt = (out_dir / "bucket_examples.txt").read_text(encoding="utf-8")
    assert "REPETITION" in txt
    assert "LENGTH_MISMATCH" in txt or "LOW_OVERLAP" in txt
