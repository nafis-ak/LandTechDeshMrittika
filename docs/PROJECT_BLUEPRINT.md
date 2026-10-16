# DESHMRITTIKA / BHUMI-SYNC
## Master Project Blueprint & Multi-Track Architecture (P1–P6)
**Tagline:** Your Land, Our Responsibility (আপনার জমি, আমাদের দায়িত্ব)  
**Hackathon Track:** Digital Land Records, Verification & Digitization  
**Primary Demonstration Problem:** P3 — Catch Fraud & Double-Selling  
**Supported Rulebook Tracks:** Full Suite P1, P2, P3, P4, P5, P6  
**Target Event:** LandTech 2026 — LandTech Innovation Hackathon (Daffodil International University)  
**Document Version:** 2.0.0 (Phase 0 Scope Expansion)  
**Date:** October 16, 2026  
**Status:** `PHASE_0_COMPLETED` | Architecture: `IN_REVIEW`  

---

## 1. Executive Summary & Mission

Land disputes in Bangladesh constitute over 70% of ongoing civil litigation, predominantly originating from:
1. Double-selling (the same seller executing deeds to multiple unsuspecting buyers before mutation).
2. Fragmented record silos between Sub-Registry Offices (Ministry of Law) and AC Land / Union Land Offices (Ministry of Land).
3. Forged historical deeds, conflicting legacy survey khatians (CS, SA, RS, BS/City), and mutation delays.
4. Encroachment upon government khas land, water bodies, and gazetted infrastructure corridors.

**DESHMRITTIKA / BHUMI-SYNC** is a synthetic-data-powered, multi-track land-record verification and due-diligence platform designed for smart e-governance in Bangladesh. It bridges Sub-Registry deeds and AC Land mutation workflows, validates document cryptographic integrity, extracts legacy records, protects public lands, and generates an explainable "Check Before You Buy" due diligence dossier.

> **Crucial Ethical & Legal Premise:**  
> The platform acts as an explainable risk-triage engine for citizens and administrative officers. It **never** claims to determine legal ownership conclusively, declare individuals guilty of fraud, or bypass statutory judicial and land administration authority.

---

## 2. Rulebook Track Alignment (LandTech 2026 Rulebook v1.2, Section 5)

The project addresses **all six problem tracks** specified in the official LandTech 2026 Rulebook v1.2, maintaining **P3 (Catch Fraud & Double-Selling)** as our primary showcase scenario:

| Track Code | Rulebook Title (English) | Rulebook Title (বাংলা) | Exact Rulebook Definition | Project Implementation Role |
|---|---|---|---|---|
| **P1** | **Digitize Old Records** | **পুরোনো রেকর্ড ডিজিটাইজেশন** | *"Turn scanned Khatian, Porcha, and Deed papers (handwritten or printed Bangla) into searchable digital data."*<br>*(স্ক্যান করা খতিয়ান, পর্চা ও দলিল (হাতে লেখা বা মুদ্রিত বাংলা) অনুসন্ধানযোগ্য ডিজিটাল ডেটায় রূপান্তর।)* | **P1 Service:** OCR & legacy document parser indexing historical CS/SA/RS/BS khatians and deeds into structured fields with honest confidence indicators. |
| **P2** | **Verify Deeds & Ownership** | **দলিল ও মালিকানা যাচাই** | *"Make land documents easy to verify (for example with QR codes, digital signatures, or hashing) so fake or changed copies are caught at once."*<br>*(কিউআর কোড, ডিজিটাল স্বাক্ষর বা হ্যাশিং দিয়ে ভূমি-দলিল সহজে যাচাইযোগ্য করা, যাতে জাল বা পরিবর্তিত কপি সঙ্গে সঙ্গে ধরা পড়ে।)* | **P2 Service:** SHA-256 cryptographic hashing, verifiable QR token generation, and document integrity tamper-detection engine. |
| **P3** *(Primary)* | **Catch Fraud & Double-Selling** | **জালিয়াতি ও একাধিকবার বিক্রি শনাক্তকরণ** | *"Spot fake documents, the same land sold to more than one buyer, and records that do not match between registration and mutation."*<br>*(জাল দলিল, একই জমি একাধিক ক্রেতার কাছে বিক্রি, এবং নিবন্ধন ও নামজারি রেকর্ডের অমিল শনাক্ত করা।)* | **P3 Core Engine:** Multi-rule double-selling detector, timeline overlap analyzer, unmutated transfer conflict flags, and officer triage review queue. |
| **P4** | **Smart e-Mutation & Registry** | **স্মার্ট ই-নামজারি ও নিবন্ধন** | *"Connect deed registration to mutation, with automatic checks and status tracking."*<br>*(স্বয়ংক্রিয় যাচাই ও অবস্থা অনুসরণসহ দলিল নিবন্ধনকে নামজারির সঙ্গে যুক্ত করা।)* | **P4 Workflow:** End-to-end bridge linking Sub-Registry deed submission to AC Land e-mutation with automated pre-checks and live status tracking. |
| **P5** | **Check Before You Buy** | **কেনার আগে যাচাই** | *"A citizen tool to check a plot’s owner, mutation history, court cases, and khas or acquisition status before buying."*<br>*(জমি কেনার আগে মালিক, নামজারির ইতিহাস, মামলা এবং খাস বা অধিগ্রহণ অবস্থা যাচাইয়ের নাগরিক টুল।)* | **P5 Citizen Portal:** 1-click "Check Before You Buy" buyer due-diligence report synthesizing ownership chains, tax status, and encumbrances into a downloadable dossier. |
| **P6** *(Innovation)* | **Cadastral Boundary Conflict & Khas Land Protection** | **স্মার্ট ক্যাডাস্ট্রাল বাউন্ডারি ও সরকারি খাস/অধিগ্রহণ জমি সুরক্ষা** | *"Any other idea that fits the track, if the organizers accept it in Round 1."*<br>*(ট্র্যাকের সঙ্গে মানানসই অন্য যেকোনো আইডিয়া, প্রথম রাউন্ডে আয়োজকদের গ্রহণ সাপেক্ষে।)* | **P6 Spatial Engine:** Geospatial cadastral engine overlaying parcel boundaries against 1-No Khas land and gazetted acquisition corridors to prevent encroachment. |

