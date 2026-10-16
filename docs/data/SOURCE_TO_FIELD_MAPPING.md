# SOURCE-TO-FIELD MAPPING SPECIFICATION
## Comprehensive Field Provenance & Schema Derivation Matrix
**Project:** DESHMRITTIKA / BHUMI-SYNC (দেশমৃত্তিকা)  
**Document Version:** 1.0.0 (Phase 1 Baseline)  
**Date:** October 17, 2026  
**Core Principle:** *A verified statutory field definition does not make the generated record real.* Every schema field is rigorously tied to its official source or architectural necessity, while all row instances are strictly marked as synthetic.

---

## 1. Schema Derivation Categories

Every field across the unified 14-entity relational schema is classified under one of three derivation types:
1. **`DIRECTLY_DERIVED`**: Field name, data type, and statutory validation rules are directly defined by official Bangladesh government acts, manuals, or portals (SATA 1950, Registration Act 1908, LDTax portal).
2. **`ADAPTED`**: Statutory field adapted for modern relational database modeling, software query indexing, or international cadastral standards (e.g. LINZ spatial geometry, ISO 8601 timestamps).
3. **`TEAM_DESIGNED`**: Architectural and audit fields designed by the project team for automated double-selling verification, cryptographic hashing, and human review triage.

All generated records are categorized as **`SYNTHETIC_VALUE`** to guarantee citizen privacy and compliance with hackathon data rules.

---

## 2. Table-by-Table Field Mapping

### A. Table: `parcels` (Cadastral Spatial Entities)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `parcel_id` | `TEAM_DESIGNED` | LINZ Cadastral Schema (`https://data.linz.govt.nz/`) | Unique alphanumeric primary key (`BD-PAR-XXXXXX`) for relational integrity. | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `district` | `DIRECTLY_DERIVED` | BBS Geocode / Bangladesh Portal (`https://bangladesh.gov.bd/`) | Administrative division level 2 (District: Dhaka, BBS code 26). | `SYNTHETIC_VALUE` (Anchored to Dhaka) | Standard official BBS geocode name. |
| `upazila` | `DIRECTLY_DERIVED` | BBS Geocode (`https://bbs.gov.bd/`) | Sub-district administrative unit (Upazila: Savar, BBS code 2672). | `SYNTHETIC_VALUE` (Anchored to Savar) | Standard official BBS geocode name. |
| `mouza` | `DIRECTLY_DERIVED` | SATA 1950 Sec 117 / Land Ministry Manuals | Cadastral survey base unit (e.g. Aminbazar, Birulia). | `SYNTHETIC_VALUE` | Authentic mouza names in Savar. |
| `jl_number` | `DIRECTLY_DERIVED` | SATA 1950 Sec 117 / DLRS Cadastral Map | Jurisdiction List Number (e.g. JL 12 for Aminbazar, JL 24 for Birulia). | `SYNTHETIC_VALUE` | Verified official JL numbering for Savar. |
| `dag_number` | `DIRECTLY_DERIVED` | DLRS Cadastral Survey Guidelines (SATA 1950) | Official survey plot identifier on mouza map sheet (e.g. 101, 102). | `SYNTHETIC_VALUE` | Synthetic integer plot sequence (1 to 100,000). |
| `khatian_number` | `DIRECTLY_DERIVED` | SATA 1950 Sec 17 & 117 (ROR Register) | Record of Rights account serial number under the mouza. | `SYNTHETIC_VALUE` | Synthetic ROR serial. |
| `survey_type` | `DIRECTLY_DERIVED` | Settlement Dept Technical Rules / SATA 1950 | Historical survey code: `CS`, `SA`, `RS`, `BS_CITY`. | `SYNTHETIC_VALUE` | Controlled enumeration matching statutory surveys. |
| `land_classification`| `DIRECTLY_DERIVED` | LDTax Portal (`https://portal.ldtax.gov.bd/`) | Statutory land tax category (Nal, Viti, Dhani, Pukur, Banijjik). | `SYNTHETIC_VALUE` | Standard Bangladesh land categories. |
| `area_decimal` | `DIRECTLY_DERIVED` | SATA 1950 Sec 117 / BS Survey Standards | Land area measured in Bangladesh standard decimals (শতক / শতাংশ; 1 acre = 100 decimals). | `SYNTHETIC_VALUE` | Realistic decimal range (2.50 to 120.00 decimals). |
| `coordinates_geojson`| `ADAPTED` | LINZ & OpenStreetMap (`https://www.openstreetmap.org/`) | Polygon boundary coordinates in WGS 84 (EPSG:4326) bounding Savar pilot. | `SYNTHETIC_VALUE` | Approximate demonstration polygons; non-authoritative survey geometry. |
| `is_disputed` | `TEAM_DESIGNED` | Project Verification Architecture | Boolean flag indicating active dispute / freeze. | `SYNTHETIC_VALUE` | Ground-truth flag for scenario validation. |
| `provenance_label` | `TEAM_DESIGNED` | Hackathon Rulebook v1.2 Sec 10 | Constant label: `SYNTHETIC_DEMO_RECORD`. | `SYNTHETIC_VALUE` | Enforced compliance watermark. |

