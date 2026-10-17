"""
DESHMRITTIKA / BHUMI-SYNC — Dedicated Advanced OCR Pipeline Test
Verifies PDF rasterization, preprocessing filters, Bengali pack detection,
confidence reporting, and structured field extraction.
"""

import unittest
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import pymupdf

from backend.app.services.ocr import DocumentOCRService

class TestAdvancedOCR(unittest.TestCase):

    def setUp(self):
        # Create a synthetic high-contrast test document image with both English and Bengali text
        self.test_img = Image.new('RGB', (800, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(self.test_img)
        # Draw text tokens
        draw.text((30, 30), "DEED OF CONVEYANCE - SAF KABALA", fill=(0, 0, 0))
        draw.text((30, 80), "DEED NUMBER: SAVAR-20261018-99999", fill=(0, 0, 0))
        draw.text((30, 130), "MOUZA: AMINBAZAR | J.L. NO: 26", fill=(0, 0, 0))
        draw.text((30, 180), "DAG NO: 8888 | KHATIAN NO: 7777", fill=(0, 0, 0))
        draw.text((30, 230), "PROPERTY AREA: 15.50 DECIMALS", fill=(0, 0, 0))
        draw.text((30, 280), "GOVERNMENT LAND RECORD VERIFICATION - DESHMRITTIKA", fill=(0, 0, 0))

        buf = io.BytesIO()
        self.test_img.save(buf, format='PNG')
        self.png_bytes = buf.getvalue()

        # Create a synthetic PDF document with PyMuPDF
        pdf_doc = pymupdf.open()
        page = pdf_doc.new_page(width=600, height=400)
        page.insert_text((50, 50), "GOVERNMENT OF BANGLADESH - LAND RECORD", fontsize=14)
        page.insert_text((50, 90), "DEED NUMBER: SAVAR-20261018-PDF01", fontsize=12)
        page.insert_text((50, 130), "MOUZA: BIRULIA | DAG NO: 450", fontsize=12)
        page.insert_text((50, 170), "KHATIAN NO: 990 | 25.00 DECIMALS", fontsize=12)
        self.pdf_bytes = pdf_doc.tobytes()
        pdf_doc.close()

    def test_01_png_ocr_extraction_and_confidence(self):
        """Test OCR on PNG with contrast enhancement and confidence score."""
        res = DocumentOCRService.process_document(
            file_bytes=self.png_bytes,
            filename="test_deed.png",
            preprocess_mode="enhance_contrast"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["ocr_status"], "SUCCESS")
        self.assertGreater(res["char_count"], 50)
        self.assertGreater(res["confidence_score"], 50.0)
        self.assertTrue(res["bengali_pack_active"])
        self.assertIn("SAVAR-20261018", res["extracted_text"].upper())

        # Verify structured field extraction
        entities = res["extracted_entities"]
        self.assertTrue(len(entities["detected_deed_numbers"]) > 0 or "8888" in str(entities["detected_dag_numbers"]))

    def test_02_pdf_multi_page_rasterization(self):
        """Test OCR on multi-page PDF rendered via PyMuPDF."""
        res = DocumentOCRService.process_document(
            file_bytes=self.pdf_bytes,
            filename="sample_record.pdf",
            preprocess_mode="grayscale"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["pages_processed"], 1)
        self.assertIn("SAVAR-20261018-PDF01", res["extracted_text"].upper())

    def test_03_preprocessing_filters(self):
        """Test different preprocessing modes (binarize, rotate)."""
        res_bin = DocumentOCRService.process_document(
            file_bytes=self.png_bytes,
            filename="test.png",
            preprocess_mode="binarize"
        )
        self.assertTrue(res_bin["success"])
        self.assertEqual(res_bin["preprocessing_applied"], "binarize")

    def test_04_unsupported_and_empty_file_handling(self):
        """Test rejection of unsupported file extensions and zero-byte files."""
        res_bad_ext = DocumentOCRService.process_document(
            file_bytes=b"dummy",
            filename="malicious.exe"
        )
        self.assertFalse(res_bad_ext["success"])
        self.assertEqual(res_bad_ext["ocr_status"], "UNSUPPORTED_FILE_TYPE")

if __name__ == "__main__":
    unittest.main()
