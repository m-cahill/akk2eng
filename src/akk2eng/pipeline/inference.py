"""T5 baseline inference for submission rows."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from akk2eng.config import (
    DEFAULT_LEXICON_CSV,
    DEFAULT_MODEL_DIR,
    DEFAULT_TRAIN_CSV,
    LEXICON_MAX_ENTRIES,
    USE_LEXICON,
    USE_NORMALIZATION,
)
from akk2eng.data.normalize import normalize_transliteration
from akk2eng.data.schema import COL_TRANSLITERATION
from akk2eng.lexicon.postprocess import apply_lexicon_postprocess, build_lexicon_pairs
from akk2eng.model.model import T5BaselineTranslator


@lru_cache(maxsize=4)
def _lexicon_pairs_cached(
    train_csv_resolved: str,
    lexicon_csv_resolved: str,
    max_entries: int,
) -> tuple[tuple[str, str], ...]:
    pairs = build_lexicon_pairs(
        Path(train_csv_resolved),
        Path(lexicon_csv_resolved),
        max_entries=max_entries,
    )
    return tuple(pairs)


def resolved_lexicon_pairs(
    *,
    train_csv: Path | None = None,
    lexicon_csv: Path | None = None,
    lexicon_max_entries: int | None = None,
) -> tuple[tuple[str, str], ...]:
    """Return cached ``(form, lexeme)`` tuples (same mapping as :func:`run_inference` uses)."""
    tcsv = DEFAULT_TRAIN_CSV if train_csv is None else train_csv
    lcsv = DEFAULT_LEXICON_CSV if lexicon_csv is None else lexicon_csv
    cap = LEXICON_MAX_ENTRIES if lexicon_max_entries is None else lexicon_max_entries
    return _lexicon_pairs_cached(str(Path(tcsv).resolve()), str(Path(lcsv).resolve()), int(cap))


def run_inference(
    df: pd.DataFrame,
    *,
    model_dir: Path | None = None,
    batch_size: int = 8,
    quiet: bool = False,
    debug_sample_n: int = 8,
    use_lexicon: bool | None = None,
    use_normalization: bool | None = None,
    train_csv: Path | None = None,
    lexicon_csv: Path | None = None,
    lexicon_max_entries: int | None = None,
) -> list[str]:
    """Translate each row's transliteration; print debug stats unless ``quiet``."""
    if COL_TRANSLITERATION not in df.columns:
        msg = f"DataFrame must contain column {COL_TRANSLITERATION!r}"
        raise ValueError(msg)

    mdir = DEFAULT_MODEL_DIR if model_dir is None else model_dir
    translator = T5BaselineTranslator(model_dir=mdir)
    texts = df[COL_TRANSLITERATION].fillna("").astype(str).tolist()
    do_norm = USE_NORMALIZATION if use_normalization is None else use_normalization
    if do_norm:
        texts = [normalize_transliteration(t) for t in texts]
    preds, tok_lens = translator.translate(texts, batch_size=batch_size)

    do_lex = USE_LEXICON if use_lexicon is None else use_lexicon
    if do_lex:
        tcsv = DEFAULT_TRAIN_CSV if train_csv is None else train_csv
        lcsv = DEFAULT_LEXICON_CSV if lexicon_csv is None else lexicon_csv
        cap = LEXICON_MAX_ENTRIES if lexicon_max_entries is None else lexicon_max_entries
        pairs = list(
            _lexicon_pairs_cached(
                str(Path(tcsv).resolve()),
                str(Path(lcsv).resolve()),
                int(cap),
            ),
        )
        preds = [apply_lexicon_postprocess(p, pairs) for p in preds]

    if not quiet:
        avg_len = sum(tok_lens) / len(tok_lens) if tok_lens else 0.0
        print("Inference: fine-tuned checkpoint =", translator.loaded_from_finetuned_dir)
        print("Average output token length (incl. pads stripped in decode):", round(avg_len, 2))
        n = min(debug_sample_n, len(texts))
        print("Sample predictions (transliteration -> translation):")
        for i in range(n):
            s = texts[i][:200] + ("…" if len(texts[i]) > 200 else "")
            p = preds[i][:200] + ("…" if len(preds[i]) > 200 else "")
            print(f"  [{i}] {s!r} -> {p!r}")

    return preds
