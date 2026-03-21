# M01-C — Kaggle submission checklist

**Prerequisite:** M01-B closed (`v0.0.3-m01b`); fine-tuned weights in `outputs/m01_t5/` (see [M01_run2.md](M01_run2.md)).

**Notebook:** `kaggle/akk2eng_m01_submission.ipynb` (self-contained; no `src/` imports).

---

## 1. Package the checkpoint

From the **repo root** (PowerShell). **Recommended:** zip **files only** at `outputs/m01_t5/` (excludes `checkpoint-*` dirs; smaller upload, same inference artifacts):

```powershell
$files = Get-ChildItem outputs\m01_t5 -File
Compress-Archive -Path ($files | ForEach-Object { $_.FullName }) -DestinationPath outputs\akk2eng-m01-model.zip -Force
```

Output: **`outputs/akk2eng-m01-model.zip`** (gitignored with `outputs/`).

**Alternative (full directory, larger):** `Compress-Archive -Path outputs/m01_t5/* -DestinationPath outputs/full-m01_t5.zip -Force`

After unzip on Kaggle, `config.json` must sit under `MODEL_INPUT` (sometimes one extra folder level — list `/kaggle/input` and adjust).

**Required files inside the archive** (same as local `outputs/m01_t5/`): `config.json`, `model.safetensors` (or `pytorch_model.bin`), tokenizer files (`tokenizer.json`, `tokenizer_config.json`, `spiece.model`, etc.).

---

## 2. Create a Kaggle dataset

1. Kaggle → **Datasets** → **New Dataset**.
2. Upload `akk2eng-m01-model.zip` (or upload the unzipped folder contents).
3. Note the **dataset slug** (e.g. `yourname/akk2eng-m01-model`). After attach, the path under `/kaggle/input/` is usually `/kaggle/input/<dataset-slug>`.

---

## 3. Configure the notebook

In `akk2eng_m01_submission.ipynb`, set:

- **`INPUT_DIR`** — directory that contains competition `test.csv` (e.g. `/kaggle/input/deep-past-initiative-machine-translation` or the slug Kaggle shows).
- **`MODEL_INPUT`** — directory that contains **`config.json`** for your fine-tuned model (e.g. `/kaggle/input/akk2eng-m01-model` or `/kaggle/input/akk2eng-m01-model/m01_t5` if the zip added a subfolder).

If paths are wrong, add a cell: `import os; print(os.listdir('/kaggle/input'))` and adjust.

---

## 4. Run and submit

1. Create a **Notebook** on Kaggle; add **Add Data**: competition bundle + your model dataset.
2. Upload or paste `akk2eng_m01_submission.ipynb`, or sync from GitHub if linked.
3. **Run All**. Confirm prints show `fine-tuned: True` when using your checkpoint.
4. Confirm **`/kaggle/working/submission.csv`** exists with header `id,translation` and one row per test `id`.
5. **Submit** to the competition; record the score in `docs/akk2eng.md` → **Leaderboard tracking**.

---

## 5. Acceptance (M01-C)

- [ ] Submission accepted by Kaggle (no format errors)
- [ ] Leaderboard score recorded (target: first **non-zero** signal for M01)
- [ ] Optional: note notebook runtime and whether inference was CPU-only (expected on Kaggle)

---

## Related

- Project source of truth: `docs/akk2eng.md`
- M01 plan: `M01_plan.md`
