# BHUMI-SYNC — Synthetic Land Officials Directory Implementation Report

**Document ID:** `AUDIT-OFFICIALS-2026-BD`  
**Date:** 2026-10-17  
**Platform Version:** DeshMrittika / BHUMI-SYNC v2.3  
**Status:** IMPLEMENTED, SEEDED & AUTOMATED TESTS VERIFIED  

---

## 1. Executive Summary

To provide realistic end-to-end simulation of citizen-to-government (C2G) and inter-agency workflows (such as mutation review, physical demarcation hearings, and registry deed cross-referencing), BHUMI-SYNC v2.3 incorporates a database-backed directory of **Land Administration Officials and Offices** across Bangladesh.

In strict adherence to project ethical guidelines, **no real persons' names, photos, employee numbers, phone numbers, or email addresses are used**. The directory comprises synthetic, realistic demo profiles created exclusively for system demonstration and training.

---

## 2. Ethical Safeguards & Anti-Impersonation Design

| Dimension | Safeguard Rule | Implementation Details |
|---|---|---|
| **Name Safeguard** | No real civil servant names | All profiles use clearly marked fictional names with explicit demo tags (e.g., `মো: রিয়াজুল ইসলাম (ডেমো কর্মকর্তা)` / `Kazi Farhana Akhter (Demo)`). |
| **Email Safeguard** | No real emails; reserved domain only | All email addresses use the reserved fictional demo sub-domain: `*@demo.land.gov.bd`. No mail is ever routed to real public mailboxes. |
| **Phone Safeguard** | Non-routable fictional phone numbers | All telephone numbers use the fictional demonstration block: `+880 1700-000XXX (ডেমো)`. |
| **Portrait Safeguard** | Original SVG vector avatars only | No real photographs or scraped images. 6 custom, professional SVG vector avatars (`portrait_male_1..3.svg`, `portrait_female_1..3.svg`) with embedded `DEMO OFFICIAL` watermark ribbons. |
| **Provenance Label** | Immutable database label | Every official record contains `provenance = "DEMO OFFICIAL — NOT A REAL PERSON"`. |
| **UI Watermark** | Unmistakable UI badges | Every profile card and modal detail prominently displays a high-visibility badge: `DEMO OFFICIAL — NOT A REAL PERSON`. |

---

## 3. Supported Land Administration Designations

The catalog supports authentic designations across the Bangladesh land management structure without assuming every designation exists at every office:

```
Ministry of Land / DLRS
  ├── Assistant Commissioner (Land) [AC_LAND] (Upazila Revenue Circle)
  ├── Kanungo [KANUNGO] (Revenue supervision & mutation inspection)
  ├── Senior Surveyor [SURVEYOR] (Cadastral measurement & boundary demarcation)
  ├── Head Assistant cum Peshkar [PESHKAR] (Summons, hearing diary & record room)
  ├── Union Land Assistant Officer (Tohsildar) [ULAO] (Union revenue collection)
  └── Union Land Sub-Assistant Officer [ULSAO] (Field inspection & spot verification)

Ministry of Law, Justice and Parliamentary Affairs (Registration Directorate)
  └── Sub-Registrar [SUB_REGISTRAR] (Deed registration & stamp duty audit)
```

---

## 4. Database Schema

