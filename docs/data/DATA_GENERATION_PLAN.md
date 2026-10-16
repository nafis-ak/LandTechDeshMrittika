# SYNTHETIC DATASET GENERATION PLAN (100,000 PARCELS)
## Authentic, Source-Informed Multi-Track Dataset Architecture
**Project:** DESHMRITTIKA / BHUMI-SYNC (দেশমৃত্তিকা)  
**Document Version:** 1.0.0 (Phase 1 Baseline)  
**Date:** October 17, 2026  
**Target Output:** 100,000 synthetic parcels, ~20,000 fictional owners, 500 controlled double-selling test scenarios, and millions of relational links supporting P1 through P6.

---

## 1. Generation Principles & Safety Constraints

1. **Authentic Structure, Synthetic Identity:**
   - Every column name, survey hierarchy, and mutation lifecycle strictly follows documented Bangladesh land administration rules (SATA 1950, Registration Act 1908, LDTax guidelines).
   - All citizen identities, telephone numbers, and NIDs are 100% fictional. Real citizens' names or government NIDs are strictly excluded.
2. **Deterministic Reproducibility:**
   - The generator runs from a fixed seed (`GENERATOR_SEED = 20261018`).
   - Re-running the pipeline produces identical primary keys, coordinates, dates, and test scenarios.
3. **Phased Validation Gate:**
   - **Step 1 (Dry-Run):** 1,000 parcels and 200 owners validated against foreign keys and rule engines.
   - **Step 2 (Full-Scale):** 100,000 parcels generated only after the dry-run passes all constraints.
4. **Relational Integrity Over Arbitrary Rows:**
   - Every deed references an existing parcel and valid seller.
   - Every transaction matches a registered deed.
   - Every mutation references a real deed applicant.
   - Area sums per parcel never violate mathematical limits unless explicitly seeded in a controlled over-sale scenario.

---

## 2. Target Scale & Entity Volume Allocation

| Entity Table | Target Record Count | Primary Jurisdiction Breakdown | Description & Linkage Rules |
|---|---|---|---|
| **`parcels`** | **100,000** | • Aminbazar Mouza (JL 12): 50,000<br>• Birulia Mouza (JL 24): 50,000 | Dag numbers 1 to 50,000 per mouza. Survey types distributed: BS_CITY (60%), RS (30%), SA (8%), CS (2%). |
| **`owners`** | **20,000** | Savar / Dhaka regional names | Fictional Bengali citizen profiles with masked contacts and synthetic NID hashes. |
| **`parcel_ownership`**| **~120,000** | Linked to parcels and owners | Temporal ownership shares (active and historical). Ownership shares sum exactly to 1.0000 per plot. |
| **`deeds`** | **~70,000** | Savar Sub-Registry Office | Registered Saf-Kabala, Heba, and partition deeds spanning years 1995 to 2026. |
| **`transactions`** | **~70,000** | 1:1 with registered deeds | Financial settlement and registry processing status. |
| **`ownership_events`** | **~85,000** | Chronological timeline | Immutable ledger of conveyances, inheritance distributions, and acquisitions. |
| **`mutation_records`** | **~60,000** | Savar AC Land Office | e-Mutation cases across the 4-stage lifecycle (Approved: 75%, Pending: 15%, Rejected: 10%). |
| **`documents`** | **~10,000** sample files | Scans & metadata | Synthetic physical files with SHA-256 hashes, QR tokens, and honest OCR statuses. |
| **`tax_records`** | **100,000** | Current & arrears fiscal years | Land development tax compliance (Paid: 80%, Due/Arrears: 18%, Exempted: 2%). |
| **`litigation_records`**| **~3,000** | Senior Assistant Judge Court, Savar | Active title injunctions and partition suits creating legal encumbrances. |
| **`khas_records`** | **~1,500** | Collector, Dhaka (১নং খাস) | Riverbeds, government khas plots, and vested property schedules. |
| **`acquisition_zones`** | **5** major projects | Dhaka-Aricha Corridor | Gazetted road widening, metro expansion, and bypass project polygons. |
| **`verification_cases`**| **~3,500** | Automated rule findings | 500 controlled double-selling cases + area discrepancies + tax/litigation alerts. |
| **`review_logs`** | **~1,000** | Officer review logs | Documented review decisions, escalations, and justifications. |

