# BHUMI-SYNC — Comprehensive P1–P6 Core Tracks Technical Audit Report

**Date of Audit:** October 17, 2026  
**Workspace:** `/Users/macbookair/Desktop/LandTechDeshMrittika`  
**Git Baseline:** Commit `6dac69b` on branch `main`  
**Auditor:** Application Security Architect & Independent QA Lead  
**Operating System:** macOS (Darwin 24.3.0 arm64)  
**Database File:** `data/generated/full_scale/landtech_synthetic.db` (115,277,824 bytes / 109.93 MB)  

---

## 1. Project & Dataset Preservation Baseline

Before conducting any track-level inspection or test executions, project state and dataset integrity were verified without resetting or modifying user files:

- **Git Status:** Clean working tree on `main` (commit `6dac69b4f80244ba113b18742763e11cf57320e0`).
- **Database Status:** Active full-scale SQLite database in WAL mode (`landtech_synthetic.db`).
- **Integrity Verification:**
  - `PRAGMA integrity_check;` returned `ok`.
  - `PRAGMA foreign_key_check;` returned 0 violations.
- **Authoritative Record Inventory:**
  - `parcels`: **100,000** records (100% intact)
  - `owners`: **20,000** synthetic profiles (100% intact)
  - `deeds`: **58,333** registered deed records (100% intact)
  - `transactions`: **58,333** transactional link records (100% intact)
  - `parcel_ownership`: **128,500** active/historical ownership share records (100% intact)
  - `mutation_records`: **57,583** records (100% intact)
  - `tax_records`: **100,000** records (100% intact)
  - `litigation_records`: **1,500** civil injunction records (100% intact)
  - `khas_records`: **1,500** government 1-No. Khas records (100% intact)
  - `acquisition_zones`: **5** gazetted national project corridors (100% intact)
  - `verification_cases`: **19,750** total triage cases:
    - `DS-01` (CRITICAL): **500** seeded double-selling fraud scenarios (`SCN-DS1-0001` to `SCN-DS1-0500`)
    - `DS-02` (LOW): **15,000** negative control clean sequential resales
    - `DS-03` (HIGH): **250** area discrepancy/rapid resale cases
    - `DS-05` (MEDIUM): **2,500** land tax arrears cases
    - `P6-ENCROACH` (CRITICAL): **1,500** Khas land encroachment cases

---

