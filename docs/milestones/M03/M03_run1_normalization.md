# M03 — Run 1: Normalization engine (v1) — measurement & decision

**Milestone:** M03 — Normalization (inference-time only)  
**Measurement date:** 2026-03-22  
**Plan:** [M03_plan.md](M03_plan.md)

**Hardware / run:** Local eval, `outputs/m01_t5`, `data/train.csv`, fixed split `data/splits/*.csv`, seed **42**, `num_beams=3`, `repetition_penalty=1.1`, `no_repeat_ngram_size=3`, lexicon **on** (unchanged).

**Archived A/B artifacts (gitignored):**

- `outputs/eval/m03_ablation/metrics_norm_on.json`, `metrics_norm_off.json`
- `outputs/eval/m03_ablation/predictions_norm_on.csv`, `predictions_norm_off.csv`
- `outputs/analysis/m03_norm_on/error_buckets.json`, `m03_norm_off/error_buckets.json`

After A/B, **`outputs/eval/`** was re-run with **normalization ON** so it matches `USE_NORMALIZATION = True`.

---

## What shipped (implementation recap)

| Item | Detail |
|------|--------|
| Module | `src/akk2eng/data/normalize.py` — `normalize_transliteration()` |
| Integration | `run_inference()` — eval + Kaggle `pipeline.run` |
| Config | `USE_NORMALIZATION = True`, `NORMALIZATION_VERSION = "v1"` |
| Artifacts | `normalization: { enabled, version }` in `metrics.json` / experiment `config.json` |
| CLI | `--no-normalization` on `pipeline.eval` / `pipeline.run` |

**v1:** noise strip (before NFKC) → NFKC → lowercase → whitespace → duplicate collapse (`len(token) ≥ 3`). **Hyphens preserved.**

---

## Metric comparison

| Metric | M02 best (reference) | M03 (norm **ON**) | M03 (norm **OFF**) |
|--------|----------------------|-------------------|---------------------|
| **chrF** | **42.82** — greedy@1.1 peak ([M02_summary.md](../M02/M02_summary.md)) | **37.64** | **39.86** |
| **BLEU** | ~43 (beam=3 snapshot in repo history) | **50.14** | **43.03** |
| **low_overlap** | ~16% cited in M02 notes (bucket heuristic; not recomputed here) | **34.0%** (53/156) | **26.9%** (42/156) |
| **numeric_errors** | ~48% (same caveat) | **44.9%** (70/156) | **48.1%** (75/156) |

**Decode alignment note:** M03 numbers are **beam=3** throughout (current repo defaults). The **42.82** peak is **not** like-for-like (greedy@1.1). The correct A/B baseline for this experiment is **norm OFF = 39.86**, which matches the prior archived beam=3 eval.

**Additional buckets (same heuristic):**

| Bucket | norm ON | norm OFF |
|--------|---------|----------|
| repetition | **54.5%** (85/156) | **70.5%** (110/156) |
| length_mismatch | 39.1% (61/156) | 41.0% (64/156) |

---

## Delta analysis

**What changed (norm ON vs OFF):**

- **chrF −2.22** (39.86 → 37.64) — **primary dev proxy regressed**.
- **BLEU +7.11** — secondary metric improved (different sensitivity to length/n-grams).
- **Repetition bucket −15.9 pp** — fewer bigram-loop style outputs with normalization.
- **Numeric errors −3.2 pp** — modest improvement.
- **Low overlap +7.1 pp** — more predictions with low token-type overlap vs reference (aligned with chrF drop).

**What did not change:**

- Same checkpoint, split, seed, decoding, lexicon.
- Empty bucket remained **0** for both runs.

**Interpretation:**

- v1 normalization **materially changes** the input surface (case, logogram casing, NFKC digit/subscript forms, etc.) vs **M01 training data**, which was **not** re-normalized.
- The model still reacts deterministically: **less repetitive** generations, but **worse chrF / overlap** vs references on this dev slice — consistent with **train/inference mismatch** on the Akkadian side.
- So: normalization **did** reduce one visible noise mode (repetition) but **did not** improve the primary agreed metric (chrF) vs the no-normalization beam baseline.

