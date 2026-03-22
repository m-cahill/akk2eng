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
| **M01** | Baseline model + first non-zero Kaggle score | ✅ Complete (`M01_plan.md`, `M01_audit.md`, `M01_summary.md`; tag `v0.0.4-m01c`) |
| **M02** | Evaluation + targeted improvement loop | ✅ Complete (`M02_summary.md`, `M02_audit.md`; tag `v0.0.5-m02`) |
| **M03** | Normalization engine | ✅ Complete (`M03_summary.md`, `M03_audit.md`; tag `v0.0.6-m03`) |
| **M04** | Sentence alignment | ✅ Complete (`M04_summary.md`, `M04_audit.md`; tag `v0.0.7-m04`) |
| **M05** | Data augmentation | ✅ Complete (`M05_summary.md`, `M05_audit.md`; tag `v0.0.8-m05`) |
| **M06** | Precision-preserving data expansion | 🚧 Next (`docs/milestones/M06/M06_plan.md`) |

## M01 scope (baseline model)

M01 introduces the first real translation logic:

- HuggingFace seq2seq baseline: **`google-t5/t5-small`**, fine-tuned on `train.csv` **locally**
- Deterministic inference (greedy / no sampling)
- Minimal validation harness (`python -m akk2eng.pipeline.validate`)
- Kaggle notebook: `kaggle/akk2eng_m01_submission.ipynb` (validated path patterns; as-run reference: `docs/akk2eng-m01c-submission.ipynb`)

**Goal:** achieve the first non-zero leaderboard score while preserving the M00 submission and execution contract.

### M01 sub-phases (execution)

**M01 closed** (`v0.0.4-m01c`). **M02 closed** (`v0.0.5-m02`). **M03 closed** (`v0.0.6-m03`). **M04 closed** (`v0.0.7-m04`). **M05 closed** (`v0.0.8-m05`). Active work continues at **M06** per roadmap.

| Sub-phase | Status | Intent |
|-----------|--------|--------|
| **M01-A** | **Complete** (`v0.0.2-m01a`) | **Substrate verification** — `docs/milestones/M01/M01_run1.md`. |
| **M01-B** | **Complete** (`v0.0.3-m01b`) | **Full local training** — `docs/milestones/M01/M01_run2.md`, `M01B_plan.md`. |
| **M01-C** | **Complete** (`v0.0.4-m01c`) | **Kaggle submit** — `docs/milestones/M01/M01_run3.md`; non-zero leaderboard signal. |

Bring-up uses **conservative FP32** in the GPU probe path; full training can use `--fp32` when validating new hardware. **GPU training may be slightly non-deterministic** between runs; treat **inference with fixed weights** as the primary determinism contract (see Determinism policy).

**Environment notes:**
- `pyproject.toml` pins **`numpy` 1.x** (`>=1.26,<2`) for compatibility with the PyTorch + `accelerate` / `Trainer` stack; do not upgrade to NumPy 2.x for this milestone without re-validating training.
- **Blackwell GPUs** (`sm_120`, e.g. RTX 5090) need a PyTorch build compiled with CUDA 12.8+ (e.g. `2.10+cu128`). This is a **required local substrate choice** for M01-A GPU validation on Blackwell; CI stays on CPU-safe PyPI wheels. The repo pin (`torch>=2.4`) has no upper bound so both tracks satisfy the declared dependency. Install the correct wheel via `--index-url .../cu128` (see `README.md`). `gpu_bringup` detects arch mismatches and prints an actionable error.

## M02 scope (evaluation + targeted improvement loop)

**Closed** (`v0.0.5-m02`). M01 baseline (public LB **11.9**) is frozen; M02 delivered **measurement-first** iteration, decoding experiments, and lexicon validation. **Closeout:** `docs/milestones/M02/M02_summary.md`, `docs/milestones/M02/M02_audit.md`.

