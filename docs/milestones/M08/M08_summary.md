# 📌 Milestone Summary — M08: Alignment-quality recovery

**Project:** akk2eng  
**Milestone:** M08 — Alignment-quality recovery  
**Baseline:** M07 closeout (`v0.0.10-m07`)  
**Status:** **Closed (regression — high-value negative result)**  
**Release tag:** `v0.0.11-m08`  
**Closeout artifacts:** [M08_audit.md](M08_audit.md), this file; runs: [M08_run1_alignment_quality_builder.md](M08_run1_alignment_quality_builder.md), [M08_run2_training_eval.md](M08_run2_training_eval.md), [M08_run3_ci.md](M08_run3_ci.md)

---

## 1. Overview

M08 implemented a deterministic **alignment-quality v2** layer: strict M04 alignment unchanged, then **narrow** `;` / `:` clause resplit repair only for **count mismatch** `na == ne + 1` with anchors found — **no** partial-prefix, relaxed rows, publications, or further M05 pool scoring. A locked **3-run GPU matrix** compared the M06 Policy A baseline rerun vs repaired training CSVs.

**Outcome:** structurally valid **+46** recovered sentence pairs were added to strict training, but dev **chrF collapsed** to **~20.0** vs the same-run baseline **52.2530** (**~−32.2 chrF**). **No Kaggle submission.**

---

## 2. Dataset composition

| Variant | Strict rows | Recovered / repair rows | Total training rows (typical) |
|---------|------------:|-------------------------:|------------------------------:|
| M06 baseline (Policy A) | 236 | 2 (proven expansion) | **238** |
| Candidate A (quality v2) | 236 | **46** (full-sentence repair) | **282** |
| Candidate B (A ∪ M06 winners) | — | Union of A + locked 2 M06 IDs | **282** (same chrF as A this run) |

Builder audit and hashes: **`M08_run1_alignment_quality_builder.md`** + local `data/derived/alignment_quality/*.json` (gitignored).

---

## 3. Results table (frozen dev, same-run)

| Run | Dataset | chrF |
|-----|---------|------|
| Baseline | `strict_plus_highconf_cap50.csv` | **52.2530** |
| Candidate A | `aligned_train_sentences_quality_v2_split.csv` | **20.0045** |
| Candidate B | `aligned_train_sentences_quality_v2_plus_m06.csv` | **20.0045** |

**Best Δ vs baseline:** **−32.2485** chrF.

---

## 4. Interpretation

- **Alignment repair ≠ usable supervision.** Rows can be structurally correct (full-sentence, count-matched, filtered) yet **harm** the continuation model when mixed into the M06-optimum regime.
- **Distribution mismatch** between recovered clauses and the **narrow** supervision distribution the model already adapted to likely dominates naive “more clean sentences.”
- **M06 optimum remains unmatched**; M07 and M08 together show that neither **scoring-widened expansion** nor **structural alignment repair** safely improves this stack without a different integration strategy.

### Required statement

```text
Structural correctness alone is insufficient; recovered rows must match the training distribution or they degrade performance.
```

---

## 5. Comparison vs M06 and M07

| | M06 Policy A | M07 cap10 | M08 Candidate A |
|--|--------------|-----------|-----------------|
| Mechanism | 236 strict + **2** gated expansion | +8 more expansion vs baseline | 236 strict + **46** repaired full sentences |
| vs same-run baseline | **+6.89** chrF vs aligned control | **~−6.6** chrF vs M06 rerun | **~−32.2** chrF vs M06 rerun |
| Lesson | Tiny clean add helps | Slightly more pool rows hurt | Many “clean” repaired rows **catastrophically** hurt |

---

## 6. Key insight

> **Structural correctness of labels is not sufficient** for low-resource continuation FT when the effective training mixture shifts away from the model’s **learned, narrow optimum**.

---

## 7. Conclusion block

```text
M08 demonstrates that structurally correct sentence alignment does not guarantee
useful supervision for model training.

Despite recovering 46 full-sentence pairs via deterministic repair,
model performance collapsed (~−32 chrF), indicating a strong distribution mismatch.

This confirms that the bottleneck is not alignment correctness, but how the model
learns from and integrates supervision.
```

---

## 8. Next direction

**M09** — pivot to **training dynamics**, **curriculum / integration**, and **model-side control** of how supervision is absorbed — **not** further alignment repair, selection scoring, or recall-first data widening. Seed: [../M09/M09_plan.md](../M09/M09_plan.md).

**Do not begin M09 implementation** until a new branch and plan are explicitly opened post-closeout.
