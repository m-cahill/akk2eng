# M03 — Normalization Engine

## Objective

Improve translation quality by reducing transliteration noise and increasing token consistency **before** tokenization (inference-time only).

## Scope

- `src/akk2eng/data/normalize.py` — `normalize_transliteration()` (**v2** default)
- Single integration point: `run_inference()` (covers `pipeline.eval` and `pipeline.run`)
- **Inputs only** — do not normalize reference English or model predictions (would corrupt metrics)
- **v2 (conservative):** explicit noise-character deletion, whitespace cleanup, immediate duplicate-token collapse (tokens length ≥ 3). **No NFKC, no lowercase** — preserves training token identity.
- **v1 (retired):** included NFKC + lowercase — train/inference mismatch; see [M03_run1_normalization.md](M03_run1_normalization.md).
- **Hyphens preserved** — no hyphen → space (avoids distribution shift vs M01 training)

## Out of scope (M03)

- Retraining / training data edits
- Decoding / model changes
- Hyphen restructuring

## Status

✅ **Closed** — `v0.0.6-m03`. See [M03_summary.md](M03_summary.md), [M03_audit.md](M03_audit.md). v2 normalization is **safe**; v1 showed regression; no dev chrF lift from norm alone.

## Exit Criteria (as-run)

- Measured v1/v2 behavior documented; **v2** default shipped.
- Stretch (chrF beat / LB **> 11.9**) **not** met without further data work → **M04**.

## References

- Prior milestone closeout: [../M02/M02_summary.md](../M02/M02_summary.md)
- v1 run log: [M03_run1_normalization.md](M03_run1_normalization.md)
- v2 run log: [M03_run2_conservative_norm.md](M03_run2_conservative_norm.md)
- Tool / run log: [M03_toolcalls.md](M03_toolcalls.md)
