# M02 — Evaluation + fast leaderboard climb

**Project:** akk2eng  
**Milestone:** M02  
**Phase:** Measurement-first improvement  
**Status:** In progress (planning / execution)

**Prerequisite:** M01 complete (`v0.0.4-m01c`); public leaderboard **11.9** (see `docs/milestones/M01/M01_run3.md`).  
**North star alignment:** `docs/moonshot.md`, `docs/akk2eng.md`.

## Objective

Improve **Kaggle leaderboard score** through a **tight eval loop**: every change is measured on a **fixed dev split** before it touches Kaggle. Optimize for **fast signal** (hours-to-days iterations), not architectural theater.

> **Not the goal:** random hyperparameter sweeps, huge retrains without a hypothesis, or breaking the M01 submission / determinism contract without an explicit decision.

## Core principle

> **One lever per experiment** — reproducible metric delta, saved predictions, short run log.

Strategy mirror (from `M01_run3.md` **Highest ROI next moves**):

1. **Eval harness first** — dev split + primary metric + artifacted predictions.  
2. **Error analysis (M02 core)** — buckets, counts, sprint from the largest gap.  
3. **Lexicon injection (M06 early leverage)** — small, auditable gloss when buckets justify it.  
4. **Simple decoding tweaks** — length, beam *only if harness proves it*, repetition control; default stays **deterministic** unless a milestone widens policy.  
5. **Normalization layer (M03 preview)** — transliteration cleanup / noise removal when the harness shows gain.  
6. **Cheap training nudges** — only after the above are exhausted or clearly parallel.  
7. **M01 contract** — schema `id,translation`; document any intentional relaxation.

## Scope

### In scope

| Workstream | Intent |
|------------|--------|
| **Dev eval CLI / module** | Extend or replace ad-hoc `pipeline.validate` with: fixed `SEED` split, **BLEU/chrF/SacreBLEU** (or competition-aligned proxy), write `outputs/eval/*.json` + optional `predictions.csv`. |
| **Error buckets** | **Targeted error analysis workflow** (Step 3): reproducible table, bucket tags, ranked counts, samples + hypothesis before each fix. |
| **Targeted fixes** | Normalization pass (flag-guarded), prompt tweaks, tiny lexicon table, `generate()` args — each behind a **single** config or flag. |
| **Re-submit discipline** | Kaggle submit only when dev metric moves **up** vs last tagged baseline; record score in `docs/akk2eng.md` and a run log (e.g. `M02_run1.md` when created). |

### Out of scope (defer)

- Full **M03** normalization engine (only **preview** slices that win on the harness).  
- Full **M06** lexicon pipeline (only **injection** experiments with provenance).  
- New backbone model (**M09**) unless eval proves ceiling hit with smaller levers.  
- Stochastic decoding as default (requires explicit governance note).

## Implementation plan (suggested order)

### Step 1 — Baseline lock

- Record **M01 dev metric** on the chosen split (even if rough): document command + hash of `train.csv` slice or split seed in `M02_toolcalls.md`.  
- Ensure `outputs/m01_t5/` (or current best checkpoint) is the **reference weights** for comparisons.

### Step 2 — Eval harness (M02 deliverable)

- Add `python -m akk2eng.pipeline.eval` (or equivalent) with: `--train-csv`, `--model-dir`, `--val-fraction` / `--seed`, metric output to stdout + JSON file.  
- Optional: `--output-predictions` for diffing runs.  
- **CI:** CPU-only smoke (tiny `max-rows`) so the module imports and runs.

### Step 3 — Targeted error analysis workflow (M02 core)

Use this **after** you have a fixed dev split and **saved predictions + references** (from Step 2 or a one-off export). Goal: answer **what the model gets wrong systematically**, not to eyeball random rows.

1. **Freeze inputs** — Same `train.csv` revision, `--seed`, `val_fraction` (or row range) as the eval harness; record in `M02_toolcalls.md`.
2. **Build a table** — One row per dev example: `id` (or index), `transliteration`, `reference`, `prediction`, optional token lengths / char counts.
3. **Define buckets** (tag each row with one or more flags):
   - **Repetition** — repeated n-grams or duplicated phrases in `prediction` vs reference length.
   - **Named / lexical** — proper-like tokens, gloss mismatches, or OOV-ish transliteration spans (heuristic: digits, parentheses, rare subword splits if you log them later).
   - **Numeric / metatext** — numbers, line markers, broken punctuation.
   - **Under-translation** — very short `prediction` vs `reference` length ratio below a threshold.
   - **Hallucination / drift** — content in `prediction` with weak lexical overlap with `reference` (simple overlap score as a first pass).
