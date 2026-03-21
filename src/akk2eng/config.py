"""Default paths for local development.

Paths are **relative to the current working directory** (run commands from the repo root).
On Kaggle, use the notebook paths (``/kaggle/input``, ``/kaggle/working``) instead.
"""

from pathlib import Path

DEFAULT_TEST_CSV = Path("data") / "test.csv"
DEFAULT_SUBMISSION_CSV = Path("outputs") / "submission.csv"
