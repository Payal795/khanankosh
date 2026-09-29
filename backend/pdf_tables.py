import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    # New PyMuPDF name
    import pymupdf as fitz
except ImportError:
    # Older installs expose `fitz`
    import fitz  # type: ignore


PREV_AT_BOTTOM = 0.60
CURR_AT_TOP = 0.45
MAX_HEADER_ROWS = 3
CAPTION_MAX_GAP = 60


# --------------------------------------------------------------------------
# Cell / number helpers
# --------------------------------------------------------------------------

def clean_cell(cell: Any) -> str:
    if cell is None:
        return ""
    return re.sub(r"\s+", " ", str(cell)).strip()


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_cell(text).lower())


# Markers that mean "no value" in reports.
# They become NULL, never 0.
NULL_MARKERS = {
    "",
    "-",
    "–",
    "—",
    "--",
    "..",
    "…",
    "na",
    "n.a",
    "n.a.",
    "n/a",
    "nm",
}


_CURRENCY_PREFIX = re.compile(
    r"^(?:rs\.?|inr|usd|us\$|₹|\$|€|£)\s*",
    re.I,
)

_FOOTNOTE_MARKS = re.compile(r"[\*†‡#]+$")
_FOOTNOTE_LETTER = re.compile(r"\s*\([a-z]\)$", re.I)

# 1234
# 1,234.5
# 1,23,456.78
# .5
_NUMBER_RE = re.compile(
    r"^[+-]?(?:(?:\d{1,3}(?:,\d{2,3})+|\d+)(?:\.\d+)?|\.\d+)$"
)


def parse_number(value: Any) -> Optional[float]:
    """
    Convert a cell into a number when possible.

    Examples:
        '1,23,456.7' -> 123456.7
        '(12.5)'     -> -12.5
        '12%'        -> 12.0
        'Rs. 5*'     -> 5.0
        'Nil'        -> 0.0
        '-', 'NA'    -> None
        'abc'        -> None
    """

    s = clean_cell(value)

    if not s:
        return None

    low = s.lower()

    if low in NULL_MARKERS:
        return None

    if low == "nil":
        return 0.0

    s = s.replace("\u2212", "-")

    s = _CURRENCY_PREFIX.sub("", s)
    s = _FOOTNOTE_MARKS.sub("", s).strip()
    s = _FOOTNOTE_LETTER.sub("", s).strip()

    negative = False

    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1].strip()

    if s.endswith("%"):
        s = s[:-1].strip()

    if not _NUMBER_RE.match(s):
        return None

    v = float(s.replace(",", ""))

    return -v if negative else v


# --------------------------------------------------------------------------
# Header heuristics
# --------------------------------------------------------------------------

_HEADER_KEYWORDS = {
    "year",
    "date",
    "description",
    "name",
    "total",
    "quantity",
    "production",
    "capacity",
    "unit",
    "value",
    "parameter",
    "remarks",
    "location",
    "depth",
    "seam",
    "area",
    "coal",
    "sl",
    "no",
    "item",
    "particulars",
}


def headers_similar(
    h1: Sequence[str],
    h2: Sequence[str]
) -> bool:

    if not h1 or not h2 or abs(len(h1) - len(h2)) > 1:
        return False

    n1 = [
        normalize_text(x)
        for x in h1
        if normalize_text(x)
    ]

    n2 = [
        normalize_text(x)
        for x in h2
        if normalize_text(x)
    ]

    if not n1 or not n2:
        return False

    if n1 == n2:
        return True

    s1 = set(n1)

    return (
        sum(1 for x in n2 if x in s1)
        / max(len(n1), len(n2))
        >= 0.6
    )


def looks_like_header(row: Sequence[str]) -> bool:

    cells = [
        clean_cell(x)
        for x in row
        if clean_cell(x)
    ]

    if not cells:
        return False

    # Mostly numeric -> probably data
    numeric = sum(
        1
        for c in cells
        if parse_number(c) is not None
    )

    if numeric / len(cells) > 0.3:
        return False

    if any(
        normalize_text(c) in _HEADER_KEYWORDS
        for c in cells
    ):
        return True

    text_cells = sum(
        1
        for c in cells
        if re.search(r"[A-Za-z]", c)
    )

    return (text_cells / len(cells)) >= 0.6


def _split_header(
    rows: List[List[str]]
) -> Tuple[List[List[str]], List[List[str]]]:

    """
    Row 0 is the header.

    Following rows are also treated as header rows when the
    previous row contains empty/spanned cells and the next row
    fills those cells with text.
    """

    if not rows:
        return [], []

    n = 1

    while n < min(MAX_HEADER_ROWS, len(rows) - 1):

        prev = rows[n - 1]
        cand = rows[n]

        filled_by_cand = [
            i
            for i, c in enumerate(prev)
            if not c
            and i < len(cand)
            and cand[i]
        ]

        cells = [
            c
            for c in cand
            if c
        ]

        pure_text = all(
            parse_number(c) is None
            and c.lower() not in NULL_MARKERS
            for c in cells
        )

        if (
            filled_by_cand
            and len(cells) >= 2
            and pure_text
        ):
            n += 1
        else:
            break

    return rows[:n], rows[n:]


