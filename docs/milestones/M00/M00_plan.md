# M00 — Kaggle-Ready Foundation + First Submission Path

## Objective

Establish a **minimal, working repository** that produces a valid Kaggle submission file (`submission.csv`) and enables a first submission attempt within hours.

> This milestone prioritizes Kaggle submission readiness over full CI rigor. CI must be minimal and non-blocking. The primary objective is enabling a valid submission within M00.

This milestone collapses the original M00 (repo init + CI foundation) and M01 (first submission) into a single sprint, driven by the **3-day competition deadline**.

---

## Context

- **Competition:** Deep Past Initiative — Akkadian → English MT (Kaggle code competition)
- **Evaluation metric:** `√(BLEU × chrF++)`
- **Deadline:** ~March 23, 2026 (3 days from plan creation)
- **Training data:** ~1,500 document-level aligned pairs
- **Test data:** ~4,000 sentence-level items from ~400 documents
- **Submission limit:** 5/day
- **Constraint:** Code competition — notebook must run end-to-end on Kaggle

---

## Non-Goals (Strict — Explicitly Deferred)

- Coverage ≥85% gate
- Full security scanning (bandit, pip-audit, gitleaks)
- Pre-commit hooks
- Structured JSON logging
- Full RediAI-style CI rigor
- ML model fine-tuning
- HuggingFace integration
- Any frontend or UI

---

## Deliverables

### 1. Repository Structure

```
akk2eng/
├── src/
│   └── akk2eng/
│       ├── __init__.py
│       ├── config.py
│       ├── run_local.py
│       ├── data/
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   └── schema.py
│       ├── pipeline/
│       │   ├── __init__.py
│       │   ├── inference.py
│       │   └── run.py
│       ├── submission/
│       │   ├── __init__.py
│       │   └── writer.py
│       └── utils/
│           ├── __init__.py
│           └── logging.py
│
├── tests/
│   └── test_sanity.py
│
├── kaggle/
│   └── akk2eng_m00_submission.ipynb
│
├── data/                  (gitignored)
├── outputs/               (gitignored)
│
├── docs/
│   └── milestones/M00/
│
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── .github/workflows/ci.yml
├── README.md
```

### 2. Dummy Pipeline (Critical Path)

#### `loader.py`
- Load CSV (train.csv / test.csv)
- Return pandas DataFrame
- Handle missing files gracefully

#### `inference.py`
- Function: `run_inference(df) -> list[str]`
- Returns dummy translations (placeholder strings)
- Deterministic: same input → same output

#### `writer.py`
- Generate `submission.csv` with columns: `id`, `translation`
- Validate format matches Kaggle sample_submission.csv

#### `run.py` (CLI entry)
```bash
python -m akk2eng.pipeline.run
```
Flow: load test.csv → infer → write submission.csv

### 3. Kaggle Notebook Stub

```
kaggle/akk2eng_m00_submission.ipynb
```

- Loads `test.csv` from Kaggle input path
- Runs same pipeline logic as local
- Outputs `submission.csv` to Kaggle output path
- Must be self-contained (no external imports from src/)

### 4. Local Execution Parity

```bash
python -m akk2eng.pipeline.run
# equivalent:
python -m akk2eng.run_local
```

Same logic as notebook, for local development/testing.

### 5. Minimal CI (Light — Non-Blocking)

GitHub Actions workflow with:

| Job  | Tool   | Purpose           |
|------|--------|-------------------|
| lint | Ruff   | Code quality      |
| test | pytest | Sanity tests only |

**NOT included:** coverage gate, security scans, typecheck gate, pre-commit.

Python 3.10 only (no matrix — speed over breadth).

### 6. Minimal Tests

#### `test_sanity.py`
- Pipeline runs end-to-end without error
- submission.csv is created
- submission.csv has correct columns (`id`, `translation`)
- submission.csv has correct row count

### 7. pyproject.toml

- Package metadata
- Ruff configuration
- pytest configuration
- Dependencies declared

### 8. requirements.txt

- pandas
- (minimal — no ML dependencies yet)

---

## Acceptance Criteria

### Must Pass
- ✅ `pip install -e .` succeeds
- ✅ `python -m akk2eng.pipeline.run` produces `submission.csv`
- ✅ `submission.csv` has correct format (id, translation columns)
- ✅ `pytest` passes all sanity tests
- ✅ Kaggle notebook stub exists and mirrors local pipeline logic
- ✅ CI runs (lint + test)

### Must Exist
- ✅ `src/akk2eng/` package structure
- ✅ Working dummy pipeline
- ✅ `kaggle/akk2eng_m00_submission.ipynb`
- ✅ `pyproject.toml`
- ✅ `.gitignore`
- ✅ `README.md`
- ✅ Milestone docs

---

## Strategic Note

This milestone is the **bridge** between:
- Your enterprise-grade governance posture (RediAI, DARIA, Foundry)
- Kaggle's reality: **Notebook → submission.csv → score**

The governance stack will be backfilled after first leaderboard signal is achieved.

From RediAI philosophy: *"Do not test the platform. Test the claims."*
The claim right now is: **"We can submit to Kaggle successfully."**

---

## Next Milestone

**M01 — First Real Kaggle Submission**

Goal: Upload notebook to Kaggle, submit, get a leaderboard score (even if poor).
