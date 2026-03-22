"""M06 selection — synthetic fixtures only (CI-safe)."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import pytest

from akk2eng.data.loader import load_csv
from akk2eng.data.selection import (
    SelectionError,
    materialize_strict_dominant_weighted,
    run_m06_selection,
    select_policy_a,
)

FIX = Path(__file__).resolve().parent / "fixtures" / "m06_selection"


def test_tiebreak_resplit_before_prefix() -> None:
    df = load_csv(FIX / "augmented_tiebreak.csv")
    conf = pd.to_numeric(df["augmentation_confidence"], errors="coerce")
    sel = select_policy_a(df, conf)
    assert sel.fallback_triggered  # <16 rows at >=0.9
    assert sel.selected_expansion_count == 1
    assert sel.cap_used == 1  # floor(0.5*2)
    exp_idx = sel.expansion_positions[0]
    assert df.iloc[exp_idx]["augmentation_type"] == "expanded_english_resplit"


def test_relaxed_excluded_from_expansion() -> None:
    df = load_csv(FIX / "augmented_relaxed.csv")
    conf = pd.to_numeric(df["augmentation_confidence"], errors="coerce")
    sel = select_policy_a(df, conf)
    assert sel.excluded_relaxed_count == 1
    assert sel.strict_count == 2
    assert sel.selected_expansion_count == 1


def test_cap_enforcement() -> None:
    df = load_csv(FIX / "augmented_cap.csv")
    conf = pd.to_numeric(df["augmentation_confidence"], errors="coerce")
    sel = select_policy_a(df, conf)
    assert sel.strict_count == 3
    assert sel.cap_used == 1
    assert sel.selected_expansion_count == 1


def test_fallback_threshold() -> None:
    df = load_csv(FIX / "augmented_fallback.csv")
    conf = pd.to_numeric(df["augmentation_confidence"], errors="coerce")
    sel = select_policy_a(df, conf)
    assert sel.fallback_triggered is True
    assert sel.threshold_used == 0.80
    assert sel.cap_used == 1
    assert sel.selected_expansion_count == 1


def test_fail_closed_bad_confidence() -> None:
    df = load_csv(FIX / "augmented_bad_conf.csv")
    conf = pd.to_numeric(df["augmentation_confidence"], errors="coerce")
    with pytest.raises(SelectionError, match="non-numeric"):
        select_policy_a(df, conf)


def test_weighted_materialization_row_counts() -> None:
    df = load_csv(FIX / "augmented_tiebreak.csv")
    conf = pd.to_numeric(df["augmentation_confidence"], errors="coerce")
    sel = select_policy_a(df, conf)
    strict_df = df.iloc[sel.strict_positions].copy()
    exp_df = df.iloc[sel.expansion_positions].copy()
    for part in (strict_df, exp_df):
        part.drop(columns=[c for c in part.columns if str(c).startswith("_")], inplace=True)
    w = materialize_strict_dominant_weighted(strict_df, exp_df, strict_repeat=2)
    assert len(w) == 2 * len(strict_df) + len(exp_df)


def test_run_m06_end_to_end_deterministic(tmp_path: Path) -> None:
    src = FIX / "augmented_tiebreak.csv"
    d1 = tmp_path / "o1"
    d2 = tmp_path / "o2"
    a1, r1, b1, rb1 = run_m06_selection(src, d1, FIX / "dev_clean.csv")
    a2, r2, b2, rb2 = run_m06_selection(src, d2, FIX / "dev_clean.csv")
    assert a1.read_bytes() == a2.read_bytes()
    assert r1.read_text(encoding="utf-8") == r2.read_text(encoding="utf-8")
    assert b1 is not None and b2 is not None
    assert b1.read_bytes() == b2.read_bytes()


def test_dev_overlap_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(SelectionError, match="Dev overlap"):
        run_m06_selection(
            FIX / "augmented_overlap.csv",
            tmp_path / "out",
            FIX / "dev_overlap.csv",
        )


def test_policy_a_csv_row_order(tmp_path: Path) -> None:
    run_m06_selection(FIX / "augmented_tiebreak.csv", tmp_path, FIX / "dev_clean.csv")
    out = tmp_path / "strict_plus_highconf_cap50.csv"
    with out.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3
    assert rows[0]["augmentation_type"] == "direct_aid_strict"
    assert rows[1]["augmentation_type"] == "direct_aid_strict"
    assert rows[2]["augmentation_type"] == "expanded_english_resplit"