## 2. Track-by-Track Detailed Technical Audit

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          TRACK IMPLEMENTATION STATUS SUMMARY                           │
├────┬──────────────────────────────────────┬──────────────────────────────┬─────────────┤
│ Tr │ Domain Description                   │ Implementation Classification│ Verif. Code │
├────┼──────────────────────────────────────┼──────────────────────────────┼─────────────┤
│ P1 │ Document Digitization & Bengali OCR  │ IMPLEMENTED AND VERIFIED     │ 200 OK      │
│ P2 │ Cryptographic Document Integrity     │ IMPLEMENTED AND VERIFIED     │ 200 OK      │
│ P3 │ Double-Selling & Fraud Detection     │ IMPLEMENTED AND VERIFIED     │ 200 OK      │
│ P4 │ E-Mutation & Registry Workflow       │ IMPLEMENTED (LOCAL SIM)      │ 200 OK      │
│ P5 │ Buyer Due Diligence & 5-Point Check  │ IMPLEMENTED AND VERIFIED     │ 200 OK      │
│ P6 │ Cadastral GIS & Khas Protection      │ PARTIALLY IMPLEMENTED        │ 200 OK / ⚠️ │
└────┴──────────────────────────────────────┴──────────────────────────────┴─────────────┘
```

---

### Track P1: Document Digitization & Bengali OCR

**Classification:** `IMPLEMENTED AND VERIFIED`  
**Primary Files:**
- Backend Service: `backend/app/services/ocr.py` (294 lines)
- API Endpoint: `backend/app/api/documents.py` (`POST /api/v1/documents/upload-ocr`)
- Frontend Handler: `frontend/js/app.js` (`executeAdvancedOCR`, lines 1630–1722)
- Unit & Pipeline Tests: `tests/test_ocr_advanced.py`, `tests/test_tracks_audit.py`

#### Observed Evidence & Execution Results:
1. **Engine & Dependencies:** Real optical character recognition is powered by local Tesseract OCR v5.5.2 with active language packs `['ben', 'eng', 'osd', 'snum']`.
2. **File Ingestion & Validation:** Accepts PNG, JPEG, TIFF, and PDF. Enforces 15 MB payload ceiling (`MAX_FILE_SIZE`). Empty file upload correctly returns `HTTP 400 Bad Request` (`detail: "Uploaded file is empty."`). Unsupported extensions (`.exe`) return `{ "success": false, "ocr_status": "UNSUPPORTED_FILE_TYPE" }`.
3. **Multi-Page PDF Rasterization:** Uses `pymupdf` (PyMuPDF) to render PDF pages into 250 DPI RGB buffers. Tested on `sample_khatian.pdf` (5.76 MB), successfully rasterizing and extracting page text.
4. **Image Preprocessing:** Implements three selectable enhancement pipelines:
   - `enhance_contrast`: Grayscale conversion, `ImageOps.autocontrast(cutoff=2)`, and 1.8x contrast multiplier.
   - `binarize`: Adaptive thresholding at pixel intensity 140.
   - `rotate_deg`: 90°, 180°, and 270° orientation correction.
5. **Real Bengali OCR Execution (Not Hardcoded):**
   - Executed on `sample_deed_authentic.png` (171 KB):
     - Status: `SUCCESS`
     - Confidence Score: `84.1%` (Level: `HIGH`)
     - Characters Extracted: `1,231` characters
     - Processing Time: `3,674.4 ms`
     - Extracted Text Preview: `গণপ্রজাতন্ত্রী বাংলাদশে সরকার — ১০০ টাকার নন-জুডশিয়াল স্ট্যাম্প...`
     - Output exhibits genuine Tesseract ligature noise (`বাংলাদশে` for `বাংলাদেশ`, `রফকলি` for `রফিকুল`), confirming dynamic OCR generation rather than static demo strings.
6. **Structured Legal Entity Extraction:** Regex parser extracts:
   - Deed Type: `সাফ-কবালা (Deed of Outright Sale)`
   - Deed Number: `৮৪৫২/২০২৪`
   - Dag Numbers: `৫১২`, `১০৪`
   - Khatian Numbers: `১৪৫`, `৩২৮`
   - Mouza & J.L.: `আমিনবাজার (JL: ২৬)`
   - Land Area & Class: `১২.৫০ শতাংশ (নাল)`
   - Seller & Buyer: `মণা: রফকলি ইসলাম` / `ACPA: জমল খাতুন`
7. **Frontend Capabilities:** Editable output textarea (`#ocr-output-textarea`), copy-to-clipboard, text download (`extracted_land_record_ocr.txt`), and cross-reference button that redirects to cadastral search for the extracted Dag.

#### Technical Limitations & Honesty Statement:
- **Ground-Truth Benchmark:** No pre-annotated Bangladesh Land Registry ground-truth corpus exists in the repository for formal Character Error Rate (CER) or Word Error Rate (WER) scoring.
- **Complex Ligatures:** 19th and early 20th century cursive Bengali deeds with physical degradation will require deep-learning based fine-tuning (e.g., TrOCR/Donut) for production legal usage.

---

### Track P2: Document Cryptographic Integrity Verification

**Classification:** `IMPLEMENTED AND VERIFIED`  
**Primary Files:**
- Backend Service: `backend/app/services/integrity.py` (45 lines)
- API Endpoint: `backend/app/api/documents.py` (`POST /api/v1/documents/verify-integrity`)
- Database Table: `documents` (51 registered document hashes)
- Frontend Handler: `frontend/js/app.js` (`handleHashFileSelection`, lines 1390–1488)
- Unit & Pipeline Tests: `tests/test_backend.py` (test_09), `tests/test_tracks_audit.py`

