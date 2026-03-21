"""M01-A: local GPU + PyTorch + Transformers substrate checks (conservative FP32).

Run: python -m akk2eng.tools.gpu_bringup

Fails hard if CUDA is missing, the PyTorch build is CPU-only, or the GPU architecture
is not supported by the installed binary (e.g. Blackwell sm_120 on an older wheel).
Not invoked from CI. Use ``--allow-cpu`` only for non-GPU verification.
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import torch

from akk2eng.config import BASE_MODEL_ID, T5_TASK_PREFIX


def _print_runtime_versions() -> None:
    import accelerate
    import transformers

    print("=== Runtime package versions ===")
    print("NumPy:", np.__version__)
    print("Torch:", torch.__version__)
    print("Transformers:", transformers.__version__)
    print("Accelerate:", accelerate.__version__)
    print()


def _enforce_numpy_major_lt_2() -> None:
    major = int(np.__version__.split(".")[0])
    if major >= 2:
        print(
            "ERROR: NumPy 2.x breaks PyTorch dynamo / Trainer. "
            "Pin numpy>=1.26,<2 (see pyproject.toml).",
            file=sys.stderr,
        )
        sys.exit(1)


def _is_pytorch_cpu_only_build() -> bool:
    return torch.version.cuda is None


def _check_gpu_arch_support() -> bool:
    """Return True if the GPU's SM arch is in the torch binary's compiled arch list.

    Prints a clear diagnostic and returns False on mismatch (e.g. Blackwell sm_120
    on a wheel that only ships up to sm_90).
    """
    if not torch.cuda.is_available():
        return True  # nothing to check

    cap = torch.cuda.get_device_capability(0)
    gpu_sm = f"sm_{cap[0]}{cap[1]}"
    arch_list = torch.cuda.get_arch_list() if hasattr(torch.cuda, "get_arch_list") else []
    arch_str = ", ".join(arch_list) if arch_list else "(unknown)"

    print("GPU SM arch:", gpu_sm)
    print("Torch compiled arch list:", arch_str)

    if arch_list and gpu_sm not in arch_list:
        gpu_name = torch.cuda.get_device_name(0)
        print()
        print(
            f"ERROR: Detected {gpu_name} ({gpu_sm}), but this PyTorch binary does not",
            file=sys.stderr,
        )
        print(
            f"include {gpu_sm} support (compiled for: {arch_str}).",
            file=sys.stderr,
        )
        print(file=sys.stderr)
        if cap[0] >= 12:
            print(
                "Blackwell GPUs (sm_120) require a PyTorch build with CUDA 12.8+ support.",
                file=sys.stderr,
            )
            print(
                "See README.md 'RTX 5090 / Blackwell local setup' or pytorch.org.",
                file=sys.stderr,
            )
        else:
            print(
                "Install a PyTorch build that includes your GPU architecture.",
                file=sys.stderr,
            )
        return False
    return True


def phase1_cuda_probe() -> None:
    print("=== Phase 1: CUDA / torch probe ===")
    print("Torch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if torch.version.cuda is not None:
        print("CUDA version (PyTorch build):", torch.version.cuda)
    else:
        print("CUDA version (PyTorch build): (none - CPU-only wheel)")
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))
        print("Compute capability:", torch.cuda.get_device_capability(0))
    print()


def phase2_matmul_fp32(device: torch.device) -> None:
    print("=== Phase 2: FP32 matmul ===")
    x = torch.randn(1000, 1000, device=device, dtype=torch.float32)
    y = torch.randn(1000, 1000, device=device, dtype=torch.float32)
    z = x @ y
    print("Tensor z device:", z.device)
    print("Tensor z dtype:", z.dtype)
    print("Mean:", z.mean().item())
    if device.type == "cuda" and z.device.type != "cuda":
        print("ERROR: matmul result not on CUDA", file=sys.stderr)
        sys.exit(1)
    print()


def phase3_transformers_seq2seq(device: torch.device) -> None:
    print("=== Phase 3: Transformers (google-t5/t5-small), FP32 ===")
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID)
    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL_ID, torch_dtype=torch.float32)
    model = model.to(device=device, dtype=torch.float32)
    model.eval()

    p0 = next(model.parameters())
    print("Model device:", p0.device)
    print("Model parameter dtype:", p0.dtype)
    if device.type == "cuda":
        assert p0.device.type == "cuda", "model not on CUDA after .to(cuda)"

    input_text = f"{T5_TASK_PREFIX}i-na E.GAL"
    inputs = tokenizer(input_text, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    first_key = next(iter(inputs))
    print("Input tensor device (" + first_key + "):", inputs[first_key].device)

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            do_sample=False,
            num_beams=1,
        )
    print("Output tensor device:", outputs.device)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    clip = text[:200] + ("..." if len(text) > 200 else "")
    print("Sample decode:", repr(clip))
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="M01-A GPU / torch / transformers bring-up (FP32)",
    )
    parser.add_argument(
        "--allow-cpu",
        action="store_true",
        help="Skip CUDA requirements (not valid for M01-A GPU sign-off)",
    )
    args = parser.parse_args()

    _print_runtime_versions()
    _enforce_numpy_major_lt_2()

    if not args.allow_cpu:
        if _is_pytorch_cpu_only_build():
            print(
                "ERROR: PyTorch is CPU-only (no CUDA). Install a CUDA wheel from pytorch.org.",
                file=sys.stderr,
            )
            sys.exit(1)
        assert torch.cuda.is_available(), "CUDA not available - aborting GPU bring-up"
        print("assert torch.cuda.is_available(): OK")

    phase1_cuda_probe()

    if torch.cuda.is_available():
        if not _check_gpu_arch_support():
            sys.exit(1)

    if not torch.cuda.is_available():
        if not args.allow_cpu:
            print("ERROR: CUDA not available after probe.", file=sys.stderr)
            sys.exit(1)
        device = torch.device("cpu")
        print("WARNING: continuing on CPU (--allow-cpu).", file=sys.stderr)
    else:
        device = torch.device("cuda:0")

    phase2_matmul_fp32(device)
    phase3_transformers_seq2seq(device)

    print("=== Bring-up finished OK ===")
    print("Expected: run `nvidia-smi` during a CUDA training smoke to confirm GPU use.")
    print("Next:")
    print("  python -m akk2eng.pipeline.train --max-samples 50 --epochs 1 --device cuda --fp32")
    print("  python -m akk2eng.tools.checkpoint_hash outputs/m01_t5")


if __name__ == "__main__":
    main()
