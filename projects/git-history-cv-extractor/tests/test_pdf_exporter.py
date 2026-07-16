"""Tests for ``src.reports.pdf_exporter``."""

from pathlib import Path

from src.reports.pdf_exporter import (
    convert_markdown_to_pdf,
    discover_markdown_files,
    export_reports_to_pdf,
)


def test_discover_markdown_files(tmp_path: Path) -> None:
    """discover_markdown_files returns all .md files recursively, sorted."""
    (tmp_path / "a.md").write_text("# A")
    sub = tmp_path / "ai"
    sub.mkdir()
    (sub / "b.md").write_text("# B")
    (tmp_path / "ignore.txt").write_text("not md")

    result = discover_markdown_files(tmp_path)

    names = [p.name for p in result]
    assert names == ["a.md", "b.md"]


def test_convert_markdown_to_pdf_creates_file(tmp_path: Path) -> None:
    """convert_markdown_to_pdf creates a valid PDF file."""
    md_path = tmp_path / "sample.md"
    md_path.write_text("# Hello World\n\nSome content here.")
    out_path = tmp_path / "out" / "sample.pdf"

    convert_markdown_to_pdf(md_path, out_path)

    assert out_path.exists()
    assert out_path.stat().st_size > 0
    # PDF files start with %PDF
    header = out_path.read_bytes()[:5]
    assert header == b"%PDF-"


def test_export_reports_to_pdf_batch(tmp_path: Path) -> None:
    """export_reports_to_pdf converts all .md to pdf/ and returns paths."""
    (tmp_path / "report.md").write_text("# Report\n\nContent.")
    sub = tmp_path / "ai"
    sub.mkdir()
    (sub / "ai_report.md").write_text("# AI\n\nMore content.")

    created = export_reports_to_pdf(tmp_path)

    pdf_dir = tmp_path / "pdf"
    assert pdf_dir.exists()
    assert len(created) == 2
    names = sorted(p.name for p in created)
    assert names == ["ai_report.pdf", "report.pdf"]
    for p in created:
        assert p.exists()
        assert p.read_bytes()[:5] == b"%PDF-"


def test_export_reports_to_pdf_no_files(tmp_path: Path) -> None:
    """export_reports_to_pdf returns empty list when no .md files exist."""
    created = export_reports_to_pdf(tmp_path)
    assert created == []