---

### B. Table: `owners` (Fictional Citizen Proprietors)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `owner_id` | `TEAM_DESIGNED` | Relational Architecture | Unique identifier (`OWN-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `fictional_name` | `ADAPTED` | Bangladesh National Portal (`https://bangladesh.gov.bd/`) | Authentic Bengali naming conventions generated via Faker (e.g. মো: রফিকুল ইসলাম). | `SYNTHETIC_VALUE` | Purely fictional; zero real person linkage. |
| `synthetic_nid_hash`| `TEAM_DESIGNED`| Smart LDTax Holding Registration Requirements | LDTax requires citizen NID. Modeled as SHA-256 hash of fictional 10/17-digit number prefixed with `SYNTH-`. | `SYNTHETIC_VALUE` | Real NIDs strictly excluded by regex. |
| `contact_masked` | `ADAPTED` | LDTax Holding Registration (`portal.ldtax.gov.bd`) | LDTax requires active mobile number. Stored as masked non-routable format (`+8801700-00XXXX`). | `SYNTHETIC_VALUE` | Fictional non-contactable format. |
| `provenance_label`| `TEAM_DESIGNED` | Hackathon Rulebook v1.2 Sec 10 | Watermark: `FICTIONAL_CITIZEN_RECORD`. | `SYNTHETIC_VALUE` | Enforced compliance watermark. |

---

### C. Table: `parcel_ownership` (Temporal M:N Ownership Ledger)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `ownership_id` | `TEAM_DESIGNED` | Relational Architecture | Primary key (`POW-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `parcel_id` | `TEAM_DESIGNED` | FK to `parcels.parcel_id` | Relational linkage to cadastral plot. | `SYNTHETIC_VALUE` | Foreign key. |
| `owner_id` | `TEAM_DESIGNED` | FK to `owners.owner_id` | Relational linkage to fictional proprietor. | `SYNTHETIC_VALUE` | Foreign key. |
| `ownership_share`| `DIRECTLY_DERIVED` | SATA 1950 Sec 117 (Khatian 16-anna / Decimal share) | Decimal ownership fraction (e.g. 0.5000 = 8 annas / 50% share). Sum per parcel <= 1.0000. | `SYNTHETIC_VALUE` | Strictly validated share sum. |
| `valid_from` | `ADAPTED` | Registration Act 1908 & SATA 1950 | Date ownership commenced (execution/mutation date). | `SYNTHETIC_VALUE` | Valid ISO 8601 date. |
| `valid_to` | `ADAPTED` | SATA 1950 (Extinguishment of title upon transfer) | Date ownership ceased (`NULL` if currently active owner). | `SYNTHETIC_VALUE` | Nullable date for active vs. historical owners. |
| `source_event_id` | `TEAM_DESIGNED` | FK to `ownership_events.event_id` | Audit reference to the deed/mutation event creating this share. | `SYNTHETIC_VALUE` | Foreign key audit trail. |

---

