"""Placeholder inference — replace with a real model in a later milestone."""

import pandas as pd

DUMMY_TRANSLATION = "dummy translation"


def run_inference(df: pd.DataFrame) -> list[str]:
    """Return one placeholder translation per row (deterministic, same length as df)."""
    return [DUMMY_TRANSLATION] * len(df)  # df length only until model uses transliterations