#### Observed Evidence & Execution Results:
1. **Binary SHA-256 Computation:** Server computes `hashlib.sha256(file_bytes).hexdigest()` directly from raw multipart uploaded bytes.
2. **Authentic File Verification:**
   - Input: `DOC-000001_SAVAR-20261018-00003.png` (26,145 bytes)
   - Calculated Hash: `3f84ba4813c96b86a1f9ce347258468ff7fe1b00598d24f610713faec38e4399`
   - Database Match: Matched against `documents.sha256_hash`
   - API Response (`HTTP 200`):
     ```json
     {
       "is_authentic": true,
       "matched_document_id": "DOC-000001",
       "parcel_id": "BD-PAR-000003",
       "deed_id": "DEED-000001",
       "document_type": "DEED_COPY",
       "status_label": "VERIFIED_AUTHENTIC",
       "provenance_label": "SYNTHETIC_DEMO_DOCUMENT"
     }
     ```
3. **One-Byte Tamper Detection Test:**
   - Modified the last byte of `DOC-000001` (`file_bytes[-1] ^= 0x01`).
   - Calculated Hash: `3b780c8b343fbc9fe112cb0651db285c6bea4ba600c0d9e7307167d0cbfe5984` (avalanche effect).
   - API Response (`HTTP 200`):
     ```json
     {
       "is_authentic": false,
       "matched_document_id": null,
       "parcel_id": null,
       "deed_id": null,
       "document_type": null,
       "status_label": "TAMPER_DETECTED_OR_UNREGISTERED",
       "provenance_label": "UNKNOWN_OR_MODIFIED_DOCUMENT"
     }
     ```
4. **Client-Side Verification:** Frontend uses WebCrypto `crypto.subtle.digest('SHA-256', arrayBuffer)` to display client-computed hash in real-time before sending to backend.
5. **Legal Disclaimer:** `frontend/index.html` line 834 explicitly clarifies:
   > "হ্যাশিং মূল দলিলের অপরিবর্তনযোগ্যতা (Tamper-Evidence) প্রমাণ করে। এটি মালিকানা সত্ত্ব সরাসরি প্রদান করে না, বরং পূর্বে নিবন্ধিত মূল দলিলের প্রতিটি বাইট অবিকৃত রয়েছে কিনা তা প্রমাণ করে।"

---

### Track P3: Double-Selling & Fraud Detection

**Classification:** `IMPLEMENTED AND VERIFIED`  
**Primary Files:**
- Backend Engine: `backend/app/services/verification.py` (182 lines, `DoubleSellingEngine`)
- API Endpoints: `backend/app/api/verification.py`, `backend/app/api/officer.py`
- Scenario Catalog: `data/scenarios/scenario_catalog.csv` (500 distinct scenarios)
- Database Tables: `verification_cases`, `deeds`, `mutation_records`, `review_logs`
- Unit & Pipeline Tests: `tests/test_backend.py` (test_05, test_07), `tests/test_tracks_audit.py`

#### Observed Evidence & Execution Results:
1. **Rule Engine Architecture:** Implements deterministic detection:
   - `DS-01`: Concurrent unmutated transfers by the same seller on the same parcel.
   - `DS-02`: Clean sequential conveyances where prior deeds have approved mutations.
   - `DS-03`: Area over-sale discrepancy (deed declared area > parcel surveyed area).
   - `DS-05`: Outstanding land development tax arrears.
   - `P6-ENCROACH`: Overlap with gazetted government Khas land.
   - `P5-LITIGATION`: Active civil court injunction stay.
2. **500 Seeded Fraud Scenarios Evaluation:**
   - Catalog: `data/scenarios/scenario_catalog.csv` contains 500 distinct rows (`SCN-DS1-0001` through `SCN-DS1-0500`) with unique parcel references (`BD-PAR-000101` to `BD-PAR-000600`).
   - Executed `DoubleSellingEngine.evaluate_parcel` on all 500 positive cases:
     - **True Positives (TP): 500**
     - **False Negatives (FN): 0**
     - **Recall: 100.00%**
3. **500 Negative Control Cases (Clean Sequential Transfers):**
   - Evaluated 500 parcels with finding code `DS-02`:
     - **True Negatives (TN): 500**
     - **False Positives (FP): 0**
     - **Precision: 100.00%**
     - **F1 Score: 100.00%**