def _combine_headers(
    header_rows: List[List[str]],
    width: int
) -> List[str]:

    padded = [
        r + [""] * (width - len(r))
        for r in header_rows
    ]

    filled: List[List[str]] = []

    for k, r in enumerate(padded):

        if k < len(padded) - 1:

            # Group rows:
            # spanned cells are empty -> carry left
            last = ""
            out = []

            for c in r:
                last = c or last
                out.append(last)

            filled.append(out)

        else:
            filled.append(r)

    names = []

    for i in range(width):

        parts: List[str] = []

        for r in filled:

            if r[i] and (
                not parts
                or parts[-1] != r[i]
            ):
                parts.append(r[i])

        names.append(" ".join(parts).strip())

    return names


# --------------------------------------------------------------------------
# Data classes
# --------------------------------------------------------------------------

@dataclass
class LogicalTable:
    """
    One table as the reader sees it,
    even if the PDF split it over pages.
    """

    index: int
    page_start: int
    page_end: int
    caption: str
    header_rows: List[List[str]]
    headers: List[str]
    rows: List[List[str]]
    row_pages: List[int]

    @property
    def n_rows(self) -> int:
        return len(self.rows)

    @property
    def is_multipage(self) -> bool:
        return self.page_end > self.page_start

    def append_fragment(
        self,
        rows: List[List[str]],
        page_num: int
    ) -> None:

        self.rows.extend(rows)

        self.row_pages.extend(
            [page_num] * len(rows)
        )

        self.page_end = page_num

    def finalize(self) -> None:
        """
        Make every row exactly as wide as the header.

        If a later page has an extra non-empty column,
        widen the header instead of silently dropping data.
        """

        width = len(self.headers)

        for r in self.rows:

            last = len(r)

            while last > 0 and not r[last - 1]:
                last -= 1

            width = max(width, last)

        self.headers = [
            (
                self.headers[i]
                if i < len(self.headers)
                and self.headers[i]
                else f"col_{i + 1}"
            )
            for i in range(width)
        ]

        self.rows = [
            (
                r + [""] * (width - len(r))
            )[:width]
            for r in self.rows
        ]


@dataclass
class ParsedDocument:
    page_count: int
    pages_text: Dict[int, str]
    tables: List[LogicalTable] = field(
        default_factory=list
    )


@dataclass
class _Prev:
    table: LogicalTable
    page: int
    bottom_y: float
    page_h: float


# --------------------------------------------------------------------------
# PDF page helpers
# --------------------------------------------------------------------------

def _overlap_ratio(
    a: Sequence[float],
    b: Sequence[float]
) -> float:

    if len(a) < 4 or len(b) < 4:
        return 0.0

    ix0 = max(a[0], b[0])
    iy0 = max(a[1], b[1])
    ix1 = min(a[2], b[2])
    iy1 = min(a[3], b[3])

    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0

    area = (
        (a[2] - a[0])
        * (a[3] - a[1])
    )

    return (
        ((ix1 - ix0) * (iy1 - iy0)) / area
        if area > 0
        else 0.0
    )


def _page_tables(
    page,
    strategy: Optional[str]
) -> List[
    Tuple[
        Tuple[float, ...],
        List[List[str]]
    ]
]:

    try:

        found = (
            page.find_tables(strategy=strategy)
            if strategy
            else page.find_tables()
        )

    except Exception:
        return []

    out = []

    for t in getattr(found, "tables", []) or []:

        try:
            raw = t.extract()
        except Exception:
            continue

        rows = [
            [clean_cell(c) for c in r]
            for r in (raw or [])
        ]

        rows = [
            r
            for r in rows
            if any(r)
        ]

        # A 1-column / 1-row "table" is usually
        # a boxed paragraph rather than a real table.
        if (
            len(rows) < 2
            or max(len(r) for r in rows) < 2
        ):
            continue

        try:
            bbox = tuple(t.bbox)
        except Exception:
            continue

        if len(bbox) < 4:
            continue

        out.append(
            (bbox, rows)
        )

    return out


# --------------------------------------------------------------------------
# SAFE PyMuPDF BLOCK HANDLING
# --------------------------------------------------------------------------

def _valid_text_block(b: Any) -> bool:
    """
    PyMuPDF text blocks normally contain:

        x0, y0, x1, y1, text, block_no, block_type

    Therefore we require at least 7 fields before accessing
    b[4] or b[6].

    This is the main protection against:

        IndexError: tuple index out of range
    """

    return (
        isinstance(b, (tuple, list))
        and len(b) >= 7
    )


