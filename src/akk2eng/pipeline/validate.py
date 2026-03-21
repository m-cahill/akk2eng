"""Minimal train/val split sanity check: INPUT → PRED → TARGET."""

from __future__ import annotations

import argparse
from pathlib import Path

from akk2eng.config import DEFAULT_MODEL_DIR, DEFAULT_TRAIN_CSV, SEED
from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_TRANSLATION, COL_TRANSLITERATION
from akk2eng.model.model import T5BaselineTranslator


def run_validation(
    train_csv: Path,
    model_dir: Path | None,
    *,
    val_fraction: float = 0.1,
    max_rows: int = 10,
) -> None:
    df = load_csv(train_csv)
    df = df.dropna(subset=[COL_TRANSLITERATION, COL_TRANSLATION])
    df = df.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    n_val = max(1, int(len(df) * val_fraction))
    val = df.iloc[:n_val]

    translator = T5BaselineTranslator(model_dir=model_dir)
    texts = val[COL_TRANSLITERATION].astype(str).tolist()
    preds, _ = translator.translate(texts, batch_size=4)

    print("Validation split (first", min(max_rows, len(val)), "rows)")
    print("Using fine-tuned dir:", translator.loaded_from_finetuned_dir)
    for i in range(min(max_rows, len(val))):
        src = texts[i]
        pred = preds[i]
        tgt = val.iloc[i][COL_TRANSLATION]
        print("---")
        print("INPUT:", src[:500] + ("…" if len(src) > 500 else ""))
        print("PRED: ", pred[:500] + ("…" if len(pred) > 500 else ""))
        print("TGT:  ", str(tgt)[:500] + ("…" if len(str(tgt)) > 500 else ""))


def main() -> None:
    parser = argparse.ArgumentParser(description="M01 validation harness on train.csv")
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=DEFAULT_TRAIN_CSV,
        help=f"Path to train.csv (default: {DEFAULT_TRAIN_CSV})",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help=f"Fine-tuned checkpoint dir (default: {DEFAULT_MODEL_DIR})",
    )
    parser.add_argument("--val-fraction", type=float, default=0.1)
    parser.add_argument("--max-rows", type=int, default=10)
    args = parser.parse_args()
    run_validation(
        args.train_csv,
        args.model_dir,
        val_fraction=args.val_fraction,
        max_rows=args.max_rows,
    )


if __name__ == "__main__":
    main()
