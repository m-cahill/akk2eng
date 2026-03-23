# 🧾 Milestone Audit — M08: Alignment-quality recovery

**Audit mode:** DELTA AUDIT  
**Milestone ID:** M08  
**Release tag:** `v0.0.11-m08`  
**Repository state:** merge `m08-alignment-quality-recovery` → `main` at closeout  

**Summary:** [M08_summary.md](M08_summary.md)  
**Plan:** [M08_plan.md](M08_plan.md)

---

## 1. Governance integrity

| Rule | Status |
|------|--------|
| Split-safe data only | ✅ |
| Dev overlap = 0 | ✅ (fail-closed in builder + verified on outputs) |
| Same-run baseline (M06 Policy A) | ✅ |
| No mid-run tuning | ✅ (repair rules frozen before GPU; locked 3-run matrix) |
| Deterministic alignment repair | ✅ (`alignment_quality.py` + tests + hashed reports) |
| No partial-prefix / relaxed rows used | ✅ |
| CI-safe phases completed before GPU | ✅ |

**Violations:** none identified at closeout.

---

## 2. Core finding (interpretation — CRITICAL)

> Alignment repair produced structurally valid rows (**+46** recovered sentence pairs), but caused **catastrophic regression** (**~−32 chrF** vs the same-run M06 Policy A baseline).

### Required statement

```text
Structural correctness alone is insufficient; recovered rows must match the training distribution or they degrade performance.
```

### Interpretation

- **Alignment repair ≠ usable supervision** for this continuation recipe: valid `(transliteration, translation)` pairs can still **destroy** dev chrF when the **mixture** shifts.
- **Distribution mismatch** dominates **local structural correctness** — the model’s optimum is **path-dependent** on the exact supervision regime established by M06.
- **M06 optimum remains unmatched**; alignment-quality v2 is **not** a viable lever without a new **integration** story (how / when / how much new supervision is applied).

---

## 3. Why this is a high-value failure

- **Same-run baseline** isolates the effect: identical eval contract, continuation from `outputs/m01_t5`, **only** the training CSV changes.
- **Clean, deterministic repair rules** (`;` / `:` only, `na == ne + 1`, document-level acceptance, row filters) remove ambiguity — the failure is **not** an ad hoc tuning artifact.
- **Full-sentence alignment** was explicitly targeted; a **large** negative outcome **rules out** “just fix alignment structure” as the primary bottleneck for this milestone sequence.
- **Large delta (~−32 chrF)** provides **strong causal signal** that the recovered distribution is **incompatible** with the current narrow optimum, not a noise band fluctuation.
- **Prevents wasted effort** on iterative alignment-repair heuristics without addressing **training dynamics** or **supervision integration**.

```text
This milestone conclusively shows that improving alignment structure alone does not produce usable training signal.
```

---

## 4. Delta scope (what changed)

| Area | Change |
|------|--------|
| Code | `src/akk2eng/data/alignment_quality.py`, `src/akk2eng/pipeline/align_quality.py`, `config.py` alignment-quality defaults |
| Tests | `tests/test_m08_alignment_quality.py`, `tests/fixtures/m08_alignment_quality/` |
| Docs | M08 plan, runbooks, summary, audit, tool log, CI run log |
| Data contract | Gitignored `data/derived/alignment_quality/*` produced locally |

---

## 5. Results (evidence)

| Run | chrF |
|-----|------|
| Baseline (M06 Policy A CSV) | **52.2530** |
| Candidate A (alignment-quality v2) | **20.0045** |
| Candidate B (v2 + M06 union) | **20.0045** |

**Best Δ vs baseline:** **−32.2485** chrF.  
**Decision:** `M08 regression — recovered rows reintroduce noise` (see [M08_run2_training_eval.md](M08_run2_training_eval.md)).

---

## 6. Kaggle / submission discipline

- **No Kaggle submission** (regression; dev gate not cleared).
- **No** `M08_run3_kaggle_submit.md`.

---

## 7. Audit conclusion

M08 is **closed** as a **documented, reproducible negative result**. The repository **truthfully records** that deterministic structural alignment repair **does not** improve this training/eval stack and **materially harms** it at scale (+46 rows).

**Next milestone:** **M09** — training dynamics / curriculum / integration (**not** alignment or selection scoring) — [../M09/M09_plan.md](../M09/M09_plan.md).
