# FORMAL DATA DICTIONARY
## Unified Multi-Track Schema Specification (P1 through P6)
**Project:** DESHMRITTIKA / BHUMI-SYNC (দেশমৃত্তিকা)  
**Document Version:** 1.0.0 (Phase 1 Baseline)  
**Date:** October 17, 2026  
**Target Persistence Engine:** SQLite (WAL Mode) with PostgreSQL-compatible schema definitions.

---

## 1. Table Specifications

### 1. `parcels`
Root cadastral entity representing a surveyed plot of land.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `parcel_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique plot identifier (e.g., `BD-PAR-000001` to `BD-PAR-100000`). |
| `district` | `VARCHAR(64)` | NO | Default: `'Dhaka'` | Administrative district name. |
| `upazila` | `VARCHAR(64)` | NO | Default: `'Savar'` | Administrative upazila name. |
| `mouza` | `VARCHAR(64)` | NO | Controlled: `'Aminbazar'`, `'Birulia'` | Cadastral survey mouza name. |
| `jl_number` | `INTEGER` | NO | `CHECK (jl_number > 0)` | Jurisdiction List serial number (12 for Aminbazar, 24 for Birulia). |
| `dag_number` | `INTEGER` | NO | `CHECK (dag_number > 0)` | Survey plot serial number on mouza map sheet. |
| `khatian_number` | `INTEGER` | NO | `CHECK (khatian_number > 0)` | Record of Rights serial account under the mouza. |
| `survey_type` | `VARCHAR(16)` | NO | `CHECK (survey_type IN ('CS', 'SA', 'RS', 'BS_CITY'))` | Historical survey era under which parcel was mapped. |
| `land_classification` | `VARCHAR(32)` | NO | `CHECK (land_classification IN ('নাল', 'ভিটি', 'ধানী', 'পুকুর', 'পতিত', 'বাগান', 'বাণিজ্যিক', 'রাস্তা'))` | Official land revenue classification. |
| `area_decimal` | `NUMERIC(10, 2)` | NO | `CHECK (area_decimal > 0.0)` | Total area of plot in decimals (শতক). |
| `coordinates_geojson` | `TEXT` | YES | Valid GeoJSON polygon string | WGS 84 (EPSG:4326) boundary polygon. Approximate demo geometry. |
| `is_disputed` | `BOOLEAN` | NO | Default: `FALSE` | High-level flag denoting active conflict / injunction. |
| `provenance_label` | `VARCHAR(64)` | NO | Default: `'SYNTHETIC_DEMO_RECORD'` | Mandatory compliance watermark. |

---

### 2. `owners`
Fictional proprietor profile for citizens and legal entities.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `owner_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique proprietor identifier (e.g., `OWN-000001` to `OWN-020000`). |
| `fictional_name` | `VARCHAR(128)` | NO | `NOT NULL` | Authentic fictional Bengali name (e.g. 'মো: রফিকুল ইসলাম'). |
| `synthetic_nid_hash` | `CHAR(64)` | NO | `UNIQUE` | SHA-256 hash of fictional 10/17-digit number prefixed with `SYNTH-`. |
| `contact_masked` | `VARCHAR(24)` | YES | Format: `+8801700-00XXXX` | Fictional masked non-contactable telephone format. |
| `provenance_label` | `VARCHAR(64)` | NO | Default: `'FICTIONAL_CITIZEN_RECORD'` | Mandatory compliance watermark. |

---

