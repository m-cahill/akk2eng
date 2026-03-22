# M07 — Run 1: confidence_v2 builder (local artifacts)

**Milestone:** M07 — Confidence-driven expansion  
**Phase:** 1 (scorer + reports) — **complete** on branch `m07-confidence-driven-expansion`  
**Date:** 2026-03-22  

## Command

From repository root (with `data/` populated per M05/M06):

```bash
python -m akk2eng.pipeline.select_confident_train
```

Defaults: `--input-augmented-csv data/derived/augmentation/augmented_train_sentences.csv`, `--baseline-m06-csv data/derived/selection/strict_plus_highconf_cap50.csv`, `--output-dir data/derived/confidence/`, `--verify-dev-split-csv data/splits/dev_split.csv`.

## Input hashes (this run)

| Artifact | SHA-256 |
|----------|---------|
| M05 `augmented_train_sentences.csv` | `9f8a852b5115d22df91bc98b53948f0e48a9e04b246d356b5b4572edd5fb70e5` |
| M06 `strict_plus_highconf_cap50.csv` (baseline) | `bf3917cdac55916da83898e0d118709b0a2db479b55dcb9fdc057741ab7b25cf` |

## Pool audit (from `confidence_v2_report.json`)

| Stage | Count |
|-------|------:|
| Expansion non-relaxed (initial) | 298 |
| After drop bad `augmentation_confidence` | 298 |
| After drop translation `<gap>` / `broken` | 262 |
| After drop translation &lt; 4 tokens | 257 |
| After dedupe duplicate normalized translation | **252** (final scored expansion pool) |

**`confidence_v2` on final pool:** min **0.1514…**, max **0.95**, mean **0.5918…**  

**Final counts by `augmentation_type`:** `expanded_english_resplit` **2**, `expanded_partial_prefix` **250**.

## M06 winner identity (locked)

Both M06 Policy A expansion rows are present in the scored pool and in cap6/cap10 selections:

- `fc678a23-7011-4f9d-8957-ebf2c8dbbb43:2651ad13-ef9b-4941-a3e9-44d76a13b191`
- `fc678a23-7011-4f9d-8957-ebf2c8dbbb43:c7d5c7a2-793b-49e0-8991-c57d70981fcf`

## Output files & hashes (this run)

| File | SHA-256 |
|------|---------|
| `scored_expansion_pool.csv` | `50487a97261114f0d91437fcc650ae8baa5f069d994a1cba2149272cdb24ccd4` |
| `strict_plus_confv2_cap6.csv` | *(see `strict_plus_confv2_cap6_report.json` → `output_csv_sha256`)* `acaedb69cb002d01c92da5f3b7c692ceb0da7d2adb36ec0fda404d76026de4f4` |
| `strict_plus_confv2_cap10.csv` | *(see cap10 report)* `432bd4d24a3e5bc5f1c5ce6f45f7d35b5e9d529c35b2ac76a66354175e8b66b7` |

## Caps

| Dataset | Strict rows | Expansion rows | Shortfall vs cap | Dev `oare_id` overlap |
|---------|------------:|-----------------:|------------------|----------------------|
| `strict_plus_confv2_cap6.csv` | 236 | 6 | 0 | **0** |
| `strict_plus_confv2_cap10.csv` | 236 | 10 | 0 | **0** |

## Top expansion rows (cap6, by rank)

See `data/derived/confidence/strict_plus_confv2_cap6_report.json` → `top_selected_expansion_rows` (includes `augmentation_confidence`, `confidence_v2`, `source_row_id`, `augmentation_type`). The first two ranked rows are the M06 `expanded_english_resplit` winners (**confidence_v2 = 0.95**).

## Status

- [x] Scorer + CLI implemented (`src/akk2eng/data/confidence.py`, `pipeline/select_confident_train.py`)
- [x] Deterministic reports + SHA-256 fields
- [x] M06 winners preserved; dev overlap **0**
- [ ] Phase 4 GPU matrix — **not started** (see `M07_local_gpu_execution.md`)