### Differentiated Rationale for P6 Innovation
* **The Problem It Solves:** Even when deeds and mutations appear legally consistent on paper, buyers and government entities frequently suffer from *spatial boundary overlap* or *fraudulent sale of government Khas land* (খাস জমি) and water bodies.
* **How It Complements P1–P5:**
  - P1 extracts text; P2 verifies paper hashes; P3 checks private double-selling; P4 bridges administrative workflows; P5 gives the citizen report.
  - **P6 introduces the spatial intelligence dimension:** it checks whether the parcel geometry intersects with protected state assets (DLRS/DC Office), resolving the cadastral blind spot.

---

## 3. High-Level Multi-Track System Architecture

```
+-----------------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER                                         |
|                                                                                               |
|   +---------------------------------------------+   +-------------------------------------+   |
|   |         Citizen & Buyer Portal              |   |       Officer & Auditor Portal      |   |
|   |  - P5: "Check Before You Buy" Dossier       |   |  - P3: Double-Selling Triage Queue  |   |
|   |  - P1: Searchable Historical Records        |   |  - P4: e-Mutation Approval Pipeline |   |
|   |  - P2: QR / SHA-256 Document Verification   |   |  - P6: Khas & Cadastral Encroachment|   |
|   |  - P6: Leaflet Cadastral Map & Spatial Alert|   |  - Officer Review Logs & Audit Trail|   |
|   |  - Bilingual UI: বাংলা (Primary) / English   |   |  - Role Guard: Sub-Registrar/AC Land|   |
|   +---------------------------------------------+   +-------------------------------------+   |
+------------------------------------------------^----------------------------------------------+
                                                 | RESTful HTTP / JSON / GeoJSON
+------------------------------------------------v----------------------------------------------+
|                                    APPLICATION BACKEND LAYER                                  |
|                                (FastAPI / Python 3.13 / Pydantic)                             |
|                                                                                               |
|  +---------------------------+  +---------------------------+  +---------------------------+  |
|  |     P1 Service Layer      |  |     P2 Service Layer      |  |   P3 Core Fraud Engine    |  |
|  | - Bangla/English OCR      |  | - SHA-256 Checksum Guard  |  | - Concurrent Deed Detector|  |
|  | - Multi-Khatian Parser    |  | - QR Verification Signer  |  | - Overlapping Sales Engine|  |
|  | - Record Indexer          |  | - Hash Tamper Alerts      |  | - Risk Scoring (0-100)    |  |
|  +---------------------------+  +---------------------------+  +---------------------------+  |
|                                                                                               |
|  +---------------------------+  +---------------------------+  +---------------------------+  |
|  |     P4 Workflow Engine    |  |     P5 Due Diligence API  |  |    P6 Spatial Engine      |  |
|  | - Registry-Mutation Link  |  | - Unified Risk Dossier    |  | - GeoJSON Boundary Math   |  |
|  | - Auto Mutation Pre-Check |  | - Tax & Litigation Status |  | - Khas Land Intersection  |  |
|  | - Status Lifecycle Machine|  | - Printable Buyer PDF     |  | - Acquisition Corridor Det|  |
|  +---------------------------+  +---------------------------+  +---------------------------+  |
+------------------------------------------------^----------------------------------------------+
                                                 | SQLAlchemy ORM
+------------------------------------------------v----------------------------------------------+
|                           UNIFIED RELATIONAL PERSISTENCE LAYER                                |
|                                (SQLite / WAL Mode Engine)                                     |
|                                                                                               |
|  [parcels]               [owners]              [parcel_ownership]        [deeds]              |
|  [transactions]          [ownership_events]    [mutation_records]        [documents]          |
|  [tax_records]           [litigation_records]  [khas_records]            [acquisition_zones]  |
|  [verification_cases]    [review_logs]         [synthetic_manifests]                          |
+-----------------------------------------------------------------------------------------------+
```

