"""Batch-convert Markdown report files to PDF.

Uses the ``markdown-pdf`` library (no system-level dependencies) to
convert ``.md`` files from the reports directory into a dedicated
``reports/pdf/`` output folder.
"""

from pathlib import Path

from markdown_pdf import MarkdownPdf, Section


def discover_markdown_files(reports_dir: Path) -> list[Path]:
    """Return all ``.md`` files under *reports_dir* (recursively), sorted."""
    return sorted(reports_dir.rglob("*.md"))


def convert_markdown_to_pdf(md_path: Path, output_path: Path) -> None:
    """Convert a single Markdown file to PDF using ``markdown-pdf``."""
    md_content = md_path.read_text(encoding="utf-8")
    pdf = MarkdownPdf(toc_level=0)
    pdf.add_section(Section(md_content))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(str(output_path))


def export_reports_to_pdf(reports_dir: Path) -> list[Path]:
    """Discover all ``.md`` files and convert each to PDF.

    PDFs are written to ``<reports_dir>/pdf/<filename>.pdf``.

    Returns
    -------
    list[Path]
        Paths to successfully written PDF files.
    """
    md_files = discover_markdown_files(reports_dir)
    pdf_dir = reports_dir / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for md_path in md_files:
        # Skip any files that are already inside the pdf/ directory
        try:
            md_path.relative_to(pdf_dir)
            continue
        except ValueError:
            pass

        pdf_name = md_path.stem + ".pdf"
        out_path = pdf_dir / pdf_name
        convert_markdown_to_pdf(md_path, out_path)
        created.append(out_path)

    return created
