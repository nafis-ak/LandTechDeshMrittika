# REFERENCE DATA FINDINGS & LAND RECORD TAXONOMY
## Bangladesh Land Administration & Survey Framework
**Project:** DESHMRITTIKA / BHUMI-SYNC (দেশমৃত্তিকা)  
**Document Version:** 1.0.0 (Phase 1 Baseline)  
**Date:** October 17, 2026  
**Context:** Authentic structural rules informing synthetic generation across P1–P6.

---

## 1. Administrative Geography & Cadastral Hierarchy

Land administration in Bangladesh operates strictly on a hierarchical cadastral tree established under the *Bengal Tenancy Act, 1885* and preserved under the *State Acquisition and Tenancy Act, 1950 (SATA 1950)*:

```
[বিভাগ / Division] (e.g. ঢাকা / Dhaka)
       |
[জেলা / District] (e.g. ঢাকা / Dhaka - BBS Code: 26)
       |
[উপজেলা / Upazila] (e.g. সাভার / Savar - BBS Code: 2672)
       |
[ইউনিয়ন / Union Parishad] (e.g. আমিনবাজার / Aminbazar)
       |
[মৌজা / Mouza] + [জে.এল. নম্বর / J.L. No.] (Cadastral Unit, e.g. Aminbazar J.L. 12)
       |
[দাগ নম্বর / Dag (Plot) Number] (Spatial Parcel Boundary)
       |
[খতিয়ান নম্বর / Khatian Number] (Record of Rights - Tenurial Account)
```

### Pilot Cadastral Definition (Dhaka Peri-Urban Zone)
To reflect realistic transaction pressures, mutation backlogs, and peri-urban boundary disputes, our synthetic generation anchors in **Savar Upazila, Dhaka District**:
* **Division:** Dhaka (ঢাকা)
* **District:** Dhaka (জেলা: ঢাকা, BBS Code 26)
* **Upazila:** Savar (উপজেলা: সাভার, BBS Code 2672)
* **Primary Pilot Mouzas:**
  1. **Aminbazar (আমিনবাজার):** J.L. No. 12 (Latitude: ~23.7850 to 23.8200 N, Longitude: ~90.3100 to 90.3450 E)
  2. **Birulia (বিরুলিয়া):** J.L. No. 24 (Latitude: ~23.8400 to 23.8850 N, Longitude: ~90.2900 to 90.3300 E)
* **Geographic Bounding Box:** Min Lat 23.7800, Max Lat 23.8900; Min Lon 90.2800, Max Lon 90.3550.

---

## 2. Historical Survey Hierarchy (CS to BS)

Land disputes frequently stem from inconsistencies between successive surveys. The synthetic data model incorporates historical survey markers:

| Survey Code | Survey Name (English) | জরিপের নাম (বাংলা) | Historical Era | Survey Methodology & Structural Characteristics |
|---|---|---|---|---|
| **CS** | **Cadastral Survey** | **সি.এস. জরিপ** | 1888–1940 | • Initiated under Bengal Tenancy Act 1885.<br>• First scientific cadastral map (16 inches = 1 mile) and Record of Rights (ROR).<br>• Uses the 16-anna share calculation system (আনা-গণ্ডা-কড়া-ক্রান্তি).<br>• Zamindar (জমিদার) as landlord, Praja/Rayat (প্রজা) as tenant. |
| **SA** | **State Acquisition Survey** | **এস.এ. জরিপ** | 1956–1962 | • Conducted after the abolition of Zamindari system via SATA 1950.<br>• Prepared rapidly based on rent-rolls of former landlords; high error rate.<br>• Directly converted tenants into maliks (proprietors under the State). |
| **RS** | **Revisional Survey** | **আর.এস. জরিপ** | 1965–1990 | • Initiated to rectify errors of the hasty SA survey.<br>• Highly respected in civil litigation as credible baseline possession evidence. |
| **BS / City** | **Bangladesh Survey / City Survey** | **বি.এস. / সিটি জরিপ** | 1990–Present | • Modern survey utilizing modern theodolite and digital cadastral methods.<br>• Metric and decimal area notation (শতক/একর). Authoritative modern record. |

---

## 3. Statutory Khatian (Porcha) Structure

Under Section 117 of SATA 1950 and the *Settlement Department Technical Rules*, an authentic Khatian (খতিয়ান / ROR) contains:
1. **Header Identification:** District, Upazila, Mouza, J.L. Number, Khatian Number, Survey Type (CS/SA/RS/BS).
2. **Owner Schedule (মালিক ও অংশ):** Full names of recorded proprietors and their individual ownership fractional share (summing exactly to 1.0000 or 16 annas).
3. **Plot Schedule (দাগ ও জমির বিবরণ):**
   - Dag Number (দাগ নম্বর)
   - Land Classification (জমির শ্রেণি)
   - Total Plot Area (দাগের মোট জমির পরিমাণ — একর ও শতকে)
   - Share Owned (দাগের মধ্যে অত্র খতিয়ানের অংশ)
   - Transferred/Calculated Area (অত্র খতিয়ানের জমির পরিমাণ — শতক)
