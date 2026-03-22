"""M05: split-safe expansion of sentence-aligned training pairs (Method 1 only).

Builds on M04 strict alignment using the same official aid file, adding **precision-biased**
recall paths (relaxed anchors, English `;` resplit, partial prefixes). No dev data, no new
external corpora.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from akk2eng.data.alignment import (
    AID_COLUMN,
    AID_LINE_NUMBER,
    AID_SENTENCE_OBJ,
    AID_SENTENCE_UUID,
    AID_SIDE,
    AID_TEXT_UUID,
    AID_TRANSLATION,
    COL_OARE_ID,
    COL_TRANSLATION,
    COL_TRANSLITERATION,
    OUTPUT_COLS,
    _extract_akk_spans,
    _find_next_anchor,
    _first_word_patterns,
    _normalize_token_for_match,
    _pair_eng_to_akk,
    _sort_sentence_rows,
    align_document_sentences_strict,
    line_tuple_to_label,
    parse_line_number_value,
    split_english_conservative,
    tokenize_transliteration_text,
)
from akk2eng.data.loader import load_csv

AUGMENT_EXTRA_COLS = ["augmentation_type", "augmentation_confidence", "source_row_id"]
AUGMENTED_OUTPUT_COLS = list(OUTPUT_COLS) + AUGMENT_EXTRA_COLS

_RELAX_LOOKAHEAD = 14


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _levenshtein_distance_leq1(a: str, b: str) -> bool:
    """True if a and b are equal or single edit apart (insert/delete/substitute)."""
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    i = j = 0
    edits = 0
    la, lb = len(a), len(b)
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1
            j += 1
        elif edits:
            return False
        else:
            edits = 1
            if la == lb:
                i += 1
                j += 1
            elif la > lb:
                i += 1
            else:
                j += 1
    tail = (la - i) + (lb - j)
    return edits + tail <= 1


def _find_next_anchor_relaxed(
    tokens: list[str],
    patterns: list[str],
    start_idx: int,
    *,
    max_lookahead: int = _RELAX_LOOKAHEAD,
) -> int | None:
    """Bounded relaxed first-word search; returns None if zero or multiple hits in window."""
    hit_strict = _find_next_anchor(tokens, patterns, start_idx)
    if hit_strict is not None:
        return hit_strict

    keys = [_normalize_token_for_match(p) for p in patterns if p]
    if not keys:
        return None

    end = min(len(tokens), start_idx + max_lookahead)
    matched_indices: list[int] = []
    for i in range(start_idx, end):
        tkey = _normalize_token_for_match(tokens[i])
        if not tkey:
            continue
        for pk in keys:
            if not pk:
                continue
            ok = False
            if tkey == pk or tkey.startswith(pk) or pk.startswith(tkey):
                ok = True
            elif len(pk) >= 3 and len(tkey) >= 3 and (pk in tkey or tkey in pk):
                ok = True
            elif len(pk) >= 3 and len(tkey) >= 3 and _levenshtein_distance_leq1(pk, tkey):
                ok = True
            if ok:
                matched_indices.append(i)
                break

    uniq = sorted(set(matched_indices))
    if len(uniq) != 1:
        return None
    return uniq[0]


def _extract_akk_spans_relaxed(
    tokens: list[str],
    sorted_rows: pd.DataFrame,
) -> tuple[list[str] | None, str | None]:
    """Like M04 ``_extract_akk_spans`` but uses :func:`_find_next_anchor_relaxed`."""
    spans: list[tuple[int, int]] = []
    cursor = 0
    for _, row in sorted_rows.iterrows():
        pats = _first_word_patterns(row)
        if not pats:
            return None, "empty_first_word_patterns"
        hit = _find_next_anchor_relaxed(tokens, pats, cursor)
        if hit is None:
            return None, "first_word_not_found_relaxed"
        spans.append((hit, hit))
        cursor = hit + 1
    if not spans:
        return None, "no_spans"
    boundaries = [s[0] for s in spans]
    boundaries.append(len(tokens))
    texts: list[str] = []
    for i in range(len(spans)):
        chunk = tokens[boundaries[i] : boundaries[i + 1]]
        if not chunk:
            return None, "empty_akk_span"
        texts.append(" ".join(chunk))
    return texts, None


def split_english_extended(text: str) -> list[str]:
    """Deterministic extra split on ``;`` when conservative split yields a single segment."""
    conservative = split_english_conservative(text)
    if len(conservative) != 1:
        return conservative
    chunk = conservative[0]
    if ";" not in chunk:
        return conservative
    segs = [s.strip() for s in chunk.split(";") if s.strip()]
    if len(segs) <= 1:
        return conservative
    return segs


def _emit_rows(
    oare_id: str,
    sorted_sub: pd.DataFrame,
    paired: list[tuple[str, str]],
    alignment_method: str,
    alignment_confidence: float,
    augmentation_type: str,
    augmentation_confidence: float,
    source_row_id: str,
) -> list[dict[str, Any]]:
    out_rows: list[dict[str, Any]] = []
    for (_, row), (akk, eng) in zip(sorted_sub.iterrows(), paired, strict=True):
        b, p = parse_line_number_value(row[AID_LINE_NUMBER])
        label = line_tuple_to_label(b, p)
        sid = f"{oare_id}:{row[AID_SENTENCE_UUID]}"
        out_rows.append(
            {
                "sentence_id": sid,
                COL_OARE_ID: oare_id,
                COL_TRANSLITERATION: akk,
                COL_TRANSLATION: eng,
                "line_start": label,
                "line_end": label,
                "alignment_method": alignment_method,
                "alignment_confidence": alignment_confidence,
                "augmentation_type": augmentation_type,
                "augmentation_confidence": augmentation_confidence,
                "source_row_id": source_row_id,
            }
        )
    return out_rows


def _try_expand_document(
    oare_id: str,
    transliteration: str,
    translation: str,
    sorted_sub: pd.DataFrame,
) -> tuple[list[dict[str, Any]], str, float] | tuple[None, str, float]:
    """Apply expansion strategies after strict M04 alignment failed."""
    tokens = tokenize_transliteration_text(transliteration)
    eng_cons = split_english_conservative(translation)
    eng_ext = split_english_extended(translation)

    extract_relaxed: Callable[..., Any] = _extract_akk_spans_relaxed
    extract_strict: Callable[..., Any] = _extract_akk_spans

    attempts: list[tuple[str, Callable[..., Any], list[str], float]] = [
        ("expanded_relaxed_first_word", extract_relaxed, eng_cons, 0.92),
        ("expanded_english_resplit", extract_strict, eng_ext, 0.90),
        ("expanded_relaxed_english_resplit", extract_relaxed, eng_ext, 0.88),
    ]
    for aug_type, extract, eng_parts, scale in attempts:
        akk_spans, err = extract(tokens, sorted_sub)
        if err:
            continue
        paired, method, conf = _pair_eng_to_akk(akk_spans, eng_parts)
        if paired is None:
            continue
        aug_conf = min(1.0, float(conf) * scale)
        rows = _emit_rows(
            oare_id,
            sorted_sub,
            paired,
            method,
            float(conf),
            aug_type,
            aug_conf,
            oare_id,
        )
        return rows, aug_type, aug_conf

    n = len(sorted_sub)
    for k in range(n, 0, -1):
        subk = sorted_sub.iloc[:k].copy().reset_index(drop=True)
        for extract, is_relaxed in ((extract_strict, False), (extract_relaxed, True)):
            akk_spans, err = extract(tokens, subk)
            if err:
                continue
            for eng_parts in (eng_cons, eng_ext):
                paired, method, conf = _pair_eng_to_akk(akk_spans, eng_parts)
                if paired is None:
                    continue
                prefix = k / n
                aug_conf = min(1.0, float(conf) * prefix * 0.88)
                aug_type = (
                    "expanded_partial_prefix_relaxed" if is_relaxed else "expanded_partial_prefix"
                )
                rows = _emit_rows(
                    oare_id,
                    subk,
                    paired,
                    method,
                    float(conf),
                    aug_type,
                    aug_conf,
                    oare_id,
                )
                return rows, aug_type, aug_conf

    return None, "expand_exhausted", 0.0


def _tag_strict_rows(rows: list[dict[str, Any]], oare_id: str) -> list[dict[str, Any]]:
    tagged: list[dict[str, Any]] = []
    for r in rows:
        ac = float(r.get("alignment_confidence", 1.0))
        tagged.append(
            {
                **r,
                "augmentation_type": "direct_aid_strict",
                "augmentation_confidence": min(1.0, ac),
                "source_row_id": oare_id,
            }
        )
    return tagged


@dataclass
class AugmentationReport:
    docs_processed: int = 0
    docs_strict: int = 0
    docs_expanded: int = 0
    rows_strict: int = 0
    rows_expanded: int = 0
    augmentation_type_counts: Counter[str] = field(default_factory=Counter)
    skip_reasons: Counter[str] = field(default_factory=Counter)
    augmented_csv_sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "docs_processed": self.docs_processed,
            "docs_strict": self.docs_strict,
            "docs_expanded": self.docs_expanded,
            "rows_strict": self.rows_strict,
            "rows_expanded": self.rows_expanded,
            "augmentation_type_counts": dict(self.augmentation_type_counts),
            "skip_reasons": dict(self.skip_reasons),
            "augmented_csv_sha256": self.augmented_csv_sha256,
        }


def _write_augmented_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sorted_rows = sorted(rows, key=lambda x: x["sentence_id"])
    with path.open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=AUGMENTED_OUTPUT_COLS, lineterminator="\n")
        w.writeheader()
        for r in sorted_rows:
            w.writerow({k: r.get(k, "") for k in AUGMENTED_OUTPUT_COLS})


def build_augmented_training_csv(
    train_csv: Path,
    sentences_aid_csv: Path,
    output_csv: Path,
    report_json: Path,
) -> AugmentationReport:
    """Build augmented_train_sentences.csv + augmentation_report.json (M05).

    ``train_csv`` should be ``train_split.csv`` for leak-safe use; caller verifies dev overlap.
    """
    train = load_csv(train_csv)
    aid = load_csv(sentences_aid_csv)
    for col in (COL_OARE_ID, COL_TRANSLITERATION, COL_TRANSLATION):
        if col not in train.columns:
            msg = f"train CSV missing {col!r}"
            raise ValueError(msg)
    req = {
        AID_TEXT_UUID,
        AID_SENTENCE_UUID,
        AID_SENTENCE_OBJ,
        AID_TRANSLATION,
        AID_LINE_NUMBER,
        AID_SIDE,
        AID_COLUMN,
    }
    missing = req - set(aid.columns)
    if missing:
        msg = f"sentences aid CSV missing columns: {sorted(missing)}"
        raise ValueError(msg)

    train = train.dropna(subset=[COL_OARE_ID, COL_TRANSLITERATION, COL_TRANSLATION])
    train = train.copy()
    train[COL_OARE_ID] = train[COL_OARE_ID].astype(str).str.strip()
    aid = aid.copy()
    aid[AID_TEXT_UUID] = aid[AID_TEXT_UUID].astype(str).str.strip()
    by_text = aid.groupby(AID_TEXT_UUID, sort=False)

    report = AugmentationReport()
    all_rows: list[dict[str, Any]] = []

    for _, trow in train.iterrows():
        oid = str(trow[COL_OARE_ID])
        report.docs_processed += 1
        if oid not in by_text.groups:
            report.skip_reasons["no_aid_rows"] += 1
            continue
        sub = by_text.get_group(oid)
        if sub.empty:
            report.skip_reasons["empty_aid_group"] += 1
            continue
        try:
            sorted_sub = _sort_sentence_rows(sub)
        except (ValueError, TypeError):
            report.skip_reasons["line_number_parse_error"] += 1
            continue

        strict_rows, reason, _conf = align_document_sentences_strict(
            oid,
            str(trow[COL_TRANSLITERATION]),
            str(trow[COL_TRANSLATION]),
            sorted_sub,
        )
        if strict_rows is not None:
            tagged = _tag_strict_rows(strict_rows, oid)
            all_rows.extend(tagged)
            report.docs_strict += 1
            report.rows_strict += len(tagged)
            for tr in tagged:
                report.augmentation_type_counts[tr["augmentation_type"]] += 1
            continue

        expanded, _etype, _econf = _try_expand_document(
            oid,
            str(trow[COL_TRANSLITERATION]),
            str(trow[COL_TRANSLATION]),
            sorted_sub,
        )
        if expanded is None:
            # Strict failure reason (same taxonomy as M04); expansion did not recover pairs.
            report.skip_reasons[reason] += 1
            continue

        report.docs_expanded += 1
        report.rows_expanded += len(expanded)
        all_rows.extend(expanded)
        for er in expanded:
            report.augmentation_type_counts[er["augmentation_type"]] += 1

    _write_augmented_csv(output_csv, all_rows)
    report.augmented_csv_sha256 = _sha256_file(output_csv)

    train_sha = _sha256_file(train_csv) if train_csv.is_file() else ""
    aid_sha = _sha256_file(sentences_aid_csv) if sentences_aid_csv.is_file() else ""

    type_counts = dict(report.augmentation_type_counts)
    payload: dict[str, Any] = {
        **report.to_dict(),
        "original_rows": report.rows_strict,
        "augmented_rows": report.rows_expanded,
        "by_type": type_counts,
        "total_rows": len(all_rows),
        "train_csv_sha256": train_sha,
        "sentences_aid_csv_sha256": aid_sha,
        "train_csv": str(train_csv.as_posix()),
        "sentences_aid_csv": str(sentences_aid_csv.as_posix()),
        "augmented_csv_path": str(output_csv.as_posix()),
    }
    try:
        payload["augmented_csv_path_rel"] = str(output_csv.relative_to(Path.cwd()))
    except ValueError:
        payload["augmented_csv_path_rel"] = str(output_csv.as_posix())

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["augmentation_report_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return report


__all__ = [
    "AUGMENTED_OUTPUT_COLS",
    "AugmentationReport",
    "build_augmented_training_csv",
    "split_english_extended",
]
