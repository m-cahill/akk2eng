"""M06: deterministic selection and weighted materialization on M05 augmented CSV.

Operates only on ``augmented_train_sentences.csv`` — no new augmentation heuristics.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from akk2eng.data.alignment import verify_aligned_no_dev_oare_overlap
from akk2eng.data.augmentation import AUGMENTED_OUTPUT_COLS
from akk2eng.data.loader import load_csv

PRIMARY_CONFIDENCE_THRESHOLD = 0.90
FALLBACK_CONFIDENCE_THRESHOLD = 0.80
MIN_EXPANSION_ROWS_BEFORE_FALLBACK = 16
CAP_FRACTION_STRICT = 0.50

STRICT_TYPE = "direct_aid_strict"
TYPE_ORDER = (
    "expanded_english_resplit",
    "expanded_partial_prefix",
)


class SelectionError(Exception):
    """Fail-closed selection / prerequisite violation."""


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _type_rank_parts(aug_type: str) -> tuple[int, str]:
    """Primary rank (lower preferred), then tie-break string for unknown types."""
    if aug_type in TYPE_ORDER:
        return TYPE_ORDER.index(aug_type), ""
    return len(TYPE_ORDER), aug_type


def _validate_numeric_confidence(df: pd.DataFrame) -> pd.Series:
    """Return float series; raise SelectionError if any value missing or non-numeric."""
    if "augmentation_confidence" not in df.columns:
        msg = "augmented CSV missing required column 'augmentation_confidence'"
        raise SelectionError(msg)
    col = df["augmentation_confidence"]
    parsed = pd.to_numeric(col, errors="coerce")
    bad = parsed.isna() | col.isna()
    # Empty strings become NaN after to_numeric; NaN triggers fail-closed.
    if bad.any():
        n = int(bad.sum())
        msg = f"augmentation_confidence missing or non-numeric for {n} row(s); fail-closed per M06"
        raise SelectionError(msg)
    return parsed


def analyze_augmented_source(df: pd.DataFrame, conf: pd.Series) -> dict[str, Any]:
    """Lightweight deterministic prerequisite analysis for reports."""
    by_type = df["augmentation_type"].astype(str).value_counts().to_dict()
    by_type = {str(k): int(v) for k, v in sorted(by_type.items())}

    relaxed_mask = df["augmentation_type"].astype(str).str.contains("relaxed", case=False, na=False)
    strict_mask = df["augmentation_type"].astype(str) == STRICT_TYPE
    expansion_non_relaxed = (~strict_mask) & (~relaxed_mask)

    sub = conf[expansion_non_relaxed]
    analysis: dict[str, Any] = {
        "row_count_total": int(len(df)),
        "counts_by_augmentation_type": by_type,
        "strict_row_count": int(strict_mask.sum()),
        "relaxed_row_count": int(relaxed_mask.sum()),
        "expansion_non_relaxed_row_count": int(expansion_non_relaxed.sum()),
        "confidence_overall": {
            "min": float(conf.min()),
            "max": float(conf.max()),
            "mean": float(conf.mean()),
        },
        "expansion_non_relaxed_confidence": {
            "min": float(sub.min()) if len(sub) else None,
            "max": float(sub.max()) if len(sub) else None,
            "mean": float(sub.mean()) if len(sub) else None,
            "count_ge_0_90": int((sub >= PRIMARY_CONFIDENCE_THRESHOLD).sum()),
            "count_ge_0_80": int((sub >= FALLBACK_CONFIDENCE_THRESHOLD).sum()),
        },
    }
    return analysis


@dataclass
class PolicySelection:
    """Result of Policy A row selection (indices refer to input ``df`` row positions)."""

    strict_positions: list[int]
    expansion_positions: list[int]
    strict_count: int
    selected_expansion_count: int
    excluded_relaxed_count: int
    cap_used: int
    threshold_used: float
    fallback_triggered: bool
    output_by_augmentation_type: dict[str, int]
    analysis: dict[str, Any]


def select_policy_a(
    df: pd.DataFrame,
    conf: pd.Series,
) -> PolicySelection:
    """Apply locked Policy A rules; ``df`` must preserve original row order."""
    if "augmentation_type" not in df.columns:
        msg = "augmented CSV missing 'augmentation_type'"
        raise SelectionError(msg)
    if "source_row_id" not in df.columns:
        msg = "augmented CSV missing 'source_row_id'"
        raise SelectionError(msg)

    df = df.reset_index(drop=True)
    conf = conf.reset_index(drop=True)
    if len(conf) != len(df):
        msg = "augmentation_confidence series length does not match dataframe"
        raise SelectionError(msg)
    if conf.isna().any():
        n = int(conf.isna().sum())
        msg = f"augmentation_confidence missing or non-numeric for {n} row(s); fail-closed per M06"
        raise SelectionError(msg)
    df["_orig_idx"] = range(len(df))
    df["_conf"] = conf

    strict_mask = df["augmentation_type"].astype(str) == STRICT_TYPE
    strict_positions = df.loc[strict_mask, "_orig_idx"].tolist()
    strict_count = len(strict_positions)

    relaxed_mask = df["augmentation_type"].astype(str).str.contains("relaxed", case=False, na=False)
    excluded_relaxed_count = int(relaxed_mask.sum())

    expansion_mask = (~strict_mask) & (~relaxed_mask)
    cand = df.loc[expansion_mask].copy()

    n_ge_primary = int((cand["_conf"] >= PRIMARY_CONFIDENCE_THRESHOLD).sum())
    fallback_triggered = n_ge_primary < MIN_EXPANSION_ROWS_BEFORE_FALLBACK
    threshold_used = (
        FALLBACK_CONFIDENCE_THRESHOLD if fallback_triggered else PRIMARY_CONFIDENCE_THRESHOLD
    )

    cand = cand[cand["_conf"] >= threshold_used].copy()
    ranks = cand["augmentation_type"].astype(str).apply(_type_rank_parts)
    cand["_rank_pri"] = ranks.apply(lambda x: x[0])
    cand["_rank_sec"] = ranks.apply(lambda x: x[1])
    cand["_sid"] = cand["source_row_id"].astype(str)

    cand = cand.sort_values(
        by=["_conf", "_rank_pri", "_rank_sec", "_sid", "_orig_idx"],
        ascending=[False, True, True, True, True],
        kind="mergesort",
    )

    cap_used = int(math.floor(CAP_FRACTION_STRICT * strict_count))
    chosen = cand.head(cap_used)
    expansion_positions = chosen["_orig_idx"].astype(int).tolist()

    # Policy A CSV order: strict block (original order) then selected expansion (rank order)
    strict_part = df.loc[df["_orig_idx"].isin(strict_positions)].sort_values(
        "_orig_idx", kind="mergesort"
    )
    exp_part = chosen.drop(columns=["_rank_pri", "_rank_sec", "_sid"], errors="ignore")
    merged_for_counts = pd.concat([strict_part, exp_part], ignore_index=True)
    type_counts = merged_for_counts["augmentation_type"].astype(str).value_counts().to_dict()
    output_by_augmentation_type = {str(k): int(v) for k, v in sorted(type_counts.items())}

    analysis = analyze_augmented_source(df.drop(columns=["_conf"], errors="ignore"), conf)

    return PolicySelection(
        strict_positions=sorted(strict_positions),
        expansion_positions=expansion_positions,
        strict_count=strict_count,
        selected_expansion_count=len(expansion_positions),
        excluded_relaxed_count=excluded_relaxed_count,
        cap_used=cap_used,
        threshold_used=threshold_used,
        fallback_triggered=fallback_triggered,
        output_by_augmentation_type=output_by_augmentation_type,
        analysis=analysis,
    )


def frames_for_policy_a(
    df: pd.DataFrame,
    sel: PolicySelection,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Strict rows (file order) and selected expansion rows (rank order)."""
    df = df.reset_index(drop=True)
    strict_df = df.iloc[sel.strict_positions].copy()
    exp_df = df.iloc[sel.expansion_positions].copy()
    return strict_df, exp_df


