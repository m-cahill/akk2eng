# akk2eng — project source of truth

This document is the **living authority** for repository scope, schema, and milestone status. Update it when behavior or data contracts change.

## Project

| Field | Value |
|--------|--------|
| **Name** | `akk2eng` |
| **Goal** | Akkadian (Old Assyrian) → English MT for the [Deep Past Initiative Kaggle code competition](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/) |
| **North star** | `docs/moonshot.md` |

## Competition data contract (reference)

Aligned with `docs/kaggledocs/datasetdescription.md`:

| File | Role |
|------|------|
| `train.csv` | ~1.5k rows; `oare_id`, `transliteration`, `translation` |
| `test.csv` | Rows with `id`, `text_id`, `line_start`, `line_end`, `transliteration` |
| `sample_submission.csv` | Columns `id`, `translation` |

**Submission artifact:** CSV with header `id,translation`, one row per test `id`.

### Obtaining the official files locally

After accepting rules on Kaggle, install the CLI (`pip install -e ".[kaggle]"` from the repo; see `README.md`) and download:

```bash
kaggle competitions download -c deep-past-initiative-machine-translation -p data
```

Unzip into `data/` so `data/test.csv` (and optionally `train.csv`, `sample_submission.csv`, etc.) match the paths used by `python -m akk2eng.pipeline.run`.

**Note:** Files under `docs/kaggledocs/` (e.g. `OA_Lexicon_eBL.csv`, `rules.md`) are **reference copies** for the team; they are **not** a substitute for the competition `test.csv` / `train.csv` bundle.

## Database schema

**None (M00).** This milestone is file-based only (CSV in/out). If SQL or document stores are introduced later, document tables and migrations here.

## Repository layout

| Path | Purpose |
|------|---------|
| `src/akk2eng/` | Installable package: load → infer → write submission |
| `tests/` | Pytest sanity tests |
| `kaggle/` | Kaggle notebook(s), self-contained for code competition |
| `data/` | Local competition CSVs (gitignored) |
| `outputs/` | Local `submission.csv` and M01 fine-tuned weights (gitignored) |
| `src/akk2eng/tools/` | Local substrate utilities (GPU bring-up, checkpoint hash); not used in CI |

## Milestones

| ID | Summary | Status |
|----|---------|--------|
| **M00** | Kaggle-ready foundation + dummy pipeline + minimal CI + notebook stub + validated Kaggle submission | ✅ Complete (validated) |
| **M01** | Baseline model + first non-zero Kaggle score | ✅ Complete (see `docs/milestones/M01/M01_plan.md`, tag `v0.0.4-m01c`) |

## M01 scope (baseline model)

M01 introduces the first real translation logic:

- HuggingFace seq2seq baseline: **`google-t5/t5-small`**, fine-tuned on `train.csv` **locally**
- Deterministic inference (greedy / no sampling)
- Minimal validation harness (`python -m akk2eng.pipeline.validate`)
- Kaggle notebook: `kaggle/akk2eng_m01_submission.ipynb` (validated path patterns; as-run reference: `docs/akk2eng-m01c-submission.ipynb`)

**Goal:** achieve the first non-zero leaderboard score while preserving the M00 submission and execution contract.

### M01 sub-phases (execution)

**M01 closed** (`v0.0.4-m01c`). Active work continues at **M02** per roadmap.

| Sub-phase | Status | Intent |
|-----------|--------|--------|
| **M01-A** | **Complete** (`v0.0.2-m01a`) | **Substrate verification** — `docs/milestones/M01/M01_run1.md`. |
| **M01-B** | **Complete** (`v0.0.3-m01b`) | **Full local training** — `docs/milestones/M01/M01_run2.md`, `M01B_plan.md`. |
| **M01-C** | **Complete** (`v0.0.4-m01c`) | **Kaggle submit** — `docs/milestones/M01/M01_run3.md`; non-zero leaderboard signal. |

Bring-up uses **conservative FP32** in the GPU probe path; full training can use `--fp32` when validating new hardware. **GPU training may be slightly non-deterministic** between runs; treat **inference with fixed weights** as the primary determinism contract (see Determinism policy).