---

## 3. Seeded Test Scenario Specifications

To test all six LandTech rulebook tracks (P1–P6) with ground truth:

```
[Total Parcels: 100,000]
  ├── Normal Single-Owner Clean Plots (80,000 parcels)
  ├── Legitimate Historical Sequential Transfers [Negative Control DS-02] (14,000 parcels)
  ├── Active Double-Selling Scenarios [DS-01] (500 parcels - GROUND TRUTH FRAUD)
  ├── Area Over-Sale Discrepancies [DS-03] (250 parcels)
  ├── Duplicate Document Uploads [DS-04] (200 parcels)
  ├── Severe Tax Arrears & Default [DS-05] (1,000 parcels)
  ├── Active Civil Court Injunctions [P5 Litigated] (1,500 parcels)
  ├── Government Khas Land Encroachment [P6 Khas] (1,500 parcels)
  └── Infrastructure Acquisition Corridor Intersections [P6 Buffer] (1,050 parcels)
```

### Controlled Double-Selling Scenario (DS-01) Breakdown:
- **Seed Count:** Exactly 500 parcels.
- **Construction Logic:**
  1. Parcel $P_i$ owned by Seller $S_j$.
  2. Seller executes Deed $D_A$ to Buyer $B_1$ on Date $T_1$.
  3. While Mutation for $D_A$ remains unfiled or pending, Seller $S_j$ executes Deed $D_B$ to Buyer $B_2$ on Date $T_2$ ($T_2 > T_1$).
  4. Both deeds declare transfer of the same ownership share.
  5. The verification engine must flag $P_i$ with finding code `DS-01`, severity `CRITICAL`, and risk score `85–95`.

---

## 4. High-Performance Generation & Persistence Strategy

Generating 100,000 relational parcels and ~500,000 linked rows requires an optimized pipeline:
1. **Streaming Batches:**
   - Generator executes in chunks of 10,000 records.
   - Bulk inserts execute within SQLite single-transaction blocks (`BEGIN TRANSACTION ... COMMIT`).
2. **SQLite Performance Optimization:**
   - Execute `PRAGMA synchronous = OFF` and `PRAGMA journal_mode = MEMORY` during bulk creation.
   - Create indexes *after* data insertion to reduce B-tree re-balancing overhead.
   - Re-enable `PRAGMA journal_mode = WAL` and `PRAGMA synchronous = NORMAL` for application runtime.
3. **Artifact Outputs:**
   - Database: `data/generated/landtech_synthetic.db` (SQLite WAL engine).
   - Versioned CSV Exports: `data/generated/csv/*.csv` for data science and auditing.
   - Checksum Manifest: `data/generated/dataset_manifest.json` containing per-table row counts, schema version, generator seed, and SHA-256 hashes.
   - Validation Report: `reports/data_validation_report.md` recording integrity metrics.

---

## 5. Automated Data Validation Rules

The post-generation validation suite executes 12 automated checks:
1. **Primary Key Uniqueness:** Zero duplicate IDs across all 14 tables.
2. **Foreign Key Completeness:** Zero orphan records in `parcel_ownership`, `deeds`, `transactions`, `mutations`, `tax`, and `khas`.
3. **Temporal Consistency:** `deed.execution_date <= deed.registration_date <= mutation.application_date <= mutation.decision_date`.
4. **Ownership Share Invariance:** Sum of active ownership shares per parcel equals $\le 1.0000$.
5. **Coordinate Range Verification:** All parcel centroids fall within Savar pilot bounding box (Lat: 23.78 to 23.89, Lon: 90.28 to 90.355).
6. **Ground Truth Scenario Recall:** 100% of the 500 seeded `DS-01` double-selling cases are detected by the rule engine.
7. **Negative Control Precision:** Zero false-positive fraud flags on the 14,000 clean sequential conveyances (`DS-02`).
8. **Document Hash Integrity:** Every document file's SHA-256 matches its database entry; byte modification triggers mismatch.
