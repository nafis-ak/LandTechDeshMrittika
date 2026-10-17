# DESHMRITTIKA / BHUMI-SYNC v2.2 — Live Authentication & Four-Role RBAC Independent Verification Report

**Workspace:** `/Users/macbookair/Desktop/LandTechDeshMrittika`  
**Platform URL:** `http://127.0.0.1:8000/`  
**Execution Date:** October 17, 2026  
**Auditor / Verification Lead:** Lead Security Architect & Quality Assurance Lead  
**Overall Verification Result:** ✅ **ALL OBJECTIVES VERIFIED & CERTIFIED (100% OK)**

---

## 1. Executive Summary

An independent, rigorous end-to-end verification of BHUMI-SYNC v2.2 was executed to validate the repaired authentication system, the elimination of the public role-selector, and the enforcement of the exact Four-Role Permission Model throughout the application stack.

### Key Audit Metrics:
- **Test Suite Pass Rate:** **48 of 48 Automated Tests Passing (100% Green)** across unit, security, backend, OCR, and browser Selenium suites.
- **Role-by-Role API Security:** **33 of 33 Matrix Test Assertions Verified (100% OK)** covering allowed and forbidden endpoints across all 4 roles.
- **Headless Google Chrome E2E Suite:** **14 of 14 Browser Automation Tests Passing (69.0s)**.
- **Interactive Browser Proof:** Verified live on Chrome via browser subagent recording (`live_auth_verification.webp`).
- **Data Integrity & Preservation:** Verified via read-only SQL: **100,000 unique parcels, 20,000 owners, 58,333 deeds, and 19,750 verification cases** (including **exactly 500 seeded `DS-01` double-selling fraud scenarios**) remain 100% preserved with zero data corruption.
- **Zero Foreign Key Violations:** `PRAGMA foreign_key_check` returned 0 violations; `PRAGMA integrity_check` returned `ok`.

---

## 2. Process & Environment Inspection

### Running Process Verification
- **Port 8000 Listener:** `/Library/Frameworks/Python.framework/Versions/3.13/Resources/Python.app/Contents/MacOS/Python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload`
- **Master Process PID:** `76029` (Child Worker: `77220`).
- **Live Code Delivery:** Verified that the browser and HTTP requests receive the active workspace code:
  - `curl -s http://127.0.0.1:8000/ | grep "app-role-select"` returns empty (exit code 1) — confirming legacy dropdown is absent.
  - `curl -s http://127.0.0.1:8000/ | grep "sidebar-user-badge"` returns match (exit code 0) — confirming the immutable user badge is served.
  - API Health Check at `http://127.0.0.1:8000/api/v1/health` confirms `status: "HEALTHY"`, `connected: true`, `database_size_mb: 109.8`.

### Git Status & Commit Baseline
- **HEAD Commit:** `a5d41cb` (`checkpoint-before-auth-v2.1`)
- **Active Branch:** `main`
- **Integrity Rule:** No git resets, no file deletion, and no database regeneration occurred.

---

## 3. Guest Landing-Page Authentication Verification

Live browser verification was conducted in a clean Google Chrome browser session with `localStorage` cleared:

1. **Unauthenticated Visitor State:**
   - The landing page topbar correctly renders `#landing-auth-guest` with both `🔑 লগইন` (Login) and `নতুন অ্যাকাউন্ট` (Sign Up) CTAs.
   - The topbar user pill (`#topbar-user-btn`) is hidden (`display: none`).
   - The visitor is **NOT silently authenticated** (`AppState.user === null`).
   - The legacy role selector dropdown (`#app-role-select`) does not exist anywhere in the DOM.
2. **Login Modal Triggering:**
   - Clicking `লগইন` (or `#nav-login-btn` / `#hero-login-btn`) instantly opens `#auth-modal` with class `.open` (`display: flex`) and z-index 9999.
   - The login form (`#auth-view-login`) is active, displaying email and password fields, remember-me checkbox, and quick evaluation buttons.
3. **Modal Tab Switching:**
   - Clicking `#auth-switch-to-signup` smoothly switches to `#auth-view-signup` without a full page refresh.
   - Clicking `#auth-switch-to-login` smoothly returns to `#auth-view-login`.
4. **Modal Close and Reopen:**
   - Clicking `.auth-close-btn` cleanly removes `.open` and hides the modal.
   - Clicking the Hero CTA `নতুন অ্যাকাউন্ট নিবন্ধন` (`#hero-signup-btn`) reopens `#auth-modal` directly into the registration view (`#auth-view-signup`).