4. **Officer Triage Queue & Attributable Review Decisions:**
   - Endpoint `GET /api/v1/officer/queue` returns pending fraud cases ordered by risk score (descending).
   - Endpoint `POST /api/v1/officer/decision` requires case ID, allowed action (`APPROVED_LEGITIMATE`, `REJECTED_FRAUD_FLAG`, `REQUESTED_PHYSICAL_INSPECTION`), and institutional reason.
   - Generates attributable `log_id` (`LOG-XXXXXX`), inserts into `review_logs` with reviewer user ID (`OFFICER-SAVAR-01`), action, reason, and ISO timestamp, and updates case status in SQLite.

---

### Track P4: E-Mutation & Registry Workflow

**Classification:** `IMPLEMENTED AND VERIFIED (LOCAL SIMULATION)`  
**Primary Files:**
- Backend Services: `backend/app/services/mutation.py` (96 lines), `backend/app/api/citizen.py` (253 lines)
- API Endpoints: `POST /api/v1/citizen/applications`, `GET /api/v1/citizen/my-applications`, `POST /api/v1/mutations/pre-check`, `POST /api/v1/mutations/{id}/status`, `POST /api/v1/officer/hearing-schedule`
- Database Tables: `citizen_applications`, `citizen_notifications`, `mutation_records`, `transactions`
- Unit & Pipeline Tests: `tests/test_auth_security.py` (test_17, test_22), `tests/test_tracks_audit.py`

#### Observed Evidence & Execution Results:
1. **Full Application Lifecycle:**
   - Citizen submits mutation request: `POST /api/v1/citizen/applications` with parcel ID, service type (`নামজারি ও জমাভাগ`), and metadata.
   - Record created in `citizen_applications` (`status: "SUBMITTED"`). Confirmation notification inserted in `citizen_notifications`.
   - Citizen reviews application status via `GET /api/v1/citizen/my-applications/{app_id}`.
   - AC Land officer queries pending mutation applications via `GET /api/v1/officer/assigned-applications`.
   - AC Land schedules hearing: `POST /api/v1/officer/hearing-schedule` records hearing date and summons notes.
   - Mutation approval pipeline (`POST /api/v1/mutations/{id}/status`) transitions mutation to `APPROVED`, assigns new synthetic mutated khatian number, and updates `transactions.mutation_link_status = 'MUTATED'`.
2. **Automated Pre-Check Engine:**
   - `MutationBridgeService.run_pre_check` evaluates four conditions:
     - Khas land: Blocks mutation if parcel is government property.
     - Tax arrears: Blocks mutation if holding has unpaid dues.
     - Civil stay: Blocks mutation if active court injunction exists.
     - Competing unmutated deed: Blocks mutation if prior conveyance is unmutated.
3. **IDOR Ownership Verification:**
   - Tested: Citizen A attempts to fetch Citizen B's application `APP-MUT-2026-0015` via `GET /api/v1/citizen/my-applications/APP-MUT-2026-0015`.
   - Server strictly returns `HTTP 403 Forbidden` (`detail: "অননুমোদিত প্রবেশাধিকার: আপনি অন্য নাগরিকের ব্যক্তিগত আবেদন পর্যালোচনা করতে পারবেন না।"`).

#### Technical Limitations & Honesty Statement:
- **Zero Real Government Registry Link:** BHUMI-SYNC does NOT interface with Bangladesh's live government mutation API (`mutation.land.gov.bd`) or the Directorate of Registration.
- **Decision Status:** All mutation actions, hearings, and approvals are purely local database transactions designed for hackathon demonstration.

---

### Track P5: Buyer Due Diligence

**Classification:** `IMPLEMENTED AND VERIFIED`  
**Primary Files:**
- Backend Service: `backend/app/services/due_diligence.py` (142 lines), `backend/app/services/search.py`
- API Endpoints: `GET /api/v1/search`, `GET /api/v1/due-diligence/{parcel_id}`, `POST /api/v1/buyer/review-requests`
- Database Tables: `parcels`, `deeds`, `tax_records`, `litigation_records`, `khas_records`, `buyer_review_requests`
- Unit & Pipeline Tests: `tests/test_backend.py` (test_03, test_06), `tests/test_tracks_audit.py`

