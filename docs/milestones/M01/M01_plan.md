# M01 — Baseline Model + First Non-Zero Score

**Project:** akk2eng  
**Milestone:** M01  
**Phase:** Baseline modeling  
**Status:** ✅ Complete (`v0.0.4-m01c`)

### M01-A / M01-B / M01-C (execution split)

- **M01-A — Substrate:** **Closed** (`v0.0.2-m01a`). Evidence: `docs/milestones/M01/M01_run1.md`. **Frozen.**
- **M01-B — Full train:** **Closed** (`v0.0.3-m01b`). Evidence: `docs/milestones/M01/M01_run2.md`. **Frozen.**
- **M01-C — Kaggle:** **Closed** (`v0.0.4-m01c`). Evidence: `docs/milestones/M01/M01_run3.md`. **Frozen.**

Canonical Kaggle notebook: `kaggle/akk2eng_m01_submission.ipynb`. Validated path reference: `docs/akk2eng-m01c-submission.ipynb`.

## Objective

Achieve the **first non-zero Kaggle leaderboard score** using a **deterministic baseline translation system**.

> This is a **signal milestone**, not an optimization milestone.

## Core principle

> **Improve output quality while preserving the M00 execution contract.**

We are **not** changing:

- Pipeline structure (load → infer → write submission)
- Submission format (`id`, `translation`)
- Execution modes (local CLI + Kaggle notebook)

We **are** adding:

- Real translation logic (fine-tuned `t5-small` on `train.csv` locally)
- Minimal preprocessing
- Local validation harness + debug prints
- Kaggle notebook path: **inference only** (upload fine-tuned weights as a separate input dataset)

## Prerequisites

- M00 closed and tagged (`v0.0.1-m00`); **do not edit** `docs/milestones/M00/*` or M00 audit/summary artifacts
- Kaggle account joined to the competition
- Local: `data/train.csv`, `data/test.csv` from the official competition bundle
- Notebook: `kaggle/akk2eng_m01_submission.ipynb` (attach competition data + optional model dataset)

## Scope

### In scope

1. **Baseline model** — HuggingFace seq2seq, default **`google-t5/t5-small`**, fine-tuned on `train.csv` **locally**
2. **Training CLI** — saves checkpoint under `outputs/m01_t5/` (gitignored)
3. **Inference** — deterministic greedy / non-sampled decoding; batch over `test.csv`
4. **Kaggle** — load saved model from `/kaggle/input/...`, run inference, write `/kaggle/working/submission.csv`
5. **Local validation (minimal)** — e.g. 90/10 split on `train.csv`, print `INPUT → PRED → TARGET` samples
6. **Debug outputs** — sample predictions (5–10 rows), token-length sanity, required in local run and notebook

### Out of scope

- Heavy preprocessing (later milestone)
- Lexicon integration
- Data augmentation
- Ensemble methods
- Kaggle-side training (M01 optimizes local train → Kaggle infer handoff)
- Full CI rigor (coverage/security gates)

## Implementation plan

### Step 1 — Model module

Create:

```text
src/akk2eng/model/
  __init__.py
  tokenizer.py
  model.py
```

Responsibilities:

- Load pretrained / fine-tuned seq2seq weights
- Tokenize transliteration with fixed task prefix
- Greedy generation with fixed `max_new_tokens` / lengths

### Step 2 — Baseline (locked default)

- **Base checkpoint:** `google-t5/t5-small`
- **Task string (prefix):** single stable prefix for all inputs (documented in code)
- **Local training:** `python -m akk2eng.pipeline.train` (writes `outputs/m01_t5/`)
- **Inference:** `python -m akk2eng.pipeline.run` with `--model-dir` or default `outputs/m01_t5/`

### Step 3 — Determinism (mandatory)

- `SEED = 42` for `torch`, `numpy`, `random`
- Training: `transformers` / `Trainer` seeding where applicable
- Inference: `do_sample=False`, `num_beams=1` (greedy), fixed caps on generation length

### Step 4 — Pipeline wiring

- Update `src/akk2eng/pipeline/inference.py`: replace dummy output with `model.generate(...)` (via model module)
- Update `src/akk2eng/pipeline/run.py`: optional `--model-dir`, `--quiet`; debug samples unless quiet

### Step 5 — Kaggle notebook

- Primary notebook: **`kaggle/akk2eng_m01_submission.ipynb`**
- Self-contained inference (attach fine-tuned folder as second dataset); debug prints: `Sample predictions:`, row counts, avg token length

### Step 6 — Local validation

- `python -m akk2eng.pipeline.validate` (or equivalent): split `train.csv`, run predictions, print comparison rows

### Step 7 — Submission verification

- CSV header: `id,translation`
- Row count matches test set
- Runs locally and on Kaggle with identical **schema** (values differ only by model inputs/weights)

## Acceptance criteria

| Requirement | Status |
|-------------|--------|
| Non-zero Kaggle score (project goal) | Target |
| Pipeline runs locally | Required |
| Notebook runs on Kaggle (inference) | Required |
| Deterministic outputs for fixed weights + inputs | Required |
| Submission accepted by competition | Required |

## Risks

| Risk | Mitigation |
|------|------------|
| Model slow on Kaggle CPU | Keep `t5-small`; batch inference |
| Tokenization mismatch | One prefix, same code path local + notebook |
| No checkpoint on Kaggle | Document uploading `outputs/m01_t5/` as a Kaggle dataset |

## Governance

- **Do not** modify M00 milestone **artifacts** under `docs/milestones/M00/` or reinterpret the M00 tag
- **Do not** break the M00 execution contract (paths configurable; schema unchanged)
- **Do** evolve the Kaggle notebook; M01 notebook name reflects the milestone

## Exit condition

> **Leaderboard score > 0.0** (first non-zero signal)

**Met** (M01-C). Proceed to **M02** (evaluation + targeted improvement loop).

## Required updates to `docs/akk2eng.md`

Cursor updates the project source of truth when M01 behavior lands: milestones table, M01 scope, roadmap, execution modes, determinism policy, leaderboard tracking (see live `docs/akk2eng.md`).
