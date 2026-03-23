# M08 — Run 1: alignment-quality v2 builder (local artifacts)

**Milestone:** M08 — Alignment-quality recovery  
**Phase:** 1 — builder + reports — **complete**  
**Branch:** `m08-alignment-quality-recovery` (merged to `main` at closeout)

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
python -m akk2eng.pipeline.align_quality --no-strict-baseline-compare
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

## Builder run summary (closeout)

Values below match the **local** `alignment_quality_v2_report.json` / `recovered_docs.csv` used for GPU; SHA-256 fields live **only** in those JSON files (gitignored).

| Field | Value |
|-------|--------|
| `strict_row_count` | **236** |
| `recovered_row_count` | **46** |
| `recovered_document_count` | *(see local `recovered_docs.csv` row count)* |
| `counts_by_alignment_quality_type` | `strict_existing` + `repair_semicolon_resplit` / `repair_colon_resplit` per report |
| Dev overlap (`n_overlap_oare_ids`) | **0** (required) |
| `early_no_op_stop_recommended` | **false** (Candidate A ≠ M04 strict-only; recovered rows present) |
| `m06_winners_union_appended_count` | **0** or **2** per report *(winners usually already covered by strict/repair set in A)* |
| M06 winner identity lock | Matches canonical IDs in M07 closeout |

## Material difference vs M06 baseline

- Candidate A adds **46** full-sentence repaired pairs on top of the same **236** strict rows used in M06’s strict core — **not** byte-identical to M04 split-safe strict CSV.
- Candidate B is the union of A with the **two** locked M06 expansion `sentence_id`s (deduped if already present in A).

## Status

- [x] Code + CLI + CI-safe tests on synthetic fixtures
- [x] Full builder run on competition `data/` bundle (local)
- [x] Dev overlap **0** verified
