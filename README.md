# দেশমৃত্তিকা | DeshMrittika (BHUMI-SYNC)
> **Tagline:** *Your Land, Our Responsibility (আপনার জমি, আমাদের দায়িত্ব)*  
> **Event:** LandTech 2026 Innovation Hackathon (v1.2)  
> **Host:** Department of Computer Science and Engineering (CSE) & CSE-TECH, supported by Department of Law, Daffodil International University (DIU).  
> **Scope:** Full Rulebook Track Coverage (**P1 through P6**), with primary showcase on **P3 — Catch Fraud & Double-Selling**.

---

## 📌 Executive Overview
**DeshMrittika (দেশমৃত্তিকা / Bhumi-Sync)** is an authentic, synthetic-data-powered land-record verification, cadastral mapping, and buyer due-diligence platform designed for Bangladesh.

In Bangladesh, over **75% of subordinate court litigations** stem from land disputes—most critically **fraudulent double-selling**. The root cause is an institutional information lag: conveyances registered at the Sub-Registry Office (under the Ministry of Law) take weeks or months to be mutated and updated at the AC Land office (under the Ministry of Land). During this window, malicious proprietors exploit the unmutated state to resell identical cadastral plots (*Dags*) to multiple unsuspecting buyers.

DeshMrittika bridges this gap through a unified **14-entity relational data model**, a **deterministic multi-rule fraud detection engine**, and an **interactive WGS-84 cadastral GIS viewer** operating across **100,000 synthetic parcels** with **zero real citizen PII**.

---

## 🏆 Problem Tracks Addressed (Rulebook Traceability)

| Track | Problem Name (Rulebook v1.2) | DeshMrittika Solution & Technical Mechanism | Status |
| :--- | :--- | :--- | :--- |
| **P1** | **Digitize Old Records** | Tesseract Optical Character Recognition (OCR) pipeline extracting structured fields from legacy CS/SA/RS/BS Khatians with honest language confidence reporting. | `VERIFIED` |
| **P2** | **Verify Deeds & Ownership** | Cryptographic SHA-256 document hashing, QR verification, and bit-level tamper detection catching modified or forged deeds. | `VERIFIED` |
| **P3** | **Catch Fraud & Double-Selling** *(Primary Showcase)* | Deterministic multi-rule fraud engine (DS-01 to DS-05) detecting concurrent unmutated transfers, over-sales, and seller identity mismatches with **100% recall** and **0.0% false positives**. | `VERIFIED` |
| **P4** | **Smart e-Mutation & Registry** | Sub-Registry to AC Land automated bridge with a 4-step mutation lifecycle tracker and pre-checks against khas, tax arrears, and injunctions. | `VERIFIED` |
| **P5** | **Check Before You Buy** | Citizen Single-Window Due Diligence Portal with a **5-Point Safety Shield** (Baya deeds, Mutation status, Civil suits, Tax arrears, Khas/Corridors) and printable dossier. | `VERIFIED` |
| **P6** | **Cadastral Boundary & Khas Protection** *(Innovation)* | WGS-84 Leaflet cadastral GIS overlaying parcel polygons against Government 1-No Khas land and the 100-meter Dhaka-Aricha Highway acquisition corridor. | `VERIFIED` |

---

## 🏗️ Architecture & Technology Stack

