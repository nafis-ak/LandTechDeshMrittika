# BHUMI-SYNC — Core Tracks Test Execution Results & Observed Logs

**Date of Execution:** October 17, 2026  
**Environment:** macOS (Darwin 24.3.0 arm64), Python 3.13.2, SQLite 3.43.2, Tesseract 5.5.2  
**Database:** `data/generated/full_scale/landtech_synthetic.db` (115,277,824 bytes)  
**Overall Regression Result:** ✅ **66 of 66 Tests Passed (100% Passing, 0 Failures, 0 Errors, 0 Skipped)**  

---

## 1. Full Test Suite Discovery Run

**Command:**
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

**Observed Execution Log:**
```
/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
  from starlette.testclient import TestClient as TestClient  # noqa

📧 [DEV EMAIL DISPATCHED] -> To: test_e1b88f7e_citizen@example.com | Subject: 'দেশমৃত্তিকা — আপনার ৬-সংখ্যার ইমেইল যাচাইকরণ ওটিপি কোড' | OTP: 806107
....
📧 [DEV EMAIL DISPATCHED] -> To: test_b0426892_verify@example.com | Subject: 'দেশমৃত্তিকা — আপনার ৬-সংখ্যার ইমেইল যাচাইকরণ ওটিপি কোড' | OTP: 169413
.
📧 [DEV EMAIL DISPATCHED] -> To: test_b1f65dcc_wrong_otp@example.com | Subject: 'দেশমৃত্তিকা — আপনার ৬-সংখ্যার ইমেইল যাচাইকরণ ওটিপি কোড' | OTP: 528650
.
📧 [DEV EMAIL DISPATCHED] -> To: test_0939c6d0_reuse@example.com | Subject: 'দেশমৃত্তিকা — আপনার ৬-সংখ্যার ইমেইল যাচাইকরণ ওটিপি কোড' | OTP: 207013
.
📧 [DEV EMAIL DISPATCHED] -> To: test_5bdeaaeb_resend@example.com | Subject: 'দেশমৃত্তিকা — আপনার ৬-সংখ্যার ইমেইল যাচাইকরণ ওটিপি কোড' | OTP: 085006
.
📧 [DEV EMAIL DISPATCHED] -> To: test_a837de8c_unver_login@example.com | Subject: 'দেশমৃত্তিকা — আপনার ৬-সংখ্যার ইমেইল যাচাইকরণ ওটিপি কোড' | OTP: 578083
.
📧 [DEV EMAIL DISPATCHED] -> To: test_1a447741_bad_pwd@example.com | Subject: 'দেশমৃত্তিকা — আপনার ৬-সংখ্যার ইমেইল যাচাইকরণ ওটিপি কোড' | OTP: 986022
..
📧 [DEV EMAIL DISPATCHED] -> To: test_58063793_pwd_reset@example.com | Subject: 'দেশমৃত্তিকা — আপনার ৬-সংখ্যার ইমেইল যাচাইকরণ ওটিপি কোড' | OTP: 551454

📧 [DEV EMAIL DISPATCHED] -> To: test_58063793_pwd_reset@example.com | Subject: 'দেশমৃত্তিকা — পাসওয়ার্ড রিসেট ভেরিফিকেশন কোড' | OTP: 112845

📧 [DEV EMAIL DISPATCHED] -> To: test_58063793_pwd_reset@example.com | Subject: 'দেশমৃত্তিকা নিরাপত্তা সতর্কতা: পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে' | OTP: None
..........
📧 [DEV EMAIL DISPATCHED] -> To: test_ff9e941d_citizen_b@example.com | Subject: 'দেশমৃত্তিকা — আপনার ৬-সংখ্যার ইমেইল যাচাইকরণ ওটিপি কোড' | OTP: 230800
.
📧 [DEV EMAIL DISPATCHED] -> To: test_81dff2e6_suspendee@example.com | Subject: 'দেশমৃত্তিকা — আপনার ৬-সংখ্যার ইমেইল যাচাইকরণ ওটিপি কোড' | OTP: 516788
............................................
----------------------------------------------------------------------
Ran 66 tests in 83.273s

OK
```

---

## 2. Dedicated Core Tracks Audit Suite

**Command:**
```bash
python3 -m unittest tests/test_tracks_audit.py
```

**Observed Execution Log:**
```
Ran 15 tests in 6.329s

OK (15 of 15 Passing)
```

**Individual Test Verification Breakdown:**
- `test_p1_01_real_ocr_execution_and_tokens`: PASS — Tesseract 5.5.2 extracted deed tokens from PNG (confidence > 60%).
- `test_p1_02_pdf_multi_page_support`: PASS — PyMuPDF rasterized multi-page PDF at 250 DPI.
- `test_p1_03_invalid_and_empty_file_handling`: PASS — HTTP 400 on empty file; unsupported type gracefully handled.
- `test_p2_01_authentic_sha256_match`: PASS — Real PNG hash matched `documents` record with `is_authentic=true`.
- `test_p2_02_one_byte_tamper_detection`: PASS — 1-bit modification flagged as `TAMPER_DETECTED_OR_UNREGISTERED`.
- `test_p2_03_unregistered_file`: PASS — Arbitrary unregistered document correctly evaluated as unauthentic.
- `test_p3_01_seeded_fraud_detection_metrics`: PASS — 50 positive DS-01 and 50 clean DS-02 evaluated without false positives/negatives.
- `test_p3_02_officer_triage_decision_and_audit_persistence`: PASS — Attributable decision inserted into `review_logs`.
- `test_p4_01_citizen_application_submission_and_persistence`: PASS — Application created, tracked, and visible in officer queue.
- `test_p4_02_mutation_precheck_rules`: PASS — Automated pre-check blocks Khas land mutation.
- `test_p5_01_search_and_due_diligence_dossier`: PASS — 5-point dossier generated; NID and officer notes omitted.
- `test_p5_02_buyer_review_request_submission`: PASS — High-risk parcel review request created and retrieved.
- `test_p6_01_parcel_geojson_and_wgs84_crs`: PASS — Valid WGS84 coordinates in Savar geographical bounding box.
- `test_p6_02_khas_land_records_identification`: PASS — Government 1-No. Khas land triggers `CRITICAL_BLOCKED`.
- `test_p6_03_gis_intersection_limitations`: PASS — Verified that dynamic acquisition intersection is currently uncomputed/mocked.