---

## Example inspection (RAW → NORMALIZED → PREDICTION)

Dev rows from `predictions_norm_*.csv`; **NORMALIZED** = `normalize_transliteration(RAW)`. Predictions differ because inputs differ.

### 1. Logogram casing + determinism (short seal line)

- **RAW (excerpt):** `KIŠIB en-na-nim DUMU a-lá-bi₄-im KIŠIB a-gi-a DUMU PUZUR₄-a-šùr … IGI GÍR ša a-šùr ni-dí-in`
- **NORM (excerpt):** `kišib en-na-nim dumu a-lá-bi4-im kišib a-gi-a dumu puzur4-a-šùr … igi gír ša a-šùr ni-dí-in`  
  (case fold, NFKC on subscripts / logogram tokens, `DUMU`→`dumu`, etc.)
- **PRED (norm ON):** *Seal Ennnum, seal Ali-abum, seal Agiya, seal of Puzur-Aur, dim.gal, seal the tablet of the colony in the name of Aur-imitt.*
- **PRED (norm OFF):** *Seal of Ennnum son of Ali-abum, seal of Agiya son of Puzur-Aur; seal of Amurrum-… son of Buzi …*

### 2. Commercial / weight passage (long line; metals & numbers)

- **RAW (excerpt):** `… 1 ma-na KÙ.BABBAR … 30 ma-na URUDU SIG₅ … DUMU … ŠU.NÍGIN …`
- **NORM (excerpt):** `… 1 ma-na kù.babbar … 30 ma-na urudu sig5 … dumu … šu.nígin …`
- **PRED (norm ON):** *Shorter, more “list-like” account; mixes tin/silver wording vs OFF.*
- **PRED (norm OFF):** *Longer obligation-style wording; different entity alignment.*

### 3. Textiles / instructions (mixed case + abbrev)

- **RAW (excerpt):** `… 8 TÚG.ḪI.A ili₅-ba-ni … TÚG.ḪI.A a-na ili₅-ba-ni … šu-IŠTAR …`
- **NORM (excerpt):** `… 8 túg.ḫi.a ili5-ba-ni … túg.ḫi.a a-na ili5-ba-ni … šu-ištar …`
- **PRED (norm ON):** *Emphasizes payment / “go to the City” style resolution.*
- **PRED (norm OFF):** *Emphasizes textile debt and eponym / silver satisfaction.*

### 4. Whitespace / surface cleanup

Most dev lines are already single-spaced; v1 **collapses** runs where present. No dev row in the sample search showed **duplicate-token collapse** (`kar kar` → `kar`) on this split; that rule remains available for noisier inputs.

### 5. Noise characters

The curated noise set (ellipsis `…`, `„`, ZW characters, BOM) is **rare** in this split; impact here is dominated by **case + NFKC**, not punctuation stripping.

---

## Decision

```
SUBMIT_TO_KAGGLE = NO
```

**Rationale (per agreed gates):**

- **chrF** with norm **ON** is **below** norm **OFF** and **far below** the historical greedy peak **42.82** (understanding decode mismatch).
- **Error buckets:** repetition improved, but **low_overlap worsened** and **chrF** — the primary permission-to-submit signal in-repo — **regressed**.
- **No Kaggle submission** this milestone: avoid shipping a **distribution-shifted** input path without a matching training pass.

**Next strategic direction (out of scope for M03 code changes):** retrain or **jointly** normalize training + inference, or a **narrower** normalizer that preserves logogram/case conventions the model learned.

---

## Step 8 — Kaggle run log

**Not created:** no submission per `SUBMIT_TO_KAGGLE = NO`. If a future run clears the chrF gate, add `docs/milestones/M03/M03_run2_kaggle.md` with score and config snapshot.

---

## Notes

- Ellipsis handling: noise strip runs **before** NFKC so U+2026 is not expanded to ASCII `...`.
- **sacrebleu** version recorded in metrics: **2.6.0** (see `metrics.json`).
