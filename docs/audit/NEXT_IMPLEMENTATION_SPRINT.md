# BHUMI-SYNC — Next Implementation Sprint: Prioritized Technical Enhancements

**Date:** October 17, 2026  
**Workspace:** `/Users/macbookair/Desktop/LandTechDeshMrittika`  
**Current Baseline:** BHUMI-SYNC v2.2 (Commit `6dac69b` on `main`)  
**Sprint Focus:** Highest-Impact Core Track Enhancements Without Architectural Rewrites  

---

## 1. Executive Summary & Top Five Identified Gaps

The independent audit of Tracks P1 through P6 confirmed that the core product foundations are genuinely implemented and working with real data:
- Tesseract v5.5.2 Bengali OCR (P1) is operational on real PNG, JPEG, and PDF documents.
- Binary SHA-256 integrity verification (P2) detects 1-byte modifications.
- Double-selling fraud engine (P3) achieves 100% precision and recall across 500 seeded scenarios and 500 clean controls.
- E-mutation workflow (P4) persists citizen applications and enforces IDOR protection.
- 5-point buyer safety dossier (P5) filters private data and generates clean risk ratings.
- 100,000 cadastral parcels possess valid WGS84 GeoJSON polygons (P6).

However, the audit revealed **five specific architectural and functional gaps** where features are currently simulated, mocked, or missing key integrations:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TOP FIVE PRODUCT GAPS                                  │
├────┬───────┬──────────────────────────────────────────┬──────────────┬────────────────┤
│ #  │ Track │ Gap Description                          │ Impact Level │ Current Status │
├────┼───────┼──────────────────────────────────────────┼──────────────┼────────────────┤
│ 1  │ P6    │ Mocked Spatial Acquisition Intersection  │ HIGH         │ SIMULATED      │
│ 2  │ P6    │ Static Frontend GIS Corridor Overlay     │ MEDIUM       │ HARDCODED UI   │
│ 3  │ P5    │ Multi-Parcel Side-by-Side Comparison     │ MEDIUM       │ SEQUENTIAL ONLY│
│ 4  │ P4    │ AC Land Application Return for Correction│ HIGH         │ MISSING ACTION │
│ 5  │ P1    │ Ground-Truth OCR Accuracy Benchmark      │ LOW          │ UNQUANTIFIED   │
└────┴───────┴──────────────────────────────────────────┴──────────────┴────────────────┘
```

---

## 2. Detailed Gap Specifications & Sprint Backlog

### Sprint Item 1 (CRITICAL — Track P6): True Server-Side Spatial Acquisition Intersection
- **Problem Statement:**  
  In `backend/app/services/due_diligence.py` (line 77), `is_acquisition` is hardcoded to `False`. The database table `acquisition_zones` contains 5 gazetted corridors with GeoJSON polygons (e.g., Dhaka-Aricha Highway 8-Lane Expansion), but no spatial point-in-polygon or bounding-box intersection test is evaluated against the parcel's `coordinates_geojson`.
- **Target Implementation:**  
  Implement a lightweight Ray-Casting algorithm or Shapely polygon-intersection evaluator in `backend/app/services/verification.py`. If a parcel's centroid or bounding polygon intersects an active acquisition corridor in `acquisition_zones`:
  1. Set `is_acquisition_corridor = True`.
  2. Emit finding `P6-ACQUISITION` (Severity: `CRITICAL`, Risk Score: 85).
  3. Mark Point 5 of the Safety Checklist as `FAILED` (`"জাতীয় মহাসড়ক/অবকাঠামো অধিগ্রহণ জোনের অন্তর্ভুক্ত"`).
- **Dependencies:** None (uses existing `acquisition_zones` table).
- **Acceptance Criteria:**
  - A parcel whose coordinates fall within `[90.315, 23.79] - [90.32, 23.83]` returns `is_acquisition_corridor: true` and `safety_rating: "CRITICAL_BLOCKED"`.
  - Parcels outside all 5 zones remain `is_acquisition_corridor: false`.

---

### Sprint Item 2 (Track P6): Dynamic Cadastral & Acquisition GeoJSON API
- **Problem Statement:**  
  In `frontend/js/app.js` (lines 1766–1775), the Highway Acquisition Corridor is rendered as a static Leaflet polyline with 3 hardcoded coordinates instead of dynamically querying the gazetted zones.
- **Target Implementation:**  
  1. Add endpoint `GET /api/v1/parcels/layers/acquisition-zones` returning a GeoJSON `FeatureCollection` of all 5 gazetted zones from `acquisition_zones`.
  2. Add endpoint `GET /api/v1/parcels/layers/khas-polygons` returning GeoJSON of gazetted Khas land parcels.
  3. Update `initCadastralGISWorkspace` in `frontend/js/app.js` to fetch and render these GeoJSON layers dynamically.
- **Dependencies:** Item 1.
- **Acceptance Criteria:**
  - Toggling `#layer-corridor-toggle` renders all 5 gazetted zones fetched from the backend API.
  - Clicking any zone displays project name, gazette notification number, and acquisition status in Leaflet popup.