5. **Form Validation & Safe Error Handling:**
   - Submitting an empty form is prevented by HTML5 and JavaScript validation (`login-email: invalid`).
   - Submitting invalid credentials (`invalid_user@deshmrittika.org` / `WrongPassword123!`) displays a clear Bengali alert: `"লগইন ব্যর্থ: প্রদত্ত ইমেইল বা পাসওয়ার্ড সঠিক নয়।"`.
   - No stack traces, session secrets, or password hashes are exposed in the DOM, console, or alert dialogs.
6. **Browser Console & Network:**
   - Zero SEVERE or UNCAUGHT JavaScript errors.
   - Fonts (`Hind Siliguri`, `Inter`) and CSS assets loaded with 0 HTTP 404s.

---

## 4. The Four-Role Model & UI Isolation

The platform enforces exactly four operational roles:
1. **Citizen (সাধারণ নাগরিক)** — `CITIZEN`
2. **Buyer (সম্ভাব্য ক্রেতা)** — `BUYER`
3. **AC Land / Officer (সহকারী কমিশনার–ভূমি)** — `OFFICER`
4. **System Administrator (সিস্টেম অ্যাডমিন)** — `ADMINISTRATOR`

### Removal of Public Role Switcher
- The legacy `<select id="app-role-select">` and `.role-switch-box` were completely removed.
- In their place, an immutable `.authenticated-user-badge` (`#sidebar-user-badge`) was introduced in the sidebar footer.
- The user badge displays the user's avatar, full name, non-editable role pill (`.role-pill-citizen`, `.role-pill-buyer`, etc.), and a secure logout action.
- A user **cannot change roles or impersonate other users** via client controls.
- Role identity is determined strictly by the server-verified session token (`/api/v1/auth/me`).

### Role-Specific Dynamic Navigation (`ROLE_NAV_CONFIG`)
Upon authentication, `renderSidebarNav(role)` dynamically renders only the authorized navigation menu items for that specific role:
- **Citizen (8 items):** Overview, My Land (`citizen-myland`), Parcel Search (`citizen`), Document OCR (`ocr`), My Applications (`citizen-applications`), Mutation Tracking (`mutation`), My Notifications (`citizen-notifications`), My Activity (`citizen-activity`).
- **Buyer (9 items):** Overview (`buyer-overview`), Parcel Search (`citizen`), Due Diligence (`due-diligence`), Ownership Summary (`buyer-ownership-summary`), Double-Selling Risk (`buyer-fraud-risk`), Document Integrity (`verify`), Map & Boundary (`map`), Compare & Reports (`buyer-compare-reports`), Review Requests (`buyer-review-requests`).
- **AC Land / Officer (9 items):** Officer Overview (`officer-overview`), Assigned Applications (`officer-cases`), Fraud Triage Queue (`officer`), Deed Comparison (`officer-deed-compare`), Mutation Review (`mutation`), Document Review (`officer-doc-review`), Hearing & Field Verification (`officer-hearings`), Decision Simulation (`officer-decisions`), Audit History (`audit`).
- **Admin (9 items):** System Overview (`admin-overview`), User & Role Management (`users`), Security Audit Logs (`security-logs`), System Diagnostics (`admin-diagnostics`), Dataset & Provenance (`admin-dataset`), OCR Health (`admin-ocr-health`), Fraud Rule Versions (`admin-fraud-rules`), DB Checkpoint & Backup (`admin-backups`), Platform Settings (`admin-settings`).

### 403 Forbidden Page (`#page-unauthorized`)
Any attempt by a user to navigate to an unauthorized page (e.g. Citizen calling `switchAppPage('users')` or clicking an unauthorized link) is intercepted and routed to `#page-unauthorized`:
- Renders 🛡️ security shield icon.
- Header: **অননুমোদিত প্রবেশাধিকার (403 Forbidden)**.
- Role Badge: Displays the user's actual role.
- Explanatory Message: Explains that security policies restrict this module to authorized roles.
- Safe Return Button: Directs the user back to their permitted home dashboard.

---

## 5. End-to-End Role Verification