---

## 4. Unified Relational Data Model (Single Shared Dataset)

Instead of six disconnected silos, **one unified relational schema** powers all six tracks simultaneously:

```
[owners] <---+ (1:N)
             |
             +---- [parcel_ownership] (M:N Temporal)
             |             ^
             v             |
         [deeds] -------- [parcels] <------- [khas_records] (P6)
            |              |     ^
            v              |     +---------- [acquisition_zones] (P6)
      [transactions]       |     |
            |              |     +---------- [litigation_records] (P5)
            v              |     |
   [mutation_records]      |     +---------- [tax_records] (P5)
         (P4)              |
            +--------------+---------------- [documents] (P1, P2)
                           |
                           +---------------- [verification_cases] (P3)
                           |                         |
                           |                         v
                           +---------------- [review_logs] (P3 Audit)
```

### Entity Schema Roles Across P1–P6:
1. **`parcels`**: Core cadastral plot (`parcel_id`, `district`, `upazila`, `mouza`, `dag_number`, `khatian_number`, `survey_type` [CS/SA/RS/BS], `area_decimal`, `coordinates_geojson`, `is_disputed`, `provenance_label`). *(Powers P1, P3, P4, P5, P6)*.
2. **`owners`**: Synthetic fictional landowners (`owner_id`, `fictional_name`, `synthetic_nid_hash`, `contact_masked`, `provenance_label`). *(Powers P3, P4, P5)*.
3. **`parcel_ownership`**: Temporal ownership ledger (`parcel_id`, `owner_id`, `ownership_share`, `valid_from`, `valid_to`, `source_event_id`). *(Powers P3, P5)*.
4. **`deeds`**: Sub-Registry registered conveyances (`deed_id`, `parcel_id`, `seller_id`, `buyer_id`, `deed_number`, `sub_registry_office`, `execution_date`, `registration_date`, `declared_area`, `deed_status`, `document_id`). *(Powers P2, P3, P4)*.
5. **`transactions`**: Financial & legal transfer records (`transaction_id`, `parcel_id`, `deed_id`, `seller_id`, `buyer_id`, `transaction_date`, `status`, `mutation_link_status`). *(Powers P3, P4)*.
6. **`ownership_events`**: Immutable audit timeline (`event_id`, `parcel_id`, `previous_owner_id`, `new_owner_id`, `deed_id`, `event_date`, `event_type`, `verification_status`). *(Powers P3, P5)*.
7. **`mutation_records`**: AC Land mutation cases (`mutation_id`, `parcel_id`, `deed_id`, `applicant_id`, `case_number`, `application_date`, `status` [PENDING, UNDER_REVIEW, APPROVED, REJECTED], `decision_date`, `khatian_corrected`). *(Powers P4, P3)*.
8. **`documents`**: Physical/scanned files (`document_id`, `parcel_id`, `deed_id`, `document_type` [DEED, KHATIAN, PORCHA, MUTATION_CERT], `file_path`, `sha256_hash`, `qr_token`, `ocr_status`, `extracted_fields_json`, `provenance_label`). *(Powers P1, P2)*.
9. **`tax_records`**: Land Development Tax status (`tax_record_id`, `parcel_id`, `holding_number`, `tax_year`, `assessed_amount`, `paid_amount`, `payment_status`). *(Powers P5)*.
10. **`litigation_records`**: Land court cases (`case_id`, `parcel_id`, `court_name`, `case_number`, `filing_date`, `dispute_type`, `status` [ACTIVE, RESOLVED]). *(Powers P5)*.
11. **`khas_records`**: Government 1-No Khas land schedule (`khas_id`, `parcel_id`, `designation` [GOVERNMENT_KHAS, VESTED, WATER_BODY], `managing_authority`). *(Powers P5, P6)*.
12. **`acquisition_zones`**: Gazetted infrastructure corridors (`zone_id`, `project_name`, `gazette_notification_number`, `geometry_geojson`, `status`). *(Powers P5, P6)*.
13. **`verification_cases`**: Automated fraud & discrepancy findings (`case_id`, `parcel_id`, `finding_code`, `severity` [LOW, MEDIUM, HIGH, CRITICAL], `risk_score` [0-100], `explanation`, `evidence_references`, `review_status`). *(Powers P3)*.
14. **`review_logs`**: Officer action logs (`log_id`, `case_id`, `reviewer_id`, `action`, `reason`, `timestamp`). *(Powers P3)*.

