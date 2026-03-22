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

## As-run notes (filled)

| Field | Value |
|--------|--------|
| Date | **2026-03-22** (builder executed) |
| `augmented_csv_sha256` | `9f8a852b5115d22df91bc98b53948f0e48a9e04b246d356b5b4572edd5fb70e5` |
| `augmentation_report_sha256` | `9ba6008ca8d11b868c1d16901ce9b3cc9263d2a8a8758b062c7292b5d24d5f53` |
| `rows_strict` | **236** |
| `rows_expanded` | **306** |
| `total_rows` | **542** |
| `docs_strict` | **85** |
| `docs_expanded` | **59** |
| `docs_processed` | **1405** |
| `augmentation_type_counts` | See below |
| Dev overlap | **`passes: true`** (`n_overlap_oare_ids`: 0) |

### `augmentation_type_counts` / `by_type`

| Type | Rows |
|------|------|
| `direct_aid_strict` | 236 |
| `expanded_partial_prefix` | 296 |
| `expanded_partial_prefix_relaxed` | 8 |
| `expanded_english_resplit` | 2 |

### Input hashes (from report)

| Input | SHA-256 |
|-------|---------|
| `train_split.csv` | `638bbcab334688d9d8c2b303e85ddc63df3cc737d2cc1c91aa215cfade93d2c9` |
| `Sentences_Oare_FirstWord_LinNum.csv` | `ec8f5b17047fcfa1ed59290f29248bf8836bfc607928719bb9bb4c840c3cb470` |

### Skip reasons (strict path, docs with aid but no final row output)

| Reason | Count |
|--------|------|
| `no_aid_rows` | 1177 |
| `count_mismatch` | 56 |
| `first_word_not_found` | 28 |

---

## Interpretation (builder)

* **+306** expansion-only sentence rows on top of the **236** M04-strict rows → **~129%** more sentence pairs vs split-safe aligned-only, still **train-split-only** and **dev-clean**.
* Most expansion mass is **`expanded_partial_prefix`** (296 rows): longest verifiable aid prefix when full strict alignment fails—consistent with the precision-biased design.
* **`expanded_relaxed_first_word`** did not appear in this run; **`expanded_english_resplit`** contributed **2** rows.

---

## Deferred (not M05 scope)

* **Back-translation** — documented hook only; no reverse-model training in this milestone.
* **Noise augmentation** — deferred pending Method 1 ceiling.