---

### Sprint Item 3 (Track P5): Multi-Parcel Comparative Risk Dossier API
- **Problem Statement:**  
  The Buyer workspace provides a "পৌরসভা ও মৌজা তুলনা" tab, but buyers cannot submit 2 or 3 parcel IDs simultaneously to generate a side-by-side comparative table.
- **Target Implementation:**  
  1. Add endpoint `POST /api/v1/buyer/compare` accepting `{"parcel_ids": ["BD-PAR-000101", "BD-PAR-001001"]}` (up to 3 parcels).
  2. Returns a structured comparison matrix: Dag, Mouza, Area, Owner count, Safety Rating, Double-Selling Flag, Tax Clearance, and Khas Status.
  3. Wire frontend `#buyer-compare-reports` tab to call this endpoint and render a responsive comparison card grid.
- **Dependencies:** `DueDiligenceService`.
- **Acceptance Criteria:**
  - Submitting 2 parcel IDs returns `HTTP 200` with both dossiers aligned in a comparative JSON schema.
  - Submitting >3 parcels returns `HTTP 400 Bad Request`.

---

### Sprint Item 4 (Track P4): AC Land "Return for Correction" & Summons Action
- **Problem Statement:**  
  Citizens can submit mutation applications, and AC Land officers can view assigned applications and schedule hearings. However, the AC Land officer has no direct endpoint to return an application to the citizen with correction notes (e.g., "খতিয়ানের মূল কপি অস্পষ্ট, পুনরায় আপলোড করুন").
- **Target Implementation:**  
  1. Add endpoint `POST /api/v1/officer/applications/{app_id}/action` with actions:
     - `RETURN_FOR_CORRECTION`: Sets status to `RETURNED_FOR_CORRECTION`, records officer notes, and pushes an actionable alert into `citizen_notifications`.
     - `APPROVE_SIMULATED`: Sets status to `APPROVED`, generates simulated mutated khatian, and updates transaction ledger.
  2. Add action buttons in `#page-officer-assigned` UI.
- **Dependencies:** `backend/app/api/officer.py`, `citizen_applications` table.
- **Acceptance Criteria:**
  - Officer returning an application updates `citizen_applications.status = 'RETURNED_FOR_CORRECTION'`.
  - Citizen viewing `/api/v1/citizen/my-applications/{app_id}` sees the officer's correction notes.

---

### Sprint Item 5 (Track P1): Ground-Truth OCR Accuracy Evaluation Harness
- **Problem Statement:**  
  While Tesseract OCR is verified to run dynamically and output real text, the project lacks an automated benchmark measuring exact Character Error Rate (CER) and Token Accuracy against ground truth.
- **Target Implementation:**  
  1. Create `data/benchmarks/ocr_ground_truth.json` containing ground-truth text for `sample_deed_authentic.png` and `sample_porcha.png`.
  2. Implement benchmark runner `tests/test_ocr_benchmark.py` computing Levenshtein-based CER and word accuracy.
- **Dependencies:** `DocumentOCRService`.
- **Acceptance Criteria:**
  - Automated test asserts Bengali OCR character accuracy >= 80% on standard scanned deed samples.

---

## 3. Sprint Execution Sequence & Estimated Effort

```
┌────────────────────────────────────────────────────────────────────────┐
│                       SPRINT IMPLEMENTATION ORDER                      │
│                                                                        │
│  Phase 1: Spatial Intersections (P6)                                   │
│  ├── [Sprint Item 1] Spatial Acquisition Intersection in Backend (3h)  │
│  └── [Sprint Item 2] Dynamic GIS Layers GeoJSON Endpoint & UI (2h)     │
│                                                                        │
│  Phase 2: Workflow & Comparison (P4 & P5)                              │
│  ├── [Sprint Item 4] AC Land Application Return & Correction API (2h)  │
│  └── [Sprint Item 3] Multi-Parcel Comparative Risk Dossier (2h)        │
│                                                                        │
│  Phase 3: Benchmarks (P1)                                              │
│  └── [Sprint Item 5] Ground-Truth OCR Accuracy Test Harness (1h)       │
└────────────────────────────────────────────────────────────────────────┘
```

**Total Estimated Implementation:** 10 Engineering Hours.  
**Guiding Principle:** Zero changes to the underlying 100,000-parcel database schema or seeded fraud scenarios. All enhancements build strictly upon existing services and REST endpoints.
