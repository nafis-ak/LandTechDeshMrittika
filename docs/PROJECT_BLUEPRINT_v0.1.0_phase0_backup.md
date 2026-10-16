# DESHMRITTIKA / BHUMI-SYNC
## Master Project Blueprint & Phase 0 Foundation
**Tagline:** Your Land, Our Responsibility (আপনার জমি, আমাদের দায়িত্ব)  
**Hackathon Track:** Digital Land Records, Verification & Digitization  
**Primary Problem:** P3 — Catch Fraud & Double-Selling  
**Target Event:** LandTech 2026 — LandTech Innovation Hackathon (Daffodil International University)  
**Document Version:** 1.0.0 (Phase 0 Execution)  
**Date:** October 16, 2026  

---

## 1. Executive Summary & Mission

Land disputes in Bangladesh constitute over 70% of ongoing civil litigation, predominantly originating from:
1. Double-selling (the same seller executing deeds to multiple unsuspecting buyers before mutation).
2. Fragmented record silos across Sub-Registry Offices (Ministry of Law) and AC Land / Union Land Offices (Ministry of Land).
3. Forged historical deeds, conflicting legacy survey khatians (CS, SA, RS, BS/City), and mutation delays.

**DESHMRITTIKA / BHUMI-SYNC** is a synthetic-data-powered land-record verification and buyer due-diligence prototype designed for smart e-governance in Bangladesh. It bridges registry deeds and mutation records to detect conflicting transfers, flag inconsistent ownership chains, compute explainable risk scores, and present transparent evidence for human officer review.

> **Crucial Ethical & Legal Premise:**  
> The system acts as an advisory risk-triage tool for human officers and citizens. It **never** claims to conclusively determine legal ownership, declare individuals guilty of fraud, or replace authorized judicial/land administration officers.

---

## 2. Hackathon Alignment (LandTech 2026 Rulebook v1.2)

From the official LandTech 2026 Rulebook (`landtech_hackathon_rulebook.pdf`), organized by the Department of CSE & CSE-TECH and supported by the Department of Law, Daffodil International University:

| Parameter | Rulebook Specification | Project Alignment |
|---|---|---|
| **Problem Track** | P3: Catch Fraud & Double-Selling | Exact match: Spot fake deeds, double-selling, and registry-to-mutation mismatches |
| **Target Users** | Citizens/Buyers, Sub-Registry, AC Land, Banks, DLRS | Citizen "Check Before You Buy" + Officer Verification Queue |
| **Submission Deadline (Round 1)** | October 18, 2026 (Online platform) | Full prototype, concept note, code repo & video script ready before deadline |
| **Team Composition** | 2 DIU Students (1 Leader, 1 Member) + 2 Mentors (1 Faculty, 1 Industry) | Template slots reserved in documentation for team insertion |
| **Deliverables Required** | 1. 3-Page Concept Note PDF<br>2. Public GitHub Repo + README<br>3. 90-second Demo Video<br>4. Live Demo Link | All four artifacts systematically produced in the execution plan |
| **Strict Data Rule** | NO real citizens' names, NID numbers, phone numbers, or real land records. NO scraping live government websites. | 100% synthetic, deterministic data with reproducible seeds and watermarks |
| **Security Rule** | Test only on local sandbox. No penetration tests against government systems. | Isolated local SQLite/FastAPI environment; no outbound requests to gov APIs |
| **AI Transparency** | List all AI tools used clearly in the README. | Explicit AI tools register in README and documentation |

---

## 3. High-Level System Architecture

```
+-----------------------------------------------------------------------------------+
|                            CLIENT PRESENTATION LAYER                              |
|  +-----------------------------------+     +-----------------------------------+  |
|  |     Citizen / Buyer Portal        |     |      Officer Verification Queue   |  |
|  | - Universal Parcel Search         |     | - Triage Risk Queue (High/Med)    |  |
|  | - "Check Before You Buy" Report   |     | - Deed & Chain Audit Trail        |  |
|  | - Leaflet Cadastral Map (GeoJSON) |     | - Human Review Decision Actions   |  |
|  | - Bilingual UI (Bangla / English) |     | - Document Integrity Inspector    |  |
|  +-----------------------------------+     +-----------------------------------+  |
+------------------------------------------^----------------------------------------+
                                           | HTTP REST / JSON
+------------------------------------------v----------------------------------------+
|                              APPLICATION BACKEND LAYER                            |
|                          (FastAPI / Python 3.13 / Pydantic)                       |
|                                                                                   |
|  +---------------------------+  +----------------------------------------------+  |
|  |   Search & Query Engine   |  |        Fraud & Double-Selling Engine         |  |
|  | - Khatian / Dag / Mouza   |  | - Deterministic Multi-Rule Validator         |  |
|  | - Owner Profile & Deeds   |  | - Timeline Overlap & Mutation Conflict       |  |
|  +---------------------------+  | - Explainable Risk Scoring & Evidence Logs   |  |
|                                 +----------------------------------------------+  |
|  +---------------------------+  +----------------------------------------------+  |
|  | Document Integrity & OCR  |  |           Role-Based Access Control          |  |
|  | - SHA-256 Checksum Engine |  | - Citizen, Buyer, Officer, Admin             |  |
|  | - Tesseract OCR & Status  |  | - Server-Side Permission Guard               |  |
|  +---------------------------+  +----------------------------------------------+  |
+------------------------------------------^----------------------------------------+
                                           | SQLAlchemy ORM
+------------------------------------------v----------------------------------------+
|                                PERSISTENCE LAYER                                  |
|                             (SQLite Engine / WAL Mode)                            |
|                                                                                   |
|  [parcels]               [owners]              [parcel_ownership]                 |
|  [deeds]                 [transactions]        [ownership_events]                 |
|  [mutation_records]      [documents]           [tax_records]                      |
|  [verification_cases]    [review_logs]         [synthetic_manifests]              |
+-----------------------------------------------------------------------------------+
```

