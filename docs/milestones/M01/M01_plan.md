# M01 — First Non-Zero Kaggle Score

**Status:** Planned (post-M00 closeout).

## Objective

> First non-zero Kaggle score via baseline translation logic.

M00 proved the pipeline works. M01 replaces the dummy model with **baseline translation logic** — retrieval, lexicon lookup, or minimal rule-based translation — to achieve a measurable leaderboard improvement.

## Prerequisites

- M00 closed and tagged (`v0.0.1-m00`)
- Kaggle account joined to the competition
- `kaggle/akk2eng_m00_submission.ipynb` (or updated notebook) verified against live dataset path

## In Scope (to be detailed)

- Replace dummy inference with baseline logic:
  - Retrieval from `train.csv`, or
  - Lexicon lookup (`OA_Lexicon_eBL.csv`), or
  - HuggingFace / pretrained seq2seq (T5, mBART, etc.)
- Achieve non-zero score on leaderboard
- Maintain submission format and Kaggle compatibility
- Preserve deterministic pipeline

## Out of Scope

- Full neural model fine-tuning
- Complex preprocessing pipeline
- Coverage/security CI expansion

## Next Steps

1. Design baseline: retrieval from `train.csv`, lexicon lookup (`OA_Lexicon_eBL.csv`), or hybrid.
2. Implement in `pipeline/inference.py` (or new module).
3. Update notebook or keep parity with local pipeline.
4. Submit; iterate within 5 submissions/day budget.
