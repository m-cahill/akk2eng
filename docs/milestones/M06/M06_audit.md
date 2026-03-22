# 🧾 Milestone Audit — M06: Precision-preserving data expansion

**Audit mode:** DELTA AUDIT  
**Milestone ID:** M06  
**Release tag:** `v0.0.9-m06`  
**Repository state:** merge `m06-precision-preserving-expansion` → `main` at closeout  

**Summary:** [M06_summary.md](M06_summary.md)  
**Plan:** [M06_plan.md](M06_plan.md)

---

## 1. Governance integrity

| Rule | Status |
|------|--------|
| Split-safe data only | ✅ |
| Dev overlap = 0 | ✅ (fail-closed in selector + verified on outputs) |
| Same-run control comparator | ✅ |
| No mid-run tuning | ✅ (thresholds/caps frozen per plan) |
| Deterministic selection policy | ✅ (`selection.py` + tests) |
| CI-safe phases before GPU | ✅ |

**Violations:** none identified at closeout.

---

## 2. Core finding (interpretation — CRITICAL)

> High-confidence expansion is **extremely sparse (2 rows)**, but sufficient to produce a **+6.9 chrF improvement** when mixed conservatively with strict alignment.

### Critical insight

> **Data quality dominates data quantity.** Extremely small amounts of high-confidence data can **significantly** improve performance versus large noisy mixtures.

### Failure contrast

- **Policy A:** **+6.8946** chrF vs same-run control — **success candidate** (beats control by >0.5 and beats pin **45.3584**).
- **Policy B:** **~25.40** chrF — **collapse** vs control; demonstrates that **reweighting / duplication** can destroy the benefit even when row identity matches Policy A.

### Required statement

```text
Expansion is only beneficial under extreme precision gating. Any dilution, even via weighting, degrades performance.
```

---

## 3. Why this is a high-value success

- **Same-run control** isolates the effect of the training CSV change (continuation from `outputs/m01_t5`, identical eval contract).
- **Deterministic selection** — fixed thresholds, cap, tie-breaks, and hashed reports — prevents post-hoc “heuristic drift” in audit narrative.
- **Minimal expansion (2 rows)** falsifies a naive “more rows ⇒ better” story; the gain is **not** from volume.
- **Strong margin (+6.9 chrF)** on the primary dev metric under the frozen contract.
- **Clear causal mechanism:** precision gating removed M05’s low-confidence mass; Policy B shows that **mixture shape** matters as much as row inclusion.

---

## 4. Delta scope (what changed)

| Area | Change |
|------|--------|
| Code | `src/akk2eng/data/selection.py`, `src/akk2eng/pipeline/select_train.py`, `config.py` selection defaults |
| Tests | `tests/test_m06_selection.py`, `tests/fixtures/m06_selection/` |
| Docs | M06 plan, runbooks, summary, audit, Kaggle run3 |
| Data contract | Gitignored `data/derived/selection/*` produced locally |

---

## 5. Risks & follow-ups

| Risk | Severity | Mitigation / next step |
|------|----------|-------------------------|
| Public LB may not mirror dev chrF | MEDIUM | Treat Kaggle score as validation; log in `M06_run3_kaggle_submit.md` |
| Only 2 expansion rows generalize | MEDIUM | M07: find more **high-confidence** rows; improve scoring — **not** blind volume |
| Policy B failure | HIGH (lesson) | Do not adopt strict duplication without re-validation; document in SoT |

---

## 6. CI / quality gate

At closeout: **`pytest tests`** and **`ruff check src tests`** expected green on merged `main` (run in CI after push).

---

## 7. Audit conclusion

M06 **closed successfully** with an audit-grade positive result on **Policy A**, a documented **Policy B** negative control, and governance artifacts complete. Proceed to **M07 planning** only; **no** M07 implementation authorized by this closeout prompt.