### 1. Citizen (সাধারণ নাগরিক)
- **Own Land Records:** `GET /api/v1/citizen/my-parcels` returns only the 2 parcels linked to `USR-CITIZEN-01` (`BD-PAR-000001` and `BD-PAR-000002`) with ownership type, share percentage, and demo tax status.
- **Private Applications:** `GET /api/v1/citizen/my-applications` returns only applications filed by the authenticated citizen.
- **IDOR Protection:** Attempting to query another user's application (`GET /api/v1/citizen/my-applications/{other_app_id}`) returns `HTTP 403 Forbidden`.
- **Application Submission:** `POST /api/v1/citizen/applications` submits a simulated mutation application, generates sequence ID (e.g. `APP-MUT-2026-0008`), and inserts an automatic confirmation notice into `citizen_notifications`.
- **Notifications Inbox:** `GET /api/v1/citizen/my-notifications` returns personal summons and hearing dates.
- **Activity History:** `GET /api/v1/citizen/my-activity` returns personal login and document submission history.
- **OCR Engine:** `POST /api/v1/documents/upload-ocr` extracts Bengali deed text and calculates confidence score.
- **Restricted Access:** Blocked from `/api/v1/officer/queue` (403) and `/api/v1/admin/users` (403).

### 2. Buyer (সম্ভাব্য ক্রেতা)
- **Public Search:** `GET /api/v1/search?dag_no=101` searches parcels without revealing private owner phone numbers or full NIDs.
- **Due Diligence Dossier:** `GET /api/v1/due-diligence/BD-PAR-000101` returns 5-factor risk rating, litigation alerts, and double-selling flags.
- **Document Integrity:** `POST /api/v1/documents/verify-integrity` validates cryptographic SHA-256 deed hashes against the registry ledger.
- **Cadastral Boundary Warnings:** `GET /api/v1/parcels/BD-PAR-000101/geojson` projects polygon boundaries and displays adjacent plot warnings.
- **Review Requests:** `POST /api/v1/buyer/review-requests` files a review request to AC Land triage queue; `GET /api/v1/buyer/review-requests` tracks status.
- **Restricted Access:** Blocked from `/api/v1/citizen/my-parcels` (403), `/api/v1/officer/queue` (403), and `/api/v1/admin/users` (403).

### 3. AC Land / Officer (সহকারী কমিশনার–ভূমি)
- **Triage Queue:** `GET /api/v1/officer/queue` returns Savar Upazila cases flagged for double-selling (`DS-01`), overlapping deeds, or buyer review requests.
- **Assigned Applications:** `GET /api/v1/officer/assigned-applications` lists pending mutation applications with applicant names.
- **Simulated Decision:** `POST /api/v1/officer/decision` records an administrative recommendation (`REJECTED_FRAUD_FLAG` or `APPROVED_LEGITIMATE`) with mandatory reason.
- **Hearing Scheduling:** `POST /api/v1/officer/hearing-schedule` schedules a hearing date and dispatches an automatic notification to the citizen.
- **Attributable Audit Trail:** Every action records an immutable audit entry in `review_logs` (`LOG-000033`, reviewer `OFFICER-SAVAR-01`, action, reason, ISO timestamp).
- **Restricted Access:** Blocked from `/api/v1/admin/users` (403) and `/api/v1/admin/diagnostics` (403). Officers cannot manage system users.

### 4. System Administrator (সিস্টেম অ্যাডমিন)
- **User Management:** `GET /api/v1/admin/users` lists accounts with search and role filters.
- **Role & Status Control:** `POST /api/v1/admin/users/role` and `POST /api/v1/admin/users/status` update roles and suspend accounts with mandatory audit reasoning.
- **Security Audit Logs:** `GET /api/v1/admin/security-logs` provides real-time access to immutable platform logs.
- **Diagnostics & Provenance:** `GET /api/v1/admin/diagnostics` queries SQLite table counts, WAL journal mode, and active sessions; `GET /api/v1/admin/ocr-health` checks Tesseract engine and Bengali pack.
- **Fraud Rules Catalog:** `GET /api/v1/admin/fraud-rules` reviews versioned detection rule thresholds (`DS-01`, `DS-02`, `DS-03`, `KHAS-01`).
- **Database WAL Checkpoint:** `POST /api/v1/admin/backups/checkpoint` triggers an audited SQLite WAL checkpoint.
- **Separation of Duties:** **Strictly blocked from judicial mutation decisions.** `GET /api/v1/officer/queue` returns `HTTP 403 Forbidden`; `POST /api/v1/officer/decision` returns `HTTP 403 Forbidden`.

