# ENTITY-RELATIONSHIP DESIGN (ERD) & RELATIONAL ARCHITECTURE
## DESHMRITTIKA / BHUMI-SYNC
**Document Version:** 1.0.0 (Phase 1 Baseline)  
**Date:** October 17, 2026  
**Scope:** Unified Relational Architecture Supporting Tracks P1 through P6.

---

## 1. Visual Entity-Relationship Diagram (Mermaid)

```mermaid
erDiagram
    parcels ||--o{ parcel_ownership : "has temporal owners"
    owners ||--o{ parcel_ownership : "holds temporal share in"
    
    parcels ||--o{ deeds : "subject of conveyance"
    owners ||--o{ deeds : "acts as seller"
    owners ||--o{ deeds : "acts as buyer"
    
    deeds ||--o{ transactions : "settles"
    parcels ||--o{ transactions : "transfers"
    owners ||--o{ transactions : "transacts as seller"
    owners ||--o{ transactions : "transacts as buyer"
    
    parcels ||--o{ ownership_events : "records history for"
    owners ||--o{ ownership_events : "previous owner"
    owners ||--o{ ownership_events : "new owner"
    deeds ||--o{ ownership_events : "authorized by"
    
    deeds ||--o{ mutation_records : "triggers mutation"
    parcels ||--o{ mutation_records : "mutated on"
    owners ||--o{ mutation_records : "applied by"
    
    parcels ||--o{ documents : "associated with"
    deeds ||--o{ documents : "contains scan of"
    
    parcels ||--o{ tax_records : "assessed under"
    parcels ||--o{ litigation_records : "encumbered by"
    parcels ||--o{ khas_records : "classified as"
    
    parcels ||--o{ verification_cases : "evaluated by"
    verification_cases ||--o{ review_logs : "reviewed via"

    parcels {
        string parcel_id PK
        string district
        string upazila
        string mouza
        int jl_number
        int dag_number
        int khatian_number
        string survey_type
        string land_classification
        float area_decimal
        text coordinates_geojson
        boolean is_disputed
        string provenance_label
    }

    owners {
        string owner_id PK
        string fictional_name
        string synthetic_nid_hash
        string contact_masked
        string provenance_label
    }

    parcel_ownership {
        string ownership_id PK
        string parcel_id FK
        string owner_id FK
        float ownership_share
        date valid_from
        date valid_to
        string source_event_id FK
    }

    deeds {
        string deed_id PK
        string deed_number
        string sub_registry_office
        string deed_type
        string parcel_id FK
        string seller_id FK
        string buyer_id FK
        date execution_date
        date registration_date
        float declared_area
        float deed_value_bdt
        string deed_status
        string document_id FK
    }

    transactions {
        string transaction_id PK
        string parcel_id FK
        string deed_id FK
        string seller_id FK
        string buyer_id FK
        date transaction_date
        string status
        string mutation_link_status
    }

    ownership_events {
        string event_id PK
        string parcel_id FK
        string previous_owner_id FK
        string new_owner_id FK
        string deed_id FK
        date event_date
        string event_type
        string verification_status
    }

    mutation_records {
        string mutation_id PK
        string case_number
        string parcel_id FK
        string deed_id FK
        string applicant_id FK
        date application_date
        string status
        date decision_date
        int mutated_khatian_no
    }

    documents {
        string document_id PK
        string parcel_id FK
        string deed_id FK
        string document_type
        string file_path
        string sha256_hash
        string qr_token
        string ocr_status
        text extracted_fields_json
        string provenance_label
    }

    tax_records {
        string tax_record_id PK
        string parcel_id FK
        string holding_number
        string tax_year
        float assessed_amount
        float paid_amount
        string dakhila_number
        string payment_status
    }

    litigation_records {
        string case_id PK
        string parcel_id FK
        string court_name
        string case_number
        string dispute_type
        date filing_date
        string status
    }

    khas_records {
        string khas_id PK
        string parcel_id FK
        string khas_category
        string managing_authority
        boolean is_protected
    }

    acquisition_zones {
        string zone_id PK
        string project_name
        string gazette_notification_no
        text corridor_geojson
        string status
    }

    verification_cases {
        string case_id PK
        string parcel_id FK
        string finding_code
        string severity
        int risk_score
        string explanation_bn
        string explanation_en
        text evidence_references
        string review_status
    }

    review_logs {
        string log_id PK
        string case_id FK
        string reviewer_id
        string action
        text reason
        datetime timestamp
    }
```