### 3. `parcel_ownership`
Temporal many-to-many ledger tracking fractional parcel ownership shares over time.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `ownership_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique ownership entry key (`POW-XXXXXX`). |
| `parcel_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> parcels(parcel_id)` | Link to target plot. |
| `owner_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> owners(owner_id)` | Link to proprietor. |
| `ownership_share` | `NUMERIC(6, 4)` | NO | `CHECK (ownership_share > 0.0 AND ownership_share <= 1.0)` | Fractional ownership share (e.g. 0.5000 = 50% / 8 annas). |
| `valid_from` | `DATE` | NO | Format: `YYYY-MM-DD` | Date ownership commenced. |
| `valid_to` | `DATE` | YES | Format: `YYYY-MM-DD` | Date ownership ceased (`NULL` indicates currently active owner). |
| `source_event_id` | `VARCHAR(32)` | YES | `FOREIGN KEY -> ownership_events(event_id)` | Audit trail linkage to deed or inheritance event. |

---

### 4. `deeds`
Sub-Registry Office registered conveyance instruments.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `deed_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique deed key (`DEED-XXXXXX`). |
| `deed_number` | `VARCHAR(32)` | NO | `UNIQUE` | Registration serial number (e.g. `10482/2024`). |
| `sub_registry_office` | `VARCHAR(64)` | NO | Default: `'Savar Sub-Registry'` | Jurisdiction of registration. |
| `deed_type` | `VARCHAR(32)` | NO | `CHECK (deed_type IN ('SAF_KABALA', 'HEBA', 'BANTANNAMA', 'MORTGAGE'))` | Legal conveyance classification. |
| `parcel_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> parcels(parcel_id)` | Subject land plot. |
| `seller_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> owners(owner_id)` | Transferor / Seller. |
| `buyer_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> owners(owner_id)` | Transferee / Buyer. |
| `execution_date` | `DATE` | NO | `execution_date <= registration_date` | Date signed before deed writer and witnesses. |
| `registration_date` | `DATE` | NO | Format: `YYYY-MM-DD` | Official Sub-Registry volume entry date. |
| `declared_area` | `NUMERIC(10, 2)` | NO | `CHECK (declared_area > 0.0)` | Area in decimals stated in deed schedule (তফসিল). |
| `deed_value_bdt` | `NUMERIC(14, 2)` | NO | `CHECK (deed_value_bdt >= 0.0)` | Consideration value in Bangladeshi Taka. |
| `deed_status` | `VARCHAR(32)` | NO | `CHECK (deed_status IN ('REGISTERED', 'DISPUTED', 'CANCELLED_BY_COURT'))` | Status of deed instrument. |
| `document_id` | `VARCHAR(32)` | YES | `FOREIGN KEY -> documents(document_id)` | Link to synthetic digital scanned deed copy. |

---

### 5. `transactions`
Financial and administrative settlement record linked to deed registration.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `transaction_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique transaction key (`TXN-XXXXXX`). |
| `parcel_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> parcels(parcel_id)` | Subject plot. |
| `deed_id` | `VARCHAR(32)` | NO | `UNIQUE, FOREIGN KEY -> deeds(deed_id)` | Registered deed instrument. |
| `seller_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> owners(owner_id)` | Seller. |
| `buyer_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> owners(owner_id)` | Buyer. |
| `transaction_date` | `DATE` | NO | Format: `YYYY-MM-DD` | Settlement date. |
| `status` | `VARCHAR(32)` | NO | `CHECK (status IN ('COMPLETED', 'SUSPENDED', 'FLAGGED_FRAUD'))` | Registry transaction status. |
| `mutation_link_status` | `VARCHAR(32)` | NO | `CHECK (mutation_link_status IN ('UNLINKED', 'MUTATION_PENDING', 'MUTATED'))` | Synchronization status with AC Land e-mutation. |

---

### 6. `ownership_events`
Immutable historical event ledger tracking all transitions of title.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `event_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique event key (`EVT-XXXXXX`). |
| `parcel_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> parcels(parcel_id)` | Subject plot. |
| `previous_owner_id` | `VARCHAR(32)` | YES | `FOREIGN KEY -> owners(owner_id)` | Previous owner (`NULL` for initial ROR creation). |
| `new_owner_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> owners(owner_id)` | Acquirer / New owner. |
| `deed_id` | `VARCHAR(32)` | YES | `FOREIGN KEY -> deeds(deed_id)` | Supporting conveyance (`NULL` for inheritance/acquisition). |
| `event_date` | `DATE` | NO | Format: `YYYY-MM-DD` | Effective date of event. |
| `event_type` | `VARCHAR(32)` | NO | `CHECK (event_type IN ('SALE_DEED', 'INHERITANCE_FARAYEZ', 'AUCTION_GOV', 'ACQUISITION'))` | Legal category of transition. |
| `verification_status` | `VARCHAR(32)` | NO | `CHECK (verification_status IN ('VERIFIED', 'CONCURRENT_CONFLICT', 'INVESTIGATION_PENDING'))` | Audit verification status. |

---