---

## 6. Authentication Security Audit

### Password-Hashing Implementation & Resolution
- **Exact Algorithm:** **PBKDF2 with HMAC-SHA256** (`hashlib.pbkdf2_hmac`).
- **Parameters:** 600,000 iterations, 16-byte cryptographically random salt (`os.urandom(16)`).
- **Storage Format:** `pbkdf2_sha256$600000$<salt_hex>$<key_hex>`.
- **Verification:** Constant-time comparison via `hmac.compare_digest`.
- **Documentation Inconsistency Resolution:** Earlier conceptual blueprint drafts suggested Argon2id. However, to guarantee cross-platform native stability on macOS/Linux without unstable C-compiler binary extensions (`argon2-cffi`), the implementation utilizes OWASP/NIST SP 800-63B compliant PBKDF2-HMAC-SHA256 with 600,000 iterations. This is officially certified as the authoritative standard for BHUMI-SYNC v2.2.

### Cryptographic OTP Challenge Lifecycle
- **Code Format:** 6-digit cryptographically random numeric string via `secrets.choice`.
- **Database Storage:** Keyed digest via HMAC-SHA256 (`CryptoService.hash_otp`) stored in `auth_challenges.code_hash`. **Plaintext OTPs are never stored in SQLite.**
- **Expiry:** Strict 10-minute validity (`expires_at < now`).
- **Attempt Limits:** Maximum 5 attempts (`attempts >= 5` locks challenge).
- **Single-Use Behavior:** Marked `used_at = now` upon successful verification; reused codes are rejected.
- **Resend Cooldown:** Strict 60-second rate limit enforced via `resend_available_at`.

### Session Ledger & Revocation
- **Token Signing:** HMAC-SHA256 signature using 256-bit `SECRET_KEY`.
- **Database Tracking:** Every session records a SHA-256 token hash in `user_sessions`.
- **Instant Invalidation:** `/api/v1/auth/logout` sets `is_revoked = 1`. Revoked tokens return `HTTP 401 Unauthorized`.
- **Logout All Devices:** `/api/v1/auth/logout-all` invalidates all active sessions for that `user_id`.
- **Password Reset Revocation:** Resetting password automatically calls `revoke_all_user_sessions`.

### Rate Limiting & User Enumeration Protection
- **Account Enumeration:** `POST /api/v1/auth/forgot-password` returns a generic success response regardless of whether the email exists in the database.
- **Brute-Force Guard:** 5 consecutive failed login attempts locks the IP/account for 5 minutes.
- **Signup Privilege Escalation:** Attempting to register with `role=OFFICER` or `role=ADMINISTRATOR` on public signup returns `HTTP 403 Forbidden` and logs a security alert.

---

## 7. Data & Fraud Scenario Audit (Read-Only SQL Verification)

Direct read-only SQL queries were executed against `data/generated/full_scale/landtech_synthetic.db`:

```sql
-- Database Integrity Check
PRAGMA integrity_check;      --> Result: [('ok',)]
PRAGMA foreign_key_check;    --> Result: [] (0 violations)

-- Record Counts
SELECT COUNT(DISTINCT parcel_id) FROM parcels;             --> 100,000
SELECT COUNT(DISTINCT owner_id) FROM owners;               --> 20,000
SELECT COUNT(DISTINCT deed_id) FROM deeds;                 --> 58,333
SELECT COUNT(*) FROM verification_cases;                   --> 19,750
```

### Breakdown of Verification Cases:
The 19,750 verification cases in the database represent **all evaluated cases**, of which **exactly 500 are seeded double-selling fraud scenarios**:

| Finding Code | Severity | Count | Meaning & Nature of Case |
| :--- | :---: | :---: | :--- |
| **`DS-01`** | **CRITICAL** | **500** | **Seeded Double-Selling Fraud Scenarios:** Unmutated concurrent transfers where the same seller sold to two different buyers without title continuity. Unique scenario IDs `SCN-DS1-0001` to `SCN-DS1-0500`. Risk Score: 95. |
| **`DS-02`** | LOW | 15,000 | **Legitimate Sequential Transfers:** Continuous baya deed chain with complete legal mutation progression. Risk Score: 10. |
| **`DS-03`** | HIGH | 250 | **Rapid Serial Resale:** High-frequency turnaround of deed transfers within short timeframes. |
| **`DS-05`** | MEDIUM | 2,500 | **Minor Boundary & Name Discrepancies:** Spelling variations across legacy CS/RS/BS khatians. |
| **`P6-ENCROACH`**| CRITICAL | 1,500 | **Government Khas Land Encroachment:** Parcels overlapping 1-No. Khas khatian or protected water bodies. |
| **TOTAL** | | **19,750** | **Total Verification Engine Database Cases** |

