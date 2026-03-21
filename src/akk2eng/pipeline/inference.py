"""T5 baseline inference for submission rows."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from akk2eng.config import DEFAULT_MODEL_DIR
from akk2eng.data.schema import COL_TRANSLITERATION
from akk2eng.model.model import T5BaselineTranslator


def run_inference(
    df: pd.DataFrame,
    *,
    model_dir: Path | None = None,
    batch_size: int = 8,
    quiet: bool = False,
    debug_sample_n: int = 8,
) -> list[str]:
    """Translate each row's transliteration; print debug stats unless ``quiet``."""
    if COL_TRANSLITERATION not in df.columns:
        msg = f"DataFrame must contain column {COL_TRANSLITERATION!r}"
        raise ValueError(msg)

    mdir = DEFAULT_MODEL_DIR if model_dir is None else model_dir
    translator = T5BaselineTranslator(model_dir=mdir)
    texts = df[COL_TRANSLITERATION].fillna("").astype(str).tolist()
    preds, tok_lens = translator.translate(texts, batch_size=batch_size)

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
