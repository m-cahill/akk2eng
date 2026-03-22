# 📌 Milestone Summary — M07: Confidence-driven expansion

**Project:** akk2eng  
**Milestone:** M07 — Confidence-driven expansion  
**Baseline:** M06 closeout (`v0.0.9-m06`)  
**Status:** **Closed (regression — high-value negative result)**  
**Release tag:** `v0.0.10-m07`  
**Closeout artifacts:** [M07_audit.md](M07_audit.md), this file; runs: [M07_run1_confidence_builder.md](M07_run1_confidence_builder.md), [M07_run2_training_eval.md](M07_run2_training_eval.md)

---

## 1. Overview

M07 tested whether a **deterministic `confidence_v2` rescoring layer** on the split-safe M05 augmented pool could admit **a few additional high-quality expansion rows** beyond the M06 Policy A optimum (**236 strict + 2 expansion**) without reintroducing M05-style noise. Implementation delivered the scorer, builder CLI, hashed reports, CI-safe tests, and a locked **3-run GPU matrix** (baseline rerun vs cap6 vs cap10).

**Outcome:** both candidates **regressed sharply** vs the same-run baseline (~**−6.6 chrF** at best). **No Kaggle submission.**

---

## 2. Dataset composition

| Variant | Strict rows | Expansion rows | Total training rows |
|---------|------------:|----------------:|--------------------:|
| M06 baseline (Policy A) | 236 | 2 | 238 |
| Candidate A (`strict_plus_confv2_cap6`) | 236 | 6 | 242 |
| Candidate B (`strict_plus_confv2_cap10`) | 236 | 10 | 246 |

Builder artifacts and dev overlap **0** are recorded in [M07_run1_confidence_builder.md](M07_run1_confidence_builder.md).

---

## 3. Results table (frozen dev, same-run)

| Run | Dataset | chrF |
|-----|---------|------|
| Baseline | `strict_plus_highconf_cap50.csv` | **52.2530** |
| Cap6 | `strict_plus_confv2_cap6.csv` | **45.4786** |
| Cap10 | `strict_plus_confv2_cap10.csv` | **45.6232** |

**Best Δ vs baseline (least-negative candidate, cap10):** **−6.6298** chrF.

**Decision:** `M07 regression — additional expansion reintroduces noise` (see [M07_run2_training_eval.md](M07_run2_training_eval.md)).

---

## 4. Interpretation

- Adding **even a small number** of additional expansion rows (**+4** or **+8** beyond the M06 pair) **degrades** dev chrF **substantially** under an unchanged training/eval contract.
- M06’s **+6.9 chrF** gain from **exactly two** gated rows **does not generalize** to “two plus a few more” selected by improved scoring.
- **`confidence_v2` is insufficient** to recover additional rows that are **training-safe** at this resolution; the useful expansion signal remains **extremely sparse and not reliably separable** from harmful partial-prefix mass.

### Required statement

```text
The M06 optimum is extremely narrow and fragile; additional expansion reintroduces noise even under improved scoring.
```

---

## 5. Comparison vs M06

| | M06 Policy A | M07 cap6 / cap10 |
|--|--------------|------------------|
| Expansion posture | **2** rows only | **6** / **10** rows (includes M06 winners + extras) |
| vs same-run baseline in milestone | **+6.89 chrF** vs aligned control | **~−6.6 chrF** vs M06 Policy A rerun |
| Mechanism | Threshold + cap + type gate | Deterministic `confidence_v2` + tiny caps |

M06 showed that **tiny** clean expansion can **help**; M07 shows that **slightly more** expansion from the **same pool**, even with **better scoring**, **hurts**.

---

## 6. Key insight

> **The M06 optimum is a razor-thin regime.** Confidence-based selection **alone** cannot safely widen the expansion set using the current augmented pool; label noise returns **immediately** once the set grows.

---

## 7. Conclusion block

```text
M07 demonstrates that the improvement observed in M06 is not extendable
through additional data selection, even with improved confidence scoring.

The beneficial signal in expansion data is extremely sparse and fragile,
and cannot be reliably increased using current heuristics.

Future progress requires improving alignment quality or introducing new
sources of high-confidence supervision, not expanding the existing pool.
```

---

## 8. Next direction

**M08** — pivot away from expansion/scoring iteration: **alignment quality**, **new high-confidence supervision**, **structural pipeline improvements** — not more confidence tuning or recall-first expansion on the same M05 pool. Seed: [../M08/M08_plan.md](../M08/M08_plan.md).

**Do not begin M08 implementation** until a new branch and plan are explicitly opened post-closeout.
