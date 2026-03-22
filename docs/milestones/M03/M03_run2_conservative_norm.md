# M03.2 — Run 2: Conservative normalization (v2)

**Date:** 2026-03-22  
**Plan context:** [M03_plan.md](M03_plan.md) · v1 postmortem: [M03_run1_normalization.md](M03_run1_normalization.md)

---

## Objective

Refine normalization to **reduce noise without changing token identity** vs M01 training (no **lowercase**, no **NFKC**).

---

## v2 definition (`NORMALIZATION_VERSION = "v2"`)

| Transform | v2 |
|-----------|-----|
| Noise removal (`…`, `„`, ZW*, BOM, WJ) | ✅ |
| Whitespace (NBSP → space, collapse) | ✅ |
| Immediate duplicate collapse (`len(token) ≥ 3`) | ✅ |
| NFKC | ❌ removed |
| Lowercase | ❌ removed |

**Code:** `src/akk2eng/data/normalize.py` · **Config:** `NORMALIZATION_VERSION = "v2"` in `config.py`.

---

## Metric comparison (beam=3, same checkpoint & split)

| Metric | Norm **OFF** | Norm **ON** (v2) | Δ |
|--------|--------------|------------------|---|
| **chrF** | **39.8601** | **39.8601** | **0** |
| **BLEU** | **43.0344** | **43.0344** | **0** |
| **low_overlap** | **26.92%** (42/156) | **26.92%** (42/156) | **0** |
| **numeric_errors** | **48.08%** (75/156) | **48.08%** (75/156) | **0** |
| **repetition** | **70.51%** (110/156) | **70.51%** (110/156) | **0** |
| **length_mismatch** | **41.03%** (64/156) | **41.03%** (64/156) | **0** |

**Interpretation:** On this dev split, v2 either leaves inputs **identical** to raw for almost all rows, or any edits are **tokenizer-invisible** for this model — so predictions and corpus metrics match **bit-for-bit** vs `--no-normalization`.

---

## Decision gates (M03.2 prompt)

| Gate | Result |
|------|--------|
| chrF ≥ **39.86** (beam baseline) | ✅ **Equal** |
| No degradation in overlap | ✅ **Unchanged** |

```
SUBMIT_TO_KAGGLE = NO
```

**Rationale:** Dev metrics are **flat** vs norm-off — there is **no new signal** that public LB would beat the current band; project discipline is to submit on **measured improvement**, not parity. **v2 remains the right default:** distribution-safe, **no harm** on dev, ready if noisier held-out lines benefit.

---

## Artifacts (gitignored)

| Path | Content |
|------|---------|
| `outputs/eval/m03_ablation_v2/metrics_norm_on_v2.json` | v2 ON |
| `outputs/eval/m03_ablation_v2/metrics_norm_off_v2.json` | OFF |
| `outputs/eval/m03_ablation_v2/predictions_norm_*_v2.csv` | paired preds |
| `outputs/analysis/m03_v2_norm_on/error_buckets.json` | ON buckets |
| `outputs/analysis/m03_v2_norm_off/error_buckets.json` | OFF buckets |

`outputs/eval/` after runs: re-synced with **normalization ON** (matches `USE_NORMALIZATION = True`).

---

## Stop condition

✅ Metrics recorded · ✅ Decision recorded · **STOP** (no Kaggle submit this step).

---

## Strategic note

v1 proved **aggressive** normalization hurts alignment. v2 **restores** the beam baseline on dev while keeping a **hook** for rare noise (ellipsis, invisible chars, duplicate tokens) on messier inputs — **train/inference alignment preserved**.
