# M01 Run 3 — Kaggle submission (M01-C)

**Purpose:** Auditable record of **M01-C** (notebook run, submission, leaderboard signal).

**Prerequisites:** [M01_run1.md](M01_run1.md) (M01-A), [M01_run2.md](M01_run2.md) (M01-B, `v0.0.3-m01b`).

---

## Local package (pre-upload)

**Recommended bundle (final weights only, no `checkpoint-*` folders):**

| Field | Value |
|--------|--------|
| Path | `outputs/akk2eng-m01-model.zip` |
| Size (approx.) | ~214 MB (varies with training) |
| Contents | Root-level `config.json`, `model.safetensors`, tokenizer files (`tokenizer.json`, `tokenizer_config.json`, `spiece.model`, `special_tokens_map.json`, `generation_config.json`, `training_args.bin`) |

**PowerShell (minimal zip):**

```powershell
Set-Location C:\coding\akk2eng
$files = Get-ChildItem outputs\m01_t5 -File
Compress-Archive -Path ($files | ForEach-Object { $_.FullName }) -DestinationPath outputs\akk2eng-m01-model.zip -Force
```

*(Optional full tree including `checkpoint-*` dirs: `Compress-Archive -Path outputs/m01_t5/*` — much larger; not required for inference if root save is complete.)*

---

## Kaggle dataset / model

| Field | Value |
|--------|--------|
| Model source | Kaggle Models (fine-tuned zip as model asset) |
| Slug (example) | `michael1232/akk2eng-m01-model-zip` (see Kaggle UI) |
| Upload artifact | `outputs/akk2eng-m01-model.zip` |
| Validated run reference | `docs/akk2eng-m01c-submission.ipynb` (paths as executed on Kaggle) |

---

## Notebook

| Field | Value |
|--------|--------|
| Canonical (repo) | `kaggle/akk2eng_m01_submission.ipynb` |
| As-run copy (paths) | `docs/akk2eng-m01c-submission.ipynb` |
| `INPUT_DIR` (validated) | `/kaggle/input/competitions/deep-past-initiative-machine-translation` |
| `MODEL_PATH` (validated) | `/kaggle/input/models/michael1232/akk2eng-m01-model-zip/pytorch/default/1` |

### Run confirmation

- [x] `fine-tuned: True` (fine-tuned weights loaded).
- [x] `device: cpu` (expected on default Kaggle notebook runtime).
- [x] `/kaggle/working/submission.csv` exists (`os.path.isfile` → `True`).
- [x] Header `id,translation`; row count matches `test.csv` (4 rows on sample / competition test as attached).
- [x] Non-empty translations; greedy / deterministic generation settings.

**Runtime notes:** CPU inference; average output token length ~59.5 on validated run. Sample rows printed in notebook output.

---

## Submission

| Field | Value |
|--------|--------|
| Competition | [Deep Past Initiative — Machine Translation](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/) |
| Submission accepted | Yes |
| **Public leaderboard score** | **11.9** |

---

## Verdict

```text
M01-C (Kaggle submission) — PASSED
```

---

## What you did (big picture)

You took the project from **pipeline-only (M00)** to a **working, audited baseline MT system** for Old Assyrian Akkadian → English:

- **Substrate (M01-A):** Proved CUDA training on **Blackwell** with a compatible PyTorch stack and fail-fast checks (`gpu_bringup`), documented in `M01_run1.md` and tag `v0.0.2-m01a`.
- **Training (M01-B):** Ran full **GPU FP32** fine-tuning of **T5-small**, saved a reproducible checkpoint, hashed artifacts, and verified local inference — `M01_run2.md`, `v0.0.3-m01b`.
- **Competition (M01-C):** Packaged weights, ran the **Kaggle** notebook path, submitted a valid **`submission.csv`**, and recorded a **public leaderboard score of 11.9** — this file and `v0.0.4-m01c`.
- **Posture:** Deterministic inference contract, milestone **tags**, run logs, and **Closeout Rule** so M01 stays frozen while **M02** owns the next gains.

---

## Final Closeout

M01 is officially complete.

Release tag: `v0.0.4-m01c` (Kaggle submission; public leaderboard **11.9**).

You achieved:

- Verified GPU execution (Blackwell)
- Full training + checkpoint pipeline
- Deterministic inference
- Valid Kaggle submission
- Leaderboard score: 11.9

> **Spec → System → Artifact → External Validation**

That's the entire Moonshot loop (see `docs/moonshot.md`).

This milestone establishes a fully operational Akkadian → English translation system.

**Next milestone:** M02 — evaluation + targeted improvement loop (see `docs/akk2eng.md` roadmap).

## Closeout Rule

After this:

- ❌ No further M01 changes (scope frozen at `v0.0.4-m01c`; no new M01 features or sub-phases without a **new milestone charter** and audit).
- ✅ All work moves to **M02** (`docs/akk2eng.md` roadmap).

**Frozen run logs:** `M01_run1.md`, `M01_run2.md`, and this file are the M01 authority; edit only for factual corrections or cross-links, not to backfill new work into M01.

---

## Next: M02 (where you gain points fast)

M02 is the **evaluation + targeted improvement loop**: measure, diagnose, change *one* lever, re-measure, then ship when the numbers move.

- **Eval harness:** fixed dev split from `train.csv`, comparable metrics run to run, and saved predictions so each experiment has a diffable artifact.
- **Error analysis:** group failures (names, numbers, OOV / rare signs, repetition, function words) so work is hypothesis-driven, not random tuning.
- **High-leverage fixes:** input normalization, lexicon or constraint hints, decoding / length controls, modest training changes — each tied to a before/after eval delta.
- **Contract:** keep M01 submission schema and deterministic inference defaults unless a later milestone explicitly relaxes them.

Authority: `docs/akk2eng.md` (roadmap **M02**), `docs/moonshot.md` for north-star alignment.
