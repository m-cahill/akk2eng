# M02 run 3 — local beam search (M02-C.3)

**Objective:** Isolate **beam search** (`num_beams=3`) vs **greedy** (`num_beams=1`) with identical repetition controls, for Kaggle / BLEU-style alignment.  
**Scope:** Local only — **no** Kaggle notebook edits, **no** submit from this task.

## Isolation

| Variant | `num_beams` | `repetition_penalty` | `no_repeat_ngram_size` |
|---------|-------------|----------------------|-------------------------|
| Greedy (archived) | 1 | 1.1 | 3 |
| Beam (current) | **3** | 1.1 | 3 |

**Archives (greedy@1.1):**

- `outputs/eval/archive_m02c2_penalty_1.1_greedy/predictions_dev.csv`, `metrics.json`
- `outputs/analysis/archive_m02c2_penalty_1.1_greedy/error_buckets.json`

## Configuration (beam run)

```json
{
  "repetition_penalty": 1.1,
  "no_repeat_ngram_size": 3,
  "num_beams": 3,
  "do_sample": false,
  "max_new_tokens": 256
}
```

**Code:** `DECODE_NUM_BEAMS = 3` in `config.py`; `T5BaselineTranslator.generate()` uses it. Treated as **M02 experiment config**, not a permanent “baseline contract” (historical M01/M02-A greedy was `num_beams=1`).

## Metrics (156 dev rows, sacrebleu 2.6.0)

| Metric | Greedy @1.1 | Beam @1.1 |
|--------|-------------|-----------|
| **chrF** | 42.82 | **39.86** |
| **BLEU** | 30.13 | **43.03** |
| **repetition %** | 74.4% | **70.5%** |
| **low_overlap %** | 16.0% | **26.9%** |
| **length_mismatch %** | 23.1% | **41.0%** |

**Interpretation:** BLEU ↑ strongly (expected for beam + n-gram overlap). chrF ↓ modestly. Repetition bucket ↓ vs greedy. **Length mismatch ↑** — beam outputs often longer vs reference (tradeoff).

## Examples (excerpts ~420 chars; full rows in CSVs)

### `f9ff19ef-86d3-477d-abf4-49be2ac7e619` (silver account)

- **REF:** Excise, transport, Lā-qēp, Erra-ilī, textiles, witnesses…  
- **GREEDY:** “transport tariff / transportation tariff…” chains + many clauses.  
- **BEAM:** Shorter, more **list-like** owes / shekels phrasing; less tariff loop.

### `373f7d4f-f847-4f95-ae8d-329e944c85d3` (seal / Kanesh)

- **GREEDY:** “Seal of… Witnessed by Iddin-anum…”  
- **BEAM:** “Seal of… seal of… to Aur's dagger” — **more parallel seal formula**, slight gap artifact.

### `671e244e-b33b-4a71-89b6-e2801b671d83` (long letter)

- **GREEDY:** Dialogue + conditionals, runs long.  
- **BEAM:** “refined silver, 30 minas of good copper, 2 gap>” — **closer opening** to REF register; still hallucinated conditionals.

## Decision (per M02-C.3 brief)

| Gate | Result |
|------|--------|
| chrF ≥ 30 | **Yes** (39.86) |
| BLEU improves or stable vs greedy | **Yes** (+12.9 BLEU) |
| Structured / formulaic tendency | **Yes** on several samples; length drift is a risk |

```text
SUBMIT_TO_KAGGLE = YES
```

**Rationale:** Primary numeric gates pass; **BLEU is the lead signal** for this step and moved strongly. **Caveat:** sync **notebook** to `num_beams=3` (and keep `repetition_penalty=1.1`, `no_repeat_ngram_size=3`) before submitting — repo local path is now beam-by-default until you revert `DECODE_NUM_BEAMS` for a greedy-only line.

## Commands

```bash
python -m akk2eng.pipeline.eval --train-csv data/train.csv --model-dir outputs/m01_t5
python -m akk2eng.pipeline.analyze_errors
```

## Related

- Greedy refinement: [M02_run2_local_refinement.md](M02_run2_local_refinement.md)  
- Kaggle log (separate): [M02_run2_kaggle.md](M02_run2_kaggle.md)
