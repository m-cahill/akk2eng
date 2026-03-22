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

# M02-D: optional post-processing of English predictions (leaked Akkadian surfaces).
USE_LEXICON = True
DEFAULT_LEXICON_CSV = Path("docs") / "kaggledocs" / "OA_Lexicon_eBL.csv"
LEXICON_MAX_ENTRIES = 400

# M03: inference-time transliteration cleanup (see ``akk2eng.data.normalize``).
USE_NORMALIZATION = True
NORMALIZATION_VERSION = "v2"

# M04: sentence alignment outputs (under ``data/``; gitignored like other competition paths).
DEFAULT_SENTENCES_AID_CSV = Path("data") / "Sentences_Oare_FirstWord_LinNum.csv"
DEFAULT_ALIGNMENT_OUTPUT_DIR = Path("data") / "derived" / "alignment"
DEFAULT_ALIGNED_TRAIN_CSV = DEFAULT_ALIGNMENT_OUTPUT_DIR / "aligned_train_sentences.csv"
DEFAULT_ALIGNMENT_REPORT_JSON = DEFAULT_ALIGNMENT_OUTPUT_DIR / "alignment_report.json"
# M04 leak-safe: align only persisted train split (never full train.csv for training/eval parity).
DEFAULT_ALIGNED_TRAIN_SPLIT_CSV = DEFAULT_ALIGNMENT_OUTPUT_DIR / "aligned_train_sentences_split.csv"
DEFAULT_ALIGNMENT_REPORT_SPLIT_JSON = DEFAULT_ALIGNMENT_OUTPUT_DIR / "alignment_report_split.json"
DEFAULT_MIXED_TRAIN_CSV = DEFAULT_ALIGNMENT_OUTPUT_DIR / "mixed_train.csv"
DEFAULT_MIXED_TRAIN_STATS_JSON = DEFAULT_ALIGNMENT_OUTPUT_DIR / "mixed_train_stats.json"

# M05: split-safe augmented / expanded alignment (under data/; gitignored)
DEFAULT_AUGMENTATION_OUTPUT_DIR = Path("data") / "derived" / "augmentation"
DEFAULT_AUGMENTED_TRAIN_CSV = DEFAULT_AUGMENTATION_OUTPUT_DIR / "augmented_train_sentences.csv"
DEFAULT_AUGMENTATION_REPORT_JSON = DEFAULT_AUGMENTATION_OUTPUT_DIR / "augmentation_report.json"

# M06: gated selection outputs (under data/; gitignored)
DEFAULT_SELECTION_OUTPUT_DIR = Path("data") / "derived" / "selection"
_SEL = DEFAULT_SELECTION_OUTPUT_DIR
DEFAULT_POLICY_A_TRAIN_CSV = _SEL / "strict_plus_highconf_cap50.csv"
DEFAULT_POLICY_B_TRAIN_CSV = _SEL / "strict_plus_highconf_cap50_weighted2x.csv"
DEFAULT_POLICY_A_REPORT_JSON = _SEL / "strict_plus_highconf_cap50_report.json"
DEFAULT_POLICY_B_REPORT_JSON = _SEL / "strict_plus_highconf_cap50_weighted2x_report.json"

# M07: confidence_v2 selection outputs (under data/; gitignored)
DEFAULT_CONFIDENCE_OUTPUT_DIR = Path("data") / "derived" / "confidence"