**Environment notes:**
- `pyproject.toml` pins **`numpy` 1.x** (`>=1.26,<2`) for compatibility with the PyTorch + `accelerate` / `Trainer` stack; do not upgrade to NumPy 2.x for this milestone without re-validating training.
- **Blackwell GPUs** (`sm_120`, e.g. RTX 5090) need a PyTorch build compiled with CUDA 12.8+ (e.g. `2.10+cu128`). This is a **required local substrate choice** for M01-A GPU validation on Blackwell; CI stays on CPU-safe PyPI wheels. The repo pin (`torch>=2.4`) has no upper bound so both tracks satisfy the declared dependency. Install the correct wheel via `--index-url .../cu128` (see `README.md`). `gpu_bringup` detects arch mismatches and prints an actionable error.

## Planned milestone roadmap

| ID | Focus |
|----|--------|
| M01 | Baseline model (first score) |
| M02 | Evaluation harness |
| M03 | Normalization engine |
| M04 | Sentence alignment |
| M05 | Data augmentation |
| M06 | Lexicon integration |
| M07 | Named entity handling |
| M08 | Rule-based improvements |
| M09 | Model upgrade |
| M10 | Training stabilization |
| M11 | Post-processing |
| M12 | Final submission system |

## Execution modes (invariant)

All milestones must support:

1. **Local execution** — e.g. `python -m akk2eng.pipeline.run` (or `python -m akk2eng.run_local`), with paths defaulting to repo-root-relative `data/` and `outputs/` (see `README.md`).
2. **Kaggle notebook execution** — self-contained notebook under `kaggle/`, competition data attached, submission written to `/kaggle/working/submission.csv`.

**Outputs** must match the competition schema: columns `id`, `translation`, one row per test `id`. Local and Kaggle runs must stay aligned on this contract even when file paths differ (`data/test.csv` vs `/kaggle/input/.../test.csv`).

M00 proved this dual path with a dummy model; M01 and later milestones keep the same contract while improving model quality.

## Determinism policy

- Pipelines must produce **identical outputs** for **identical inputs** and **identical saved model weights**
- **Random seeds** are fixed for training and inference utilities (project default: `42`)
- **No stochastic decoding** unless explicitly approved for an experiment; M01 uses greedy generation
- **Training on GPU** may yield small run-to-run differences; compare checkpoints with `python -m akk2eng.tools.checkpoint_hash` when auditing repeatability
- **Inference** with **fixed checkpoint files** and greedy decoding is the strict determinism target; GPU vs CPU inference for the same weights should match schema and be stable for the same code path, subject only to documented numerical edge cases

## Leaderboard tracking

| Milestone | Score |
|-----------|--------|
| M00 | 0.0 |
| M01 | 11.9 |

Run log: `docs/milestones/M01/M01_run3.md` (public leaderboard; private LB may differ at competition end).

## M00 validation (Kaggle)

M00 achieved full end-to-end validation via Kaggle execution:

- Notebook executed successfully in Kaggle environment
- Data loaded from competition input path (e.g. `/kaggle/input/deep-past-initiative-machine-translation` or `/kaggle/input/competitions/deep-past-initiative-machine-translation`)
- Submission file generated at `/kaggle/working/submission.csv`
- Submission accepted by competition
- Leaderboard score returned (0.0 expected for dummy baseline)

This confirms:

- Kaggle runtime compatibility
- Submission format correctness
- End-to-end pipeline integrity

## CI (M00)

GitHub Actions:

- **Ruff** (lint + format)
- **pytest** (sanity tests)

Scope intentionally minimal to prioritize Kaggle submission readiness.

Full CI rigor (coverage gates, security scanning, reproducibility enforcement) deferred to post-M01 milestones.

## Release tags

| Tag | Description |
|-----|-------------|
| v0.0.1-m00 | Kaggle-ready foundation; first valid submission pipeline |
| v0.0.2-m01a | GPU substrate validated (RTX 5090 / Blackwell, CUDA 12.8); M01-A closed |
| v0.0.3-m01b | Baseline model trained (T5-small), checkpoint + hash + local inference verified; M01-B closed |
| v0.0.4-m01c | Kaggle submission with fine-tuned baseline; public leaderboard 11.9; M01 complete |

## Related governance docs

- RediAI v3 reference (posture): `docs/rediai33/rediai-v3.md`
- DARIA / EZRA / Foundry manuals: `docs/manuals/`
