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

## Kaggle dataset

| Field | Value |
|--------|--------|
| Dataset slug | *(operator: e.g. `username/akk2eng-m01-model`)* |
| Upload artifact | `outputs/akk2eng-m01-model.zip` |
| Created / updated | *(ISO date)* |

---

## Notebook

| Field | Value |
|--------|--------|
| Notebook | `kaggle/akk2eng_m01_submission.ipynb` |
| `INPUT_DIR` | *(path under `/kaggle/input/` to folder containing `test.csv`)* |
| `MODEL_INPUT` | *(path under `/kaggle/input/` to folder containing `config.json`)* |

### Run confirmation

- [ ] Log shows fine-tuned checkpoint in use (equivalent to: `Inference: fine-tuned checkpoint = True` / notebook `from_finetuned: True`).
- [ ] `/kaggle/working/submission.csv` exists.
- [ ] Header `id,translation`; row count matches competition `test.csv`.

**Runtime notes:** *(CPU inference expected on default Kaggle; wall time, any OOM or path fixes.)*

---

## Submission

| Field | Value |
|--------|--------|
| Submitted at (UTC) | *(operator)* |
| Competition | [Deep Past Initiative — Machine Translation](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/) |
| Submission accepted | *(Y/N)* |
| **Public leaderboard score** | ***(fill after grading — target: first non-zero for M01)*** |

---

## Verdict

```text
M01-C (Kaggle submission) — PENDING OPERATOR
```

After submit, replace with **`PASSED`** or **`NEEDS_DIAGNOSIS`** (if score 0.0 or rejected), update `docs/akk2eng.md` **Leaderboard tracking**, and close M01 per `M01_plan.md` exit condition if score **> 0**.
