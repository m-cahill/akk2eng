"""Checkpoint hashing utility (no GPU, no HuggingFace download)."""

from pathlib import Path

from akk2eng.tools.checkpoint_hash import format_manifest, hash_checkpoint_dir, manifest_sha256


def test_hash_checkpoint_dir_sorted_and_stable(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("bb", encoding="utf-8")

    pairs = hash_checkpoint_dir(tmp_path)
    assert [n for n, _ in pairs] == ["a.txt", "b.txt"]

    m1 = manifest_sha256(pairs)
    m2 = manifest_sha256(hash_checkpoint_dir(tmp_path))
    assert m1 == m2


def test_format_manifest_tabs(tmp_path: Path) -> None:
    (tmp_path / "f").write_bytes(b"x")
    pairs = hash_checkpoint_dir(tmp_path)
    text = format_manifest(pairs)
    assert "\t" in text
    assert text.endswith("\n")
