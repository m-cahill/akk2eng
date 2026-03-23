"""M04: dev / aligned oare_id overlap check."""

from __future__ import annotations

from pathlib import Path

import pytest

from akk2eng.data.alignment import verify_aligned_no_dev_oare_overlap


def test_verify_overlap_passes_when_disjoint(tmp_path: Path) -> None:
    aligned = tmp_path / "a.csv"
    dev = tmp_path / "d.csv"
    aligned.write_text(
        "sentence_id,oare_id,transliteration,translation,line_start,line_end,"
        "alignment_method,alignment_confidence\n"
        "x,d1,aa,One.,1,1,exact,1\n",
        encoding="utf-8",
    )
    dev.write_text(
        "oare_id,transliteration,translation\nd2,bb,Two.\n",
        encoding="utf-8",
    )
    r = verify_aligned_no_dev_oare_overlap(aligned, dev)
    assert r["passes"] is True
    assert r["n_overlap_oare_ids"] == 0


def test_verify_overlap_fails_when_shared_oare_id(tmp_path: Path) -> None:
    aligned = tmp_path / "a.csv"
    dev = tmp_path / "d.csv"
    aligned.write_text(
        "sentence_id,oare_id,transliteration,translation,line_start,line_end,"
        "alignment_method,alignment_confidence\n"
        "x,SHARED,aa,One.,1,1,exact,1\n",
        encoding="utf-8",
    )
    dev.write_text(
        "oare_id,transliteration,translation\nSHARED,bb,Two.\n",
        encoding="utf-8",
    )
    r = verify_aligned_no_dev_oare_overlap(aligned, dev)
    assert r["passes"] is False
    assert r["n_overlap_oare_ids"] == 1
    assert "SHARED" in r["overlap_oare_ids_sample"]


def test_verify_missing_column_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    bad.write_text("foo,bar\n1,2\n", encoding="utf-8")
    dev = tmp_path / "d.csv"
    dev.write_text("oare_id,transliteration,translation\nx,a,b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="aligned CSV missing"):
        verify_aligned_no_dev_oare_overlap(bad, dev)
