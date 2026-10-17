"""
DESHMRITTIKA / BHUMI-SYNC — 4-Screen Usability & Functional Integration Test Suite
Validates:
  Screen 1: Dashboard / Overview (Real Backend Stats, Sample Parcels, Recent Audit Feed)
  Screen 2: Dag & Khatian Search / Buyer Due Diligence (Cascading Geography, Flexible Search, 5-Point Safety Checklist)
  Screen 3: Dedicated Fraud Investigation (Risk Overview, Filterable Queue, Case Dossier & Officer Action)
  Screen 4: Ownership History / Chain of Title (Vertical Timeline, Area Flow, Document Citations)
"""

import unittest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

class TestFourScreensRedesign(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Authenticate as Officer for administrative & triage actions
        login_res_off = client.post("/api/v1/auth/login", json={
            "email": "officer@savar.land.gov.bd",
            "password": "Password123!"
        })
        assert login_res_off.status_code == 200, f"Officer login failed: {login_res_off.text}"
        cls.officer_token = login_res_off.json()["access_token"]
        cls.officer_headers = {"Authorization": f"Bearer {cls.officer_token}"}

        # Authenticate as Citizen
        login_res_cit = client.post("/api/v1/auth/login", json={
            "email": "citizen@example.com",
            "password": "Password123!"
        })
        assert login_res_cit.status_code == 200, f"Citizen login failed: {login_res_cit.text}"
        cls.citizen_token = login_res_cit.json()["access_token"]
        cls.citizen_headers = {"Authorization": f"Bearer {cls.citizen_token}"}

    # =========================================================================
    # SCREEN 1: DASHBOARD / OVERVIEW
    # =========================================================================
    def test_screen_1_dashboard_stats_and_feed(self):
        """Test Dashboard stats returns actual database metrics, sample parcels, and masked audit logs."""
        res = client.get("/api/v1/dashboard/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["status"], "SUCCESS")
        summary = data["summary"]
        self.assertEqual(summary["total_parcels"], 100000)
        self.assertEqual(summary["high_risk_records"], 2250)
        self.assertEqual(summary["pending_verification"], 4746)
        self.assertEqual(summary["completed_applications"], 57083)

        # Recent activity logs with privacy masking
        logs = data["recent_activity"]
        self.assertGreaterEqual(len(logs), 1)
        for log in logs:
            self.assertIn("id", log)
            self.assertIn("action", log)
            self.assertIn("action_text_bn", log)
            self.assertIn("timestamp", log)

        # 4 Showcase Sample Parcels
        samples = data["sample_parcels"]
        self.assertEqual(len(samples), 4)
        sample_ids = [s["parcel_id"] for s in samples]
        self.assertIn("BD-PAR-000101", sample_ids)
        self.assertIn("BD-PAR-001001", sample_ids)
        self.assertIn("BD-PAR-000205", sample_ids)
        self.assertIn("BD-PAR-000304", sample_ids)

        # Ensure sample coordinates and Bangla descriptions exist
        for s in samples:
            self.assertIn("lat", s)
            self.assertIn("lon", s)
            self.assertIn("risk_label_bn", s)
            self.assertIn("description_bn", s)

    # =========================================================================
    # SCREEN 2: DAG & KHATIAN SEARCH / BUYER DUE DILIGENCE
    # =========================================================================
    def test_screen_2_cascading_geography_selectors(self):
        """Verify 5-level cascading administrative selectors: Division -> District -> Upazila -> Union -> Mouza."""
        # 1. Divisions
        div_res = client.get("/api/v1/geography/divisions")
        self.assertEqual(div_res.status_code, 200)
        divisions = div_res.json()["divisions"]
        self.assertEqual(len(divisions), 8)
        dhaka_div = next(d for d in divisions if d["name_en"] == "Dhaka")
        self.assertEqual(dhaka_div["division_id"], "DIV-30")

        # 2. Districts filtered by Dhaka division
        dist_res = client.get(f"/api/v1/geography/districts?division_id={dhaka_div['division_id']}")
        self.assertEqual(dist_res.status_code, 200)
        districts = dist_res.json()["districts"]
        self.assertGreaterEqual(len(districts), 13)
        dhaka_dist = next(d for d in districts if d["name_en"] == "Dhaka")
        self.assertEqual(dhaka_dist["district_id"], "DIST-26")

        # 3. Upazilas filtered by Dhaka district
        upz_res = client.get(f"/api/v1/geography/upazilas?district_id={dhaka_dist['district_id']}")
        self.assertEqual(upz_res.status_code, 200)
        upazilas = upz_res.json()["upazilas"]
        savar_upz = next(u for u in upazilas if u["name_en"] == "Savar")
        self.assertEqual(savar_upz["upazila_id"], "UPZ-2672")

        # 4. Unions in Savar
        union_res = client.get(f"/api/v1/geography/unions?upazila_id={savar_upz['upazila_id']}")
        self.assertEqual(union_res.status_code, 200)
        unions = union_res.json()["unions"]
        self.assertGreaterEqual(len(unions), 1)

        # 5. Mouzas in Savar
        mouza_res = client.get(f"/api/v1/geography/mouzas?upazila_id={savar_upz['upazila_id']}")
        self.assertEqual(mouza_res.status_code, 200)
        mouzas = mouza_res.json()["mouzas"]
        self.assertGreaterEqual(len(mouzas), 1)
        mouza_names = [m["name_en"] for m in mouzas]
        self.assertIn("Aminbazar", mouza_names)

    def test_screen_2_flexible_identifier_search_and_dossier(self):
        """Verify search by Dag, Khatian, and Parcel ID with 5-point safety checklist response."""
        # Search by Dag
        res_dag = client.get("/api/v1/search?dag=101&limit=5")
        self.assertEqual(res_dag.status_code, 200)
        data_dag = res_dag.json()
        self.assertGreater(data_dag["total_matches"], 0)

        # Search by exact Parcel ID
        res_id = client.get("/api/v1/search?parcel_id=BD-PAR-000101")
        self.assertEqual(res_id.status_code, 200)
        data_id = res_id.json()
        self.assertEqual(data_id["total_matches"], 1)
        p = data_id["parcels"][0]
        self.assertEqual(p["parcel_id"], "BD-PAR-000101")

        # Due Diligence 5-Point Safety Checklist
        dd_res = client.get(f"/api/v1/due-diligence/{p['parcel_id']}")
        self.assertEqual(dd_res.status_code, 200)
        dd_data = dd_res.json()

        checklist = dd_data["safety_checklist"]
        self.assertEqual(len(checklist), 5)
        points = [c["point"] for c in checklist]
        self.assertEqual(points, [1, 2, 3, 4, 5])

        # Verify point titles in Bengali
        titles = [c["title_bn"] for c in checklist]
        self.assertTrue(any("মালিকানা" in t for t in titles))
        self.assertTrue(any("দ্বৈত" in t for t in titles))
        self.assertTrue(any("কর" in t for t in titles))
        self.assertTrue(any("মামলা" in t for t in titles))
        self.assertTrue(any("খাস" in t for t in titles))

        # Check critical rating on double-selling demo parcel
        self.assertEqual(dd_data["safety_rating"], "CRITICAL_BLOCKED")
        self.assertEqual(dd_data["risk_score"], 95)
        self.assertIn("disclaimer", dd_data)

    # =========================================================================
    # SCREEN 3: DEDICATED FRAUD INVESTIGATION & RISK ANALYSIS
    # =========================================================================
    def test_screen_3_fraud_risk_overview_stats(self):
        """Verify dedicated fraud stats endpoint returns real metrics for high risk, pending, demo scenarios, and cleared cases."""
        res = client.get("/api/v1/verification/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["high_risk_cases"], 2250)
        self.assertEqual(data["awaiting_review"], 4746)
        self.assertEqual(data["confirmed_demo_scenarios"], 500)
        self.assertEqual(data["cleared_cases"], 15004)
        self.assertEqual(data["total_recorded_cases"], 19750)

    def test_screen_3_fraud_queue_multi_filter_and_dossier(self):
        """Verify fraud case queue supports filtering by rule, severity, status, search, and returns complete investigation dossier."""
        # Filter by finding_code DS-01
        res_ds1 = client.get("/api/v1/verification/cases?finding_code=DS-01&limit=10")
        self.assertEqual(res_ds1.status_code, 200)
        cases_ds1 = res_ds1.json()["cases"]
        self.assertGreater(len(cases_ds1), 0)
        for c in cases_ds1:
            self.assertEqual(c["finding_code"], "DS-01")

        # Filter by severity CRITICAL
        res_crit = client.get("/api/v1/verification/cases?severity=CRITICAL&limit=10")
        self.assertEqual(res_crit.status_code, 200)
        cases_crit = res_crit.json()["cases"]
        self.assertGreater(len(cases_crit), 0)
        for c in cases_crit:
            self.assertEqual(c["severity"], "CRITICAL")

        # Text search by Mouza or Parcel
        res_search = client.get("/api/v1/verification/cases?search=Aminbazar&limit=5")
        self.assertEqual(res_search.status_code, 200)

        # Full Case Investigation Dossier
        target_case_id = cases_ds1[0]["case_id"]
        detail_res = client.get(f"/api/v1/verification/cases/{target_case_id}")
        self.assertEqual(detail_res.status_code, 200)
        detail = detail_res.json()

        self.assertIn("case", detail)
        self.assertIn("rule_specification", detail)
        self.assertIn("registered_deeds", detail)
        self.assertIn("review_logs", detail)

        rule_spec = detail["rule_specification"]
        self.assertEqual(rule_spec["rule_code"], "DS-01")
        self.assertIn("statutory_reference", rule_spec)
        self.assertIn("description_bn", rule_spec)

    def test_screen_3_officer_review_decision_action(self):
        """Verify authorized AC Land decision recording updates review status and creates audit log."""
        case_id = "CASE-000001"
        action_payload = {
            "action": "APPROVED_LEGITIMATE",
            "reason": "Four-screen redesign test: Field verification report reviewed and confirmed.",
            "officer_role": "AC_LAND"
        }
        res = client.post(
            f"/api/v1/verification/cases/{case_id}/review",
            json=action_payload,
            headers=self.officer_headers
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["case_id"], case_id)
        self.assertEqual(data["new_status"], "APPROVED_LEGITIMATE")
        self.assertIn("log_id", data)

    # =========================================================================
    # SCREEN 4: OWNERSHIP HISTORY / CHAIN OF TITLE
    # =========================================================================
    def test_screen_4_parcel_chain_of_title(self):
        """Verify chain of title endpoint returns chronological timeline, area transition flow, and document citations."""
        parcel_id = "BD-PAR-000101"
        res = client.get(f"/api/v1/parcels/{parcel_id}/chain-of-title")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["parcel_id"], parcel_id)
        self.assertIn("parcel", data)
        self.assertIn("timeline", data)
        self.assertIn("area_summary", data)
        self.assertIn("document_references", data)
        self.assertIn("disclaimer", data)

        # Timeline sequence validation
        timeline = data["timeline"]
        self.assertGreaterEqual(len(timeline), 3)

        # Verify historical events include survey and deed events
        event_types = [e["event_type"] for e in timeline]
        self.assertIn("SURVEY_RECORD", event_types)
        self.assertIn("DEED_TRANSFER", event_types)

        # Verify area flow numbers
        area_sum = data["area_summary"]
        self.assertIn("original_area_decimal", area_sum)
        self.assertIn("total_transferred_decimal", area_sum)
        self.assertIn("current_retained_decimal", area_sum)
        self.assertGreater(area_sum["original_area_decimal"], 0)

        # Document citations
        doc_refs = data["document_references"]
        self.assertGreaterEqual(len(doc_refs), 1)
        for doc in doc_refs:
            self.assertIn("doc_type", doc)
            self.assertIn("doc_number", doc)
            self.assertIn("registry_office", doc)

if __name__ == "__main__":
    unittest.main()