---

## 3. Dedicated Fraud Detection Performance Metrics (500 Scenarios)

**Command:**
```bash
python3 -c "
import csv, sqlite3
from backend.app.services.verification import DoubleSellingEngine
from backend.app.config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
conn.row_factory = sqlite3.Row

# 500 positive seeded scenarios
scenarios = []
with open('data/scenarios/scenario_catalog.csv', 'r', encoding='utf-8') as f:
    scenarios = list(csv.DictReader(f))

tp = sum(1 for sc in scenarios if 'DS-01' in [f.finding_code for f in DoubleSellingEngine.evaluate_parcel(conn, sc['parcel_id']).findings])
fn = len(scenarios) - tp

# 500 clean negative control parcels
cur = conn.cursor()
cur.execute(\"SELECT parcel_id FROM verification_cases WHERE finding_code = 'DS-02' LIMIT 500\")
clean_parcels = [r[0] for r in cur.fetchall()]

fp = sum(1 for p in clean_parcels if 'DS-01' in [f.finding_code for f in DoubleSellingEngine.evaluate_parcel(conn, p).findings])
tn = len(clean_parcels) - fp

precision = tp / (tp + fp)
recall = tp / (tp + fn)
f1 = 2 * (precision * recall) / (precision + recall)

print(f'True Positives:  {tp} / {len(scenarios)}')
print(f'False Negatives: {fn}')
print(f'True Negatives:  {tn} / {len(clean_parcels)}')
print(f'False Positives: {fp}')
print(f'Precision:       {precision*100:.2f}%')
print(f'Recall:          {recall*100:.2f}%')
print(f'F1 Score:        {f1*100:.2f}%')
"
```

**Observed Output:**
```
True Positives:  500 / 500
False Negatives: 0
True Negatives:  500 / 500
False Positives: 0
Precision:       100.00%
Recall:          100.00%
F1 Score:        100.00%
```

---

## 4. Optical Character Recognition (OCR) Execution Benchmark

**Command:**
```bash
python3 -c "
from backend.app.services.ocr import DocumentOCRService

for fname in ['sample_deed_authentic.png', 'sample_porcha.png', 'sample_khatian.pdf']:
    path = f'frontend/assets/samples/{fname}'
    with open(path, 'rb') as f:
        data = f.read()
    res = DocumentOCRService.process_document(data, fname)
    print(f'File: {fname} | Status: {res[\"ocr_status\"]} | Conf: {res[\"confidence_score\"]}% | Chars: {res[\"char_count\"]} | Time: {res[\"processing_time_ms\"]} ms')
"
```

**Observed Output:**
```
File: sample_deed_authentic.png | Status: SUCCESS | Conf: 84.1% | Chars: 1231 | Time: 3674.4 ms
File: sample_porcha.png         | Status: SUCCESS | Conf: 82.5% | Chars: 819  | Time: 2344.0 ms
File: sample_khatian.pdf        | Status: SUCCESS | Conf: 84.7% | Chars: 1227 | Time: 3464.2 ms
```

---

## 5. Cryptographic Document Tamper Detection Benchmark

**Command:**
```bash
python3 -c "
import hashlib
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)
with open('data/generated/full_scale/documents/DOC-000001_SAVAR-20261018-00003.png', 'rb') as f:
    authentic = f.read()

# Authentic test
res_auth = client.post('/api/v1/documents/verify-integrity', files={'file': ('doc.png', authentic, 'image/png')})
print('Authentic Status:', res_auth.status_code, res_auth.json()['status_label'])

# 1-byte modified test
tampered = bytearray(authentic)
tampered[-1] ^= 0x01
res_tamp = client.post('/api/v1/documents/verify-integrity', files={'file': ('doc_tamp.png', bytes(tampered), 'image/png')})
print('Tampered Status: ', res_tamp.status_code, res_tamp.json()['status_label'])
"
```

**Observed Output:**
```
Authentic Status: 200 VERIFIED_AUTHENTIC
Tampered Status:  200 TAMPER_DETECTED_OR_UNREGISTERED
```

---

## 6. Database Health & Record Integrity Check

**Command:**
```bash
python3 -c "
import sqlite3
from backend.app.config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
cur = conn.cursor()
cur.execute('PRAGMA integrity_check;')
print('PRAGMA integrity_check:', cur.fetchall())
cur.execute('PRAGMA foreign_key_check;')
print('PRAGMA foreign_key_check violations:', len(cur.fetchall()))

for t in ['parcels', 'owners', 'deeds', 'transactions', 'verification_cases', 'review_logs', 'citizen_applications']:
    cur.execute(f'SELECT COUNT(*) FROM {t}')
    print(f'{t:22}: {cur.fetchone()[0]:,}')
"
```

**Observed Output:**
```
PRAGMA integrity_check: [('ok',)]
PRAGMA foreign_key_check violations: 0
parcels               : 100,000
owners                : 20,000
deeds                 : 58,333
transactions          : 58,333
verification_cases    : 19,750
review_logs           : 37
citizen_applications  : 16
```
