# BHUMI-SYNC v2.1 — Automated Security & Authentication Test Report

**Execution Timestamp:** 2026-10-17 12:06:11 UTC  
**Environment:** macOS (Darwin 24.6.0), Python 3.13, FastAPI 0.139.2, SQLite3  
**Database File:** `data/generated/full_scale/landtech_synthetic.db` (100,000 parcels intact)  
**Test Runner:** `unittest` via `python3 -m unittest discover -s tests -p "test_*.py"`  

---

## 1. Executive Summary

| Test Suite File | Test Objective | Tests Executed | Passed | Failed | Execution Time |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `tests/test_auth_security.py` | Complete Auth, OTP, Password Reset, RBAC & Protection | 16 | 16 | 0 | 2.700s |
| `tests/test_backend.py` | Problem Tracks P1–P6, Due Diligence, Officer Triage | 10 | 10 | 0 | 1.880s |
| `tests/test_ocr_advanced.py` | Bengali Tesseract OCR Pipeline & Confidence Extraction | 4 | 4 | 0 | 1.363s |
| **TOTAL** | **Entire Platform Integration & Security Suite** | **30** | **30** | **0** | **5.943s** |

**Final Status:** **100% PASSED (0 Regressions, 0 Failures)**

---

## 2. Detailed Test Results (`tests/test_auth_security.py`)

| Test ID | Test Name | Target Requirement | HTTP Status / Assertions | Result |
| :---: | :--- | :--- | :---: | :---: |
| **01** | `test_01_signup_valid_citizen` | Valid signup creates `UNVERIFIED` account + dispatches 6-digit OTP | HTTP 200, status `UNVERIFIED` | **PASSED** |
| **02** | `test_02_signup_privilege_escalation_blocked` | Public signup requesting `OFFICER` or `ADMINISTRATOR` blocked | HTTP 403 Forbidden | **PASSED** |
| **03** | `test_03_signup_password_rules_and_mismatch` | Rejection of passwords <8 characters or mismatched confirmation | HTTP 400 Bad Request | **PASSED** |
| **04** | `test_04_signup_duplicate_email` | Duplicate email address registration prevention | HTTP 400 Bad Request | **PASSED** |
| **05** | `test_05_otp_successful_verification` | 6-digit OTP transitions account to `ACTIVE` + returns bearer session | HTTP 200, status `ACTIVE` | **PASSED** |
| **06** | `test_06_otp_invalid_code_and_remaining_attempts` | Incorrect code decrements attempts counter and provides feedback | HTTP 400, attempt count decremented | **PASSED** |
| **07** | `test_07_otp_reuse_blocked` | Used OTP cannot be replayed or reused | HTTP 400 on second submission | **PASSED** |
| **08** | `test_08_resend_cooldown_rate_limit` | Resend endpoint enforces strict 60-second cooldown rate limiting | HTTP 429 Too Many Requests | **PASSED** |
| **09** | `test_09_login_unverified_account_blocked` | Unverified accounts cannot login; triggers prompt to complete OTP | HTTP 403 (`ACCOUNT_UNVERIFIED`) | **PASSED** |
| **10** | `test_10_login_invalid_password` | Incorrect password returns generic 401 without user enumeration | HTTP 401 Unauthorized | **PASSED** |
| **11** | `test_11_logout_and_session_invalidation` | Logout revokes token in SQLite; subsequent requests return 401 | HTTP 401 on revoked token | **PASSED** |
| **12** | `test_12_password_reset_flow` | End-to-end reset flow (forgot -> OTP -> reset -> login with new password) | HTTP 200, old password rejected | **PASSED** |
| **13** | `test_13_citizen_cannot_access_admin_or_officer` | Citizen bearer token cannot access admin or officer endpoints | HTTP 403 Forbidden | **PASSED** |
| **14** | `test_14_buyer_cannot_access_officer_or_admin` | Buyer bearer token cannot access officer review or admin APIs | HTTP 403 Forbidden | **PASSED** |
| **15** | `test_15_ac_land_can_access_officer_queue_but_not_admin` | AC Land token can access triage queue, but not admin management | HTTP 200 on queue, 403 on admin | **PASSED** |
| **16** | `test_16_admin_full_management_and_last_admin_protection` | Admin manages users/logs, but is prevented from demoting last admin | HTTP 200 on list, 400 on demote last | **PASSED** |

---

## 3. Cryptographic & Security Verification Details

### 1. Password Hashing (PBKDF2-HMAC-SHA256)
- **Algorithm:** PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP / NIST SP 800-63B compliant).
- **Salt:** 16 cryptographically secure random bytes generated per password.
- **Verification:** Constant-time `hmac.compare_digest` prevents timing discrepancy leaks.
- **Performance Benchmark:** ~0.177s per verification, balancing defense against offline dictionary attacks with low server latency.

### 2. 6-Digit Verification Code (OTP) Security
- **Generation:** `secrets.randbelow(1000000)` produces cryptographically random integers formatted to 6 zero-padded digits.
- **Storage:** Stored exclusively as an HMAC-SHA256 digest keyed with `SECRET_KEY`. Cleartext OTP codes are never persisted in the database.
- **Lifespan:** 10 minutes maximum validity.
- **Brute-Force Guard:** Maximum 5 failed attempts allowed before challenge is permanently locked (HTTP 429).
- **Cooldown:** Strict 60-second wait required between successive resend requests.

### 3. Session Revocation & Invalidation
- **Session ID:** 256-bit cryptographically random token issued upon successful login or verification.
- **Persistence:** Stored as a SHA-256 digest in `user_sessions`.
- **Revocation:** Calling `/auth/logout` flags `is_revoked = 1`, resulting in immediate invalidation across subsequent requests.
- **Global Logout:** Calling `/auth/logout-all` invalidates all tokens associated with the user account.

---

## 4. Regression Testing Summary

All pre-existing problem track test suites were executed concurrently:
- **Track P1 (Ancient Deed & Porcha OCR):** 4/4 Passed. Verified multi-lingual Bangla/English Tesseract extraction, image contrast preprocessing, and confidence calculations.
- **Track P2 (Cryptographic Hash Verification):** Passed. Verified SHA-256 client and server computation against registered land deeds.
- **Track P3 (Double-Selling Fraud Detection):** Passed. Verified 100% recall on seeded conflict scenarios and AC Land triage diff comparisons.
- **Track P4 (Smart e-Mutation Simulator):** Passed. Verified 3-way automated pre-check (khas, tax, restrictions).
- **Track P5 (5-Factor Due Diligence Dossiers):** Passed. Verified parcel search, ownership timeline, and risk gauge calculations.
- **Track P6 (Cadastral GIS & Khas Land Protection):** Passed. Verified WGS-84 polygon boundaries and Dhaka-Aricha 100-meter highway buffer alerts.