### D. Table: `deeds` (Sub-Registry Conveyance Records)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `deed_id` | `TEAM_DESIGNED` | Relational Architecture | Primary key (`DEED-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `deed_number` | `DIRECTLY_DERIVED` | Registration Act 1908 Sec 52 (Book 1 Serial) | Serial registered deed number assigned by Sub-Registry (e.g. `10482/2024`). | `SYNTHETIC_VALUE` | Synthetic serial sequence. |
| `sub_registry_office`| `DIRECTLY_DERIVED`| Registration Act 1908 Sec 3 | Sub-Registry jurisdiction name (e.g. `সাভার সাব-রেজিস্ট্রি অফিস / Savar Sub-Registry`). | `SYNTHETIC_VALUE` (Savar) | Authentic office name. |
| `deed_type` | `DIRECTLY_DERIVED` | Transfer of Property Act 1882 / Registration Manual | Conveyance type: `SAF_KABALA`, `HEBA`, `BANTANNAMA`, `MORTGAGE`. | `SYNTHETIC_VALUE` | Controlled statutory enum. |
| `parcel_id` | `TEAM_DESIGNED` | FK to `parcels.parcel_id` | Transferred plot reference. | `SYNTHETIC_VALUE` | Foreign key. |
| `seller_id` | `TEAM_DESIGNED` | FK to `owners.owner_id` | Transferor identity. | `SYNTHETIC_VALUE` | Foreign key. |
| `buyer_id` | `TEAM_DESIGNED` | FK to `owners.owner_id` | Transferee identity. | `SYNTHETIC_VALUE` | Foreign key. |
| `execution_date` | `DIRECTLY_DERIVED` | Registration Act 1908 Sec 23 | Date deed was signed by parties before deed-writer. | `SYNTHETIC_VALUE` | Chronologically precedes registration. |
| `registration_date`| `DIRECTLY_DERIVED`| Registration Act 1908 Sec 60 | Date deed was registered in volume by Sub-Registrar. | `SYNTHETIC_VALUE` | Chronologically consistent date. |
| `declared_area` | `DIRECTLY_DERIVED` | SATA 1950 & Deed Schedule Rules | Area in decimals stated in the property schedule (তফসিল). | `SYNTHETIC_VALUE` | Validated against parcel area. |
| `deed_value_bdt` | `DIRECTLY_DERIVED` | Stamp Act 1899 & Registration Rules | Monetary consideration in Bangladeshi Taka (পণমূল্য). | `SYNTHETIC_VALUE` | Plausible peri-urban valuation. |
| `deed_status` | `TEAM_DESIGNED` | Project Architecture | Status: `REGISTERED`, `DISPUTED`, `CANCELLED_BY_COURT`. | `SYNTHETIC_VALUE` | Controlled status value. |
| `document_id` | `TEAM_DESIGNED` | FK to `documents.document_id` | Linkage to synthetic digital scanned deed document. | `SYNTHETIC_VALUE` | Foreign key. |

---

### E. Table: `transactions` (Financial & Registry Settlement)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `transaction_id`| `TEAM_DESIGNED` | Relational Architecture | Primary key (`TXN-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `parcel_id` | `TEAM_DESIGNED` | FK to `parcels.parcel_id` | Transferred plot. | `SYNTHETIC_VALUE` | Foreign key. |
| `deed_id` | `TEAM_DESIGNED` | FK to `deeds.deed_id` | Legal instrument underlying transaction. | `SYNTHETIC_VALUE` | Foreign key. |
| `seller_id` | `TEAM_DESIGNED` | FK to `owners.owner_id` | Seller reference. | `SYNTHETIC_VALUE` | Foreign key. |
| `buyer_id` | `TEAM_DESIGNED` | FK to `owners.owner_id` | Buyer reference. | `SYNTHETIC_VALUE` | Foreign key. |
| `transaction_date`| `ADAPTED` | Financial settlement standards | Date of monetary settlement and registry fees. | `SYNTHETIC_VALUE` | Matches deed registration date. |
| `status` | `TEAM_DESIGNED` | Project Architecture | Status: `COMPLETED`, `SUSPENDED`, `FLAGGED_FRAUD`. | `SYNTHETIC_VALUE` | Controlled status value. |
| `mutation_link_status`| `TEAM_DESIGNED`| P4 Bridge Architecture | Status: `UNLINKED`, `MUTATION_PENDING`, `MUTATED`. | `SYNTHETIC_VALUE` | Powers P4 and P3 unmutated checks. |