- **Dev decoding (M02-C / C.2 / C.3):** `config.py` sets `repetition_penalty=1.1`, `no_repeat_ngram_size=3`, and **`num_beams=3`** (M02-C.3 beam experiment; see `docs/milestones/M02/M02_run3_local_beam.md`). Eval artifacts record full `decoding` dict. Greedy@1.1 archive: `M02_run2_local_refinement.md`; penalty 1.2 step: `M02_run1_m02c_decoding.md`. **Kaggle notebook:** must match repo decode (including **`num_beams`**). Submit log: `docs/milestones/M02/M02_run2_kaggle.md`.
- **Lexicon post-process (M02-D):** `USE_LEXICON`, `DEFAULT_LEXICON_CSV`, `LEXICON_MAX_ENTRIES` in `config.py`; applied in `run_inference()` **only to model outputs** (train-filtered `form→lexeme`, boundary-safe regex). CLI: `--no-lexicon`, `--lexicon-csv`, `--lexicon-train-csv`, `--lexicon-max-entries` on `pipeline.eval`; `pipeline.run` supports `--no-lexicon` / lexicon overrides. See `docs/milestones/M02/M02_run4_lexicon.md`.
- **Plan (charter):** `docs/milestones/M02/M02_plan.md`  
- **Tool log:** `docs/milestones/M02/M02_toolcalls.md`.  
- **Strategy mirror:** `docs/milestones/M01/M01_run3.md` (section **Next: M02**).

### M02 Closeout

- Dev metric (chrF) improved significantly via decoding controls (e.g. **18.65 → 42.82** peak greedy@1.1 on the frozen dev split; beam tradeoffs in `M02_run3_local_beam.md`).
- Kaggle leaderboard plateaued at **~11.6–11.9** (decode-only work did not establish a sustained public beat over **11.9**).
- Lexicon injection **validated** but **inactive on dev** in practice (no standalone matching forms in dev English predictions; **0/156** rows changed vs beam baseline in `M02_run4_lexicon.md`); pipeline remains on for future leakage.
- Decoding space **exhausted** for material gains without **data / normalization** improvements.

**Conclusion:**  
M02 complete. Next gains require normalization + data pipeline improvements (**M03**).

### M02 Evaluation Contract

All improvements must be validated via:

- deterministic dev split (**seed = 42**, **90 / 10**) persisted under `data/splits/` (`train_split.csv`, `dev_split.csv`);
- saved predictions (`outputs/eval/predictions_dev.csv`);
- saved metrics (`outputs/eval/metrics.json`) with **chrF** as the primary dev signal and **BLEU** as secondary.

**Dev loop:** the exact Kaggle metric is **not** reproduced locally; **chrF improvement = permission to submit**; public leaderboard score is **validation only**. No probe submissions to reverse-engineer scoring.

### Experiment Tracking

All M02 experiments must produce:

- `config.json`
- `metrics.json`
- `predictions_dev.csv`

Stored under `outputs/experiments/exp_<timestamp>/` (and mirrored under `outputs/eval/` for the latest run). Artifacts are **required for audit** and stay **uncommitted** (`outputs/` is gitignored).

### Submission Discipline

Submissions are only allowed when **dev chrF improves** over the previous best (see `M02_plan.md` guardrails). Each submit is logged (e.g. `docs/milestones/M02/M02_runX.md`).

**M02 outcome:** dev harness and decoding experiments delivered large **chrF** improvements locally; public LB remained in the **~11.6–11.9** band — **M03** targets normalization and data quality to break the plateau. *(Original stretch exit — scripted dev metric + Kaggle **> 11.9** — carries forward as **M03 exit** alongside dev chrF.)*

## M03 scope (normalization engine)

**Closed** (`v0.0.6-m03`). Inference-time transliteration cleanup in `akk2eng.data.normalize.normalize_transliteration()`, integrated only in `run_inference()`. **Closeout:** `docs/milestones/M03/M03_summary.md`, `docs/milestones/M03/M03_audit.md`.

- **v1:** NFKC + lowercase → dev **chrF regression** vs norm-off (train/inference mismatch); documented in `docs/milestones/M03/M03_run1_normalization.md`.
- **v2:** noise + whitespace + duplicate collapse only → **metric parity** vs `--no-normalization` on frozen dev (chrF **~39.86**, beam=3); `docs/milestones/M03/M03_run2_conservative_norm.md`.
- **Config:** `USE_NORMALIZATION`, `NORMALIZATION_VERSION` (`v2`); CLI `--no-normalization` on `pipeline.eval` / `pipeline.run`.

### M03 Closeout