### 7. `mutation_records`
Assistant Commissioner (Land) e-Mutation cases.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `mutation_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique mutation key (`MUT-XXXXXX`). |
| `case_number` | `VARCHAR(64)` | NO | `UNIQUE` | Official case pattern: `M-YYYY-UPAZILA-XXXXX`. |
| `parcel_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> parcels(parcel_id)` | Subject plot. |
| `deed_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> deeds(deed_id)` | Registered deed submitted for mutation. |
| `applicant_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> owners(owner_id)` | Citizen applicant (buyer). |
| `application_date` | `DATE` | NO | Format: `YYYY-MM-DD` | Filing date at AC Land office. |
| `status` | `VARCHAR(32)` | NO | `CHECK (status IN ('SUBMITTED', 'ULAO_INSPECTION', 'HEARING_DCR_PENDING', 'APPROVED', 'REJECTED'))` | 4-stage mutation process. |
| `decision_date` | `DATE` | YES | `decision_date >= application_date` | Date final order signed. |
| `mutated_khatian_no` | `INTEGER` | YES | `CHECK (mutated_khatian_no > 0)` | New Khatian number created upon approval. |

---

### 8. `documents`
Scanned digital document metadata, cryptographic SHA-256 hashes, and OCR extracts.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `document_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique document key (`DOC-XXXXXX`). |
| `parcel_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> parcels(parcel_id)` | Related plot. |
| `deed_id` | `VARCHAR(32)` | YES | `FOREIGN KEY -> deeds(deed_id)` | Related deed instrument (if applicable). |
| `document_type` | `VARCHAR(32)` | NO | `CHECK (document_type IN ('DEED_COPY', 'CS_KHATIAN', 'RS_KHATIAN', 'BS_PORCHA', 'MUTATION_CERT', 'DAKHILA'))` | Statutory document category. |
| `file_path` | `VARCHAR(255)` | NO | Relative filesystem path | Local path to generated synthetic file. |
| `sha256_hash` | `CHAR(64)` | NO | `CHECK (length(sha256_hash) = 64)` | Cryptographic SHA-256 checksum of actual file bytes. |
| `qr_token` | `VARCHAR(128)` | YES | Unique token string | Cryptographic verification token. |
| `ocr_status` | `VARCHAR(32)` | NO | `CHECK (ocr_status IN ('NOT_RUN', 'SUCCESS', 'PARTIAL_CONFIDENCE', 'LANGUAGE_PACK_UNAVAILABLE', 'FAILED'))` | Honest engine execution status. |
| `extracted_fields_json`| `TEXT` | YES | JSON formatted string | Structured Khatian/Dag/Owner data extracted by OCR. |
| `provenance_label` | `VARCHAR(64)` | NO | Default: `'SYNTHETIC_DEMO_DOCUMENT'` | Watermark on document canvas. |

---

### 9. `tax_records`
Land Development Tax compliance and Dakhila payment status.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `tax_record_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique tax record key (`TAX-XXXXXX`). |
| `parcel_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> parcels(parcel_id)` | Assessed plot. |
| `holding_number` | `VARCHAR(64)` | NO | Realistic holding format | Union Land Office holding identifier. |
| `tax_year` | `VARCHAR(16)` | NO | Format: `1430-1431` | Bengali fiscal year. |
| `assessed_amount` | `NUMERIC(10, 2)` | NO | `CHECK (assessed_amount >= 0.0)` | Total tax assessed in BDT. |
| `paid_amount` | `NUMERIC(10, 2)` | NO | `CHECK (paid_amount >= 0.0 AND paid_amount <= assessed_amount)` | Total tax paid in BDT. |
| `dakhila_number` | `VARCHAR(64)` | YES | Unique Dakhila serial | Populated upon payment. |
| `payment_status` | `VARCHAR(16)` | NO | `CHECK (payment_status IN ('PAID', 'ARREARS_DUE', 'EXEMPTED'))` | LDTax compliance status. |

---

### 10. `litigation_records`
Civil court title suits and temporary injunctions.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `case_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique litigation key (`LIT-XXXXXX`). |
| `parcel_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> parcels(parcel_id)` | Litigated plot. |
| `court_name` | `VARCHAR(128)` | NO | Realistic civil court | Jurisdiction (e.g. Senior Assistant Judge Court, Savar). |
| `case_number` | `VARCHAR(64)` | NO | Realistic case serial | e.g. `Title Suit No. 84/2023`. |
| `dispute_type` | `VARCHAR(32)` | NO | `CHECK (dispute_type IN ('TITLE_DECLARATION', 'PARTITION_DISPUTE', 'INJUNCTION_AGAINST_SALE', 'ADVERSE_POSSESSION'))` | Subject matter of dispute. |
| `filing_date` | `DATE` | NO | Format: `YYYY-MM-DD` | Date suit instituted. |
| `status` | `VARCHAR(32)` | NO | `CHECK (status IN ('ACTIVE_INJUNCTION_STAY', 'DISMISSED', 'DECREED'))` | Status of litigation. |

