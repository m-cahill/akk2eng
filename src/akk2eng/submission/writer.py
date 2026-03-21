"""Write Kaggle submission.csv (id, translation)."""

from pathlib import Path

import pandas as pd

from akk2eng.data.schema import COL_ID, COL_TRANSLATION, SUBMISSION_COLUMNS


def write_submission(
    ids: pd.Series,
    translations: list[str],
    path: Path | str,
) -> None:
    """Write submission CSV with columns id, translation."""
    if len(ids) != len(translations):
        msg = f"id count ({len(ids)}) != translation count ({len(translations)})"
        raise ValueError(msg)
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame({COL_ID: ids, COL_TRANSLATION: translations})
    frame.to_csv(out, index=False)
    # Validate column order and names for Kaggle
    written = pd.read_csv(out)
    if list(written.columns) != list(SUBMISSION_COLUMNS):
        msg = f"Expected columns {SUBMISSION_COLUMNS}, got {list(written.columns)}"
        raise ValueError(msg)