4. **Count and rank** — Sort buckets by count and by **mean penalty** (if you have per-row loss or 1−BLEU proxy); pick **one** top bucket for the next sprint.
5. **Sample for humans** — 5–10 rows per top bucket; paste into `M02_toolcalls.md` or a short `M02_error_digest.md` (create when needed) with **hypothesis** (“repetition from greedy decode”, “OA sign X under-translated”, etc.).
6. **Hand off** — Next experiment must cite bucket + hypothesis in the tool log before code changes.

**Deliverable shape:** script under `src/akk2eng/` or `tools/`, or a notebook under `docs/` / `notebooks/` — but **outputs** must be reproducible from CLI + paths (no click-only workflows in the audit path).

### Step 4 — Fast climb iterations

For each iteration:

1. Hypothesis from error table.  
2. Implement **one** change.  
3. Re-run eval; compare JSON / predictions to baseline.  
4. If improved: optional Kaggle notebook refresh + submit; update leaderboard row.

Prioritize **lexicon hints**, **normalization**, **decoding** before long retraining.

## Quick +5 score strategy (tactical sprint)

**Intent:** Stack **high-leverage, cheap** changes first to move the **public leaderboard** meaningfully above the M01 baseline (**11.9**). **+5** (i.e. toward **~16.9**) is a **stretch target**, not a guarantee — competition metrics are opaque and non-linear; every step still needs **dev harness** confirmation before a Kaggle burn.

**Order (stop early if a step fails on dev):**

| Priority | Move | Why it often pays |
|----------|------|-------------------|
| A | **Lock eval + error digest** (Step 2–3) in one session | Avoids fixing the wrong problem. |
| B | **Transliteration normalization** (M03 preview) | Reduces tokenizer noise; fast if buckets show inconsistent unicode / punctuation / spacing. |
| C | **Tiny lexicon injection** (M06 preview) — tens to low hundreds of high-confidence glosses | Akkadian is lexically sparse in the model; entity/lemma errors are common failure mode. |
| D | **Decoding** — `max_new_tokens`, repetition / n-gram block, then **small beam** (2–4) *only if* repetition or truncation buckets dominate | Cheap inference-side gain; log loss of determinism if you leave greedy. |
| E | **Short retrain** — +1–2 epochs, LR schedule tweak, or slightly larger batch *only if* A–D plateau on dev | Higher cost; only when hypothesis says capacity/data noise, not decoding. |

**Rules:** one lever per submit; record **before/after** dev metric + Kaggle score in `M02_toolcalls.md`; do not stack B+C+D in one Kaggle submit without a local combined eval pass.

## Acceptance criteria

| Requirement | Target |
|-------------|--------|
| Reproducible dev metric | Same command + seed → same number (within documented GPU float noise if any CUDA eval). |
| Before/after artifacts | Saved metrics + optional predictions for baseline and each winning experiment. |
| Leaderboard | **Strict improvement** vs M01 **11.9** on at least one public submit (document in `akk2eng.md`). |
| Governance | M02 changes documented in `M02_toolcalls.md`; no silent breaking of submission schema. |

## Risks

| Risk | Mitigation |
|------|------------|
| Dev metric ≠ Kaggle metric | Periodically re-align with competition scoring notes; keep Kaggle submits sparse but real. |
| Overfitting dev split | Refresh split only with documented rationale; prefer stable held-out slice. |
| Determinism drift (beam, etc.) | Log decoding config in run artifacts; default greedy until proven. |

## Exit condition

M02 is **complete** when:

- Dev harness is **stable and scripted**, and  
- At least **one** Kaggle submission documents **score > 11.9** (public LB), with run log + toolcalls updated.

Then proceed to **M03** (normalization engine) and **M06** (lexicon) per roadmap, or continue M02-style iteration under a new charter.

## Related

- ROI ordering: `docs/milestones/M01/M01_run3.md` (section **Next: M02**).  
- Tool log: [M02_toolcalls.md](M02_toolcalls.md).  
- Source of truth: `docs/akk2eng.md`.