---

### F. Table: `ownership_events` (Immutable Audit Ledger)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `event_id` | `TEAM_DESIGNED` | Relational Architecture | Primary key (`EVT-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `parcel_id` | `TEAM_DESIGNED` | FK to `parcels.parcel_id` | Parcel experiencing tenure transition. | `SYNTHETIC_VALUE` | Foreign key. |
| `previous_owner_id`| `TEAM_DESIGNED`| FK to `owners.owner_id` | Transferor (`NULL` for original settlement / ROR creation). | `SYNTHETIC_VALUE` | Nullable foreign key. |
| `new_owner_id` | `TEAM_DESIGNED` | FK to `owners.owner_id` | Transferee. | `SYNTHETIC_VALUE` | Foreign key. |
| `deed_id` | `TEAM_DESIGNED` | FK to `deeds.deed_id` | Conveyance reference (`NULL` for inheritance/acquisition). | `SYNTHETIC_VALUE` | Nullable foreign key. |
| `event_date` | `ADAPTED` | Chronological audit trail | Timestamp of tenure modification. | `SYNTHETIC_VALUE` | Valid chronological date. |
| `event_type` | `DIRECTLY_DERIVED` | SATA 1950 Sec 143 (Modes of Transfer) | Type: `SALE_DEED`, `INHERITANCE_FARAYEZ`, `AUCTION_GOV`, `ACQUISITION`. | `SYNTHETIC_VALUE` | Controlled statutory enum. |
| `verification_status`| `TEAM_DESIGNED`| P3 Verification Core | Status: `VERIFIED`, `CONCURRENT_CONFLICT`, `INVESTIGATION_PENDING`. | `SYNTHETIC_VALUE` | Powers P3 detection engine. |

---

### G. Table: `mutation_records` (AC Land e-Mutation Cases)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `mutation_id` | `TEAM_DESIGNED` | Relational Architecture | Primary key (`MUT-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `case_number` | `DIRECTLY_DERIVED` | Ministry of Land e-Mutation Manual | Official e-mutation case number pattern: `M-YYYY-UPAZILA-XXXXX` (e.g. `M-2026-SAVAR-01429`). | `SYNTHETIC_VALUE` | Authentic case numbering syntax. |
| `parcel_id` | `TEAM_DESIGNED` | FK to `parcels.parcel_id` | Parcel submitted for separation/khatian update. | `SYNTHETIC_VALUE` | Foreign key. |
| `deed_id` | `TEAM_DESIGNED` | FK to `deeds.deed_id` | Registered deed supporting application. | `SYNTHETIC_VALUE` | Foreign key. |
| `applicant_id` | `TEAM_DESIGNED` | FK to `owners.owner_id` | Applicant citizen (Buyer). | `SYNTHETIC_VALUE` | Foreign key. |
| `application_date`| `DIRECTLY_DERIVED`| SATA 1950 Sec 143 | Filing date at Assistant Commissioner (Land) office. | `SYNTHETIC_VALUE` | Must be on or after deed registration date. |
| `status` | `DIRECTLY_DERIVED` | Ministry of Land 4-Stage Mutation Process | Status: `SUBMITTED`, `ULAO_INSPECTION`, `HEARING_DCR_PENDING`, `APPROVED`, `REJECTED`. | `SYNTHETIC_VALUE` | Exact match to government mutation workflow. |
| `decision_date` | `ADAPTED` | AC Land Order Sheet Date | Date final mutation order signed by AC Land. | `SYNTHETIC_VALUE` | Nullable until approved/rejected. |
| `mutated_khatian_no`| `DIRECTLY_DERIVED`| SATA 1950 Sec 144 (New Jote Creation) | New Khatian number created upon approval (জমা-খারিজ খতিয়ান). | `SYNTHETIC_VALUE` | Assigned upon approval. |

