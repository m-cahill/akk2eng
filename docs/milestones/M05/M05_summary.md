# M05 — Summary (closeout)

Formal closure of **Milestone M05** — alignment expansion / data augmentation for `akk2eng`.

**Audit:** [M05_audit.md](M05_audit.md)  
**Release tag:** `v0.0.8-m05`

---

## Overview

### Purpose

Expand **sentence-aligned** supervision beyond M04 strict pairs using only the official train split + `Sentences_Oare_FirstWord_LinNum.csv`, with split-safe enforcement, provenance tags, and deterministic artifacts—then measure dev chrF vs the M04-validated baseline and a **same-run** aligned-only control.

### What was implemented

| Component | Role |
|-----------|------|
| `src/akk2eng/data/augmentation.py` | Expansion engine (relaxed anchors, English `;` resplit, partial prefix), report + CSV hashes |
| `python -m akk2eng.pipeline.augment --split-safe` | Builds `augmented_train_sentences.csv` + `augmentation_report.json`; dev overlap check |
| `src/akk2eng/data/alignment.py` | `align_document_sentences_strict`, `tokenize_transliteration_text` (hooks for M05) |
| `src/akk2eng/config.py` | Default paths under `data/derived/augmentation/` |
| Tests | `tests/test_m05_augmentation.py` + fixtures |
| Docs | `M05_plan.md`, `M05_run1_augmentation_builder.md`, `M05_run2_training_eval.md`, `M05_local_gpu_execution.md` |

Methods 2–3 (back-translation, noise) were **deferred** by design.

---

## Dataset (split-safe builder)

| Metric | Value |
|--------|--------|
| Strict (`direct_aid_strict`) rows | **236** |
| Expansion-only rows | **306** |
| **Total** | **542** |
| Dev `oare_id` overlap | **0** |

**By `augmentation_type` (row counts):** `direct_aid_strict` 236; `expanded_partial_prefix` 296; `expanded_partial_prefix_relaxed` 8; `expanded_english_resplit` 2.

Details: [M05_run1_augmentation_builder.md](M05_run1_augmentation_builder.md).

---

## Key result (GPU, 3 epochs, frozen dev)

Eval contract: beam=3, lexicon on, normalization v2 (same as M02/M04).

| Run | chrF | BLEU |
|-----|------|------|
| M04 baseline (historical split-safe aligned) | **~43.34** | — |
| **M05 control** (236-row split-safe aligned, same run) | **45.3584** | 63.8998 |
| **M05 augmented** (542-row expanded CSV) | **20.3932** | 12.7255 |

**Δ (augmented − control):** **≈ −24.97 chrF**.

Control > historical M04 pin is consistent with **run-to-run / environment variance** on GPU fine-tuning; the milestone discriminator remains **augmented vs same-run control**.

---

## Conclusion

```text
M05 did not improve performance. Mixing a large block of partial-prefix and other
expansion rows with high-confidence strict pairs degraded dev chrF catastrophically
vs the same-run aligned-only control.
```

**Insight:** For this task, **precision of supervision beats naive recall**. Alignment expansion without **quality gating or weighting** is harmful.

---

## Submission

**No Kaggle submission** (augmented path regressed; discipline preserved).

---

## Handoff

**Next:** [../M06/M06_plan.md](../M06/M06_plan.md) — precision-preserving data strategies (quality gates, selective inclusion, or weighted training)—**not** started in M05 closeout.
