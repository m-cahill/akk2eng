"""M07: deterministic confidence_v2 scoring over split-safe M05 augmented rows.

Operates only on ``augmented_train_sentences.csv`` and the frozen M06 Policy A baseline CSV.
No dev labels, no new augmentation.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from akk2eng.data.alignment import verify_aligned_no_dev_oare_overlap
from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_OARE_ID, COL_TRANSLATION, COL_TRANSLITERATION
from akk2eng.data.selection import write_policy_csv

STRICT_TYPE = "direct_aid_strict"
TYPE_EXPANDED_RESPLIT = "expanded_english_resplit"
TYPE_EXPANDED_PREFIX = "expanded_partial_prefix"
TYPE_ORDER = (TYPE_EXPANDED_RESPLIT, TYPE_EXPANDED_PREFIX)

REQUIRED_COLUMNS = (
    "sentence_id",
    COL_OARE_ID,
    COL_TRANSLITERATION,
    COL_TRANSLATION,
    "augmentation_type",
    "augmentation_confidence",
    "source_row_id",
)

_DIGIT_RE = re.compile(r"\d+")


class ConfidenceError(Exception):
    """Fail-closed M07 confidence pipeline."""


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_translation_text(text: str) -> str:
    """Whitespace-normalize English for token counts and duplicate detection."""
    return " ".join(str(text).split())


def translation_token_count(text: str) -> int:
    nt = normalize_translation_text(text)
    return len(nt.split()) if nt else 0


def transliteration_token_count(text: str) -> int:
    return len(str(text).split())


def _type_rank(aug_type: str) -> tuple[int, str]:
    s = str(aug_type)
    if s in TYPE_ORDER:
        return TYPE_ORDER.index(s), ""
    return len(TYPE_ORDER), s


def type_prior(aug_type: str) -> float:
    s = str(aug_type)
    if s == TYPE_EXPANDED_RESPLIT:
        return 0.05
    if s == TYPE_EXPANDED_PREFIX:
        return 0.0
    return 0.0


def digit_multiset(text: str) -> Counter[str]:
    return Counter(_DIGIT_RE.findall(str(text)))


def digit_consistency_adjustment(transliteration: str, translation: str) -> float:
    src = digit_multiset(transliteration)
    tgt = digit_multiset(translation)
    src_empty = len(src) == 0
    tgt_empty = len(tgt) == 0
    if not src_empty and not tgt_empty:
        return 0.05 if src == tgt else 0.0
    if src_empty ^ tgt_empty:
        return -0.05
    return 0.0


def length_adequacy_adjustment(src_len: int, tgt_len: int) -> float:
    if src_len <= 0:
        return -0.05
    low = max(4, math.floor(0.15 * src_len))
    high = math.ceil(1.25 * src_len)
    if low <= tgt_len <= high:
        return 0.05
    return -0.05


def source_gap_penalty(transliteration: str) -> float:
    t = str(transliteration).lower()
    if "<gap>" in t or "broken" in t:
        return -0.05
    return 0.0


def translation_has_exclusion_markers(translation: str) -> bool:
    tl = str(translation).lower()
    return "<gap>" in tl or "broken" in tl


def clip_unit(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def compute_confidence_v2(
    *,
    augmentation_confidence: float,
    augmentation_type: str,
    transliteration: str,
    translation: str,
) -> float:
    raw = float(augmentation_confidence)
    tp = type_prior(augmentation_type)
    da = digit_consistency_adjustment(transliteration, translation)
    slen = transliteration_token_count(transliteration)
    tlen = translation_token_count(translation)
    la = length_adequacy_adjustment(slen, tlen)
    gp = source_gap_penalty(transliteration)
    return clip_unit(raw + tp + da + la + gp)


def _validate_required_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        msg = f"augmented CSV missing required column(s): {missing!r}"
        raise ConfidenceError(msg)


def load_m06_expansion_sentence_ids(baseline_csv: Path) -> list[str]:
    """Return ``sentence_id`` values for non-strict rows in the M06 Policy A CSV."""
    if not baseline_csv.is_file():
        msg = f"M06 baseline CSV not found: {baseline_csv}"
        raise ConfidenceError(msg)
    base = load_csv(baseline_csv)
    _validate_required_columns(base)
    exp_mask = base["augmentation_type"].astype(str) != STRICT_TYPE
    ids = base.loc[exp_mask, "sentence_id"].astype(str).tolist()
    if len(ids) != 2:
        msg = (
            f"expected exactly 2 M06 expansion rows in baseline, found {len(ids)}; "
            "stop — cannot lock winner identity"
        )
        raise ConfidenceError(msg)
    return ids


def expansion_candidate_mask(df: pd.DataFrame) -> pd.Series:
    strict = df["augmentation_type"].astype(str) == STRICT_TYPE
    relaxed = df["augmentation_type"].astype(str).str.contains("relaxed", case=False, na=False)
    return ~strict & ~relaxed


def build_scored_expansion_pool(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return deduped, sorted expansion frame with ``confidence_v2`` + exclusion audit."""
    _validate_required_columns(df)
    df = df.reset_index(drop=True)
    df["_orig_idx"] = range(len(df))

    audit: dict[str, Any] = {}
    cand_mask = expansion_candidate_mask(df)
    work = df.loc[cand_mask].copy()
    audit["count_expansion_non_relaxed_initial"] = int(len(work))

    # Bad augmentation_confidence → drop row
    parsed = pd.to_numeric(work["augmentation_confidence"], errors="coerce")
    work = work.loc[parsed.notna()].copy()
    raw = pd.to_numeric(work["augmentation_confidence"], errors="coerce").astype(float)
    work["_raw_conf"] = raw
    audit["count_after_drop_bad_augmentation_confidence"] = int(len(work))

    # Translation gap/broken markers
    bad_mark = work[COL_TRANSLATION].astype(str).map(translation_has_exclusion_markers)
    work = work.loc[~bad_mark].copy()
    audit["count_after_drop_translation_gap_or_broken_marker"] = int(len(work))

    # Short normalized translation (<4 tokens)
    tok_counts = work[COL_TRANSLATION].astype(str).map(translation_token_count)
    work = work.loc[tok_counts >= 4].copy()
    audit["count_after_drop_short_translation_lt4_tokens"] = int(len(work))
    work["_aug_type"] = work["augmentation_type"].astype(str)
    tr = work[COL_TRANSLITERATION].astype(str)
    en = work[COL_TRANSLATION].astype(str)
    work["_confidence_v2"] = [
        compute_confidence_v2(
            augmentation_confidence=rc,
            augmentation_type=at,
            transliteration=s,
            translation=e,
        )
        for rc, at, s, e in zip(work["_raw_conf"], work["_aug_type"], tr, en, strict=True)
    ]

    ranks = work["_aug_type"].map(_type_rank)
    work["_type_pri"] = ranks.apply(lambda x: x[0])
    work["_type_sec"] = ranks.apply(lambda x: x[1])
    work["_sid"] = work["source_row_id"].astype(str)

    work = work.sort_values(
        by=["_confidence_v2", "_raw_conf", "_type_pri", "_type_sec", "_sid", "_orig_idx"],
        ascending=[False, False, True, True, True, True],
        kind="mergesort",
    )

    # Duplicate translations: keep highest-ranked only
    seen_norm: set[str] = set()
    keep_rows: list[int] = []
    for idx in work.index:
        norm = normalize_translation_text(str(work.at[idx, COL_TRANSLATION]))
        if norm in seen_norm:
            continue
        seen_norm.add(norm)
        keep_rows.append(idx)

    work = work.loc[keep_rows].copy()
    audit["count_after_dedupe_duplicate_normalized_translation"] = int(len(work))
    audit["final_scored_expansion_row_count"] = int(len(work))

    by_type = work["_aug_type"].value_counts().to_dict()
    audit["counts_by_augmentation_type_final"] = {
        str(k): int(v) for k, v in sorted(by_type.items())
    }

    v2 = work["_confidence_v2"]
    audit["confidence_v2_summary"] = {
        "count": int(len(v2)),
        "min": float(v2.min()) if len(v2) else None,
        "max": float(v2.max()) if len(v2) else None,
        "mean": float(v2.mean()) if len(v2) else None,
    }

    out = work.drop(
        columns=["_type_pri", "_type_sec", "_sid", "_raw_conf"],
        errors="ignore",
    )
    out = out.rename(columns={"_confidence_v2": "confidence_v2"})
    return out, audit