---

### H. Table: `documents` (Scanned Deeds, Khatians, & Files)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `document_id` | `TEAM_DESIGNED` | Relational Architecture | Primary key (`DOC-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `parcel_id` | `TEAM_DESIGNED` | FK to `parcels.parcel_id` | Parcel this document relates to. | `SYNTHETIC_VALUE` | Foreign key. |
| `deed_id` | `TEAM_DESIGNED` | FK to `deeds.deed_id` | Related deed (if document is a deed). | `SYNTHETIC_VALUE` | Nullable foreign key. |
| `document_type` | `DIRECTLY_DERIVED` | Land Record Categories (SATA / Registration Act) | Type: `DEED_COPY`, `CS_KHATIAN`, `RS_KHATIAN`, `BS_PORCHA`, `MUTATION_CERT`, `DAKHILA`. | `SYNTHETIC_VALUE` | Controlled statutory enum. |
| `file_path` | `TEAM_DESIGNED` | Local filesystem storage | Path relative to project root (`data/generated/documents/...`). | `SYNTHETIC_VALUE` | Physical synthetic file on disk. |
| `sha256_hash` | `TEAM_DESIGNED` | NIST FIPS 180-4 (SHA-256) / P2 Requirement | 64-character hexadecimal SHA-256 hash computed directly from file bytes. | `SYNTHETIC_VALUE` | Real cryptographic checksum. |
| `qr_token` | `TEAM_DESIGNED` | P2 QR Verification Requirement | Cryptographic validation token embedded into document QR code. | `SYNTHETIC_VALUE` | Verifiable synthetic token. |
| `ocr_status` | `TEAM_DESIGNED` | P1 OCR Pipeline Requirement | Status: `NOT_RUN`, `SUCCESS`, `PARTIAL_CONFIDENCE`, `LANGUAGE_PACK_UNAVAILABLE`, `FAILED`. | `SYNTHETIC_VALUE` | Honest reporting of OCR engine status. |
| `extracted_fields_json`| `TEAM_DESIGNED`| P1 Search & Extraction Engine | JSON blob containing OCR-extracted Khatian/Dag/Owner fields. | `SYNTHETIC_VALUE` | Real output from OCR parser. |
| `provenance_label`| `TEAM_DESIGNED` | Hackathon Rulebook v1.2 Sec 10 & 11 | Watermark: `SYNTHETIC DEMO DOCUMENT — NOT AN OFFICIAL RECORD`. | `SYNTHETIC_VALUE` | Visible on document canvas. |

---

### I. Table: `tax_records` (Land Development Tax Compliance)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `tax_record_id` | `TEAM_DESIGNED` | Relational Architecture | Primary key (`TAX-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `parcel_id` | `TEAM_DESIGNED` | FK to `parcels.parcel_id` | Assessed plot. | `SYNTHETIC_VALUE` | Foreign key. |
| `holding_number` | `DIRECTLY_DERIVED` | LDTax Portal (`https://portal.ldtax.gov.bd/`) | Union Land Office holding identifier (e.g. `HLD-SAVAR-2024-8192`). | `SYNTHETIC_VALUE` | Realistic holding format. |
| `tax_year` | `DIRECTLY_DERIVED` | LDTax Ordinance / Bengali Fiscal Year | Fiscal tax assessment year (e.g. `1430-1431 / 2023-2024`). | `SYNTHETIC_VALUE` | Standard tax fiscal years. |
| `assessed_amount`| `DIRECTLY_DERIVED` | LDTax Rate Schedules (Min of Land) | Annual assessed tax based on classification and area in decimals (BDT). | `SYNTHETIC_VALUE` | Computed from statutory rates. |
| `paid_amount` | `DIRECTLY_DERIVED` | LDTax Dakhila Receipts | Total tax paid for the fiscal period (BDT). | `SYNTHETIC_VALUE` | Must match or be less than assessed. |
| `dakhila_number`| `DIRECTLY_DERIVED` | LDTax Dakhila Portal (`portal.ldtax.gov.bd`) | Tax payment receipt serial (দাখিলা নম্বর). | `SYNTHETIC_VALUE` | Populated if paid. |
| `payment_status`| `DIRECTLY_DERIVED` | LDTax Payment Status | Status: `PAID`, `ARREARS_DUE`, `EXEMPTED`. | `SYNTHETIC_VALUE` | Controlled statutory enum. |

