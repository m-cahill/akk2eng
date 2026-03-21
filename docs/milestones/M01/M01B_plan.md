# M01-B — Full local training + checkpoint audit

**Parent:** [M01_plan.md](M01_plan.md)  
**Prerequisite:** M01-A closed (`v0.0.2-m01a`); `docs/milestones/M01/M01_run1.md` records GPU substrate PASS.  
**Status:** Complete (see [M01_run2.md](M01_run2.md))  

## Objective

Run **full** fine-tuning of `google-t5/t5-small` on `data/train.csv`, produce a reproducible checkpoint under `outputs/m01_t5/`, hash artifacts, and prepare weights for M01-C (Kaggle inference).

## Requirements

| Requirement | Notes |
|-------------|--------|
| **GPU** | `--device cuda` on a validated workstation (Blackwell: CUDA 12.8+ torch per `README.md`). |
| **FP32** | Use `--fp32` for parity with M01-A substrate validation unless explicitly experimenting. |
| **Epochs** | Default target: **3** (adjust via `--epochs` if plan changes; document in `M01B_toolcalls.md`). |
| **Checkpoint** | Trainer output directory `outputs/m01_t5/` (or `--output-dir` if used). |
| **Hash** | `python -m akk2eng.tools.checkpoint_hash <output_dir>` — recorded in `docs/milestones/M01/M01_run2.md`. |
| **Smoke (optional)** | `--max-samples N` for a quick GPU path check before the long run. |

## Commands (summary)

See **`M01B_toolcalls.md`** for copy-paste sequences.

1. Activate venv; confirm `python -m akk2eng.tools.gpu_bringup` still passes (Blackwell).
2. Full train, e.g.:

   ```bash
   python -m akk2eng.pipeline.train --device cuda --fp32 --epochs 3
   ```

3. During training: optional `nvidia-smi` snapshot for audit.
4. After training:

   ```bash
   python -m akk2eng.tools.checkpoint_hash outputs/m01_t5
   ```

5. Local inference smoke:

   ```bash
   python -m akk2eng.pipeline.run --model-dir outputs/m01_t5
   ```

## Acceptance (M01-B)

- [x] Training completes without device/assert failures.
- [x] `outputs/m01_t5/` contains loadable HuggingFace artifacts (`config.json`, weights, tokenizer files as saved by Trainer).
- [x] Checkpoint hash manifest captured.
- [x] `pipeline.run` produces `outputs/submission.csv` with valid schema.

## Exit

Hand off to **M01-C**: package checkpoint for Kaggle dataset, run `kaggle/akk2eng_m01_submission.ipynb`, submit, record score in `docs/akk2eng.md` leaderboard table.

## Closeout (governance)

**Tag:** `v0.0.3-m01b`. **Run log:** [M01_run2.md](M01_run2.md). M01-B is **closed and frozen**; follow [M01C_checklist.md](M01C_checklist.md) for submission.
