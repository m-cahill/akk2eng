"""M04: deterministic sentence alignment from official train + OARE sentence aid.

Uses ``Sentences_Oare_FirstWord_LinNum.csv`` (``text_uuid`` joins ``train.oare_id``).
High-precision policy: skip documents on missing anchors, ambiguous first-word hits,
or unresolvable English/Akkadian sentence count mismatches (beyond one bounded fallback).
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_OARE_ID, COL_TRANSLATION, COL_TRANSLITERATION

# Aid file column names (official bundle)
AID_TEXT_UUID = "text_uuid"
AID_SENTENCE_UUID = "sentence_uuid"
AID_SENTENCE_OBJ = "sentence_obj_in_text"
AID_TRANSLATION = "translation"
AID_FIRST_WORD_TRANSCRIPTION = "first_word_transcription"
AID_FIRST_WORD_SPELLING = "first_word_spelling"
AID_FIRST_WORD_OBJ = "first_word_obj_in_text"
AID_LINE_NUMBER = "line_number"
AID_SIDE = "side"
AID_COLUMN = "column"

OUTPUT_COLS = [
    "sentence_id",
    COL_OARE_ID,
    COL_TRANSLITERATION,
    COL_TRANSLATION,
    "line_start",
    "line_end",
    "alignment_method",
    "alignment_confidence",
]

_SUBSCRIPT_DIGITS = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def parse_line_number_string(raw: str) -> tuple[int, int]:
    """Parse competition-style line labels: ``1``, ``1'``, ``1''``, etc.

    Returns ``(base_line, prime_count)`` where ``prime_count`` is the number of
    trailing ASCII apostrophe characters.
    """
    s = raw.strip()
    if not s:
        msg = "empty line number string"
        raise ValueError(msg)
    prime = 0
    while s.endswith("'"):
        prime += 1
        s = s[:-1]
    if not s.isdigit():
        msg = f"unsupported line number string: {raw!r}"
        raise ValueError(msg)
    return int(s), prime


def parse_line_number_value(value: Any) -> tuple[int, int]:
    """Parse a line number from the aid CSV (float with fractional prime encoding) or string."""
    if isinstance(value, str):
        return parse_line_number_string(value)
    if value is None or (isinstance(value, float) and math.isnan(value)):
        msg = "line number is null/NaN"
        raise ValueError(msg)
    val = float(value)
    base = int(math.floor(val + 1e-9))
    frac = round(val - base, 2)
    if abs(frac) < 1e-6:
        return base, 0
    cent = int(round(frac * 100))
    if cent < 0 or cent > 10:
        msg = f"unsupported fractional line encoding: {value!r}"
        raise ValueError(msg)
    return base, cent


def line_tuple_to_label(base: int, prime: int) -> str:
    """Render ``(base, prime_count)`` as ``1``, ``1'``, ``1''``, …"""
    return str(base) + ("'" * prime)


def _normalize_token_for_match(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s))
    s = s.translate(_SUBSCRIPT_DIGITS)
    s = s.lower()
    s = re.sub(r"[\s\-_.]+", "", s)
    return s


def _tokenize_transliteration(text: str) -> list[str]:
    return [t for t in str(text).split() if t]


def split_english_conservative(text: str) -> list[str]:
    """High-precision English sentence split (deterministic, low recall accepted)."""
    text = (text or "").strip()
    if not text:
        return []
    # Split after sentence-ending punctuation when followed by space and likely new sentence.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(0-9])", text)
    out = [p.strip() for p in parts if p.strip()]
    return out if out else [text]


def _first_word_patterns(row: pd.Series) -> list[str]:
    raw_t = row.get(AID_FIRST_WORD_TRANSCRIPTION, "")
    raw_s = row.get(AID_FIRST_WORD_SPELLING, "")
    cands: list[str] = []
    if isinstance(raw_t, str) and raw_t.strip():
        cands.append(raw_t.strip())
    if isinstance(raw_s, str) and raw_s.strip():
        cands.append(raw_s.strip())
    # De-duplicate preserving order
    seen: set[str] = set()
    uniq: list[str] = []
    for c in cands:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


def _find_next_anchor(
    tokens: list[str],
    patterns: list[str],
    start_idx: int,
) -> int | None:
    if not patterns:
        return None
    keys = [_normalize_token_for_match(p) for p in patterns]
    for i in range(start_idx, len(tokens)):
        tkey = _normalize_token_for_match(tokens[i])
        for pk in keys:
            if not pk:
                continue
            if tkey == pk or tkey.startswith(pk) or pk.startswith(tkey):
                return i
    return None


@dataclass
class _DocWork:
    oare_id: str
    transliteration: str
    translation: str
    rows: pd.DataFrame