---

### J. Table: `litigation_records` (Civil Land Court Injunctions)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `case_id` | `TEAM_DESIGNED` | Relational Architecture | Primary key (`LIT-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `parcel_id` | `TEAM_DESIGNED` | FK to `parcels.parcel_id` | Subject parcel under dispute. | `SYNTHETIC_VALUE` | Foreign key. |
| `court_name` | `DIRECTLY_DERIVED` | Civil Courts Act 1887 / Bangladesh Portal | Court jurisdiction (e.g. `সিনিয়র সহকারী জজ আদালত, সাভার / Senior Assistant Judge Court, Savar`). | `SYNTHETIC_VALUE` | Authentic court jurisdiction name. |
| `case_number` | `DIRECTLY_DERIVED` | Civil Court Case Filing Practice | Case number format (e.g. `Title Suit No. 84/2023`). | `SYNTHETIC_VALUE` | Realistic civil suit numbering. |
| `dispute_type` | `DIRECTLY_DERIVED` | Code of Civil Procedure 1908 (Title Injunctions) | Type: `TITLE_DECLARATION`, `PARTITION_DISPUTE`, `INJUNCTION_AGAINST_SALE`, `ADVERSE_POSSESSION`. | `SYNTHETIC_VALUE` | Common land dispute categories. |
| `filing_date` | `ADAPTED` | Court Register Records | Date suit instituted. | `SYNTHETIC_VALUE` | Chronologically valid date. |
| `status` | `DIRECTLY_DERIVED` | Judicial Case Management | Status: `ACTIVE_INJUNCTION_STAY`, `DISMISSED`, `DECREED`. | `SYNTHETIC_VALUE` | Controls P5 due-diligence flag. |

---

### K. Table: `khas_records` (Government 1-No Khas Schedule)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `khas_id` | `TEAM_DESIGNED` | Relational Architecture | Primary key (`KHS-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `parcel_id` | `TEAM_DESIGNED` | FK to `parcels.parcel_id` | Parcel designated as public state property. | `SYNTHETIC_VALUE` | Foreign key. |
| `khas_category` | `DIRECTLY_DERIVED` | SATA 1950 Sec 86 & Non-Agricultural Tenancy Act | Category: `1_NO_GOVERNMENT_KHAS`, `RIVER_CANAL_WATERBODY`, `VESTED_PROPERTY`, `FORESHORE`. | `SYNTHETIC_VALUE` | Statutory public land categories. |
| `managing_authority`| `DIRECTLY_DERIVED`| SATA 1950 / Land Management Manual | Responsible authority: `COLLECTOR_DHAKA` (Deputy Commissioner, Dhaka). | `SYNTHETIC_VALUE` | Official statutory custodian. |
| `is_protected` | `TEAM_DESIGNED` | P6 Protection Engine | Boolean flag: Transfer is prohibited by law. | `SYNTHETIC_VALUE` | Triggers P6 encroachment alert. |

---

### L. Table: `acquisition_zones` (Gazetted Infrastructure Corridors)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `zone_id` | `TEAM_DESIGNED` | Relational Architecture | Primary key (`ACQ-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `project_name` | `ADAPTED` | Roads and Highways Dept / Bangladesh Portal | Infrastructure project name (e.g. `Dhaka-Aricha Highway 8-Lane Expansion Project`). | `SYNTHETIC_VALUE` | Realistic public development project. |
| `gazette_notification_no`| `DIRECTLY_DERIVED`| ARIPA 2017 Sec 4 (Gazette Notification) | Official Section 4 gazette serial (e.g. `DHAKA-GAZ-ARIPA-2024-402`). | `SYNTHETIC_VALUE` | Realistic gazette reference. |
| `corridor_geojson`| `ADAPTED` | INLIS Road Line Protection Reference (`app.sla.gov.sg/inlis/`) | Spatial polygon of infrastructure corridor in Savar pilot coordinates. | `SYNTHETIC_VALUE` | Approximate demonstration corridor geometry. |
| `status` | `DIRECTLY_DERIVED` | ARIPA 2017 Acquisition Stages | Status: `SECTION_4_NOTIFIED`, `SECTION_7_VERIFIED`, `SECTION_8_AWARDED`. | `SYNTHETIC_VALUE` | Statutory acquisition phases. |

