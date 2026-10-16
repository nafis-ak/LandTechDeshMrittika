# RULEBOOK TRACEABILITY MATRIX
## LandTech 2026 Innovation Hackathon (Rulebook v1.2)
**Project Name:** DESHMRITTIKA / BHUMI-SYNC (দেশমৃত্তিকা)  
**Track:** Digital Land Records, Verification & Digitization  
**Primary Demonstration Focus:** P3 — Catch Fraud & Double-Selling  
**Scope:** Full Multi-Track Implementation (P1 through P6)  
**Document Version:** 1.0.0  
**Last Updated:** October 16, 2026 (Phase 0 Baseline)  

---

## 1. Traceability Methodology & Status Lifecycle

To comply with the LandTech 2026 Rulebook v1.2 and strict software engineering integrity, every feature and requirement is explicitly mapped from the rulebook to its architectural components, tests, and demonstration evidence.

Status markers are defined as follows:
- `PLANNED`: Requirement analyzed, architecture designed, implementation scheduled.
- `IN PROGRESS`: Active implementation and test development underway.
- `IMPLEMENTED`: Code and configuration complete, pending automated test verification.
- `TESTED`: Automated test suite passing with documented execution logs and artifacts.

---

## 2. Problem Track Traceability Matrix (P1 – P6)

