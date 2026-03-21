"""Default paths and model constants.

Paths are **relative to the current working directory** (run commands from the repo root).
On Kaggle, use the notebook paths (``/kaggle/input``, ``/kaggle/working``) instead.
"""

from pathlib import Path

SEED = 42

# Seq2seq baseline (M01)
BASE_MODEL_ID = "google-t5/t5-small"
T5_TASK_PREFIX = "translate Old Assyrian Akkadian to English: "
MAX_INPUT_LENGTH = 512
MAX_TARGET_LENGTH = 512
MAX_NEW_TOKENS = 256

DEFAULT_TRAIN_CSV = Path("data") / "train.csv"
DEFAULT_TEST_CSV = Path("data") / "test.csv"
DEFAULT_SUBMISSION_CSV = Path("outputs") / "submission.csv"
DEFAULT_MODEL_DIR = Path("outputs") / "m01_t5"
