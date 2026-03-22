# M04 Run 2 — Alignment builder (implementation + local smoke)

**Date:** 2026-03-22  
**Plan:** [M04_plan.md](M04_plan.md)

## Code surface

| Path | Role |
|------|------|
| `src/akk2eng/data/alignment.py` | Line parsing, English split, Akkadian span extraction, pairing, CSV + report |
| `src/akk2eng/pipeline/align.py` | CLI: `python -m akk2eng.pipeline.align` |
| `src/akk2eng/config.py` | `DEFAULT_*` paths for aid file + derived alignment dir |
| `tests/test_m04_alignment.py` | Synthetic fixtures only |
| `tests/fixtures/m04_alignment/*.csv` | Minimal train + aid CSVs (column-aligned) |

## Train integration

* **Continuation fine-tune:** `python -m akk2eng.pipeline.train --resume-model-dir outputs/m01_t5 --train-csv <aligned.csv> ...`
* New CLI flag: `--resume-model-dir` (loads weights + tokenizer from checkpoint dir instead of base HF id only).

## Output contract (tentative — canonicalize at M04 closeout in `akk2eng.md`)

**Paths (gitignored via `data/`):**

* `data/derived/alignment/aligned_train_sentences.csv`
* `data/derived/alignment/alignment_report.json`

**Aligned CSV columns:** `sentence_id`, `oare_id`, `transliteration`, `translation`, `line_start`, `line_end`, `alignment_method`, `alignment_confidence`

**Report JSON:** `docs_processed`, `docs_aligned`, `sentence_pairs`, `method_counts`, `skip_reasons`, `aligned_csv_sha256`, `aligned_csv_path` (relative when under cwd), `alignment_report_sha256` (hash of canonical payload **before** embedding the hash field).

## Local smoke (official bundle, this workspace)

Command: `python -m akk2eng.pipeline.align`

| Metric | Value |
|--------|------:|
| `docs_processed` | 1561 |
| `docs_aligned` | 94 |
| `sentence_pairs` | 262 |
| `aligned_csv_sha256` | `8a802fdb3e378d6952739a0b91009429a9c4e23e19d223f0eb53291c2e935eaf` |

**Method counts:** `exact_count` 75, `merge_english` 18, `split_english` 1  

**Skip reasons:** `no_aid_rows` 1308, `count_mismatch` 92, `first_word_not_found` 46, `split_english_failed` 21

**Determinism:** running the builder twice on the same inputs reproduces the same `aligned_csv_sha256` (verified).

## Tests

`pytest tests/test_m04_alignment.py` — line parsing, ordering, exact/merge/split pairing, skips, stable IDs + hashes on fixtures.
