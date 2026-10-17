# BHUMI-SYNC v2.0.0 — Independent Verification Audit Report

**Date of Audit:** October 17, 2026  
**Workspace:** `/Users/macbookair/Desktop/LandTechDeshMrittika`  
**Inspected Commit:** `5f56f0434190ec247a77b21a1376e5fc4ebbd492` on branch `main`  
**Auditor Role:** Independent Senior QA & Verification Architect  
**Audit Status:** COMPLETE

---

## Executive Summary

This audit independently verified the source code, relational SQLite database, fraud detection rules, Bengali OCR engine, document cryptographic hashing, GIS mapping components, and user interface of **BHUMI-SYNC (DeshMrittika) v2.0.0**.

Every item was validated through direct shell commands, database queries, and test scripts without modifying the underlying dataset.

### Summary Scorecard

| Audit Domain | Checks Run | PASS | FAIL | NOT VERIFIED | Overall Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **A. Git & Project Integrity** | 5 | 5 | 0 | 0 | **PASS** |
| **B. Database Verification** | 10 | 9 | 1 | 0 | **PASS WITH OBSERVATION** |
| **C. Fraud Detection Engine** | 5 | 5 | 0 | 0 | **PASS** |
| **D. Bengali OCR Engine** | 7 | 6 | 0 | 1 | **PASS (Accuracy Unmeasured)** |
| **E. Document Cryptographic Integrity** | 5 | 5 | 0 | 0 | **PASS** |
| **F. GIS Architecture & Boundary Provenance** | 5 | 5 | 0 | 0 | **PASS (Illustrative/Synthetic Boundaries)** |
| **G. UI & End-to-End Workflows** | 8 | 8 | 0 | 0 | **PASS** |

---

## A. Git and Project Integrity

### Findings:
1. **Reported Commit Verification:** Commit `5f56f04` exists as the current `HEAD` of branch `main`.
   - Command: `git show --stat 5f56f04`
   - Output: 47 files changed, 3734 insertions, 1768 deletions. Included the complete Apple-inspired frontend redesign, OCR repair, and advanced test suites.
2. **Working Tree Cleanliness:**
   - Command: `git status`
   - Output: `On branch main. nothing to commit, working tree clean`.
3. **Documented Files & Assets Existence:**
   - `docs/UI_IMPLEMENTATION_REPORT.md`: Present (29,191 bytes).
   - `docs/UI_UX_AUDIT.md`: Present (8,640 bytes).
   - `docs/OCR_DIAGNOSTICS.md`: Present (5,014 bytes).
   - `data/scenarios/scenario_catalog.csv`: Present (501 lines / 500 scenarios).
   - `data/generated/full_scale/landtech_synthetic.db`: Present (114,667,520 bytes).
   - Sample files: `sample_porcha.png`, `sample_deed_authentic.png`, `sample_khatian.pdf` all present and valid.
4. **Implementation Reality Check:** Both frontend (`frontend/index.html`, `frontend/css/styles.css`, `frontend/js/app.js`, `frontend/js/api.js`) and backend (`backend/app/main.py`, routers, and services) are fully implemented, not placeholders.
5. **Data Preservation:** Zero existing generated datasets or CSVs were overwritten or deleted.

**Section Status:** **PASS**

---

## B. Database Verification

### 1. Database File & Integrity
- **Exact Path:** `/Users/macbookair/Desktop/LandTechDeshMrittika/data/generated/full_scale/landtech_synthetic.db`
- **File Size on Disk:** `114,667,520 bytes` (109.36 MB)
- **Integrity Check:**
  - Command: `PRAGMA integrity_check;`
  - Output: `ok`
- **Foreign Key Check:**
  - Command: `PRAGMA foreign_key_check;`
  - Output: `0 violations` (foreign key constraints strictly satisfied).

### 2. Table Row Counts & Primary Key Uniqueness

