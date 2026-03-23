"""M08: deterministic alignment-quality v2 — narrow English clause resplit repair.

Runs strict M04 alignment first, then attempts semicolon/colon resplits only for
documents with count mismatch ``na == ne + 1`` and successful first-word anchors.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from akk2eng.data.alignment import (
    AID_LINE_NUMBER,
    AID_SENTENCE_UUID,
    AID_TEXT_UUID,
    OUTPUT_COLS,
    _extract_akk_spans,
    _pair_eng_to_akk,
    _rows_for_doc,
    _sort_sentence_rows,
    _tokenize_transliteration,
    line_tuple_to_label,
    parse_line_number_value,
    split_english_conservative,
    verify_aligned_no_dev_oare_overlap,
)
from akk2eng.data.confidence import (
    load_m06_expansion_sentence_ids,
    normalize_translation_text,
    translation_has_exclusion_markers,
    translation_token_count,
)
from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_OARE_ID, COL_TRANSLATION, COL_TRANSLITERATION

# Locked M06 Policy A expansion identities (see M07_run1_confidence_builder.md).
M06_CANONICAL_WINNER_SENTENCE_IDS: frozenset[str] = frozenset(
    {
        "fc678a23-7011-4f9d-8957-ebf2c8dbbb43:2651ad13-ef9b-4941-a3e9-44d76a13b191",
        "fc678a23-7011-4f9d-8957-ebf2c8dbbb43:c7d5c7a2-793b-49e0-8991-c57d70981fcf",
    }
)

M08_EXTRA_COL = "alignment_quality_type"
M08_OUTPUT_COLS = [*OUTPUT_COLS, M08_EXTRA_COL]

TYPE_STRICT = "strict_existing"
TYPE_SEMICOLON = "repair_semicolon_resplit"
TYPE_COLON = "repair_colon_resplit"
TYPE_M06_UNION = "m06_winner_union"

REPAIR_ORDER: tuple[tuple[str, str], ...] = (
    (TYPE_SEMICOLON, ";"),
    (TYPE_COLON, ":"),
)


class AlignmentQualityError(Exception):
    """Fail-closed M08 alignment-quality pipeline."""


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_canonical_rows(rows: list[dict[str, Any]], core_keys: tuple[str, ...]) -> str:
    """Deterministic fingerprint over sorted sentence_id for leakage-safe comparisons."""
    slim = []
    for r in rows:
        slim.append({k: str(r.get(k, "")) for k in core_keys})
    slim.sort(key=lambda x: x["sentence_id"])
    payload = json.dumps(slim, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_m06_baseline_winners(baseline_csv: Path) -> None:
    """Fail-closed: baseline must contain exactly the two locked expansion rows."""
    found = frozenset(load_m06_expansion_sentence_ids(baseline_csv))
    if found != M06_CANONICAL_WINNER_SENTENCE_IDS:
        msg = (
            f"M06 baseline expansion sentence_id set {sorted(found)!r} != "
            f"canonical {sorted(M06_CANONICAL_WINNER_SENTENCE_IDS)!r}"
        )
        raise AlignmentQualityError(msg)


def apply_delimiter_resplit(
    eng_parts: list[str],
    delimiter: str,
    expected_total: int,
) -> tuple[list[str] | None, str]:
    """Split exactly one English segment on the first delimiter occurrence.

    Returns rebuilt segments or ``(None, reason)``.
    """
    if delimiter not in (";", ":"):
        msg = f"unsupported delimiter: {delimiter!r}"
        raise ValueError(msg)
    hits = [i for i, seg in enumerate(eng_parts) if delimiter in seg]
    if len(hits) != 1:
        return None, "not_exactly_one_segment_contains_delimiter"
    idx = hits[0]
    segment = eng_parts[idx]
    pos = segment.find(delimiter)
    assert pos >= 0
    left = segment[:pos].strip()
    right = segment[pos + 1 :].strip()
    if not left or not right:
        return None, "empty_clause_after_split"
    merged = eng_parts[:idx] + [left, right] + eng_parts[idx + 1 :]
    if len(merged) != expected_total:
        return None, "repaired_segment_count_mismatch"
    return merged, "ok"


def _materialize_rows(
    oare_id: str,
    sorted_aid: pd.DataFrame,
    paired: list[tuple[str, str]],
    method: str,
    conf: float,
    quality_type: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for (_, row), (akk, eng) in zip(sorted_aid.iterrows(), paired, strict=True):
        b, p = parse_line_number_value(row[AID_LINE_NUMBER])
        label = line_tuple_to_label(b, p)
        sid = f"{oare_id}:{row[AID_SENTENCE_UUID]}"
        out.append(
            {
                "sentence_id": sid,
                COL_OARE_ID: oare_id,
                COL_TRANSLITERATION: akk,
                COL_TRANSLATION: eng,
                "line_start": label,
                "line_end": label,
                "alignment_method": method,
                "alignment_confidence": conf,
                M08_EXTRA_COL: quality_type,
            }
        )
    return out


def _document_passes_filters(
    rows: list[dict[str, Any]],
    *,
    is_recovered: bool,
    recovered_norm_translations: set[str],
) -> tuple[bool, str]:
    """All rows must pass; recovered rows also check duplicate normalized translation."""
    pending_norms: list[str] = []
    for r in rows:
        akk = str(r[COL_TRANSLITERATION])
        eng = str(r[COL_TRANSLATION])
        if translation_has_exclusion_markers(eng):
            return False, "translation_gap_or_broken"
        if translation_token_count(eng) < 4:
            return False, "short_translation"
        if len(akk.split()) < 2:
            return False, "short_transliteration"
        if is_recovered:
            norm = normalize_translation_text(eng)
            if norm in recovered_norm_translations or norm in pending_norms:
                return False, "duplicate_normalized_translation_among_recovered"
            pending_norms.append(norm)
    for n in pending_norms:
        recovered_norm_translations.add(n)
    return True, ""


def _validate_train_aid_columns(train: pd.DataFrame, aid: pd.DataFrame) -> None:
    for col in (COL_OARE_ID, COL_TRANSLITERATION, COL_TRANSLATION):
        if col not in train.columns:
            msg = f"train CSV missing required column {col!r}"
            raise AlignmentQualityError(msg)
    req_aid = {
        AID_TEXT_UUID,
        AID_SENTENCE_UUID,
        AID_LINE_NUMBER,
    }
    missing = req_aid - set(aid.columns)
    if missing:
        msg = f"sentences aid CSV missing columns: {sorted(missing)}"
        raise AlignmentQualityError(msg)


def _write_m08_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=M08_OUTPUT_COLS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in M08_OUTPUT_COLS})


def _write_recovered_docs_csv(path: Path, docs: list[dict[str, Any]]) -> None:
    if not docs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("oare_id,repair_type,num_pairs,sentence_ids\n", encoding="utf-8")
        return
    cols = ["oare_id", "repair_type", "num_pairs", "sentence_ids"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for d in docs:
            w.writerow(d)


def build_alignment_quality_v2(
    train_split_csv: Path,
    dev_split_csv: Path,
    sentences_aid_csv: Path,
    output_dir: Path,
    m06_baseline_csv: Path,
    *,
    strict_baseline_csv: Path | None = None,
) -> dict[str, Any]:
    """Build Candidate A/B CSVs, reports, and recovered-docs audit."""
    validate_m06_baseline_winners(m06_baseline_csv)

    train = load_csv(train_split_csv)
    dev = load_csv(dev_split_csv)
    aid = load_csv(sentences_aid_csv)
    _validate_train_aid_columns(train, aid)

    if COL_OARE_ID not in dev.columns:
        msg = f"dev split CSV missing {COL_OARE_ID!r}"
        raise AlignmentQualityError(msg)

    train = train.dropna(subset=[COL_OARE_ID, COL_TRANSLITERATION, COL_TRANSLATION]).copy()
    train[COL_OARE_ID] = train[COL_OARE_ID].astype(str).str.strip()
    aid = aid.copy()
    aid[AID_TEXT_UUID] = aid[AID_TEXT_UUID].astype(str).str.strip()
    by_text = aid.groupby(AID_TEXT_UUID, sort=False)

    all_rows: list[dict[str, Any]] = []
    recovered_docs_records: list[dict[str, Any]] = []
    repair_reject: Counter[str] = Counter()
    recovered_norm_translations: set[str] = set()

    for _, trow in train.iterrows():
        oid = str(trow[COL_OARE_ID])
        translit = str(trow[COL_TRANSLITERATION])
        translation = str(trow[COL_TRANSLATION])

        if oid not in by_text.groups:
            continue
        sub = by_text.get_group(oid)
        if sub.empty:
            continue
        try:
            sorted_sub = _sort_sentence_rows(sub)
        except (ValueError, TypeError):
            continue

        built, _reason, _conf = _rows_for_doc(oid, translit, translation, sorted_sub)
        if built is not None:
            # M08: carry strict M04 rows through unchanged (no extra row filters on strict).
            paired_strict = [(str(r[COL_TRANSLITERATION]), str(r[COL_TRANSLATION])) for r in built]
            rows = _materialize_rows(
                oid,
                sorted_sub,
                paired_strict,
                str(built[0]["alignment_method"]),
                float(built[0]["alignment_confidence"]),
                TYPE_STRICT,
            )
            all_rows.extend(rows)
            continue

        tokens = _tokenize_transliteration(translit)
        akk_spans, anchor_err = _extract_akk_spans(tokens, sorted_sub)
        if anchor_err is not None:
            if anchor_err == "first_word_not_found":
                repair_reject["skip_first_word_not_found"] += 1
            else:
                repair_reject[f"skip_anchor_error:{anchor_err}"] += 1
            continue

        eng_parts = split_english_conservative(translation)
        na = len(akk_spans)
        ne = len(eng_parts)
        paired, _method, _c = _pair_eng_to_akk(akk_spans, eng_parts)
        if paired is not None:
            repair_reject["unexpected_strict_success_after_repair_precheck"] += 1
            continue

        if na != ne + 1:
            repair_reject["ineligible_count_not_plus_one"] += 1
            continue

        accepted = False
        for repair_type, delim in REPAIR_ORDER:
            rebuilt, rreason = apply_delimiter_resplit(eng_parts, delim, na)
            if rebuilt is None:
                repair_reject[f"{repair_type}:{rreason}"] += 1
                continue
            paired2, method2, conf2 = _pair_eng_to_akk(akk_spans, rebuilt)
            if paired2 is None or method2 != "exact_count":
                repair_reject[f"{repair_type}:pairing_failed_after_resplit"] += 1
                continue
            cand = _materialize_rows(oid, sorted_sub, paired2, method2, conf2, repair_type)
            ok, why = _document_passes_filters(
                cand,
                is_recovered=True,
                recovered_norm_translations=recovered_norm_translations,
            )
            if not ok:
                repair_reject[f"{repair_type}:doc_rejected:{why}"] += 1
                continue
            all_rows.extend(cand)
            recovered_docs_records.append(
                {
                    "oare_id": oid,
                    "repair_type": repair_type,
                    "num_pairs": str(len(cand)),
                    "sentence_ids": ";".join(r["sentence_id"] for r in cand),
                }
            )
            accepted = True
            break

        if not accepted:
            repair_reject["repair_exhausted_no_accepted_path"] += 1

    sentence_ids = [r["sentence_id"] for r in all_rows]
    if len(sentence_ids) != len(set(sentence_ids)):
        dup = [x for x in sentence_ids if sentence_ids.count(x) > 1]
        msg = f"duplicate sentence_id in Candidate A output (fail-closed): {dup[:5]!r}"
        raise AlignmentQualityError(msg)

    candidate_a_path = output_dir / "aligned_train_sentences_quality_v2_split.csv"
    report_a_path = output_dir / "alignment_quality_v2_report.json"
    recovered_path = output_dir / "recovered_docs.csv"
    candidate_b_path = output_dir / "aligned_train_sentences_quality_v2_plus_m06.csv"
    report_b_path = output_dir / "alignment_quality_v2_plus_m06_report.json"

    _write_m08_csv(candidate_a_path, all_rows)
    _write_recovered_docs_csv(recovered_path, recovered_docs_records)

    overlap = verify_aligned_no_dev_oare_overlap(candidate_a_path, dev_split_csv)
    if not overlap["passes"]:
        msg = f"dev overlap fail-closed: {overlap!r}"
        raise AlignmentQualityError(msg)

    core_keys = (
        "sentence_id",
        COL_OARE_ID,
        COL_TRANSLITERATION,
        COL_TRANSLATION,
        "line_start",
        "line_end",
        "alignment_method",
        "alignment_confidence",
    )
    fp_a = _sha256_canonical_rows(all_rows, core_keys)

    strict_row_count = sum(1 for r in all_rows if r[M08_EXTRA_COL] == TYPE_STRICT)
    recovered_row_count = sum(
        1 for r in all_rows if r[M08_EXTRA_COL] in (TYPE_SEMICOLON, TYPE_COLON)
    )
    by_quality = Counter(str(r[M08_EXTRA_COL]) for r in all_rows)

    m06_base = load_csv(m06_baseline_csv)
    winner_rows: list[dict[str, Any]] = []
    for sid in sorted(M06_CANONICAL_WINNER_SENTENCE_IDS):
        match = m06_base.loc[m06_base["sentence_id"].astype(str) == sid]
        if match.empty:
            msg = f"M06 winner sentence_id missing from baseline: {sid!r}"
            raise AlignmentQualityError(msg)
        r0 = match.iloc[0]
        winner_rows.append(
            {
                "sentence_id": sid,
                COL_OARE_ID: str(r0[COL_OARE_ID]),
                COL_TRANSLITERATION: str(r0[COL_TRANSLITERATION]),
                COL_TRANSLATION: str(r0[COL_TRANSLATION]),
                "line_start": str(r0.get("line_start", "")),
                "line_end": str(r0.get("line_end", "")),
                "alignment_method": str(r0.get("alignment_method", "")),
                "alignment_confidence": str(r0.get("alignment_confidence", "")),
                M08_EXTRA_COL: TYPE_M06_UNION,
            }
        )

    existing_ids = {r["sentence_id"] for r in all_rows}
    union_extra: list[dict[str, Any]] = []
    for wr in winner_rows:
        if wr["sentence_id"] not in existing_ids:
            union_extra.append(wr)
    candidate_b_rows = all_rows + union_extra

    _write_m08_csv(candidate_b_path, candidate_b_rows)
    overlap_b = verify_aligned_no_dev_oare_overlap(candidate_b_path, dev_split_csv)
    if not overlap_b["passes"]:
        msg = f"dev overlap fail-closed (Candidate B): {overlap_b!r}"
        raise AlignmentQualityError(msg)

    fp_b = _sha256_canonical_rows(candidate_b_rows, core_keys)

    m06_all_fp = _sha256_canonical_rows(
        [
            {
                "sentence_id": str(r["sentence_id"]),
                COL_OARE_ID: str(r[COL_OARE_ID]),
                COL_TRANSLITERATION: str(r[COL_TRANSLITERATION]),
                COL_TRANSLATION: str(r[COL_TRANSLATION]),
                "line_start": str(r.get("line_start", "")),
                "line_end": str(r.get("line_end", "")),
                "alignment_method": str(r.get("alignment_method", "")),
                "alignment_confidence": str(r.get("alignment_confidence", "")),
            }
            for _, r in m06_base.iterrows()
        ],
        core_keys,
    )

    strict_baseline_fp: str | None = None
    no_op_a = False
    strict_fingerprint_available = False
    if strict_baseline_csv is not None and strict_baseline_csv.is_file():
        strict_aligned = load_csv(strict_baseline_csv)
        for col in ("sentence_id", COL_OARE_ID, COL_TRANSLITERATION, COL_TRANSLATION):
            if col not in strict_aligned.columns:
                msg = f"strict baseline CSV missing {col!r}"
                raise AlignmentQualityError(msg)
        strict_rows = [
            {
                "sentence_id": str(r["sentence_id"]),
                COL_OARE_ID: str(r[COL_OARE_ID]),
                COL_TRANSLITERATION: str(r[COL_TRANSLITERATION]),
                COL_TRANSLATION: str(r[COL_TRANSLATION]),
                "line_start": str(r.get("line_start", "")),
                "line_end": str(r.get("line_end", "")),
                "alignment_method": str(r.get("alignment_method", "")),
                "alignment_confidence": str(r.get("alignment_confidence", "")),
            }
            for _, r in strict_aligned.iterrows()
        ]
        strict_baseline_fp = _sha256_canonical_rows(strict_rows, core_keys)
        strict_fingerprint_available = True
        no_op_a = fp_a == strict_baseline_fp and recovered_row_count == 0

    no_op_b = fp_b == m06_all_fp

    report_common = {
        "source_train_split_csv": str(train_split_csv.as_posix()),
        "source_train_split_sha256": _sha256_file(train_split_csv),
        "source_dev_split_csv": str(dev_split_csv.as_posix()),
        "source_dev_split_sha256": _sha256_file(dev_split_csv),
        "source_sentences_aid_csv": str(sentences_aid_csv.as_posix()),
        "source_sentences_aid_sha256": _sha256_file(sentences_aid_csv),
        "m06_baseline_csv": str(m06_baseline_csv.as_posix()),
        "m06_baseline_sha256": _sha256_file(m06_baseline_csv),
        "strict_baseline_csv": str(strict_baseline_csv.as_posix()) if strict_baseline_csv else None,
        "strict_baseline_canonical_sha256": strict_baseline_fp,
        "output_candidate_a_csv": str(candidate_a_path.as_posix()),
        "output_candidate_a_sha256": _sha256_file(candidate_a_path),
        "candidate_a_canonical_core_sha256": fp_a,
        "strict_row_count": strict_row_count,
        "recovered_row_count": recovered_row_count,
        "recovered_document_count": len(recovered_docs_records),
        "counts_by_alignment_quality_type": dict(sorted(by_quality.items())),
        "repair_rejection_counts": dict(sorted(repair_reject.items())),
        "m06_winner_sentence_ids_canonical": sorted(M06_CANONICAL_WINNER_SENTENCE_IDS),
        "m06_winners_present_in_candidate_a_sentence_ids": sorted(
            sid for sid in M06_CANONICAL_WINNER_SENTENCE_IDS if sid in existing_ids
        ),
        "m06_winners_union_appended_count": len(union_extra),
        "dev_overlap_check_candidate_a": overlap,
        "early_no_op_gate_candidate_a": no_op_a,
        "early_no_op_gate_candidate_a_strict_fingerprint_available": strict_fingerprint_available,
        "early_no_op_gate_candidate_b_identical_to_m06_baseline": no_op_b,
        "early_no_op_stop_recommended": bool(no_op_a and no_op_b),
        "output_candidate_b_csv": str(candidate_b_path.as_posix()),
        "output_candidate_b_sha256": _sha256_file(candidate_b_path),
        "candidate_b_canonical_core_sha256": fp_b,
        "m06_baseline_canonical_core_sha256": m06_all_fp,
        "dev_overlap_check_candidate_b": overlap_b,
    }

    report_a_path.parent.mkdir(parents=True, exist_ok=True)
    payload_a = {**report_common, "report_kind": "alignment_quality_v2_candidate_a"}
    canonical_a = json.dumps(payload_a, sort_keys=True, separators=(",", ":"))
    payload_a["alignment_quality_v2_report_sha256"] = hashlib.sha256(
        canonical_a.encode("utf-8")
    ).hexdigest()
    report_a_path.write_text(
        json.dumps(payload_a, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    payload_b = {
        **report_common,
        "report_kind": "alignment_quality_v2_plus_m06",
        "total_rows_candidate_b": len(candidate_b_rows),
    }
    canonical_b = json.dumps(payload_b, sort_keys=True, separators=(",", ":"))
    payload_b["alignment_quality_v2_plus_m06_report_sha256"] = hashlib.sha256(
        canonical_b.encode("utf-8")
    ).hexdigest()
    report_b_path.write_text(
        json.dumps(payload_b, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return payload_a
