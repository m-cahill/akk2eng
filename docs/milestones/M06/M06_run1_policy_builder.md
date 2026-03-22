# M06 — Run 1 — Policy builder (selection + reports)

**Purpose:** Build **Policy A** and **Policy B** training CSVs from the split-safe M05 augmented superset, with hashed JSON reports and **zero** dev `oare_id` overlap.

**Plan:** [M06_plan.md](M06_plan.md)

---

## Prerequisites

1. **Frozen dev split** exists: `data/splits/dev_split.csv` (and train split as used in M04/M05).
2. **M05 artifact** exists: `data/derived/augmentation/augmented_train_sentences.csv`  
   - Treat as **read-only input**. Regenerate with `python -m akk2eng.pipeline.augment --split-safe` **only** if the file is missing or inconsistent with M05 closeout hashes/counts; if you regenerate, record that here as a **reproducibility recovery** note.

### Prerequisite check (local)

```powershell
Test-Path data\derived\augmentation\augmented_train_sentences.csv
Test-Path data\splits\dev_split.csv
```

If the augmented CSV is missing, stop and run M05 `--split-safe` first, then re-run this step.

---

## Build policies (deterministic)

From repo root (venv activated):

```bash
python -m akk2eng.pipeline.select_train \
  --input-csv data/derived/augmentation/augmented_train_sentences.csv \
  --output-dir data/derived/selection \
  --verify-dev-split-csv data/splits/dev_split.csv
```

Defaults match the paths above; flags are shown explicitly for audit copy-paste.

**On success:** writes:

| Artifact | Path |
|----------|------|
| Policy A CSV | `data/derived/selection/strict_plus_highconf_cap50.csv` |
| Policy A report | `data/derived/selection/strict_plus_highconf_cap50_report.json` |
| Policy B CSV | `data/derived/selection/strict_plus_highconf_cap50_weighted2x.csv` |
| Policy B report | `data/derived/selection/strict_plus_highconf_cap50_weighted2x_report.json` |

**On failure:** CLI exits non-zero (`SelectionError` — e.g. bad confidence, dev overlap, missing input). Do not proceed to GPU training until this step is clean.

---

## Phase-1 analysis (from reports)

After a successful run, copy **as-built** fields from the JSON reports into the tables below (do not hand-edit counts without re-running the selector).

### Source analysis (`prerequisite_analysis` in Policy A report)

| Field | Value (paste from JSON) |
|-------|-------------------------|
| `row_count_total` | |
| `strict_row_count` | |
| `relaxed_row_count` | |
| `expansion_non_relaxed_row_count` | |
| `confidence_overall` (min / max / mean) | |
| `expansion_non_relaxed_confidence.count_ge_0_90` | |
| `expansion_non_relaxed_confidence.count_ge_0_80` | |
| Fallback would trigger? (`count_ge_0_90` < 16) | |

### Policy A — `strict_plus_highconf_cap50_report.json`

| Field | Value |
|-------|--------|
| `source_csv_sha256` | |
| `output_csv_sha256` | |
| `strict_row_count` | |
| `selected_expansion_row_count` | |
| `excluded_relaxed_row_count` | |
| `confidence_threshold_used` | |
| `fallback_threshold_triggered` | |
| `cap_value_used` | |
| `strict_expansion_effective_sampling_ratio` | |
| `dev_overlap_oare_ids` | **must be 0** |

### Policy B — `strict_plus_highconf_cap50_weighted2x_report.json`

| Field | Value |
|-------|--------|
| `output_csv_sha256` | |
| `strict_row_materialized_count` | |
| `selected_expansion_row_count` | |
| `strict_repeat_factor` / `expansion_repeat_factor` | |
| `strict_expansion_effective_sampling_ratio` | |
| `dev_overlap_oare_ids` | **must be 0** |

---

## CI note

Selector logic and fail-closed behavior are covered by `tests/test_m06_selection.py` (fixtures only; no competition data in CI).
