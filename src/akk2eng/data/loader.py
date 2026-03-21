"""Load competition CSV files into pandas DataFrames."""

from pathlib import Path

import pandas as pd


def load_csv(path: Path | str) -> pd.DataFrame:
    """Load a CSV file. Raises FileNotFoundError if the path does not exist."""
    p = Path(path)
    if not p.is_file():
        msg = f"CSV not found: {p}"
        raise FileNotFoundError(msg)
    return pd.read_csv(p)
