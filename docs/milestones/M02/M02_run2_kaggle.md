# M02 run 2 — Kaggle validation (M02-C decoding)

**Intent:** Confirm dev chrF gains transfer to **public leaderboard** (vs M01 baseline **11.9**).

## Code alignment

| Field | Value |
|-------|--------|
| **Repo commit (local decode)** | `cb9cd8aaeca816202a4bcb6a5ab0fde875ca3f63` |
| **Repo commit (Kaggle notebook aligned)** | `f047f17` *(or later; notebook must match decode table below)* |
| **Notebook** | `kaggle/akk2eng_m01_submission.ipynb` |
| **Weights** | Same as M01-C: fine-tuned `outputs/m01_t5` exported to Kaggle (`MODEL_INPUT`) |

## Decoding params (must match `src/akk2eng/config.py`)

| Parameter | Value |
|-----------|--------|
| `do_sample` | `False` |
| `num_beams` | `1` |
| `max_new_tokens` | `256` |
| `repetition_penalty` | `1.2` |
| `no_repeat_ngram_size` | `3` |

**Not in this run:** beam search, lexicon, normalization.

## Execution checklist

1. Upload/sync notebook from repo (or paste cells); set `INPUT_DIR` / `MODEL_INPUT`.
2. Run all cells; confirm `submission.csv` under `/kaggle/working/`.
3. Submit **once** (no other changes vs this spec).
4. Record public LB below and commit an update to this file if desired.

## Results *(fill after submit)*

| Item | Value |
|------|--------|
| **Submission date (UTC)** | *(pending)* |
| **Public leaderboard score** | *(pending)* |
| **Δ vs M01 baseline (11.9)** | *(pending)* |
| **Notes** | e.g. truncation on long lines, repetition still visible in samples — optional |

## Interpretation guide

| Outcome | Action |
|---------|--------|
| LB **>** 11.9 | M02-C validated on competition metric → continue M02-C.2 tuning if needed |
| LB **≈** 11.9 | Possible metric / distribution mismatch → keep dev as primary gate; consider small decode nudge |
| LB **<** 11.9 | Review truncation / penalty strength → M02-C.2 Option A/B/C per plan |

## Related

- Dev proof + metrics: [M02_run1_m02c_decoding.md](M02_run1_m02c_decoding.md)  
- Tool log: [M02_toolcalls.md](M02_toolcalls.md)
