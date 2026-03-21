# M02 run 1 — M02-C repetition control (decoding only)

**Date:** 2026-03-21  
**Lever:** single variable — greedy decoding with `repetition_penalty` + `no_repeat_ngram_size`  
**Model / weights:** unchanged (`outputs/m01_t5`)  
**Dev split:** frozen `data/splits/*`, seed 42, 90/10 (156 dev rows)

## Decoding config (`src/akk2eng/config.py`)

| Parameter | Value |
|-----------|--------|
| `do_sample` | `False` |
| `num_beams` | `1` |
| `max_new_tokens` | `256` |
| `repetition_penalty` | `1.2` |
| `no_repeat_ngram_size` | `3` |

## Metrics (sacrebleu, dev)

| Metric | Before (M02-A/B baseline) | After (M02-C) |
|--------|---------------------------|---------------|
| **chrF** | 18.6521 | **34.4085** |
| **BLEU** | 8.7224 | **32.3906** |

## Error buckets (`pipeline.analyze_errors`)

| Bucket | Before % | After % |
|--------|----------|---------|
| repetition (repeat bigram) | 87.82 | **73.72** |
| length_mismatch | 25.64 | **23.72** |
| low_overlap | 42.31 | **16.67** |
| empty | 0.0 | 0.0 |
| numeric_errors | 50.64 | 43.59 |

## Commands

```bash
python -m akk2eng.pipeline.eval --train-csv data/train.csv --model-dir outputs/m01_t5
python -m akk2eng.pipeline.analyze_errors
```

## Verdict

- **Dev chrF improved strongly** vs M02-A baseline → meets internal gate for considering a Kaggle submit (separate audit per `M02_plan.md`).
- Repetition bucket **dropped**; overlap improved, consistent with reduced looping.
- **Next (if needed):** tune penalty (e.g. 1.1) only if a later experiment regresses; no beam / lexicon / normalization until chartered.

Artifacts: `outputs/eval/*`, `outputs/analysis/*`, `outputs/experiments/exp_*/`.
