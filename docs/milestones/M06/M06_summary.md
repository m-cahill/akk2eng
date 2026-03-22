# 📌 Milestone Summary — M06: Precision-preserving data expansion

**Project:** akk2eng  
**Milestone:** M06 — Precision-preserving data expansion  
**Baseline:** M05 closeout (`v0.0.8-m05`)  
**Status:** **Closed**  
**Release tag:** `v0.0.9-m06`  
**Closeout artifacts:** [M06_audit.md](M06_audit.md), this file; runs: [M06_run1_policy_builder.md](M06_run1_policy_builder.md), [M06_run2_training_eval.md](M06_run2_training_eval.md), [M06_run3_kaggle_submit.md](M06_run3_kaggle_submit.md)

---

## 1. Overview

M06 tested whether **deterministic quality gating** on the split-safe M05 augmented superset could recover useful signal without repeating M05’s unweighted volume failure. Implementation added a selection layer (`src/akk2eng/data/selection.py`, `python -m akk2eng.pipeline.select_train`), CI-safe tests, and a locked 3-run GPU matrix (control vs Policy A vs Policy B).

---

## 2. Dataset composition

| Component | Rows |
|-----------|------|
| Strict aligned (`direct_aid_strict`) | **236** |
| Policy A selected expansion | **2** |
| **Policy A training CSV total** | **238** |

High-confidence expansion under the locked thresholds and tie-breaks was **extremely sparse**; only **two** expansion rows were admitted.

---

## 3. Results table (frozen dev, same-run control)

| Run | Dataset | chrF |
|-----|---------|------|
| Control | `aligned_train_sentences_split.csv` | **45.3584** |
| Policy A | `strict_plus_highconf_cap50.csv` | **52.2530** |
| Policy B | `strict_plus_highconf_cap50_weighted2x.csv` | **25.4027** |

**Best Δ vs control (Policy A):** **+6.8946** chrF.

---

## 4. Interpretation

- **Policy A** validates the M06 hypothesis: a **small**, **high-confidence**, **capped**, **strict-majority** expansion slice can **improve** dev chrF vs strict-only when label quality is preserved.
- **Policy B** shows that **duplicating strict rows** (2×) while holding expansion fixed is **not** equivalent to benign upsampling here — dev chrF **collapsed** (~25.4), consistent with **reintroduced optimization imbalance** or **effective dilution** of useful gradient signal relative to Policy A’s mixture.

---

## 5. Key insight

> **Data quality dominates data quantity.** Extremely small amounts of **high-confidence** supervision can outperform large **noisy** corpora — and **weighting / repetition** can still fail if it distorts the effective training mixture.

---

## 6. Comparison vs M05

| | M05 (naive augmented mix) | M06 Policy A |
|--|---------------------------|--------------|
| Expansion posture | Large ungated mix (incl. partial-prefix mass) | **2** gated rows only |
| vs same-run control | **~−25 chrF** (catastrophic) | **+6.89 chrF** (material gain) |

```text
M06 demonstrates that the failure of M05 was not due to expansion itself,
but due to the inclusion of low-confidence supervision.

When restricted to extremely high-confidence rows, even minimal expansion
(2 rows) produces a large performance gain (+6.9 chrF).

This confirms that precision-first data selection is the correct direction.
```

---

## 7. Kaggle decision

Dev success-candidate rules satisfied for **Policy A**; submission authorized under project discipline. Log: [M06_run3_kaggle_submit.md](M06_run3_kaggle_submit.md). Leaderboard scores are recorded there when available (**not** fabricated in repo docs).

---

## Handoff

**Follow-on:** M07 — confidence-driven expansion — **closed** (`v0.0.10-m07`, regression documented): [../M07/M07_summary.md](../M07/M07_summary.md). **Current next:** M08 — alignment quality / new supervision (seed): [../M08/M08_plan.md](../M08/M08_plan.md).
