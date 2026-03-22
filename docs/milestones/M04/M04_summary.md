# M04 — Summary (closeout)

Formal closure of **Milestone M04** — sentence alignment for the `akk2eng` project.

**Audit:** [M04_audit.md](M04_audit.md)  
**Release tag:** `v0.0.7-m04`

---

## Overview

### Purpose

Resolve the **document-level train** vs **sentence-level test** granularity mismatch by deriving deterministic, auditable **sentence-aligned** `(transliteration, translation)` pairs from official training data and the sentence-aid file, then measuring whether **alignment-only** fine-tuning improves dev chrF under the frozen M02 evaluation contract.

### What was implemented

| Component | Role |
|-----------|------|
| `src/akk2eng/data/alignment.py` | Deterministic alignment engine, line-number parsing, pairing, reporting, **`verify_aligned_no_dev_oare_overlap()`** |
| `python -m akk2eng.pipeline.align` | Build `aligned_train_sentences.csv` + `alignment_report.json`; **`--split-safe`** uses **`train_split.csv` only** and enforces **zero `oare_id` overlap** with `dev_split.csv` |
| `src/akk2eng/config.py` | Paths for derived alignment artifacts (full-train vs split-safe CSV/report) |
| `python -m akk2eng.pipeline.mix_train` | **Mixed corpus** (full `train.csv` + aligned rows) — explored; **not** the validated primary outcome |
| `python -m akk2eng.pipeline.train` | Multi `--train-csv` / aligned paths for continuation from `outputs/m01_t5` |
| Tests | `tests/test_m04_alignment.py`, `tests/test_m04_split_leakage.py` + synthetic fixtures |

### Derived data contract (local, gitignored)

| Artifact | Meaning |
|----------|---------|
| `data/derived/alignment/aligned_train_sentences.csv` | Sentence pairs from **full** `train.csv` (legacy / experiments) |
| `data/derived/alignment/alignment_report.json` | Coverage, skip reasons, method counts, **SHA-256** of aligned CSV |
| `data/derived/alignment/aligned_train_sentences_split.csv` | **Leak-safe** pairs: alignment input = **`data/splits/train_split.csv` only** |
| `data/derived/alignment/alignment_report_split.json` | Report for split-safe build |

**Hard rule for honest dev eval:** use **`--split-safe`** (or equivalent paths) so alignment is never built from documents that appear in the dev holdout.

---

## Key result (validated, no leakage)

| Metric | Value |
|--------|--------|
| **Baseline** (frozen dev, `outputs/m01_t5`, beam=3, lex on, norm v2) | chrF **~39.8601** |
| **Leakage-free aligned run** (`aligned_train_sentences_split.csv`, 3 epochs, split-safe build) | chrF **~43.34** |
| **Δ chrF** | **+3.48** |
| **Dev overlap check** | **`n_overlap_oare_ids = 0`** (`passes: true`) |

Run detail: [M04_run3_training_eval.md](M04_run3_training_eval.md) — section **Leakage-fixed run — aligned-only (train_split)**.

---

## Leakage discovery and resolution

An initial **3-epoch** run using alignment built from **full** `train.csv` showed **~52.25 chrF** — **not trustworthy** for generalization because **dev `oare_id`s could appear** in alignment supervision (train/dev document overlap).

After enforcing **split discipline** (`--split-safe`), the headline gain **stabilized at +3.48 chrF** — a **real, audited** improvement consistent with high-signal sentence supervision **without** train/dev contamination.

---

## Interpretation

1. **Sentence-aligned supervision materially improves** dev chrF vs the document-only baseline **when evaluation is clean**.
2. This **confirms the system-design thesis** in `docs/moonshot.md`: **structural data alignment** can outperform ad-hoc model/decoding tweaks in this low-resource setting.
3. **Mixed training** (full corpus + aligned) was run in early experiments; under the same short budgets it **did not** beat baseline — **weighting / integration** is **deferred** (future milestone), not M04’s validated win.

---

## Submission

**No Kaggle submission** was required for M04 closeout; dev gain is **validated locally** with split integrity. Optional **GPU parity** re-run is documented as follow-up (see audit **Deferred**).

---

## Conclusion

```
M04 complete.
Sentence alignment shipped, tested, and leak-checked.
Validated dev chrF gain: +3.48 vs ~39.86 baseline (split-safe aligned-only).
```

**Handoff:** [../M05/M05_plan.md](../M05/M05_plan.md)
