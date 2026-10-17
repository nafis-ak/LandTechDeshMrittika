"""
DESHMRITTIKA / BHUMI-SYNC — Synthetic Land Officials & Offices Seeder
Populates:
1. Land Offices (AC Land Offices, Sub-Registry, Union Land Offices, Settlement Offices)
2. Synthetic Land Officials with authentic designations, demo profiles, and portrait assets.
Strictly Fictional Credentials conforming to project security & ethics guidelines.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "generated" / "full_scale" / "landtech_synthetic.db"

# Sample Land Offices
OFFICES = [
    # Savar (UPZ-2672)
    {
        "office_id": "OFFICE-SAVAR-ACLAND",
        "office_name_en": "Office of the Assistant Commissioner (Land), Savar",
        "office_name_bn": "সহকারী কমিশনার (ভূমি) এর কার্যালয়, সাভার",
        "office_type": "AC_LAND_OFFICE",
        "division_id": "DIV-30",
        "district_id": "DIST-26",
        "upazila_id": "UPZ-2672",
        "union_id": "UNI-SAV-11",
        "address_en": "Upazila Complex, Savar, Dhaka-1340",
        "address_bn": "উপজেলা পরিষদ চত্বর, সাভার, ঢাকা-১৩৪০",
        "phone_demo": "+880 1700-010001 (ডেমো)",
        "email_demo": "acland.savar@demo.land.gov.bd",
        "lat": 23.8560,
        "lon": 90.2600
    },
    {
        "office_id": "OFFICE-SAVAR-SUBREG",
        "office_name_en": "Sub-Registry Office, Savar",
        "office_name_bn": "সাব-রেজিস্ট্রারের কার্যালয়, সাভার",
        "office_type": "SUB_REGISTRY_OFFICE",
        "division_id": "DIV-30",
        "district_id": "DIST-26",
        "upazila_id": "UPZ-2672",
        "union_id": "UNI-SAV-11",
        "address_en": "Bazar Road, Savar, Dhaka",
        "address_bn": "বাজার রোড, সাভার, ঢাকা",
        "phone_demo": "+880 1700-010002 (ডেমো)",
        "email_demo": "subreg.savar@demo.land.gov.bd",
        "lat": 23.8575,
        "lon": 90.2615
    },
    {
        "office_id": "OFFICE-SAVAR-SETTLE",
        "office_name_en": "Upazila Settlement Office, Savar (DLRS)",
        "office_name_bn": "উপজেলা সেটেলমেন্ট কার্যালয়, সাভার",
        "office_type": "SETTLEMENT_OFFICE",
        "division_id": "DIV-30",
        "district_id": "DIST-26",
        "upazila_id": "UPZ-2672",
        "union_id": "UNI-SAV-11",
        "address_en": "Court Building Area, Savar, Dhaka",
        "address_bn": "কোর্ট ভবন সংলগ্ন, সাভার, ঢাকা",
        "phone_demo": "+880 1700-010003 (ডেমো)",
        "email_demo": "settlement.savar@demo.land.gov.bd",
        "lat": 23.8580,
        "lon": 90.2625
    },
    {
        "office_id": "OFFICE-AMINBAZAR-ULO",
        "office_name_en": "Aminbazar Union Land Office",
        "office_name_bn": "আমিনবাজার ইউনিয়ন ভূমি অফিস (তহশিল অফিস)",
        "office_type": "UNION_LAND_OFFICE",
        "division_id": "DIV-30",
        "district_id": "DIST-26",
        "upazila_id": "UPZ-2672",
        "union_id": "UNI-SAV-01",
        "address_en": "Aminbazar Bus Stand, Savar, Dhaka",
        "address_bn": "আমিনবাজার বাসস্ট্যান্ড সংলগ্ন, সাভার, ঢাকা",
        "phone_demo": "+880 1700-010004 (ডেমো)",
        "email_demo": "ulo.aminbazar@demo.land.gov.bd",
        "lat": 23.7915,
        "lon": 90.3245
    },
    {
        "office_id": "OFFICE-BIRULIA-ULO",
        "office_name_en": "Birulia Union Land Office",
        "office_name_bn": "বিরুলিয়া ইউনিয়ন ভূমি অফিস",
        "office_type": "UNION_LAND_OFFICE",
        "division_id": "DIV-30",
        "district_id": "DIST-26",
        "upazila_id": "UPZ-2672",
        "union_id": "UNI-SAV-02",
        "address_en": "Birulia Bazar, Savar, Dhaka",
        "address_bn": "বিরুলিয়া বাজার সংলগ্ন, সাভার, ঢাকা",
        "phone_demo": "+880 1700-010005 (ডেমো)",
        "email_demo": "ulo.birulia@demo.land.gov.bd",
        "lat": 23.8450,
        "lon": 90.3150
    },

    # Dhamrai (UPZ-2614)
    {
        "office_id": "OFFICE-DHAMRAI-ACLAND",
        "office_name_en": "Office of the Assistant Commissioner (Land), Dhamrai",
        "office_name_bn": "সহকারী কমিশনার (ভূমি) এর কার্যালয়, ধামরাই",
        "office_type": "AC_LAND_OFFICE",
        "division_id": "DIV-30",
        "district_id": "DIST-26",
        "upazila_id": "UPZ-2614",
        "union_id": "UNI-DHA-03",
        "address_en": "Upazila Complex, Dhamrai, Dhaka",
        "address_bn": "উপজেলা পরিষদ চত্বর, ধামরাই, ঢাকা",
        "phone_demo": "+880 1700-010010 (ডেমো)",
        "email_demo": "acland.dhamrai@demo.land.gov.bd",
        "lat": 23.9167,
        "lon": 90.2167
    },

    # Gazipur Sadar (UPZ-3330)
    {
        "office_id": "OFFICE-GAZIPUR-ACLAND",
        "office_name_en": "Office of the Assistant Commissioner (Land), Gazipur Sadar",
        "office_name_bn": "সহকারী কমিশনার (ভূমি) এর কার্যালয়, গাজীপুর সদর",
        "office_type": "AC_LAND_OFFICE",
        "division_id": "DIV-30",
        "district_id": "DIST-33",
        "upazila_id": "UPZ-3330",
        "union_id": "UNI-GAZ-01",
        "address_en": "Rajbari Area, Joydebpur, Gazipur",
        "address_bn": "রাজবাড়ি চত্বর, জয়দেবপুর, গাজীপুর",
        "phone_demo": "+880 1700-010020 (ডেমো)",
        "email_demo": "acland.gazipursadar@demo.land.gov.bd",
        "lat": 24.0023,
        "lon": 90.4264
    },

    # Chattogram - Patiya (UPZ-1561)
    {
        "office_id": "OFFICE-PATIYA-ACLAND",
        "office_name_en": "Office of the Assistant Commissioner (Land), Patiya",
        "office_name_bn": "সহকারী কমিশনার (ভূমি) এর কার্যালয়, পটিয়া",
        "office_type": "AC_LAND_OFFICE",
        "division_id": "DIV-20",
        "district_id": "DIST-15",
        "upazila_id": "UPZ-1561",
        "union_id": "UNI-PAT-01",
        "address_en": "Patiya Upazila Parishad, Chattogram",
        "address_bn": "পটিয়া উপজেলা পরিষদ, চট্টগ্রাম",
        "phone_demo": "+880 1700-010030 (ডেমো)",
        "email_demo": "acland.patiya@demo.land.gov.bd",
        "lat": 22.3000,
        "lon": 91.9833
    },

    # Sylhet Sadar (UPZ-9162)
    {
        "office_id": "OFFICE-SYLHET-ACLAND",
        "office_name_en": "Office of the Assistant Commissioner (Land), Sylhet Sadar",
        "office_name_bn": "সহকারী কমিশনার (ভূমি) এর কার্যালয়, সিলেট সদর",
        "office_type": "AC_LAND_OFFICE",
        "division_id": "DIV-60",
        "district_id": "DIST-91",
        "upazila_id": "UPZ-9162",
        "union_id": "UNI-SYL-01",
        "address_en": "Bandar Bazar, Sylhet-3100",
        "address_bn": "বন্দর বাজার, সিলেট-৩১০০",
        "phone_demo": "+880 1700-010040 (ডেমো)",
        "email_demo": "acland.sylhetsadar@demo.land.gov.bd",
        "lat": 24.8949,
        "lon": 91.8687
    },

    # Rajshahi Sadar (UPZ-8172)
    {
        "office_id": "OFFICE-RAJSHAHI-ACLAND",
        "office_name_en": "Office of the Assistant Commissioner (Land), Boalia Revenue Circle",
        "office_name_bn": "সহকারী কমিশনার (ভূমি) এর কার্যালয়, বোয়ালিয়া সার্কেল, রাজশাহী",
        "office_type": "AC_LAND_OFFICE",
        "division_id": "DIV-50",
        "district_id": "DIST-81",
        "upazila_id": "UPZ-8172",
        "union_id": None,
        "address_en": "Court Area, Rajshahi-6000",
        "address_bn": "কোর্ট চত্বর, রাজশাহী-৬০০০",
        "phone_demo": "+880 1700-010050 (ডেমো)",
        "email_demo": "acland.rajshahi@demo.land.gov.bd",
        "lat": 24.3636,
        "lon": 88.6241
    },

    # Khulna Sadar (UPZ-4751)
    {
        "office_id": "OFFICE-KHULNA-ACLAND",
        "office_name_en": "Office of the Assistant Commissioner (Land), Kotwali Circle",
        "office_name_bn": "সহকারী কমিশনার (ভূমি) এর কার্যালয়, কোতোয়ালী সার্কেল, খুলনা",
        "office_type": "AC_LAND_OFFICE",
        "division_id": "DIV-40",
        "district_id": "DIST-47",
        "upazila_id": "UPZ-4751",
        "union_id": None,
        "address_en": "Collectorate Road, Khulna-9100",
        "address_bn": "কালেক্টরেট রোড, খুলনা-৯১০০",
        "phone_demo": "+880 1700-010060 (ডেমো)",
        "email_demo": "acland.khulna@demo.land.gov.bd",
        "lat": 22.8456,
        "lon": 89.5403
    },

    # Barishal Sadar (UPZ-0651)
    {
        "office_id": "OFFICE-BARISHAL-ACLAND",
        "office_name_en": "Office of the Assistant Commissioner (Land), Barishal Sadar",
        "office_name_bn": "সহকারী কমিশনার (ভূমি) এর কার্যালয়, বরিশাল সদর",
        "office_type": "AC_LAND_OFFICE",
        "division_id": "DIV-10",
        "district_id": "DIST-06",
        "upazila_id": "UPZ-0651",
        "union_id": None,
        "address_en": "Band Road, Barishal-8200",
        "address_bn": "বাঁধ রোড, বরিশাল-৮২০০",
        "phone_demo": "+880 1700-010070 (ডেমো)",
        "email_demo": "acland.barishal@demo.land.gov.bd",
        "lat": 22.7010,
        "lon": 90.3535
    },

    # Rangpur Sadar (UPZ-8549)
    {
        "office_id": "OFFICE-RANGPUR-ACLAND",
        "office_name_en": "Office of the Assistant Commissioner (Land), Rangpur Sadar",
        "office_name_bn": "সহকারী কমিশনার (ভূমি) এর কার্যালয়, রংপুর সদর",
        "office_type": "AC_LAND_OFFICE",
        "division_id": "DIV-55",
        "district_id": "DIST-85",
        "upazila_id": "UPZ-8549",
        "union_id": None,
        "address_en": "Kachari Bazar, Rangpur-5400",
        "address_bn": "কাচারি বাজার, রংপুর-৫৪০০",
        "phone_demo": "+880 1700-010080 (ডেমো)",
        "email_demo": "acland.rangpur@demo.land.gov.bd",
        "lat": 25.7439,
        "lon": 89.2752
    },

    # Mymensingh Sadar (UPZ-6152)
    {
        "office_id": "OFFICE-MYMENSINGH-ACLAND",
        "office_name_en": "Office of the Assistant Commissioner (Land), Mymensingh Sadar",
        "office_name_bn": "সহকারী কমিশনার (ভূমি) এর কার্যালয়, ময়মনসিংহ সদর",
        "office_type": "AC_LAND_OFFICE",
        "division_id": "DIV-45",
        "district_id": "DIST-61",
        "upazila_id": "UPZ-6152",
        "union_id": None,
        "address_en": "Court Road, Mymensingh-2200",
        "address_bn": "কোর্ট রোড, ময়মনসিংহ-২২০০",
        "phone_demo": "+880 1700-010090 (ডেমো)",
        "email_demo": "acland.mymensingh@demo.land.gov.bd",
        "lat": 24.7471,
        "lon": 90.4203
    }
]

# Synthetic Officials (Strictly Fictional Profiles)
OFFICIALS = [
    # Savar AC Land Office
    {
        "official_id": "OFF-SAV-001",
        "name_en": "Mohammad Riazul Haque (Demo)",
        "name_bn": "মোহাম্মদ রিয়াজুল হক (ডেমো কর্মকর্তা)",
        "designation_en": "Assistant Commissioner (Land)",
        "designation_bn": "সহকারী কমিশনার (ভূমি)",
        "designation_code": "AC_LAND",
        "office_id": "OFFICE-SAVAR-ACLAND",
        "emp_no": "EMP-DEMO-0101",
        "email_demo": "acland.riazul.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000101 (ডেমো)",
        "portrait": "/assets/portraits/portrait_male_1.svg",
        "jurisdiction_en": "Savar Upazila, Dhaka District",
        "jurisdiction_bn": "সাভার উপজেলা, ঢাকা জেলা",
        "status": "ACTIVE"
    },
    {
        "official_id": "OFF-SAV-002",
        "name_en": "Kazi Farhana Akhter (Demo)",
        "name_bn": "কাজী ফারহানা আক্তার (ডেমো কর্মকর্তা)",
        "designation_en": "Kanungo",
        "designation_bn": "কানুনগো",
        "designation_code": "KANUNGO",
        "office_id": "OFFICE-SAVAR-ACLAND",
        "emp_no": "EMP-DEMO-0102",
        "email_demo": "kanungo.farhana.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000102 (ডেমো)",
        "portrait": "/assets/portraits/portrait_female_1.svg",
        "jurisdiction_en": "Revenue & Boundary Demarcation, Savar Upazila",
        "jurisdiction_bn": "রাজস্ব ও সীমানা যাচাই, সাভার উপজেলা",
        "status": "ACTIVE"
    },
    {
        "official_id": "OFF-SAV-003",
        "name_en": "Md. Shahinur Alam (Demo)",
        "name_bn": "মো: শাহিনুর আলম (ডেমো কর্মকর্তা)",
        "designation_en": "Senior Surveyor",
        "designation_bn": "সিনিয়র সার্ভেয়ার",
        "designation_code": "SURVEYOR",
        "office_id": "OFFICE-SAVAR-ACLAND",
        "emp_no": "EMP-DEMO-0103",
        "email_demo": "surveyor.shahin.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000103 (ডেমো)",
        "portrait": "/assets/portraits/portrait_male_3.svg",
        "jurisdiction_en": "Cadastral Plot Field Verification, Savar",
        "jurisdiction_bn": "সরেজমিন ক্যাডাস্ট্রাল দাগ পরিমাপ ও নকশা যাচাই",
        "status": "ACTIVE"
    },
    {
        "official_id": "OFF-SAV-004",
        "name_en": "Begum Rokeya Sultana (Demo)",
        "name_bn": "বেগম রোকেয়া সুলতানা (ডেমো কর্মকর্তা)",
        "designation_en": "Head Assistant cum Peshkar",
        "designation_bn": "প্রধান সহকারী কাম পেশকার",
        "designation_code": "PESHKAR",
        "office_id": "OFFICE-SAVAR-ACLAND",
        "emp_no": "EMP-DEMO-0104",
        "email_demo": "peshkar.rokeya.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000104 (ডেমো)",
        "portrait": "/assets/portraits/portrait_female_3.svg",
        "jurisdiction_en": "Case Scheduling & Summons Management, Savar",
        "jurisdiction_bn": "মামলা ডায়রি ও সমন নোটিশ জারি",
        "status": "ACTIVE"
    },

    # Savar Sub-Registry
    {
        "official_id": "OFF-SAV-005",
        "name_en": "Syed Enamul Kabir (Demo)",
        "name_bn": "সৈয়দ এনামুল কবির (ডেমো কর্মকর্তা)",
        "designation_en": "Sub-Registrar",
        "designation_bn": "সাব-রেজিস্ট্রার",
        "designation_code": "SUB_REGISTRAR",
        "office_id": "OFFICE-SAVAR-SUBREG",
        "emp_no": "EMP-DEMO-0105",
        "email_demo": "subreg.enamul.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000105 (ডেমো)",
        "portrait": "/assets/portraits/portrait_male_2.svg",
        "jurisdiction_en": "Deed Registration & Balam Ledger Verification",
        "jurisdiction_bn": "দলিল নিবন্ধন ও বালাম বহি হেফাজত",
        "status": "ACTIVE"
    },

    # Aminbazar Union Land Office
    {
        "official_id": "OFF-AMN-001",
        "name_en": "Nasrin Jahan (Demo)",
        "name_bn": "নাসরিন জাহান (ডেমো কর্মকর্তা)",
        "designation_en": "Union Land Assistant Officer (Tohsildar)",
        "designation_bn": "ইউনিয়ন ভূমি সহকারী কর্মকর্তা (তহশিলদার)",
        "designation_code": "ULAO",
        "office_id": "OFFICE-AMINBAZAR-ULO",
        "emp_no": "EMP-DEMO-0106",
        "email_demo": "tohsildar.nasrin.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000106 (ডেমো)",
        "portrait": "/assets/portraits/portrait_female_2.svg",
        "jurisdiction_en": "Aminbazar Union, Mouzas: Aminbazar (JL 12), Kaundia (JL 15)",
        "jurisdiction_bn": "আমিনবাজার ইউনিয়ন, মৌজা: আমিনবাজার ও কাউন্দিয়া",
        "status": "ACTIVE"
    },
    {
        "official_id": "OFF-AMN-002",
        "name_en": "Md. Anwar Hossain (Demo)",
        "name_bn": "মো: আনোয়ার হোসেন (ডেমো কর্মকর্তা)",
        "designation_en": "Union Land Sub-Assistant Officer",
        "designation_bn": "ইউনিয়ন ভূমি উপ-সহকারী কর্মকর্তা",
        "designation_code": "ULSAO",
        "office_id": "OFFICE-AMINBAZAR-ULO",
        "emp_no": "EMP-DEMO-0107",
        "email_demo": "ulsao.anwar.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000107 (ডেমো)",
        "portrait": "/assets/portraits/portrait_male_3.svg",
        "jurisdiction_en": "Field Inquiries & LDTax Collection, Aminbazar",
        "jurisdiction_bn": "সরেজমিন তদন্ত ও ভূমি উন্নয়ন কর আদায়",
        "status": "ACTIVE"
    },

    # Birulia Union Land Office
    {
        "official_id": "OFF-BIR-001",
        "name_en": "Md. Moniruzzaman (Demo)",
        "name_bn": "মো: মনিরুজ্জামান (ডেমো কর্মকর্তা)",
        "designation_en": "Union Land Assistant Officer (Tohsildar)",
        "designation_bn": "ইউনিয়ন ভূমি সহকারী কর্মকর্তা (তহশিলদার)",
        "designation_code": "ULAO",
        "office_id": "OFFICE-BIRULIA-ULO",
        "emp_no": "EMP-DEMO-0108",
        "email_demo": "tohsildar.monir.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000108 (ডেমো)",
        "portrait": "/assets/portraits/portrait_male_1.svg",
        "jurisdiction_en": "Birulia Union, Mouzas: Birulia (JL 24)",
        "jurisdiction_bn": "বিরুলিয়া ইউনিয়ন, মৌজা: বিরুলিয়া",
        "status": "ACTIVE"
    },

    # Dhamrai AC Land Office
    {
        "official_id": "OFF-DHA-001",
        "name_en": "Tahmina Parveen (Demo)",
        "name_bn": "তাহমিনা পারভীন (ডেমো কর্মকর্তা)",
        "designation_en": "Assistant Commissioner (Land)",
        "designation_bn": "সহকারী কমিশনার (ভূমি)",
        "designation_code": "AC_LAND",
        "office_id": "OFFICE-DHAMRAI-ACLAND",
        "emp_no": "EMP-DEMO-0201",
        "email_demo": "acland.tahmina.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000201 (ডেমো)",
        "portrait": "/assets/portraits/portrait_female_1.svg",
        "jurisdiction_en": "Dhamrai Upazila, Dhaka District",
        "jurisdiction_bn": "ধামরাই উপজেলা, ঢাকা জেলা",
        "status": "ACTIVE"
    },

    # Gazipur Sadar AC Land Office
    {
        "official_id": "OFF-GAZ-001",
        "name_en": "Tanvir Mahmud (Demo)",
        "name_bn": "তানভীর মাহমুদ (ডেমো কর্মকর্তা)",
        "designation_en": "Assistant Commissioner (Land)",
        "designation_bn": "সহকারী কমিশনার (ভূমি)",
        "designation_code": "AC_LAND",
        "office_id": "OFFICE-GAZIPUR-ACLAND",
        "emp_no": "EMP-DEMO-0301",
        "email_demo": "acland.tanvir.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000301 (ডেমো)",
        "portrait": "/assets/portraits/portrait_male_2.svg",
        "jurisdiction_en": "Gazipur Sadar Upazila, Gazipur District",
        "jurisdiction_bn": "গাজীপুর সদর উপজেলা, গাজীপুর জেলা",
        "status": "ACTIVE"
    },

    # Chattogram - Patiya AC Land Office
    {
        "official_id": "OFF-PAT-001",
        "name_en": "Nazmul Hasan Chowdhury (Demo)",
        "name_bn": "নাজমুল হাসান চৌধুরী (ডেমো কর্মকর্তা)",
        "designation_en": "Assistant Commissioner (Land)",
        "designation_bn": "সহকারী কমিশনার (ভূমি)",
        "designation_code": "AC_LAND",
        "office_id": "OFFICE-PATIYA-ACLAND",
        "emp_no": "EMP-DEMO-0401",
        "email_demo": "acland.nazmul.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000401 (ডেমো)",
        "portrait": "/assets/portraits/portrait_male_1.svg",
        "jurisdiction_en": "Patiya Upazila, Chattogram District",
        "jurisdiction_bn": "পটিয়া উপজেলা, চট্টগ্রাম জেলা",
        "status": "ACTIVE"
    },

    # Sylhet Sadar AC Land Office
    {
        "official_id": "OFF-SYL-001",
        "name_en": "Sharmin Sultana (Demo)",
        "name_bn": "শারমিন সুলতানা (ডেমো কর্মকর্তা)",
        "designation_en": "Assistant Commissioner (Land)",
        "designation_bn": "সহকারী কমিশনার (ভূমি)",
        "designation_code": "AC_LAND",
        "office_id": "OFFICE-SYLHET-ACLAND",
        "emp_no": "EMP-DEMO-0501",
        "email_demo": "acland.sharmin.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000501 (ডেমো)",
        "portrait": "/assets/portraits/portrait_female_2.svg",
        "jurisdiction_en": "Sylhet Sadar Upazila, Sylhet District",
        "jurisdiction_bn": "সিলেট সদর উপজেলা, সিলেট জেলা",
        "status": "ACTIVE"
    },

    # Rajshahi Boalia AC Land Office
    {
        "official_id": "OFF-RAJ-001",
        "name_en": "Dr. Arifur Rahman (Demo)",
        "name_bn": "ড. আরিফুর রহমান (ডেমো কর্মকর্তা)",
        "designation_en": "Assistant Commissioner (Land)",
        "designation_bn": "সহকারী কমিশনার (ভূমি)",
        "designation_code": "AC_LAND",
        "office_id": "OFFICE-RAJSHAHI-ACLAND",
        "emp_no": "EMP-DEMO-0601",
        "email_demo": "acland.arif.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000601 (ডেমো)",
        "portrait": "/assets/portraits/portrait_male_3.svg",
        "jurisdiction_en": "Boalia Revenue Circle, Rajshahi City",
        "jurisdiction_bn": "বোয়ালিয়া রাজস্ব সার্কেল, রাজশাহী",
        "status": "ACTIVE"
    },

    # Khulna Sadar AC Land Office
    {
        "official_id": "OFF-KHU-001",
        "name_en": "Fatema Zohra (Demo)",
        "name_bn": "ফাতেমা জোহরা (ডেমো কর্মকর্তা)",
        "designation_en": "Assistant Commissioner (Land)",
        "designation_bn": "সহকারী কমিশনার (ভূমি)",
        "designation_code": "AC_LAND",
        "office_id": "OFFICE-KHULNA-ACLAND",
        "emp_no": "EMP-DEMO-0701",
        "email_demo": "acland.fatema.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000701 (ডেমো)",
        "portrait": "/assets/portraits/portrait_female_3.svg",
        "jurisdiction_en": "Kotwali Revenue Circle, Khulna",
        "jurisdiction_bn": "কোতোয়ালী রাজস্ব সার্কেল, খুলনা",
        "status": "ACTIVE"
    },

    # Barishal Sadar AC Land Office
    {
        "official_id": "OFF-BAR-001",
        "name_en": "Khandaker Mostafa (Demo)",
        "name_bn": "খন্দকার মোস্তফা (ডেমো কর্মকর্তা)",
        "designation_en": "Assistant Commissioner (Land)",
        "designation_bn": "সহকারী কমিশনার (ভূমি)",
        "designation_code": "AC_LAND",
        "office_id": "OFFICE-BARISHAL-ACLAND",
        "emp_no": "EMP-DEMO-0801",
        "email_demo": "acland.mostafa.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000801 (ডেমো)",
        "portrait": "/assets/portraits/portrait_male_2.svg",
        "jurisdiction_en": "Barishal Sadar Upazila, Barishal District",
        "jurisdiction_bn": "বরিশাল সদর উপজেলা, বরিশাল জেলা",
        "status": "ACTIVE"
    },

    # Rangpur Sadar AC Land Office
    {
        "official_id": "OFF-RAN-001",
        "name_en": "Nusrat Jahan Shanta (Demo)",
        "name_bn": "নুসরাত জাহান শান্তা (ডেমো কর্মকর্তা)",
        "designation_en": "Assistant Commissioner (Land)",
        "designation_bn": "সহকারী কমিশনার (ভূমি)",
        "designation_code": "AC_LAND",
        "office_id": "OFFICE-RANGPUR-ACLAND",
        "emp_no": "EMP-DEMO-0901",
        "email_demo": "acland.shanta.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-000901 (ডেমো)",
        "portrait": "/assets/portraits/portrait_female_1.svg",
        "jurisdiction_en": "Rangpur Sadar Upazila, Rangpur District",
        "jurisdiction_bn": "রংপুর সদর উপজেলা, রংপুর জেলা",
        "status": "ACTIVE"
    },

    # Mymensingh Sadar AC Land Office
    {
        "official_id": "OFF-MYM-001",
        "name_en": "Ziaul Karim (Demo)",
        "name_bn": "জিয়াউল করিম (ডেমো কর্মকর্তা)",
        "designation_en": "Assistant Commissioner (Land)",
        "designation_bn": "সহকারী কমিশনার (ভূমি)",
        "designation_code": "AC_LAND",
        "office_id": "OFFICE-MYMENSINGH-ACLAND",
        "emp_no": "EMP-DEMO-1001",
        "email_demo": "acland.ziaul.demo@demo.land.gov.bd",
        "phone_demo": "+880 1700-001001 (ডেমো)",
        "portrait": "/assets/portraits/portrait_male_1.svg",
        "jurisdiction_en": "Mymensingh Sadar Upazila, Mymensingh District",
        "jurisdiction_bn": "ময়মনসিংহ সদর উপজেলা, ময়মনসিংহ জেলা",
        "status": "ACTIVE"
    }
]

def seed_officials_and_offices():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS land_offices (
        office_id TEXT PRIMARY KEY,
        office_name_en TEXT NOT NULL,
        office_name_bn TEXT NOT NULL,
        office_type TEXT NOT NULL,
        division_id TEXT NOT NULL,
        district_id TEXT NOT NULL,
        upazila_id TEXT NOT NULL,
        union_id TEXT,
        address_en TEXT,
        address_bn TEXT,
        phone_demo TEXT,
        email_demo TEXT,
        latitude REAL,
        longitude REAL,
        provenance TEXT DEFAULT 'DEMO_OFFICE — NOT AN OFFICIAL CONTACT',
        created_at TEXT NOT NULL,
        FOREIGN KEY(division_id) REFERENCES geo_divisions(division_id),
        FOREIGN KEY(district_id) REFERENCES geo_districts(district_id),
        FOREIGN KEY(upazila_id) REFERENCES geo_upazilas(upazila_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS land_officials (
        official_id TEXT PRIMARY KEY,
        name_en TEXT NOT NULL,
        name_bn TEXT NOT NULL,
        designation_en TEXT NOT NULL,
        designation_bn TEXT NOT NULL,
        designation_code TEXT NOT NULL,
        office_id TEXT NOT NULL,
        employee_number_demo TEXT NOT NULL,
        email_demo TEXT NOT NULL,
        phone_demo TEXT NOT NULL,
        portrait_image TEXT NOT NULL,
        jurisdiction_en TEXT,
        jurisdiction_bn TEXT,
        status TEXT DEFAULT 'ACTIVE',
        provenance TEXT DEFAULT 'DEMO OFFICIAL — NOT A REAL PERSON',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(office_id) REFERENCES land_offices(office_id)
    );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_land_offices_upz ON land_offices(upazila_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_land_offices_dist ON land_offices(district_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_land_officials_office ON land_officials(office_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_land_officials_code ON land_officials(designation_code);")

    now_ts = datetime.now(timezone.utc).isoformat()

    # Seed Offices
    print(f"Seeding {len(OFFICES)} land administration offices...")
    for off in OFFICES:
        cur.execute("""
        INSERT OR REPLACE INTO land_offices (
            office_id, office_name_en, office_name_bn, office_type,
            division_id, district_id, upazila_id, union_id,
            address_en, address_bn, phone_demo, email_demo, latitude, longitude, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            off["office_id"], off["office_name_en"], off["office_name_bn"], off["office_type"],
            off["division_id"], off["district_id"], off["upazila_id"], off.get("union_id"),
            off["address_en"], off["address_bn"], off["phone_demo"], off["email_demo"],
            off.get("lat"), off.get("lon"), now_ts
        ))

    # Seed Officials
    print(f"Seeding {len(OFFICIALS)} synthetic demo land officials...")
    for off in OFFICIALS:
        cur.execute("""
        INSERT OR REPLACE INTO land_officials (
            official_id, name_en, name_bn, designation_en, designation_bn, designation_code,
            office_id, employee_number_demo, email_demo, phone_demo, portrait_image,
            jurisdiction_en, jurisdiction_bn, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            off["official_id"], off["name_en"], off["name_bn"], off["designation_en"], off["designation_bn"], off["designation_code"],
            off["office_id"], off["emp_no"], off["email_demo"], off["phone_demo"], off["portrait"],
            off["jurisdiction_en"], off["jurisdiction_bn"], off["status"], now_ts, now_ts
        ))

    conn.commit()
    conn.close()
    print("Land offices and officials seeding completed successfully!")

if __name__ == "__main__":
    seed_officials_and_offices()