---

## 5. Primary Verification Logic: P3 Catch Fraud & Double-Selling

The core verification engine runs five explainable, deterministic rule vectors:

1. **Rule DS-01: Concurrent Unmutated Deeds (Active Double-Selling)**
   - *Trigger:* Same parcel, same seller, deed A executed to Buyer 1, deed B executed to Buyer 2 while Mutation for Deed A remains pending or unfiled.
   - *Severity:* `CRITICAL` (Risk Score: 90).
   - *Action:* High-priority alert to Sub-Registrar and Buyer; blocks automatic e-mutation.

2. **Rule DS-02: Clean Sequential Conveyance (Negative Control)**
   - *Trigger:* Deed A executed -> Mutation approved and Khatian updated -> Buyer 1 (now owner) executes Deed B to Buyer 2.
   - *Severity:* `CLEAR` (Risk Score: 0).
   - *Action:* Verified legitimate chain of custody.

3. **Rule DS-03: Area Over-Sale Discrepancy**
   - *Trigger:* Cumulative area in active transfers exceeds the recorded parcel khatian area (e.g. 15 decimals transferred from a 10-decimal plot).
   - *Severity:* `HIGH` (Risk Score: 75).
   - *Action:* Flags mathematical discrepancy for AC Land manual survey review.

4. **Rule DS-04: Duplicate Document Upload vs. New Sale**
   - *Trigger:* Identical SHA-256 file uploaded twice for the same deed transaction.
   - *Severity:* `INFO / LOW` (Risk Score: 10).
   - *Action:* Distinguishes redundant upload from an attempted second sale.

5. **Rule DS-05: Tax Arrears & Encumbrance Warning**
   - *Trigger:* Outstanding LDTax arrears exceeding 3 fiscal years or active civil litigation.
   - *Severity:* `MEDIUM` (Risk Score: 40).
   - *Action:* Advisory caveat included in citizen due-diligence report.

---

## 6. Implementation Status & Traceability Markers

Every component and deliverable is strictly tracked under controlled status values:
- `PLANNED`: Designed and mapped; implementation not yet started.
- `IN PROGRESS`: Active implementation currently underway.
- `IMPLEMENTED`: Code complete; awaiting formal test verification.
- `TESTED`: Automated tests pass with documented evidence.

### Current Status Matrix (End of Phase 0):

