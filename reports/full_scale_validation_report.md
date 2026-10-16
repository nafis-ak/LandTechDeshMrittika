# FULL-SCALE DATASET VALIDATION REPORT (100,000 PARCELS)
## DESHMRITTIKA / BHUMI-SYNC — Phase 2B Validation
**Execution Date:** 2026-10-16T17:52:18.026812+00:00Z  
**Seed:** 20261018 | **Database:** `data/generated/full_scale/landtech_synthetic.db` (109.35 MB)  
**Overall Status:** **ALL CHECKS PASSED**  

---

### 1. Summary of Integrity Checks

| Check ID | Integrity Test Title | Status | Diagnostic Summary |
|---|---|---|---|
| **CHK-01** | Table Population & Scale | ✅ PASSED | All 14 tables populated. Parcels: 100,000, Owners: 20,000, Deeds: 58,333, Mutations: 57,583 |
| **CHK-02** | Primary Key Uniqueness | ✅ PASSED | Zero primary key collisions across all 14 tables (duplicate count = 0) |
| **CHK-03** | Foreign Key Integrity | ✅ PASSED | Tested 13 foreign key linkages. Total orphan records detected = 0 |
| **CHK-04** | Active Ownership Share Sum | ✅ PASSED | Active ownership shares sum <= 1.0000 across all parcels (violating parcels = 0) |
| **CHK-05** | Chronological Date Validity | ✅ PASSED | Deed execution precedes registration (errors: 0). Mutation application precedes decision (errors: 0). |
| **CHK-06** | Geospatial Bounding Box | ✅ PASSED | Sampled parcel polygons verified within Savar Pilot Bounding Box (out-of-bounds = 0) |
| **CHK-07** | DS-01 Double-Selling Rule Recall | ✅ PASSED | Engine captured 500/500 (100.0%) of seeded unmutated concurrent sales. |
| **CHK-08** | DS-02 Negative Control Precision | ✅ PASSED | Clean sequential conveyances flagged as fraud = 0 (False Positive Rate = 0.0%) |
| **CHK-09** | Synthetic Provenance Labeling | ✅ PASSED | All generated records carry mandatory compliance watermark (unlabeled records = 0) |
| **CHK-10** | SHA-256 Hash & Tamper Detection | ✅ PASSED | Verified 5/5 document files against disk bytes. Tamper detection caught 100% of single-byte modifications. |
| **CHK-11** | Actual Tesseract OCR Execution | ✅ PASSED | Pytesseract executed on generated deed image 'DOC-000001_SAVAR-20261018-00003.png'. Extracted tokens: 'SAVAR', 'DEED', 'SYNTHETIC'. |
| **CHK-12** | Dataset Manifest & Checksum Audit | ✅ PASSED | Manifest validated at data/generated/full_scale/dataset_manifest.json with seed 20261018 and recorded checksums. |

---

### 2. Table Row Count Verification

| Table Name | Row Count | Provenance Classification |
|---|---|---|
| `parcels` | 100,000 | `SYNTHETIC_DERIVED` |
| `owners` | 20,000 | `SYNTHETIC_DERIVED` |
| `parcel_ownership` | 128,500 | `SYNTHETIC_DERIVED` |
| `deeds` | 58,333 | `SYNTHETIC_DERIVED` |
| `transactions` | 58,333 | `SYNTHETIC_DERIVED` |
| `ownership_events` | 31,000 | `SYNTHETIC_DERIVED` |
| `mutation_records` | 57,583 | `SYNTHETIC_DERIVED` |
| `documents` | 51 | `SYNTHETIC_DERIVED` |
| `tax_records` | 100,000 | `SYNTHETIC_DERIVED` |
| `litigation_records` | 1,500 | `SYNTHETIC_DERIVED` |
| `khas_records` | 1,500 | `SYNTHETIC_DERIVED` |
| `acquisition_zones` | 5 | `SYNTHETIC_DERIVED` |
| `verification_cases` | 19,750 | `SYNTHETIC_DERIVED` |
| `review_logs` | 20 | `SYNTHETIC_DERIVED` |

---

### 3. Scenario Recall & Detection Metrics

- **Total Seeded DS-01 Double-Selling Scenarios:** 500
- **Successfully Detected by Rules Engine:** 500 (100.0% Recall)
- **Clean Sequential Negative Control Transfers (DS-02):** 15,000
- **False Positive Fraud Flags:** 0 (0.0% False Positive Rate)

---

### 4. Query Performance & Latency Benchmarks

| Benchmark Operation | Tested Sample | Average Latency | Performance Target |
|---|---|---|---|
| Universal Search (Dag & Mouza) | 50 random queries | **0.028 ms** | < 10.0 ms (Exceeded) |
| Search by Khatian Number | 50 random queries | **0.072 ms** | < 10.0 ms (Exceeded) |
| Double-Selling Rule Evaluation | 50 random parcels | **1.955 ms** | < 20.0 ms (Exceeded) |

---

### 5. OCR Pipeline Verification Output

**Tested File:** `data/generated/full_scale/documents/DOC-000001_SAVAR-20261018-00003.png`  
```
‘no prea mE (DEED_COPY}

SYNTHETIC DEMO DOCUMENTENOTAN OFFICIAL LAND RECORD

DOCUMENT ID: DoC-000001

PARCEL REF: BD-PAR-000003

DEED NUMBER SAVAR-20261018-00003,

DISTRICT. DHAKA UPAZILA SAVAR

MOUZA AMINBAZAR J.LNO.12

SCHEDULE: TRANSFEROF TITLE/ SAF-KABALACONVEVANCE

PROPERTY AREA 12.50 DECIMALS

CONSIDERATION VALUE BDT 4500.00,

SELLER FICTIONALCITIZEN A ~> BUYER FICTIONAL CITIZEN 8

(CRYPTOGRAPHIC INTEGRITY TOKEN: SHA256-SYNTH-DOC-000001,

VERIFICATION PORTAL:hitp//127.0.0.18000)verify
```

---

### 6. Comparison Against Dry-Run Baseline

| Metric | Phase 2A Dry-Run | Phase 2B Full-Scale | Growth Factor |
|---|---|---|---|
| Parcels | 1,000 | **100,000** | 100x |
| Owners | 200 | **20,000** | 100x |
| Double-Selling Scenarios | 10 | **500** | 50x |
| Database Size | 1.0 MB | **109.35 MB** | ~109x |
| Search Latency (Indexed) | 0.8 ms | **0.028 ms** | Sub-millisecond maintained |
