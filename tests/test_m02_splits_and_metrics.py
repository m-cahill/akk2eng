"""M02-A: deterministic splits and metric helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from akk2eng.config import SEED
from akk2eng.data.loader import load_csv
from akk2eng.data.splits import ensure_split_csvs, train_dev_split
from akk2eng.pipeline.eval import compute_translation_metrics

FIXTURE_TRAIN = Path(__file__).resolve().parent / "fixtures" / "tiny_train.csv"


def test_train_dev_split_counts_and_determinism() -> None:
    df = load_csv(FIXTURE_TRAIN)
    train_a, dev_a = train_dev_split(df, seed=SEED, dev_fraction=0.1)
    train_b, dev_b = train_dev_split(df, seed=SEED, dev_fraction=0.1)
    assert len(dev_a) == 1
    assert len(train_a) == 11
    pd.testing.assert_frame_equal(dev_a.reset_index(drop=True), dev_b.reset_index(drop=True))
    pd.testing.assert_frame_equal(train_a.reset_index(drop=True), train_b.reset_index(drop=True))


def test_ensure_split_csvs_idempotent(tmp_path: Path) -> None:
    src = tmp_path / "train.csv"
    src.write_bytes(FIXTURE_TRAIN.read_bytes())
    tr = tmp_path / "train_split.csv"
    dv = tmp_path / "dev_split.csv"
    ensure_split_csvs(src, tr, dv, seed=SEED, dev_fraction=0.1, force=False)
    m1 = tr.stat().st_mtime_ns
    d1 = load_csv(dv)
    ensure_split_csvs(src, tr, dv, seed=SEED, dev_fraction=0.1, force=False)
    m2 = tr.stat().st_mtime_ns
    d2 = load_csv(dv)
    assert m1 == m2
    pd.testing.assert_frame_equal(d1, d2)


def test_ensure_split_csvs_force_regenerates(tmp_path: Path) -> None:
    src = tmp_path / "train.csv"
    src.write_bytes(FIXTURE_TRAIN.read_bytes())
    tr = tmp_path / "train_split.csv"
    dv = tmp_path / "dev_split.csv"
    ensure_split_csvs(src, tr, dv, seed=SEED, dev_fraction=0.1, force=False)
    m1 = tr.stat().st_mtime_ns
    ensure_split_csvs(src, tr, dv, seed=SEED, dev_fraction=0.1, force=True)
    m2 = tr.stat().st_mtime_ns
    assert m2 >= m1


def test_compute_translation_metrics_length_mismatch() -> None:
    with pytest.raises(ValueError, match="Length mismatch"):
        compute_translation_metrics(["a"], ["a", "b"])


def test_compute_translation_metrics_identical_strings() -> None:
    # BLEU needs enough n-gram overlap; very short strings can score 0.0.
    s = [
        "the cat sat on the mat .",
        "there are enough words here for n gram overlap .",
    ]
    m = compute_translation_metrics(s, s)
    assert m["chrf"] == pytest.approx(100.0, abs=0.01)
    assert m["bleu"] == pytest.approx(100.0, abs=0.05)
