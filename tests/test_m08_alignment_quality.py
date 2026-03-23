"""M08 alignment-quality v2 — synthetic fixtures only (CPU-safe)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from akk2eng.data.alignment_quality import (
    M06_CANONICAL_WINNER_SENTENCE_IDS,
    AlignmentQualityError,
    apply_delimiter_resplit,
    build_alignment_quality_v2,
    validate_m06_baseline_winners,
)

FIX = Path(__file__).resolve().parent / "fixtures" / "m08_alignment_quality"


def _m06_baseline(tmp_path: Path) -> Path:
    p = tmp_path / "m06_baseline.csv"
    p.write_text((FIX / "baseline_m06_min.csv").read_text(encoding="utf-8"), encoding="utf-8")
    return p


def test_apply_delimiter_resplit_semicolon_ok() -> None:
    parts = ["one two three four; five six seven eight."]
    out, reason = apply_delimiter_resplit(parts, ";", expected_total=2)
    assert reason == "ok"
    assert out is not None
    assert len(out) == 2
    assert out[0] == "one two three four"
    assert out[1] == "five six seven eight."


def test_apply_delimiter_resplit_colon_ok() -> None:
    parts = ["aaa bbb ccc ddd: eee fff ggg hhh."]
    out, reason = apply_delimiter_resplit(parts, ":", expected_total=2)
    assert out is not None
    assert len(out) == 2


def test_apply_delimiter_resplit_not_plus_one_segment() -> None:
    parts = ["a;b", "c;d"]
    out, reason = apply_delimiter_resplit(parts, ";", expected_total=2)
    assert out is None
    assert reason == "not_exactly_one_segment_contains_delimiter"


def test_apply_delimiter_resplit_empty_clause() -> None:
    parts = ["; right side ok ok ok ok"]
    out, reason = apply_delimiter_resplit(parts, ";", expected_total=2)
    assert out is None
    assert reason == "empty_clause_after_split"


def test_validate_m06_baseline_winners_ok(tmp_path: Path) -> None:
    validate_m06_baseline_winners(_m06_baseline(tmp_path))


def test_validate_m06_baseline_winners_fail_wrong_ids(tmp_path: Path) -> None:
    p = tmp_path / "bad.csv"
    p.write_text(
        "sentence_id,oare_id,transliteration,translation,line_start,line_end,"
        "alignment_method,alignment_confidence,augmentation_type,"
        "augmentation_confidence,source_row_id\n"
        "wrong:id:1,x,tt tt tt tt,word word word word word,1,1,exact_count,1.0,"
        "expanded_english_resplit,0.95,x\n"
        "wrong:id:2,y,uu uu uu uu,phrase phrase phrase phrase phrase,1,1,exact_count,1.0,"
        "expanded_english_resplit,0.95,y\n",
        encoding="utf-8",
    )
    with pytest.raises(AlignmentQualityError, match="canonical"):
        validate_m06_baseline_winners(p)


def test_semicolon_repair_success(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    rep = build_alignment_quality_v2(
        FIX / "train_semicolon.csv",
        FIX / "dev_ok.csv",
        FIX / "sentences_semicolon.csv",
        out_dir,
        _m06_baseline(tmp_path),
        strict_baseline_csv=None,
    )
    assert rep["recovered_row_count"] == 2
    assert rep["strict_row_count"] == 0
    assert rep["counts_by_alignment_quality_type"]["repair_semicolon_resplit"] == 2
    csv_path = out_dir / "aligned_train_sentences_quality_v2_split.csv"
    text = csv_path.read_text(encoding="utf-8")
    h1 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    build_alignment_quality_v2(
        FIX / "train_semicolon.csv",
        FIX / "dev_ok.csv",
        FIX / "sentences_semicolon.csv",
        out_dir,
        _m06_baseline(tmp_path),
        strict_baseline_csv=None,
    )
    h2 = hashlib.sha256(csv_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    assert h1 == h2


def test_colon_repair_success(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    rep = build_alignment_quality_v2(
        FIX / "train_colon.csv",
        FIX / "dev_ok.csv",
        FIX / "sentences_colon.csv",
        out_dir,
        _m06_baseline(tmp_path),
        strict_baseline_csv=None,
    )
    assert rep["recovered_row_count"] == 2
    assert rep["counts_by_alignment_quality_type"]["repair_colon_resplit"] == 2


def test_ineligible_count_not_plus_one(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    rep = build_alignment_quality_v2(
        FIX / "train_not_plus_one.csv",
        FIX / "dev_ok.csv",
        FIX / "sentences_three.csv",
        out_dir,
        _m06_baseline(tmp_path),
        strict_baseline_csv=None,
    )
    assert rep["recovered_row_count"] == 0
    assert int(rep["repair_rejection_counts"].get("ineligible_count_not_plus_one", 0)) >= 1


def test_empty_clause_rejection(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    rep = build_alignment_quality_v2(
        FIX / "train_empty_clause.csv",
        FIX / "dev_ok.csv",
        FIX / "sentences_empty_clause.csv",
        out_dir,
        _m06_baseline(tmp_path),
        strict_baseline_csv=None,
    )
    assert rep["recovered_row_count"] == 0
    keys = [k for k in rep["repair_rejection_counts"] if "empty_clause" in k]
    assert keys


def test_gap_marker_rejection(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    rep = build_alignment_quality_v2(
        FIX / "train_gap.csv",
        FIX / "dev_ok.csv",
        FIX / "sentences_gap.csv",
        out_dir,
        _m06_baseline(tmp_path),
        strict_baseline_csv=None,
    )
    assert rep["recovered_row_count"] == 0
    rej = rep["repair_rejection_counts"]
    assert any("doc_rejected:translation_gap_or_broken" in k for k in rej)


def test_short_translation_rejection(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    rep = build_alignment_quality_v2(
        FIX / "train_short.csv",
        FIX / "dev_ok.csv",
        FIX / "sentences_short.csv",
        out_dir,
        _m06_baseline(tmp_path),
        strict_baseline_csv=None,
    )
    assert rep["recovered_row_count"] == 0


def test_duplicate_normalized_across_recovered_docs(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    rep = build_alignment_quality_v2(
        FIX / "train_cross_dup.csv",
        FIX / "dev_ok.csv",
        FIX / "sentences_cross_dup.csv",
        out_dir,
        _m06_baseline(tmp_path),
        strict_baseline_csv=None,
    )
    assert rep["recovered_row_count"] == 2
    assert rep["recovered_document_count"] == 1


def test_fail_closed_missing_train_column(tmp_path: Path) -> None:
    bad_train = tmp_path / "bad_train.csv"
    bad_train.write_text("oare_id,transliteration\nx,a b\n", encoding="utf-8")
    with pytest.raises(AlignmentQualityError, match="translation"):
        build_alignment_quality_v2(
            bad_train,
            FIX / "dev_ok.csv",
            FIX / "sentences_semicolon.csv",
            tmp_path / "out",
            _m06_baseline(tmp_path),
            strict_baseline_csv=None,
        )


def test_fail_closed_dev_overlap(tmp_path: Path) -> None:
    with pytest.raises(AlignmentQualityError, match="dev overlap"):
        build_alignment_quality_v2(
            FIX / "train_overlap.csv",
            FIX / "dev_overlap.csv",
            FIX / "sentences_overlap.csv",
            tmp_path / "out",
            _m06_baseline(tmp_path),
            strict_baseline_csv=None,
        )


def test_candidate_b_union_m06_winners(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    build_alignment_quality_v2(
        FIX / "train_semicolon.csv",
        FIX / "dev_ok.csv",
        FIX / "sentences_semicolon.csv",
        out_dir,
        _m06_baseline(tmp_path),
        strict_baseline_csv=None,
    )
    b = (out_dir / "aligned_train_sentences_quality_v2_plus_m06.csv").read_text(encoding="utf-8")
    for sid in M06_CANONICAL_WINNER_SENTENCE_IDS:
        assert sid in b
    rep_path = out_dir / "alignment_quality_v2_plus_m06_report.json"
    rep_b = json.loads(rep_path.read_text(encoding="utf-8"))
    assert rep_b["m06_winners_union_appended_count"] == 2


def test_canonical_winner_ids_fixture_matches_locked_set() -> None:
    """Guardrail: fixture baseline must stay aligned with M07 closeout identities."""
    text = (FIX / "baseline_m06_min.csv").read_text(encoding="utf-8")
    for sid in M06_CANONICAL_WINNER_SENTENCE_IDS:
        assert sid in text
