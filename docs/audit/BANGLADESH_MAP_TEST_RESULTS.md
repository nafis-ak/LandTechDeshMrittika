# BHUMI-SYNC — Bangladesh Interactive Map & Geography Test Results

**Document ID:** `AUDIT-TEST-MAP-2026-BD`  
**Date:** 2026-10-17  
**Platform Version:** DeshMrittika / BHUMI-SYNC v2.3  
**Test Suite:** `tests/test_geography_and_officials.py`  
**Execution Environment:** Python 3.13 / FastAPI TestClient / SQLite 3 / macOS  
**Result:** ALL 12 TESTS PASSED (100% SUCCESS RATE)  

---

## 1. Test Execution Summary

The newly developed automated test suite `tests/test_geography_and_officials.py` executes 12 rigorous integration scenarios verifying administrative hierarchy integrity, GeoJSON compliance, spatial viewport bounding-box performance, synthetic official safety rules, RBAC enforcement, and regression protection.

```
Ran 12 tests in 0.625s

OK
```

---

## 2. Test Verification Matrix

| # | Test Scenario | Method / Assertions | Result | Details |
|---|---|---|---|---|
| **1** | **Administrative Hierarchy & Cascading Filters** | `test_01_administrative_hierarchy_cascading` | **PASSED** | Validated Division (8) → District (64) → Upazila (501) → Union (24) → Mouza (15) parent-child relationships with stable IDs. |
| **2** | **Duplicate Mouza Names in Different Areas** | `test_02_duplicate_mouza_names_handling` | **PASSED** | Verified that identical names (e.g. *Mirzapur* in Gazipur vs *Mirzapur* in Tangail) maintain distinct primary keys (`MOU-XXXX-XX`) and valid parent upazila foreign keys. |
| **3** | **Nationwide Administrative Coverage Counts** | `test_03_nationwide_coverage_counts` | **PASSED** | Exactly 8 divisions verified with BBS geocodes; exactly 64 districts verified; 501 upazilas verified. |
| **4** | **Missing or Incomplete Coverage Handling** | `test_04_missing_or_incomplete_coverage_handling` | **PASSED** | Areas without digital mouza vectors return `coverage_status: "INCOMPLETE_OFFICIAL_DATA"` with empty array (200 OK) without fabricating synthetic geometry. |
| **5** | **GeoJSON RFC 7946 Validity & EPSG:4326 CRS** | `test_05_geojson_validity_and_crs` | **PASSED** | Validated coordinates format (`[longitude, latitude]`) within Bangladesh geographic extent (`lon [88.0, 93.0]`, `lat [20.0, 27.0]`). |
| **6** | **Spatial Viewport Bounding-Box Queries** | `test_06_parcels_spatial_bbox_queries` | **PASSED** | Verified bbox filtering (`centroid_lon`, `centroid_lat`), empty bbox handling, and malformed query parameter resilience. |
| **7** | **Parcel Location & Due Diligence Linkage** | `test_07_parcel_location_and_due_diligence` | **PASSED** | Verified `/api/v1/parcels/{id}/location` centroid calculation, boundary polygon return, public due diligence summary, and 404 for missing IDs. |
| **8** | **Synthetic Official Profiles Safeguards** | `test_08_synthetic_official_safeguards` | **PASSED** | 100% of emails end with `@demo.land.gov.bd`; 100% of phone numbers contain `(ডেমো)`; 100% of profiles have `DEMO OFFICIAL` provenance; all portraits are SVG vectors. |
| **9** | **Official-to-Office Jurisdiction Relationships** | `test_09_official_jurisdiction_relationships` | **PASSED** | All 17 officials verified against valid office foreign keys, division, district, and upazila revenue jurisdictions. |
| **10** | **Directory Search, Multi-Field Filters & Pagination** | `test_10_directory_search_and_filters` | **PASSED** | Tested designation filters (`AC_LAND`, `KANUNGO`, etc.), division filters, text search, pagination offset/limit, and empty result handling. |
| **11** | **Role Permissions & RBAC Enforcement** | `test_11_role_permissions_rbac` | **PASSED** | Public geography and directory accessible without authentication; unauthorized admin and mutation approval endpoints strictly return 401/403. |
| **12** | **Core Tracks Regression Verification** | `test_12_regression_core_tracks` | **PASSED** | Validated health endpoint, cryptographic integrity verification (P2), double-selling evaluation (P3), mutation pre-check (P4), and audit logging (P5/P6). |