---

## 4. Relational Data Model Blueprint

The data model enforces relational integrity across fragmented records without forcing 1:1 shortcuts:

1. **`parcels`**: Root cadastral entity (`parcel_id`, `district`, `upazila`, `mouza`, `dag_number`, `khatian_number`, `land_classification`, `area_decimal`, `coordinates`, `provenance_label`).
2. **`owners`**: Fictional identities (`owner_id`, `fictional_name`, `synthetic_nid_hash`, `contact_masked`, `provenance_label`).
3. **`parcel_ownership`**: Many-to-many temporal ownership (`parcel_id`, `owner_id`, `ownership_share`, `valid_from`, `valid_to`).
4. **`deeds`**: Sub-registry records (`deed_id`, `parcel_id`, `seller_id`, `buyer_id`, `execution_date`, `registration_date`, `declared_area`, `deed_status`, `document_hash`).
5. **`transactions`**: Financial and legal settlement (`transaction_id`, `parcel_id`, `deed_id`, `seller_id`, `buyer_id`, `transaction_date`, `status`, `mutation_status`).
6. **`ownership_events`**: Immutable event ledger (`event_id`, `parcel_id`, `previous_owner_id`, `new_owner_id`, `deed_id`, `event_date`, `event_type`, `verification_status`).
7. **`mutation_records`**: AC Land e-mutation history (`mutation_id`, `parcel_id`, `deed_id`, `applicant_id`, `application_date`, `status`, `decision_date`, `synthetic_case_number`).
8. **`documents`**: Physical or scanned digital papers (`document_id`, `parcel_id`, `document_type`, `file_path`, `sha256_hash`, `ocr_status`, `ocr_text`).
9. **`tax_records`**: LDTax compliance status (`tax_record_id`, `parcel_id`, `holding_id`, `tax_year`, `assessed_amount`, `paid_amount`, `payment_status`).
10. **`verification_cases`**: Automated audit outputs (`case_id`, `parcel_id`, `finding_code`, `severity`, `risk_score`, `explanation`, `evidence_references`, `review_status`).
11. **`review_logs`**: Tamper-evident reviewer audit trail (`log_id`, `case_id`, `reviewer_id`, `action`, `reason`, `timestamp`).

---

## 5. Double-Selling & Fraud Detection Logic

The verification engine executes five explainable, deterministic rule vectors:

1. **Rule DS-01: Concurrent Unmutated Deeds (Active Double-Selling)**
   - *Condition:* Same parcel, same seller, deed A executed to Buyer 1, deed B executed to Buyer 2 within an overlapping window where Mutation for Deed A is either pending or absent, yet seller attempts to transfer the same share.
   - *Severity:* CRITICAL (Score: 85-95).
   - *Output:* Flags both deeds, provides timeline evidence, alerts officer for immediate cross-verification with Sub-Registry.

2. **Rule DS-02: Sequential Legitimate Transfer (Negative Control / No Fraud)**
   - *Condition:* Deed A executed from Owner 1 to Owner 2 -> Mutation completed and approved -> Owner 2 executes Deed B to Owner 3.
   - *Severity:* CLEAR (Score: 0-10).
   - *Output:* Chain of title verified; marked as clean sequential conveyance.

3. **Rule DS-03: Area Over-Sale Discrepancy**
   - *Condition:* Sum of shares or decimals transferred in active deeds exceeds the recorded parcel khatian area.
   - *Severity:* HIGH (Score: 70-80).
   - *Output:* Explicit math discrepancy logged with recorded vs. transferred area.

