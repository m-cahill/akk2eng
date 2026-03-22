"""M05 alignment expansion — synthetic fixtures only."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from akk2eng.data.alignment import split_english_conservative, verify_aligned_no_dev_oare_overlap
from akk2eng.data.augmentation import (
    AUGMENTED_OUTPUT_COLS,
    build_augmented_training_csv,
    split_english_extended,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "m05_augmentation"
M04_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "m04_alignment"


def test_split_english_extended_semicolon() -> None:
    assert split_english_conservative("First; Second") == ["First; Second"]
    assert split_english_extended("First; Second") == ["First", "Second"]


def test_augmented_schema_and_relaxed_expansion(tmp_path: Path) -> None:
    train = FIXTURES / "train_relaxed.csv"
    aid = FIXTURES / "sentences_relaxed.csv"
    out_csv = tmp_path / "aug.csv"
    out_rep = tmp_path / "rep.json"
    rep = build_augmented_training_csv(train, aid, out_csv, out_rep)
    assert rep.docs_expanded == 1
    assert rep.docs_strict == 0
    assert rep.rows_expanded == 2
    assert rep.augmentation_type_counts["expanded_relaxed_first_word"] == 2

    with out_csv.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    for row in rows:
        for col in AUGMENTED_OUTPUT_COLS:
            assert col in row
        assert row["augmentation_type"] == "expanded_relaxed_first_word"
        assert 0 < float(row["augmentation_confidence"]) <= 1.0
        assert row["source_row_id"] == "doc-rel"


def test_english_resplit_path(tmp_path: Path) -> None:
    train = FIXTURES / "train_semicolon.csv"
    aid = FIXTURES / "sentences_semicolon.csv"
    out_csv = tmp_path / "aug.csv"
    out_rep = tmp_path / "rep.json"
    rep = build_augmented_training_csv(train, aid, out_csv, out_rep)
    assert rep.docs_expanded == 1
    assert rep.augmentation_type_counts["expanded_english_resplit"] == 2


def test_deterministic_output_hash(tmp_path: Path) -> None:
    train = FIXTURES / "train_relaxed.csv"
    aid = FIXTURES / "sentences_relaxed.csv"
    out1 = tmp_path / "a.csv"
    out2 = tmp_path / "b.csv"
    rep1 = tmp_path / "r1.json"
    rep2 = tmp_path / "r2.json"
    r1 = build_augmented_training_csv(train, aid, out1, rep1)
    r2 = build_augmented_training_csv(train, aid, out2, rep2)
    assert out1.read_bytes() == out2.read_bytes()
    assert r1.augmented_csv_sha256 == r2.augmented_csv_sha256
    j1 = json.loads(rep1.read_text(encoding="utf-8"))
    j2 = json.loads(rep2.read_text(encoding="utf-8"))
    assert j1["augmented_csv_sha256"] == j2["augmented_csv_sha256"]


def test_direct_aid_strict_tagging(tmp_path: Path) -> None:
    train = M04_FIXTURES / "train_exact.csv"
    aid = M04_FIXTURES / "sentences_exact.csv"
    out_csv = tmp_path / "aug.csv"
    out_rep = tmp_path / "rep.json"
    rep = build_augmented_training_csv(train, aid, out_csv, out_rep)
    assert rep.docs_strict == 1
    assert rep.docs_expanded == 0
    assert rep.augmentation_type_counts["direct_aid_strict"] == 2


def test_dev_overlap_detected(tmp_path: Path) -> None:
    train = FIXTURES / "train_split.csv"
    aid = FIXTURES / "sentences_overlap.csv"
    out_csv = tmp_path / "aug.csv"
    out_rep = tmp_path / "rep.json"
    build_augmented_training_csv(train, aid, out_csv, out_rep)
    dev = FIXTURES / "dev_split.csv"
    check = verify_aligned_no_dev_oare_overlap(out_csv, dev)
    assert check["passes"] is False
    assert check["n_overlap_oare_ids"] >= 1
