# M07 — Run 2: training & eval (locked 3-run matrix)

**Milestone:** M07 — Confidence-driven expansion  
**Status:** **Closed** — Phase 4 (local GPU) complete  

## Purpose

Same-run comparison under the frozen eval contract (dev split, **beam = 3**, lexicon on, normalization **v2**):

1. **Baseline:** M06 winning mix (`strict_plus_highconf_cap50.csv`) — 236 strict + 2 expansion  
2. **Candidate A:** `strict_plus_confv2_cap6.csv` — 236 strict + 6 expansion  
3. **Candidate B:** `strict_plus_confv2_cap10.csv` — 236 strict + 10 expansion  

## Commands

Exact copy-paste: **`M07_local_gpu_execution.md`**.

## Results

| Run | Train CSV | Model dir | Eval output dir | chrF (primary) | BLEU (secondary) |
|-----|-----------|-----------|-----------------|----------------|------------------|
| Baseline | `data/derived/selection/strict_plus_highconf_cap50.csv` | `outputs/m07_t5_baseline_m06_policy_a` | `outputs/eval_m07_baseline` | **52.2530** | *(see `metrics.json`)* |
| Cap6 | `data/derived/confidence/strict_plus_confv2_cap6.csv` | `outputs/m07_t5_cap6` | `outputs/eval_m07_cap6` | **45.4786** | *(see `metrics.json`)* |
| Cap10 | `data/derived/confidence/strict_plus_confv2_cap10.csv` | `outputs/m07_t5_cap10` | `outputs/eval_m07_cap10` | **45.6232** | *(see `metrics.json`)* |

**Best candidate vs baseline:** cap10 at **45.6232** → **Δ = −6.6298 chrF** vs baseline **52.2530**.

## Locked decision label

```text
M07 regression — additional expansion reintroduces noise
```

## Completion signal (paste-back)

```text
Baseline chrF: 52.2530
Cap6 chrF: 45.4786
Cap10 chrF: 45.6232
Best Δ vs baseline: -6.6298
Decision: M07 regression — additional expansion reintroduces noise
```

## Kaggle

**No M07 submission** (regression; discipline per `M07_plan.md` §11). No `M07_run3_kaggle_submit.md`.
