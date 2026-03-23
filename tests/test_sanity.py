"""Sanity tests: pipeline produces a valid, deterministic submission file."""

from pathlib import Path

import pandas as pd
import pytest

from akk2eng.pipeline.run import run_pipeline


def _minimal_test_csv(path: Path) -> None:
    """Write a tiny test.csv matching competition column names."""
    content = "id,text_id,line_start,line_end,transliteration\n1,a,1,1,ša-bi-im\n2,a,2,2,ki-ma\n"
    path.write_text(content, encoding="utf-8")


def test_pipeline_writes_submission(tmp_path: Path) -> None:
    test_csv = tmp_path / "test.csv"
    submission_csv = tmp_path / "submission.csv"
    _minimal_test_csv(test_csv)

    # Lexicon path loads train.csv for form→lexeme pairs; CI has no `data/train.csv` (gitignored).
    run_pipeline(test_csv, submission_csv, quiet=True, batch_size=2, use_lexicon=False)

    assert submission_csv.is_file()
    out = pd.read_csv(submission_csv)
    assert list(out.columns) == ["id", "translation"]
    assert len(out) == 2
    assert out["translation"].astype(str).str.len().gt(0).all()

    run_pipeline(test_csv, submission_csv, quiet=True, batch_size=2, use_lexicon=False)
    out2 = pd.read_csv(submission_csv)
    assert out["translation"].tolist() == out2["translation"].tolist()


def test_load_csv_missing_file(tmp_path: Path) -> None:
    from akk2eng.data.loader import load_csv

    missing = tmp_path / "nope.csv"
    with pytest.raises(FileNotFoundError):
        load_csv(missing)
