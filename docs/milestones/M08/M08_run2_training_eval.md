# M08 — Run 2: training + eval (local GPU matrix)

**Milestone:** M08 — Alignment-quality recovery  
**Phase:** 4 — **complete** (local GPU, frozen dev contract)  
**Branch:** `m08-alignment-quality-recovery` (closeout merge → `main`)

## Preconditions (met)

1. CI-safe tests green before GPU.
2. `python -m akk2eng.pipeline.align_quality` completed; dev overlap **0**.
3. Early no-op gate **did not** apply (Candidate A materially differed from M04 strict-only via recovered rows).

## Locked 3-run matrix

| Run | Output dir | Train CSV |
|-----|------------|-----------|
| Baseline | `outputs/m08_t5_baseline_m06_policy_a` | `data/derived/selection/strict_plus_highconf_cap50.csv` |
| Candidate A | `outputs/m08_t5_alignment_quality_v2` | `data/derived/alignment_quality/aligned_train_sentences_quality_v2_split.csv` |
| Candidate B | `outputs/m08_t5_alignment_quality_v2_plus_m06` | `data/derived/alignment_quality/aligned_train_sentences_quality_v2_plus_m06.csv` |

Exact shell commands: **`M08_local_gpu_execution.md`**.

## Results table (frozen dev, same-run)

| Run | chrF (dev) | Notes |
|-----|------------|-------|
| Baseline (M06 Policy A CSV rerun) | **52.2530** | Same continuation recipe as M06/M07 |
| Candidate A (alignment-quality v2) | **20.0045** | 236 strict + **46** recovered full-sentence pairs |
| Candidate B (A ∪ M06 winners) | **20.0045** | No dev gain vs A in this run |

**Best Δ vs baseline (least-negative candidate):** **−32.2485** chrF (vs **52.2530**).  
**Historical pin reference:** **52.2530** chrF (M06 Policy A).

## Completion signal (locked)

```text
Baseline chrF: 52.2530
Alignment-quality v2 chrF: 20.0045
Alignment-quality v2 + M06 chrF: 20.0045
Best Δ vs baseline: -32.2485
Decision: M08 regression — recovered rows reintroduce noise
```

## Decision rules (±0.5 chrF band)

**Locked label:**

```text
M08 regression — recovered rows reintroduce noise
```

Success and neutral labels from the plan **do not apply** for this closeout.

## Kaggle

**No submission.** No `M08_run3_kaggle_submit.md` (regression; dev gate not cleared).

## Status

- [x] Baseline + Candidate A + Candidate B trained and evaluated locally
- [x] Decision recorded
- [x] Milestone closed as **high-value negative result**
