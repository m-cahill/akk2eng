"""M03: transliteration normalization (deterministic, stdlib-only)."""

from __future__ import annotations

from akk2eng.data.normalize import MIN_DUP_TOKEN_LEN, normalize_transliteration


def test_empty_and_whitespace_only() -> None:
    assert normalize_transliteration("") == ""
    assert normalize_transliteration("   \n\t  ") == ""


def test_preserves_casing_v2() -> None:
    """v2 must not lowercase — training distribution uses mixed case logograms."""
    assert normalize_transliteration("KÀ-NI-IA") == "KÀ-NI-IA"


def test_hyphens_preserved() -> None:
    assert normalize_transliteration("kà-ni-ia") == "kà-ni-ia"


def test_whitespace_collapsed() -> None:
    assert normalize_transliteration("  a   b  ") == "a b"


def test_nbsp_mapped_to_space() -> None:
    assert normalize_transliteration("a\u00a0b") == "a b"


def test_removes_unicode_ellipsis_and_low_quote() -> None:
    assert normalize_transliteration("x\u2026y") == "xy"
    assert normalize_transliteration("x\u201ey") == "xy"


def test_removes_zero_width_and_bom() -> None:
    assert normalize_transliteration("ab\u200bcd") == "abcd"
    assert normalize_transliteration("\ufeffhello") == "hello"


def test_collapse_immediate_duplicates_when_len_ge_threshold() -> None:
    assert normalize_transliteration("kar kar") == "kar"
    assert normalize_transliteration("kar kar kar") == "kar"


def test_no_collapse_when_token_too_short() -> None:
    assert normalize_transliteration("a a") == "a a"
    assert normalize_transliteration("ab ab") == "ab ab"
    assert MIN_DUP_TOKEN_LEN == 3


def test_non_adjacent_duplicates_unchanged() -> None:
    assert normalize_transliteration("kar x kar") == "kar x kar"
