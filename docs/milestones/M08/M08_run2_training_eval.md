# M08 — Run 2: training + eval (local GPU matrix)

**Milestone:** M08 — Alignment-quality recovery  
**Phase:** 4 — **not started** (blocked until Phase 1–3 green and early no-op gate evaluated)

## Preconditions

1. `python -m pytest tests -q` green on `main` / M08 branch.
2. `python -m akk2eng.pipeline.align_quality` completed; reports show `dev_overlap_check_candidate_a.passes == true`.
3. If `early_no_op_stop_recommended == true` in `alignment_quality_v2_report.json`, **do not run GPU** — document neutral closeout per plan.

## Locked 3-run matrix

| Run | Output dir | Train CSV |
|-----|------------|-----------|
| Baseline | `outputs/m08_t5_baseline_m06_policy_a` | `data/derived/selection/strict_plus_highconf_cap50.csv` |
| Candidate A | `outputs/m08_t5_alignment_quality_v2` | `data/derived/alignment_quality/aligned_train_sentences_quality_v2_split.csv` |
| Candidate B | `outputs/m08_t5_alignment_quality_v2_plus_m06` | `data/derived/alignment_quality/aligned_train_sentences_quality_v2_plus_m06.csv` |

Exact shell commands: **`M08_local_gpu_execution.md`**.

## Results table (fill after runs)

| Run | chrF (dev) | Notes |
|-----|------------|-------|
| Baseline | | same-run M06 CSV rerun |
| Candidate A | | |
| Candidate B | | |

**Best Δ vs baseline:**  
**Historical pin reference:** 52.2530 chrF (M06 Policy A)

## Decision rules (±0.5 chrF band)

Use **exactly one** label:

```text
M08 success candidate — alignment-quality recovery beats M06 baseline
```

```text
M08 neutral — alignment repair yields no clear gain
```

```text
M08 regression — recovered rows reintroduce noise
```

## Kaggle

Only if success-candidate rules clear **and** documented here → add **`M08_run3_kaggle_submit.md`**. Otherwise **no** submit log.

## Completion signal (paste-back)

```text
Baseline chrF:
Alignment-quality v2 chrF:
Alignment-quality v2 + M06 chrF:
Best Δ vs baseline:
Decision:
```
