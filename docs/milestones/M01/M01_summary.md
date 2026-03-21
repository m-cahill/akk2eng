# 📌 Milestone Summary — M01: Baseline Model + First Non-Zero Kaggle Score

**Project:** akk2eng  
**Phase:** Baseline modeling (signal milestone)  
**Milestone:** M01 — Baseline model + first non-zero Kaggle score  
**Timeframe:** 2026-03-20 → 2026-03-21  
**Status:** Closed  
**Baseline reference:** M00 complete (`v0.0.1-m00`); execution contract from M00 preserved  

---

## 1. Milestone Objective

M01 existed to deliver **real translation logic** (not a dummy pipeline) and prove **external value** via the competition leaderboard: a **first non-zero score** using a **deterministic baseline** (fine-tuned T5-small), without breaking the M00 submission schema or dual execution modes (local CLI + Kaggle notebook).

> Without M01, the project would have had no validated ML baseline, no GPU training path, and no evidence that the system improves over the 0.0 dummy score.

---

## 2. Scope Definition

### In Scope

- HuggingFace **seq2seq** baseline: **`google-t5/t5-small`**, fine-tuned on `train.csv` locally
- **Training CLI** (`pipeline/train`) with device/FP32/sample limits; GPU assertions for `--device cuda`
- **Inference** via `T5BaselineTranslator`; **greedy** generation defaults
- **Local validation** harness (`pipeline/validate`)
- **Tools:** `gpu_bringup`, `checkpoint_hash`
- **Kaggle:** `kaggle/akk2eng_m01_submission.ipynb`; validated reference `docs/akk2eng-m01c-submission.ipynb`
- **Dependencies:** torch, transformers, datasets, accelerate, sentencepiece; NumPy 1.x pin
- **Documentation:** `docs/akk2eng.md`, M01 plans, **M01_run1–3**, release tags **v0.0.2-m01a**, **v0.0.3-m01b**, **v0.0.4-m01c**
- **CI:** CPU-only; HF cache in workflow; tests updated for real inference

### Out of Scope

- Full normalization engine (**M03**), lexicon integration (**M06**), ensembles, Kaggle-side training
- Stochastic decoding as default
- Coverage/security gates beyond minimal CI
- Editing **M00** milestone artifacts under `docs/milestones/M00/` (per plan)

### Scope Changes

- **M01-A/B/C** execution split added for substrate, train, and Kaggle phases; documented in `akk2eng.md` and `M01_plan.md`.

---

## 3. Work Executed

| Area | Actions |
|------|---------|
| **Package** | Added `src/akk2eng/model/` (tokenizer, T5 wrapper), `pipeline/train.py`, `pipeline/validate.py`, `tools/gpu_bringup.py`, `tools/checkpoint_hash.py` |
| **Config** | Extended `config.py` for model IDs, lengths, seeds, default paths |
| **Notebook** | M01 Kaggle notebook; path documentation for competition + Models mounts |
| **Tests** | `test_sanity.py` updated; `test_checkpoint_hash.py` added |
| **Deps** | `pyproject.toml` / `requirements.txt` — torch range, transformers, numpy<2, etc. |
| **Docs** | M01 plan, B/C plans, run logs 1–3, M01C checklist, README GPU + Kaggle sections |
| **Git** | Tags for each sub-milestone closeout and final M01 |

Mechanical vs semantic: primarily **new modules and docs**; pipeline **contract** (CSV schema, flow) preserved from M00.

---

## 4. Validation & Evidence

| Mechanism | Result |
|-----------|--------|
| **Local pytest** | 4 passed (latest local run at audit time) |
| **Ruff** | Clean on maintained paths |
| **GPU bring-up** | Documented PASS on Blackwell-class workstation (`M01_run1.md`) |
| **Training** | Full GPU FP32 run; checkpoint + hash (`M01_run2.md`) |
| **Inference** | `pipeline.run` → valid `submission.csv` |
| **Kaggle** | Submission accepted; **public leaderboard 11.9** (`M01_run3.md`, `akk2eng.md`) |

Validation is **meaningful** for the milestone objective (external score + reproducible artifacts). **Gap:** no unified dev-set metric CLI in M01 — explicitly **M02**.

---

## 5. CI / Automation Impact

| Item | Detail |
|------|--------|
| Workflow | `.github/workflows/ci.yml` — Ruff + pytest |
| Change | Hugging Face hub cache for CI (speed); still **CPU-only** |
| Behavior | CI does not run CUDA or full training; local responsibility for GPU validation |

CI **validated** package import and sanity paths; it does **not** observe GPU or Kaggle runtime risk (accepted for M01).

---

## 6. Issues & Exceptions

| Issue | Root cause | Resolution |
|-------|------------|--------------|
| Blackwell / `sm_120` vs older torch wheels | PyTorch binary arch list | Documented override (CUDA 12.8+ wheel); `gpu_bringup` fails fast |
| NumPy 2.x vs torch extensions | Ecosystem mismatch | Pin `numpy<2` |
| Windows console Unicode | cp1252 | Replaced problematic Unicode in prints (ASCII) |

No unresolved **blocking** issues for M01 closure.

---

## 7. Deferred Work

| Item | Pre-existed? | Notes |
|------|--------------|--------|
| `pipeline.eval` + metrics | Yes (roadmap) | **M02** |
| Full M03/M06 | Yes | Preview only in M02 plan |
| Private LB snapshot | No | Record when competition ends |

---

## 8. Governance Outcomes

**Provably true after M01 (and not before):**

- A **fine-tuned** checkpoint can be produced, hashed, and loaded for inference locally and on Kaggle.
- **GPU substrate** can be validated with an explicit tool (`gpu_bringup`).
- **Leaderboard signal** > 0 (**11.9** public) is recorded with run logs and tags.
- **M01 scope is frozen** under documented Closeout Rule (`M01_run3.md`).

---

## 9. Exit Criteria Evaluation

| Criterion (from `M01_plan.md`) | Status | Evidence |
|--------------------------------|--------|----------|
| Non-zero Kaggle score | **Met** | 11.9 public LB |
| Pipeline runs locally | **Met** | `pipeline.run`, `train` |
| Notebook runs on Kaggle (inference) | **Met** | `M01_run3.md` |
| Deterministic outputs for fixed weights + inputs | **Met** | Greedy defaults; policy in `akk2eng.md` |
| Submission accepted | **Met** | `M01_run3.md` |

---

## 10. Final Verdict

**Milestone objectives met. M01 is closed.** Safe to proceed under **M02** per `docs/akk2eng.md` and `docs/milestones/M02/M02_plan.md`.

---

## 11. Authorized Next Step

- **M02** — Evaluation + targeted improvement loop (and optional **Quick +5** tactical sprint per `M02_plan.md`).
- **Constraint:** No new M01 scope without a new charter (`M01_run3.md` Closeout Rule).

---

## 12. Canonical References

| Reference | Location |
|-----------|----------|
| Tags | `v0.0.2-m01a`, `v0.0.3-m01b`, `v0.0.4-m01c` |
| Run logs | `docs/milestones/M01/M01_run1.md`, `M01_run2.md`, `M01_run3.md` |
| Plan | `docs/milestones/M01/M01_plan.md` |
| Tool log | `docs/milestones/M01/M01_toolcalls.md` |
| Source of truth | `docs/akk2eng.md` |
| Audit (this milestone) | `docs/milestones/M01/M01_audit.md` |
| Prior milestone summary | `docs/milestones/M00/M00_summary.md` |

**Commit (audit document snapshot):** `f3f9ed9` (workspace at generation time; tags point to earlier closeout commits on `main`).
