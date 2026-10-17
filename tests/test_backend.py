"""
DESHMRITTIKA / BHUMI-SYNC — Backend Integration & Unit Test Suite
Covers all 6 LandTech Problem Tracks (P1–P6), RBAC Security, Due Diligence Dossiers,
Double-Selling Verification, Document Cryptographic Integrity, and Officer Audit Logs.
"""

import os
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import BASE_DIR, DOCUMENTS_DIR

client = TestClient(app)

class TestBackendEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Obtain tokens for Citizen and Officer roles
        login_res_cit = client.post("/api/v1/auth/login", json={
            "email": "citizen@example.com",
            "password": "Password123!"
        })
        assert login_res_cit.status_code == 200, f"Citizen login failed: {login_res_cit.text}"
        cls.citizen_token = login_res_cit.json()["access_token"]
        cls.citizen_headers = {"Authorization": f"Bearer {cls.citizen_token}"}

        login_res_off = client.post("/api/v1/auth/login", json={
            "email": "officer@savar.land.gov.bd",
            "password": "Password123!"
        })
        assert login_res_off.status_code == 200, f"Officer login failed: {login_res_off.text}"
        cls.officer_token = login_res_off.json()["access_token"]
        cls.officer_headers = {"Authorization": f"Bearer {cls.officer_token}"}

    def test_01_health_and_root(self):
        """Verify API health check, database status, and supported tracks."""
        res = client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertTrue(data["database"]["connected"])
        self.assertGreater(data["database"]["size_mb"], 0)
        self.assertListEqual(data["tracks_supported"], ["P1", "P2", "P3", "P4", "P5", "P6"])

        root_res = client.get("/")
        self.assertEqual(root_res.status_code, 200)

    def test_02_authentication_and_rbac(self):
        """Verify session issuance, authentication checks, and strict RBAC enforcement."""
        # Invalid email credentials
        res_invalid = client.post("/api/v1/auth/login", json={
            "email": "unknown_hacker@darkweb.org",
            "password": "mock"
        })
        self.assertEqual(res_invalid.status_code, 401)

        # /auth/me with valid citizen token
        res_me = client.get("/api/v1/auth/me", headers=self.citizen_headers)
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()["role"], "CITIZEN")

        # Citizen attempts to access Officer Queue -> MUST be 403 Forbidden
        res_forbidden = client.get("/api/v1/officer/queue", headers=self.citizen_headers)
        self.assertEqual(res_forbidden.status_code, 403)
        self.assertIn("lacks authorized officer review permissions", res_forbidden.json()["detail"])

        # Officer accesses Officer Queue -> MUST be 200 OK
        res_officer = client.get("/api/v1/officer/queue", headers=self.officer_headers)
        self.assertEqual(res_officer.status_code, 200)
        officer_data = res_officer.json()
        self.assertEqual(officer_data["role"], "OFFICER")
        self.assertIn("queue", officer_data)

    def test_03_universal_search(self):
        """Verify indexed search across Dag, Mouza, Khatian, and Parcel ID."""
        # Search by parcel_id
        res_id = client.get("/api/v1/search?parcel_id=BD-PAR-000101")
        self.assertEqual(res_id.status_code, 200)
        self.assertGreaterEqual(res_id.json()["total_matches"], 1)
        self.assertEqual(res_id.json()["parcels"][0]["parcel_id"], "BD-PAR-000101")

        # Search by mouza
        res_mouza = client.get("/api/v1/search?mouza=Aminbazar&limit=5")
        self.assertEqual(res_mouza.status_code, 200)
        self.assertGreaterEqual(res_mouza.json()["total_matches"], 1)

        # Search by dag
        res_dag = client.get("/api/v1/search?dag=101&limit=5")
        self.assertEqual(res_dag.status_code, 200)
        self.assertGreaterEqual(res_dag.json()["total_matches"], 1)

    def test_04_parcel_profile_and_geojson(self):
        """Verify full 14-entity relational linked profile and GeoJSON endpoint."""
        res_profile = client.get("/api/v1/parcels/BD-PAR-000101")
        self.assertEqual(res_profile.status_code, 200)
        p = res_profile.json()
        self.assertEqual(p["parcel_id"], "BD-PAR-000101")
        self.assertIn("current_owners", p)
        self.assertIn("historical_deeds", p)
        self.assertIn("tax_status", p)
        self.assertIn("coordinates_geojson", p)

        # GeoJSON endpoint
        res_geo = client.get("/api/v1/parcels/BD-PAR-000101/geojson")
        self.assertEqual(res_geo.status_code, 200)
        geo = res_geo.json()
        self.assertEqual(geo["type"], "Feature")
        self.assertEqual(geo["geometry"]["type"], "Polygon")
        self.assertEqual(geo["properties"]["parcel_id"], "BD-PAR-000101")

    def test_05_p3_double_selling_evaluation(self):
        """Verify DS-01 double-selling detection on seeded fraud parcel and DS-02 negative control."""
        # 1. Seeded DS-01 Fraud Parcel (BD-PAR-000101)
        res_ds1 = client.get("/api/v1/verification/evaluate/BD-PAR-000101")
        self.assertEqual(res_ds1.status_code, 200)
        eval_ds1 = res_ds1.json()
        self.assertFalse(eval_ds1["is_safe_for_transaction"])
        self.assertGreaterEqual(eval_ds1["overall_risk_score"], 90)
        finding_codes = [f["finding_code"] for f in eval_ds1["findings"]]
        self.assertIn("DS-01", finding_codes)

        # 2. Clean Resale Sequential Control Parcel (BD-PAR-001001)
        res_ds2 = client.get("/api/v1/verification/evaluate/BD-PAR-001001")
        self.assertEqual(res_ds2.status_code, 200)
        eval_ds2 = res_ds2.json()
        self.assertTrue(eval_ds2["is_safe_for_transaction"])
        self.assertEqual(eval_ds2["overall_risk_score"], 0)
        finding_codes_clean = [f["finding_code"] for f in eval_ds2["findings"]]
        self.assertIn("DS-02", finding_codes_clean)

    def test_06_p5_buyer_due_diligence_dossier(self):
        """Verify 5-Point Safety Check due-diligence dossier generation."""
        # Evaluate flagged parcel
        res_dossier = client.get("/api/v1/due-diligence/BD-PAR-000101")
        self.assertEqual(res_dossier.status_code, 200)
        dossier = res_dossier.json()
        self.assertEqual(dossier["parcel"]["parcel_id"], "BD-PAR-000101")
        self.assertIn(dossier["safety_rating"], ["HIGH_RISK", "CRITICAL_BLOCKED"])
        self.assertEqual(len(dossier["safety_checklist"]), 5)
        self.assertIn("সতর্কীকরণ", dossier["disclaimer"])

        # Evaluate clean parcel
        res_clean = client.get("/api/v1/due-diligence/BD-PAR-001001")
        self.assertEqual(res_clean.status_code, 200)
        dossier_clean = res_clean.json()
        self.assertEqual(dossier_clean["safety_rating"], "SAFE")
        self.assertTrue(dossier_clean["tax_compliant"])

    def test_07_officer_review_decision_and_audit(self):
        """Verify officer triage queue, decision submission, and persistent audit logging."""
        # 1. Fetch queue
        queue_res = client.get("/api/v1/officer/queue?limit=1", headers=self.officer_headers)
        self.assertEqual(queue_res.status_code, 200)
        queue = queue_res.json()["queue"]
        self.assertGreater(len(queue), 0)
        case_id = queue[0]["case_id"]

        # 2. Record review decision
        decision_res = client.post("/api/v1/officer/decision", json={
            "case_id": case_id,
            "action": "REQUESTED_PHYSICAL_INSPECTION",
            "reason": "Test audit decision: Discrepancy observed between registry deed and field porcha."
        }, headers=self.officer_headers)
        self.assertEqual(decision_res.status_code, 200)
        dec_data = decision_res.json()
        self.assertEqual(dec_data["status"], "SUCCESS")
        self.assertIn("LOG-", dec_data["log_id"])

        # 3. Verify audit log persistence
        audit_res = client.get("/api/v1/officer/audit-logs?limit=5", headers=self.officer_headers)
        self.assertEqual(audit_res.status_code, 200)
        audit_logs = audit_res.json()["audit_logs"]
        matching = [l for l in audit_logs if l["case_id"] == case_id]
        self.assertGreater(len(matching), 0)
        self.assertEqual(matching[0]["action"], "REQUESTED_PHYSICAL_INSPECTION")

    def test_08_p4_mutation_precheck(self):
        """Verify Smart e-Mutation pre-checks against khas, tax arrears, and active disputes."""
        pre_res = client.post("/api/v1/mutations/pre-check", json={
            "parcel_id": "BD-PAR-000101",
            "deed_id": "SAVAR-20261018-000101",
            "applicant_id": "OWN-000305"
        })
        self.assertEqual(pre_res.status_code, 200)
        pre_data = pre_res.json()
        self.assertIn("can_proceed", pre_data)
        self.assertIn("precheck_summary_bn", pre_data)

    def test_09_p2_cryptographic_document_integrity(self):
        """Verify SHA-256 tamper detection on authentic vs modified document binaries."""
        sample_doc_path = DOCUMENTS_DIR / "DOC-000001_SAVAR-20261018-00003.png"
        self.assertTrue(sample_doc_path.exists(), f"Sample document {sample_doc_path} not found.")

        # Test authentic document
        with open(sample_doc_path, "rb") as f:
            file_bytes = f.read()

        res_auth = client.post(
            "/api/v1/documents/verify-integrity",
            files={"file": ("DOC-000001.png", file_bytes, "image/png")}
        )
        self.assertEqual(res_auth.status_code, 200)
        data_auth = res_auth.json()
        self.assertTrue(data_auth["is_authentic"])
        self.assertEqual(data_auth["matched_document_id"], "DOC-000001")
        self.assertEqual(data_auth["status_label"], "VERIFIED_AUTHENTIC")

        # Test tampered document (append corrupt byte)
        tampered_bytes = file_bytes + b"TAMPERED_CONTENT_TEST"
        res_tamper = client.post(
            "/api/v1/documents/verify-integrity",
            files={"file": ("DOC-000001_tampered.png", tampered_bytes, "image/png")}
        )
        self.assertEqual(res_tamper.status_code, 200)
        data_tamper = res_tamper.json()
        self.assertFalse(data_tamper["is_authentic"])
        self.assertEqual(data_tamper["status_label"], "TAMPER_DETECTED_OR_UNREGISTERED")

    def test_10_p1_document_ocr_pipeline(self):
        """Verify Tesseract OCR execution and honest status reporting."""
        sample_doc_path = DOCUMENTS_DIR / "DOC-000001_SAVAR-20261018-00003.png"
        with open(sample_doc_path, "rb") as f:
            file_bytes = f.read()

        res_ocr = client.post(
            "/api/v1/documents/upload-ocr",
            files={"file": ("sample_deed.png", file_bytes, "image/png")}
        )
        self.assertEqual(res_ocr.status_code, 200)
        ocr_data = res_ocr.json()
        self.assertTrue(ocr_data["success"])
        self.assertIn("ocr_status", ocr_data)
        # Check text extracted
        self.assertGreater(ocr_data["char_count"], 0)
        self.assertIn("DEED", ocr_data["extracted_text"].upper())

if __name__ == "__main__":
    unittest.main()
