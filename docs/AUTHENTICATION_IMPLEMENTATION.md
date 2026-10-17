# DESHMRITTIKA / BHUMI-SYNC v2.2 — Complete Authentication & RBAC Architecture

**Project:** DeshMrittika / BHUMI-SYNC v2.2  
**Workspace:** `/Users/macbookair/Desktop/LandTechDeshMrittika`  
**Security Standard:** Strict Server-Enforced Four-Role RBAC + Cryptographic Session Management  
**Status:** FULLY IMPLEMENTED & INDEPENDENTLY TESTED (48/48 Passing)  

---

## 1. System Architecture & End-to-End User Journey

BHUMI-SYNC v2.2 provides an integrated identity and access management system with zero client-side privilege assumption:

```
[Guest Landing Page] ──► [Responsive Auth Modal] (Login / Signup / OTP / Forgot Password)
         │
         ▼
[PBKDF2 Hash / HMAC-SHA256 Challenge Verification]
         │
         ▼
[Server-Issued Signed Session Token] ──► [Stored in Secure Local Storage / Headers]
         │
         ▼
[Server-Determined Role Identity] ──► (CITIZEN | BUYER | OFFICER | ADMINISTRATOR)
         │
         ▼
[Role-Isolated Workspace Shell] ──► (Only Authorized Navigation & Views Rendered)
         │
         ▼
[Strict Server-Side RBAC & IDOR Guards] ──► (403 Forbidden on Any Cross-Role Route)
         │
         ▼
[Audited Invalidation & Logout] ──► (Session Hash Marked Revoked in SQLite)
```

---

## 2. API Endpoints Reference

### Authentication & Lifecycle (`/api/v1/auth/`)
| Endpoint | Method | Security Level | Functionality |
| :--- | :---: | :---: | :--- |
| `POST /auth/signup` | POST | Public | Validates email, password strength (>=8 chars), matching passwords. Only allows `CITIZEN` or `BUYER`. Rejects `OFFICER` or `ADMINISTRATOR` with 403. Dispatches 6-digit OTP. |
| `POST /auth/verify-email` | POST | Public | Validates OTP hash digest, expiry (10 min), attempt limits (<=5). Marks user `ACTIVE` and issues session token. |
| `POST /auth/resend-code` | POST | Public | Re-generates OTP with 60-second resend cooldown. |
| `POST /auth/login` | POST | Public | Validates PBKDF2 hash, account `ACTIVE` status, and brute-force lockout (5 failures in 5 min). Issues persistent HMAC session token. |
| `POST /auth/forgot-password` | POST | Public | Generates single-use password reset OTP digest. Safe response prevents account enumeration. |
| `POST /auth/reset-password` | POST | Public | Validates reset OTP, updates PBKDF2 password hash, and executes `revoke_all_user_sessions`. |
| `POST /auth/change-password` | POST | Authenticated | Re-authenticates old password and sets new password. |
| `POST /auth/logout` | POST | Authenticated | Revokes current session token hash in `user_sessions`. |
| `POST /auth/logout-all` | POST | Authenticated | Revokes all active sessions for current user across all devices. |
| `GET /auth/me` | GET | Authenticated | Returns current authenticated user record with verified role and timestamps. |
| `GET /auth/dev-mailbox` | GET | Dev-Only | Displays sent OTP emails in local development mode with clear prototype notice. |

### Citizen Workspace API (`/api/v1/citizen/`)
| Endpoint | Method | Access Guard | Functionality |
| :--- | :---: | :---: | :--- |
| `GET /citizen/my-parcels` | GET | Citizen | Returns only the authenticated user's linked land parcels (`citizen_parcels` table). IDOR-protected. |
| `GET /citizen/my-applications` | GET | Citizen | Returns list of citizen's submitted mutation and correction applications. |
| `GET /citizen/my-applications/{id}`| GET | Citizen | Returns application dossier. Strictly prohibits cross-account inspection (403). |
| `POST /citizen/applications` | POST | Citizen | Creates a simulated mutation application with parcel link, service type, and metadata. |
| `GET /citizen/my-notifications` | GET | Citizen | Returns personal notices, hearing summons, and alerts. |
| `POST /citizen/notifications/{id}/read` | POST | Citizen | Marks personal notification as read. |
| `GET /citizen/my-activity` | GET | Citizen | Personal audit trail of logins and document submissions. |

### Buyer Due Diligence API (`/api/v1/buyer/`)
| Endpoint | Method | Access Guard | Functionality |
| :--- | :---: | :---: | :--- |
| `POST /buyer/review-requests` | POST | Buyer | Submits official parcel review request to AC Land triage queue. |
| `GET /buyer/review-requests` | GET | Buyer | Lists all review requests filed by current buyer with status. |

### Officer / AC Land API (`/api/v1/officer/`)
| Endpoint | Method | Access Guard | Functionality |
| :--- | :---: | :---: | :--- |
| `GET /officer/queue` | GET | Officer-Only | Returns triage queue of double-selling fraud alerts (P3) and buyer requests. |
| `GET /officer/assigned-applications` | GET | Officer-Only | Returns assigned mutation cases within Savar Upazila jurisdiction. |
| `POST /officer/decision` | POST | Officer-Only | Records simulated administrative recommendation or inquiry flag. |
| `POST /officer/hearing-schedule` | POST | Officer-Only | Schedules simulated field inspection or hearing notice. |
| `GET /officer/audit-logs` | GET | Officer-Only | Immutable audit log of all officer triage actions. |

