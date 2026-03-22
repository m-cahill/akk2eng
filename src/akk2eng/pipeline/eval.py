"""M02-A: dev evaluation harness — fixed split, chrF (primary) + BLEU (secondary)."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any

import sacrebleu

from akk2eng.config import (
    DECODE_NO_REPEAT_NGRAM_SIZE,
    DECODE_NUM_BEAMS,
    DECODE_REPETITION_PENALTY,
    DEFAULT_DEV_SPLIT_CSV,
    DEFAULT_EVAL_OUTPUT_DIR,
    DEFAULT_EXPERIMENTS_DIR,
    DEFAULT_LEXICON_CSV,
    DEFAULT_MODEL_DIR,
    DEFAULT_SPLITS_DIR,
    DEFAULT_TRAIN_CSV,
    DEFAULT_TRAIN_SPLIT_CSV,
    DEV_FRACTION,
    LEXICON_MAX_ENTRIES,
    MAX_NEW_TOKENS,
    SEED,
    USE_LEXICON,
)
from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_TRANSLATION, COL_TRANSLITERATION
from akk2eng.data.splits import ensure_split_csvs
from akk2eng.pipeline.inference import resolved_lexicon_pairs, run_inference


def compute_translation_metrics(
    hypotheses: list[str],
    references: list[str],
) -> dict[str, Any]:
    """Return chrF (primary) and BLEU (secondary) corpus scores (sacrebleu scale)."""
    if len(hypotheses) != len(references):
        msg = f"Length mismatch: {len(hypotheses)} hypotheses vs {len(references)} references"
        raise ValueError(msg)
    wrapped_refs: list[list[str]] = [[r] for r in references]
    bleu = sacrebleu.corpus_bleu(hypotheses, wrapped_refs)
    chrf = sacrebleu.corpus_chrf(hypotheses, wrapped_refs)
    return {
        "chrf": float(chrf.score),
        "bleu": float(bleu.score),
        "sacrebleu_version": getattr(sacrebleu, "__version__", "unknown"),
    }


def run_eval(
    *,
    train_csv: Path,
    train_split_csv: Path,
    dev_split_csv: Path,
    model_dir: Path | None,
    eval_output_dir: Path,
    experiments_dir: Path,
    batch_size: int,
    force_splits: bool,
    quiet: bool,
    use_lexicon: bool | None = None,
    lexicon_csv: Path | None = None,
    lexicon_train_csv: Path | None = None,
    lexicon_max_entries: int | None = None,
) -> dict[str, Any]:
    """Ensure splits, run inference on dev, write eval + experiment artifacts."""
    ensure_split_csvs(
        train_csv,
        train_split_csv,
        dev_split_csv,
        seed=SEED,
        dev_fraction=DEV_FRACTION,
        force=force_splits,
    )

    dev_df = load_csv(dev_split_csv)
    if COL_TRANSLITERATION not in dev_df.columns or COL_TRANSLATION not in dev_df.columns:
        msg = f"Dev split must contain {COL_TRANSLITERATION!r} and {COL_TRANSLATION!r}"
        raise ValueError(msg)

    do_lex = USE_LEXICON if use_lexicon is None else use_lexicon
    lcsv = DEFAULT_LEXICON_CSV if lexicon_csv is None else lexicon_csv
    ltrain = train_csv if lexicon_train_csv is None else lexicon_train_csv
    lcap = LEXICON_MAX_ENTRIES if lexicon_max_entries is None else lexicon_max_entries

    preds = run_inference(
        dev_df,
        model_dir=model_dir,
        batch_size=batch_size,
        quiet=quiet,
        use_lexicon=do_lex,
        train_csv=ltrain,
        lexicon_csv=lcsv,
        lexicon_max_entries=lcap,
    )
    refs = dev_df[COL_TRANSLATION].fillna("").astype(str).tolist()
    metrics = compute_translation_metrics(preds, refs)

    eval_output_dir = Path(eval_output_dir)
    eval_output_dir.mkdir(parents=True, exist_ok=True)

    out_pred = dev_df.copy()
    out_pred["prediction"] = preds
    pred_path = eval_output_dir / "predictions_dev.csv"
    out_pred.to_csv(pred_path, index=False)

    metrics_path = eval_output_dir / "metrics.json"
    decoding = {
        "do_sample": False,
        "num_beams": DECODE_NUM_BEAMS,
        "max_new_tokens": MAX_NEW_TOKENS,
        "repetition_penalty": DECODE_REPETITION_PENALTY,
        "no_repeat_ngram_size": DECODE_NO_REPEAT_NGRAM_SIZE,
    }
    n_lex = 0
    if do_lex:
        n_lex = len(
            resolved_lexicon_pairs(
                train_csv=ltrain,
                lexicon_csv=lcsv,
                lexicon_max_entries=lcap,
            ),
        )
    lexicon_cfg = {
        "use_lexicon": do_lex,
        "lexicon_csv": str(Path(lcsv).resolve()) if do_lex else None,
        "train_csv_for_lexicon": str(Path(ltrain).resolve()) if do_lex else None,
        "max_entries": int(lcap) if do_lex else None,
        "n_entries": n_lex,
    }
    metrics_blob = {
        **metrics,
        "primary_metric": "chrf",
        "secondary_metric": "bleu",
        "n_dev": len(preds),
        "seed": SEED,
        "dev_fraction": DEV_FRACTION,
        "train_csv": str(Path(train_csv).resolve()),
        "dev_split_csv": str(Path(dev_split_csv).resolve()),
        "train_split_csv": str(Path(train_split_csv).resolve()),
        "model_dir": str(Path(model_dir).resolve()) if model_dir else None,
        "decoding": decoding,
        "lexicon": lexicon_cfg,
    }
    metrics_path.write_text(json.dumps(metrics_blob, indent=2) + "\n", encoding="utf-8")

    summary_lines = [
        "akk2eng M02 dev evaluation",
        f"dev rows: {len(preds)}",
        f"primary (chrF): {metrics['chrf']:.4f}",
        f"secondary (BLEU): {metrics['bleu']:.4f}",
        f"sacrebleu: {metrics['sacrebleu_version']}",
        f"seed: {SEED}, dev_fraction: {DEV_FRACTION}",
        (
            f"decoding: num_beams={DECODE_NUM_BEAMS}, do_sample=False, "
            f"repetition_penalty={DECODE_REPETITION_PENALTY}, "
            f"no_repeat_ngram_size={DECODE_NO_REPEAT_NGRAM_SIZE}, "
            f"max_new_tokens={MAX_NEW_TOKENS}"
        ),
        (
            f"lexicon: use_lexicon={do_lex}, n_entries={n_lex}, "
            f"max_entries={lcap if do_lex else 'n/a'}"
        ),
        f"predictions: {pred_path}",
        f"metrics: {metrics_path}",
    ]
    summary_path = eval_output_dir / "eval_summary.txt"
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    if not quiet:
        print("\n".join(summary_lines))

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    exp_dir = Path(experiments_dir) / f"exp_{ts}"
    exp_dir.mkdir(parents=True, exist_ok=True)
    try:
        pkg_ver = metadata.version("akk2eng")
    except metadata.PackageNotFoundError:
        pkg_ver = "unknown"
    config_blob = {
        "akk2eng_version": pkg_ver,
        "seed": SEED,
        "dev_fraction": DEV_FRACTION,
        "train_csv": str(Path(train_csv).resolve()),
        "train_split_csv": str(Path(train_split_csv).resolve()),
        "dev_split_csv": str(Path(dev_split_csv).resolve()),
        "model_dir": str(Path(model_dir).resolve()) if model_dir else None,
        "batch_size": batch_size,
        "eval_output_dir": str(eval_output_dir.resolve()),
        "sacrebleu_version": metrics["sacrebleu_version"],
        "decoding": decoding,
        "lexicon": lexicon_cfg,
        "USE_LEXICON": USE_LEXICON,
        "DEFAULT_LEXICON_CSV": str(Path(DEFAULT_LEXICON_CSV).resolve()),
        "LEXICON_MAX_ENTRIES": LEXICON_MAX_ENTRIES,
    }
    (exp_dir / "config.json").write_text(
        json.dumps(config_blob, indent=2) + "\n",
        encoding="utf-8",
    )
    shutil.copy2(metrics_path, exp_dir / "metrics.json")
    shutil.copy2(pred_path, exp_dir / "predictions_dev.csv")
    notes_path = exp_dir / "notes.txt"
    if not notes_path.is_file():
        notes_path.write_text(
            "M02 experiment snapshot (auto). Add hypothesis and outcome here.\n",
            encoding="utf-8",
        )

    return metrics_blob


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "M02 dev eval: fixed 90/10 split (seed=42), chrF + BLEU, artifacted predictions"
        ),
    )
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=DEFAULT_TRAIN_CSV,
        help=f"Source train.csv (default: {DEFAULT_TRAIN_CSV})",
    )
    parser.add_argument(
        "--train-split-csv",
        type=Path,
        default=DEFAULT_TRAIN_SPLIT_CSV,
        help=f"Persisted train split (default: {DEFAULT_TRAIN_SPLIT_CSV})",
    )
    parser.add_argument(
        "--dev-split-csv",
        type=Path,
        default=DEFAULT_DEV_SPLIT_CSV,
        help=f"Persisted dev split (default: {DEFAULT_DEV_SPLIT_CSV})",
    )
    parser.add_argument(
        "--splits-dir",
        type=Path,
        default=DEFAULT_SPLITS_DIR,
        help=f"Convenience default parent for split paths (default: {DEFAULT_SPLITS_DIR})",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help=f"Fine-tuned checkpoint dir (default: {DEFAULT_MODEL_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_EVAL_OUTPUT_DIR,
        help=(
            "Write predictions_dev.csv, metrics.json, eval_summary.txt "
            f"(default: {DEFAULT_EVAL_OUTPUT_DIR})"
        ),
    )
    parser.add_argument(
        "--experiments-dir",
        type=Path,
        default=DEFAULT_EXPERIMENTS_DIR,
        help=f"Experiment snapshots exp_<UTC>/ (default: {DEFAULT_EXPERIMENTS_DIR})",
    )
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--force-splits",
        action="store_true",
        help="Regenerate train_split.csv and dev_split.csv from --train-csv",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress stdout summary (artifacts still written)",
    )
    parser.add_argument(
        "--no-lexicon",
        action="store_true",
        help="Disable M02-D lexicon post-processing on predictions",
    )
    parser.add_argument(
        "--lexicon-csv",
        type=Path,
        default=None,
        help=f"eBL lexicon CSV (default: {DEFAULT_LEXICON_CSV})",
    )
    parser.add_argument(
        "--lexicon-train-csv",
        type=Path,
        default=None,
        help="train.csv used to filter lexicon forms (default: same as --train-csv)",
    )
    parser.add_argument(
        "--lexicon-max-entries",
        type=int,
        default=None,
        help=f"Cap lexicon size after filtering (default: {LEXICON_MAX_ENTRIES})",
    )
    args = parser.parse_args()

    train_split = args.train_split_csv
    dev_split = args.dev_split_csv
    # If split paths were left at defaults, honor --splits-dir for both filenames.
    if train_split == DEFAULT_TRAIN_SPLIT_CSV and dev_split == DEFAULT_DEV_SPLIT_CSV:
        train_split = args.splits_dir / "train_split.csv"
        dev_split = args.splits_dir / "dev_split.csv"

    run_eval(
        train_csv=args.train_csv,
        train_split_csv=train_split,
        dev_split_csv=dev_split,
        model_dir=args.model_dir,
        eval_output_dir=args.output_dir,
        experiments_dir=args.experiments_dir,
        batch_size=args.batch_size,
        force_splits=args.force_splits,
        quiet=args.quiet,
        use_lexicon=False if args.no_lexicon else None,
        lexicon_csv=args.lexicon_csv,
        lexicon_train_csv=args.lexicon_train_csv,
        lexicon_max_entries=args.lexicon_max_entries,
    )


if __name__ == "__main__":
    main()