def strict_rows_preserve_order(df: pd.DataFrame) -> pd.DataFrame:
    """All strict rows in original CSV order."""
    df = df.reset_index(drop=True)
    m = df["augmentation_type"].astype(str) == STRICT_TYPE
    return df.loc[m].copy()


def select_top_expansion(scored: pd.DataFrame, cap: int) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Take first ``cap`` rows from pre-sorted deduped ``scored`` frame."""
    n_available = len(scored)
    n_take = min(cap, n_available)
    part = scored.head(n_take).copy()
    meta = {
        "cap_requested": cap,
        "expansion_rows_selected": n_take,
        "shortfall_vs_cap": max(0, cap - n_take),
        "pool_size_before_cap": n_available,
    }
    return part, meta


def _strip_internal_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    drop = [c for c in out.columns if str(c).startswith("_")]
    return out.drop(columns=drop, errors="ignore")


def _top_rows_for_report(expansion_df: pd.DataFrame, k: int = 20) -> list[dict[str, Any]]:
    cols = [
        "sentence_id",
        "source_row_id",
        "augmentation_type",
        "augmentation_confidence",
        "confidence_v2",
    ]
    have = [c for c in cols if c in expansion_df.columns]
    sub = expansion_df.head(k)
    return sub[have].to_dict(orient="records")


def run_m07_confidence_build(
    source_augmented_csv: Path,
    baseline_m06_csv: Path,
    output_dir: Path,
    dev_split_csv: Path,
    *,
    cap6: int = 6,
    cap10: int = 10,
) -> dict[str, Path]:
    """Write scored pool, main report, cap6/cap10 CSVs + reports. Returns paths dict."""
    if not source_augmented_csv.is_file():
        msg = f"Prerequisite augmented CSV not found: {source_augmented_csv}"
        raise ConfidenceError(msg)

    full = load_csv(source_augmented_csv)
    _validate_required_columns(full)

    m06_winners = load_m06_expansion_sentence_ids(baseline_m06_csv)
    winner_set = set(m06_winners)

    scored, pool_audit = build_scored_expansion_pool(full)
    scored_ids = set(scored["sentence_id"].astype(str))
    missing_winners = sorted(winner_set - scored_ids)
    if missing_winners:
        msg = (
            "M06 winner expansion row(s) excluded by confidence_v2 hard filters or not found "
            f"in scored pool: {missing_winners!r}; stop and report"
        )
        raise ConfidenceError(msg)

    output_dir.mkdir(parents=True, exist_ok=True)
    pool_path = output_dir / "scored_expansion_pool.csv"
    scored_out = _strip_internal_columns(scored)
    write_policy_csv(pool_path, scored_out)

    strict_df = strict_rows_preserve_order(full)
    for c in list(strict_df.columns):
        if str(c).startswith("_"):
            strict_df = strict_df.drop(columns=[c])

    def build_cap_csv(
        cap: int,
        stem: str,
    ) -> tuple[Path, Path, dict[str, Any]]:
        exp_sel, cap_meta = select_top_expansion(scored, cap)
        exp_sel_out = _strip_internal_columns(exp_sel)
        selected_ids = set(exp_sel_out["sentence_id"].astype(str))
        not_in_top = sorted(winner_set - selected_ids)
        if not_in_top:
            msg = (
                f"M06 winner row(s) not in top-{cap} expansion selection by confidence_v2: "
                f"{not_in_top!r}; stop and report"
            )
            raise ConfidenceError(msg)

        merged = pd.concat([strict_df, exp_sel_out], ignore_index=True)
        out_csv = output_dir / f"{stem}.csv"
        write_policy_csv(out_csv, merged)
        dev_check = verify_aligned_no_dev_oare_overlap(out_csv, dev_split_csv)
        if not dev_check["passes"]:
            msg = (
                f"Dev overlap check failed for {stem}: "
                f"n_overlap_oare_ids={dev_check['n_overlap_oare_ids']} (required 0)"
            )
            raise ConfidenceError(msg)

        report: dict[str, Any] = {
            "milestone": "M07",
            "dataset": stem,
            "source_augmented_csv_sha256": _sha256_file(source_augmented_csv),
            "baseline_m06_csv_sha256": _sha256_file(baseline_m06_csv),
            "output_csv_sha256": _sha256_file(out_csv),
            "strict_row_count": int(len(strict_df)),
            "m06_winner_sentence_ids": m06_winners,
            "m06_winners_preserved_in_selection": True,
            "dev_overlap_oare_ids": dev_check["n_overlap_oare_ids"],
            "dev_overlap_passes": dev_check["passes"],
            "cap_metadata": cap_meta,
            "top_selected_expansion_rows": _top_rows_for_report(exp_sel_out, k=max(cap, 10)),
            "counts_by_augmentation_type": {
                str(k): int(v)
                for k, v in sorted(
                    merged["augmentation_type"].astype(str).value_counts().to_dict().items()
                )
            },
        }
        rep_path = output_dir / f"{stem}_report.json"
        rep_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return out_csv, rep_path, report

    csv6, rep6, _ = build_cap_csv(cap6, "strict_plus_confv2_cap6")
    csv10, rep10, _ = build_cap_csv(cap10, "strict_plus_confv2_cap10")

    main_report: dict[str, Any] = {
        "milestone": "M07",
        "artifact": "confidence_v2_pool",
        "source_augmented_csv_sha256": _sha256_file(source_augmented_csv),
        "baseline_m06_csv_sha256": _sha256_file(baseline_m06_csv),
        "scored_expansion_pool_csv_sha256": _sha256_file(pool_path),
        "m06_winner_sentence_ids": m06_winners,
        "m06_winners_in_scored_pool": not bool(winner_set - scored_ids),
        "pool_exclusion_audit": pool_audit,
        "strict_row_count": int(len(strict_df)),
        "cap6_output": str(csv6.name),
        "cap10_output": str(csv10.name),
    }
    main_path = output_dir / "confidence_v2_report.json"
    main_path.write_text(json.dumps(main_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "scored_pool": pool_path,
        "main_report": main_path,
        "cap6_csv": csv6,
        "cap6_report": rep6,
        "cap10_csv": csv10,
        "cap10_report": rep10,
    }