| Track | Problem Name (Rulebook v1.2) | Exact Rulebook Requirement | Status | Shared Data Model Entities | Backend Service & API | Frontend Workflow & UI Component | Automated Tests | Demo Evidence & Acceptance Criteria |
|---|---|---|---|---|---|---|---|---|
| **P1** | **Digitize Old Records**<br>*(পুরোনো রেকর্ড ডিজিটাইজেশন)* | *"Turn scanned Khatian, Porcha, and Deed papers (handwritten or printed Bangla) into searchable digital data."*<br><br>*(স্ক্যান করা খতিয়ান, পর্চা ও দলিল (হাতে লেখা বা মুদ্রিত বাংলা) অনুসন্ধানযোগ্য ডিজিটাল ডেটায় রূপান্তর।)* | `PLANNED` | • `documents`<br>• `parcels`<br>• `deeds` | • `OCRService` (`app/services/ocr.py`)<br>• `GET /api/v1/records/search`<br>• `POST /api/v1/documents/parse-khatian` | • Search bar with Khatian/Dag/Mouza filters<br>• Legacy document split-screen viewer (scanned image vs. parsed structured data)<br>• Honest OCR confidence score badge | • `test_ocr_service.py`<br>• `test_bangla_text_extractor.py`<br>• `test_ocr_fallback_handling.py` | • Uploading synthetic historical Khatian extracts structured Dag, Khatian, Owner names.<br>• Unreadable scan honestly outputs `OCR_STATUS = 'FAILED_TO_PARSE'` without mock fabrication. |
| **P2** | **Verify Deeds & Ownership**<br>*(দলিল ও মালিকানা যাচাই)* | *"Make land documents easy to verify (for example with QR codes, digital signatures, or hashing) so fake or changed copies are caught at once."*<br><br>*(কিউআর কোড, ডিজিটাল স্বাক্ষর বা হ্যাশিং দিয়ে ভূমি-দলিল সহজে যাচাইযোগ্য করা, যাতে জাল বা পরিবর্তিত কপি সঙ্গে সঙ্গে ধরা পড়ে।)* | `PLANNED` | • `documents`<br>• `deeds`<br>• `review_logs` | • `HashingService` (`app/services/integrity.py`)<br>• `POST /api/v1/documents/verify-integrity`<br>• `GET /api/v1/deeds/{id}/qr-token` | • Citizen Document Verifier upload card<br>• SHA-256 hash calculator widget<br>• QR code scanner simulator<br>• Tamper Alert modal (Hash Mismatch warning) | • `test_sha256_integrity.py`<br>• `test_tamper_detection.py`<br>• `test_qr_verification.py` | • Uploading original deed outputs `VERIFIED_AUTHENTIC`.<br>• Changing 1 byte in deed file immediately flags `HASH_MISMATCH_TAMPERED`. |
| **P3** *(Primary)* | **Catch Fraud & Double-Selling**<br>*(জালিয়াতি ও একাধিকবার বিক্রি শনাক্তকরণ)* | *"Spot fake documents, the same land sold to more than one buyer, and records that do not match between registration and mutation."*<br><br>*(জাল দলিল, একই জমি একাধিক ক্রেতার কাছে বিক্রি, এবং নিবন্ধন ও নামজারি রেকর্ডের অমিল শনাক্ত করা।)* | `PLANNED` | • `parcels`<br>• `deeds`<br>• `transactions`<br>• `mutation_records`<br>• `verification_cases`<br>• `review_logs` | • `DoubleSellingEngine` (`app/services/verification.py`)<br>• `GET /api/v1/verification/cases`<br>• `POST /api/v1/verification/evaluate/{parcel_id}`<br>• `POST /api/v1/officer/review-decision` | • Officer Risk Triage Queue (High/Medium/Low)<br>• Side-by-side deed comparison card<br>• Interactive Timeline showing conflicting sale dates<br>• Officer Review Action (Escalate, Clear, Flag) | • `test_double_selling_rules.py`<br>• `test_sequential_transfer_clean.py`<br>• `test_unmutated_deed_conflict.py`<br>• `test_area_oversale_math.py` | • Scenario DS-01 (Concurrent unmutated deeds) correctly generates `CRITICAL_RISK` alert.<br>• Scenario DS-02 (Legitimate sequential resale) generates `CLEAR` status.<br>• Reviewer decision logged in audit trail. |
| **P4** | **Smart e-Mutation & Registry**<br>*(স্মার্ট ই-নামজারি ও নিবন্ধন)* | *"Connect deed registration to mutation, with automatic checks and status tracking."*<br><br>*(স্বয়ংক্রিয় যাচাই ও অবস্থা অনুসরণসহ দলিল নিবন্ধনকে নামজারির সঙ্গে যুক্ত করা।)* | `PLANNED` | • `deeds`<br>• `transactions`<br>• `mutation_records`<br>• `parcels` | • `MutationBridgeService` (`app/services/mutation.py`)<br>• `GET /api/v1/mutations/{case_id}/track`<br>• `POST /api/v1/mutations/pre-check`<br>• `POST /api/v1/mutations/link-deed` | • e-Mutation Application Status Tracker (Visual 4-step stepper: Registered -> AC Land Ingestion -> Verification -> Approved)<br>• Sub-Registry to AC Land pre-flight check widget | • `test_mutation_state_machine.py`<br>• `test_registry_to_mutation_link.py`<br>• `test_precheck_validation.py` | • Entering Deed Number auto-populates AC Land mutation draft with pre-checked tax & ownership validation.<br>• Real-time status badge updates on approval. |
| **P5** | **Check Before You Buy**<br>*(কেনার আগে যাচাই)* | *"A citizen tool to check a plot’s owner, mutation history, court cases, and khas or acquisition status before buying."*<br><br>*(জমি কেনার আগে মালিক, নামজারির ইতিহাস, মামলা এবং খাস বা অধিগ্রহণ অবস্থা যাচাইয়ের নাগরিক টুল।)* | `PLANNED` | • `parcels`<br>• `owners`<br>• `parcel_ownership`<br>• `tax_records`<br>• `litigation_records`<br>• `khas_records` | • `DueDiligenceService` (`app/services/due_diligence.py`)<br>• `GET /api/v1/due-diligence/{parcel_id}`<br>• `GET /api/v1/due-diligence/{parcel_id}/pdf` | • Citizen "Check Before You Buy" single-page audit dashboard<br>• 5-Point Safety Checklist (Owner title, Mutation status, Tax arrears, Court cases, Khas status)<br>• Printable PDF Dossier generator | • `test_due_diligence_report.py`<br>• `test_litigation_checker.py`<br>• `test_tax_status_verifier.py` | • Citizen enters Khatian/Dag; receives complete due diligence dossier with color-coded safety indicators and downloadable report. |
| **P6** *(Innovation)* | **Cadastral Boundary Conflict & Khas Land Protection**<br>*(স্মার্ট ক্যাডাস্ট্রাল বাউন্ডারি ও সরকারি খাস/অধিগ্রহণ জমি সুরক্ষা)* | *"Any other idea that fits the track, if the organizers accept it in Round 1."*<br><br>*(ট্র্যাকের সঙ্গে মানানসই অন্য যেকোনো আইডিয়া, প্রথম রাউন্ডে আয়োজকদের গ্রহণ সাপেক্ষে।)* | `PLANNED` | • `parcels`<br>• `khas_records`<br>• `acquisition_zones` | • `CadastralSpatialService` (`app/services/spatial.py`)<br>• `GET /api/v1/spatial/parcels-geojson`<br>• `POST /api/v1/spatial/check-encroachment` | • Interactive Leaflet Cadastral Map<br>• Toggleable layers: Private plots, Government Khas (1-No Khatian), Highway acquisition corridor<br>• Spatial overlap warning banner | • `test_spatial_intersection.py`<br>• `test_khas_encroachment_alert.py`<br>• `test_geojson_validity.py` | • Plot boundary intersecting a gazetted highway project or government water body immediately triggers `GOVERNMENT_ENCROACHMENT_ALERT`. |

---

