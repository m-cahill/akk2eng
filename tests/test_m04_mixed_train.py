"""M04 mixed training CSV and multi-file train loading."""

from __future__ import annotations

from pathlib import Path

from akk2eng.data.mixed_train import build_mixed_train_csv
from akk2eng.pipeline.train import _load_concat_train_dataframes


def test_build_mixed_train_csv_order_and_stats(tmp_path: Path) -> None:
    doc = tmp_path / "doc.csv"
    ali = tmp_path / "ali.csv"
    out = tmp_path / "mixed.csv"
    stats_path = tmp_path / "stats.json"
    doc.write_text(
        "oare_id,transliteration,translation\n"
        "d1,aa bb,One.\n"
        "d2,cc dd,Two.\n",
        encoding="utf-8",
    )
    ali.write_text(
        "sentence_id,oare_id,transliteration,translation,line_start,line_end,"
        "alignment_method,alignment_confidence\n"
        "z-last,d1,zz,Last.,1,1,exact,1\n"
        "a-first,d1,xx,First.,1,1,exact,1\n",
        encoding="utf-8",
    )
    stats = build_mixed_train_csv(doc, ali, out, stats_json=stats_path)
    assert stats["document_rows"] == 2
    assert stats["aligned_rows"] == 2
    assert stats["total_rows"] == 4
    text = out.read_text(encoding="utf-8")
    lines = text.strip().splitlines()
    assert lines[0].startswith("oare_id")
    # Document block first (preserves train order)
    assert "d1,aa bb" in lines[1]
    assert "d2,cc dd" in lines[2]
    # Aligned block sorted by sentence_id: a-first before z-last (text columns only)
    assert text.index("xx,First.") < text.index("zz,Last.")


def test_load_concat_train_dataframes(tmp_path: Path) -> None:
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text(
        "oare_id,transliteration,translation\nx,1,One.\n",
        encoding="utf-8",
    )
    b.write_text(
        "oare_id,transliteration,translation\ny,2,Two.\n",
        encoding="utf-8",
    )
    df, meta = _load_concat_train_dataframes([a, b])
    assert len(df) == 2
    assert meta["n_sources"] == 2
    assert meta["total_rows_after_dropna"] == 2
    assert df.iloc[0]["transliteration"] == "1"
    assert df.iloc[1]["transliteration"] == "2"
