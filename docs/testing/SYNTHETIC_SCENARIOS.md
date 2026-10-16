# SYNTHETIC SCENARIO SPECIFICATION & TESTING CATALOG
## Ground-Truth Scenarios for LandTech Rulebook Tracks (P1 through P6)
**Project:** DESHMRITTIKA / BHUMI-SYNC (দেশমৃত্তিকা)  
**Document Version:** 1.0.0 (Phase 2B Baseline)  
**Date:** October 17, 2026  
**Seed:** `20261018` | **Dataset Scale:** 100,000 Parcels  

---

## 1. Scenario Taxonomy & Ground Truth Matrix

The synthetic dataset incorporates balanced positive and negative control scenarios across all six LandTech tracks:

| Scenario Code | Track | Scenario Name | Category | Sample Parcel Range | Target Volume | Expected Engine Determination | Risk Level |
|---|---|---|---|---|---|---|---|
| **`SCN-DS1`** | **P3** | **Active Double-Selling (Concurrent Unmutated Transfers)** | Ground Truth Fraud | `BD-PAR-000101` to `BD-PAR-000600` | **Exactly 500** | `DETECTED_FRAUD_CRITICAL`: Prior deed mutation unfiled/pending; second deed executed. | `CRITICAL` (Score 90–95) |
| **`SCN-DS2`** | **P3** | **Clean Sequential Resales (Negative Control)** | Legitimate Clean | `BD-PAR-001001` to `BD-PAR-016000` | **15,000** | `VERIFIED_CLEAR`: Title chain verified through successive approved mutations. | `CLEAR` (Score 0) |
| **`SCN-DS3`** | **P3** | **Area Over-Sale Discrepancy** | Mathematical Conflict | `BD-PAR-016001` to `BD-PAR-016250` | **250** | `AREA_DISCREPANCY_FLAG`: Transferred area exceeds ROR recorded plot size. | `HIGH` (Score 75) |
| **`SCN-DS4`** | **P2, P3**| **Duplicate Document Re-Upload (Negative Control)**| Integrity Check | `BD-PAR-016251` to `BD-PAR-016450` | **200** | `DUPLICATE_FILE_DETECTED`: Same SHA-256 hash; classified as duplicate filing, not a second sale. | `LOW` (Score 10) |
| **`SCN-DS5`** | **P5** | **Tax Arrears Default (> 3 Years)** | Statutory Encumbrance | `BD-PAR-016451` to `BD-PAR-017450` | **1,000** | `TAX_DEFAULT_WARNING`: Unpaid LDTax arrears halt automatic mutation. | `MEDIUM` (Score 40) |
| **`SCN-LIT`** | **P5** | **Civil Court Title Dispute & Injunction** | Judicial Encumbrance | `BD-PAR-017451` to `BD-PAR-018950` | **1,500** | `COURT_INJUNCTION_STAY`: Active title suit with temporary injunction. | `MEDIUM` (Score 45) |
| **`SCN-KHS`** | **P6** | **Government 1-No Khas Land Encroachment** | Public Asset Protection | `BD-PAR-018951` to `BD-PAR-020450` | **1,500** | `GOVERNMENT_KHAS_PROHIBITED`: State-owned land; private sale is void ab initio. | `CRITICAL` (Score 90) |
| **`SCN-ACQ`** | **P6** | **Infrastructure Acquisition Corridor Buffer** | Corridor Protection | `BD-PAR-020451` to `BD-PAR-021500` | **1,050** | `ACQUISITION_CORRIDOR_ENCROACHMENT`: Intersects gazetted ARIPA Section 4 highway zone. | `HIGH` (Score 70) |
| **`SCN-NORM`**| **P5** | **Normal Clean Single-Owner Plots** | Standard Baseline | `BD-PAR-021501` to `BD-PAR-100000` | **78,500** | `VERIFIED_CLEAR`: Clean holding, paid tax, no litigation. | `CLEAR` (Score 0) |

---

## 2. Controlled Double-Selling Scenario Logic (SCN-DS1)

The 500 double-selling cases simulate the authentic administrative vulnerability between the Sub-Registry and AC Land offices:
1. **Initial State:** Fictional citizen $S_i$ holds active ownership in parcel $P_i$.
2. **Deed 1 Execution:** On Date $T_1$, $S_i$ executes a Saf-Kabala deed $D_{i,1}$ to Buyer $B_{i,1}$. The deed is registered at Savar Sub-Registry.
3. **Mutation Pending:** Buyer $B_{i,1}$ applies for mutation at Savar AC Land office. The case is logged with status `SUBMITTED` or `ULAO_INSPECTION`. The Record of Rights has not yet been altered.
4. **Fraudulent Deed 2 Execution:** On Date $T_2$ ($T_2 > T_1$, typically 30 to 90 days later), Seller $S_i$, presenting an outdated copy of the original unmutated Khatian, executes Deed $D_{i,2}$ to an unsuspecting second buyer $B_{i,2}$ for the same land.
5. **Verification Engine Rule:** The engine checks whether the seller attempted to transfer the same parcel share while a prior deed's mutation remains pending or unresolved. It triggers:
   - Rule Code: `DS-01`
   - Severity: `CRITICAL`
   - Risk Score: `95`
   - Status: `PENDING_REVIEW` (Officer Triage Queue)

---

## 3. Negative Control Architecture

To ensure the system avoids false-positive hysteria:
1. **Legitimate Resale (`SCN-DS2`):** In a healthy property market, land is bought and subsequently resold. The engine requires that between Deed 1 (Owner 1 $\rightarrow$ Owner 2) and Deed 2 (Owner 2 $\rightarrow$ Owner 3), a completed and approved mutation exists (`status = 'APPROVED'`). When this condition is met, the engine awards a `0` risk score and marks the title chain as `CLEAR`.
2. **Duplicate Uploads (`SCN-DS4`):** When a citizen uploads the same scanned deed twice, the SHA-256 hash matches an existing record for that transaction. The engine distinguishes this clerical duplication from a second sale and assigns a minimal triage score of `10` (`INFO`).