- Normalization engine implemented and integrated at inference-time.
- **v1** (aggressive) caused performance regression due to train/inference mismatch.
- **v2** (conservative) restored distribution alignment and produced **identical** dev metrics and error buckets vs baseline (norm off).
- No measurable improvement in dev chrF from normalization alone; **no** Kaggle submission in M03 (discipline: no dev gain).

**Conclusion:**  
Normalization is validated as a **safe** transformation layer but is **not** a primary optimization lever.  
Structural data alignment was pursued in **M04** (✅ complete, `v0.0.7-m04`); **M05** (data augmentation) is ✅ complete (`v0.0.8-m05`); next roadmap focus is **M06** (precision-preserving expansion).

## M04 scope (sentence alignment)

**Closed** (`v0.0.7-m04`). Deterministic sentence-level `(transliteration, translation)` pairs from the official train bundle + `Sentences_Oare_FirstWord_LinNum.csv`, with reports and content hashes. **Closeout:** `docs/milestones/M04/M04_summary.md`, `docs/milestones/M04/M04_audit.md`.

### Pipeline

- **Engine:** `src/akk2eng/data/alignment.py` — line-number parsing (incl. primes / float encodings), conservative English splitting, monotonic pairing, skip-with-reason semantics.
- **CLI:** `python -m akk2eng.pipeline.align` → `data/derived/alignment/aligned_train_sentences.csv` + `alignment_report.json` (local, gitignored).
- **Split-safe requirement (honest dev eval):** `python -m akk2eng.pipeline.align --split-safe` reads **`data/splits/train_split.csv` only**, writes `aligned_train_sentences_split.csv` + `alignment_report_split.json`, and **fails** if any aligned `oare_id` appears in **`data/splits/dev_split.csv`**.
- **Training:** `python -m akk2eng.pipeline.train` supports aligned / mixed CSV paths; continuation from `outputs/m01_t5` documented in M04 run notes.
- **Mixed corpus:** `python -m akk2eng.pipeline.mix_train` — explored; validated M04 outcome is **split-safe aligned-only** gain, not mixed.

### Derived dataset contract (gitignored)

| Path | Role |
|------|------|
| `data/derived/alignment/aligned_train_sentences.csv` | Sentence pairs from **full** `train.csv` (experiments / legacy) |
| `data/derived/alignment/alignment_report.json` | Full-train alignment report + CSV SHA-256 |
| `data/derived/alignment/aligned_train_sentences_split.csv` | **Leak-safe** pairs (train split only) |
| `data/derived/alignment/alignment_report_split.json` | Split-safe report |

### M04 Closeout

- **Baseline** (frozen dev, M01 checkpoint, beam=3, lex on, norm v2): chrF **~39.8601**.
- **Leakage issue:** alignment from **full** `train.csv` produced **~52.25 chrF** — **invalid** as a generalization estimate because dev documents could contribute to alignment supervision.
- **Fix:** `--split-safe` + overlap check → **0** shared `oare_id` with dev.
- **Validated result:** **~43.34 chrF** (**+3.48** vs baseline) on split-safe aligned-only continuation — **trustworthy** under the same evaluation contract.
- **Thesis:** aligns with `docs/moonshot.md` — **fixing data structure** (sentence alignment) yields measurable gain without model swap.

**Conclusion:**  
M04 complete. Next at time of M04 closeout was **M05**; **M05 is now closed** — see `docs/milestones/M05/M05_summary.md`. Active next: **M06** — `docs/milestones/M06/M06_plan.md`.

## M05 scope (data augmentation / alignment expansion)

**Closed** (`v0.0.8-m05`). Split-safe **expansion** of sentence-aligned pairs (`python -m akk2eng.pipeline.augment --split-safe`) on top of M04 strict alignment, with full row provenance and hashes. **Closeout:** `docs/milestones/M05/M05_summary.md`, `docs/milestones/M05/M05_audit.md`.

### Pipeline

- **Engine:** `src/akk2eng/data/augmentation.py` — relaxed first-word, English `;` resplit, partial-prefix recovery; deterministic CSV + `augmentation_report.json`.
- **CLI:** `python -m akk2eng.pipeline.augment --split-safe` → `data/derived/augmentation/augmented_train_sentences.csv` (gitignored); dev overlap check (fail-closed).
- **Training:** same continuation contract as M04 (`--resume-model-dir outputs/m01_t5`, 3-epoch comparison vs aligned-only control).