### 4.1 `land_offices` Table
```sql
CREATE TABLE land_offices (
    office_id VARCHAR(32) PRIMARY KEY,
    office_name_en VARCHAR(128) NOT NULL,
    office_name_bn VARCHAR(128) NOT NULL,
    office_type VARCHAR(32) NOT NULL,
    division_id VARCHAR(16) NOT NULL REFERENCES geo_divisions(division_id),
    district_id VARCHAR(16) NOT NULL REFERENCES geo_districts(district_id),
    upazila_id VARCHAR(16) NOT NULL REFERENCES geo_upazilas(upazila_id),
    union_id VARCHAR(16) REFERENCES geo_unions(union_id),
    address_en TEXT,
    address_bn TEXT,
    phone_demo VARCHAR(64),
    email_demo VARCHAR(64),
    latitude REAL,
    longitude REAL,
    status VARCHAR(16) DEFAULT 'ACTIVE',
    provenance VARCHAR(64) DEFAULT 'SYNTHETIC_DEMO_OFFICE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 `land_officials` Table
```sql
CREATE TABLE land_officials (
    official_id VARCHAR(32) PRIMARY KEY,
    name_en VARCHAR(96) NOT NULL,
    name_bn VARCHAR(96) NOT NULL,
    designation_en VARCHAR(96) NOT NULL,
    designation_bn VARCHAR(96) NOT NULL,
    designation_code VARCHAR(32) NOT NULL,
    office_id VARCHAR(32) NOT NULL REFERENCES land_offices(office_id),
    employee_number_demo VARCHAR(32) UNIQUE NOT NULL,
    email_demo VARCHAR(96) NOT NULL,
    phone_demo VARCHAR(64) NOT NULL,
    portrait_image VARCHAR(128) NOT NULL,
    jurisdiction_en TEXT,
    jurisdiction_bn TEXT,
    status VARCHAR(16) DEFAULT 'ACTIVE',
    provenance VARCHAR(96) DEFAULT 'DEMO OFFICIAL — NOT A REAL PERSON',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. Seeded Inventory

- **Total Synthetic Land Offices**: 14
  - AC Land Offices: 8 (Savar, Gazipur Sadar, Patiya, Sylhet Sadar, Boalia/Rajshahi, Kotwali/Khulna, Barishal Sadar, Rangpur Sadar)
  - Sub-Registry Offices: 2 (Savar, Joydebpur)
  - Settlement Offices (DLRS): 1 (Savar)
  - Union Land Offices: 3 (Aminbazar, Birulia, Joydebpur Union)
- **Total Synthetic Officials**: 17
  - AC (Land): 8
  - Kanungo: 2
  - Senior Surveyor: 2
  - Union Land Assistant Officer (ULAO): 2
  - Union Land Sub-Assistant Officer (ULSAO): 1
  - Sub-Registrar: 1
  - Head Assistant cum Peshkar: 1

---

## 6. Directory API Endpoints

| Method | Endpoint | Query Parameters | Description |
|---|---|---|---|
| `GET` | `/api/v1/officials` | `division_id`, `district_id`, `upazila_id`, `designation`, `office_type`, `search`, `limit`, `offset` | Filtered list of synthetic officials with count, pagination, and office details |
| `GET` | `/api/v1/officials/{id}` | None | Detailed profile with office details, jurisdiction scope, and provenance label |
| `GET` | `/api/v1/officials/meta/designations` | None | Returns active catalog of designations with Bengali/English titles |
| `GET` | `/api/v1/officials/offices` | `division_id`, `district_id`, `office_type` | List of administrative offices with coordinates for map display |
| `GET` | `/api/v1/officials/offices/{id}` | None | Single office profile with assigned officials list |

---

## 7. Frontend User Experience

1. **Dedicated Workspace (`#page-officials-directory`)**:
   - Integrated with role-based navigation for Citizen, Buyer, Officer, and Administrator.
   - Cascading filter bar: Division → District → Upazila → Designation → Office Type.
   - Debounced keyword search for fast auto-filtering across name, designation, and office.
   - English / Bengali language toggle with real-time UI text updates.
2. **Interactive Cards Grid**:
   - Responsive CSS Grid (`repeat(auto-fill, minmax(330px, 1fr))`).
   - SVG avatar portraits with `DEMO OFFICIAL` watermark.
   - Direct button `[ 🗺️ ম্যাপে কার্যালয় ]`: Navigates to `#page-map`, flies Leaflet viewport to the office coordinates, and opens the office information popup.
3. **Full Profile Modal (`#official-detail-modal`)**:
   - High-fidelity modal displaying complete jurisdiction scope, office address, demo contact credentials, and official role provenance.
