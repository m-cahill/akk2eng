# M02 — Summary (closeout)

Formal closure of **Milestone M02** — evaluation harness, error analysis, controlled decoding experiments, and lexicon validation — for the `akk2eng` project.

**Audit:** [M02_audit.md](M02_audit.md)  
**Release tag:** `v0.0.5-m02`

---

## Overview

### What M02 set out to do

- Establish a **measurement-first** dev loop: fixed **90/10 split** (seed **42**), persisted splits, reproducible metrics.
- Enable **targeted improvement** via error bucketing (not guesswork).
- Improve translation quality where **decoding** was the limiter (repetition, length drift) without retraining the baseline checkpoint.
- Validate **lexicon post-processing** as a surgical lever for leaked transliteration surfaces.

### What was built

| Area | Deliverable |
|------|-------------|
| **Eval** | `python -m akk2eng.pipeline.eval` — chrF (primary), BLEU (secondary), `predictions_dev.csv`, `metrics.json`, `eval_summary.txt`, experiment snapshots under `outputs/experiments/exp_<UTC>/` |
| **Analysis** | `python -m akk2eng.pipeline.analyze_errors` — buckets: repetition, length_mismatch, low_overlap, empty, numeric_errors |
| **Decoding** | `config.py`-driven `repetition_penalty`, `no_repeat_ngram_size`, `num_beams`; recorded in eval artifacts |
| **Lexicon (M02-D)** | Train-filtered eBL `form → lexeme`, boundary-safe replacement on **predictions only**; flags in `metrics.json` / experiment `config.json` |

---

## Key results

### Public leaderboard (Kaggle)

| Anchor | Score (public LB) | Notes |
|--------|-------------------|--------|
| **M01 baseline** | **11.9** | Documented in `docs/milestones/M01/M01_run3.md` |
| **M02 band** | **~11.6–11.9** | Greedy decode with repetition control showed **dip vs 11.9** at penalty 1.2 (see `M02_run2_local_refinement.md`); beam-aligned runs reported **~11.6** in project logs — **not** a sustained beat of 11.9 |

*The competition metric is **not** reproduced locally; dev chrF/BLEU are **proxy** signals.*

### Dev metrics (156 dev rows, sacrebleu 2.6.0, same frozen split)

| Stage | chrF | Notes |
|-------|------|--------|
| M02-A/B baseline (pre–M02-C) | **18.65** | Starting point for decoding work |
| M02-C (`repetition_penalty` 1.2, greedy) | **34.41** | Large chrF jump |
| M02-C.2 (penalty **1.1**, greedy) | **42.82** | **Peak chrF** in the decoding series |
| M02-C.3 (beam **3**, penalty 1.1) | **39.86** | BLEU ↑ vs greedy; chrF ↓; tradeoff documented in `M02_run3_local_beam.md` |

### Repetition reduction

- Repetition bucket (repeat-bigram heuristic): **87.8% → 73.7%** with penalty **1.2** vs pre–M02-C baseline (`M02_run1_m02c_decoding.md`).
- Further tuning to **1.1** improved chrF/overlap vs 1.2 locally; repetition bucket ~74% (`M02_run2_local_refinement.md`).

### Beam / lexicon findings

- **Beam (`num_beams=3`):** Strong **BLEU** lift vs greedy at same penalty; **chrF** lower than greedy@1.1 peak; length_mismatch and low_overlap buckets shifted (see `M02_run3_local_beam.md`).
- **Lexicon (M02-D):** Implementation **validated**; on archived dev predictions vs beam run, **0 / 156** rows changed — **no** standalone lexicon `form` tokens in English outputs, so **no dev metric effect** (`M02_run4_lexicon.md`). Pipeline remains safe for future leakage on held-out text.

---

## Experiment timeline

| ID | Focus | Doc |
|----|--------|-----|
| **M02-C** | `repetition_penalty=1.2`, `no_repeat_ngram_size=3`, greedy | [M02_run1_m02c_decoding.md](M02_run1_m02c_decoding.md) |
| **M02-C.2** | Penalty **1.2 → 1.1** (single variable) | [M02_run2_local_refinement.md](M02_run2_local_refinement.md) |
| **M02-C.3** | **`num_beams=3`** vs greedy@1.1 | [M02_run3_local_beam.md](M02_run3_local_beam.md) |
| **M02-D** | Lexicon post-process on predictions | [M02_run4_lexicon.md](M02_run4_lexicon.md) |

Kaggle alignment / submit logging: [M02_run2_kaggle.md](M02_run2_kaggle.md) (template + checklist).

---

## Key insights (critical)

1. **Dev metric ≠ Kaggle metric** — chrF/BLEU on dev are useful for **ordering experiments** and catching regressions; they do **not** equal the public score. Submits must be **disciplined** and logged.
2. **Repetition was the dominant visible failure mode** early in M02 — **repetition controls** addressed it materially on dev buckets and output quality.
3. **Lexicon did not activate on dev** — no token leakage matching the safe replacement patterns; the lever is **ready** but **not** a current differentiator.
4. **Plateau with decoding** — further **decode-only** tweaks are unlikely to overcome **data / transliteration noise** without **normalization** or **training/data** changes.

---

## Final state

### Best known config (repo defaults at M02 close)

- **Weights:** `outputs/m01_t5` (unchanged since M01 fine-tune for this line of work).
- **Decoding:** `do_sample=False`, `repetition_penalty=1.1`, `no_repeat_ngram_size=3`, `num_beams=3`, `max_new_tokens=256` (`src/akk2eng/config.py`; `model.py` consumes these).
- **Lexicon:** `USE_LEXICON=True` by default; train-filtered map; **no-op** when predictions contain no matching forms.
- **Splits:** `data/splits/train_split.csv`, `dev_split.csv` (seed 42, 90/10).

### Stable pipeline

- `pipeline.eval` + `pipeline.analyze_errors` + `pipeline.run` form a **closed, auditable** loop.
- Run log: [M02_toolcalls.md](M02_toolcalls.md).

---

## Handoff to M03

**Conclusion:** M02 objectives for **measurement, analysis, and decoding exploration** are met. **Next gains** require **transliteration normalization / preprocessing** and broader **data pipeline** work — see [../M03/M03_plan.md](../M03/M03_plan.md).
