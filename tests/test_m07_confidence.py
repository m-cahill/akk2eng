"""M07 confidence_v2 — synthetic fixtures only (CPU / CI-safe)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from akk2eng.data.confidence import (
    ConfidenceError,
    build_scored_expansion_pool,
    compute_confidence_v2,
    digit_consistency_adjustment,
    length_adequacy_adjustment,
    load_m06_expansion_sentence_ids,
    run_m07_confidence_build,
    source_gap_penalty,
    translation_has_exclusion_markers,
    type_prior,
)
from akk2eng.data.loader import load_csv

FIX = Path(__file__).resolve().parent / "fixtures" / "m07_confidence"


def test_type_prior_resplit_and_prefix() -> None:
    assert type_prior("expanded_english_resplit") == 0.05
    assert type_prior("expanded_partial_prefix") == 0.0


def test_digit_consistency_match_and_one_sided() -> None:
    assert digit_consistency_adjustment("3 GÚ 8 ma-na", "3 talents 8 minas") == 0.05
    assert digit_consistency_adjustment("no digits here x", "one 1 token") == -0.05
    assert digit_consistency_adjustment("a b", "c d") == 0.0


def test_length_adequacy_band() -> None:
    # src_len=10 → low=max(4,1)=4, high=13; tgt 5 → +0.05
    assert length_adequacy_adjustment(10, 5) == 0.05
    assert length_adequacy_adjustment(10, 20) == -0.05


def test_source_gap_penalty() -> None:
    assert source_gap_penalty("a <gap> b") == -0.05
    assert source_gap_penalty("broken seal") == -0.05
    assert source_gap_penalty("intact text") == 0.0


def test_translation_markers() -> None:
    assert translation_has_exclusion_markers("see <gap> here") is True
    assert translation_has_exclusion_markers("BROKEN line") is True
    assert translation_has_exclusion_markers("fine text four tok") is False


def test_compute_confidence_v2_clip() -> None:
    # extreme positive components still clip to 1.0
    v = compute_confidence_v2(
        augmentation_confidence=0.99,
        augmentation_type="expanded_english_resplit",
        transliteration="x " * 10,
        translation="y " * 5,
    )
    assert v == 1.0


def test_build_pool_drops_duplicate_normalized_translation() -> None:
    df = load_csv(FIX / "augmented_duplicate_translation.csv")
    scored, audit = build_scored_expansion_pool(df)
    assert audit["count_expansion_non_relaxed_initial"] == 3
    assert audit["count_after_dedupe_duplicate_normalized_translation"] == 2
    assert len(scored) == 2


def test_load_m06_expansion_sentence_ids() -> None:
    ids = load_m06_expansion_sentence_ids(FIX / "baseline_m06_two_winners.csv")
    assert ids == ["sw1", "sw2"]


def test_run_m07_deterministic(tmp_path: Path) -> None:
    o1 = tmp_path / "o1"
    o2 = tmp_path / "o2"
    p1 = run_m07_confidence_build(
        FIX / "augmented_ok.csv",
        FIX / "baseline_m06_two_winners.csv",
        o1,
        FIX / "dev_clean.csv",
    )
    p2 = run_m07_confidence_build(
        FIX / "augmented_ok.csv",
        FIX / "baseline_m06_two_winners.csv",
        o2,
        FIX / "dev_clean.csv",
    )
    assert p1["cap6_csv"].read_bytes() == p2["cap6_csv"].read_bytes()
    assert p1["main_report"].read_text(encoding="utf-8") == p2["main_report"].read_text(
        encoding="utf-8"
    )


def test_cap6_includes_m06_winners_and_shortfall_metadata(tmp_path: Path) -> None:
    out = run_m07_confidence_build(
        FIX / "augmented_ok.csv",
        FIX / "baseline_m06_two_winners.csv",
        tmp_path,
        FIX / "dev_clean.csv",
        cap6=6,
        cap10=10,
    )
    rep = json.loads(out["cap6_report"].read_text(encoding="utf-8"))
    assert rep["strict_row_count"] == 2
    assert rep["cap_metadata"]["expansion_rows_selected"] == 4
    assert rep["cap_metadata"]["shortfall_vs_cap"] == 2
    assert rep["dev_overlap_oare_ids"] == 0
    assert rep["m06_winners_preserved_in_selection"] is True


def test_winner_not_in_top_cap_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfidenceError, match="not in top-2"):
        run_m07_confidence_build(
            FIX / "augmented_winner_not_in_cap.csv",
            FIX / "baseline_m06_two_winners.csv",
            tmp_path,
            FIX / "dev_clean.csv",
            cap6=2,
            cap10=6,
        )


def test_winner_excluded_by_hard_filter_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfidenceError, match="excluded by confidence_v2"):
        run_m07_confidence_build(
            FIX / "augmented_winner_filtered.csv",
            FIX / "baseline_winner_filtered.csv",
            tmp_path,
            FIX / "dev_clean.csv",
        )


def test_dev_overlap_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(ConfidenceError, match="Dev overlap"):
        run_m07_confidence_build(
            FIX / "augmented_overlap.csv",
            FIX / "baseline_overlap.csv",
            tmp_path,
            FIX / "dev_overlap.csv",
        )


def test_missing_required_column_raises() -> None:
    df = load_csv(FIX / "augmented_ok.csv").drop(columns=["sentence_id"])
    with pytest.raises(ConfidenceError, match="missing required column"):
        build_scored_expansion_pool(df)


def test_duplicate_pool_preserves_baseline_winners(tmp_path: Path) -> None:
    run_m07_confidence_build(
        FIX / "augmented_duplicate_translation.csv",
        FIX / "baseline_dup_winners.csv",
        tmp_path,
        FIX / "dev_clean.csv",
    )


def test_relaxed_expansion_excluded_from_pool() -> None:
    df = load_csv(FIX / "augmented_ok.csv")
    row = df.iloc[0].to_dict()
    row["sentence_id"] = "rel1"
    row["augmentation_type"] = "expanded_partial_prefix_relaxed"
    row["augmentation_confidence"] = 1.0
    df2 = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    _, audit = build_scored_expansion_pool(df2)
    assert audit["count_expansion_non_relaxed_initial"] == 4
