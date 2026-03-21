# M01 Run 1 — GPU / CUDA substrate (M01-A)

**Purpose:** Auditable record of **M01-A** execution on the RTX 5090 (Blackwell).

---

## Environment

| Field | Value |
|--------|--------|
| Date | 2026-03-21 |
| OS | Windows 11 (native) |
| GPU | NVIDIA GeForce RTX 5090 |
| Compute capability | `sm_120` (Blackwell) |
| Driver | (see `nvidia-smi` during M01-B) |
| Python | 3.11 |
| Torch | `2.10.0+cu128` |
| CUDA (PyTorch build) | `12.8` |
| `torch.cuda.get_arch_list()` | `['sm_70', 'sm_75', 'sm_80', 'sm_86', 'sm_90', 'sm_100', 'sm_120']` |
| NumPy | `1.26.4` |
| Transformers | `4.47.1` |
| Accelerate | `1.13.0` |
| Torch track used | **Blackwell local override** (`pip install torch --index-url .../cu128`; see `README.md`) |

---

## Execution

### 1. `python -m akk2eng.tools.gpu_bringup`

```
=== Runtime package versions ===
NumPy: 1.26.4
Torch: 2.10.0+cu128
Transformers: 4.47.1
Accelerate: 1.13.0

assert torch.cuda.is_available(): OK
=== Phase 1: CUDA / torch probe ===
Torch version: 2.10.0+cu128
CUDA available: True
CUDA version (PyTorch build): 12.8
GPU: NVIDIA GeForce RTX 5090
Compute capability: (12, 0)

GPU SM arch: sm_120
Torch compiled arch list: sm_70, sm_75, sm_80, sm_86, sm_90, sm_100, sm_120
=== Phase 2: FP32 matmul ===
Tensor z device: cuda:0
Tensor z dtype: torch.float32
Mean: 0.10504370927810669

=== Phase 3: Transformers (google-t5/t5-small), FP32 ===
Model device: cuda:0
Model parameter dtype: torch.float32
Input tensor device (input_ids): cuda:0
Output tensor device: cuda:0
Sample decode: 'i-na E.GAL'

=== Bring-up finished OK ===
```

**Checks:**

- [x] `assert torch.cuda.is_available(): OK`
- [x] GPU SM arch (`sm_120`) in `torch.cuda.get_arch_list()`
- [x] `Model device: cuda:0`
- [x] `Input tensor device: cuda:0`
- [x] `Output tensor device: cuda:0`

### 2. CUDA training smoke

*Pending: run in M01-B.*

### 3. `nvidia-smi` (optional snapshot)

*Pending: capture during M01-B training.*

### 4. Checkpoint hash

*Pending: after M01-B training completes.*

---

## Validation checklist

| Criterion | Pass? |
|-----------|--------|
| GPU detected (`cuda:0`) | PASS |
| GPU arch (`sm_120`) in compiled arch list | PASS |
| Bring-up model on CUDA | PASS |
| FP32 matmul on CUDA | PASS |
| No silent CPU fallback | PASS |
| No kernel errors | PASS |
| Training model on CUDA (assertions passed) | Pending (M01-B) |
| Checkpoint written | Pending (M01-B) |
| Hash manifest produced | Pending (M01-B) |

---

## Arch mismatch history

Initial attempt with `torch 2.5.1+cu124` failed: PyTorch binary supported up to `sm_90`; Blackwell requires `sm_120`. `gpu_bringup` detected this and printed an actionable error. Resolved by installing `torch 2.10.0+cu128` which includes `sm_120`.

---

## Determinism notes

- **GPU training** may differ slightly run-to-run; compare manifests with `checkpoint_hash` if auditing.
- **Inference** with **fixed saved weights** and greedy decode is the primary determinism contract.

---

## Verdict

```
M01-A (GPU substrate) — PASSED
```

**Sign-off:** M01-A bring-up validated 2026-03-21.

---

## Closeout

M01-A is officially closed.

The system has achieved:

- Verified CUDA execution on Blackwell (`sm_120`)
- Compatible PyTorch build (CUDA 12.8)
- Deterministic inference contract preserved
- Fail-fast GPU validation enforced
- Stable dependency configuration

This milestone establishes a verified GPU execution substrate for all subsequent training work.

**Next step:** M01-B — full local training and first real submission (see `docs/milestones/M01/M01B_plan.md`).
