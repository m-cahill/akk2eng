# M02 run 4 — lexicon post-processing (M02-D)

**Objective:** Surgical **English prediction** cleanup: replace leaked Akkadian surfaces (logograms, copy-through tokens) using **eBL `form` → `lexeme`** only, with **train-filtered** entries and **token-boundary-safe** regex.  
**Scope:** Repo inference/eval path only — **no** tokenizer / training / input changes; **no** Kaggle notebook edit in this task.

**Repo commit:** `de26161`.

## Design (locked)

| Rule | Implementation |
|------|------------------|
| Source | `docs/kaggledocs/OA_Lexicon_eBL.csv` — columns **`form` → `lexeme`** only (not `norm`) |
| Where applied | After `translate()` in `run_inference()` → `prediction = apply_lexicon_postprocess(prediction, pairs)` |
| Train filter (Option B) | Include `form` only if it appears as a **whitespace token** in `train.csv` transliterations (multi-word `form` uses boundary regex on full lines) |
| Unambiguous | Drop `form` if CSV maps it to **more than one** distinct `lexeme` |
| Safe lexeme | Non-empty; **no internal whitespace** (reject multi-word glosses) |
| Min length | `len(form) >= 3` |
| Cap | `LEXICON_MAX_ENTRIES = 400` (target band ~200–400) |
| Replacement | `(?<![\w])` + `re.escape(form)` + `(?![\w])` — **full tokens only** |

**Code:** `src/akk2eng/lexicon/postprocess.py`, wired from `pipeline/inference.py`.  
**Config:** `USE_LEXICON`, `DEFAULT_LEXICON_CSV`, `LEXICON_MAX_ENTRIES` in `config.py`; mirrored in eval `metrics.json` / experiment `config.json` under `lexicon` + `USE_LEXICON` / `DEFAULT_LEXICON_CSV` / `LEXICON_MAX_ENTRIES`.

## Archive (beam baseline before this run)

Pre-lexicon **beam@1.1** dev artifacts (unchanged decoding):

- `outputs/eval/archive_m02c3_beam/predictions_dev.csv`, `metrics.json`, `eval_summary.txt`
- `outputs/analysis/archive_m02c3_beam/error_buckets.json`

## Metrics (156 dev rows, sacrebleu 2.6.0, beam decode unchanged)

| Metric | Beam (archived) | + Lexicon post-process |
|--------|-----------------|-------------------------|
| **chrF** | 39.8601 | **39.8601** (identical) |
| **BLEU** | 43.0344 | **43.0344** (identical) |
| **low_overlap %** | 26.92 | **26.92** |
| **numeric_errors %** | 48.08 | **48.08** |

**Row-level diff:** `0 / 156` dev predictions changed vs archived beam CSV (no leaked lexicon `form` values matched as standalone tokens in current English outputs).

## Examples

### Controlled illustration (not from dev — shows intended behavior)

- Input prediction: `He owes 5 KÙ.BABBAR and leaves.`
- After map entry `(KÙ.BABBAR → kaspu)` (if present in built pairs): `He owes 5 kaspu and leaves.`
- Substring guard: `XKÙ.BABBAR` → **unchanged** (no `\w` boundary before `K`).

### Dev set

No before/after pairs on dev this run — **post-process was a no-op** on all rows. The harness is in place for Kaggle/test rows where logograms or copy-through surfaces appear.

## Decision

| Gate | Result |
|------|--------|
| Outputs stable / no corruption | **Yes** — identical dev predictions |
| chrF / BLEU | **Stable** (expected when no tokens match) |
| numeric_errors / low_overlap | **Unchanged** (same preds) |
| Safe wiring + audit fields | **Yes** — `lexicon` block in artifacts |

```text
SUBMIT_TO_KAGGLE = NO_NEW_SUBMIT_REQUIRED
```

**Rationale:** Dev chrF did not move; **no leaderboard justification** from this step alone. **Keep** beam submit line from [M02_run3_local_beam.md](M02_run3_local_beam.md). Optional: mirror the same post-process in the Kaggle notebook if you want leak cleanup on **test** (repo `pipeline.run` already applies it when `USE_LEXICON` is true).

## Commands

```bash
# Baseline comparison archive (done once for this milestone)
# outputs/eval/archive_m02c3_beam/

python -m akk2eng.pipeline.eval --train-csv data/train.csv --model-dir outputs/m01_t5
python -m akk2eng.pipeline.analyze_errors --output-dir outputs/analysis/m02_run4_lexicon

# A/B: disable lexicon
python -m akk2eng.pipeline.eval --no-lexicon
```

## Related

- Beam step: [M02_run3_local_beam.md](M02_run3_local_beam.md)  
- Tool log: [M02_toolcalls.md](M02_toolcalls.md)
