# M05 Plan — Data augmentation (alignment expansion)

**Milestone:** M05  
**Title:** Data augmentation  
**Status:** **In progress**  
**Branch:** `m05-data-augmentation`  
**Baseline tag:** `v0.0.7-m04`

---

## Objective

Increase effective **sentence-aligned** training supervision **without breaking split discipline or precision**, building on M04’s validated lever (~**43.34** chrF split-safe aligned-only vs ~**39.86** baseline).

For this milestone, **“augmentation” means trustworthy recovery of additional supervised pairs** from the same official inputs—not broad synthetic generation.

---

## Locked scope (required vs deferred)

| Track | Status |
|--------|--------|
| **Method 1 — Alignment expansion** | **Required** (primary M05 deliverable) |
| **Method 2 — Back-translation** | **Deferred** (optional hook / TODO in run notes only; no reverse-model training in M05) |
| **Method 3 — Noise-based augmentation** | **Deferred** (document only if needed) |

Rationale: M04 proved **sentence alignment** is the high-signal lever. M05 tests whether **controlled recall expansion** on the same aid file and `train_split` can add rows **without** the audit dilution of multiple augmentation paradigms.

---

## Core principle (non-negotiable)

```text
NO TRAIN/DEV LEAKAGE
```

* Inputs for building training pairs: **`data/splits/train_split.csv` only** (never full `train.csv` for split-safe builds).
* **`data/splits/dev_split.csv`** must not be used in alignment, expansion, filtering, or lexicon building.
* Output must pass the same **`oare_id` overlap check** as M04 (`verify_aligned_no_dev_oare_overlap`).

---

## Method 1 — Alignment expansion

**Idea:** Recover more sentence pairs from documents that M04 strict alignment skipped or dropped, using only:

* `Sentences_Oare_FirstWord_LinNum.csv` (same official aid as M04)
* `train_split.csv` transliteration + translation

**Allowed (precision-biased):**

* Controlled **relaxed first-word** matching (bounded window, **skip if ambiguous**)
* **Alternate English segmentation** (e.g. `;`-bounded splits) when conservative splitting fails count pairing—deterministic only
* **Partial prefix alignment**: if strict alignment fails, recover the **longest verifiable prefix** of aid sentences with monotonic anchors (no whole-document guessing)

**Not allowed:**

* Whole-document guessing
* Silent inclusion of ambiguous anchor matches
* Inflating low-confidence synthetic pairs
* New external datasets or undocumented sidecar files

**Provenance (every row):**

* `augmentation_type` — `direct_aid_strict` vs expansion subtypes (`expanded_relaxed_first_word`, `expanded_english_resplit`, `expanded_partial_prefix`, …)
* `augmentation_confidence` — scalar in **(0, 1]**, policy-defined
* `source_row_id` — stable document key (`oare_id`) for traceability

---

## Implementation artifacts

| Path | Role |
|------|------|
| `src/akk2eng/data/augmentation.py` | Expansion engine + report |
| `src/akk2eng/pipeline/augment.py` | CLI |
| `data/derived/augmentation/` | **Gitignored** outputs (local) |

**Outputs:**

* `augmented_train_sentences.csv` — schema = M04 alignment columns + `augmentation_type`, `augmentation_confidence`, `source_row_id`
* `augmentation_report.json` — counts by type, input hashes, **SHA-256** of augmented CSV, dev overlap block

**Determinism:** Same inputs → identical CSV + report (row order sorted by `sentence_id` like M04).

**CLI:**

```bash
python -m akk2eng.pipeline.augment --split-safe
```

`--split-safe` reads **`train_split.csv`**, writes under `data/derived/augmentation/`, verifies **zero** `oare_id` overlap with `dev_split.csv` (fail-closed).

---

## Training & evaluation

**Training budget:** **3 epochs** for milestone comparison runs (continuity with M04 validated run). Short smokes allowed for CI / sanity.

**Example augmented continuation train:**

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/augmentation/augmented_train_sentences.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m05_t5_augmented \
  --device cuda --fp32 \
  --epochs 3
```

**Evaluation contract:** Unchanged from M02/M04 — frozen dev split, chrF primary, BLEU secondary, same decoding / lexicon / normalization defaults.

**Baseline to beat:** chrF **≈ 43.34** (M04 split-safe aligned-only).

### Exit criteria

| Tier | chrF vs frozen dev |
|------|---------------------|
| Minimum | **> 43.34** |
| Strong | **≥ 45** |
| Exceptional | **≥ 47** |

---

## Non-goals (M05)

* No model architecture upgrade
* No decoding / normalization changes
* No lexicon expansion
* No Kaggle submission until validated locally
* No **`docs/akk2eng.md`** milestone closeout update until M05 is audited (per handoff)

---

## Tests

* `tests/test_m05_augmentation.py` — determinism, schema, provenance fields, **zero dev overlap** on synthetic splits, confidence bounds

---

## Run documentation (this milestone)

* `M05_run1_augmentation_builder.md` — dataset build, report hashes, row counts by `augmentation_type`
* `M05_run2_training_eval.md` — 3-epoch train + eval vs 43.34 baseline

---

## Deferred follow-ons (not M05 unless explicitly reopened)

* **Back-translation** (English→Akkadian reverse model or heuristics) — second training contract; gate behind Method 1 outcome.
* **Noise augmentation** — only after expansion ceiling is understood.

---

## References

* Project SoT: [../../akk2eng.md](../../akk2eng.md)
* M04 closeout: [../M04/M04_summary.md](../M04/M04_summary.md)
* Tool log: [M05_toolcalls.md](M05_toolcalls.md)
* Local GPU execution (final M05 step): [M05_local_gpu_execution.md](M05_local_gpu_execution.md)