### Derived dataset contract (gitignored)

| Path | Role |
|------|------|
| `data/derived/augmentation/augmented_train_sentences.csv` | Strict + expanded rows (542 as-built), provenance columns |
| `data/derived/augmentation/augmentation_report.json` | Counts, `by_type`, SHA-256 |

### M05 Closeout

- **Builder:** 236 strict + 306 expansion rows = **542** total; **0** dev `oare_id` overlap.
- **GPU eval (same run):** control (236-row aligned) **chrF 45.36**; augmented (542-row) **chrF 20.39**; **Δ ≈ −25 chrF** vs control.
- **M04 pin (~43.34):** augmented **far below**; control **above** pin (run variance—**augmented vs control** is the primary discriminator).
- **Thesis tested:** naive **volume** expansion without **quality gating** **hurts**; **precision > recall** for this supervision.

```text
M05 demonstrated that mixing low-confidence partial-prefix pairs with strict
alignment degraded translation quality catastrophically. Future expansion must
preserve alignment precision (gating, weighting, or selective inclusion).
```

**Conclusion:**  
M05 complete. Next roadmap focus: **M06 (precision-preserving data expansion)** — `docs/milestones/M06/M06_plan.md`.

## Planned milestone roadmap

| ID | Focus |
|----|--------|
| M01 | Baseline model (first score) |
| M02 | Evaluation + targeted improvement loop (✅ closed) |
| M03 | Normalization engine (✅ closed) |
| M04 | Sentence alignment (✅ closed) |
| M05 | Data augmentation (✅ closed) |
| M06 | Precision-preserving data expansion (🚧 next) |
| M07 | Lexicon integration |
| M08 | Named entity handling |
| M09 | Rule-based improvements |
| M10 | Model upgrade |
| M11 | Training stabilization |
| M12 | Post-processing |
| M13 | Final submission system |

## Execution modes (invariant)

All milestones must support:

1. **Local execution** — e.g. `python -m akk2eng.pipeline.run` (or `python -m akk2eng.run_local`), with paths defaulting to repo-root-relative `data/` and `outputs/` (see `README.md`).
2. **Kaggle notebook execution** — self-contained notebook under `kaggle/`, competition data attached, submission written to `/kaggle/working/submission.csv`.

**Outputs** must match the competition schema: columns `id`, `translation`, one row per test `id`. Local and Kaggle runs must stay aligned on this contract even when file paths differ (`data/test.csv` vs `/kaggle/input/.../test.csv`).

M00 proved this dual path with a dummy model; M01 and later milestones keep the same contract while improving model quality.

## Determinism policy

- Pipelines must produce **identical outputs** for **identical inputs** and **identical saved model weights**
- **Random seeds** are fixed for training and inference utilities (project default: `42`)
- **No stochastic decoding** unless explicitly approved for an experiment; M01 used greedy generation (`num_beams=1`). **Deterministic beam** (`do_sample=False`, fixed `num_beams`) is allowed when documented (e.g. M02-C.3).
- **Training on GPU** may yield small run-to-run differences; compare checkpoints with `python -m akk2eng.tools.checkpoint_hash` when auditing repeatability
- **Inference** with **fixed checkpoint files** and **deterministic** decoding (greedy or fixed beam, no sampling) is the determinism target; GPU vs CPU inference for the same weights should match schema and be stable for the same code path, subject only to documented numerical edge cases

## Leaderboard tracking

| Milestone | Score |
|-----------|--------|
| M00 | 0.0 |
| M01 | 11.9 |
| M02 | ~11.6–11.9 (public LB band; see `M02_summary.md`) |

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
| v0.0.5-m02 | M02 complete — evaluation harness, error analysis, decoding optimization, lexicon validation |
| v0.0.6-m03 | M03 complete — normalization engine implemented, validated, stabilized (`NORMALIZATION_VERSION=v2`) |
| v0.0.7-m04 | M04 complete — sentence alignment implemented, leakage fixed, **+3.48 chrF** validated (split-safe) |
| v0.0.8-m05 | M05 complete — alignment expansion implemented; **regression** vs same-run control (~**−25 chrF**); precision > recall |

## Related governance docs

- RediAI v3 reference (posture): `docs/rediai33/rediai-v3.md`
- DARIA / EZRA / Foundry manuals: `docs/manuals/`
