"""Standard logging helper (M00 — no structured JSON yet)."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a module logger (stdlib only)."""
    return logging.getLogger(name)