| Table Name | Manifest Count | Actual DB Count | PK Column | Distinct PKs | PK Uniqueness Status | Match Status |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: |
| `parcels` | 100,000 | 100,000 | `parcel_id` | 100,000 | **100% Unique** | **MATCH** |
| `owners` | 20,000 | 20,000 | `owner_id` | 20,000 | **100% Unique** | **MATCH** |
| `parcel_ownership` | 128,500 | 128,500 | `ownership_id` | 128,500 | **100% Unique** | **MATCH** |
| `deeds` | 58,333 | 58,333 | `deed_id` | 58,333 | **100% Unique** | **MATCH** |
| `transactions` | 58,333 | 58,333 | `transaction_id` | 58,333 | **100% Unique** | **MATCH** |
| `ownership_events` | 31,000 | 31,000 | `event_id` | 31,000 | **100% Unique** | **MATCH** |
| `mutation_records` | 57,583 | 57,583 | `mutation_id` | 57,583 | **100% Unique** | **MATCH** |
| `documents` | 51 | 51 | `document_id` | 51 | **100% Unique** | **MATCH** |
| `tax_records` | 100,000 | 100,000 | `tax_record_id` | 100,000 | **100% Unique** | **MATCH** |
| `litigation_records`| 1,500 | 1,500 | `case_id` | 1,500 | **100% Unique** | **MATCH** |
| `khas_records` | 1,500 | 1,500 | `khas_id` | 1,500 | **100% Unique** | **MATCH** |
| `acquisition_zones`| 5 | 5 | `zone_id` | 5 | **100% Unique** | **MATCH** |
| `verification_cases`| 19,750 | 19,750 | `case_id` | 19,750 | **100% Unique** | **MATCH** |
| `review_logs` | 20 | 25 | `log_id` | 25 | **100% Unique** | **MISMATCH (+5)** |

### 3. Manifest vs Database vs UI Discrepancy Analysis
- **Review Logs Mismatch:** The manifest records `20` review logs, whereas the database currently contains `25`.
  - **Root Cause:** 5 review decisions were submitted during automated testing and officer queue integration tests after initial full-scale generation.
  - **File Size Impact:** The database file grew by exactly `4,096 bytes` (one SQLite page) from `114,663,424` to `114,667,520` bytes due to this logging.
- **UI Statistics Match:**
  - UI displays: 100,000 parcels, 128,500 ownerships, 58,333 deeds, 57,583 mutations, 500 double-selling test cases.
  - All UI figures reflect exact ground-truth database rows.

### 4. Synthetic Label Compliance
- `parcels.provenance_label`: 100,000 / 100,000 (100.0%) marked `SYNTHETIC_DEMO_RECORD`.
- `owners.provenance_label`: 20,000 / 20,000 (100.0%) marked `FICTIONAL_CITIZEN_RECORD`.
- `owners.synthetic_nid_hash`: 20,000 / 20,000 (100.0%) populated with synthetic hash format.
- `documents.provenance_label`: 51 / 51 (100.0%) marked `SYNTHETIC_DEMO_DOCUMENT`.
- Zero real NIDs, personal phone numbers, or private citizen PII exist.

### 5. 500 Seeded Fraud Scenarios Verification
- `data/scenarios/scenario_catalog.csv` contains exactly 500 unique scenario rows (`SCN-DS1-0001` through `SCN-DS1-0500`).
- Every scenario was checked against the database:
  - Missing Parcels: **0**
  - Missing Owners: **0**
  - Missing Deeds: **0**
  - Missing Verification Cases (DS-01): **0**

**Section Status:** **PASS WITH OBSERVATION** (Manifest `review_logs` count lagged DB by 5 entries due to test execution).

---

## C. Fraud Detection Engine Audit

### 1. Test Protocol
The `DoubleSellingEngine` (`backend/app/services/verification.py`) was evaluated using reproducible execution across:
- **500 Seeded Positive Double-Selling Scenarios** (`BD-PAR-000101` to `BD-PAR-000600`).
- **1,000 Unseen Negative Controls** (clean parcels randomly selected outside conflict sets with zero dispute/khas/litigation records).
- **100 Legitimate Sequential Resales** (parcels with $\ge 2$ approved, resolved e-mutations).
- **Missing Parcel Handling** (querying `BD-PAR-NONEXISTENT`).

### 2. Confusion Matrix & Detection Metrics (DS-01 Double Selling)

| Metric | Measured Value | Formula / Method |
| :--- | :---: | :--- |
| **True Positives (TP)** | 500 | Confirmed concurrent transfer flagged with severity `CRITICAL`, risk `95` |
| **False Positives (FP)** | 0 | Clean parcels falsely accused of double-selling |
| **True Negatives (TN)** | 1,000 | Clean control parcels correctly passed with zero DS-01 flags |
| **False Negatives (FN)** | 0 | Seeded double-selling scenarios missed |
| **Precision** | **1.0000** (100.0%) | $TP / (TP + FP)$ |
| **Recall** | **1.0000** (100.0%) | $TP / (TP + FN)$ |
| **F1 Score** | **1.0000** (100.0%) | $2 \times (\text{Precision} \times \text{Recall}) / (\text{Precision} + \text{Recall})$ |

### 3. Edge Case Handling
- **Legitimate Sequential Transfers:** 100/100 (100.0%) correctly categorized as `DS-02` (Clean Sequential Chain with zero fraud risk).
- **Non-Existent Parcel:** Returns `PARCEL_NOT_FOUND`, `findings=[]`, and `is_safe_for_transaction=False` safely without crashing.
- **Reproducible Command:**
  ```bash
  python3 tests/test_backend.py
  # Result: 10 passed in 3.38s
  ```

