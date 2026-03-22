# M05 Plan — Data augmentation

**Milestone:** M05  
**Title:** Data augmentation  
**Status:** **Seeded** (not started — plan only)  
**Baseline tag:** `v0.0.7-m04`  
**Primary intent:** explore **additional training signal** beyond the official competition bundle, under competition rules and repo governance — without breaking the M02 dev contract or the M04 alignment discipline.

## Why this milestone exists

M04 validated that **structural alignment** (sentence-level supervision) improves dev chrF **without leakage** when splits are respected. The next lever in the roadmap is **more or richer training data** — carefully scoped so augmentation does not violate data policy, does not reintroduce train/dev leakage, and remains auditable.

## Objective (draft)

Define and prototype one or more **documented, deterministic** augmentation paths (e.g. curated public text, rule-safe paraphrase, or competition-legal synthetic variants), integrate optional training inputs behind explicit CLI/config flags, and measure dev chrF vs the **M04-validated baseline** (`~43.34` chrF split-safe aligned path or pinned checkpoint — to be locked at M05 kickoff).

## Hard exit criteria (to refine at kickoff)

1. Augmentation **sources and contracts** documented in `akk2eng.md` and run notes.
2. **No** competition-data redistribution in git; generated corpora remain gitignored where required.
3. **Split discipline:** any derived training table must respect **`train_split` / `dev_split`** the same way as M04 `--split-safe`.
4. At least one **controlled** train + eval run with standard artifacts (`metrics.json`, `predictions_dev.csv`, experiment snapshot).
5. `pytest` + `ruff check src tests` green.

## Non-goals (initial)

* No mandatory model architecture upgrade (defer to M09 unless unblocker).
* No change to default decoding/normalization/lexicon without a justified bug fix.

## References

* Prior milestone closeout: [../M04/M04_summary.md](../M04/M04_summary.md)
* Tool log (to be filled): [M05_toolcalls.md](M05_toolcalls.md)
* Roadmap: [../../akk2eng.md](../../akk2eng.md) (`docs/akk2eng.md`)
