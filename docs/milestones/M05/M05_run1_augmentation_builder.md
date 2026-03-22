# M05 — Run 1: Augmentation builder (alignment expansion)

**Milestone:** M05  
**Purpose:** Build split-safe `augmented_train_sentences.csv` + `augmentation_report.json` with explicit provenance and hashes.

---

## Commands (local, repo root)

**Split-safe build (required for honest dev comparison):**

```bash
python -m akk2eng.pipeline.augment --split-safe
```

Reads:

* `data/splits/train_split.csv`
* `data/Sentences_Oare_FirstWord_LinNum.csv`

Writes (gitignored):

* `data/derived/augmentation/augmented_train_sentences.csv`
* `data/derived/augmentation/augmentation_report.json`

Verifies **zero** `oare_id` overlap with `data/splits/dev_split.csv` (process exits non-zero on leakage).

---

## Report fields (reference)

* `rows_strict` / `rows_expanded` — counts for M04-strict vs expansion-recovered pairs
* `augmentation_type_counts` — e.g. `direct_aid_strict`, `expanded_relaxed_first_word`, `expanded_english_resplit`, `expanded_partial_prefix`, …
* `train_csv_sha256`, `sentences_aid_csv_sha256`, `augmented_csv_sha256`
* `total_rows`, `original_rows`, `augmented_rows` (aligned naming: original = strict, augmented = expansion-only in report dict)

---

## As-run notes (fill after local execution)

| Field | Value |
|--------|--------|
| Date | _pending_ |
| `augmented_csv_sha256` | _from report_ |
| `rows_strict` | _from report_ |
| `rows_expanded` | _from report_ |
| `augmentation_type_counts` | _from report_ |

---

## Deferred (not M05 scope)

* **Back-translation** — documented hook only; no reverse-model training in this milestone.
* **Noise augmentation** — deferred pending Method 1 ceiling.
