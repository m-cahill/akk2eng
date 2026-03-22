# M04 — Sentence Alignment

## Objective

Improve translation quality by aligning training data at **sentence** level.

## Rationale

Training data is largely **document-level** aligned while **test** inference is **sentence** / line-level. Reducing this structural mismatch should improve what the model learns from `train.csv` without changing the competition I/O schema.

## Scope

- Sentence segmentation (transliteration + translation)
- Alignment of transliteration ↔ translation pairs
- Generation of new training pairs suitable for fine-tuning (when approved)

## Out of scope (initial charter)

- Competition submission schema changes
- Stochastic decoding experiments without documented approval

## Exit Criteria

- chrF improvement over **M03** baseline (beam=3 norm **v2** parity point: **~39.86** on frozen dev, or successor baseline documented in run log)
- Optional stretch: public Kaggle score **> 11.9** (submit only per project discipline)

## References

- Prior milestone closeout: [../M03/M03_summary.md](../M03/M03_summary.md)
- Tool / run log: [M04_toolcalls.md](M04_toolcalls.md)
