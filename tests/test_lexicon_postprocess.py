"""Tests for M02-D lexicon post-processing (predictions only)."""

from __future__ import annotations

from pathlib import Path

import pytest

from akk2eng.lexicon.postprocess import apply_lexicon_postprocess, build_lexicon_pairs


def test_apply_lexicon_full_token_only() -> None:
    pairs = [("KÙ.BABBAR", "kaspu"), ("AND", "x")]
    assert apply_lexicon_postprocess("pay KÙ.BABBAR now", pairs) == "pay kaspu now"
    # Do not touch substring inside English word
    assert apply_lexicon_postprocess("KÙ.BABBARland", pairs) == "KÙ.BABBARland"


def test_apply_lexicon_longest_first_order() -> None:
    # Caller must pass longest form first; module documents sort in build_lexicon_pairs
    pairs = [("KÙ.BABBAR-pí-šu", "a"), ("KÙ.BABBAR", "b")]
    assert apply_lexicon_postprocess("X KÙ.BABBAR-pí-šu Y", pairs) == "X a Y"


def test_build_lexicon_filters_unambiguous_and_train(tmp_path: Path) -> None:
    train = tmp_path / "train.csv"
    train.write_text(
        "oare_id,transliteration,translation\n"
        "1,WORDX other,ref\n"
        "2,AMBIG other,ref\n"
        "3,OKK other,ref\n",
        encoding="utf-8",
    )
    lex = tmp_path / "lex.csv"
    lex.write_text(
        "type,form,norm,lexeme\n"
        "w,WORDX,n,lemma1\n"
        "w,AMBIG,n,one\n"
        "w,AMBIG,n,two\n"
        "w,NOTIN,n,lemma2\n"
        "w,SH,n,short\n"
        "w,TWO WORDS,n,badlex\n"
        'w,OKK,n,"two words"\n',
        encoding="utf-8",
    )
    pairs = build_lexicon_pairs(train, lex, max_entries=50, min_form_len=3)
    forms = {f for f, _ in pairs}
    assert "WORDX" in forms
    assert "AMBIG" not in forms
    assert "NOTIN" not in forms
    assert "SH" not in forms
    assert "TWO WORDS" not in forms
    assert "OKK" not in forms  # lexeme contains whitespace → rejected


def test_build_lexicon_requires_columns(tmp_path: Path) -> None:
    train = tmp_path / "train.csv"
    train.write_text("oare_id,transliteration,translation\n1,X, y\n", encoding="utf-8")
    bad = tmp_path / "bad.csv"
    bad.write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="form"):
        build_lexicon_pairs(train, bad)
