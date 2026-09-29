"""
pdf_to_docx.py

Layout-preserving PDF -> DOCX conversion (the "iLovePDF-style" step of the
pipeline). Uses pdf2docx, which parses the PDF's layout tree (text blocks,
fonts, images, table grids) and rebuilds it as native Word XML, rather than
dumping the page as an image.

This is a plain function module meant to be imported by main.py as the
first stage of the pipeline:

    pdf_to_docx.convert_pdf_to_docx  ->  chunks.index_pdf_for_rag
        ->  projectsih.process_and_rewrite_document
"""

import time
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf
from pdf2docx import Converter

from heading_normalizer import normalize_headings


@dataclass
class ConversionResult:
    success: bool
    input_path: str
    output_path: str
    pages_converted: int = 0
    duration_seconds: float = 0.0
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    heading_report: dict | None = None


def convert_pdf_to_docx(
    input_path: str,
    output_path: str,
    start: int = 0,
    end: int | None = None,
    pages: list[int] | None = None,
    normalize: bool = True,
) -> ConversionResult:
    """
    Convert a PDF into a DOCX, preserving layout: paragraphs, headings
    (by font-size heuristics), images, and tables (as real Word tables,
    not flattened text).

    Args:
        input_path: path to the source .pdf
        output_path: path to write the .docx to
        start: first page index to convert (0-based), ignored if `pages` set
        end: last page index (exclusive) to convert, ignored if `pages` set
        pages: explicit list of 0-based page indices to convert, overrides
               start/end when provided
        normalize: if True (default), run heading_normalizer afterwards so
               heading paragraphs get real "Heading N" styles instead of
               pdf2docx's default (bold Normal text, sometimes merged with
               the body paragraph that follows). Needed for any downstream
               step that segments the doc "by topic" via paragraph styles.
    """
    input_path = str(input_path)
    output_path = str(output_path)

    src = Path(input_path)
    if not src.exists():
        return ConversionResult(
            success=False, input_path=input_path, output_path=output_path,
            error=f"Input file not found: {input_path}",
        )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    warnings: list[str] = []
    t0 = time.time()
    cv = None
    try:
        with pymupdf.open(input_path) as _doc:
            total_pages = _doc.page_count

        cv = Converter(input_path)

        if pages is not None:
            cv.convert(output_path, pages=pages)
            n_converted = len(pages)
        else:
            cv.convert(output_path, start=start, end=end)
            n_converted = (end if end is not None else total_pages) - start

        heading_report = None
        if normalize:
            try:
                tmp_path = output_path.replace(".docx", "_tmp_norm.docx")
                heading_report = normalize_headings(output_path, tmp_path, pdf_path=input_path)
                Path(tmp_path).replace(output_path)
            except Exception as e:
                warnings.append(f"Heading normalization skipped due to error: {e}")

        duration = time.time() - t0
        return ConversionResult(
            success=True,
            input_path=input_path,
            output_path=output_path,
            pages_converted=n_converted,
            duration_seconds=round(duration, 2),
            warnings=warnings,
            heading_report=heading_report,
        )
    except Exception as e:
        return ConversionResult(
            success=False,
            input_path=input_path,
            output_path=output_path,
            duration_seconds=round(time.time() - t0, 2),
            error=f"{type(e).__name__}: {e}",
        )
    finally:
        if cv is not None:
            cv.close()
