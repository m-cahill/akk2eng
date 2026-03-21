"""Tokenizer loading for the baseline seq2seq model."""

from pathlib import Path

from transformers import PreTrainedTokenizerBase


def load_tokenizer(model_name_or_path: str | Path) -> PreTrainedTokenizerBase:
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(str(model_name_or_path))
