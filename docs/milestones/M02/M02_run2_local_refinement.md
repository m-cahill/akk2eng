# M02 run 2 — local decoding refinement (M02-C.2)

**Goal:** Soften `repetition_penalty` after Kaggle dip (11.9 → 11.6) on 1.2; **single-variable** change only.  
**Scope:** Local only — no notebook edits, no Kaggle submit from this task.

## Repo state

| Field | Value |
|-------|--------|
| Config commit | `ba11195` (`DECODE_REPETITION_PENALTY = 1.1`) |
| Splits | **Not** regenerated (`--force-splits` not used) |
| Weights | `outputs/m01_t5` (unchanged) |

## 1. Configuration (M02-C.2)

```json
{
  "repetition_penalty": 1.1,
  "no_repeat_ngram_size": 3,
  "num_beams": 1,
  "do_sample": false,
  "max_new_tokens": 256
}
```

**Prior run (M02-C, archived):** `repetition_penalty`: **1.2** (same other fields).

## Artifacts

| Role | Path |
|------|------|
| Backup pred + metrics @1.2 | `outputs/eval/archive_m02c_penalty_1.2/predictions_dev.csv`, `metrics.json` |
| Buckets @1.2 (recomputed on archive preds) | `outputs/analysis/archive_m02c_penalty_1.2/error_buckets.json` |
| Current @1.1 | `outputs/eval/*`, `outputs/analysis/*`, `outputs/experiments/exp_<UTC>/` |

## 2. Metric comparison

| Metric | Previous (penalty **1.2**) | New (penalty **1.1**) |
|--------|---------------------------|------------------------|
| **chrF** | 34.41 | **42.82** |
| **BLEU** | 32.39 | **30.13** |
| **repetition %** (repeat-bigram bucket) | 73.7% | **74.4%** |
| **low_overlap %** | 16.7% | **16.0%** |
| length_mismatch % | 23.7% | **23.1%** |
| numeric_errors % | 43.6% | **48.1%** |

*Sources: archived vs current `metrics.json` and `error_buckets.json` (156 dev rows, sacrebleu 2.6.0).*

## 3. Example outputs (REF vs pred@1.2 vs pred@1.1)

Excerpts ~480 chars; full strings in CSVs above.

### Sample A — `f9ff19ef-86d3-477d-abf4-49be2ac7e619` (long silver account)

- **REF:** 10 minas refined silver, excise, transport, Lā-qēp, Erra-ilī, textiles, packets, witnesses…  
- **@1.2:** Opens with transport-tariff phrasing; amounts/entities somewhat scrambled vs REF.  
- **@1.1:** Similar opening; extends with more clauses (“import tariff”, “3 -textiles”) — **more verbose**, different errors; not a pure “more natural” win on this row.

### Sample B — `671e244e-b33b-4a71-89b6-e2801b671d83` (letter to Mannum-kī-Aššur)

- **@1.2:** Narrative loops reduced vs pre–M02-C era; ends mid-thought.  
- **@1.1:** Different wording (“2 gap>”, quoted dialogue); still **truncated** / incomplete at max length.

### Sample C — `6443bc8f-a0c8-4626-af75-b83c65364f05` (Šalim-Aššur / textiles)

- **@1.2:** Shorter, somewhat coherent conditional ending.  
- **@1.1:** **More** “seized / colony” repetition and **longer** run-on — **worse** on this row qualitatively despite higher corpus chrF.

### Sample D — `373f7d4f-f847-4f95-ae8d-329e944c85d3` (seal / Kanesh)

- **@1.2:** Extra conditional on debt.  
- **@1.1:** Tighter; adds “Witnessed by Iddin-anum” — **closer** to seal-witness style.

### Sample E — `091abe17-bf55-4912-b402-15442365622a` (13 minas tin)

- **Both** preds drift from REF; **@1.1** continues with more **invented** obligations (“gold and the smuggling”) — **riskier** phrasing.

**Truncation:** Still present on long rows (`max_new_tokens=256` unchanged).

## 4. Decision (numeric-first, then qualitative)

| Gate | Result |
|------|--------|
| chrF ≥ 30 | **Yes** (42.82) |
| Repetition ≪ 87.8% (pre–M02-C baseline) | **Yes** (~74%) |
| Qualitative tie-breaker | **Mixed** per row; corpus-level chrF **strongly** up, BLEU slightly down |

```text
SUBMIT_TO_KAGGLE = YES
```

**Rationale:** Mandatory numeric gates pass; repetition remains **far** below the original 87.8% failure rate. **chrF +8.4** points vs 1.2 suggests better dev alignment with references on aggregate — consistent with **retrying Kaggle** after the 11.6 dip on 1.2. **Caveat:** validate on **test** samples for truncation and hallucination; if LB regresses again, next knob is **not** in this doc (per stop condition).

---

## Commands used

```bash
# Backup (manual copy to archive_m02c_penalty_1.2/)
python -m akk2eng.pipeline.analyze_errors \
  --predictions-csv outputs/eval/archive_m02c_penalty_1.2/predictions_dev.csv \
  --output-dir outputs/analysis/archive_m02c_penalty_1.2

# After config DECODE_REPETITION_PENALTY = 1.1
python -m akk2eng.pipeline.eval --train-csv data/train.csv --model-dir outputs/m01_t5
python -m akk2eng.pipeline.analyze_errors
```

## Related

- Kaggle submit log (separate): [M02_run2_kaggle.md](M02_run2_kaggle.md)  
- Prior decode step: [M02_run1_m02c_decoding.md](M02_run1_m02c_decoding.md)
