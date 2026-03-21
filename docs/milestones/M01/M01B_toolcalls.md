# M01-B — Tool calls (execution log)

Copy-paste oriented. Adjust paths if your repo root differs.

## Environment

```powershell
Set-Location C:\coding\akk2eng
.\.venv\Scripts\Activate.ps1
```

## 1. Substrate re-check (recommended)

```powershell
python -m akk2eng.tools.gpu_bringup
```

## 2. Optional GPU smoke before full run

```powershell
python -m akk2eng.pipeline.train --device cuda --fp32 --max-samples 50 --epochs 1 --logging-steps 5
```

## 3. Full training (M01-B default)

```powershell
python -m akk2eng.pipeline.train --device cuda --fp32 --epochs 3
```

(Optional: second terminal) GPU utilization:

```powershell
nvidia-smi
```

## 4. Checkpoint hash (audit)

```powershell
python -m akk2eng.tools.checkpoint_hash outputs/m01_t5
```

## 5. Local submission smoke

```powershell
python -m akk2eng.pipeline.run --model-dir outputs/m01_t5
```

## 6. Next (M01-C)

- Upload `outputs/m01_t5/` (or exported folder) as a Kaggle dataset.
- Run `kaggle/akk2eng_m01_submission.ipynb` with competition data + model input attached.
- Submit; update leaderboard row in `docs/akk2eng.md`.

---

| Timestamp | Action | Result / notes |
|-----------|--------|----------------|
| 2026-03-21 | Full train `--device cuda --fp32 --epochs 3` | 1173 steps, `train_loss` 2.541, model on `cuda:0`; see `M01_run2.md` |
| 2026-03-21 | `checkpoint_hash outputs/m01_t5` | `MANIFEST_SHA256` recorded in `M01_run2.md` |
| 2026-03-21 | `pipeline.run --model-dir outputs/m01_t5` | `outputs/submission.csv` valid schema |
