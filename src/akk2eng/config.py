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

# M02-C / C.2 / C.3: deterministic decoding (no sampling). Repetition control always on.
# M02-C.3: num_beams>1 is an experiment for Kaggle-alignment (see M02_run3_local_beam.md);
# historical baseline contract was greedy (num_beams=1).
DECODE_REPETITION_PENALTY = 1.1
DECODE_NO_REPEAT_NGRAM_SIZE = 3
DECODE_NUM_BEAMS = 3

DEFAULT_TRAIN_CSV = Path("data") / "train.csv"
DEFAULT_TEST_CSV = Path("data") / "test.csv"
DEFAULT_SUBMISSION_CSV = Path("outputs") / "submission.csv"
DEFAULT_MODEL_DIR = Path("outputs") / "m01_t5"

# M02 — fixed train/dev split (persist under data/splits/; data/ is gitignored)
DEFAULT_SPLITS_DIR = Path("data") / "splits"
DEFAULT_TRAIN_SPLIT_CSV = DEFAULT_SPLITS_DIR / "train_split.csv"
DEFAULT_DEV_SPLIT_CSV = DEFAULT_SPLITS_DIR / "dev_split.csv"
DEV_FRACTION = 0.1

# M02 — eval artifacts (outputs/ is gitignored)
DEFAULT_EVAL_OUTPUT_DIR = Path("outputs") / "eval"
DEFAULT_EXPERIMENTS_DIR = Path("outputs") / "experiments"
DEFAULT_PREDICTIONS_DEV_CSV = DEFAULT_EVAL_OUTPUT_DIR / "predictions_dev.csv"
DEFAULT_ANALYSIS_OUTPUT_DIR = Path("outputs") / "analysis"
