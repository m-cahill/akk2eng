# M04 Run 1 — Baseline pin and alignment data audit

**Date:** 2026-03-22 (branch `m04-sentence-alignment`)  
**Plan:** [M04_plan.md](M04_plan.md)

## 1. Sentence aid file (environment fact)

**Resolved path (this machine):**  
`c:\coding\akk2eng\data\Sentences_Oare_FirstWord_LinNum.csv`

Relative to repo root: `data/Sentences_Oare_FirstWord_LinNum.csv`

> Do **not** hardcode this path in governance docs as a global contract; it is the standard competition layout when data are unzipped into `data/`.

### Schema (columns)

| Column | Role |
|--------|------|
| `display_name` | Human label |
| `text_uuid` | **Join key to `train.oare_id`** (UUID string) |
| `sentence_uuid` | Stable sentence id (used in `sentence_id` output) |
| `sentence_obj_in_text` | OARE ordering hint |
| `translation` | English line from OARE (reference; pairing uses **train `translation`** split/merged) |
| `first_word_transcription` | First word (transcription tier); may be empty |
| `first_word_spelling` | Syllabic spelling tier |
| `first_word_number`, `first_word_obj_in_text` | OARE object indices |
| `line_number` | **float64** in bundle; integer part = line, fractional `.01`/`.02`/`.03` encodes prime marks (`1'`, `1''`, …) |
| `side`, `column` | Tablet face / column; used for deterministic sort |

## 2. Coverage vs `train.csv` (from audit JSON)

Machine-generated snapshot: `outputs/alignment/baseline_alignment_audit.json` (gitignored).

Summary:

| Metric | Value |
|--------|------:|
| `train_row_count` | 1561 |
| `unique_train_oare_ids` | 1561 |
| `train_docs_with_aid_rows` | **253** |
| `train_docs_without_aid_rows` | **1308** |
| `unique_aid_text_uuids` (full aid file) | 1700 |
| Rows with fractional `line_number` | 259 (encoding primes) |

**Implication:** the aid file only covers **~16%** of training documents. The alignment builder is expected to **skip** the rest with `no_aid_rows`; M04 training on aligned data alone uses a **subset** of the corpus unless a later fallback (mixed curriculum) is explicitly run per plan.

## 3. M04 baseline — repo-default eval (pinned target)

**Command:** `python -m akk2eng.pipeline.eval` (defaults; frozen splits, no `--force-splits`).

| Item | Value |
|------|--------|
| Checkpoint / `model_dir` | `outputs/m01_t5` |
| Decoding | `num_beams=3`, `repetition_penalty=1.1`, `no_repeat_ngram_size=3`, `do_sample=false`, `max_new_tokens=256` |
| Lexicon | `USE_LEXICON=True`, 400 entries, train-filtered forms |
| Normalization | `USE_NORMALIZATION=True`, `NORMALIZATION_VERSION=v2` |
| Dev split | seed **42**, **10%** dev (`data/splits/*`) |
| **chrF (primary)** | **39.8600826251388** |
| BLEU (secondary) | 43.034372510596235 |

Artifacts: `outputs/eval/metrics.json`, `outputs/eval/predictions_dev.csv`, latest `outputs/experiments/exp_<UTC>/`.

## 4. Default vs archived “best” dev result

| Variant | chrF | Notes |
|---------|------|--------|
| **Repo default now** (beam=3, norm v2, lex on) | **~39.86** | Same as M03 parity baseline; operational M04 hurdle. |
| **Archived M02 greedy @1.1** (documented in `docs/akk2eng.md`) | **~42.82** peak on frozen dev | Different **decoding** contract; **not** the current repo default. |

**Conclusion:** M04 experiments should beat the **pinned M04 baseline (~39.86 chrF)** using the **current** eval defaults unless the milestone explicitly changes decoding (out of scope for M04 per plan).

## 5. Edge cases / ambiguity (logged)

* **`line_number` as float:** `.01`–`.03` suffixes encode prime marks; parser maps these to sort keys `(base, prime_level)`.
* **Aid vs train transliteration:** first-word matching uses NFKC + subscript digit normalization and hyphen/whitespace-stripped keys; orthographic drift → `first_word_not_found` skips.
* **English pairing:** conservative regex split + at most **one** merge or **one** split; otherwise `count_mismatch` or `split_english_failed`.

Further deferrals belong in M04 closeout audit if still open.