## 3. Shared Relational Dataset Integration Strategy

Rather than generating disconnected synthetic databases for each problem track, a **single unified relational dataset** interconnects all 6 tracks. This ensures data consistency across the entire prototype:

```
                      +-------------------+
                      |      owners       |
                      +---------+---------+
                                | 1
                                |
                                | M
                      +---------v---------+
                      | parcel_ownership  |
                      +---------+---------+
                                | M
                                |
                                | 1
+--------------------+ 1      +---+---------------+      1 +--------------------+
|    khas_records    +-------->      parcels      <--------+ acquisition_zones  |
|      (P5, P6)      |        +---+---------------+        |      (P5, P6)      |
+--------------------+            |       |                +--------------------+
                                  | 1     | 1
                                  |       |
                                  | M     | M
                       +----------v--+  +-v------------------+
                       | tax_records |  | litigation_records |
                       |    (P5)     |  |        (P5)        |
                       +-------------+  +--------------------+
                                  |
                                  | 1
                                  |
                                  | M
                       +----------v----------+
                       |        deeds        | (P2, P3, P4)
                       +----+-----------+----+
                            | 1         | 1
                            |           |
                            | M         | M
                 +----------v---+     +-v--------------------+
                 | transactions |     |      documents       | (P1, P2)
                 +----+---------+     | - SHA-256 Hash       |
                      | 1             | - OCR Text & Status  |
                      |               +----------------------+
                      | 1
           +----------v----------+
           |  mutation_records   | (P4, P3)
           +----------+----------+
                      | 1
                      |
                      | M
           +----------v----------+
           | verification_cases  | (P3 Core Engine)
           +----------+----------+
                      | 1
                      |
                      | M
           +----------v----------+
           |     review_logs     | (P3 Audit Trail)
           +---------------------+
```

### Synergy Across the Shared Schema:
1. **P1 (Digitization):** Scanned historical papers populate `documents` with OCR text, linking back to legacy survey khatians in `parcels`.
2. **P2 (Verification):** Cryptographic SHA-256 and QR tokens are stored on `documents` and validated against `deeds`.
3. **P3 (Fraud & Double-Selling):** Evaluates `deeds`, `transactions`, `mutation_records`, and `parcel_ownership` to detect concurrent sales of the same plot.
4. **P4 (Smart e-Mutation):** Reads `deeds` and automatically spawns structured `mutation_records` with automated pre-checks.
5. **P5 (Check Before You Buy):** Queries `parcels`, `owners`, `tax_records`, `litigation_records`, and `khas_records` to construct the unified due diligence report.
6. **P6 (Cadastral Spatial Guard):** Reads GeoJSON coordinates from `parcels` and calculates intersections with `khas_records` and `acquisition_zones`.

---

## 4. Phase 0 Audit & Baseline Deliverables

| Deliverable | Location | Status | Evidence / Verification |
|---|---|---|---|
| **Workspace Confirmation** | `/Users/macbookair/Desktop/LandTechDeshMrittika` | `IMPLEMENTED` | Inspected via `list_dir`, verified empty baseline. |
| **Rulebook Ingestion** | `docs/landtech_hackathon_rulebook.pdf` | `IMPLEMENTED` | Copied locally, text extracted via `pdfminer`, verbatim P1–P6 validated. |
| **Project Blueprint (v2.0.0)** | `docs/PROJECT_BLUEPRINT.md` | `IMPLEMENTED` | Updated with full P1–P6 architecture and status markers. |
| **Blueprint Phase 0 Backup** | `docs/PROJECT_BLUEPRINT_v0.1.0_phase0_backup.md` | `IMPLEMENTED` | Preserved prior to v2.0.0 update. |
| **Rulebook Traceability Matrix** | `docs/RULEBOOK_TRACEABILITY_MATRIX.md` | `IMPLEMENTED` | Full mapping table with statuses and acceptance criteria. |
| **Initial Risk Register** | `docs/PROJECT_BLUEPRINT.md#section-6` | `IMPLEMENTED` | Covers privacy, legal disclaimers, OCR fallbacks, cadastral boundaries. |

---

## 5. Next Steps for Phase 1

Upon user approval of this Traceability Matrix and the updated Project Blueprint, Phase 1 will execute:
1. **`docs/research/SOURCE_REGISTER.md`** and **`data/source_register.csv`** (Official Bangladesh & International sources).
2. **`docs/research/REFERENCE_DATA_FINDINGS.md`** (Survey taxonomy, Khatian layouts, Deed registration laws).
3. **`docs/architecture/ERD.md`** & **`docs/data/DATA_DICTIONARY.md`** (Complete entity field definitions for all 14 tables).
4. **Synthetic Data Generation Plan** (Seed configuration, scenario allocations for P1–P6).
