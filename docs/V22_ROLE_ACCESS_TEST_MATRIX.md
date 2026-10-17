# DESHMRITTIKA / BHUMI-SYNC v2.2 — Authoritative Role Access Test Matrix

**Project:** DeshMrittika / BHUMI-SYNC v2.2  
**Verification Target:** 4-Role RBAC Authorization & Separation of Duties  
**Workspace:** `/Users/macbookair/Desktop/LandTechDeshMrittika`  
**Execution Timestamp:** 2026-10-17 17:35:36 UTC+6  
**Status:** **33 of 33 Matrix Test Assertions Verified (100% OK)**  

---

## 1. Complete Role-by-Role API Authorization Matrix

| # | Role Tested | HTTP Method | Endpoint Path | Expected HTTP Status | Observed HTTP Status | Result | Enforcement Guard / Mechanism | Attributable Audit Log |
| :---: | :--- | :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| **CITIZEN (সাধারণ নাগরিক)** | | | | | | | | |
| 1 | `CITIZEN` | GET | `/api/v1/citizen/my-parcels` | 200 | 200 | **PASS** | `require_citizen_access` + `cp.user_id = ?` | Reads own linked parcels |
| 2 | `CITIZEN` | GET | `/api/v1/citizen/my-applications` | 200 | 200 | **PASS** | `require_citizen_access` + `ca.user_id = ?` | Reads own applications |
| 3 | `CITIZEN` | POST | `/api/v1/citizen/applications` | 200 | 200 | **PASS** | `require_citizen_access` + parcel check | Creates simulated mutation app + sends notice |
| 4 | `CITIZEN` | GET | `/api/v1/citizen/my-notifications` | 200 | 200 | **PASS** | `require_citizen_access` + `user_id = ?` | Reads personal notifications |
| 5 | `CITIZEN` | GET | `/api/v1/citizen/my-activity` | 200 | 200 | **PASS** | `require_citizen_access` | Reads security audit log events |
| 6 | `CITIZEN` | GET | `/api/v1/officer/queue` | 403 | 403 | **PASS** | `require_officer_role` | Forbidden: Cannot access officer triage |
| 7 | `CITIZEN` | GET | `/api/v1/admin/users` | 403 | 403 | **PASS** | `require_admin_role` | Forbidden: Cannot access admin user management |
| 8 | `CITIZEN` | POST | `/api/v1/officer/decision` | 403 | 403 | **PASS** | `require_officer_role` | Forbidden: Cannot record officer decisions |
| **BUYER (সম্ভাব্য ক্রেতা)** | | | | | | | | |
| 9 | `BUYER` | GET | `/api/v1/search?dag_no=101` | 200 | 200 | **PASS** | Public cadastral search (sanitized) | Search parcel records |
| 10 | `BUYER` | GET | `/api/v1/due-diligence/BD-PAR-000101` | 200 | 200 | **PASS** | `require_authenticated_user` | 5-factor risk score dossier |
| 11 | `BUYER` | GET | `/api/v1/parcels/BD-PAR-000101/geojson` | 200 | 200 | **PASS** | Public GeoJSON projection | Cadastral boundary coordinates |
| 12 | `BUYER` | POST | `/api/v1/buyer/review-requests` | 200 | 200 | **PASS** | `require_buyer_access` | Submits parcel review request to officer |
| 13 | `BUYER` | GET | `/api/v1/buyer/review-requests` | 200 | 200 | **PASS** | `require_buyer_access` + `buyer_id = ?` | Lists buyer's own review requests |
| 14 | `BUYER` | GET | `/api/v1/citizen/my-parcels` | 403 | 403 | **PASS** | `require_citizen_access` | Forbidden: Cannot view private landowner data |
| 15 | `BUYER` | GET | `/api/v1/citizen/my-applications` | 403 | 403 | **PASS** | `require_citizen_access` | Forbidden: Cannot view private applications |
| 16 | `BUYER` | GET | `/api/v1/officer/queue` | 403 | 403 | **PASS** | `require_officer_role` | Forbidden: Cannot access officer queue |
| 17 | `BUYER` | GET | `/api/v1/admin/users` | 403 | 403 | **PASS** | `require_admin_role` | Forbidden: Cannot access admin user management |
| **AC LAND / OFFICER (সহকারী কমিশনার–ভূমি)** | | | | | | | | |
| 18 | `OFFICER` | GET | `/api/v1/officer/queue` | 200 | 200 | **PASS** | `require_officer_role` | Savar triage queue cases |
| 19 | `OFFICER` | GET | `/api/v1/officer/assigned-applications`| 200 | 200 | **PASS** | `require_officer_role` | Assigned e-mutation applications |
| 20 | `OFFICER` | POST | `/api/v1/officer/decision` | 200 | 200 | **PASS** | `require_officer_role` + `case_id` lookup | Inserts `review_logs` record with reviewer ID |
| 21 | `OFFICER` | POST | `/api/v1/officer/hearing-schedule` | 200 | 200 | **PASS** | `require_officer_role` + `app_id` lookup | Updates hearing date + creates citizen notice |
| 22 | `OFFICER` | GET | `/api/v1/officer/audit-logs` | 200 | 200 | **PASS** | `require_officer_role` | Attributable audit log of decisions |
| 23 | `OFFICER` | GET | `/api/v1/admin/users` | 403 | 403 | **PASS** | `require_admin_role` | Forbidden: Officers cannot manage system users |
| 24 | `OFFICER` | GET | `/api/v1/admin/diagnostics` | 403 | 403 | **PASS** | `require_admin_role` | Forbidden: Officers cannot view system diagnostics |
| **SYSTEM ADMINISTRATOR (সিস্টেম অ্যাডমিন)** | | | | | | | | |
| 25 | `ADMIN` | GET | `/api/v1/admin/users` | 200 | 200 | **PASS** | `require_admin_role` | Lists all platform users |
| 26 | `ADMIN` | GET | `/api/v1/admin/security-logs` | 200 | 200 | **PASS** | `require_admin_role` | Immutable security audit logs |
| 27 | `ADMIN` | GET | `/api/v1/admin/diagnostics` | 200 | 200 | **PASS** | `require_admin_role` | Operational health and table counts |
| 28 | `ADMIN` | GET | `/api/v1/admin/ocr-health` | 200 | 200 | **PASS** | `require_admin_role` | Tesseract OCR & Bengali pack health |
| 29 | `ADMIN` | GET | `/api/v1/admin/fraud-rules` | 200 | 200 | **PASS** | `require_admin_role` | Versioned rule catalog (DS-01, DS-02, etc.) |
| 30 | `ADMIN` | POST | `/api/v1/admin/backups/checkpoint` | 200 | 200 | **PASS** | `require_admin_role` | Triggers SQLite WAL checkpoint + audit log |
| 31 | `ADMIN` | GET | `/api/v1/officer/queue` | 403 | 403 | **PASS** | `require_officer_role` (**Separation of Duties**) | Forbidden: Admin cannot access officer queue |
| 32 | `ADMIN` | POST | `/api/v1/officer/decision` | 403 | 403 | **PASS** | `require_officer_role` (**Separation of Duties**) | Forbidden: Admin cannot decide fraud cases |
| 33 | `ADMIN` | POST | `/api/v1/officer/hearing-schedule` | 403 | 403 | **PASS** | `require_officer_role` (**Separation of Duties**) | Forbidden: Admin cannot schedule hearings |

