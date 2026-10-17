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

    @classmethod
    def extract_structured_fields(cls, text: str) -> Dict[str, Any]:
        """Extracts recognizable land record tokens using enhanced regex patterns for official Bangladesh deeds and khatians."""
        fields: Dict[str, Any] = {
            "detected_deed_numbers": [],
            "detected_deed_type": None,
            "detected_dag_numbers": [],
            "detected_dag_numbers_ar": [],
            "detected_khatian_numbers": [],
            "detected_khatian_numbers_ar": [],
            "detected_mouza": None,
            "detected_jl_number": None,
            "detected_area": None,
            "detected_land_class": None,
            "detected_seller": None,
            "detected_buyer": None
        }

        bn_to_ar = {'০':'0', '১':'1', '২':'2', '৩':'3', '৪':'4', '৫':'5', '৬':'6', '৭':'7', '৮':'8', '৯':'9'}
        def to_arabic_num(s: str) -> str:
            return ''.join(bn_to_ar.get(ch, ch) for ch in str(s))

        # 1. Deed Type Detection
        if re.search(r'সাফ[-\s]*কবালা|বিক্রয়[-\s]*দলিল|SAF\s*KABALA', text, re.IGNORECASE):
            fields["detected_deed_type"] = "সাফ-কবালা (Deed of Outright Sale)"
        elif re.search(r'হেবা\s*বিল\s*এওয়াজ', text, re.IGNORECASE):
            fields["detected_deed_type"] = "হেবা বিল এওয়াজ (Gift for Consideration)"
        elif re.search(r'দানপত্র|হেবা', text, re.IGNORECASE):
            fields["detected_deed_type"] = "দানপত্র / হেবা (Deed of Gift)"
        elif re.search(r'বণ্টননামা', text, re.IGNORECASE):
            fields["detected_deed_type"] = "বণ্টননামা (Partition Deed)"
        elif re.search(r'খত[িী]*[য়য][় া]*ন|স্বত্বল[িী]*প[িী]|পর্চা|রেকর্ড\s*অব\s*রাইটস|ROR|KHATIAN', text, re.IGNORECASE):
            fields["detected_deed_type"] = "আর.এস. খতিয়ান / পরচা (Record of Rights)"

        # 2. Match Deed Numbers
        deed_candidates = []
        for m in re.findall(r'SAVAR[-_]\d{8}[-_][A-Za-z0-9-]+', text, re.IGNORECASE):
            deed_candidates.append(m.strip().upper())
        for m in re.findall(r'([০-৯\d]{3,6}\s*/\s*[০-৯\d]{4})', text):
            deed_candidates.append(m.strip().replace(" ", ""))
        for m in re.findall(r'(?:দলিল\s*নং|দলিল\s*নম্বর|DEED\s*NO)[\s:.-]*([০-৯\d]{3,8})', text, re.IGNORECASE):
            val = m.strip()
            if val.upper() not in ["MOUZA", "NUMBER", "DEED", "SAVAR"]:
                deed_candidates.append(val)

        seen_deeds = set()
        for d in deed_candidates:
            if d not in seen_deeds and len(d) >= 3:
                seen_deeds.add(d)
                fields["detected_deed_numbers"].append(d)
        fields["detected_deed_numbers"] = fields["detected_deed_numbers"][:3]

        # 3. Match Dag numbers (both inline labels and table grid rows)
        dags, dags_ar = [], []
        dag_matches = re.findall(r'(?:হাল\s*দাগ|সাবেক\s*দাগ|দাগ|প্লট|DAG|PLOT)[\s:.-]*(?:নং|নম্বর|NO)?[\s:.-]*([০-৯\d]{1,6})', text, re.IGNORECASE)
        for d in dag_matches:
            d_str = d.strip()
            if d_str and d_str not in dags:
                dags.append(d_str)
                dags_ar.append(to_arabic_num(d_str))

        # Check for tabular Dag rows following header (e.g. ১০৪ (104))
        table_dags = re.findall(r'\n\s*([০-৯\d]{1,6})\s*\([০-৯\d]+\)', text)
        for td in table_dags:
            td_str = td.strip()
            if td_str and td_str not in dags:
                dags.append(td_str)
                dags_ar.append(to_arabic_num(td_str))

        fields["detected_dag_numbers"] = dags[:5]
        fields["detected_dag_numbers_ar"] = dags_ar[:5]

        # 4. Match Khatian numbers
        khatian_matches = re.findall(r'(?:আর[\s.]*এস[\s.]*খত|এস[\s.]*এ[\s.]*খত|বি[\s.]*এস[\s.]*খত|খতিয়ান|খতিয়ান|খতয়ান|খতয়ান|খতিয|খতয|KHATIAN|PORCHA)[\s:.-]*(?:নং|নম্বর|NO)?[\s:.-]*([০-৯\d]{1,6})', text, re.IGNORECASE)
        if khatian_matches:
            khats, khats_ar = [], []
            for k in khatian_matches:
                k_str = k.strip()
                if k_str and k_str not in khats:
                    khats.append(k_str)
                    khats_ar.append(to_arabic_num(k_str))
            fields["detected_khatian_numbers"] = khats[:5]
            fields["detected_khatian_numbers_ar"] = khats_ar[:5]

        # 5. Detect Mouza and J.L. Number (Prioritize Specific Mouza over Upazila)
        mouzas = [
            ("আমিনবাজার", ["আমিনবাজার", "আমনিবাজার", "aminbazar"], "২৬ (26)"),
            ("বিরুলিয়া", ["বিরুলিয়া", "বিরুলীয়া", "birulia"], "২৭ (27)"),
            ("সাভার পৌরসভা", ["সাভার", "savar"], "২৮ (28)")
        ]
        for canonical, variants, jl in mouzas:
            if any(v.lower() in text.lower() for v in variants):
                fields["detected_mouza"] = canonical
                fields["detected_jl_number"] = jl
                break

        # 6. Detect Decimal Area
        area_match = re.search(r'([\d.]+|[০-৯.]+)\s*(?:decimals?|শতাংশ|শতক|একর)', text, re.IGNORECASE)
        if area_match:
            fields["detected_area"] = area_match.group(0)

        # 7. Detect Land Classification
        classes = [
            ("নাল (কৃষি জমি)", ["নাল", "কৃষি জমি", "nal", "agricultural"]),
            ("ভিটি / বাস্তু (উঁচু জমি)", ["ভিটি", "বাস্তু", "ভিটা", "homestead"]),
            ("বাণিজ্যিক", ["বাণিজ্যিক", "commercial"]),
            ("পুকুর / জলাশয়", ["পুকুর", "ডোবা", "জলাশয়", "pond"]),
            ("বাগান", ["বাগান", "ফলবাগান", "orchard"])
        ]
        for label, terms in classes:
            if any(term in text.lower() for term in terms):
                fields["detected_land_class"] = label
                break

        # 8. Detect Seller / Donor
        seller_match = re.search(r'(?:দাতার\s*নাম|বিক্রেতার\s*নাম)[:\s.-]*([^\n,।]+)', text)
        if seller_match:
            s_name = seller_match.group(1).strip()
            if len(s_name) >= 3 and not any(x in s_name for x in ["সাভার", "আমিনবাজার", "ঢাকা", "দলিল", "দাগ"]):
                fields["detected_seller"] = s_name

        # 9. Detect Purchaser / Donee
        buyer_match = re.search(r'(?:গ্রহীতার\s*নাম|ক্রেতার\s*নাম)[:\s.-]*([^\n,।]+)', text)
        if buyer_match:
            b_name = buyer_match.group(1).strip()
            if len(b_name) >= 3 and not any(x in b_name for x in ["সাভার", "আমিনবাজার", "ঢাকা", "দলিল", "দাগ"]):
                fields["detected_buyer"] = b_name

        return fields
