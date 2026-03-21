# M02 — Evaluation + Fast Leaderboard Climb

**Milestone ID:** M02  
**Phase:** Measurement & Optimization  
**Prerequisite:** M01 closed (`v0.0.4-m01c`)  
**Status:** Active  

**North star:** `docs/moonshot.md` · **Source of truth:** `docs/akk2eng.md`

---

## 1. Objective

Establish a **measurement-first improvement system** and achieve a **verified leaderboard gain (>11.9)** through **targeted, explainable changes**.

> M02 is NOT about building new features.  
> M02 is about **proving what actually improves translation quality**.

---

## 2. Core Philosophy

M02 introduces a strict loop:

```text
Measure → Diagnose → Change ONE thing → Re-measure → Submit (only if improved)
```

This replaces:

- intuition-driven iteration  
- blind retraining  
- Kaggle spam submissions  

With:

- deterministic evaluation  
- attributable improvements  
- audit-ready decisions  

---

## 3. Scope

### In Scope

#### 3.1 Evaluation Harness (FOUNDATIONAL)

Create a **dev evaluation system**:

- Split `train.csv` → **train / dev** (deterministic **seed = 42**, **90 / 10**).  
- Persist splits (reused across all experiments):

  ```text
  data/splits/
    train_split.csv
    dev_split.csv
  ```

  (`data/` is gitignored; splits are local audit inputs.)

- CLI:

  ```bash
  python -m akk2eng.pipeline.eval
  ```

- Outputs:

  ```text
  outputs/
    eval/
      predictions_dev.csv
      metrics.json
      eval_summary.txt
  ```

- Metrics (**M02 policy — authoritative**):

  - **Primary (dev loop): chrF** — main optimization signal (sacrebleu).  
  - **Secondary: BLEU** — sanity check only.  
  - **Kaggle leaderboard:** validation only; exact competition metric is **not** reproduced locally; **do not** probe-reverse-engineer via submissions.

#### 3.2 Error Analysis Engine (HIGH ROI)

Add:

```bash
python -m akk2eng.pipeline.analyze_errors
```

Outputs:

```text
outputs/analysis/
  error_buckets.json
  examples_by_bucket.txt
```

Initial buckets:

- Named entities (PN, GN)  
- Numbers / quantities  
- Rare tokens (OOV)  
- Repetition / hallucination  
- Function words / grammar  
- Word order issues  

This drives ALL improvements.

#### 3.3 Logging & Experiment Tracking

Each eval run produces:

```text
outputs/experiments/
  exp_<timestamp>/
    config.json
    metrics.json
    predictions_dev.csv
    notes.txt
```

Must include:

- model version / checkpoint path  
- preprocessing flags (when introduced)  
- decoding settings  

#### 3.4 First Targeted Improvements (Small + High Impact)

Implement ONLY if supported by eval:

**A. Normalization Preview (M03-lite)**

- Lowercase normalization (if safe)  
- Strip noise tokens  
- Normalize delimiters  

**B. Decoding Controls**

- max_length tuning  
- repetition penalty  
- optional beam search (ONLY if proven better)  

**C. Lexicon Injection (M06 preview)**

- Small, high-confidence dictionary  
- Apply as post-processing replacement (**preferred**)  
- Source: `docs/kaggledocs/OA_Lexicon_eBL.csv` (light-touch; not full M06)  

---

## 4. Out of Scope

- Full normalization engine (M03)  
- Full lexicon system (M06)  
- Model architecture changes  
- Large retraining experiments  
- Ensembles  

---

## 5. Execution Plan (Phased)

### Phase M02-A — Eval Harness

- Build `pipeline.eval`  
- Save predictions + metrics  
- Validate determinism  

**Exit:** repeatable metric output  

---

### Phase M02-B — Error Analysis

- Implement error bucketing  
- Generate ranked failure categories  

**Exit:** top 3 error classes identified  

---

### Phase M02-C — Targeted Fixes

- Apply 1–2 improvements ONLY  
- Re-run eval  
- Compare metrics  

**Exit:** measurable dev improvement  

---

### Phase M02-D — Kaggle Submission

Submit ONLY if:

- **dev chrF** improved vs previous best (permission to submit)  

Record:

```text
docs/milestones/M02/M02_runX.md
```

**Exit:** leaderboard **> 11.9** (validation)  

---

## 6. Acceptance Criteria

### Required

- [ ] `pipeline.eval` implemented  
- [ ] Deterministic dev split (seed=42, 90/10), persisted under `data/splits/`  
- [ ] Metrics saved to disk (chrF + BLEU)  
- [ ] Error analysis output generated (M02-B)  
- [ ] At least ONE improvement tested via eval (M02-C)  
- [ ] At least ONE Kaggle submission with full audit log (M02-D)  

### Success Condition

- Leaderboard score **> 11.9** (public LB, documented)  

---

## 7. Guardrails (CRITICAL)

### 7.1 No Blind Submissions

Every submission must be preceded by **dev chrF improvement**.

### 7.2 One Variable Rule

Only change ONE major variable per experiment.

### 7.3 Determinism Enforcement

- Fixed seeds  
- Greedy decoding baseline preserved unless an experiment explicitly documents a change  

### 7.4 Artifact Requirement

Every run must produce:

- predictions  
- metrics  
- config snapshot  

(under `outputs/eval/` and `outputs/experiments/`, gitignored)  

---

## 8. Deliverables

| Artifact        | Location                                 |
| --------------- | ---------------------------------------- |
| Eval CLI        | `src/akk2eng/pipeline/eval.py`           |
| Error analysis  | `src/akk2eng/pipeline/analyze_errors.py` |
| Split helpers   | `src/akk2eng/data/splits.py`             |
| Metrics output  | `outputs/eval/metrics.json`              |
| Experiment logs | `outputs/experiments/`                   |
| Run logs        | `docs/milestones/M02/M02_runX.md`        |

---

## 9. Audit Focus

M02 will be audited on:

- Measurement validity  
- Attribution clarity  
- Determinism adherence  
- Submission discipline  

---

## 10. Closeout Instructions (for Cursor)

At milestone completion:

1. Generate `M02_summary.md`, `M02_audit.md`  
2. Update `docs/akk2eng.md`  
3. Record best score + experiment lineage  
4. Tag release `v0.0.X-m02`  
5. Create next milestone folder `M03/`  

Ensure all documentation is updated as necessary.

---

## 11. Strategic Notes

This is the **most important milestone in the entire Kaggle trajectory**.

M01 proved: **“We can produce signal.”**  
M02 proves: **“We can systematically improve signal.”**

---

## 12. Authoritative Clarifications (locked)

| Topic | Decision |
| ----- | -------- |
| Competition metric | Not reproduced locally; **chrF ↑ = submit gate**; Kaggle = validation only |
| Dev split | **90 / 10**, `seed = 42`, `n_dev = max(1, int(0.10 * n))` |
| Split storage | `data/splits/train_split.csv`, `data/splits/dev_split.csv`, reused forever unless `--force-splits` |
| Lexicon | `docs/kaggledocs/OA_Lexicon_eBL.csv`; M02 = small / high-confidence / post-process only |
| Artifacts | `outputs/` (eval, analysis, experiments) — **gitignored**, required locally for audit |

---

## Related

- Tool log: [M02_toolcalls.md](M02_toolcalls.md)  
- M01 → M02 handoff: `docs/milestones/M01/M01_run3.md`  
