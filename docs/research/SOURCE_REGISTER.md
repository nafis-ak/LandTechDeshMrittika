# OFFICIAL SOURCE REGISTER & PROVENANCE RECORD
## DESHMRITTIKA / BHUMI-SYNC
**Project:** DESHMRITTIKA / BHUMI-SYNC (দেশমৃত্তিকা)  
**Hackathon:** LandTech 2026 — LandTech Innovation Hackathon (DIU)  
**Document Version:** 1.0.0 (Phase 1 Source Research)  
**Access & Verification Date:** October 16–17, 2026  
**Safety & Compliance Standard:** Zero live scraping, zero real citizen NID/PII ingestion, strict attribution.

---

## 1. Source Classification & Provenance Taxonomy

To ensure legal integrity, ethical compliance, and academic rigor, every reference used in DESHMRITTIKA / BHUMI-SYNC is categorized into one of five provenance levels:

- **LEVEL A — Official Bangladesh Reference Information:** Public portals, published statutory forms, and government administrative guidelines. Used strictly for schema definitions, workflow logic, and terminology. *(No bulk scraping or private record collection permitted).*
- **LEVEL B — International Cadastral & Survey Standards:** Published open data portals (LINZ, Singapore INLIS) used as architectural reference models for cadastre-to-title linkage.
- **LEVEL C — Permitted Open Data:** Openly licensed geospatial datasets (OpenStreetMap, BBS Geocodes) used for basemaps and administrative bounding boxes under explicit open licenses (e.g., ODbL, CC BY 4.0).
- **LEVEL D — Synthetic Team-Generated Data:** Fictional identities, simulated transactions, synthetic document files, and demonstration scenarios created deterministically from fixed random seeds.
- **LEVEL E — Inaccessible / Unverified Sources:** Portals that were down, certificate-restricted, or authenticated. Explicitly marked as `UNVERIFIED / INACCESSIBLE` with documented fallbacks.

---

## 2. Complete Source Register Table

| Ref ID | Source Organization | Source URL | Access Date | Verification Status | Available Public Data / Artifacts | License / Terms of Use | Usage Restrictions | Project Implementation Role |
|---|---|---|---|---|---|---|---|---|
| **SRC-01** | **Ministry of Land (ভূমি মন্ত্রণালয়)** — Land Development Tax Portal | `https://portal.ldtax.gov.bd/` | 2026-10-16 | **VERIFIED (Active)** | • Holding registration form requirements<br>• Dakhila (দাখিলা) structure<br>• 16122 helpline reference | Crown Copyright / Gov Bangladesh. Public information portal. | Requires citizen NID SSO for actual tax records. No bulk scraping. | Informs `tax_records` schema (holding ID, tax year, demand vs. paid, Dakhila receipt status) for **P5**. |
| **SRC-02** | **Department of Land Records and Surveys (DLRS)** — ভূমি রেকর্ড ও জরিপ অধিদপ্তর | `https://dlrs.portal.gov.bd/` | 2026-10-16 | **INACCESSIBLE (Gov Notice)** | Domain returns official notice: *"Domain is not available: dlrs.portal.gov.bd. সাময়িকভাবে নিষ্ক্রিয় রাখা হয়েছে।"* | Not applicable during downtime. | Do not scrape or fabricate live DLRS API endpoints. | Fallback to statutory survey acts (BTA 1885, SATA 1950) for CS, SA, RS, BS survey hierarchies. |
| **SRC-03** | **Ministry of Land** — E-Porcha Portal (ই-পর্চা) | `https://www.eporcha.gov.bd/` | 2026-10-16 | **UNVERIFIED (Host Unresolved)** | Host unresolvable via public DNS at time of test. | Not applicable during outage. | Do not invent fake download links or private scrapers. | Fallback to published standard ROR (খতিয়ান) 8-column layout from land ministry manuals. |
| **SRC-04** | **Government of Bangladesh** — National Web Portal (তথ্য বাতায়ন) | `https://bangladesh.gov.bd/` | 2026-10-16 | **VERIFIED (Active)** | • BBS Geocode hierarchy (`bbs.gov.bd`)<br>• Laws of Bangladesh (`bdlaws.minlaw.gov.bd`)<br>• 16122 Smart Bhumi Seba link | Public information portal. | Commercial reproduction restricted without permission. | Authoritative administrative hierarchy (Division -> District -> Upazila -> Union -> Mouza) for Savar pilot. |
| **SRC-05** | **Land Information New Zealand (LINZ)** — Toitū Te Whenua | `https://data.linz.govt.nz/` | 2026-10-16 | **VERIFIED (Active)** | • NZ Cadastral Parcels Layer<br>• Property boundary schema (`id`, `appellation`, `status`, `area`) | Creative Commons Attribution 4.0 International (CC BY 4.0). | Requires attribution to "Land Information New Zealand". | Architectural model for multi-temporal parcel ownership and boundary math. |
| **SRC-06** | **Singapore Land Authority (SLA)** — INLIS Portal | `https://app.sla.gov.sg/inlis/` | 2026-10-16 | **VERIFIED (Active)** | • Integrated Land Information Service workflow<br>• Title search & encumbrance check<br>• Road/railway protection buffers | Singapore Government SLA copyright. Commercial purchase for actual records. | No automated scraping. Reference workflow only. | Informs **P5 ("Check Before You Buy")** dossier layout and **P6** acquisition corridor buffer check. |
| **SRC-07** | **OpenStreetMap Foundation (OSMF)** | `https://www.openstreetmap.org/` | 2026-10-16 | **VERIFIED (Active)** | • Open GIS basemap tiles<br>• Savar/Dhaka road networks & waterways | Open Database License (ODbL) 1.0. | Must display attribution: *"© OpenStreetMap contributors"*. | Leaflet interactive map basemap and coordinate bounding box for pilot Mouza. |
| **SRC-08** | **Laws of Bangladesh (Legislative Division, Ministry of Law)** | `http://bdlaws.minlaw.gov.bd/` | 2026-10-16 | **VERIFIED (Active)** | • State Acquisition & Tenancy Act 1950<br>• Registration Act 1908<br>• Transfer of Property Act 1882<br>• ARIPA 2017 (Acquisition Act) | Public statutory law texts. | Legal text reference. | Provides statutory rules for deed execution, registration, mutation necessity, and Khas definitions. |

---

## 3. Handling of Inaccessible Sources & Uncertainty Protocol

1. **`dlrs.portal.gov.bd` Downtime:**
   - *Status:* Inaccessible due to official government maintenance message.
   - *Protocol:* Documented as `INACCESSIBLE`. No live connectivity attempted. Structural definitions for Cadastral Survey (CS), Revisional Survey (RS), and Bangladesh Survey (BS) are derived from the *State Acquisition and Tenancy Act 1950* and published *Technical Rules of the Settlement Department*.
2. **`eporcha.gov.bd` DNS Unresolvability:**
   - *Status:* Unresolvable on public internet DNS.
   - *Protocol:* Documented as `UNVERIFIED`. The Khatian schema is reconstructed using the standardized statutory Khatian format approved under Section 117 of the SATA 1950, consisting of District, Upazila, Mouza, J.L. No., Khatian No., Dag No., Owner Share, Land Class, and Acre/Decimal Area.
3. **Citizen Data Protection Guarantee:**
   - Even when government portals are active, **zero live records, citizen NIDs, telephone numbers, or genuine ownership names are extracted or used.** All identities in DESHMRITTIKA / BHUMI-SYNC are 100% synthetically generated.
