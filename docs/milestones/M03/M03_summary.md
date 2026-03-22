# M03 — Summary (closeout)

Formal closure of **Milestone M03** — normalization engine for the `akk2eng` project.

**Audit:** [M03_audit.md](M03_audit.md)  
**Release tag:** `v0.0.6-m03`

---

## Overview

### Purpose

Improve translation **input hygiene** before tokenization by adding a deterministic **normalization layer** at inference time, without retraining the M01 checkpoint — testing whether surface cleanup could raise dev chrF / reduce error buckets before investing in heavier data work.

### What was implemented

| Component | Role |
|-----------|------|
| `src/akk2eng/data/normalize.py` | `normalize_transliteration()` — stdlib-only, deterministic |
| `run_inference()` | Single integration point: eval (`pipeline.eval`), submission (`pipeline.run`) |
| `config.py` | `USE_NORMALIZATION`, `NORMALIZATION_VERSION` |
| `pipeline.eval` / `pipeline.run` | `--no-normalization` for A/B |
| Artifacts | `normalization: { enabled, version }` in `metrics.json` and experiment `config.json` |

### Where applied

**Inference-time only** — transliteration column **before** `T5BaselineTranslator.translate()`. **Not** applied to English references or to model outputs (would corrupt metrics).

---

## Implementation (technical)

- **v1:** noise strip → NFKC → lowercase → whitespace → immediate duplicate collapse (`len(token) ≥ 3`); hyphens preserved.
- **v2:** noise strip → whitespace → duplicate collapse only (**no NFKC, no lowercase**).

CLI mirrors config defaults; overrides are explicit (`--no-normalization`).

---

## Results (measured, beam=3, `outputs/m01_t5`, dev n=156)

| Variant | chrF (vs norm OFF) | Outcome |
|---------|-------------------|---------|
| **v1** | **37.64** vs **39.86** (↓) | **Harmful** — train/inference distribution mismatch |
| **v2** | **39.8601** vs **39.8601** (=) | **Neutral** — identical chrF, BLEU, and error buckets vs `--no-normalization` |

Run logs: [M03_run1_normalization.md](M03_run1_normalization.md), [M03_run2_conservative_norm.md](M03_run2_conservative_norm.md).

---

## Key findings (critical)

1. **Aggressive normalization (v1)** — lowercasing + NFKC — **breaks alignment** with the surface forms seen during M01 fine-tuning; dev **chrF regressed**, **low_overlap worsened**, even though **repetition** and **BLEU** moved favorably for some settings.
2. **Conservative normalization (v2)** is **distribution-safe** on the frozen dev split: **metric parity** with norm-off — no harm, no measured lift on this corpus.
3. The baseline model is already **tolerant** of typical whitespace in dev rows; rare noise characters and duplicate-token patterns did not change aggregate behavior in v2 A/B.
4. **Normalization alone** is **not** a primary optimization lever at this stage; breaking the public LB plateau requires **structural data work** (next: **M04**).

---

## Final state (repo defaults)

| Setting | Value |
|---------|--------|
| `NORMALIZATION_VERSION` | **`v2`** |
| `USE_NORMALIZATION` | **`True`** |
| Policy | v2 retained as **safe default** — handles invisible/stray characters without altering token identity |

---

## Conclusion

```
M03 complete.
Normalization validated as safe but not a primary optimization lever.
Next gains require structural data improvements (M04).
```

**Handoff:** [../M04/M04_plan.md](../M04/M04_plan.md)