def _block_key(b) -> Tuple[str, int]:
    """
    Safely create a key for a PyMuPDF text block.

    Repeated page numbers are normalized so:
        Page 3
        Page 4

    produce the same textual key.
    """

    if not _valid_text_block(b):
        return "", 0

    try:
        text = re.sub(
            r"\d+",
            "#",
            " ".join(
                str(b[4]).split()
            ).lower()
        )
    except (TypeError, ValueError, IndexError):
        text = ""

    try:
        y = float(b[1])
    except (TypeError, ValueError, IndexError):
        y = 0.0

    return text, round(y / 5)


def _running_blocks(doc) -> set:
    """
    Find text repeated in the top/bottom margin of many pages.

    These are usually:
      - running headers
      - footers
      - page numbers

    Malformed/short PyMuPDF tuples are skipped safely.
    """

    n = doc.page_count

    if n < 4:
        return set()

    counts: Counter = Counter()

    for page in doc:

        h = page.rect.height
        seen = set()

        try:
            blocks = page.get_text("blocks")
        except Exception:
            blocks = []

        for b in blocks:

            # FIX:
            # Never access b[6] before checking tuple length.
            if not _valid_text_block(b):
                continue

            try:
                block_type = b[6]
                y0 = float(b[1])
                y1 = float(b[3])
            except (
                TypeError,
                ValueError,
                IndexError
            ):
                continue

            if block_type == 0 and (
                y1 < h * 0.12
                or y0 > h * 0.88
            ):
                seen.add(
                    _block_key(b)
                )

        counts.update(seen)

    need = max(
        3,
        math.ceil(0.4 * n)
    )

    return {
        key
        for key, count in counts.items()
        if count >= need
    }


def _find_caption(
    page,
    bbox: Sequence[float],
    all_bboxes: List[Sequence[float]],
    running: set
) -> str:

    """
    Find the closest text block directly above the table.

    Example:
        Table 3.1: Coal reserves ...
    """

    if len(bbox) < 4:
        return ""

    x0, y0, x1, _ = bbox

    best: Optional[
        Tuple[float, str]
    ] = None

    try:
        blocks = page.get_text("blocks")
    except Exception:
        blocks = []

    for b in blocks:

        # FIX:
        # Prevent b[6] / b[4] tuple errors.
        if not _valid_text_block(b):
            continue

        try:

            if b[6] != 0:
                continue

            bx0 = float(b[0])
            by0 = float(b[1])
            bx1 = float(b[2])
            by1 = float(b[3])
            text = str(b[4])

        except (
            TypeError,
            ValueError,
            IndexError
        ):
            continue

        if _block_key(b) in running:
            continue

        if (
            by1 > y0 + 2
            or by1 < y0 - CAPTION_MAX_GAP
        ):
            continue

        if bx1 < x0 or bx0 > x1:
            continue

        try:
            overlaps = any(
                _overlap_ratio(
                    (bx0, by0, bx1, by1),
                    tb
                ) > 0.5
                for tb in all_bboxes
            )
        except (
            TypeError,
            ValueError,
            IndexError
        ):
            overlaps = False

        if overlaps:
            continue

        text = clean_cell(text)

        if not text or len(text) > 300:
            continue

        if (
            best is None
            or by1 > best[0]
        ):
            best = (
                by1,
                text
            )

    return (
        best[1]
        if best
        else ""
    )


# --------------------------------------------------------------------------
# OCR
# --------------------------------------------------------------------------

from hybrid_ocr import MultiTierHybridOCR


# Initialize OCR router once globally
ocr_router = MultiTierHybridOCR()


def _narrative_text(
    page,
    table_bboxes: List[Sequence[float]],
    running: set
) -> str:

    parts = []

    try:
        blocks = page.get_text(
            "blocks",
            sort=True
        )
    except Exception:
        blocks = []

    for b in blocks:

        # FIX:
        # Never access b[6] before checking length.
        if not _valid_text_block(b):
            continue

        try:

            if b[6] != 0:
                continue

            block_bbox = b[:4]

        except (
            TypeError,
            IndexError
        ):
            continue

        try:

            if any(
                _overlap_ratio(
                    block_bbox,
                    tb
                ) > 0.5
                for tb in table_bboxes
            ):
                continue

        except (
            TypeError,
            ValueError,
            IndexError
        ):
            continue

        if _block_key(b) in running:
            continue

        try:
            text = " ".join(
                str(b[4]).split()
            )
        except (
            TypeError,
            IndexError
        ):
            continue

        if text:
            parts.append(text)

    extracted = "\n\n".join(parts)

    # --------------------------------------------------------------
    # Multi-Tier OCR fallback
    # --------------------------------------------------------------

    if len(extracted.strip()) < 20:

        try:

            pix = page.get_pixmap(
                dpi=200
            )

            img_bytes = pix.tobytes(
                "png"
            )

            from PIL import Image
            import io

            pil_img = Image.open(
                io.BytesIO(img_bytes)
            )

            ocr_text, _, _ = (
                ocr_router.ocr_image(
                    pil_img,
                    img_bytes
                )
            )

            return ocr_text or ""

        except Exception:
            # If OCR fails, return whatever digital
            # text was extracted instead of crashing
            # the entire report pipeline.
            return extracted

    return extracted


