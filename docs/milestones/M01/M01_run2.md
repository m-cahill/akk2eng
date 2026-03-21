# M01 Run 2 — Full training + checkpoint + local inference (M01-B)

**Purpose:** Auditable record of **M01-B** (baseline fine-tune, hash, submission smoke).

**Prerequisite:** [M01_run1.md](M01_run1.md) (M01-A substrate PASS, tag `v0.0.2-m01a`).

---

## Environment

Same substrate as M01-A unless noted:

| Field | Value |
|--------|--------|
| Date | 2026-03-21 |
| GPU / arch | Same workstation as [M01_run1.md](M01_run1.md) (RTX 5090 / `sm_120`); training asserted `cuda:0` |
| Python | 3.11 |
| Torch | `2.10.0+cu128` |
| CUDA (PyTorch build) | `12.8` |
| NumPy | `1.26.4` (venv) |
| Transformers | `4.47.1` |
| Train CSV | `data/train.csv` (1561 rows after tokenization map; Trainer steps 1173 total) |
| Command | `python -m akk2eng.pipeline.train --device cuda --fp32 --epochs 3` |

---

## Training

### Command

```text
python -m akk2eng.pipeline.train --device cuda --fp32 --epochs 3
```

### Device confirmation

```text
Training device mode: cuda -> resolved: cuda | Trainer use_cpu: False
Model device: cuda:0
Model parameter dtype (before Trainer): torch.float32
Expected: run `nvidia-smi` during training to confirm GPU utilization.
...
Model parameter device (after train): cuda:0
Model parameter dtype (after train): torch.float32
CUDA device count: 1 | current: 0
```

### Loss progression (logged steps, `logging_steps=50`)

| Step | Loss | Epoch (approx) |
|------|------|----------------|
| 50 | 4.0134 | 0.13 |
| 100 | 3.3501 | 0.26 |
| 150 | 3.0612 | 0.38 |
| 200 | 2.946 | 0.51 |
| 250 | 2.7426 | 0.64 |
| 300 | 2.7204 | 0.77 |
| 350 | 2.7261 | 0.90 |
| 400 | 2.5662 | 1.02 |
| 450 | 2.4597 | 1.15 |
| 500 | 2.3606 | 1.28 |
| 550 | 2.4572 | 1.41 |
| 600 | 2.4326 | 1.53 |
| 650 | 2.345 | 1.66 |
| 700 | 2.2735 | 1.79 |
| 750 | 2.3412 | 1.92 |
| 800 | 2.3234 | 2.05 |
| 850 | 2.2891 | 2.17 |
| 900 | 2.1642 | 2.30 |
| 950 | 2.2754 | 2.43 |
| 1000 | 2.2118 | 2.56 |
| 1050 | 2.1392 | 2.69 |
| 1100 | 2.1381 | 2.81 |
| 1150 | 2.2767 | 2.94 |

### Trainer summary

```text
{'train_runtime': 50.6044, 'train_samples_per_second': 92.541, 'train_steps_per_second': 23.18, 'train_loss': 2.540788401728091, 'epoch': 3.0}
```

Each logged step included `DEVICE: cuda` from `_GpuTrainingStepLogger`.

---

## GPU evidence

`nvidia-smi` snapshot was **not** captured in this run log; recommended for future audits during training.

---

## Checkpoint

**Output directory:** `outputs/m01_t5/`

**Artifacts present:** `config.json`, `model.safetensors`, tokenizer files, `training_args.bin`, `generation_config.json`.

### `python -m akk2eng.tools.checkpoint_hash outputs/m01_t5`

```text
Per-file (name<TAB>sha256):
config.json	2f49c463c8c6d7ef0d58a920ad26d62a857632042d3aa6351dc269d66198d732
generation_config.json	89858a726a3dd80215416137d3fccdd435903df2a14e65877e788e3421f33d30
model.safetensors	98938d57905d1ac7d3ee582af841b625dc62499c2f00f585317d03454242606e
special_tokens_map.json	65d84a9271d68f1230ab99518c00f0f7eaef95c7b363001595ba6fa662d434b1
spiece.model	d60acb128cf7b7f2536e8f38a5b18a05535c9e14c7a355904270e15b0945ea86
tokenizer.json	681ea40876d5ffe83d0f158f123980f10439d9062b0febedf8bcc3e94a16ec0a
tokenizer_config.json	7b68321438a1a1636b72645d0a7d769457df9cacd23bd62a1d4c304ce78cb7c9
training_args.bin	20e6f016fadc16bbbb0da1598711832368d77d9c51ac4b84ecbe74162407ab09
MANIFEST_SHA256: 71f66f5e76d488deac68e638386c139398ae72eab1d27806f8552cf7101f366d
```

---

## Inference validation

**Command:**

```text
python -m akk2eng.pipeline.run --model-dir outputs/m01_t5
```

**Output:** `outputs/submission.csv`

**Schema:** columns `id`, `translation` (header present).

**Local test row count:** 4 rows (matches local `data/test.csv` in this workspace; full competition test set will be larger on Kaggle).

**Sample:** `pipeline.run` printed fine-tuned `Inference: fine-tuned checkpoint = True` and sample transliteration `->` translation lines (console encoding may mangle cuneiform transliteration characters on Windows cp1252).

---

## Acceptance checklist

- [x] Training completes without device/assert failures
- [x] Model on `cuda:0` before and after `trainer.train()`
- [x] Checkpoint directory loadable (inference used same path)
- [x] Hash manifest generated (`MANIFEST_SHA256` recorded above)
- [x] `pipeline.run` produces valid `submission.csv` schema

---

## Verdict

```text
M01-B (full train + checkpoint + local inference) — PASSED
```

**Next:** **M01-C** — package `outputs/m01_t5/` for Kaggle, run `kaggle/akk2eng_m01_submission.ipynb`, submit, record leaderboard score in `docs/akk2eng.md`.

---

## Closeout

M01-B is officially closed (`v0.0.3-m01b`).

The system has achieved:

- Full GPU training on Blackwell (`sm_120`)
- Stable checkpoint generation
- Deterministic inference pipeline (greedy decode, fixed seeds)
- Verified submission artifact generation (`id`, `translation`)
- Reproducible checkpoint hashing (`MANIFEST_SHA256` recorded above)

This milestone establishes a complete baseline translation system ready for Kaggle submission.

**Next step:** M01-C — Kaggle submission and first non-zero leaderboard score (checklist: `docs/milestones/M01/M01C_checklist.md`).

**Governance:** No further M01-B scope without a new audit; all product work proceeds under M01-C until M01 exit criteria are met.
