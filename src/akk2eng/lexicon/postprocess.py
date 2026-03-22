"""Build a small form→lexeme map from eBL CSV + train.csv; apply to predictions only."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_TRANSLITERATION


def _token_boundary_pattern(form: str) -> re.Pattern[str]:
    """Match ``form`` as a full token (not a substring of a longer word-like span).

    Uses negative lookbehind/ahead on ``\\w`` (Unicode-aware in Python 3) so we do not
    rely on ``\\b`` alone around punctuation such as ``.`` in ``KÙ.BABBAR``.
    """
    escaped = re.escape(form)
    return re.compile(rf"(?<![\w]){escaped}(?![\w])", flags=re.UNICODE)


def _is_safe_single_token_lexeme(lexeme: str) -> bool:
    """Reject empty / multi-word English-ish glosses (spaces = multiple tokens)."""
    s = lexeme.strip()
    if not s:
        return False
    # Hyphenated lemmas (e.g. Abā-aḫu) stay single-token; reject internal whitespace.
    if any(ch.isspace() for ch in s):
        return False
    return True


def _train_whitespace_tokens(texts: list[str]) -> set[str]:
    """All whitespace-delimited chunks (logograms + syllabic runs appear as train tokens)."""
    toks: set[str] = set()
    for t in texts:
        for w in t.split():
            if w:
                toks.add(w)
    return toks


def form_appears_in_transliterations(
    form: str,
    texts: list[str],
    *,
    train_tokens: set[str] | None = None,
) -> bool:
    """True if ``form`` occurs at least once as a full token in any transliteration.

    Single-token forms (no internal whitespace) use a precomputed token set for speed.
    Multi-word ``form`` values use a boundary-safe regex scan (rarer in the lexicon).
    """
    if len(form.strip()) < 3:
        return False
    if not any(ch.isspace() for ch in form):
        ts = _train_whitespace_tokens(texts) if train_tokens is None else train_tokens
        return form in ts
    pat = _token_boundary_pattern(form)
    return any(pat.search(t) for t in texts)


def _train_token_counts(texts: list[str]) -> Counter[str]:
    c: Counter[str] = Counter()
    for t in texts:
        for w in t.split():
            if w:
                c[w] += 1
    return c


def _train_frequency(
    form: str,
    texts: list[str],
    *,
    token_counts: Counter[str],
) -> int:
    """How often ``form`` hits train data (Counter for simple forms; regex for multi-word)."""
    if len(form.strip()) < 3:
        return 0
    if not any(ch.isspace() for ch in form):
        return int(token_counts[form])
    pat = _token_boundary_pattern(form)
    return sum(len(pat.findall(t)) for t in texts)


def build_lexicon_pairs(
    train_csv: Path,
    lexicon_csv: Path,
    *,
    max_entries: int = 400,
    min_form_len: int = 3,
) -> list[tuple[str, str]]:
    """Return ``(form, lexeme)`` pairs sorted for safe replacement (longest ``form`` first).

    Selection (Option B):
    - ``form`` must appear in training transliterations (token-boundary match).
    - ``form`` length >= ``min_form_len`` (characters).
    - ``lexeme`` non-empty, no whitespace (single surface chunk).
    - Unambiguous: one lexeme per form in the CSV (else form is dropped).
    - At most ``max_entries`` forms, preferring higher train frequency then longer forms.
    """
    train_df = load_csv(Path(train_csv))
    if COL_TRANSLITERATION not in train_df.columns:
        msg = f"{train_csv} must contain column {COL_TRANSLITERATION!r}"
        raise ValueError(msg)
    texts = train_df[COL_TRANSLITERATION].fillna("").astype(str).tolist()
    train_tokens = _train_whitespace_tokens(texts)
    token_counts = _train_token_counts(texts)

    # form -> set of distinct lexemes (after strip)
    by_form: dict[str, set[str]] = defaultdict(set)
    with Path(lexicon_csv).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fn = reader.fieldnames
        if fn is None or "form" not in fn or "lexeme" not in fn:
            msg = f"{lexicon_csv} must have 'form' and 'lexeme' columns"
            raise ValueError(msg)
        for row in reader:
            form = (row.get("form") or "").strip()
            lexeme = (row.get("lexeme") or "").strip()
            if len(form) < min_form_len:
                continue
            if not _is_safe_single_token_lexeme(lexeme):
                continue
            by_form[form].add(lexeme)

    unambiguous: list[tuple[str, str]] = []
    for form, lexs in by_form.items():
        if len(lexs) != 1:
            continue
        if not form_appears_in_transliterations(form, texts, train_tokens=train_tokens):
            continue
        (lexeme,) = tuple(lexs)
        unambiguous.append((form, lexeme))

    freq_map = {
        form: _train_frequency(form, texts, token_counts=token_counts) for form, _ in unambiguous
    }

    # Cap: prefer frequent-in-train, then longer forms (more specific).
    unambiguous.sort(key=lambda fl: (-freq_map[fl[0]], -len(fl[0]), fl[0]))
    capped = unambiguous[:max_entries]
    # Replacement order: longest form first to reduce partial-shadowing.
    capped.sort(key=lambda fl: (-len(fl[0]), fl[0]))
    return capped


def apply_lexicon_postprocess(text: str, pairs: list[tuple[str, str]]) -> str:
    """Replace leaked Akkadian in ``text`` using ``pairs`` (caller sorts longest keys first)."""
    out = text
    for form, lexeme in pairs:
        pat = _token_boundary_pattern(form)
        out = pat.sub(lexeme, out)
    return out