# --------------------------------------------------------------------------
# Multi-page table continuation
# --------------------------------------------------------------------------

def _continuation_decision(
    prev: Optional[_Prev],
    page_num: int,
    page_h: float,
    top_y: float,
    first_row: List[str]
) -> Tuple[bool, bool]:

    """
    Returns:

        (is_continuation, drop_repeated_header)
    """

    if (
        prev is None
        or prev.page != page_num - 1
    ):
        return False, False

    if (
        prev.bottom_y
        <= prev.page_h * PREV_AT_BOTTOM
    ):
        return False, False

    if top_y >= page_h * CURR_AT_TOP:
        return False, False

    if abs(
        len(first_row)
        - len(prev.table.headers)
    ) > 1:
        return False, False

    # Make sure header_rows exists
    if not prev.table.header_rows:
        return False, False

    if headers_similar(
        prev.table.header_rows[0],
        first_row
    ):
        return True, True

    if not looks_like_header(first_row):
        return True, False

    return False, False


# --------------------------------------------------------------------------
# Public entry point
# --------------------------------------------------------------------------

def extract_document(
    pdf_path: str,
    table_strategy: Optional[str] = None
) -> ParsedDocument:

    """
    Open the PDF once and return:

        - joined tables
        - narrative text per page

    table_strategy:
        pass "text" for borderless tables.
        PyMuPDF default is usually "lines".
    """

    doc = fitz.open(pdf_path)

    tables: List[
        LogicalTable
    ] = []

    pages_text: Dict[
        int,
        str
    ] = {}

    prev: Optional[
        _Prev
    ] = None

    try:

        running = _running_blocks(doc)

        for page in doc:

            page_num = page.number + 1
            page_h = page.rect.height

            found = _page_tables(
                page,
                table_strategy
            )

            bboxes = [
                bb
                for bb, _ in found
            ]

            pages_text[
                page_num
            ] = _narrative_text(
                page,
                bboxes,
                running
            )

            last_on_page: Optional[
                _Prev
            ] = None

            for idx, (
                bbox,
                rows
            ) in enumerate(found):

                # Extra protection against an empty table.
                if not rows:
                    continue

                top_y = bbox[1]
                bottom_y = bbox[3]

                is_cont = False
                drop_hdr = False

                if idx == 0 and rows:

                    is_cont, drop_hdr = (
                        _continuation_decision(
                            prev,
                            page_num,
                            page_h,
                            top_y,
                            rows[0]
                        )
                    )

                # --------------------------------------------------
                # Continuation of previous page table
                # --------------------------------------------------

                if (
                    is_cont
                    and prev is not None
                ):

                    root = prev.table

                    if drop_hdr:

                        header_count = len(
                            root.header_rows
                        )

                        data = rows[
                            header_count:
                        ]

                    else:
                        data = rows

                    root.append_fragment(
                        data,
                        page_num
                    )

                    last_on_page = _Prev(
                        root,
                        page_num,
                        bottom_y,
                        page_h
                    )

                # --------------------------------------------------
                # New table
                # --------------------------------------------------

                else:

                    header_rows, data = (
                        _split_header(rows)
                    )

                    if not rows:
                        continue

                    width = max(
                        len(r)
                        for r in rows
                    )

                    tbl = LogicalTable(

                        index=len(tables),

                        page_start=page_num,

                        page_end=page_num,

                        caption=_find_caption(
                            page,
                            bbox,
                            bboxes,
                            running
                        ),

                        header_rows=header_rows,

                        headers=_combine_headers(
                            header_rows,
                            width
                        ),

                        rows=list(data),

                        row_pages=[
                            page_num
                        ] * len(data),
                    )

                    tables.append(tbl)

                    last_on_page = _Prev(
                        tbl,
                        page_num,
                        bottom_y,
                        page_h
                    )

            # A page with no table breaks the
            # multi-page continuation chain.
            prev = last_on_page

    finally:

        page_count = doc.page_count

        doc.close()

    # Normalize all tables after extraction.
    for t in tables:
        t.finalize()

    return ParsedDocument(
        page_count=page_count,
        pages_text=pages_text,
        tables=tables
    )