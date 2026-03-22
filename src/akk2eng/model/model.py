"""T5 baseline: load checkpoint and run deterministic decoding (greedy or beam per config)."""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import torch
from transformers import PreTrainedModel, PreTrainedTokenizerBase

from akk2eng.config import (
    BASE_MODEL_ID,
    DECODE_NO_REPEAT_NGRAM_SIZE,
    DECODE_NUM_BEAMS,
    DECODE_REPETITION_PENALTY,
    MAX_INPUT_LENGTH,
    MAX_NEW_TOKENS,
    SEED,
    T5_TASK_PREFIX,
)
from akk2eng.model.tokenizer import load_tokenizer


def set_deterministic_seeds() -> None:
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    random.seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)


def _cuda_arch_supported() -> bool:
    """True if the GPU's SM arch is in the torch binary's compiled list."""
    if not torch.cuda.is_available():
        return False
    cap = torch.cuda.get_device_capability(0)
    gpu_sm = f"sm_{cap[0]}{cap[1]}"
    arch_list = torch.cuda.get_arch_list() if hasattr(torch.cuda, "get_arch_list") else []
    return not arch_list or gpu_sm in arch_list


def safe_cuda_device() -> torch.device:
    """Return cuda:0 only when the GPU arch is actually runnable, else CPU.

    This is NOT a silent fallback — it is an intentional arch-aware device
    selection for inference.  The training path (``--device cuda``) still
    asserts hard.  ``gpu_bringup`` diagnoses the mismatch explicitly.
    """
    if torch.cuda.is_available() and _cuda_arch_supported():
        return torch.device("cuda:0")
    return torch.device("cpu")


def resolve_model_path(model_dir: Path | None) -> tuple[str, bool]:
    """Return (path_or_id, loaded_from_finetuned_dir)."""
    if model_dir is not None and (Path(model_dir) / "config.json").is_file():
        return str(model_dir), True
    return BASE_MODEL_ID, False


class T5BaselineTranslator:
    """Seq2seq translation for one T5-style checkpoint (``DECODE_NUM_BEAMS`` in config)."""

    def __init__(self, model_dir: Path | None = None) -> None:
        set_deterministic_seeds()
        path, self._from_finetuned = resolve_model_path(model_dir)
        self._tokenizer: PreTrainedTokenizerBase = load_tokenizer(path)
        from transformers import AutoModelForSeq2SeqLM

        self._model: PreTrainedModel = AutoModelForSeq2SeqLM.from_pretrained(path)
        self._model.eval()
        self._device = safe_cuda_device()
        self._model.to(self._device)

    @property
    def loaded_from_finetuned_dir(self) -> bool:
        return self._from_finetuned

    def _prefix_inputs(self, transliterations: list[str]) -> list[str]:
        p = T5_TASK_PREFIX
        return [f"{p}{t}" for t in transliterations]

    @torch.inference_mode()
    def translate(
        self,
        transliterations: list[str],
        *,
        batch_size: int = 8,
    ) -> tuple[list[str], list[int]]:
        """Return (translations, output_token_lengths per row)."""
        out_texts: list[str] = []
        out_lens: list[int] = []
        prefixed = self._prefix_inputs(transliterations)
        for i in range(0, len(prefixed), batch_size):
            chunk = prefixed[i : i + batch_size]
            enc = self._tokenizer(
                chunk,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=MAX_INPUT_LENGTH,
            )
            enc = {k: v.to(self._device) for k, v in enc.items()}
            gen = self._model.generate(
                **enc,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                num_beams=DECODE_NUM_BEAMS,
                repetition_penalty=DECODE_REPETITION_PENALTY,
                no_repeat_ngram_size=DECODE_NO_REPEAT_NGRAM_SIZE,
            )
            for row in gen:
                out_lens.append(int((row != self._tokenizer.pad_token_id).sum().item()))
            out_texts.extend(self._tokenizer.batch_decode(gen, skip_special_tokens=True))
        return out_texts, out_lens