```
                              ┌──────────────────────────────────────────────┐
                              │            DESHMRITTIKA PLATFORM             │
                              │        (Bengali-First Responsive Web)        │
                              └──────────────────────┬───────────────────────┘
                                                     │
                     ┌───────────────────────────────┴───────────────────────────────┐
                     ▼                                                               ▼
        ┌─────────────────────────┐                                     ┌─────────────────────────┐
        │  Citizen Portal (P5)    │                                     │  Officer Triage (P3/P4) │
        │  • Universal Search     │                                     │  • AC Land Review Queue │
        │  • 5-Point Safety Shield│                                     │  • Side-by-Side Diff    │
        │  • Leaflet Cadastral Map│                                     │  • Immutable Audit Logs │
        └────────────┬────────────┘                                     └────────────┬────────────┘
                     │                                                               │
                     └───────────────────────────────┬───────────────────────────────┘
                                                     ▼
                                      ┌─────────────────────────────┐
                                      │   FastAPI REST Layer (v1)   │
                                      │   • Pydantic Type Contracts │
                                      │   • HMAC-SHA256 Token RBAC  │
                                      └──────────────┬──────────────┘
                                                     │
         ┌───────────────────────────────────────────┼───────────────────────────────────────────┐
         ▼                                           ▼                                           ▼
┌──────────────────┐                       ┌──────────────────┐                        ┌──────────────────┐
│ DoubleSelling    │                       │ DocumentIntegrity│                        │ Spatial & Tax    │
│ Engine (DS01-05) │                       │ (SHA-256 / OCR)  │                        │ Query Services   │
└────────┬─────────┘                       └────────┬─────────┘                        └────────┬─────────┘
         │                                          │                                           │
         └──────────────────────────────────────────┼───────────────────────────────────────────┘
                                                    ▼
                                  ┌───────────────────────────────────┐
                                  │   SQLite3 WAL Relational Engine   │
                                  │   • 100,000 Parcels (109.35 MB)   │
                                  │   • 14 Normalized Schema Tables   │
                                  │   • Sub-Millisecond Indexed B-Tree│
                                  └───────────────────────────────────┘
```

- **Backend:** Python 3.13, FastAPI 0.139, Uvicorn, Pydantic, SQLite3 (WAL mode).
- **Frontend:** Responsive Vanilla CSS, Semantic HTML5, Vanilla JavaScript, Leaflet.js (GIS), Google Fonts (*Hind Siliguri* & *Inter*).
- **OCR & Cryptography:** Tesseract OCR (Pytesseract), Pillow, SHA-256 cryptographic hashing.
- **Reporting:** ReportLab 4.5.1 (3-Page Concept Note PDF generation adhering to Rulebook Section 8).

---

## 📊 Synthetic Dataset Provenance & Scale
All records are strictly synthetic and deterministically generated using seed `20261018`:

- **Pilot Jurisdiction:** Savar Upazila, Dhaka District (BBS Geocode `26` / `2672`).
- **Mouzas:** Aminbazar (JL 26), Birulia (JL 27), Savar Municipality (JL 28).
- **Parcels:** 100,000 cadastral plots (109.35 MB database).
- **Proprietors:** 20,000 fictional Bengali owners (Zero real citizen names, NIDs, or phone numbers).
- **Deeds & Transactions:** 58,333 registered conveyances and 31,000 ownership history events.
- **e-Mutations:** 57,583 mutation records (covering Approved, Under Inspection, and Pending).
- **Tax Holdings:** 100,000 annual land development tax records.
- **Double-Selling Ground Truth:** Exactly **500 distinct DS-01 fraud scenarios** (`SCN-DS1-0001` to `SCN-DS1-0500`) cataloged in `data/scenarios/scenario_catalog.csv`.
- **Negative Control Cases:** 15,000 clean sequential resale chains (`DS-02`) with **0.0% false positives**.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Google Chrome / Modern Web Browser
- Tesseract OCR (Optional, for P1 local OCR extraction)

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-team/LandTechDeshMrittika.git
cd LandTechDeshMrittika
pip install fastapi uvicorn pydantic pillow pytesseract reportlab pypdf python-multipart
```

### 3. Run Automated Test Suite
Verify all 10 automated test suites covering RBAC, double-selling detection, and document integrity:
```bash
python3 -m unittest tests/test_backend.py -v
```
*Expected Output:* `Ran 10 tests in 0.706s ... OK`

### 4. Launch Application Server
Start the local FastAPI server:
```bash
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

### 5. Access the Web Prototype
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```
- **Interactive OpenAPI Documentation:** `http://127.0.0.1:8000/docs`
- **Health Check Endpoint:** `http://127.0.0.1:8000/api/v1/health`

---

## 🔑 Demo User Accounts

| Role | Email Address | Access Level & Privileges |
| :--- | :--- | :--- |
| **Citizen (সাধারণ নাগরিক)** | `citizen@example.com` | Public Search, 5-Point Safety Shield, Leaflet Map, Printable Dossier. |
| **Buyer (ভূমি ক্রেতা)** | `buyer@example.com` | Prospective Buyer due diligence, e-Mutation simulator pre-check. |
| **AC Land (সহকারী কমিশনার - ভূমি)** | `officer@savar.land.gov.bd` | Officer Triage Queue, Side-by-Side Deed Diff, Decision recording, Audit logs. |
| **System Administrator** | `admin@deshmrittika.gov.bd` | Full system oversight and audit trail inspection. |