---

## 2. Insecure Direct Object Reference (IDOR) Protection Matrix

| Scenario | Actor Role | Target Resource | Request | Expected Status | Actual Status | Security Finding |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| Cross-Citizen Application | `USR-CITIZEN-01` | `USR-CITIZEN-02` application | `GET /citizen/my-applications/{other_app_id}` | 403 | 403 | **BLOCKED:** Server validates `app_data["user_id"] == citizen["user_id"]`. |
| Cross-Citizen Parcels | `USR-CITIZEN-01` | All unlinked parcels | `GET /citizen/my-parcels` | 200 | 200 | **ISOLATED:** SQL query strictly uses `WHERE cp.user_id = ?`. Returns only 2 linked parcels for USR-CITIZEN-01. |
| Buyer Request Snooping | `USR-BUYER-01` | `USR-BUYER-02` requests | `GET /buyer/review-requests` | 200 | 200 | **ISOLATED:** SQL query strictly uses `WHERE brr.buyer_id = ?`. Cross-account records excluded. |

---

## 3. Separation of Administrative & Judicial Duties Matrix

| Administrative Actor | Statutory Officer Action Attempted | Policy Constraint | Result | Audit Log Attributed |
| :--- | :--- | :--- | :---: | :--- |
| `admin@deshmrittika.gov.bd` | Access `/api/v1/officer/queue` | Strictly prohibited. System admin does not hold judicial authority. | **403 Forbidden** | Rejected before reaching DB |
| `admin@deshmrittika.gov.bd` | Submit `/api/v1/officer/decision` | Admin cannot issue mutation decisions or resolve fraud cases. | **403 Forbidden** | Rejected before reaching DB |
| `admin@deshmrittika.gov.bd` | Schedule `/api/v1/officer/hearing-schedule` | Admin cannot issue official summons or set judicial hearing dates. | **403 Forbidden** | Rejected before reaching DB |

---

## 4. Attributable Audit Log Verification

Every authorized privileged action generates an immutable security audit event in SQLite:

```
Sample Review Log Recorded:
- Log ID: LOG-000033
- Case ID: CASE-000001
- Reviewer ID: OFFICER-SAVAR-01
- Action: REJECTED_FRAUD_FLAG
- Reason: Verified conflicting subsequent transfer
- Timestamp: 2026-10-17T11:35:35.863743+00:00

Sample Database Checkpoint Log Recorded:
- Log ID: SEC-E6C685651BC5
- User ID: USR-ADMIN-01
- Actor Email: admin@deshmrittika.gov.bd
- Action: DB_CHECKPOINT_TRIGGERED
- Timestamp: 2026-10-17T11:35:36.002144+00:00
```