### System Administration API (`/api/v1/admin/`)
| Endpoint | Method | Access Guard | Functionality |
| :--- | :---: | :---: | :--- |
| `GET /admin/users` | GET | Admin-Only | Paginated and filtered user account management list. |
| `POST /admin/users/role` | POST | Admin-Only | Modifies user role with mandatory reason audit logging. Protects last active admin. |
| `POST /admin/users/status` | POST | Admin-Only | Activates or suspends user accounts. Invalids sessions immediately on suspension. |
| `GET /admin/security-logs` | GET | Admin-Only | Real-time platform security audit log monitoring. |
| `GET /admin/diagnostics` | GET | Admin-Only | Operational health: SQLite table counts, WAL journal mode, active sessions. |
| `GET /admin/ocr-health` | GET | Admin-Only | Tesseract engine status, Bengali language pack (`ben`), PIL preprocessor health. |
| `GET /admin/fraud-rules` | GET | Admin-Only | Versioned fraud detection rule catalog (DS-01, DS-02, DS-03, KHAS-01) and thresholds. |
| `POST /admin/backups/checkpoint` | POST | Admin-Only | Triggers audited SQLite WAL checkpoint (PASSIVE/FULL). |

---

## 3. Database Schema Implementation

All security tables reside directly in `data/generated/full_scale/landtech_synthetic.db` with foreign key relationships and performance indexes:

```sql
-- 1. Users Identity & State
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    role TEXT NOT NULL DEFAULT 'CITIZEN' CHECK(role IN ('CITIZEN', 'BUYER', 'OFFICER', 'ADMINISTRATOR')),
    status TEXT NOT NULL DEFAULT 'UNVERIFIED' CHECK(status IN ('UNVERIFIED', 'ACTIVE', 'SUSPENDED')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_login_at TEXT
);

-- 2. Cryptographic OTP Verification Challenges
CREATE TABLE IF NOT EXISTS auth_challenges (
    challenge_id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    user_id TEXT,
    purpose TEXT NOT NULL CHECK(purpose IN ('EMAIL_VERIFY', 'PWD_RESET', 'STEP_UP_AUTH')),
    code_hash TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 5,
    resend_available_at TEXT NOT NULL,
    used_at TEXT,
    created_at TEXT NOT NULL
);

-- 3. Persistent User Sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    token_hash TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    expires_at TEXT NOT NULL,
    is_revoked INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 4. Immutable Security Audit Logs
CREATE TABLE IF NOT EXISTS security_audit_logs (
    log_id TEXT PRIMARY KEY,
    user_id TEXT,
    actor_email TEXT NOT NULL,
    action TEXT NOT NULL,
    ip_address TEXT,
    details_json TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

-- 5. Citizen Explicit Linked Parcels
CREATE TABLE IF NOT EXISTS citizen_parcels (
    link_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    parcel_id TEXT NOT NULL,
    ownership_type TEXT NOT NULL,
    share_percent REAL NOT NULL,
    khatian_no TEXT NOT NULL,
    tax_status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id)
);

-- 6. Citizen Service & Mutation Applications
CREATE TABLE IF NOT EXISTS citizen_applications (
    app_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    parcel_id TEXT NOT NULL,
    app_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'SUBMITTED',
    details_json TEXT NOT NULL,
    hearing_date TEXT,
    officer_notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id)
);

-- 7. Citizen Notifications & Summons
CREATE TABLE IF NOT EXISTS citizen_notifications (
    notif_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    notif_type TEXT NOT NULL DEFAULT 'APPLICATION',
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 8. Buyer Review Requests
CREATE TABLE IF NOT EXISTS buyer_review_requests (
    request_id TEXT PRIMARY KEY,
    buyer_id TEXT NOT NULL,
    parcel_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    urgency TEXT NOT NULL DEFAULT 'NORMAL',
    status TEXT NOT NULL DEFAULT 'PENDING_OFFICER_REVIEW',
    created_at TEXT NOT NULL,
    FOREIGN KEY (buyer_id) REFERENCES users(user_id),
    FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id)
);
```

---

## 4. Cryptographic Security Standards

1. **Password Hashing:** PBKDF2 with HMAC-SHA256, 100,000 iterations, and a cryptographically random 16-byte salt per user (`os.urandom(16)`). Passwords are never stored in plaintext.
2. **Session Signature:** HMAC-SHA256 signature using `SECRET_KEY`. Bearer token contains URL-safe base64 payload and signature: `<payload_b64>.<signature_b64>`.
3. **Session Revocation:** Every token is hashed via SHA-256 and matched against `user_sessions.token_hash`. If `is_revoked = 1` or account status is `SUSPENDED`, requests are rejected with `HTTP 401 Unauthorized`.
4. **OTP Storage:** OTP codes are hashed with SHA-256 before insertion into `auth_challenges.code_hash`. Plaintext OTPs are never stored in the database.
5. **Separation of Duties:** Administrators are strictly prohibited from judicial mutation decisions (`require_officer_role` returns 403 for `ADMINISTRATOR`). Officers cannot modify users or security logs.
