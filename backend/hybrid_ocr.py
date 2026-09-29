import os
import logging
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Set Tesseract path explicitly for Windows if not in PATH
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

class MultiTierHybridOCR:
    def __init__(self, use_gpu: bool = False):
        self._paddle_ocr = None
        self._paddle_initialized = False
        self._paddle_failure_logged = False
        self._tesseract_failure_logged = False
        self._docling_converter = None
        self.use_gpu = use_gpu

    def _init_paddle(self):
        if self._paddle_initialized:
            return
        self._paddle_initialized = True
        try:
            from paddleocr import PaddleOCR
            self._paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        except Exception as e:
            if not self._paddle_failure_logged:
                logger.warning(f"PaddleOCR unavailable as fallback: {e}")
                self._paddle_failure_logged = True

    def ocr_image(self, pil_img: Image.Image, img_bytes: bytes) -> Tuple[str, int, str]:
        try:
            text = pytesseract.image_to_string(pil_img)
            if text.strip():
                return text, 0, "Tesseract"
        except Exception as e:
            if not self._tesseract_failure_logged:
                logger.warning(f"Tesseract failed; trying PaddleOCR fallback: {e}")
                self._tesseract_failure_logged = True

        self._init_paddle()
        if self._paddle_ocr is None:
            return "", 0, "No OCR"

        try:
            paddle_res = self._paddle_ocr.ocr(img_bytes, cls=True)
            lines = []
            low_confidence_blocks = 0
            if paddle_res and paddle_res[0]:
                for line in paddle_res[0]:
                    text, confidence = line[1][0], line[1][1]
                    lines.append(text)
                    if confidence < 0.60:
                        low_confidence_blocks += 1
            return "\n".join(lines), low_confidence_blocks, "PaddleOCR"
        except Exception as e:
            if not self._paddle_failure_logged:
                logger.warning(f"PaddleOCR fallback failed: {e}")
                self._paddle_failure_logged = True
            return "", 0, "PaddleOCR"

    def _init_docling(self):
        if self._docling_converter is None:
            try:
                from docling.document_converter import DocumentConverter
                self._docling_converter = DocumentConverter()
            except Exception as e:
                logger.error(f"Docling init failed: {e}")

    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        doc = fitz.open(pdf_path)
        results = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            
            # ==========================================
            # LAYER 0: Digital PDF Text (PyMuPDF)
            # ==========================================
            digital_text = page.get_text("text").strip()
            if len(digital_text) > 60:  # Page has native selectable text
                results.append({
                    "page": page_idx + 1,
                    "tier": "Layer 0 (PyMuPDF)",
                    "text": digital_text,
                    "confidence": 1.0
                })
                continue

            # Render page image for OCR tiers
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            pil_img = Image.open(io.BytesIO(img_bytes))

            # ==========================================
            # LAYER 1: Tesseract, then PaddleOCR fallback
            # ==========================================
            layer1_text, low_confidence_blocks, ocr_engine = self.ocr_image(
                pil_img, img_bytes
            )

            # ==========================================
            # LAYER 2: Layout & Table Escalate (Docling)
            # ==========================================
            # If Layer 1 output has low confidence or is sparse on a scanned page, escalate to Docling
            if low_confidence_blocks > 3 or len(layer1_text.strip()) < 30:
                logger.info(f"Escalating Page {page_idx + 1} to Layer 2 (Docling Layout Engine)...")
                self._init_docling()
                
                if self._docling_converter:
                    try:
                        # Convert single page context via Docling
                        docling_doc = self._docling_converter.convert(pdf_path)
                        markdown_text = docling_doc.document.export_to_markdown()
                        results.append({
                            "page": page_idx + 1,
                            "tier": "Layer 2 (Docling)",
                            "text": markdown_text,
                            "confidence": 0.95
                        })
                        continue
                    except Exception as e:
                        logger.error(f"Docling processing failed: {e}")

            # Default to Layer 1 result if Layer 2 wasn't needed or failed
            results.append({
                "page": page_idx + 1,
                "tier": f"Layer 1 ({ocr_engine})",
                "text": layer1_text,
                "confidence": 0.80
            })

        return results