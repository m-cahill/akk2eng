"""M03: deterministic transliteration normalization (inference-time only).

**v2 (conservative, distribution-safe):** reduce surface noise **without** changing
token identity vs training (no NFKC, no case fold).

Applied in order:

1. Removal of a small set of **noise characters** (explicit codepoints; no regex)
2. **Whitespace** normalization (NBSP → space, collapse runs, trim)
3. Collapse **immediate duplicate tokens** when each token has length ≥ ``MIN_DUP_TOKEN_LEN``

Hyphens **are preserved** (syllable boundaries; training distribution).

**v1** (retired for default): also applied NFKC + lowercase — caused train/inference
mismatch (see ``docs/milestones/M03/M03_run1_normalization.md``).

This module must stay free of heavy dependencies (stdlib only).
"""

from __future__ import annotations

# Immediate duplicate collapse runs only when tokens are long enough to avoid
# removing repeated short grammatical / gloss particles (e.g. "a a").
MIN_DUP_TOKEN_LEN = 3

# Characters removed entirely (ord → delete). Extend only with explicit review.
_NOISE_ORDS: tuple[int, ...] = (
    0x2026,  # HORIZONTAL ELLIPSIS (…)
    0x201E,  # DOUBLE LOW-9 QUOTATION MARK („)
    0x200B,  # ZERO WIDTH SPACE
    0x200C,  # ZERO WIDTH NON-JOINER
    0x200D,  # ZERO WIDTH JOINER
    0xFEFF,  # BYTE ORDER MARK (when not stripped by loader)
    0x2060,  # WORD JOINER
)
_NOISE_DELETE = dict.fromkeys(_NOISE_ORDS)


def _remove_noise_chars(text: str) -> str:
    return text.translate(_NOISE_DELETE)


def _normalize_whitespace(text: str) -> str:
    """Map NBSP to ASCII space, then collapse all whitespace runs to single spaces."""
    t = text.replace("\u00a0", " ")
    return " ".join(t.split())


def _collapse_immediate_duplicate_tokens(text: str, *, min_len: int) -> str:
    """Drop consecutive identical tokens when token length >= min_len."""
    parts = text.split()
    if not parts:
        return ""
    out: list[str] = [parts[0]]
    for tok in parts[1:]:
        if tok == out[-1] and len(tok) >= min_len:
            continue
        out.append(tok)
    return " ".join(out)


def normalize_transliteration(text: str) -> str:
    """Return a deterministic, cleaned transliteration string for model input."""
    if not text:
        return ""
    t = _remove_noise_chars(text)
    t = _normalize_whitespace(t)
    t = _collapse_immediate_duplicate_tokens(t, min_len=MIN_DUP_TOKEN_LEN)
    return t