---

### M. Table: `verification_cases` (Automated Audit Findings)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `case_id` | `TEAM_DESIGNED` | Relational Architecture | Primary key (`CASE-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `parcel_id` | `TEAM_DESIGNED` | FK to `parcels.parcel_id` | Evaluated parcel. | `SYNTHETIC_VALUE` | Foreign key. |
| `finding_code` | `TEAM_DESIGNED` | P3 Fraud Engine Rules | Code: `DS-01` (Concurrent unmutated sales), `DS-02` (Sequential clean), `DS-03` (Area over-sale), `DS-04` (Duplicate upload), `DS-05` (Tax/court arrears), `P6-ENCROACH` (Khas/Corridor overlap). | `SYNTHETIC_VALUE` | Controlled rule code. |
| `severity` | `TEAM_DESIGNED` | Triage Architecture | Level: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`. | `SYNTHETIC_VALUE` | Triage indicator for officers. |
| `risk_score` | `TEAM_DESIGNED` | Mathematical Scoring Model | Explainable risk score from 0 (Clean) to 100 (Critical Fraud Risk). | `SYNTHETIC_VALUE` | Strictly triage, not legal probability. |
| `explanation_bn`| `TEAM_DESIGNED` | Bilingual E-Governance Standards | Plain-language Bengali explanation for human review. | `SYNTHETIC_VALUE` | User-facing rationale. |
| `explanation_en`| `TEAM_DESIGNED` | Bilingual E-Governance Standards | Plain-language English explanation. | `SYNTHETIC_VALUE` | User-facing rationale. |
| `evidence_references`| `TEAM_DESIGNED`| Audit Provenance Standard | JSON array of linked deed IDs, transaction IDs, or file hashes. | `SYNTHETIC_VALUE` | Direct evidence trail. |
| `review_status` | `TEAM_DESIGNED` | Officer Workflow | Status: `PENDING_REVIEW`, `UNDER_INVESTIGATION`, `ESCALATED`, `RESOLVED_CLEARED`. | `SYNTHETIC_VALUE` | Governs officer review queue. |

---

### N. Table: `review_logs` (Officer Review Audit Trail)

| Field Name | Derivation Type | Reference Source & Exact URL | Statutory / Empirical Evidence | Generated Value Status | Uncertainty & Restrictions |
|---|---|---|---|---|---|
| `log_id` | `TEAM_DESIGNED` | Relational Architecture | Primary key (`LOG-XXXXXX`). | `SYNTHETIC_VALUE` | Internal synthetic PK. |
| `case_id` | `TEAM_DESIGNED` | FK to `verification_cases.case_id` | Evaluated finding. | `SYNTHETIC_VALUE` | Foreign key. |
| `reviewer_id` | `TEAM_DESIGNED` | Role-Based Access Control | Identifier of authorized officer (`OFFICER-SAVAR-01`). | `SYNTHETIC_VALUE` | Demo officer identity. |
| `action` | `TEAM_DESIGNED` | Administrative Review Actions | Action: `APPROVED_LEGITIMATE`, `REJECTED_FRAUD_FLAG`, `REQUESTED_PHYSICAL_INSPECTION`. | `SYNTHETIC_VALUE` | Controlled action enum. |
| `reason` | `TEAM_DESIGNED` | Human Audit Integrity | Officer's recorded justification notes. | `SYNTHETIC_VALUE` | Mandatory review note. |
| `timestamp` | `ADAPTED` | ISO 8601 Audit Standard | UTC timestamp when review action was executed. | `SYNTHETIC_VALUE` | Tamper-evident timestamp. |
