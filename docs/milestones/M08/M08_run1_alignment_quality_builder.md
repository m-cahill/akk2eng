# M08 — Run 1: alignment-quality v2 builder (local artifacts)

**Milestone:** M08 — Alignment-quality recovery  
**Phase:** 1 — builder + reports  
**Branch:** `m08-alignment-quality-recovery`

## Command (repo root, `data/` populated)

```bash
python -m akk2eng.pipeline.align_quality
```

### Defaults

| Input | Path |
|-------|------|
| Train split | `data/splits/train_split.csv` |
| Dev split | `data/splits/dev_split.csv` |
| Sentences aid | `data/Sentences_Oare_FirstWord_LinNum.csv` |
| M06 Policy A baseline | `data/derived/selection/strict_plus_highconf_cap50.csv` |
| M04 strict (no-op fingerprint) | `data/derived/alignment/aligned_train_sentences_split.csv` |

### Useful overrides

```bash
# If M04 strict CSV is missing (no-op gate skips strict fingerprint compare)
python -m akk2eng.pipeline.align_quality --no-strict-baseline-compare

# Custom output directory
python -m akk2eng.pipeline.align_quality --output-dir data/derived/alignment_quality
```

## Outputs (gitignored under `data/derived/alignment_quality/`)

| File | Purpose |
|------|---------|
| `aligned_train_sentences_quality_v2_split.csv` | **Candidate A** |
| `alignment_quality_v2_report.json` | Hashes, counts, repair rejections, early no-op flags |
| `recovered_docs.csv` | One row per successfully repaired document |
| `aligned_train_sentences_quality_v2_plus_m06.csv` | **Candidate B** (A ∪ M06 winners) |
| `alignment_quality_v2_plus_m06_report.json` | Candidate B audit |

## Fill after local run

Paste from `alignment_quality_v2_report.json` / `alignment_quality_v2_plus_m06_report.json`:

| Field | Value |
|-------|-------|
| `strict_row_count` | |
| `recovered_row_count` | |
| `recovered_document_count` | |
| `counts_by_alignment_quality_type` | |
| Top `repair_rejection_counts` keys | |
| `output_candidate_a_sha256` | |
| `output_candidate_b_sha256` | |
| `early_no_op_stop_recommended` | |
| `early_no_op_gate_candidate_a_strict_fingerprint_available` | `false` if M04 strict CSV missing — then **A gate is not asserted** (`early_no_op_gate_candidate_a` stays `false`) |
| `m06_winners_present_in_candidate_a_sentence_ids` | |
| `m06_winners_union_appended_count` | |
| Dev overlap (`n_overlap_oare_ids`) | **must be 0** |

## Material difference vs M06 baseline

- If `early_no_op_gate_candidate_b_identical_to_m06_baseline` is **true**, Candidate B matches M06 baseline on canonical core columns → **no training gain expected** from B.
- If Candidate A adds recovered rows, document **repair paths used** (`repair_semicolon_resplit` vs `repair_colon_resplit`) in `recovered_docs.csv`.

## Status

- [x] Code + CLI + CI-safe tests on synthetic fixtures
- [ ] Full builder run on competition `data/` bundle — **pending local execution**