---

## 2. Relational Cardinality & Cascade Integrity Rules

| Parent Entity | Child Entity | Cardinality | Foreign Key Constraint | Delete / Cascade Behavior | Business & Integrity Rule |
|---|---|---|---|---|---|
| `parcels` | `parcel_ownership` | 1 to Many (1:N) | `parcel_ownership.parcel_id` | `RESTRICT` | A parcel cannot be deleted if historical ownership records exist. |
| `owners` | `parcel_ownership` | 1 to Many (1:N) | `parcel_ownership.owner_id` | `RESTRICT` | An owner profile cannot be purged while holding active or historical shares. |
| `parcels` | `deeds` | 1 to Many (1:N) | `deeds.parcel_id` | `RESTRICT` | Preserves all registered deeds associated with the parcel across history. |
| `parcels` | `transactions` | 1 to Many (1:N) | `transactions.parcel_id` | `RESTRICT` | Financial audit ledger cannot have orphan transactions. |
| `deeds` | `transactions` | 1 to 1 (1:1) | `transactions.deed_id` | `RESTRICT` | Every registered deed maps to exactly one registry transaction settlement. |
| `deeds` | `mutation_records` | 1 to Many (1:N) | `mutation_records.deed_id` | `RESTRICT` | Links deed to its subsequent e-mutation application(s). |
| `parcels` | `documents` | 1 to Many (1:N) | `documents.parcel_id` | `CASCADE` | Scanned legacy khatians, deeds, and receipts belong to the parcel dossier. |
| `deeds` | `documents` | 1 to 1 (1:1) | `deeds.document_id` | `SET NULL` | A deed references its scanned digital facsimile. |
| `parcels` | `tax_records` | 1 to Many (1:N) | `tax_records.parcel_id` | `CASCADE` | Annual tax assessment history per plot. |
| `parcels` | `litigation_records`| 1 to Many (1:N) | `litigation_records.parcel_id`| `CASCADE` | Active civil injunctions and title disputes encumbering the parcel. |
| `parcels` | `khas_records` | 1 to 1 (1:1) | `khas_records.parcel_id` | `CASCADE` | Denotes state 1-No Khas land schedule. |
| `parcels` | `verification_cases`| 1 to Many (1:N) | `verification_cases.parcel_id`| `CASCADE` | Automated double-selling and anomaly audit findings. |
| `verification_cases`| `review_logs`| 1 to Many (1:N) | `review_logs.case_id` | `RESTRICT` | Tamper-evident reviewer audit trail; logs cannot be purged. |

---

## 3. Database Indexes for High-Performance Queries

To ensure rapid sub-second query performance at scale (100,000 parcels and ~500,000 relational links):

1. **Spatial & Search Indexes:**
   - `idx_parcels_mouza_dag_khatian`: `parcels(mouza, dag_number, khatian_number)` — primary search composite index.
   - `idx_parcels_upazila`: `parcels(upazila, district)` — administrative filtering.
2. **Double-Selling Detection Indexes:**
   - `idx_deeds_parcel_seller`: `deeds(parcel_id, seller_id, execution_date)` — detects concurrent transfers by the same seller.
   - `idx_deeds_deed_number`: `deeds(deed_number)` — unique deed registration index.
   - `idx_mutation_deed`: `mutation_records(deed_id, status)` — detects unmutated deed transfers.
3. **Citizen Due Diligence Indexes:**
   - `idx_tax_parcel_status`: `tax_records(parcel_id, payment_status)` — instantaneous tax arrears check.
   - `idx_litigation_parcel`: `litigation_records(parcel_id, status)` — instantaneous active court injunction check.
   - `idx_khas_parcel`: `khas_records(parcel_id, is_protected)` — instantaneous public land protection flag.
4. **Cryptographic Integrity Indexes:**
   - `idx_documents_sha256`: `documents(sha256_hash)` — hash lookup to prevent duplicate file re-uploads or identify file tampering.
