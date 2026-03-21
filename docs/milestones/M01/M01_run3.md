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
| **Public leaderboard score** | **Non-zero** (M01 exit criterion met). *Paste exact numeric metric from Kaggle UI into `docs/akk2eng.md` leaderboard table when you want the ledger to show the precise value.* |

---

## Verdict

```text
M01-C (Kaggle submission) — PASSED
```

---

## Final Closeout

M01 is officially complete.

Release tag: `v0.0.4-m01c` (Kaggle submission + non-zero leaderboard signal).

The system has achieved:

- Verified GPU execution (Blackwell)
- Full training + checkpoint pipeline
- Deterministic inference
- Valid Kaggle submission
- First non-zero leaderboard signal (public LB)

This milestone establishes a fully operational baseline translation system.

**Next milestone:** M02 — evaluation + improvement loop (see `docs/akk2eng.md` roadmap).

**Governance:** No further M01 scope without a new milestone charter; product work proceeds under M02+.