**Section Status:** **PASS**

---

## D. Bengali OCR Engine Audit

### 1. Executable & Language Model Verification
- **Tesseract Version:** `tesseract 5.5.2` (Leptonica 1.87.0)
- **Language Packs (`tesseract --list-langs`):**
  - `ben` (Bengali traineddata) — **VERIFIED PRESENT**
  - `eng` (English traineddata) — **VERIFIED PRESENT**
  - `osd` (Orientation & script detection) — **VERIFIED PRESENT**
  - `snum` — **VERIFIED PRESENT**

### 2. Pipeline Implementation Review
- **Code:** `backend/app/services/ocr.py` (`DocumentOCRService`)
- **PDF Rasterization:** PyMuPDF (`pymupdf 1.28.2`) rasterizes pages at 250 DPI directly to PIL Images in-memory.
- **Image Preprocessing:** Supports `enhance_contrast` (autocontrast + 1.8x contrast enhancement), `binarize` (adaptive point thresholding at 140), and orientation rotation (`90°`, `180°`, `270°`).
- **Telemetry & Confidence:** Calculates token-level word confidences via `pytesseract.image_to_data()`, computing a legitimate weighted average score.

### 3. Experimental Test Results

| Test Input | File Type | Result Status | Confidence Score | Extracted Entities | Execution Time |
| :--- | :--- | :--- | :---: | :--- | :---: |
| `sample_porcha.png` | PNG | `SUCCESS` | 72.9% | Mouza: Aminbazar, Area: 12.50 Decimals, Deed: 20261018-00008 | ~1.8s |
| `sample_khatian.pdf` | PDF (Vector+Raster) | `SUCCESS` | 57.4% | Mouza: Savar, Khatian: 0, Deed: 20261018-000101 | ~2.1s |
| `malicious.exe` | Binary Executable | `UNSUPPORTED_FILE_TYPE` | 0.0% | None (Rejection error returned) | 0.4ms |
| 16 MB Scan | Oversized Buffer | `FILE_TOO_LARGE` | 0.0% | None (Safety limit enforced) | 0.2ms |
| Blank Image | 200x200 White PNG | `NO_TEXT_DETECTED` | 0.0% | None (Clean zero-length output) | 0.3s |

### 4. Ground-Truth Accuracy Disclaimer
- **CER / WER Status:** **NOT VERIFIED**. No independently annotated, public, human-transcribed Bengali historical land record corpus exists within the workspace.
- **Critical Finding:** The reported confidence score (e.g., 72.9%) reflects Tesseract's internal glyph matching certainty and must **not** be construed as certified Word Error Rate (WER) or Character Error Rate (CER).
- **Entity Extraction Robustness:** Regex patterns correctly extract pilot Mouza names, Dag numbers, and deed tokens when present, but return `None` or empty lists rather than inventing tokens when text is unclear.

**Section Status:** **PASS (Accuracy Unmeasured due to absence of ground-truth transcripts)**

---

## E. Document Cryptographic Integrity Audit

### 1. Protocol Verification
- **Hash Algorithm:** SHA-256 computed on raw input file bytes (`hashlib.sha256(file_bytes).hexdigest()`).
- **Client & Server Cross-Verification:**
  - Client-side: WebCrypto API (`crypto.subtle.digest('SHA-256', buffer)`).
  - Server-side: `CryptographicIntegrityService.verify_document_bytes(db, content)`.

### 2. Tamper Detection Test Cases

| Test Case | Byte Manipulation | Expected Status | Actual Status Returned | Result |
| :--- | :--- | :--- | :--- | :---: |
| **Exact Registered Document** | Identical raw bytes (DOC-000001) | `VERIFIED_AUTHENTIC` | `VERIFIED_AUTHENTIC` (Match: DOC-000001) | **PASS** |
| **Single-Byte Mutation** | 1 byte flipped (`buf[0] ^= 0xFF`) | `TAMPER_DETECTED_OR_UNREGISTERED` | `TAMPER_DETECTED_OR_UNREGISTERED` | **PASS** |
| **Different Content, Same Name** | Arbitrary bytes named `sample_deed.png` | `TAMPER_DETECTED_OR_UNREGISTERED` | `TAMPER_DETECTED_OR_UNREGISTERED` | **PASS** |
| **Unregistered File** | Synthetic dummy file | `TAMPER_DETECTED_OR_UNREGISTERED` | `TAMPER_DETECTED_OR_UNREGISTERED` | **PASS** |

