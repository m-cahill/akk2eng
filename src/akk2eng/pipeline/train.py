"""Fine-tune T5-small on train.csv (local M01 training)."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    TrainerCallback,
)

from akk2eng.config import (
    BASE_MODEL_ID,
    DEFAULT_MODEL_DIR,
    DEFAULT_TRAIN_CSV,
    MAX_INPUT_LENGTH,
    MAX_TARGET_LENGTH,
    SEED,
    T5_TASK_PREFIX,
)
from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_TRANSLATION, COL_TRANSLITERATION
from akk2eng.model.model import set_deterministic_seeds
from akk2eng.model.tokenizer import load_tokenizer


def _preprocess_batch(examples: dict, tokenizer, prefix: str) -> dict:
    src = [f"{prefix}{t}" for t in examples[COL_TRANSLITERATION]]
    model_inputs = tokenizer(src, max_length=MAX_INPUT_LENGTH, truncation=True)
    labels = tokenizer(
        text_target=examples[COL_TRANSLATION],
        max_length=MAX_TARGET_LENGTH,
        truncation=True,
    )
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def _make_preprocess_fn(tokenizer, prefix: str):
    def _fn(examples: dict) -> dict:
        return _preprocess_batch(examples, tokenizer, prefix)

    return _fn


class _GpuTrainingStepLogger(TrainerCallback):
    """M01-A: explicit step / loss / device lines when training on CUDA."""

    def __init__(self, expect_cuda: bool) -> None:
        self.expect_cuda = expect_cuda

    def on_log(self, args, state, control, logs=None, **kwargs):
        if not self.expect_cuda or logs is None or "loss" not in logs:
            return
        print(f"STEP {state.global_step}")
        print(f"LOSS: {logs['loss']}")
        print("DEVICE: cuda")


def _resolve_device(device: str) -> tuple[str, bool]:
    """Return (label, use_cpu) for TrainingArguments."""
    if device == "auto":
        use_cpu = not torch.cuda.is_available()
        label = "cpu" if use_cpu else "cuda"
        return label, use_cpu
    if device == "cpu":
        return "cpu", True
    if device == "cuda":
        if not torch.cuda.is_available():
            msg = "--device cuda requested but torch.cuda.is_available() is False"
            raise RuntimeError(msg)
        return "cuda", False
    msg = f"Unknown device mode: {device!r}"
    raise ValueError(msg)


def train(
    train_csv: Path,
    output_dir: Path,
    *,
    epochs: float = 3.0,
    batch_size: int = 4,
    learning_rate: float = 3e-4,
    max_samples: int | None = None,
    device: str = "auto",
    fp32: bool = False,
    logging_steps: int = 50,
) -> None:
    set_deterministic_seeds()
    label, use_cpu = _resolve_device(device)
    print("Training device mode:", device, "-> resolved:", label, "| Trainer use_cpu:", use_cpu)

    df = load_csv(train_csv)
    for col in (COL_TRANSLITERATION, COL_TRANSLATION):
        if col not in df.columns:
            msg = f"train CSV must contain column {col!r}"
            raise ValueError(msg)
    df = df.dropna(subset=[COL_TRANSLITERATION, COL_TRANSLATION])
    df = df.astype({COL_TRANSLITERATION: str, COL_TRANSLATION: str})
    if max_samples is not None:
        if max_samples < 1:
            msg = "--max-samples must be >= 1"
            raise ValueError(msg)
        df = df.iloc[:max_samples].reset_index(drop=True)
        print("Using subset: first", len(df), "rows after dropna (CSV order).")

    from datasets import Dataset

    ds = Dataset.from_pandas(df[[COL_TRANSLITERATION, COL_TRANSLATION]].reset_index(drop=True))
    tokenizer = load_tokenizer(BASE_MODEL_ID)

    dtype_kw = {}
    if fp32:
        dtype_kw["torch_dtype"] = torch.float32

    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL_ID, **dtype_kw)
    if fp32:
        model = model.to(dtype=torch.float32)
    if not use_cpu:
        model = model.to(device=torch.device("cuda"), dtype=model.dtype)
        assert next(model.parameters()).device.type == "cuda", "Training is not using GPU"

    print("Model device:", next(model.parameters()).device)
    print("Model parameter dtype (before Trainer):", next(model.parameters()).dtype)

    tokenized = ds.map(
        _make_preprocess_fn(tokenizer, T5_TASK_PREFIX),
        batched=True,
        remove_columns=ds.column_names,
    )

    collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    args = Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        save_strategy="epoch",
        logging_steps=logging_steps,
        seed=SEED,
        report_to=[],
        predict_with_generate=False,
        use_cpu=use_cpu,
        fp16=False,
        bf16=False,
    )

    expect_cuda = not use_cpu
    trainer = Seq2SeqTrainer(
        model=model,
        args=args,
        train_dataset=tokenized,
        tokenizer=tokenizer,
        data_collator=collator,
        callbacks=[_GpuTrainingStepLogger(expect_cuda)],
    )
    if expect_cuda:
        assert next(trainer.model.parameters()).device.type == "cuda", (
            "Trainer model not on CUDA before train() - possible CPU fallback"
        )
        print("Expected: run `nvidia-smi` during training to confirm GPU utilization.")
    trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    print("Model parameter device (after train):", next(trainer.model.parameters()).device)
    print("Model parameter dtype (after train):", next(trainer.model.parameters()).dtype)
    if not use_cpu and torch.cuda.is_available():
        print(
            "CUDA device count:",
            torch.cuda.device_count(),
            "| current:",
            torch.cuda.current_device(),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune T5-small on train.csv (M01)")
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=DEFAULT_TRAIN_CSV,
        help=f"Path to train.csv (default: {DEFAULT_TRAIN_CSV})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help=f"Directory to save model + tokenizer (default: {DEFAULT_MODEL_DIR})",
    )
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        metavar="N",
        help="Use only the first N rows after dropna (CSV order); for smoke tests",
    )
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
        help="Training device: auto (CUDA if available), cpu, or cuda (fail if no CUDA)",
    )
    parser.add_argument(
        "--fp32",
        action="store_true",
        help="Load and keep model weights in float32 (conservative; recommended for new GPUs)",
    )
    parser.add_argument(
        "--logging-steps",
        type=int,
        default=50,
        help="Trainer logging interval (lower for short smoke runs)",
    )
    args = parser.parse_args()
    train(
        args.train_csv,
        args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        max_samples=args.max_samples,
        device=args.device,
        fp32=args.fp32,
        logging_steps=args.logging_steps,
    )


if __name__ == "__main__":
    main()