4. **Rule DS-04: Duplicate Document Upload / Tamper Detection**
   - *Condition:* Same deed or porcha file uploaded twice or file content modified resulting in SHA-256 hash collision or mismatch.
   - *Severity:* MEDIUM (Score: 50).
   - *Output:* Distinguishes duplicate upload of identical file from a second sale.

5. **Rule DS-05: Tax Arrears & Mutation Stoppage**
   - *Condition:* Unpaid land development tax exceeding statutory thresholds or pending acquisition gazette notification.
   - *Severity:* MEDIUM/LOW (Score: 30-40).
   - *Output:* Due diligence warning for buyer negotiation.

---

## 6. Initial Risk Register

| Risk ID | Category | Risk Description | Severity | Mitigation Strategy |
|---|---|---|---|---|
| **RSK-01** | Data Privacy | Accidental leakage of real citizen names, NIDs, or phone numbers. | CRITICAL | Strictly use synthetic data generators with fixed faker seeds and explicit prefix `SYNTH-`. Automated regex scan against real NID patterns. |
| **RSK-02** | Legal / Ethics | Misleading claims of definitive automated fraud conviction or title guarantee. | HIGH | Clear disclaimer banners across all UI screens and PDF reports: *"Advisory triage tool only. Does not constitute conclusive legal title."* |
| **RSK-03** | Scraping / Security | Attempting live scrapers against `eporcha.gov.bd` or `portal.ldtax.gov.bd` violating hackathon rules. | CRITICAL | Zero external live scraper code. Purely model public schemas from official documentation as reference structures for synthetic generators. |
| **RSK-04** | OCR Fragility | Local environment missing Bengali OCR training data or failing on low-res scans. | MEDIUM | Graceful degradation: report accurate `OCR_STATUS = 'LANGUAGE_PACK_UNAVAILABLE'` or `FAILED_TO_PARSE` without fabricating fake extracted text. |
| **RSK-05** | Cadastral Accuracy | Confusing synthetic boundary polygons with official DLRS cadastral maps. | MEDIUM | Synthetic GeoJSON generated with explicit randomized offsets around realistic mouza coordinates, watermarked as *"Synthetic Cadastral Visualization"*. |
| **RSK-06** | Hackathon Eligibility | Missing team student/mentor structure or violating presentation rules. | HIGH | Dedicated team configuration placeholders created in Phase 0; strict adherence to 2-student + 2-mentor structure. |

---

## 7. Phase Gates & Execution Roadmap

```
Phase 0: Workspace & Requirements Baseline (CURRENT)
   └── Confirm workspace, rulebook ingestion, blueprint, risk register.
Phase 1: Source Research & Data Design
   └── Official source register, reference data findings, ERD & data dictionary.
Phase 2: Minimal Synthetic Dataset (1,000 parcels, 200 owners)
   └── Deterministic generator, scenario catalog, integrity validation pipeline.
Phase 3: Backend Core Engine & APIs
   └── FastAPI models, search endpoints, double-selling rules engine, pytest suite.
Phase 4: Frontend Development
   └── Bengali-first UI, English toggle, parcel profile, due diligence card, review view.
Phase 5: Supporting Due Diligence & GIS
   └── Leaflet cadastral map, SHA-256 document hashing, OCR pipeline, officer audit log.
Phase 6: Scale & Optimization
   └── Dataset validation at scale, performance benchmark, relationship consistency.
Phase 7: Final Packaging & Submission Deliverables
   └── README, 3-page Concept Note PDF, 90-sec demo script, verification checklist.
```

---

## 8. Required Outputs & Unresolved Decisions

### A. Phase 0 Deliverables
- [x] Absolute workspace verified (`/Users/macbookair/Desktop/LandTechDeshMrittika`).
- [x] Existing workspace inspected (Confirmed empty).
- [x] Hackathon rulebook located (`/Users/macbookair/Downloads/landtech_hackathon_rulebook.pdf`) and fully analyzed.
- [x] Project Blueprint and Risk Register authored in `docs/PROJECT_BLUEPRINT.md`.

### B. Unresolved User Decisions (Awaiting Input)
1. **Team & Mentor Information:**
   - Student 1 (Team Leader): Name & DIU Student ID
   - Student 2 (Member): Name & DIU Student ID
   - Faculty Mentor: Name, Department, DIU Designation
   - Industry Mentor: Name, Organization, Designation
   *(Note: These can be filled in now or kept as documented placeholders until submission preparation.)*
2. **Pilot Location Selection:**
   - Recommended: Savar Upazila, Dhaka District (e.g., Mouza: Aminbazar / Birulia) — highly relevant for peri-urban land disputes and rapid development.
   - Alternative: Gazipur Sadar or Purbachal.
3. **Approval to Proceed:**
   - Formal sign-off on Phase 0 to proceed to **Phase 1: Source Research & Data Design**.
