"""
DESHMRITTIKA / BHUMI-SYNC — Upgraded Document OCR Pipeline (P1 Track)
Supports Multi-page PDFs (via PyMuPDF), image preprocessing (contrast, binarize, rotate),
Bengali & English dual language detection (ben+eng), confidence scoring, and structured field extraction.
"""

import io
import time
import re
from typing import Dict, Any, List, Optional
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import pymupdf

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp', 'webp', 'pdf'}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

class DocumentOCRService:

    @staticmethod
    def preprocess_image(image: Image.Image, mode: str = "enhance_contrast", rotate_deg: int = 0) -> Image.Image:
        """Applies image preprocessing to improve OCR accuracy on legacy documents."""
        # 1. Orientation correction
        if rotate_deg in [90, 180, 270]:
            image = image.rotate(-rotate_deg, expand=True)

        # 2. Mode processing
        if mode == "grayscale":
            image = image.convert("L")
        elif mode == "enhance_contrast":
            image = image.convert("L")
            image = ImageOps.autocontrast(image, cutoff=2)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.8)
        elif mode == "binarize":
            image = image.convert("L")
            image = ImageOps.autocontrast(image)
            # Simple adaptive thresholding
            threshold = 140
            image = image.point(lambda p: 255 if p > threshold else 0)

        return image

    @classmethod
    def process_document(
        cls,
        file_bytes: bytes,
        filename: str,
        preprocess_mode: str = "enhance_contrast",
        rotate_deg: int = 0,
        lang_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Runs end-to-end OCR with honest telemetry, confidence scoring, and multi-page PDF support."""
        start_time = time.time()
        ext = filename.split('.')[-1].lower() if '.' in filename else ''

        if ext not in ALLOWED_EXTENSIONS:
            return {
                "success": False,
                "ocr_status": "UNSUPPORTED_FILE_TYPE",
                "extracted_text": "",
                "error": f"ফাইল টাইপ '.{ext}' সমর্থিত নয়। অনুমোদিত: PDF, PNG, JPEG, TIFF।"
            }

        if len(file_bytes) > MAX_FILE_SIZE:
            return {
                "success": False,
                "ocr_status": "FILE_TOO_LARGE",
                "extracted_text": "",
                "error": "ফাইলের আকার ১৫ মেগাবাইট অতিক্রম করেছে।"
            }

        try:
            # 1. Detect available Tesseract languages
            try:
                available_langs = pytesseract.get_languages()
            except Exception:
                available_langs = ['eng']

            has_ben = 'ben' in available_langs
            active_lang = lang_override if lang_override and lang_override in available_langs else ('ben+eng' if has_ben else 'eng')

            # 2. Extract images from file (handle PDF vs image)
            images_to_process: List[Image.Image] = []
            if ext == 'pdf':
                doc = pymupdf.open(stream=file_bytes, filetype="pdf")
                total_pages = min(len(doc), 5)  # Process up to first 5 pages in demo
                for p_no in range(total_pages):
                    page = doc[p_no]
                    pix = page.get_pixmap(dpi=250)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    images_to_process.append(img)
                doc.close()
            else:
                raw_img = Image.open(io.BytesIO(file_bytes))
                images_to_process.append(raw_img)

            if not images_to_process:
                return {
                    "success": False,
                    "ocr_status": "EMPTY_DOCUMENT",
                    "extracted_text": "",
                    "error": "নথির কোনো পাতা বা চিত্র পড়া যায়নি।"
                }

            # 3. Process each page with preprocessing and OCR
            full_text_pages: List[str] = []
            all_confidences: List[float] = []

            for idx, img in enumerate(images_to_process):
                processed_img = cls.preprocess_image(img, mode=preprocess_mode, rotate_deg=rotate_deg)

                # Get text
                page_text = pytesseract.image_to_string(processed_img, lang=active_lang)
                cleaned = page_text.strip()
                if cleaned:
                    full_text_pages.append(cleaned)

                # Calculate confidence metrics
                try:
                    data = pytesseract.image_to_data(processed_img, lang=active_lang, output_type=pytesseract.Output.DICT)
                    confs = [float(c) for c in data.get('conf', []) if c not in ('-1', -1, None) and float(c) > 0]
                    if confs:
                        all_confidences.extend(confs)
                except Exception:
                    pass

            combined_text = "\n\n--- [পাতা বিভাজক] ---\n\n".join(full_text_pages) if len(full_text_pages) > 1 else (full_text_pages[0] if full_text_pages else "")

            # 4. Compute average confidence
            avg_confidence = round(sum(all_confidences) / len(all_confidences), 1) if all_confidences else 0.0

            # 5. Extract structured entities (Deed No, Dag, Khatian, Mouza, Area)
            entities = cls.extract_structured_fields(combined_text)

            processing_ms = round((time.time() - start_time) * 1000, 1)

            status = "SUCCESS" if combined_text else "NO_TEXT_DETECTED"
            confidence_level = "HIGH" if avg_confidence >= 75 else ("MEDIUM" if avg_confidence >= 45 else "LOW")

            return {
                "success": True,
                "ocr_status": status,
                "extracted_text": combined_text,
                "confidence_score": avg_confidence,
                "confidence_level": confidence_level,
                "language_used": active_lang,
                "bengali_pack_active": has_ben,
                "pages_processed": len(images_to_process),
                "char_count": len(combined_text),
                "processing_time_ms": processing_ms,
                "preprocessing_applied": preprocess_mode,
                "extracted_entities": entities,
                "note": f"টেসেরাক্ট ইঞ্জিনে {active_lang} ভাষায় {len(images_to_process)} টি পাতা অপটিক্যাল রিকগনিশন সফল হয়েছে।"
            }

        except Exception as e:
            return {
                "success": False,
                "ocr_status": "OCR_EXECUTION_ERROR",
                "extracted_text": "",
                "error": f"OCR প্রক্রিয়াকরণে ত্রুটি ঘটেছে: {str(e)}"
            }

    @staticmethod
    def extract_structured_fields(text: str) -> Dict[str, Any]:
        """Extracts recognizable land record tokens using regex patterns."""
        fields: Dict[str, Any] = {
            "detected_deed_numbers": [],
            "detected_dag_numbers": [],
            "detected_khatian_numbers": [],
            "detected_mouza": None,
            "detected_area": None
        }

        # Match deed numbers (e.g., SAVAR-20261018-00003 or 4-6 digit Bengali/English numbers)
        deed_matches = re.findall(r'(?:SAVAR|DEED|দলিল|দলিল\s*নং)[:\s-]*([A-Za-z0-9-]+|\d+)', text, re.IGNORECASE)
        if deed_matches:
            fields["detected_deed_numbers"] = list(set([m.strip() for m in deed_matches if len(m.strip()) >= 3]))[:3]

        # Match Dag numbers (দাগ নং: ১২৩ or DAG: 123)
        dag_matches = re.findall(r'(?:দাগ|প্লট|DAG|PLOT)[:\s-]*([০-৯\d]+)', text, re.IGNORECASE)
        if dag_matches:
            fields["detected_dag_numbers"] = list(set([d.strip() for d in dag_matches]))[:5]

        # Match Khatian numbers (খতিয়ান নং: ৪৫৬ or KHATIAN: 456)
        khatian_matches = re.findall(r'(?:খতিয়ান|পর্চা|KHATIAN|PORCHA)[:\s-]*([০-৯\d]+)', text, re.IGNORECASE)
        if khatian_matches:
            fields["detected_khatian_numbers"] = list(set([k.strip() for k in khatian_matches]))[:5]

        # Detect common pilot Mouzas
        for mouza in ["আমিনবাজার", "Aminbazar", "বিরুলিয়া", "Birulia", "সাভার", "Savar"]:
            if mouza.lower() in text.lower():
                fields["detected_mouza"] = mouza
                break

        # Detect Decimal Area (e.g. 12.50 decimals or ১২.৫০ শতাংশ)
        area_match = re.search(r'([\d.]+|[০-৯.]+)\s*(?:decimals?|শতাংশ|শতক)', text, re.IGNORECASE)
        if area_match:
            fields["detected_area"] = area_match.group(0)

        return fields
