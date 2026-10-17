"""
DESHMRITTIKA / BHUMI-SYNC — Bangladesh-Wide Geography & Synthetic Land Officials Test Suite
Phase 7 Automated Verification covering:
1. Administrative hierarchy relationships and cascading filters
2. Duplicate mouza names across different administrative areas
3. 8-division and 64-district nationwide coverage verification
4. Missing or incomplete upazila, union, and mouza record handling
5. GeoJSON RFC 7946 validity, CRS (EPSG:4326), and spatial bounding-box queries
6. Parcels with polygons, bounding boxes, and missing geometry handling
7. Map API pagination, bbox viewport performance, and limits
8. Synthetic official profiles, reserved demo email domains (@demo.land.gov.bd), and demo watermarks
9. Official-to-office and jurisdiction relationships
10. Directory search, multi-field filters, pagination, and empty states
11. Role permissions and authorization checks
12. Regression testing for existing OCR, hash verification, fraud detection, due diligence, and audit logging
"""

import unittest
import sqlite3
import json
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import DATABASE_PATH

client = TestClient(app)

class TestBangladeshGeographyAndOfficials(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Database verification
        cls.db_path = DATABASE_PATH
        cls.conn = sqlite3.connect(cls.db_path)
        cls.conn.row_factory = sqlite3.Row

        # Login tokens for RBAC tests
        res_cit = client.post("/api/v1/auth/login", json={"email": "citizen@example.com", "password": "Password123!"})
        cls.cit_token = res_cit.json().get("access_token")
        cls.cit_headers = {"Authorization": f"Bearer {cls.cit_token}"} if cls.cit_token else {}

        res_off = client.post("/api/v1/auth/login", json={"email": "officer@savar.land.gov.bd", "password": "Password123!"})
        cls.off_token = res_off.json().get("access_token")
        cls.off_headers = {"Authorization": f"Bearer {cls.off_token}"} if cls.off_token else {}

        res_adm = client.post("/api/v1/auth/login", json={"email": "admin@deshmrittika.gov.bd", "password": "Password123!"})
        cls.adm_token = res_adm.json().get("access_token")
        cls.adm_headers = {"Authorization": f"Bearer {cls.adm_token}"} if cls.adm_token else {}

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'conn'):
            cls.conn.close()

    # =========================================================================
    # 1. HIERARCHY RELATIONSHIPS & CASCADING FILTERS
    # =========================================================================
    def test_01_administrative_hierarchy_cascading(self):
        """Validates cascading endpoints: Division -> District -> Upazila -> Union -> Mouza."""
        # Step 1: Divisions
        res_div = client.get("/api/v1/geography/divisions")
        self.assertEqual(res_div.status_code, 200)
        div_data = res_div.json()
        self.assertIn("divisions", div_data)
        self.assertEqual(len(div_data["divisions"]), 8)

        # Pick Dhaka Division (DIV-30)
        dhaka_div = next((d for d in div_data["divisions"] if d["division_id"] == "DIV-30"), None)
        self.assertIsNotNone(dhaka_div)
        self.assertEqual(dhaka_div["name_en"], "Dhaka")

        # Step 2: Districts in Dhaka Division
        res_dist = client.get("/api/v1/geography/districts?division_id=DIV-30")
        self.assertEqual(res_dist.status_code, 200)
        dist_data = res_dist.json()
        self.assertGreater(dist_data["total"], 0)
        for d in dist_data["districts"]:
            self.assertEqual(d["division_id"], "DIV-30")

        # Pick Dhaka District (DIST-26)
        dhaka_dist = next((d for d in dist_data["districts"] if d["district_id"] == "DIST-26"), None)
        self.assertIsNotNone(dhaka_dist)

        # Step 3: Upazilas in Dhaka District
        res_upz = client.get("/api/v1/geography/upazilas?district_id=DIST-26")
        self.assertEqual(res_upz.status_code, 200)
        upz_data = res_upz.json()
        self.assertGreater(upz_data["total"], 0)
        for u in upz_data["upazilas"]:
            self.assertEqual(u["district_id"], "DIST-26")

        # Pick Savar Upazila (UPZ-2672)
        savar_upz = next((u for u in upz_data["upazilas"] if u["upazila_id"] == "UPZ-2672"), None)
        self.assertIsNotNone(savar_upz)

        # Step 4: Unions in Savar
        res_uni = client.get("/api/v1/geography/unions?upazila_id=UPZ-2672")
        self.assertEqual(res_uni.status_code, 200)
        uni_data = res_uni.json()
        self.assertGreaterEqual(uni_data["total"], 11)  # 11 sample unions in Savar pilot

        # Step 5: Mouzas in Savar
        res_mouza = client.get("/api/v1/geography/mouzas?upazila_id=UPZ-2672")
        self.assertEqual(res_mouza.status_code, 200)
        mouza_data = res_mouza.json()
        self.assertGreaterEqual(mouza_data["total"], 5)
        # Verify JL numbers present
        aminbazar = next((m for m in mouza_data["mouzas"] if m["name_en"] == "Aminbazar"), None)
        self.assertIsNotNone(aminbazar)
        self.assertEqual(int(aminbazar["jl_number"]), 12)

    # =========================================================================
    # 2. DUPLICATE MOUZA NAMES IN DIFFERENT ADMINISTRATIVE AREAS
    # =========================================================================
    def test_02_duplicate_mouza_names_handling(self):
        """Verifies that mouzas with duplicate or similar names across districts have distinct stable IDs."""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT name_en, COUNT(*) as cnt
            FROM geo_mouzas
            GROUP BY name_en
            HAVING cnt > 1
        """)
        dupes = cur.fetchall()

        # Check Mirzapur (Gazipur vs Tangail)
        cur.execute("SELECT mouza_id, name_en, upazila_id, jl_number FROM geo_mouzas WHERE name_en = 'Mirzapur'")
        rows = cur.fetchall()
        if len(rows) > 1:
            ids = [r["mouza_id"] for r in rows]
            self.assertEqual(len(ids), len(set(ids)), "Duplicate mouza names must have distinct unique IDs")
            upazilas = [r["upazila_id"] for r in rows]
            self.assertNotEqual(upazilas[0], upazilas[1], "Same-named mouzas must belong to distinct upazilas")

    # =========================================================================
    # 3. NATIONWIDE COVERAGE: 8 DIVISIONS & 64 DISTRICTS
    # =========================================================================
    def test_03_nationwide_coverage_counts(self):
        """Asserts authoritative coverage of all 8 divisions and all 64 districts in Bangladesh."""
        cur = self.conn.cursor()

        # Exactly 8 divisions
        cur.execute("SELECT COUNT(*) FROM geo_divisions")
        div_count = cur.fetchone()[0]
        self.assertEqual(div_count, 8, f"Expected 8 divisions, found {div_count}")

        # Authoritative 8 division codes
        expected_div_codes = {"10", "20", "30", "40", "45", "50", "55", "60"}
        cur.execute("SELECT bbs_code FROM geo_divisions")
        actual_div_codes = {r[0] for r in cur.fetchall()}
        self.assertEqual(expected_div_codes, actual_div_codes)

        # Exactly 64 districts
        cur.execute("SELECT COUNT(*) FROM geo_districts")
        dist_count = cur.fetchone()[0]
        self.assertEqual(dist_count, 64, f"Expected 64 districts, found {dist_count}")

        # Over 500 upazilas
        cur.execute("SELECT COUNT(*) FROM geo_upazilas")
        upz_count = cur.fetchone()[0]
        self.assertGreaterEqual(upz_count, 500, f"Expected >= 500 upazilas, found {upz_count}")

    # =========================================================================
    # 4. MISSING OR INCOMPLETE GEOGRAPHIC COVERAGE HANDLING
    # =========================================================================
    def test_04_missing_or_incomplete_coverage_handling(self):
        """Verifies API returns graceful empty states and does not invent fake records for areas without digital mouzas."""
        # Query upazila in Bandarban (UPZ-0314 Ruma)
        res = client.get("/api/v1/geography/mouzas?upazila_id=UPZ-0314")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total"], 0)
        self.assertEqual(data["mouzas"], [])
        self.assertEqual(data["coverage_status"], "INCOMPLETE_OFFICIAL_DATA")

        # Nonexistent upazila ID
        res_non = client.get("/api/v1/geography/mouzas?upazila_id=UPZ-NONEXISTENT")
        self.assertEqual(res_non.status_code, 200)
        self.assertEqual(res_non.json()["total"], 0)

    # =========================================================================
    # 5. GEOJSON VALIDITY & COORDINATE REFERENCE SYSTEM (EPSG:4326)
    # =========================================================================
    def test_05_geojson_validity_and_crs(self):
        """Verifies spatial layers return valid RFC 7946 GeoJSON FeatureCollections in WGS84 (lon, lat)."""
        # Acquisition Zones
        res_acq = client.get("/api/v1/parcels/layers/acquisition-zones")
        self.assertEqual(res_acq.status_code, 200)
        data_acq = res_acq.json()
        self.assertEqual(data_acq["type"], "FeatureCollection")
        self.assertGreater(len(data_acq["features"]), 0)

        for feat in data_acq["features"]:
            self.assertEqual(feat["type"], "Feature")
            self.assertIn("geometry", feat)
            geom = feat["geometry"]
            self.assertEqual(geom["type"], "Polygon")
            # Verify coordinates are in Bangladesh bounding box (lon ~88-93, lat ~20-27)
            for ring in geom["coordinates"]:
                for lon, lat in ring:
                    self.assertTrue(88.0 <= lon <= 93.0, f"Longitude {lon} out of Bangladesh bounds")
                    self.assertTrue(20.0 <= lat <= 27.0, f"Latitude {lat} out of Bangladesh bounds")

        # Khas Land
        res_khas = client.get("/api/v1/parcels/layers/khas-land?limit=10")
        self.assertEqual(res_khas.status_code, 200)
        data_khas = res_khas.json()
        self.assertEqual(data_khas["type"], "FeatureCollection")
        self.assertGreater(len(data_khas["features"]), 0)

    # =========================================================================
    # 6. BOUNDING-BOX SPATIAL PARCEL RETRIEVAL & INDEXING
    # =========================================================================
    def test_06_parcels_spatial_bbox_queries(self):
        """Verifies viewport bounding-box parcel retrieval and performance."""
        # Query valid bounding box in Savar pilot area
        bbox = "90.31,23.79,90.33,23.81"
        res = client.get(f"/api/v1/parcels/map?bbox={bbox}&limit=50")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertGreater(len(data["features"]), 0)
        self.assertLessEqual(len(data["features"]), 50)

        # Verify disclaimer on demo parcel features
        self.assertIn("DEMO DATA", data["properties"]["disclaimer"])

        # Query outside bounding box (e.g. Bay of Bengal)
        empty_bbox = "90.0,20.0,90.1,20.1"
        res_empty = client.get(f"/api/v1/parcels/map?bbox={empty_bbox}&limit=50")
        self.assertEqual(res_empty.status_code, 200)
        self.assertEqual(len(res_empty.json()["features"]), 0)

        # Query with malformed bbox (gracefully handled without 500 error)
        res_malformed = client.get("/api/v1/parcels/map?bbox=invalid,bbox&limit=10")
        self.assertEqual(res_malformed.status_code, 200)

    # =========================================================================
    # 7. PARCEL LOCATION & DUE DILIGENCE LINKAGE
    # =========================================================================
    def test_07_parcel_location_and_due_diligence(self):
        """Verifies single parcel location endpoint grounding and due diligence synthesis."""
        res = client.get("/api/v1/parcels/BD-PAR-000001/location")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["parcel_id"], "BD-PAR-000001")
        self.assertEqual(data["mouza"], "Aminbazar")
        self.assertEqual(data["upazila"], "Savar")
        self.assertEqual(data["district"], "Dhaka")
        self.assertIn("centroid", data)
        self.assertIn("boundary_polygon", data)
        self.assertIn("due_diligence_summary", data)
        self.assertIn("DEMO DATA", data["disclaimer"])

        # Nonexistent parcel returns 404
        res_404 = client.get("/api/v1/parcels/BD-PAR-NONEXISTENT/location")
        self.assertEqual(res_404.status_code, 404)

    # =========================================================================
    # 8. SYNTHETIC OFFICIAL PROFILES & CONTACT SAFEGUARDS
    # =========================================================================
    def test_08_synthetic_official_safeguards(self):
        """Strictly validates fictional contact safeguards: reserved emails, fictional phones, demo watermarks."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM land_officials")
        officials = cur.fetchall()
        self.assertGreater(len(officials), 0)

        for off in officials:
            # 1. Reserved demo email domain
            email = off["email_demo"]
            self.assertTrue(email.endswith("@demo.land.gov.bd"), f"Non-demo email detected: {email}")

            # 2. Marked fictional phone number
            phone = off["phone_demo"]
            self.assertTrue("ডেমো" in phone or "+880 1700-000" in phone, f"Unsafe phone number: {phone}")

            # 3. Demo provenance badge
            provenance = off["provenance"]
            self.assertIn("DEMO OFFICIAL", provenance)
            self.assertIn("NOT A REAL PERSON", provenance)

            # 4. Explicit demo label in Bengali name
            name_bn = off["name_bn"]
            self.assertIn("ডেমো", name_bn)

            # 5. Portrait image is non-photographic SVG avatar
            portrait = off["portrait_image"]
            self.assertTrue(portrait.endswith(".svg"), f"Portrait must be an SVG asset: {portrait}")

    # =========================================================================
    # 9. OFFICIAL-TO-OFFICE JURISDICTION RELATIONSHIPS
    # =========================================================================
    def test_09_official_jurisdiction_relationships(self):
        """Verifies that each official is linked to a valid land office and administrative hierarchy."""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT o.official_id, o.name_en, o.designation_code,
                   f.office_id, f.office_type, f.division_id, f.district_id, f.upazila_id
            FROM land_officials o
            JOIN land_offices f ON o.office_id = f.office_id
        """)
        linked = cur.fetchall()
        self.assertEqual(len(linked), 17)

        # Check Savar AC Land officer
        savar_acland = next((r for r in linked if r["designation_code"] == "AC_LAND" and r["upazila_id"] == "UPZ-2672"), None)
        self.assertIsNotNone(savar_acland)
        self.assertEqual(savar_acland["office_id"], "OFFICE-SAVAR-ACLAND")
        self.assertEqual(savar_acland["division_id"], "DIV-30")
        self.assertEqual(savar_acland["district_id"], "DIST-26")

    # =========================================================================
    # 10. DIRECTORY SEARCH, MULTI-FIELD FILTERS & PAGINATION
    # =========================================================================
    def test_10_directory_search_and_filters(self):
        """Verifies officials directory query parameters, filters, pagination and empty states."""
        # 1. Filter by designation
        res_desig = client.get("/api/v1/officials?designation=AC_LAND")
        self.assertEqual(res_desig.status_code, 200)
        data_desig = res_desig.json()
        self.assertGreater(data_desig["total"], 0)
        for o in data_desig["officials"]:
            self.assertEqual(o["designation_code"], "AC_LAND")

        # 2. Filter by division
        res_div = client.get("/api/v1/officials?division_id=DIV-30")
        self.assertEqual(res_div.status_code, 200)
        self.assertGreater(res_div.json()["total"], 0)

        # 3. Filter by search keyword
        res_search = client.get("/api/v1/officials?search=সাভার")
        self.assertEqual(res_search.status_code, 200)
        self.assertGreater(res_search.json()["total"], 0)

        # 4. Pagination
        res_page1 = client.get("/api/v1/officials?limit=5&offset=0")
        self.assertEqual(res_page1.status_code, 200)
        self.assertEqual(len(res_page1.json()["officials"]), 5)

        res_page2 = client.get("/api/v1/officials?limit=5&offset=5")
        self.assertEqual(res_page2.status_code, 200)
        self.assertEqual(len(res_page2.json()["officials"]), 5)

        # Distinct officials across pages
        ids_page1 = {o["official_id"] for o in res_page1.json()["officials"]}
        ids_page2 = {o["official_id"] for o in res_page2.json()["officials"]}
        self.assertTrue(ids_page1.isdisjoint(ids_page2))

        # 5. Empty filter state
        res_empty = client.get("/api/v1/officials?search=NonexistentNameXYZ")
        self.assertEqual(res_empty.status_code, 200)
        self.assertEqual(res_empty.json()["total"], 0)
        self.assertEqual(res_empty.json()["officials"], [])

    # =========================================================================
    # 11. ROLE PERMISSIONS & RBAC AUTHORIZATION
    # =========================================================================
    def test_11_role_permissions_rbac(self):
        """Enforces RBAC: public read for geography/officials, strict auth for mutations and admin ops."""
        # Public endpoints accessible without auth token
        res_geo = client.get("/api/v1/geography/divisions")
        self.assertEqual(res_geo.status_code, 200)

        res_officials = client.get("/api/v1/officials")
        self.assertEqual(res_officials.status_code, 200)

        res_map = client.get("/api/v1/parcels/map?limit=10")
        self.assertEqual(res_map.status_code, 200)

        # Citizen cannot access admin user management
        res_unauth_admin = client.get("/api/v1/admin/users", headers=self.cit_headers)
        self.assertIn(res_unauth_admin.status_code, [401, 403])

        # Citizen cannot approve mutations (Officer/Admin only)
        res_unauth_mutate = client.post("/api/v1/mutations/MUT-2026-TEST/action",
                                        json={"action": "APPROVE", "notes": "Unauthorized"},
                                        headers=self.cit_headers)
        self.assertIn(res_unauth_mutate.status_code, [401, 403, 404])

    # =========================================================================
    # 12. REGRESSION TESTS: OCR, HASH, FRAUD DETECTION, AUDIT LOGGING
    # =========================================================================
    def test_12_regression_core_tracks(self):
        """Verifies no regression in previously established P1-P6 core functionality."""
        # 1. Health check
        res_health = client.get("/api/v1/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.json()["status"], "HEALTHY")

        # 2. Cryptographic hash verification (P2)
        res_hash = client.post("/api/v1/documents/verify-integrity", files={"file": ("test_deed.txt", b"Authentic deed bytes sample", "text/plain")})
        self.assertEqual(res_hash.status_code, 200)
        self.assertIn("status_label", res_hash.json())

        # 3. Fraud triage & evaluation (P3)
        res_eval = client.get("/api/v1/verification/evaluate/BD-PAR-000101")
        self.assertEqual(res_eval.status_code, 200)

        res_cases = client.get("/api/v1/verification/cases?limit=5")
        self.assertEqual(res_cases.status_code, 200)

        # 4. Mutation Pre-check workflow (P4)
        res_mut = client.post("/api/v1/mutations/pre-check", json={
            "parcel_id": "BD-PAR-000101",
            "deed_id": "DEED-SAVAR-2024-00101",
            "applicant_id": "USR-CITIZEN-01"
        })
        self.assertEqual(res_mut.status_code, 200)
        self.assertIn("can_proceed", res_mut.json())
        self.assertTrue(res_mut.json()["can_proceed"])

        # 5. Audit logs endpoint (P5/P6)
        res_audit = client.get("/api/v1/officer/audit-logs?limit=5", headers=self.off_headers)
        self.assertEqual(res_audit.status_code, 200)


if __name__ == "__main__":
    unittest.main()
