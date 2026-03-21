# M01 Audit — Baseline Model + First Non-Zero Kaggle Score

**Audit Mode:** DELTA AUDIT  
**Milestone:** M01  
**Project:** akk2eng  
**Date:** 2026-03-21  
**Range (closeout):** M00 tag `v0.0.1-m00` → M01 tag `v0.0.4-m01c` (see git tags; workspace HEAD at audit write: `f3f9ed9`)  
**CI status:** Green (local verification: `pytest` 4 passed, `ruff` clean on touched paths; GitHub Actions: Ruff + pytest per `.github/workflows/ci.yml` — **specific run ID not recorded** in milestone logs)

**Audit verdict:** **PASS (green)** — M01 met its signal objective with auditable substrate, training, and external validation; no blocking regressions identified against stated scope.

---

## 1. Executive Summary (delta-focused)

**Improvements**

- Real **seq2seq baseline** (`google-t5/t5-small`) with local fine-tune, deterministic greedy inference, and Kaggle inference path preserved.
- **GPU substrate discipline:** `gpu_bringup`, arch checks (incl. Blackwell `sm_120`), FP32 training path, checkpoint **SHA-256** manifest tooling.
- **Governance trail:** `M01_run1.md`–`M01_run3.md`, release tags `v0.0.2-m01a` … `v0.0.4-m01c`, `docs/akk2eng.md` updated.
- **External validation:** Kaggle submission accepted; **public leaderboard 11.9** recorded (see `M01_run3.md`, `akk2eng.md`).

**Risks**

- **Training non-determinism** on GPU (documented); inference-with-fixed-weights is the strict determinism target.
- **Dev metric gap:** no dedicated `pipeline.eval` in M01 (deferred to **M02** per `M02_plan.md`).
- **Dependency surface:** torch/transformers stack sensitive to NumPy 2.x and CUDA wheel/arch mismatch (mitigated by pins + `gpu_bringup`).

**Single most important next action**

- Execute **M02**: scripted dev eval + targeted error analysis before further Kaggle burns (`docs/milestones/M02/M02_plan.md`).

---

## 2. Evidence Reviewed

| Evidence | Source | Finding |
|----------|--------|---------|
| GPU substrate PASS | `docs/milestones/M01/M01_run1.md` | Blackwell-compatible torch; FP32 matmul + Transformers on CUDA |
| Full train + hash | `docs/milestones/M01/M01_run2.md` | 3 epochs, `cuda:0`, `MANIFEST_SHA256` recorded |
| Kaggle submit + score | `docs/milestones/M01/M01_run3.md` | `fine-tuned: True`, submission schema OK, **11.9** public LB |
| Source of truth | `docs/akk2eng.md` | M01 complete; leaderboard row; release tags |
| Plan + exit | `docs/milestones/M01/M01_plan.md` | Exit condition (score > 0) met |
| Implementation | `src/akk2eng/model/`, `pipeline/train.py`, `inference.py`, `tools/` | Matches M01 plan scope |
| CI workflow | `.github/workflows/ci.yml` | CPU-only; Ruff + pytest; HF cache optional |
| Tests | `tests/test_sanity.py`, `tests/test_checkpoint_hash.py` | Pass locally (4 tests) |

---

## 3. Pass/Fail by Category (quality gates)

| Gate | Result | Notes |
|------|--------|--------|
| **Functionality** | ✅ PASS | Train, infer, submit path operational; schema `id,translation` |
| **Determinism (contract)** | ✅ PASS | Greedy decode, seeds; GPU train variability documented |
| **CI integrity (scoped)** | ✅ PASS | Minimal CI unchanged in spirit; no required job weakened |
| **Contracts** | ✅ PASS | M00 submission / dual execution modes preserved |
| **Security / secrets** | ⚠️ NARROW | `docs/kaggletoken.txt` remains a local risk if committed — `.gitignore` should exclude; not introduced as M01 requirement |
| **Reproducibility** | ✅ PASS | Checkpoint hashing + pinned deps + run logs |

---

## 4. Structured Findings

**No HIGH-severity blockers** for M01 closure.

| ID | Observation | Interpretation | Recommendation (≤90 min) | Guardrail |
|----|-------------|----------------|---------------------------|-----------|
| F1 | No `pipeline.eval` in M01 | Hard to prove incremental improvements | Implement M02 eval CLI + JSON artifacts | Require dev delta before Kaggle submit |
| F2 | `safe_cuda_device()` CPU fallback for unsupported arch | Prevents crash on mismatched torch; training still asserts on `--device cuda` | Document in README for operators | Keep `gpu_bringup` mandatory for GPU claims |

---

## 5. Deferred Items

| Item | Rationale | Exit / Owner |
|------|-----------|--------------|
| Full eval harness (BLEU/chrF, saved preds) | M02 scope | `M02_plan.md` Step 2 |
| Coverage ≥85%, security scans | Same as M00 deferral | Post-M02+ per roadmap |
| Private leaderboard final | Competition timeline | Record when available |

---

## 6. Final Score

**5.0 / 5.0**

### Justification

- **Functionality:** Full stack from GPU bring-up to non-zero leaderboard — **5/5**
- **Determinism posture:** Correct boundary (train vs inference) — **5/5**
- **Governance:** Tags, run logs, closeout rule, `akk2eng.md` — **5/5**
- **CI:** Appropriate minimal scope; no leakage of GPU requirement into CI — **5/5**

---

## 7. Recommendation

**M01 is fit for closure.** Proceed under **M02** with measurement-first iteration. Re-open M01 only under a new milestone charter (`M01_run3.md` Closeout Rule).
