"""M04: combine document-level train.csv with sentence-aligned rows for mixed fine-tuning."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_OARE_ID, COL_TRANSLATION, COL_TRANSLITERATION

# Aligned CSV may include this column for deterministic ordering
COL_SENTENCE_ID = "sentence_id"
COL_ROW_ORIGIN = "_row_origin"


def build_mixed_train_csv(
    document_train_csv: Path,
    aligned_train_csv: Path,
    output_csv: Path,
    *,
    stats_json: Path | None = None,
) -> dict[str, Any]:
    """Concatenate full ``train.csv`` then sentence-level aligned rows.

    Output columns: ``oare_id``, ``transliteration``, ``translation``, ``_row_origin``
    (``document`` | ``aligned_sentence``). Training uses only the two text columns.

    * Document rows keep CSV row order.
    * Aligned rows are sorted by ``sentence_id`` when present, else by
      ``(oare_id, transliteration, translation)`` for byte-stable output.
    """
    doc = load_csv(document_train_csv)
    ali = load_csv(aligned_train_csv)
    for col in (COL_OARE_ID, COL_TRANSLITERATION, COL_TRANSLATION):
        if col not in doc.columns:
            msg = f"document train CSV missing column {col!r}"
            raise ValueError(msg)
    for col in (COL_OARE_ID, COL_TRANSLITERATION, COL_TRANSLATION):
        if col not in ali.columns:
            msg = f"aligned train CSV missing column {col!r}"
            raise ValueError(msg)

    doc_part = doc[[COL_OARE_ID, COL_TRANSLITERATION, COL_TRANSLATION]].copy()
    doc_part = doc_part.dropna(subset=[COL_TRANSLITERATION, COL_TRANSLATION])
    doc_part[COL_ROW_ORIGIN] = "document"

    ali_part = ali[[COL_OARE_ID, COL_TRANSLITERATION, COL_TRANSLATION]].copy()
    if COL_SENTENCE_ID in ali.columns:
        ali_part[COL_SENTENCE_ID] = ali[COL_SENTENCE_ID].astype(str)
        ali_part = ali_part.sort_values(
            by=[COL_SENTENCE_ID],
            kind="mergesort",
        ).reset_index(drop=True)
        ali_part = ali_part.drop(columns=[COL_SENTENCE_ID])
    else:
        ali_part = ali_part.sort_values(
            by=[COL_OARE_ID, COL_TRANSLITERATION, COL_TRANSLATION],
            kind="mergesort",
        ).reset_index(drop=True)
    ali_part = ali_part.dropna(subset=[COL_TRANSLITERATION, COL_TRANSLATION])
    ali_part[COL_ROW_ORIGIN] = "aligned_sentence"

    mixed = pd.concat([doc_part, ali_part], ignore_index=True)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    mixed.to_csv(output_csv, index=False, lineterminator="\n")

    n_doc = int(len(doc_part))
    n_ali = int(len(ali_part))
    n_tot = n_doc + n_ali
    stats: dict[str, Any] = {
        "document_train_csv": str(document_train_csv.as_posix()),
        "aligned_train_csv": str(aligned_train_csv.as_posix()),
        "mixed_train_csv": str(output_csv.as_posix()),
        "document_rows": n_doc,
        "aligned_rows": n_ali,
        "total_rows": n_tot,
        "aligned_to_document_ratio": (n_ali / n_doc) if n_doc else None,
        "aligned_fraction_of_total": (n_ali / n_tot) if n_tot else 0.0,
        "document_fraction_of_total": (n_doc / n_tot) if n_tot else 0.0,
    }
    if stats_json is not None:
        stats_json.parent.mkdir(parents=True, exist_ok=True)
        stats_json.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return stats