@dataclass
class AlignmentReport:
    docs_processed: int = 0
    docs_aligned: int = 0
    sentence_pairs: int = 0
    method_counts: Counter[str] = field(default_factory=Counter)
    skip_reasons: Counter[str] = field(default_factory=Counter)
    aligned_csv_sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "docs_processed": self.docs_processed,
            "docs_aligned": self.docs_aligned,
            "sentence_pairs": self.sentence_pairs,
            "method_counts": dict(self.method_counts),
            "skip_reasons": dict(self.skip_reasons),
            "aligned_csv_sha256": self.aligned_csv_sha256,
        }


def _sort_sentence_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Deterministic ordering within a document."""
    work = df.copy()
    line_bases: list[int] = []
    line_primes: list[int] = []
    for _, row in work.iterrows():
        b, p = parse_line_number_value(row[AID_LINE_NUMBER])
        line_bases.append(b)
        line_primes.append(p)
    work["_lb"] = line_bases
    work["_lp"] = line_primes
    work = work.sort_values(
        by=[AID_SIDE, AID_COLUMN, "_lb", "_lp", AID_SENTENCE_OBJ],
        kind="mergesort",
    ).reset_index(drop=True)
    return work.drop(columns=["_lb", "_lp"])


def _extract_akk_spans(
    tokens: list[str],
    sorted_rows: pd.DataFrame,
) -> tuple[list[str] | None, str | None]:
    spans: list[tuple[int, int]] = []
    cursor = 0
    for _, row in sorted_rows.iterrows():
        pats = _first_word_patterns(row)
        if not pats:
            return None, "empty_first_word_patterns"
        hit = _find_next_anchor(tokens, pats, cursor)
        if hit is None:
            return None, "first_word_not_found"
        spans.append((hit, hit))
        cursor = hit + 1
    if not spans:
        return None, "no_spans"
    # Boundaries: sentence i uses tokens[starts[i] : starts[i + 1]].
    boundaries = [s[0] for s in spans]
    boundaries.append(len(tokens))
    texts: list[str] = []
    for i in range(len(spans)):
        chunk = tokens[boundaries[i] : boundaries[i + 1]]
        if not chunk:
            return None, "empty_akk_span"
        texts.append(" ".join(chunk))
    return texts, None


def _pair_eng_to_akk(
    akk_spans: list[str],
    eng_parts: list[str],
) -> tuple[list[tuple[str, str]] | None, str, float]:
    na, ne = len(akk_spans), len(eng_parts)
    if na == ne:
        return list(zip(akk_spans, eng_parts, strict=True)), "exact_count", 1.0
    if na == 0:
        return None, "skip_empty_akk", 0.0

    # One split: need one more English segment than we have parts -> split one segment at first ". "
    if na == ne + 1:
        for i, seg in enumerate(eng_parts):
            if ". " not in seg:
                continue
            left, right = seg.split(". ", 1)
            left = left.strip() + "."
            right = right.strip()
            merged = eng_parts[:i] + [left, right] + eng_parts[i + 1 :]
            if len(merged) == na:
                return list(zip(akk_spans, merged, strict=True)), "split_english", 0.85
        return None, "split_english_failed", 0.0

    # One merge: need one fewer English segment
    if na == ne - 1:
        best_k: int | None = None
        for k in range(ne - 1):
            merged = eng_parts[:k] + [f"{eng_parts[k]} {eng_parts[k + 1]}"] + eng_parts[k + 2 :]
            if len(merged) == na:
                best_k = k if best_k is None else min(best_k, k)
        if best_k is not None:
            merged = (
                eng_parts[:best_k]
                + [f"{eng_parts[best_k]} {eng_parts[best_k + 1]}"]
                + eng_parts[best_k + 2 :]
            )
            return list(zip(akk_spans, merged, strict=True)), "merge_english", 0.85
        return None, "merge_english_failed", 0.0

    return None, "count_mismatch", 0.0


def align_document_sentences_strict(
    oare_id: str,
    transliteration: str,
    translation: str,
    sorted_aid: pd.DataFrame,
) -> tuple[list[dict[str, Any]] | None, str, float]:
    """M04/M05: strict per-document alignment (public wrapper for tooling/tests)."""
    return _rows_for_doc(oare_id, transliteration, translation, sorted_aid)


def tokenize_transliteration_text(text: str) -> list[str]:
    """Tokenize competition transliteration for anchor search (M05 expansion)."""
    return _tokenize_transliteration(text)


def _rows_for_doc(
    oare_id: str,
    transliteration: str,
    translation: str,
    sorted_aid: pd.DataFrame,
) -> tuple[list[dict[str, Any]], str, float] | tuple[None, str, float]:
    tokens = _tokenize_transliteration(transliteration)
    akk_spans, err = _extract_akk_spans(tokens, sorted_aid)
    if err:
        return None, err, 0.0
    eng_parts = split_english_conservative(translation)
    paired, method, conf = _pair_eng_to_akk(akk_spans, eng_parts)
    if paired is None:
        return None, method, conf

    out_rows: list[dict[str, Any]] = []
    for (_, row), (akk, eng) in zip(sorted_aid.iterrows(), paired, strict=True):
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
                "alignment_method": method,
                "alignment_confidence": conf,
            }
        )
    return out_rows, method, conf


def build_aligned_training_csv(
    train_csv: Path,
    sentences_aid_csv: Path,
    output_csv: Path,
    report_json: Path,
) -> AlignmentReport:
    """Build ``aligned_train_sentences.csv`` and ``alignment_report.json``."""
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

    report = AlignmentReport()
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

        built, reason, _conf = _rows_for_doc(
            oid,
            str(trow[COL_TRANSLITERATION]),
            str(trow[COL_TRANSLATION]),
            sorted_sub,
        )
        if built is None:
            report.skip_reasons[reason] += 1
            continue
        report.docs_aligned += 1
        report.method_counts[built[0]["alignment_method"]] += 1
        report.sentence_pairs += len(built)
        all_rows.extend(built)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    _write_aligned_csv(output_csv, all_rows)
    report.aligned_csv_sha256 = _sha256_file(output_csv)

    report_json.parent.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    try:
        payload["aligned_csv_path"] = str(output_csv.relative_to(Path.cwd()))
    except ValueError:
        payload["aligned_csv_path"] = output_csv.as_posix()
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["alignment_report_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    report_json.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return report


def _write_aligned_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=OUTPUT_COLS, lineterminator="\n")
        w.writeheader()
        for r in sorted(rows, key=lambda x: x["sentence_id"]):
            w.writerow({k: r.get(k, "") for k in OUTPUT_COLS})


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_baseline_alignment_audit(
    train_csv: Path,
    sentences_aid_csv: Path,
    output_json: Path,
) -> dict[str, Any]:
    """Phase A: schema/coverage stats (no alignment logic)."""
    train = load_csv(train_csv)
    aid = load_csv(sentences_aid_csv)
    n_train = len(train)
    aid_ids = set(aid[AID_TEXT_UUID].astype(str))
    train_ids = set(train[COL_OARE_ID].astype(str))
    covered = train_ids & aid_ids
    line_vals = aid[AID_LINE_NUMBER]
    fractional = [float(x) for x in line_vals if pd.notna(x) and float(x) != int(float(x))]

    audit: dict[str, Any] = {
        "train_row_count": int(n_train),
        "unique_train_oare_ids": int(train[COL_OARE_ID].nunique()),
        "unique_aid_text_uuids": int(len(aid_ids)),
        "train_docs_with_aid_rows": int(len(covered)),
        "train_docs_without_aid_rows": int(len(train_ids - aid_ids)),
        "aid_line_number_dtype": str(line_vals.dtype),
        "fractional_line_number_count": int(len(fractional)),
        "sample_fractional_line_numbers": sorted(set(round(x, 2) for x in fractional))[:25],
        "sentences_aid_columns": list(aid.columns),
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return audit


def verify_aligned_no_dev_oare_overlap(
    aligned_csv: Path,
    dev_split_csv: Path,
) -> dict[str, Any]:
    """Return overlap stats between ``oare_id`` in aligned output and dev split.

    For leak-safe M04 training, ``passes`` must be True (empty intersection).
    """
    aligned = load_csv(aligned_csv)
    dev = load_csv(dev_split_csv)
    if COL_OARE_ID not in aligned.columns:
        msg = f"aligned CSV missing {COL_OARE_ID!r}"
        raise ValueError(msg)
    if COL_OARE_ID not in dev.columns:
        msg = f"dev split CSV missing {COL_OARE_ID!r}"
        raise ValueError(msg)
    a_ids = set(aligned[COL_OARE_ID].astype(str).str.strip())
    d_ids = set(dev[COL_OARE_ID].astype(str).str.strip())
    inter = a_ids & d_ids
    sample = sorted(inter)[:50]
    return {
        "aligned_csv": str(aligned_csv.as_posix()),
        "dev_split_csv": str(dev_split_csv.as_posix()),
        "n_unique_oare_in_aligned": len(a_ids),
        "n_unique_oare_in_dev": len(d_ids),
        "n_overlap_oare_ids": len(inter),
        "overlap_oare_ids_sample": sample,
        "passes": len(inter) == 0,
    }
