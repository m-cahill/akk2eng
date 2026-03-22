# 🧾 Milestone Audit — M07: Confidence-driven expansion

**Audit mode:** DELTA AUDIT  
**Milestone ID:** M07  
**Release tag:** `v0.0.10-m07`  
**Repository state:** merge `m07-confidence-driven-expansion` → `main` at closeout  

**Summary:** [M07_summary.md](M07_summary.md)  
**Plan:** [M07_plan.md](M07_plan.md)

---

## 1. Governance integrity

| Rule | Status |
|------|--------|
| Split-safe data only | ✅ |
| Dev overlap = 0 | ✅ (fail-closed in builder + verified on outputs) |
| Same-run baseline (M06 Policy A) | ✅ |
| No mid-run tuning | ✅ (scorer frozen before GPU; caps per plan) |
| Deterministic scoring (`confidence_v2`) | ✅ (`confidence.py` + tests + hashed reports) |
| No weighting / duplication used | ✅ |
| CI-safe phases complete before GPU | ✅ |

**Violations:** none identified at closeout.

---

## 2. Core finding (interpretation — CRITICAL)

> Adding even a small number of additional expansion rows (cap6/cap10) degrades performance significantly (~**−6.6 chrF** vs the same-run M06 Policy A baseline).

### Required statement

```text
The M06 optimum is extremely narrow and fragile; additional expansion reintroduces noise even under improved scoring.
```

### Interpretation

- M06 success does **not generalize** to “M06 winners + a few more” from the same augmented pool.
- **`confidence_v2` scoring is insufficient** to recover additional **usable** expansion rows at this scale.
- The useful expansion signal is **extremely sparse and not reliably separable** from harmful rows using the current features and pool.

---

## 3. Why this is a high-value failure

- **Same-run baseline** isolates the effect of changing only the training CSV (continuation from `outputs/m01_t5`, identical eval contract).
- **Controlled caps (6 / 10 expansion rows)** show the failure is **not** explained by M05-style bulk volume; the regression appears with **only a handful** of extra rows.
- **Deterministic scoring** eliminates ad hoc “heuristic drift” in selection — the negative result is **reproducible and auditable**, not a tuning artifact.
- **Clear causal signal:** additional selected rows → **immediate** dev chrF collapse vs the M06 optimum.
- **Prevents wasted effort** on iterative confidence tuning atop the same split-safe augmented pool without changing alignment or supervision sources.

```text
This milestone conclusively shows that confidence-based selection alone cannot expand beyond the M06 optimum.
```

---

## 4. Delta scope (what changed)

| Area | Change |
|------|--------|
| Code | `src/akk2eng/data/confidence.py`, `src/akk2eng/pipeline/select_confident_train.py`, `config.py` confidence output defaults |
| Tests | `tests/test_m07_confidence.py`, `tests/fixtures/m07_confidence/` |
| Docs | M07 plan, runbooks, summary, audit, tool log |
| Data contract | Gitignored `data/derived/confidence/*` produced locally |

---

## 5. Results (evidence)

| Run | chrF |
|-----|------|
| Baseline (M06 Policy A CSV) | **52.2530** |
| Cap6 | **45.4786** |
| Cap10 | **45.6232** |

**Best Δ vs baseline:** **−6.6298** (cap10 vs baseline).  
**Decision:** `M07 regression — additional expansion reintroduces noise` — [M07_run2_training_eval.md](M07_run2_training_eval.md).

---

## 6. Kaggle

**No submission** for M07. **No** `M07_run3_kaggle_submit.md`.

---

## 7. CI / quality gate

At closeout: **`pytest tests`** and **`ruff check src tests`** expected green on merged `main` after push.

---

## 8. Audit conclusion

M07 **closed honestly** as a **regression milestone** with **full governance**: constraints held, artifacts and hashes recorded, and the negative outcome **documented as a hard pivot signal**. **Do not** pursue further expansion/scoring iteration on this pool without **alignment or supervision changes** — see **M08** seed plan.