#### Observed Evidence & Execution Results:
1. **Multi-Attribute Search:**
   - By `parcel_id`: Exact lookup (`BD-PAR-000101` -> 1 match).
   - By `dag`: Exact plot match (`dag=101` -> 20 matches across 20 khatians/mouzas).
   - By `mouza`: Case-insensitive text search (`mouza=Aminbazar` -> 50,000 matches).
2. **5-Point Safety Dossier:**
   - Point 1: Ownership Chain & ROR Shares (`unmutated_count == 0`).
   - Point 2: Double-Selling & Registry Integrity (`DS-01` check).
   - Point 3: Land Development Tax Clearance (`tax_records.payment_status == 'PAID'`).
   - Point 4: Civil Litigation & Injunctions (`litigation_records.status == 'ACTIVE_INJUNCTION_STAY'`).
   - Point 5: Government Khas & Acquisition Clearance (`khas_records` match).
   - Safety Ratings: Evaluated as `SAFE`, `CAUTION`, `HIGH_RISK`, or `CRITICAL_BLOCKED`.
3. **Privacy & Redaction Safeguards:**
   - Raw National ID hashes (`synthetic_nid_hash`), personal phone numbers, and internal officer investigation notes are completely stripped from the buyer dossier payload.
4. **Buyer Review Request Submission:**
   - Buyers can submit formal investigation requests to the AC Land office (`POST /api/v1/buyer/review-requests`). Persisted in `buyer_review_requests` table.
5. **Print & Export:**
   - Web application features responsive print styles (`window.print()`), enabling instant generation of a clean PDF due diligence dossier.

---

### Track P6: Cadastral GIS & Khas-Land Protection

**Classification:** `PARTIALLY IMPLEMENTED`  
**Primary Files:**
- Backend Endpoint: `backend/app/api/parcels.py` (`GET /api/v1/parcels/{parcel_id}/geojson`)
- Database Tables: `parcels` (`coordinates_geojson`), `khas_records` (1,500 rows), `acquisition_zones` (5 rows)
- Frontend GIS Canvas: `frontend/js/app.js` (`initCadastralGISWorkspace`, lines 1740–1803)
- Unit & Pipeline Tests: `tests/test_backend.py` (test_04), `tests/test_tracks_audit.py`

#### Observed Evidence:
1. **Cadastral Geometry Data:**
   - All 100,000 parcels in `parcels` table possess valid GeoJSON Polygon geometries.
   - Coordinate Reference System: Standard WGS84 (EPSG:4326) with longitudes (90.2° to 90.4° E) and latitudes (23.7° to 23.9° N) centered on Savar Upazila, Dhaka.
   - API endpoint `GET /api/v1/parcels/{id}/geojson` returns compliant GeoJSON Feature with provenance tag `"SYNTHETIC_CADASTRAL_VISUALIZATION"`.
2. **Interactive Map Display:**
   - Frontend initializes Leaflet.js canvas with OpenStreetMap base layer.
   - Interactive layer toggles for Highway Acquisition Corridor and Government Khas Polygons.
   - Quick navigation by Dag (`101`, `205`) repositions viewport.
3. **Khas Protection Integration:**
   - 1,500 parcels in `khas_records` are linked to Collectorate of Dhaka (`COLLECTOR_DHAKA`).
   - Any due diligence check on a Khas parcel immediately triggers `CRITICAL_BLOCKED` safety rating with legal prohibition warning.

#### Incomplete / Simulated Gaps (Why "Partially Implemented"):
1. **Mocked Acquisition Intersection (`backend/app/services/due_diligence.py` line 77):**
   ```python
   # 6. Acquisition check (check if within coordinates)
   # Mocking check for demo
   is_acquisition = False
   ```
   Dynamic polygon intersection between parcel boundaries and the 5 gazetted acquisition zones in `acquisition_zones` is **NOT** computed server-side using spatial operators (e.g., Shapely). It is currently hardcoded to `False`.