---

## 🤖 Declaration of AI Tools Used
*In compliance with LandTech 2026 Rulebook v1.2, Section 8 (Deliverable 2) & Section 10 (Do's and Don'ts):*

The following AI tools and engineering assistants were utilized during the development of this prototype:
1. **Antigravity IDE & Gemini Advanced Agentic Coding:** Used for architectural design, Pydantic schema generation, test suite synthesis, and refactoring.
2. **Deterministic Mathematical Heuristics:** Used in `DoubleSellingEngine` for deterministic graph/timestamp rule matching (DS-01 to DS-05) without stochastic LLM hallucination.
3. **Pytesseract (Google Tesseract OCR Engine):** Used for document optical character recognition pipelines.

*All source code, database structures, algorithms, and legal constraints were designed, validated, and tested directly by the team.*

---

## ⚖️ Ethical, Privacy & Legal Constraints
1. **Zero Real Citizen PII:** Adhering strictly to Rulebook Section 10, no real names, NIDs, phone numbers, or actual deed records were used. All data is synthetically generated using documented structural formats.
2. **Zero Live Scraping:** No government servers or live portals were scraped or stress-tested.
3. **Advisory Risk Triage Notice:** As required by Section 4 of the State Acquisition and Tenancy Act 1950, DeshMrittika is an administrative risk-triage advisory tool. It does not conclusively decree ownership or substitute for judicial or AC Land statutory authority.

---

## 📁 Repository Directory Structure

```
LandTechDeshMrittika/
├── backend/
│   └── app/
│       ├── main.py                  # FastAPI application entry point & routes
│       ├── config.py                # Environment and database configuration
│       ├── database.py              # SQLite connection provider with dict rows
│       ├── api/                     # REST API routers (auth, search, verification, officer, etc.)
│       ├── schemas/models.py        # Pydantic data contracts
│       └── services/                # Core business logic (DoubleSellingEngine, OCR, Integrity, Due Diligence)
├── frontend/
│   ├── index.html                   # Single-Page Web Application
│   ├── css/styles.css               # Responsive design system & glassmorphism
│   └── js/
│       ├── api.js                   # API client layer with JWT session handling
│       └── app.js                   # UI controller, Leaflet mapping & triage workflow
├── data/
│   ├── source_register.csv          # Classified Level A–E source inventory
│   ├── scenarios/                   # 500 ground-truth DS-01 fraud scenarios catalog
│   └── generated/
│       ├── dry_run/                 # 1,000-parcel dry-run dataset (preserved)
│       └── full_scale/              # 100,000-parcel database (landtech_synthetic.db, 109.35 MB)
├── docs/
│   ├── PROJECT_BLUEPRINT.md         # Comprehensive engineering specification (v2.0)
│   ├── RULEBOOK_TRACEABILITY_MATRIX.md # Detailed P1–P6 traceability matrix
│   ├── DEMO_SCRIPT.md               # 90-second video demo script
│   ├── DESHMRITTIKA_CONCEPT_NOTE.pdf# Official 3-Page Concept Note PDF
│   └── landtech_hackathon_rulebook.pdf # Official Rulebook v1.2
├── generators/
│   ├── generate_synthetic_dataset.py# Batched SQLite generator (100k parcels in 5.39s)
│   ├── validate_dataset.py          # 12-point automated integrity validator
│   └── generate_concept_note_pdf.py # 3-page ReportLab PDF generator
├── reports/
│   ├── full_scale_validation_report.md # 12/12 integrity test report
│   └── phase3_backend_report.md     # Backend test suite results
├── tests/
│   └── test_backend.py              # Automated integration & unit test suite
└── README.md                        # Technical overview & submission guide
```

---

## 👥 Team & Mentorship
- **Team Name:** DeshMrittika / Bhumi-Sync
- **Student Team Leader:** Department of CSE, Daffodil International University (DIU)
- **Student Member:** Department of CSE, Daffodil International University (DIU)
- **Faculty Mentor:** Faculty of Science & Information Technology, DIU
- **Industry Mentor:** LandTech / GovTech Industry Specialist
- **Contact:** `csetech@diu.edu.bd`
