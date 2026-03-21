"""Deterministic train/dev split from train.csv (M02).

Split is **fixed** for all experiments: shuffle with ``SEED``, hold out the first
``dev_fraction`` of rows as **dev** (same convention as ``pipeline.validate``).
CSV files are written once under ``data/splits/`` and reused unless ``force`` is set.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from akk2eng.config import SEED
from akk2eng.data.loader import load_csv
from akk2eng.data.schema import COL_TRANSLATION, COL_TRANSLITERATION


def train_dev_split(
    df: pd.DataFrame,
    *,
    seed: int = SEED,
    dev_fraction: float = 0.1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return ``(train_df, dev_df)`` after shuffling and a fixed fraction dev holdout.

    Dev rows are the **first** ``n_dev`` rows after shuffle (matches historical
    ``pipeline.validate`` behavior). ``n_dev = max(1, int(dev_fraction * n))``.
    """
    if not 0.0 < dev_fraction < 1.0:
        msg = f"dev_fraction must be in (0, 1), got {dev_fraction!r}"
        raise ValueError(msg)
    work = df.dropna(subset=[COL_TRANSLITERATION, COL_TRANSLATION]).copy()
    work = work.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    n = len(work)
    if n == 0:
        msg = "No rows left after dropping missing transliteration/translation"
        raise ValueError(msg)
    n_dev = max(1, int(dev_fraction * n))
    dev = work.iloc[:n_dev].copy()
    train = work.iloc[n_dev:].copy()
    if len(train) == 0:
        msg = "Dev fraction leaves zero training rows; lower dev_fraction or add data"
        raise ValueError(msg)
    return train, dev


def ensure_split_csvs(
    train_csv: Path,
    train_split_csv: Path,
    dev_split_csv: Path,
    *,
    seed: int = SEED,
    dev_fraction: float = 0.1,
    force: bool = False,
) -> tuple[Path, Path]:
    """Create ``train_split_csv`` / ``dev_split_csv`` if missing (or if ``force``).

    Returns ``(train_split_csv, dev_split_csv)`` paths.
    """
    train_csv = Path(train_csv)
    train_split_csv = Path(train_split_csv)
    dev_split_csv = Path(dev_split_csv)

    if not force and train_split_csv.is_file() and dev_split_csv.is_file():
        return train_split_csv, dev_split_csv

    df = load_csv(train_csv)
    train_df, dev_df = train_dev_split(df, seed=seed, dev_fraction=dev_fraction)
    train_split_csv.parent.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(train_split_csv, index=False)
    dev_df.to_csv(dev_split_csv, index=False)
    return train_split_csv, dev_split_csv