| Component / Subsystem | Track Scope | Current Status | Notes / Evidence |
|---|---|---|---|
| **Phase 0 Baseline & Rulebook Audit** | General | `IMPLEMENTED` | Verified against `docs/landtech_hackathon_rulebook.pdf` v1.2 |
| **Traceability Matrix (`docs/RULEBOOK_TRACEABILITY_MATRIX.md`)** | P1–P6 | `IMPLEMENTED` | Complete mapping across all 6 problem tracks |
| **Source Register & Reference Documentation** | P1–P6 | `PLANNED` | Scheduled for Phase 1 |
| **Shared Relational Schema & Data Dictionary** | P1–P6 | `PLANNED` | Unified 14-entity relational data model |
| **Deterministic Synthetic Dataset Generator** | P1–P6 | `PLANNED` | 1,000 parcels, 200 owners, fixed seed |
| **Data Integrity Validation Pipeline** | P1–P6 | `PLANNED` | Foreign-key, chronology, and coordinate checks |
| **P1 OCR & Khatian Search Engine** | P1 | `PLANNED` | Tesseract OCR + graceful failure reporting |
| **P2 SHA-256 Hashing & QR Verifier** | P2 | `PLANNED` | Cryptographic tamper-evidence service |
| **P3 Double-Selling Detection Core** | P3 | `PLANNED` | 5 explainable deterministic rules |
| **P4 Smart e-Mutation Bridge** | P4 | `PLANNED` | Sub-Registry to AC Land status state-machine |
| **P5 "Check Before You Buy" Dossier** | P5 | `PLANNED` | Citizen-facing due diligence card and printable report |
| **P6 Geospatial Cadastral & Khas Inspector** | P6 | `PLANNED` | Leaflet GeoJSON layer + Khas buffer detection |
| **Officer Review Queue & Audit Log** | P3, P4 | `PLANNED` | Role-enforced review workflow |
| **Submission Artifacts (Concept Note, Video Script, README)** | Hackathon | `PLANNED` | Scheduled for Phase 7 |

---

## 7. Recommended Implementation Order Across Phases

```
Phase 0: Workspace & Multi-Track Requirements Baseline (COMPLETED)
   ├── Rulebook v1.2 Ingestion (P1–P6)
   ├── Backup & Update Project Blueprint
   └── Create Traceability Matrix (docs/RULEBOOK_TRACEABILITY_MATRIX.md)
   
Phase 1: Source Research & Data Design (NEXT)
   ├── Official Source Register (portal.ldtax, dlrs, eporcha, national portal)
   ├── Reference Data Findings (CS/SA/RS/BS, Khatian structures, Deed tax laws)
   ├── Unified Relational ERD & Data Dictionary
   └── Multi-Track Synthetic Generation Specification

Phase 2: Minimal Shared Synthetic Dataset
   ├── 1,000 Parcels + 200 Owners + Seeded Scenarios for P1–P6
   ├── Deterministic scenario catalog with ground truth
   └── Rigorous data validation pipeline & manifest generation

Phase 3: Backend Multi-Track Services & APIs
   ├── Core FastAPI architecture & SQLite persistence
   ├── P3 Double-Selling Rule Engine (Primary)
   ├── P1 OCR & Document Integrity (P2)
   ├── P4 e-Mutation State Machine
   ├── P5 Due Diligence Dossier API
   ├── P6 Spatial Boundary Intersection Service
   └── Pytest regression test suite

Phase 4: Responsive Frontend Interface
   ├── Bilingual UI (Bangla-first with English toggle)
   ├── Citizen "Check Before You Buy" Search & Dossier (P5)
   ├── P3 Officer Review Queue & Case Discrepancy View
   └── P4 Mutation Lifecycle Tracker

Phase 5: Supporting Workflows & GIS Presentation
   ├── P6 Leaflet Cadastral Map (GeoJSON parcels & Khas overlays)
   ├── P2 Live Document Upload & SHA-256 Verifier
   ├── P1 Searchable Legacy Khatian viewer
   └── PDF printable due-diligence report

Phase 6: Scale, Benchmark & Verification
   ├── Extended dataset validation
   └── Performance & relationship consistency checks

Phase 7: Final Hackathon Packaging & Deliverables
   ├── Technical README (setup instructions, data sources, AI tools)
   ├── 3-Page Concept Note PDF (strictly adhering to Rulebook Section 8)
   ├── 90-Second Demo Video Script
   └── Final regression test run and acceptance sign-off
```

---

## 8. Preserved Project Constraints & Safety Rules

1. **Strictly Synthetic Data:** No real citizen names, NID numbers, phone numbers, or genuine land records will be used.
2. **Zero Live Scraping:** No automated scraping or penetration attempts against live government portals.
3. **Deterministic & Reproducible:** All synthetic data and test cases generated from fixed random seeds.
4. **Honest Failure Reporting:** If OCR fails or Bangla language packs are missing, the system will explicitly report the failure status without fabricating mock text.
5. **Human Advisory Scope:** The system clearly advises human officers and citizens; it never issues legally binding title determinations.