def materialize_strict_dominant_weighted(
    strict_df: pd.DataFrame,
    expansion_df: pd.DataFrame,
    strict_repeat: int = 2,
) -> pd.DataFrame:
    """Policy B: repeat each strict row ``strict_repeat`` times, then expansion once each."""
    if strict_repeat < 1:
        msg = "strict_repeat must be >= 1"
        raise ValueError(msg)
    parts: list[pd.DataFrame] = []
    for _, row in strict_df.iterrows():
        chunk = pd.DataFrame([row.to_dict()] * strict_repeat)
        parts.append(chunk)
    if not expansion_df.empty:
        parts.append(expansion_df.copy())
    if not parts:
        return pd.DataFrame(columns=strict_df.columns)
    out = pd.concat(parts, ignore_index=True)
    return out


def write_policy_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = [c for c in AUGMENTED_OUTPUT_COLS if c in frame.columns]
    extra = [c for c in frame.columns if c not in cols and not str(c).startswith("_")]
    use_cols = cols + extra
    with path.open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=use_cols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for _, row in frame.iterrows():
            w.writerow({k: row.get(k, "") for k in use_cols})


def build_policy_a_report(
    *,
    source_csv: Path,
    output_csv: Path,
    dev_check: dict[str, Any],
    sel: PolicySelection,
) -> dict[str, Any]:
    return {
        "policy": "strict_plus_highconf_cap50",
        "source_csv_sha256": _sha256_file(source_csv),
        "output_csv_sha256": _sha256_file(output_csv),
        "strict_row_count": sel.strict_count,
        "selected_expansion_row_count": sel.selected_expansion_count,
        "excluded_relaxed_row_count": sel.excluded_relaxed_count,
        "counts_by_augmentation_type": sel.output_by_augmentation_type,
        "confidence_threshold_used": sel.threshold_used,
        "fallback_threshold_triggered": sel.fallback_triggered,
        "cap_value_used": sel.cap_used,
        "strict_expansion_effective_sampling_ratio": (
            f"{sel.strict_count}:{sel.selected_expansion_count}"
        ),
        "dev_overlap_oare_ids": dev_check["n_overlap_oare_ids"],
        "dev_overlap_passes": dev_check["passes"],
        "prerequisite_analysis": sel.analysis,
    }


