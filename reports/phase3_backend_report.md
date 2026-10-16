# DESHMRITTIKA / BHUMI-SYNC — Phase 3 Backend Engineering Report
**Project Name:** দেশমৃত্তিকা | DeshMrittika / Bhumi-Sync
**Platform Version:** 2.0.0
**Evaluation Date:** 2026-10-17
**Status:** COMPLETE & PASSING (10/10 automated tests passing)

---

## 1. Architectural Summary
The Phase 3 backend implements a high-throughput, deterministic REST API layer built on **FastAPI** and **SQLite3 WAL mode**, interfacing directly with the 100,000-parcel relational synthetic dataset (`landtech_synthetic.db`, 109.35 MB).

All six problem tracks from the LandTech 2026 Rulebook v1.2 are mapped directly into modular services and endpoints:

| Rulebook Track | Service Component | Endpoints | Key Functionality |
| :--- | :--- | :--- | :--- |
| **System & Health** | `main.py` | `GET /api/v1/health`, `GET /` | Database connectivity, versioning, uptime status. |
| **RBAC & Auth** | `services/auth.py` | `POST /api/v1/auth/login`, `GET /api/v1/auth/me` | HMAC-SHA256 session tokens, server-side RBAC guards (`CITIZEN`, `BUYER`, `OFFICER`, `ADMINISTRATOR`). |
| **Search Engine** | `services/search.py` | `GET /api/v1/search` | Multi-field indexed search across Mouza, Dag, Khatian, Deed, and Proprietor name. |
| **Cadastral Profiles** | `services/parcel_profile.py` | `GET /api/v1/parcels/{id}`, `GET /api/v1/parcels/{id}/geojson` | 14-entity relational joins, historical deed chains, GeoJSON cadastral polygons. |
| **P3: Catch Fraud** | `services/verification.py` | `GET /api/v1/verification/evaluate/{id}`, `GET /api/v1/verification/cases` | Deterministic double-selling detector (DS-01 to DS-05), unmutated deed conflicts, risk triage. |
| **P5: Due Diligence** | `services/due_diligence.py` | `GET /api/v1/due-diligence/{id}` | Citizen 5-point buyer due-diligence safety checklist, rating (SAFE/CAUTION/HIGH_RISK/CRITICAL). |
| **P4: Smart e-Mutation** | `services/mutation.py` | `POST /api/v1/mutations/pre-check`, `POST /api/v1/mutations/{id}/status` | Sub-Registry to AC Land bridge, pre-checks against khas, tax arrears, and competing transfers. |
| **P2: Integrity & Tamper** | `services/integrity.py` | `POST /api/v1/documents/verify-integrity` | SHA-256 cryptographic hash verification, QR verification, bit-level tamper detection. |
| **P1: Digitize Records** | `services/ocr.py` | `POST /api/v1/documents/upload-ocr` | Real Tesseract OCR pipeline with honest language pack reporting (eng/ben). |
| **Officer Triage Queue** | `api/officer.py` | `GET /api/v1/officer/queue`, `POST /api/v1/officer/decision`, `GET /api/v1/officer/audit-logs` | AC Land / Sub-Registrar triage queue, immutable review logs, and audit trail. |

---

## 2. Automated Test Suite Execution Results
The test suite was executed against the active 100,000-parcel dataset using Python's standard `unittest` and FastAPI's `TestClient`.

```
test_01_health_and_root (tests.test_backend.TestBackendEndpoints.test_01_health_and_root)
Verify API health check, database status, and supported tracks. ... ok
test_02_authentication_and_rbac (tests.test_backend.TestBackendEndpoints.test_02_authentication_and_rbac)
Verify session issuance, authentication checks, and strict RBAC enforcement. ... ok
test_03_universal_search (tests.test_backend.TestBackendEndpoints.test_03_universal_search)
Verify indexed search across Dag, Mouza, Khatian, and Parcel ID. ... ok
test_04_parcel_profile_and_geojson (tests.test_backend.TestBackendEndpoints.test_04_parcel_profile_and_geojson)
Verify full 14-entity relational linked profile and GeoJSON endpoint. ... ok
test_05_p3_double_selling_evaluation (tests.test_backend.TestBackendEndpoints.test_05_p3_double_selling_evaluation)
Verify DS-01 double-selling detection on seeded fraud parcel and DS-02 negative control. ... ok
test_06_p5_buyer_due_diligence_dossier (tests.test_backend.TestBackendEndpoints.test_06_p5_buyer_due_diligence_dossier)
Verify 5-Point Safety Check due-diligence dossier generation. ... ok
test_07_officer_review_decision_and_audit (tests.test_backend.TestBackendEndpoints.test_07_officer_review_decision_and_audit)
Verify officer triage queue, decision submission, and persistent audit logging. ... ok
test_08_p4_mutation_precheck (tests.test_backend.TestBackendEndpoints.test_08_p4_mutation_precheck)
Verify Smart e-Mutation pre-checks against khas, tax arrears, and active disputes. ... ok
test_09_p2_cryptographic_document_integrity (tests.test_backend.TestBackendEndpoints.test_09_p2_cryptographic_document_integrity)
Verify SHA-256 tamper detection on authentic vs modified document binaries. ... ok
test_10_p1_document_ocr_pipeline (tests.test_backend.TestBackendEndpoints.test_10_p1_document_ocr_pipeline)
Verify Tesseract OCR execution and honest status reporting. ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.706s

OK
```

### Test Assertions Summary:
1. **RBAC Isolation:** Requesting `/api/v1/officer/queue` with a Citizen JWT returned HTTP 403 (`Access denied: Role 'CITIZEN' lacks authorized officer review permissions`), confirming security boundaries.
2. **Double-Selling Precision:**
   - Seeded fraud parcel `BD-PAR-000101` triggered `DS-01` Critical alert (score 95, `is_safe_for_transaction: false`).
   - Clean resale negative control parcel `BD-PAR-001001` triggered `DS-02` Clean Sequential chain (score 0, `is_safe_for_transaction: true`).
3. **Cryptographic Integrity:** Authentic deed binary matched registered SHA-256 hash (`VERIFIED_AUTHENTIC`). Tampered byte sequence was immediately detected and rejected (`TAMPER_DETECTED_OR_UNREGISTERED`).
4. **Audit Trail:** Review decisions by officers are immutably logged with sequential `LOG-XXXXXX` IDs and retrievable via `/api/v1/officer/audit-logs`.