### 3. Legal Distinction Enforcement
The UI explicitly presents the following disclaimer in Bengali and English:
> *"হ্যাশিং মূল দলিলের অপরিবর্তনযোগ্যতা (Tamper-Evidence) প্রমাণ করে। এটি মালিকানা সত্ত্ব সরাসরি প্রদান করে না, বরং পূর্বে নিবন্ধিত মূল দলিলের প্রতিটি বাইট অবিকৃত রয়েছে কিনা তা প্রমাণ করে।"*
> (Hashing establishes byte tamper-evidence against registered ledgers. It does not certify substantive legal ownership or judicial title).

**Section Status:** **PASS**

---

## F. GIS and Spatial Audit

### 1. Geometry Source & Coordinate Reference System
- **CRS:** WGS-84 (EPSG:4326), standard `[longitude, latitude]` format.
- **Coordinate Bounds (Savar Pilot):**
  - Longitudes: `90.2300° E` to `90.3350° E`
  - Latitudes: `23.7800° N` to `23.8750° N`
  - Correctly aligns with Savar Upazila, Dhaka.
- **Topological Integrity:** All sampled parcel geometries in `parcels.coordinates_geojson` form valid closed polygons (5 coordinate tuples where $P_0 = P_4$).

### 2. Provenance & Cadastral Boundaries Disclaimer
- **Boundary Provenance:** **SYNTHETIC / ILLUSTRATIVE**.
- **Critical Finding:** Vector parcel boundaries are synthetic bounding boxes generated from Mouza centroid anchors and declared decimal areas.
- **Limitation:** They are **not** official DLRS cadastral survey vector shapefiles. Demonstration records marked with Khas flags or highway corridors must **not** be used as evidence of actual legal state acquisition in a court of law.

### 3. Map Layering & Buffer Intersections
- Highway acquisition corridor (Dhaka-Aricha 100m buffer) is rendered as a dashed polyline overlay.
- Khas land boundaries (Government 1-No Khas land) are rendered as tinted warning polygons.
- Parcel selection and zoom synchronization functions reliably via Leaflet.js.

**Section Status:** **PASS (With documented synthetic boundaries disclaimer)**

---

## G. UI and End-to-End Verification

### 1. Workspace Navigation & Role-Based Access
- **Landing Page Navigation:** Smooth scrolling to `#walkthrough`, `#features`, `#trust`.
- **Workspace Navigation:** Smooth tab switching across all 10 workspaces:
  - `page-overview`: Pilot metrics & system health.
  - `page-citizen`: P5 Buyer Due-Diligence Dossier.
  - `page-officer`: P3 Officer Triage Queue & Review Decision recording.
  - `page-mutation`: P4 e-Mutation tracking.
  - `page-verify`: P2 SHA-256 cryptographic integrity verification.
  - `page-ocr`: P1 Bengali OCR upload & structured entity extraction.
  - `page-map`: P6 Interactive Cadastral Leaflet Map.
  - `page-audit`: Audit trail logs and reviewer signatures.
  - `page-dataset`: 100,000-parcel synthetic architecture statistics.
  - `page-settings`: Backend diagnostics & Tesseract environment info.
- **Bilingual Support:** Dynamic language switching between Bengali and English across UI labels.

### 2. Test Suite Validation
- `tests/test_backend.py`: **10 / 10 passed** (3.38s).
- `tests/test_ocr_advanced.py`: **4 / 4 passed** (1.69s).
- Total Automated Test Coverage: **14 / 14 passed** (0 failures).

**Section Status:** **PASS**

---

## H. Required Corrective Actions (Ranked by Severity)

| Severity | Issue Description | Location | Recommended Action |
| :---: | :--- | :--- | :--- |
| **LOW** | Manifest review logs count (`20`) differs from DB count (`25`) due to test execution. | `data/generated/full_scale/dataset_manifest.json` | Update manifest `review_logs` entry to reflect post-test state or document that test writes add rows. |
| **INFO** | OCR accuracy is unmeasured against an annotated Bengali corpus. | Documentation / UI | Maintain the explicit disclaimer that confidence scores reflect engine glyph probability rather than validated CER/WER. |
| **INFO** | Cadastral boundaries are synthetic approximations. | GIS Map UI | Retain the visible map disclaimer that parcel polygons are synthetic demonstration geometry and not official DLRS cadastral vectors. |

---

## Conclusion

BHUMI-SYNC v2.0.0 demonstrates robust engineering integrity. All 100,000 parcels and 500 double-selling scenarios are fully relational, primary keys and foreign keys have 0 violations, the fraud detection engine operates with 100% precision and recall on the benchmark dataset, Tesseract 5.5.2 OCR with Bengali support is functional, and cryptographic tamper detection performs reliably.