def build_policy_b_report(
    *,
    source_csv: Path,
    policy_a_csv: Path,
    output_csv: Path,
    dev_check: dict[str, Any],
    sel: PolicySelection,
    strict_repeat: int,
    weighted_by_augmentation_type: dict[str, int],
) -> dict[str, Any]:
    eff_strict = sel.strict_count * strict_repeat
    return {
        "policy": "strict_plus_highconf_cap50_weighted2x",
        "source_csv_sha256": _sha256_file(source_csv),
        "policy_a_csv_sha256": _sha256_file(policy_a_csv),
        "output_csv_sha256": _sha256_file(output_csv),
        "strict_row_count_logical": sel.strict_count,
        "strict_row_materialized_count": eff_strict,
        "selected_expansion_row_count": sel.selected_expansion_count,
        "excluded_relaxed_row_count": sel.excluded_relaxed_count,
        "counts_by_augmentation_type": weighted_by_augmentation_type,
        "confidence_threshold_used": sel.threshold_used,
        "fallback_threshold_triggered": sel.fallback_triggered,
        "cap_value_used": sel.cap_used,
        "strict_repeat_factor": strict_repeat,
        "expansion_repeat_factor": 1,
        "strict_expansion_effective_sampling_ratio": (
            f"{eff_strict}:{sel.selected_expansion_count}"
        ),
        "dev_overlap_oare_ids": dev_check["n_overlap_oare_ids"],
        "dev_overlap_passes": dev_check["passes"],
        "prerequisite_analysis": sel.analysis,
    }


def run_m06_selection(
    source_augmented_csv: Path,
    output_dir: Path,
    dev_split_csv: Path,
    *,
    write_policy_b: bool = True,
) -> tuple[Path, Path, Path | None, Path | None]:
    """Build Policy A (and optionally B) CSVs + JSON reports; verify dev overlap.

    Returns paths: policy_a_csv, policy_a_report, policy_b_csv|None, policy_b_report|None
    """
    if not source_augmented_csv.is_file():
        msg = f"Prerequisite augmented CSV not found: {source_augmented_csv}"
        raise SelectionError(msg)

    df = load_csv(source_augmented_csv)
    conf = _validate_numeric_confidence(df)
    sel = select_policy_a(df, conf)
    strict_df, exp_df = frames_for_policy_a(df, sel)

    # Drop helper columns if present
    for part in (strict_df, exp_df):
        for c in list(part.columns):
            if str(c).startswith("_"):
                part.drop(columns=[c], inplace=True)

    out_a = output_dir / "strict_plus_highconf_cap50.csv"
    rep_a = output_dir / "strict_plus_highconf_cap50_report.json"
    write_policy_csv(out_a, pd.concat([strict_df, exp_df], ignore_index=True))

    dev_check = verify_aligned_no_dev_oare_overlap(out_a, dev_split_csv)
    if not dev_check["passes"]:
        msg = (
            f"Dev overlap check failed: n_overlap_oare_ids={dev_check['n_overlap_oare_ids']} "
            f"(required 0)"
        )
        raise SelectionError(msg)

    report_a = build_policy_a_report(
        source_csv=source_augmented_csv,
        output_csv=out_a,
        dev_check=dev_check,
        sel=sel,
    )
    rep_a.write_text(json.dumps(report_a, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    out_b_path: Path | None = None
    rep_b_path: Path | None = None
    if write_policy_b:
        out_b = output_dir / "strict_plus_highconf_cap50_weighted2x.csv"
        rep_b = output_dir / "strict_plus_highconf_cap50_weighted2x_report.json"
        weighted = materialize_strict_dominant_weighted(strict_df, exp_df, strict_repeat=2)
        write_policy_csv(out_b, weighted)
        dev_b = verify_aligned_no_dev_oare_overlap(out_b, dev_split_csv)
        if not dev_b["passes"]:
            msg = (
                f"Policy B dev overlap check failed: "
                f"n_overlap_oare_ids={dev_b['n_overlap_oare_ids']}"
            )
            raise SelectionError(msg)
        wtypes = weighted["augmentation_type"].astype(str).value_counts().to_dict()
        weighted_by_type = {str(k): int(v) for k, v in sorted(wtypes.items())}
        report_b = build_policy_b_report(
            source_csv=source_augmented_csv,
            policy_a_csv=out_a,
            output_csv=out_b,
            dev_check=dev_b,
            sel=sel,
            strict_repeat=2,
            weighted_by_augmentation_type=weighted_by_type,
        )
        rep_b.write_text(json.dumps(report_b, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        out_b_path, rep_b_path = out_b, rep_b

    return out_a, rep_a, out_b_path, rep_b_path
