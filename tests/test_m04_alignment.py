"""M04 alignment engine tests (synthetic fixtures only)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from akk2eng.data.alignment import (
    build_aligned_training_csv,
    line_tuple_to_label,
    parse_line_number_string,
    parse_line_number_value,
    split_english_conservative,
    write_baseline_alignment_audit,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "m04_alignment"


def test_parse_line_number_string_primes() -> None:
    assert parse_line_number_string("1") == (1, 0)
    assert parse_line_number_string("1'") == (1, 1)
    assert parse_line_number_string("1''") == (1, 2)


def test_parse_line_number_float_encoding() -> None:
    assert parse_line_number_value(1.0) == (1, 0)
    assert parse_line_number_value(2.01) == (2, 1)
    assert parse_line_number_value(3.02) == (3, 2)


def test_line_tuple_to_label_roundtrip_style() -> None:
    assert line_tuple_to_label(5, 0) == "5"
    assert line_tuple_to_label(5, 2) == "5''"


def test_split_english_conservative_basic() -> None:
    parts = split_english_conservative("One. Two.")
    assert parts == ["One.", "Two."]


def test_deterministic_sort_sentence_rows(tmp_path: Path) -> None:
    """Later line_number must sort after earlier within same side/column."""
    train = tmp_path / "train.csv"
    aid = tmp_path / "aid.csv"
    train.write_text(
        "oare_id,transliteration,translation\ndoc,x y z w,Alpha. Beta.\n",
        encoding="utf-8",
    )
    aid.write_text(
        "display_name,text_uuid,sentence_uuid,sentence_obj_in_text,translation,"
        "first_word_transcription,first_word_spelling,first_word_number,"
        "first_word_obj_in_text,line_number,side,column\n"
        "t,doc,s2,2,E2.,z,,1,2,2.0,1,1\n"
        "t,doc,s1,1,E1.,x,,1,1,1.0,1,1\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.csv"
    rep = tmp_path / "rep.json"
    build_aligned_training_csv(train, aid, out, rep)
    import csv

    with out.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["transliteration"].startswith("x")
    assert rows[1]["transliteration"].startswith("z")


def test_e2e_exact_fixture(tmp_path: Path) -> None:
    train = FIXTURES / "train_exact.csv"
    aid = FIXTURES / "sentences_exact.csv"
    out_csv = tmp_path / "aligned.csv"
    out_rep = tmp_path / "report.json"
    r = build_aligned_training_csv(train, aid, out_csv, out_rep)
    assert r.docs_aligned == 1
    assert r.sentence_pairs == 2
    assert r.method_counts["exact_count"] == 1
    text = out_csv.read_text(encoding="utf-8")
    h1 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    build_aligned_training_csv(train, aid, out_csv, out_rep)
    h2 = hashlib.sha256(out_csv.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    assert h1 == h2
    rep = json.loads(out_rep.read_text(encoding="utf-8"))
    assert rep["aligned_csv_sha256"] == h1
    assert rep["sentence_pairs"] == 2
    assert "alignment_report_sha256" in rep


def test_e2e_merge_english(tmp_path: Path) -> None:
    r = build_aligned_training_csv(
        FIXTURES / "train_merge.csv",
        FIXTURES / "sentences_merge.csv",
        tmp_path / "a.csv",
        tmp_path / "r.json",
    )
    assert r.docs_aligned == 1
    assert r.sentence_pairs == 2
    assert r.method_counts["merge_english"] == 1


def test_e2e_split_english(tmp_path: Path) -> None:
    r = build_aligned_training_csv(
        FIXTURES / "train_split.csv",
        FIXTURES / "sentences_split.csv",
        tmp_path / "a.csv",
        tmp_path / "r.json",
    )
    assert r.docs_aligned == 1
    assert r.sentence_pairs == 3
    assert r.method_counts["split_english"] == 1


def test_skip_first_word_not_found(tmp_path: Path) -> None:
    r = build_aligned_training_csv(
        FIXTURES / "train_skip.csv",
        FIXTURES / "sentences_skip.csv",
        tmp_path / "a.csv",
        tmp_path / "r.json",
    )
    assert r.docs_aligned == 0
    assert r.skip_reasons["first_word_not_found"] >= 1


def test_baseline_audit_writes_json(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.json"
    aud = write_baseline_alignment_audit(
        FIXTURES / "train_exact.csv",
        FIXTURES / "sentences_exact.csv",
        audit_path,
    )
    assert aud["train_row_count"] == 1
    assert audit_path.is_file()


def test_stable_sentence_ids(tmp_path: Path) -> None:
    out_csv = tmp_path / "aligned.csv"
    build_aligned_training_csv(
        FIXTURES / "train_exact.csv",
        FIXTURES / "sentences_exact.csv",
        out_csv,
        tmp_path / "r.json",
    )
    import csv

    with out_csv.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    ids = {row["sentence_id"] for row in rows}
    assert ids == {"doc-exact:su-a", "doc-exact:su-b"}