---

## 3. Spatial Performance & Indexing Benchmark

### 3.1 Problem Statement & Solution
Loading 100,000 polygon geometries into Leaflet at once consumes hundreds of megabytes of memory and locks browser rendering. To ensure instantaneous, flicker-free rendering:
1. Two indexed floating-point columns were added to the `parcels` table: `centroid_lat REAL` and `centroid_lon REAL`.
2. Composite spatial index created: `idx_parcels_spatial ON parcels (centroid_lon, centroid_lat)`.
3. Bounding-box queries are filtered directly in SQL:
   ```sql
   SELECT parcel_id, mouza, jl_number, dag_number, khatian_number,
          area_decimal, is_disputed, coordinates_geojson, centroid_lat, centroid_lon
   FROM parcels
   WHERE coordinates_geojson IS NOT NULL
     AND centroid_lon BETWEEN ? AND ?
     AND centroid_lat BETWEEN ? AND ?
   LIMIT ?
   ```

### 3.2 Benchmark Results
- **Centroid Extraction & Index Creation**: 100,000 rows indexed in **0.53 seconds**.
- **Spatial Bounding-Box Query Time**: **0.13 milliseconds** for 50 parcels.
- **API Response Time**: Sub-15ms for `/api/v1/parcels/map?bbox=...` with full GeoJSON serialization.

---

## 4. Active Spatial Layers Summary

| Layer Name | Type | Count / Extent | Styling | Interactive Popup Content |
|---|---|---|---|---|
| **Synthetic Cadastral Parcels** | GeoJSON Viewport | Dynamic (100–150 per view, out of 100,000 total) | Green `#059669` (Regular), Red `#dc2626` (Disputed) | Dag number, Khatian number, Mouza, Area, Dispute alert, link to Citizen Dossier |
| **Gazetted Infrastructure Corridors** | GeoJSON Polygon | 5 national corridors | Purple `#9333ea`, dashed outline, 35% opacity | Project name, Gazette notification number, buffer area notification |
| **Government 1-No. Khas Land** | GeoJSON Polygon | 150 sample parcels in Savar | Amber `#d97706`, 55% fill opacity | Khas ID, Category, Managing authority, non-transferability warning |
| **Land Administration Offices** | Leaflet DivIcon Marker | 14 administrative offices across 8 divisions | Blue circular icon `🏛️` with white outline | Office name, address, contact, button to view assigned officials |

---

## 5. Database Integrity & Protection Verification

Before migrations, a full verifiable backup was performed:
- **Backup Location**: `data/backups/landtech_synthetic_backup_20261017_181841.db` (110MB)
- **PRAGMA integrity_check**: `ok`
- **Foreign Key Violations**: `0`
- **Existing Dataset Preserved**:
  - Parcels: 100,000
  - Owners: 20,000
  - Registered Deeds: 58,333
  - Verification Cases: 19,750
  - Seeded Double-Selling Scenarios: 500

---

## 6. Known Limitations & Next Steps

1. **Digital Cadastral Vector Coverage**: Currently, digitized vector parcel polygons exist for the Savar pilot zone (Aminbazar and Birulia mouzas). For other upazilas and mouzas, the system accurately displays administrative centroids, office locations, and infrastructure corridors.
2. **Authoritative Survey Ingestion**: When the Ministry of Land and DLRS complete digitized cadastral surveys (EDLMS / BRS) for additional upazilas, new polygon shapefiles can be ingested into the normalized `parcels` and `geo_mouzas` tables using the established migration script without schema modifications.
