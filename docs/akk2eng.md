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
| `outputs/` | Local `submission.csv` (gitignored) |

## Milestones

| ID | Summary | Status |
|----|---------|--------|
| **M00** | Kaggle-ready foundation + dummy pipeline + minimal CI + notebook stub + validated Kaggle submission | ✅ Complete (validated) |
| **M01** | First non-zero Kaggle score via baseline translation logic | 📋 Planned (see `docs/milestones/M01/M01_plan.md`) |

## M00 Validation (Kaggle)

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

## Execution Contract (M00)

The system must support two execution modes:

1. **Local:** `python -m akk2eng.pipeline.run` (or `python -m akk2eng.run_local`)
2. **Kaggle:** Notebook-based execution producing `/kaggle/working/submission.csv`

Both paths must produce identical schema-compliant outputs (`id`, `translation`).

## Related governance docs

- RediAI v3 reference (posture): `docs/rediai33/rediai-v3.md`
- DARIA / EZRA / Foundry manuals: `docs/manuals/`
