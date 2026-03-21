"""SHA-256 manifest for a saved HuggingFace-style checkpoint directory.

Sorted filenames; auditable combined digest.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def hash_checkpoint_dir(directory: Path) -> list[tuple[str, str]]:
    """Sorted (filename, sha256_hex) for each regular file (top-level only, skip dotfiles)."""
    if not directory.is_dir():
        msg = f"Not a directory: {directory}"
        raise NotADirectoryError(msg)

    pairs: list[tuple[str, str]] = []
    for path in sorted(directory.iterdir(), key=lambda p: p.name):
        if not path.is_file() or path.name.startswith("."):
            continue
        pairs.append((path.name, sha256_file(path)))
    return pairs


def format_manifest(pairs: list[tuple[str, str]]) -> str:
    lines = [f"{name}\t{digest}" for name, digest in pairs]
    return "\n".join(lines) + ("\n" if lines else "")


def manifest_sha256(pairs: list[tuple[str, str]]) -> str:
    """Single digest over the sorted manifest text (for quick compare between runs)."""
    body = format_manifest(pairs).encode()
    return hashlib.sha256(body).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print SHA-256 for each file in a checkpoint directory (sorted by filename).",
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing config, weights, tokenizer files (e.g. outputs/m01_t5)",
    )
    parser.add_argument(
        "--combined-only",
        action="store_true",
        help="Print only the sha256 of the full manifest line (for comparing two training runs).",
    )
    args = parser.parse_args()
    pairs = hash_checkpoint_dir(args.directory)
    if args.combined_only:
        print("MANIFEST_SHA256:", manifest_sha256(pairs))
        return
    print("Per-file (name<TAB>sha256):")
    print(format_manifest(pairs), end="")
    print("MANIFEST_SHA256:", manifest_sha256(pairs))


if __name__ == "__main__":
    main()