2. **Static Frontend Overlay:**
   The Dhaka-Aricha Highway corridor in `frontend/js/app.js` is drawn as a hardcoded static Leaflet polyline rather than loaded dynamically from `acquisition_zones.corridor_geojson`.
3. **Survey Accuracy Disclaimer:**
   The boundaries are synthetic rectangular/trapezoidal bounding boxes and must never be represented as gazetted cadastral survey records.

---

## 3. Role-Based Access Control (RBAC) Verification

Tested against `docs/ROLE_PERMISSION_MATRIX.md` via automated unit and live API suites:

| Role | Tested Route | HTTP Status | Verdict | Explanation |
| :--- | :--- | :---: | :---: | :--- |
| **Citizen** | `GET /api/v1/citizen/my-parcels` | `200 OK` | PASS | Can view own linked parcels. |
| **Citizen** | `GET /api/v1/officer/queue` | `403 Forbidden` | PASS | Blocked from officer triage queue. |
| **Citizen** | `GET /api/v1/admin/users` | `403 Forbidden` | PASS | Blocked from admin console. |
| **Citizen A**| `GET /api/v1/citizen/my-applications/{B_ID}` | `403 Forbidden` | PASS | Blocked from viewing Citizen B's application (IDOR). |
| **Buyer** | `GET /api/v1/due-diligence/BD-PAR-000101` | `200 OK` | PASS | Can view sanitized 5-point dossier. |
| **Buyer** | `GET /api/v1/officer/queue` | `403 Forbidden` | PASS | Blocked from officer triage queue. |
| **Buyer** | `GET /api/v1/admin/users` | `403 Forbidden` | PASS | Blocked from admin user management. |
| **AC Land** | `GET /api/v1/officer/queue` | `200 OK` | PASS | Can view assigned fraud queue. |
| **AC Land** | `POST /api/v1/officer/decision` | `200 OK` | PASS | Can record attributable decision with reason. |
| **AC Land** | `GET /api/v1/admin/users` | `403 Forbidden` | PASS | Blocked from user account management. |
| **Admin** | `GET /api/v1/admin/users` | `200 OK` | PASS | Can manage user accounts and roles. |
| **Admin** | `POST /api/v1/officer/decision` | `403 Forbidden` | PASS | **Separation of Duties:** Admin cannot approve officer decisions. |

---

## 4. Summary of Top Technical Gaps & Limitations

1. **Gap 1 (Track P6 — Spatial Intersections):** The backend does not compute true geometric polygon intersections between parcel boundaries and the 5 gazetted acquisition zones. It relies on a mocked flag in `due_diligence.py`.
2. **Gap 2 (Track P4 — External e-Mutation Gateways):** The workflow is entirely internal and simulated. There is no connectivity to live government portals (`mutation.land.gov.bd`).
3. **Gap 3 (Track P1 — Ground-Truth OCR Corpus):** Bengali OCR accuracy is functional on clear sample scans (84.1% confidence), but lacks an annotated ground-truth benchmark to measure exact Word/Character Error Rates.
4. **Gap 4 (Track P5 — Multi-Parcel Batch Comparison):** While individual dossiers are complete, comparing multiple parcels side-by-side in the Buyer workspace currently relies on sequential single-parcel lookups.
5. **Gap 5 (Track P6 — Dynamic GeoJSON Layer Ingestion):** The GIS map uses hardcoded coordinates for corridor overlays rather than fetching GeoJSON from `/api/v1/` spatial endpoints.

---

## 5. Verification Commands

```bash
# Run core tracks audit test suite (15 tests):
python3 -m unittest tests/test_tracks_audit.py

# Run comprehensive regression suite (66 tests):
python3 -m unittest discover -s tests -p "test_*.py"

# Inspect database row counts:
python3 -c "import sqlite3; conn=sqlite3.connect('data/generated/full_scale/landtech_synthetic.db'); cur=conn.cursor(); print([(t[0], cur.execute(f'SELECT COUNT(*) FROM {t[0]}').fetchone()[0]) for t in cur.execute(\"SELECT name FROM sqlite_master WHERE type='table';\").fetchall()])"
```