---

### 11. `khas_records`
Government 1-No Khas land schedule.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `khas_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique khas record key (`KHS-XXXXXX`). |
| `parcel_id` | `VARCHAR(32)` | NO | `UNIQUE, FOREIGN KEY -> parcels(parcel_id)` | Target public plot. |
| `khas_category` | `VARCHAR(32)` | NO | `CHECK (khas_category IN ('1_NO_GOVERNMENT_KHAS', 'RIVER_CANAL_WATERBODY', 'VESTED_PROPERTY', 'FORESHORE'))` | Statutory public land classification. |
| `managing_authority` | `VARCHAR(64)` | NO | Default: `'COLLECTOR_DHAKA'` | Deputy Commissioner, Dhaka. |
| `is_protected` | `BOOLEAN` | NO | Default: `TRUE` | Private transfer strictly illegal. |

---

### 12. `acquisition_zones`
Gazetted public infrastructure acquisition corridors (ARIPA 2017).

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `zone_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique zone key (`ACQ-XXXXXX`). |
| `project_name` | `VARCHAR(128)` | NO | Development project | e.g. `Dhaka-Aricha Highway 8-Lane Expansion Project`. |
| `gazette_notification_no` | `VARCHAR(64)` | NO | `UNIQUE` | Official Section 4 gazette serial. |
| `corridor_geojson` | `TEXT` | NO | Valid GeoJSON polygon | Spatial polygon of acquisition zone in Savar. |
| `status` | `VARCHAR(32)` | NO | `CHECK (status IN ('SECTION_4_NOTIFIED', 'SECTION_7_VERIFIED', 'SECTION_8_AWARDED'))` | Stage under ARIPA 2017. |

---

### 13. `verification_cases`
Automated audit findings and explainable risk triage cases.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `case_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique case key (`CASE-XXXXXX`). |
| `parcel_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> parcels(parcel_id)` | Evaluated plot. |
| `finding_code` | `VARCHAR(32)` | NO | Controlled: `DS-01`, `DS-02`, `DS-03`, `DS-04`, `DS-05`, `P6-ENCROACH` | Detection rule code. |
| `severity` | `VARCHAR(16)` | NO | `CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))` | Risk triage severity. |
| `risk_score` | `INTEGER` | NO | `CHECK (risk_score >= 0 AND risk_score <= 100)` | Explainable risk score (0 to 100). |
| `explanation_bn` | `TEXT` | NO | Bengali plain text | Clear rationale in Bengali. |
| `explanation_en` | `TEXT` | NO | English plain text | Clear rationale in English. |
| `evidence_references` | `TEXT` | NO | JSON array of IDs | Supporting deed IDs, transaction IDs, hashes. |
| `review_status` | `VARCHAR(32)` | NO | `CHECK (review_status IN ('PENDING_REVIEW', 'UNDER_INVESTIGATION', 'ESCALATED', 'RESOLVED_CLEARED'))` | Officer queue status. |

---

### 14. `review_logs`
Tamper-evident officer action logs and audit trail.

| Column | Data Type | Nullable | Constraints & Defaults | Description & Business Rules |
|---|---|---|---|---|
| `log_id` | `VARCHAR(32)` | NO | `PRIMARY KEY` | Unique log entry key (`LOG-XXXXXX`). |
| `case_id` | `VARCHAR(32)` | NO | `FOREIGN KEY -> verification_cases(case_id)` | Finding reviewed. |
| `reviewer_id` | `VARCHAR(64)` | NO | Authorized officer ID | e.g. `OFFICER-SAVAR-01`. |
| `action` | `VARCHAR(32)` | NO | `CHECK (action IN ('APPROVED_LEGITIMATE', 'REJECTED_FRAUD_FLAG', 'REQUESTED_PHYSICAL_INSPECTION'))` | Officer decision. |
| `reason` | `TEXT` | NO | Officer justification | Mandatory review explanation. |
| `timestamp` | `TIMESTAMP` | NO | ISO 8601 UTC | Tamper-evident action time. |
