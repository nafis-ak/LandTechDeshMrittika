# DESHMRITTIKA / BHUMI-SYNC v2.2 — Authoritative Role & Permission Authorization Matrix

**Project:** DeshMrittika / BHUMI-SYNC v2.2  
**Security Standard:** Strict Four-Role RBAC + Server-Side Enforcement + Separation of Duties  
**Workspace:** `/Users/macbookair/Desktop/LandTechDeshMrittika`  
**Evaluation Standard:** Independent Automated Verification & Zero Client-Side Authority  

---

## 1. Authoritative Four-Role Specification

The platform defines exactly four distinct operational roles across database records, session tokens, backend authorization middleware, and UI workspace views:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DESHMRITTIKA RBAC ROLES                         │
├─────────────────────┬───────────────────┬──────────────────────────────┤
│ Internal Role Code  │ English Standard  │ Bengali System Designation   │
├─────────────────────┼───────────────────┼──────────────────────────────┤
│ CITIZEN             │ Citizen           │ সাধারণ নাগরিক                 │
│ BUYER               │ Prospective Buyer │ সম্ভাব্য ক্রেতা               │
│ OFFICER             │ AC Land (Officer) │ সহকারী কমিশনার–ভূমি          │
│ ADMINISTRATOR       │ System Admin      │ সিস্টেম অ্যাডমিন             │
└─────────────────────┴───────────────────┴──────────────────────────────┘
```

---

## 2. Role-by-Role Capabilities & Security Restrictions

### ROLE 1 — সাধারণ নাগরিক (Citizen)
*Primary Purpose: নিজের জমি, নথি ও আবেদন পরিচালনা।*

#### Authorized Capabilities:
- **Private Linked Land:** View own linked land parcels (`/api/v1/citizen/my-parcels`) with deed type, ownership share percentage, RS/BS khatian, and clearly labelled demo land-tax status.
- **Search Capabilities:** Search parcels using Dag, Khatian, Mouza, or Parcel ID subject to public redaction policies.
- **OCR Engine (P1):** Upload deed, Khatian, and Porcha scans for multi-lingual Bengali OCR extraction. Review, edit, save, and download OCR results.
- **Mutation & Service Applications:** Submit simulated mutation or record-correction applications (`POST /api/v1/citizen/applications`) with attached supporting metadata.
- **Tracking & Notice Inbox:** Real-time tracking of personal application milestones, hearing notices, and official summons (`/api/v1/citizen/my-notifications`).
- **Personal Audit Trail:** View personal login history and document activity logs (`/api/v1/citizen/my-activity`).

#### Security Restrictions:
- **IDOR Restriction:** Strictly prohibited from accessing other citizens' private documents, unlinked parcels, or applications.
- **Officer Confidentiality:** Cannot view internal AC Land investigation notes, recommendation drafts, or confidential flags.
- **Separation of Duties:** Cannot approve own or others' mutation applications; cannot modify authoritative database records.
- **Restricted Endpoints:** Blocked with `HTTP 403 Forbidden` from Officer triage (`/officer/*`) and Administrator (`/admin/*`) endpoints.
- **Simulation Disclaimer:** Cannot represent simulated application receipts as official government deeds.

---

### ROLE 2 — সম্ভাব্য ক্রেতা (Buyer)
*Primary Purpose: জমি কেনার আগে ঝুঁকি ও নথি যাচাই।*

#### Authorized Capabilities:
- **Cadastral Search:** Search parcels across Savar Mouzas by Parcel ID, Dag, Khatian, and Mouza.
- **Ownership Timeline Summary:** View sanitized baya deed progression and timeline summaries (`/api/v1/buyer-ownership-summary`).
- **Double-Selling Risk (P3):** Inspect conflicting subsequent transfer flags and serial transfer risk scores.
- **Document Integrity (P2):** Verify cryptographic SHA-256 hash against registered ledger references.
- **Advisory Indicators:** View demo land-tax flags, litigation warnings, acquisition notifications, and 1-No. Khas land proximity alerts.
- **Boundary Conflicts (P6):** Inspect GeoJSON polygon overlays and synthetic adjacent-plot dispute warnings.
- **Comparative Due Diligence (P5):** Generate and download 5-factor due diligence evaluation reports.
- **Review Requests:** Submit official review requests (`POST /api/v1/buyer/review-requests`) for suspicious parcels to AC Land office.

#### Security Restrictions:
- **Privacy Shield:** Strictly prohibited from accessing unredacted National IDs (NID), phone numbers, or private citizen documents.
- **Officer Deliberations:** Cannot view internal investigation case files or officer draft recommendations.
- **Immutable Ledger:** Cannot modify ownership records or approve mutation files.
- **Title Disclaimer:** Risk scores and hash matches do NOT constitute conclusive legal title warranty. Clear synthetic evaluation warning displayed.

---

### ROLE 3 — সহকারী কমিশনার–ভূমি (AC Land / Officer)
*Primary Purpose: Assigned case review, mutation workflow simulation, and fraud investigation.*

#### Authorized Capabilities:
- **Assigned Queue:** View triage queue of conflicting mutation files, P3 double-selling alerts, and buyer review requests (`/api/v1/officer/queue`, `/api/v1/officer/assigned-applications`).
- **Deed Comparison:** Cross-check extracted OCR deed fields with registered land office baya deed records.
- **Hearing & Field Verification:** Schedule simulated hearing dates, issue digital summons, and record field inspection reports.
- **Workflow Recommendations:** Record draft recommendations, return applications for correction, or flag cases for law enforcement investigation (`POST /api/v1/officer/decision`).
- **Audited Decisions:** Every action records mandatory institutional reason, case ID, officer actor email, and ISO timestamp in security audit log.

#### Security Restrictions:
- **Jurisdictional Boundary:** Restricted to authorized Upazila (Savar) jurisdiction; cannot tamper with other sub-district records.
- **Admin Isolation:** Strictly prohibited from administrative user management (`/admin/users`) or security configuration endpoints.
- **Non-Repudiation:** Cannot alter, truncate, or delete historical case audit trail records.
- **Prototype Warning:** Workflow decisions are simulated decision-support records and do not constitute legally binding gazetted decrees.

---

### ROLE 4 — সিস্টেম অ্যাডমিন (Admin)
*Primary Purpose: Account administration, security, configuration, and system health.*

#### Authorized Capabilities:
- **User & Role Administration:** Manage user accounts, approve pending roles, activate or suspend accounts (`/api/v1/admin/users`, `/api/v1/admin/users/role`, `/api/v1/admin/users/status`).
- **Security Audit Logs:** Monitor login events, privilege access attempts, and access-denied incidents (`/api/v1/admin/security-logs`).
- **System Health Diagnostics:** Query SQLite WAL mode, database size, table counts, and active sessions (`/api/v1/admin/diagnostics`).
- **OCR Health Diagnostics:** Monitor Tesseract OCR engine, Bengali language pack (`ben`), and image preprocessors (`/api/v1/admin/ocr-health`).
- **Fraud Engine Configuration:** Review versioned fraud rule catalogs (DS-01, DS-02, DS-03, KHAS-01) and detection thresholds (`/api/v1/admin/fraud-rules`).
- **WAL Backup Checkpoint:** Trigger audited SQLite WAL passive/full checkpoints (`POST /api/v1/admin/backups/checkpoint`).

#### Security Restrictions:
- **Separation of Duties:** **Admin privileges do NOT grant judicial land mutation approval authority or case triage jurisdiction.** Calls to `/api/v1/officer/queue` return `HTTP 403 Forbidden`.
- **Last Admin Guard:** Server blocks removal, suspension, or demotion of the last active administrator account.
- **No Impersonation:** Cannot switch identity or impersonate citizens or officers via client dropdowns.

---

## 3. End-to-End API Authorization Enforcement Matrix

| API Endpoint | Method | `CITIZEN` | `BUYER` | `OFFICER` | `ADMIN` | Backend Guard Dependency |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `/api/v1/auth/signup` | POST | ✓ (Citizen/Buyer) | ✓ (Citizen/Buyer) | ✗ (403) | ✗ (403) | Privilege escalation check |
| `/api/v1/auth/verify-email` | POST | ✓ | ✓ | ✓ | ✓ | HMAC-SHA256 digest match |
| `/api/v1/auth/login` | POST | ✓ | ✓ | ✓ | ✓ | PBKDF2 + Brute-force rate guard |
| `/api/v1/auth/me` | GET | ✓ | ✓ | ✓ | ✓ | `require_authenticated_user` |
| `/api/v1/auth/logout` | POST | ✓ | ✓ | ✓ | ✓ | `revoke_session` in SQLite |
| `/api/v1/citizen/my-parcels` | GET | ✓ | ✗ (403) | ✗ (403) | ✓ (Audit) | `require_citizen_access` |
| `/api/v1/citizen/my-applications` | GET | ✓ | ✗ (403) | ✗ (403) | ✓ (Audit) | `require_citizen_access` |
| `/api/v1/citizen/applications` | POST | ✓ | ✗ (403) | ✗ (403) | ✗ (403) | `require_citizen_access` |
| `/api/v1/citizen/my-notifications`| GET | ✓ | ✗ (403) | ✗ (403) | ✗ (403) | `require_citizen_access` |
| `/api/v1/citizen/my-activity` | GET | ✓ | ✗ (403) | ✗ (403) | ✗ (403) | `require_citizen_access` |
| `/api/v1/buyer/review-requests` | POST | ✗ (403) | ✓ | ✗ (403) | ✓ (Audit) | `require_buyer_access` |
| `/api/v1/buyer/review-requests` | GET | ✗ (403) | ✓ | ✗ (403) | ✓ (Audit) | `require_buyer_access` |
| `/api/v1/documents/upload-ocr` | POST | ✓ | ✓ | ✓ | ✓ | `require_authenticated_user` |
| `/api/v1/documents/verify-integrity`| POST| ✓ | ✓ | ✓ | ✓ | `require_authenticated_user` |
| `/api/v1/due-diligence/{id}` | GET | ✓ | ✓ | ✓ | ✓ | Redacted personal info |
| `/api/v1/officer/queue` | GET | ✗ (403) | ✗ (403) | ✓ | ✗ (403) | `require_officer_role` (Separation of Duties) |
| `/api/v1/officer/assigned-applications` | GET | ✗ (403) | ✗ (403) | ✓ | ✗ (403) | `require_officer_role` |
| `/api/v1/officer/decision` | POST | ✗ (403) | ✗ (403) | ✓ | ✗ (403) | `require_officer_role` |
| `/api/v1/officer/hearing-schedule` | POST | ✗ (403) | ✗ (403) | ✓ | ✗ (403) | `require_officer_role` |
| `/api/v1/admin/users` | GET | ✗ (403) | ✗ (403) | ✗ (403) | ✓ | `require_admin_role` |
| `/api/v1/admin/users/role` | POST | ✗ (403) | ✗ (403) | ✗ (403) | ✓ | `require_admin_role` + Last Admin Guard |
| `/api/v1/admin/users/status` | POST | ✗ (403) | ✗ (403) | ✗ (403) | ✓ | `require_admin_role` + Last Admin Guard |
| `/api/v1/admin/security-logs` | GET | ✗ (403) | ✗ (403) | ✗ (403) | ✓ | `require_admin_role` |
| `/api/v1/admin/diagnostics` | GET | ✗ (403) | ✗ (403) | ✗ (403) | ✓ | `require_admin_role` |
| `/api/v1/admin/ocr-health` | GET | ✗ (403) | ✗ (403) | ✗ (403) | ✓ | `require_admin_role` |
| `/api/v1/admin/fraud-rules` | GET | ✗ (403) | ✗ (403) | ✗ (403) | ✓ | `require_admin_role` |
| `/api/v1/admin/backups/checkpoint`| POST | ✗ (403) | ✗ (403) | ✗ (403) | ✓ | `require_admin_role` |

---

## 4. UI Workspace Isolation Matrix

Each role renders a dedicated workspace shell. Direct manual URL access to unauthorized pages is intercepted by client-side guards and returns `#page-unauthorized` (403 Access Denied), backed by strict server-side 403 API enforcement:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ROLE-SPECIFIC NAVIGATION WORKSPACES                  │
├─────────────────────┬──────────────────────────────────────────────────┤
│ Role                │ Authorized Pages in App Shell                    │
├─────────────────────┼──────────────────────────────────────────────────┤
│ CITIZEN             │ overview, citizen-myland, citizen, ocr,          │
│                     │ citizen-applications, mutation,                  │
│                     │ citizen-notifications, citizen-activity          │
├─────────────────────┼──────────────────────────────────────────────────┤
│ BUYER               │ buyer-overview, citizen, due-diligence,          │
│                     │ buyer-ownership-summary, buyer-fraud-risk,       │
│                     │ verify, map, buyer-compare-reports,              │
│                     │ buyer-review-requests                            │
├─────────────────────┼──────────────────────────────────────────────────┤
│ OFFICER             │ officer-overview, officer-cases, officer,        │
│                     │ officer-deed-compare, mutation,                  │
│                     │ officer-doc-review, officer-hearings,            │
│                     │ officer-decisions, audit                         │
├─────────────────────┼──────────────────────────────────────────────────┤
│ ADMINISTRATOR       │ admin-overview, users, security-logs,            │
│                     │ admin-diagnostics, admin-dataset,                │
│                     │ admin-ocr-health, admin-fraud-rules,             │
│                     │ admin-backups, admin-settings                    │
└─────────────────────┴──────────────────────────────────────────────────┘
```
