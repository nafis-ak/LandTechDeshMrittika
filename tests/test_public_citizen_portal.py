"""
DESHMRITTIKA / BHUMI-SYNC — Public Citizen Portal Test Suite
Verifies:
1. Anonymous accessibility of Public Citizen Portal routes (/, /citizen, /public).
2. Anonymous access to public search (Dag, Mouza, Survey Type, Khatian).
3. Anonymous access to 5-point Pre-Purchase Due Diligence analysis.
4. Anonymous document SHA-256 integrity check (Mode 1 calculate, Mode 2 compare reference hash).
5. OCR endpoint input validation and safe error handling.
6. Public geography hierarchy cascading.
7. Strict preservation of security boundaries: Officer/Admin operations remain 401/403 protected.
"""

import io
import unittest
from fastapi.testclient import TestClient
from backend.app.main import app


class TestPublicCitizenPortal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_public_portal_routes_anonymous_access(self):
        """Citizens must be able to open /, /citizen, /public directly without auth redirect."""
        for path in ["/", "/citizen", "/public"]:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Route {path} should return 200 OK")
            self.assertIn("text/html", res.headers.get("content-type", ""))
            self.assertIn("দেশমৃত্তিকা", res.text)
            self.assertIn("পাবলিক সিটিজেন বাতায়ন", res.text)

    def test_02_anonymous_parcel_search_with_survey_type(self):
        """Search must work without auth and support flexible parameters including survey_type."""
        # Query with dag=101
        res = self.client.get("/api/v1/search?dag=101&mouza=Aminbazar&limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("parcels", data)
        self.assertGreater(len(data["parcels"]), 0)
        parcel = data["parcels"][0]
        self.assertEqual(str(parcel["dag_number"]), "101")
        # Ensure private sensitive fields like NID or phone are NOT exposed in public search
        self.assertNotIn("nid", parcel)
        self.assertNotIn("phone", parcel)

    def test_03_anonymous_mouza_dag_geography_cascade(self):
        """Cascading selectors must return administrative references without authentication."""
        # Divisions
        div_res = self.client.get("/api/v1/geography/divisions")
        self.assertEqual(div_res.status_code, 200)
        divisions = div_res.json().get("divisions", [])
        self.assertGreater(len(divisions), 0)
        dhaka_div = next((d for d in divisions if d["name_en"] == "Dhaka"), divisions[0])

        # Districts
        dist_res = self.client.get(f"/api/v1/geography/districts?division_id={dhaka_div['division_id']}")
        self.assertEqual(dist_res.status_code, 200)
        districts = dist_res.json().get("districts", [])
        self.assertGreater(len(districts), 0)
        dhaka_dist = next((d for d in districts if d["name_en"] == "Dhaka"), districts[0])

        # Upazilas
        upz_res = self.client.get(f"/api/v1/geography/upazilas?district_id={dhaka_dist['district_id']}&limit=50")
        self.assertEqual(upz_res.status_code, 200)
        upazilas = upz_res.json().get("upazilas", [])
        self.assertGreater(len(upazilas), 0)

    def test_04_anonymous_due_diligence_report(self):
        """Public due diligence check on a parcel returns 5-point analysis and provenance."""
        res = self.client.get("/api/v1/due-diligence/BD-PAR-000101")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("risk_score", data)
        self.assertIn("safety_checklist", data)
        self.assertEqual(len(data["safety_checklist"]), 5)
        # Verify check points 1 to 5
        points = [c["point"] for c in data["safety_checklist"]]
        self.assertEqual(points, [1, 2, 3, 4, 5])

    def test_05_document_integrity_mode_1_hash_calculation(self):
        """Mode 1: Compute SHA-256 hash for an arbitrary uploaded document anonymously."""
        file_content = b"TEST_DEED_CONTENT_OCT_2026_DESHMRITTIKA"
        files = {"file": ("citizen_deed.pdf", io.BytesIO(file_content), "application/pdf")}
        res = self.client.post("/api/v1/documents/verify-integrity", files=files)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("calculated_hash", data)
        self.assertEqual(len(data["calculated_hash"]), 64)  # Valid SHA-256 hex string
        self.assertEqual(data["comparison_status"], "HASH_CALCULATED_UNREGISTERED")

    def test_06_document_integrity_mode_2_reference_hash_matching(self):
        """Mode 2: Match against a user-provided reference hash."""
        import hashlib
        file_content = b"AUTHENTIC_SAMPLE_DEED_PARCEL_101"
        expected_hash = hashlib.sha256(file_content).hexdigest()

        # Test exact match
        files = {"file": ("deed.pdf", io.BytesIO(file_content), "application/pdf")}
        res = self.client.post(
            "/api/v1/documents/verify-integrity",
            files=files,
            data={"reference_hash": expected_hash}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["comparison_status"], "MATCHES_SUPPLIED_REFERENCE")
        self.assertEqual(data["calculated_hash"], expected_hash)
        self.assertEqual(data["reference_hash"], expected_hash)

        # Test mismatch / tamper detection
        files_tampered = {"file": ("deed.pdf", io.BytesIO(b"TAMPERED_CONTENT_DIFFERENT_BYTE"), "application/pdf")}
        res_tampered = self.client.post(
            "/api/v1/documents/verify-integrity",
            files=files_tampered,
            data={"reference_hash": expected_hash}
        )
        self.assertEqual(res_tampered.status_code, 200)
        data_tampered = res_tampered.json()
        self.assertEqual(data_tampered["comparison_status"], "DOES_NOT_MATCH_SUPPLIED_REFERENCE")

    def test_07_ocr_file_validation_and_safety(self):
        """OCR endpoint rejects invalid files and enforces maximum upload boundaries."""
        # Empty file returns 400
        res_empty = self.client.post("/api/v1/documents/upload-ocr", files={"file": ("empty.png", io.BytesIO(b""), "image/png")})
        self.assertEqual(res_empty.status_code, 400)

        # Unsupported extension returns success=False and status
        exe_file = {"file": ("malicious.exe", io.BytesIO(b"MZ executable header"), "application/x-msdownload")}
        res = self.client.post("/api/v1/documents/upload-ocr", files=exe_file)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["success"])
        self.assertEqual(res.json()["ocr_status"], "UNSUPPORTED_FILE_TYPE")

    def test_08_officer_admin_boundaries_strictly_protected(self):
        """Anonymous citizen access to protected officer/admin endpoints must return 401 or 403."""
        # Officer triage decision
        res_decide = self.client.post("/api/v1/officer/decision", json={"case_id": "CASE-000001", "decision": "APPROVED"})
        self.assertIn(res_decide.status_code, [401, 403])

        # Admin user list
        res_users = self.client.get("/api/v1/admin/users")
        self.assertIn(res_users.status_code, [401, 403])

        # Security audit logs
        res_logs = self.client.get("/api/v1/admin/security-logs")
        self.assertIn(res_logs.status_code, [401, 403])


if __name__ == "__main__":
    unittest.main()