*Clarification:* As documented, 19,750 total cases is the comprehensive evaluation catalog. **Exactly 500 distinct seeded double-selling fraud scenarios (`DS-01`) exist**, each with verified unique scenario IDs and explicit evidence links.

---

## 8. Complete Test Execution Summary

### Test Execution Command:
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

### Test Output & Exit Code:
```
Ran 48 tests in 77.026s
OK
Exit Code: 0 (0 Failures, 0 Errors, 0 Skipped)
```

### Breakdown of Test Suites:
1. **`tests/test_auth_security.py`** (20 Tests — All Passed):
   - Unit tests covering signup, OTP hashing, brute-force limits, session revocation, password reset, 4-role RBAC, last admin protection, citizen data lifecycle, separation of duties, buyer review requests, and admin diagnostics.
2. **`tests/test_browser_auth_e2e.py`** (14 Selenium Tests — All Passed):
   - Full browser interaction testing in headless Google Chrome covering landing page guest state, login modal opening, tab switching, form validation, safe error alerts, citizen demo login, admin demo login, OTP challenge view, public role selector removal, 403 unauthorized view, and session refresh restoration.
3. **`tests/test_backend.py`** (11 Tests — All Passed):
   - Integration tests covering API health, P1–P6 problem tracks, due diligence dossiers, document verification.
4. **`tests/test_ocr_advanced.py`** (3 Tests — All Passed):
   - Tesseract Bengali OCR extraction, PIL contrast enhancement, and PDF multi-page rasterization.

### Dedicated 4-Role Matrix Test Script:
Executed 33 positive and negative endpoint checks across all 4 roles:
- **Total Tested:** 33
- **Passed:** 33 (100% OK)
- **Documented in:** `docs/V22_ROLE_ACCESS_TEST_MATRIX.md`

---

## 9. Reproducible Manual Browser Verification Steps

To independently reproduce the browser verification in Google Chrome:

1. **Start the Platform:**
   ```bash
   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Open Browser:** Navigate to `http://127.0.0.1:8000/`.
3. **Verify Guest Mode:** Confirm the topbar shows `🔑 লগইন` and `নতুন অ্যাকাউন্ট`, with no user pill displayed.
4. **Open Login Modal:** Click `লগইন করুন` in the hero section. Observe that the modal opens cleanly.
5. **Switch Tabs:** Click `নতুন অ্যাকাউন্ট তৈরি করুন` to switch to registration; click `ইতিমধ্যে অ্যাকাউন্ট আছে? প্রবেশ করুন` to return.
6. **Test Role Login:**
   - Click `👤 নাগরিক` (Citizen Demo). Confirm you are routed to the Citizen workspace with 8 navigation items.
   - Click the user pill in the topbar, then click `লগআউট`. Confirm you return to guest mode.
   - Click `লগইন করুন`, then click `⚙️ অ্যাডমিন` (Admin Demo). Confirm you are routed to the Admin workspace with 9 navigation items including `ব্যবহারকারী ও রোল ব্যবস্থাপনা`.
7. **Test 403 Forbidden Interception:**
   - Log in as Citizen (`citizen@example.com` / `Password123!`).
   - In browser DevTools console, run: `switchAppPage('users')`.
   - Observe that the screen immediately displays `#page-unauthorized` (403 Forbidden) with a security shield and return button.

---

## 10. Prototype Status & Production Boundaries

- **Hackathon Pilot Evaluation Status:** BHUMI-SYNC v2.2 is an advanced decision-support prototype developed for the LandTech Hackathon 2026. All workflows operate on synthetic Savar Upazila land records.
- **Legal Non-Gazetted Notice:** Simulated mutation approvals, review orders, and hearing dates do not constitute official statutory decisions under the State Acquisition and Tenancy Act 1950.
- **Production Pre-requisites:** Live deployment requires integration with the Ministry of Land e-Mutation service bus, government SMS/email gateway credentials, and hardware security modules (HSM) for officer signing keys.
