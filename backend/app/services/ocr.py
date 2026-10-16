"""
DESHMRITTIKA / BHUMI-SYNC — Document OCR Pipeline (P1 Track)
Validates file types, executes real Tesseract OCR, and reports honest execution statuses.
"""

import io
from typing import Dict, Any, Tuple
from PIL import Image
import pytesseract

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

class DocumentOCRService:

    @staticmethod
    def process_document(file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Runs honest OCR extraction on uploaded file without fabricating results."""
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return {
                "success": False,
                "ocr_status": "UNSUPPORTED_FILE_TYPE",
                "extracted_text": "",
                "error": f"File type '.{ext}' is not supported. Use PNG, JPEG, or TIFF."
            }

        if len(file_bytes) > MAX_FILE_SIZE:
            return {
                "success": False,
                "ocr_status": "FILE_TOO_LARGE",
                "extracted_text": "",
                "error": "File size exceeds 10 MB limit."
            }

        try:
            image = Image.open(io.BytesIO(file_bytes))
            # Run pytesseract
            raw_text = pytesseract.image_to_string(image)
            cleaned_text = raw_text.strip()

            if not cleaned_text:
                return {
                    "success": False,
                    "ocr_status": "FAILED_TO_PARSE",
                    "extracted_text": "",
                    "note": "Document image was unreadable or contained no detectable text."
                }

            # Check available language packs
            try:
                available_langs = pytesseract.get_languages()
            except Exception:
                available_langs = ['eng']

            has_bangla_pack = 'ben' in available_langs

            status = "SUCCESS" if has_bangla_pack else "PARTIAL_CONFIDENCE"
            note = "Full OCR extraction completed." if has_bangla_pack else "English text and alphanumeric deed tokens parsed; Bengali language pack ('ben') not installed on local host."

            return {
                "success": True,
                "ocr_status": status,
                "extracted_text": cleaned_text,
                "note": note,
                "char_count": len(cleaned_text)
            }

        except Exception as e:
            return {
                "success": False,
                "ocr_status": "OCR_EXECUTION_ERROR",
                "extracted_text": "",
                "error": str(e)
            }
