# M06 — Run 1 — Policy builder (selection + reports)

**Purpose:** Build **Policy A** and **Policy B** training CSVs from the split-safe M05 augmented superset, with hashed JSON reports and **zero** dev `oare_id` overlap.

**Plan:** [M06_plan.md](M06_plan.md)  
**Status:** **Complete** (M06 closeout).

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

## Closeout snapshot (locked training composition)

Canonical row counts used for training/eval (Policy A CSV):

| Item | Value |
|------|--------|
| Strict (`direct_aid_strict`) | **236** |
| Selected expansion (Policy A) | **2** |
| **Policy A total rows** | **238** |
| `dev_overlap_oare_ids` | **0** (required) |

High-confidence expansion under the locked policy proved **extremely sparse** (only **2** rows survived gating + cap). Full `prerequisite_analysis`, SHA-256 hashes, threshold/fallback flags, and per-type counts remain in the local JSON reports under `data/derived/selection/` (gitignored).

---

## Phase-1 analysis (from reports)

After a successful run, copy **as-built** fields from the JSON reports into the tables below (do not hand-edit counts without re-running the selector). At closeout, **row counts** above are the authority for milestone narrative; hashes live only in local `*_report.json`.

### Source analysis (`prerequisite_analysis` in Policy A report)

| Field | Value (paste from JSON) |
|-------|-------------------------|
| `row_count_total` | *(local JSON)* |
| `strict_row_count` | **236** (matches closeout) |
| `relaxed_row_count` | *(local JSON)* |
| `expansion_non_relaxed_row_count` | *(local JSON)* |
| `confidence_overall` (min / max / mean) | *(local JSON)* |
| `expansion_non_relaxed_confidence.count_ge_0_90` | *(local JSON)* |
| `expansion_non_relaxed_confidence.count_ge_0_80` | *(local JSON)* |
| Fallback would trigger? (`count_ge_0_90` < 16) | *(local JSON)* |

### Policy A — `strict_plus_highconf_cap50_report.json`

| Field | Value |
|-------|--------|
| `source_csv_sha256` | *(local JSON)* |
| `output_csv_sha256` | *(local JSON)* |
| `strict_row_count` | **236** |
| `selected_expansion_row_count` | **2** |
| `excluded_relaxed_row_count` | *(local JSON)* |
| `confidence_threshold_used` | *(local JSON)* |
| `fallback_threshold_triggered` | *(local JSON)* |
| `cap_value_used` | *(local JSON; design max 118 at strict=236)* |
| `strict_expansion_effective_sampling_ratio` | **236:2** |
| `dev_overlap_oare_ids` | **0** |

### Policy B — `strict_plus_highconf_cap50_weighted2x_report.json`

| Field | Value |
|-------|--------|
| `output_csv_sha256` | *(local JSON)* |
| `strict_row_materialized_count` | **472** (236 × 2) |
| `selected_expansion_row_count` | **2** |
| `strict_repeat_factor` / `expansion_repeat_factor` | **2** / **1** |
| `strict_expansion_effective_sampling_ratio` | **472:2** |
| `dev_overlap_oare_ids` | **0** |

---

## CI note

Selector logic and fail-closed behavior are covered by `tests/test_m06_selection.py` (fixtures only; no competition data in CI).