4. **Revenue & Encumbrance (খাজনা ও মন্তব্য):** Assessed land revenue, easements, or legal possession caveats.

### Standard Land Classifications (জমির শ্রেণি)
- **নাল (Nal):** Arable low/medium crop land (Paddy/seasonal crops).
- **ভিটি / বাড়ি (Viti / Bari):** Elevated residential homestead plot.
- **ধানী (Dhani):** Wet paddy field.
- **পুকুর / জলাশয় (Pukur / Waterbody):** Fish pond or registered water reservoir.
- **পতিত (Patit):** Uncultivated / fallow highland.
- **বাগান (Bagan):** Orchard / timber plantation.
- **বাণিজ্যিক (Banijjik):** Commercial shop or industrial warehouse.
- **রাস্তা / গোপাট (Rasta / Gopāt):** Public thoroughfare or cattle trail.

---

## 4. Sub-Registry Deed Execution Lifecycle (Registration Act 1908)

The conveyance of immovable property is governed by the *Transfer of Property Act 1882* and *Registration Act 1908*:
1. **Deed Types:**
   - **সাফ-কবলা (Saf-Kabala):** Outright irrevocable sale conveyance (Primary project focus).
   - **হেবা (Heba):** Muslim gift between specific blood relations.
   - **বণ্টননামা (Bantannama):** Family amicable partition deed.
   - **বন্ধক (Bandhak):** Usufructuary or bank mortgage deed.
2. **Execution & Registration Requirements:**
   - **Execution Date (দলিল সম্পাদনের তারিখ):** Date parties sign before witnesses.
   - **Registration Date (রেজিস্ট্রেশন তারিখ):** Date presented before the Sub-Registrar and serial volume/deed number assigned.
   - **Property Schedule (তফসিল):** Precise specification of District, Upazila, Mouza, J.L., Khatian, Dag, Boundaries (চৌহদ্দি: উত্তর, দক্ষিণ, পূর্ব, পশ্চিম).
   - **Consideration Price (পণমূল্য):** Total sale value in BDT upon which stamp duty (1.5%), registration fee (1%), local government tax (2-3%), and AIT are assessed.

---

## 5. AC Land e-Mutation Workflow (ই-নামজারি)

Mutation (নামজারি ও জমা-খারিজ) is the statutory process under Section 143 of SATA 1950 whereby the Assistant Commissioner (Land) updates the Record of Rights following a registered deed:

```
[১. দলিল নিবন্ধন] (Sub-Registry Office - Min of Law)
       |
       v  (CRITICAL ADMINISTRATIVE DISCONNECT OCCURS HERE)
[২. নামজারি আবেদন] (AC Land Office - Min of Land: Case No. M-2026-SAVAR-XXXX)
       |
[৩. ইউএলএও তদন্ত] (Union Land Assistant Officer verifies possession & rent)
       |
[৪. শুনানি ও ফি] (Notice to interested parties, Hearing, DCR Fee Payment)
       |
[৫. চূড়ান্ত অনুমোদন] (AC Land signs order, updates ROR, issues new Mutated Khatian)
```

* **The Core Double-Selling Vulnerability:** In current practice, between Step 1 (Deed Registration) and Step 5 (Final Mutation Approval), a fraudulent seller can obtain a duplicate extract of their old unmutated Khatian and execute a second deed to an unsuspecting second buyer at the Sub-Registry. **DeshMrittika / Bhumi-Sync eliminates this vulnerability by linking deed events to mutation state machines in real time.**

---

## 6. Land Development Tax (LDTax) & Holding Architecture

Under the *Land Development Tax Ordinance 1976* and *Smart LDTax Guidelines (portal.ldtax.gov.bd)*:
- **Holding Account:** Every mutated plot belongs to a Holding Number (হোল্ডিং নম্বর) under a Union Land Office.
- **Assessment:** Calculated annually per decimal according to land classification (agricultural rate vs. commercial/residential rate).
- **Tax Clearance Receipt (দাখিলা / Dakhila):** A unique receipt number issued upon payment.
- **Arrears (বকেয়া):** Unpaid tax accumulates interest; tax default exceeding 3 fiscal years constitutes an administrative encumbrance that legally halts mutation approval.

---

## 7. Public Land Protections: Government Khas & Acquisition Corridors

1. **১নং খাস খতিয়ান (Collector's 1-No Khas Khatian):**
   - Immovable property owned directly by the State (Government of Bangladesh, managed by the Deputy Commissioner).
   - Categories: Riverbeds/canals (নদী/খাল), foreshore land, acquired khas, vested enemy property (অর্পিত সম্পত্তি).
   - Private deeds registered over 1-No Khas land are void *ab initio* (বাতিল).
2. **Infrastructure Acquisition Corridors (ARIPA 2017):**
   - The *Acquisition and Requisition of Immovable Property Act, 2017* requires official gazette notification (Section 4 preliminary notice) for national infrastructure (e.g. Dhaka-Aricha Highway widening, Savar EPZ expansion).
   - Transfer of land after Section 4 gazette notification is severely restricted; fraudulent sellers attempt to sell plots before government compensation is disbursed.
