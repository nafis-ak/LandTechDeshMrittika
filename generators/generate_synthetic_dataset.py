#!/usr/bin/env python3
"""
DESHMRITTIKA / BHUMI-SYNC — Synthetic Dataset Generator
Multi-Track Land Records Generator (P1 through P6)
Configurable for Dry-Run (1,000 parcels) or Full-Scale (100,000 parcels)
Seed: 20261018
"""

import os
import sys
import csv
import json
import random
import hashlib
import sqlite3
import argparse
import time
from datetime import datetime, timezone, timedelta
from faker import Faker
from PIL import Image, ImageDraw

BENGALI_FIRST_NAMES = [
    "মো: রফিকুল", "মো: আনিসুর", "মো: শফিকুল", "মো: তারেক", "মো: কামরুল",
    "মো: জহিরুল", "মো: আশরাফুল", "মো: মাহবুবুর", "মো: ফজলুল", "মো: নাজমুল",
    "মোছা: ফাতেমা", "মোছা: সুলতানা", "মোছা: নাসরিন", "মোছা: রোকেয়া", "মোছা: পারভীন",
    "মোছা: সালমা", "মোছা: শিরীন", "মোছা: তাসলিমা", "মোছা: ইয়াসমিন", "মোছা: রেহানা",
    "আব্দুর", "মোস্তাফিজুর", "খলিলুর", "গোলাম", "আবু", "হাসান", "সাইফুল"
]

BENGALI_LAST_NAMES = [
    "ইসলাম", "রহমান", "হোসেন", "আহমেদ", "চৌধুরী",
    "খান", "শিকদার", "ভূঁইয়া", "হক", "বেগম",
    "খন্দকার", "মোল্লা", "মন্ডল", "তালুকদার", "সরকার"
]

LAND_CLASSES = ['নাল', 'ভিটি', 'ধানী', 'পুকুর', 'পতিত', 'বাগান', 'বাণিজ্যিক', 'রাস্তা']
LAND_CLASS_WEIGHTS = [0.45, 0.30, 0.10, 0.04, 0.04, 0.03, 0.02, 0.02]

SURVEY_TYPES = ['BS_CITY', 'RS', 'SA', 'CS']
SURVEY_TYPE_WEIGHTS = [0.60, 0.30, 0.08, 0.02]

def setup_database(db_path: str):
    """Initializes SQLite schema for all 14 entities."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA synchronous = OFF;")
    cur.execute("PRAGMA journal_mode = MEMORY;")

    cur.execute("""
    CREATE TABLE parcels (
        parcel_id VARCHAR(32) PRIMARY KEY,
        district VARCHAR(64) NOT NULL,
        upazila VARCHAR(64) NOT NULL,
        mouza VARCHAR(64) NOT NULL,
        jl_number INTEGER NOT NULL,
        dag_number INTEGER NOT NULL,
        khatian_number INTEGER NOT NULL,
        survey_type VARCHAR(16) NOT NULL,
        land_classification VARCHAR(32) NOT NULL,
        area_decimal NUMERIC(10, 2) NOT NULL,
        coordinates_geojson TEXT,
        is_disputed BOOLEAN NOT NULL DEFAULT 0,
        provenance_label VARCHAR(64) NOT NULL DEFAULT 'SYNTHETIC_DEMO_RECORD'
    );
    """)

    cur.execute("""
    CREATE TABLE owners (
        owner_id VARCHAR(32) PRIMARY KEY,
        fictional_name VARCHAR(128) NOT NULL,
        synthetic_nid_hash CHAR(64) NOT NULL UNIQUE,
        contact_masked VARCHAR(24),
        provenance_label VARCHAR(64) NOT NULL DEFAULT 'FICTIONAL_CITIZEN_RECORD'
    );
    """)

    cur.execute("""
    CREATE TABLE parcel_ownership (
        ownership_id VARCHAR(32) PRIMARY KEY,
        parcel_id VARCHAR(32) NOT NULL,
        owner_id VARCHAR(32) NOT NULL,
        ownership_share NUMERIC(6, 4) NOT NULL,
        valid_from DATE NOT NULL,
        valid_to DATE,
        source_event_id VARCHAR(32),
        FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id),
        FOREIGN KEY (owner_id) REFERENCES owners(owner_id)
    );
    """)

    cur.execute("""
    CREATE TABLE deeds (
        deed_id VARCHAR(32) PRIMARY KEY,
        deed_number VARCHAR(32) NOT NULL UNIQUE,
        sub_registry_office VARCHAR(64) NOT NULL,
        deed_type VARCHAR(32) NOT NULL,
        parcel_id VARCHAR(32) NOT NULL,
        seller_id VARCHAR(32) NOT NULL,
        buyer_id VARCHAR(32) NOT NULL,
        execution_date DATE NOT NULL,
        registration_date DATE NOT NULL,
        declared_area NUMERIC(10, 2) NOT NULL,
        deed_value_bdt NUMERIC(14, 2) NOT NULL,
        deed_status VARCHAR(32) NOT NULL,
        document_id VARCHAR(32),
        FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id),
        FOREIGN KEY (seller_id) REFERENCES owners(owner_id),
        FOREIGN KEY (buyer_id) REFERENCES owners(owner_id)
    );
    """)

    cur.execute("""
    CREATE TABLE transactions (
        transaction_id VARCHAR(32) PRIMARY KEY,
        parcel_id VARCHAR(32) NOT NULL,
        deed_id VARCHAR(32) NOT NULL UNIQUE,
        seller_id VARCHAR(32) NOT NULL,
        buyer_id VARCHAR(32) NOT NULL,
        transaction_date DATE NOT NULL,
        status VARCHAR(32) NOT NULL,
        mutation_link_status VARCHAR(32) NOT NULL,
        FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id),
        FOREIGN KEY (deed_id) REFERENCES deeds(deed_id),
        FOREIGN KEY (seller_id) REFERENCES owners(owner_id),
        FOREIGN KEY (buyer_id) REFERENCES owners(owner_id)
    );
    """)

    cur.execute("""
    CREATE TABLE ownership_events (
        event_id VARCHAR(32) PRIMARY KEY,
        parcel_id VARCHAR(32) NOT NULL,
        previous_owner_id VARCHAR(32),
        new_owner_id VARCHAR(32) NOT NULL,
        deed_id VARCHAR(32),
        event_date DATE NOT NULL,
        event_type VARCHAR(32) NOT NULL,
        verification_status VARCHAR(32) NOT NULL,
        FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id),
        FOREIGN KEY (previous_owner_id) REFERENCES owners(owner_id),
        FOREIGN KEY (new_owner_id) REFERENCES owners(owner_id),
        FOREIGN KEY (deed_id) REFERENCES deeds(deed_id)
    );
    """)

    cur.execute("""
    CREATE TABLE mutation_records (
        mutation_id VARCHAR(32) PRIMARY KEY,
        case_number VARCHAR(64) NOT NULL UNIQUE,
        parcel_id VARCHAR(32) NOT NULL,
        deed_id VARCHAR(32) NOT NULL,
        applicant_id VARCHAR(32) NOT NULL,
        application_date DATE NOT NULL,
        status VARCHAR(32) NOT NULL,
        decision_date DATE,
        mutated_khatian_no INTEGER,
        FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id),
        FOREIGN KEY (deed_id) REFERENCES deeds(deed_id),
        FOREIGN KEY (applicant_id) REFERENCES owners(owner_id)
    );
    """)

    cur.execute("""
    CREATE TABLE documents (
        document_id VARCHAR(32) PRIMARY KEY,
        parcel_id VARCHAR(32) NOT NULL,
        deed_id VARCHAR(32),
        document_type VARCHAR(32) NOT NULL,
        file_path VARCHAR(255) NOT NULL,
        sha256_hash CHAR(64) NOT NULL,
        qr_token VARCHAR(128),
        ocr_status VARCHAR(32) NOT NULL,
        extracted_fields_json TEXT,
        provenance_label VARCHAR(64) NOT NULL DEFAULT 'SYNTHETIC_DEMO_DOCUMENT',
        FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id),
        FOREIGN KEY (deed_id) REFERENCES deeds(deed_id)
    );
    """)

    cur.execute("""
    CREATE TABLE tax_records (
        tax_record_id VARCHAR(32) PRIMARY KEY,
        parcel_id VARCHAR(32) NOT NULL,
        holding_number VARCHAR(64) NOT NULL,
        tax_year VARCHAR(16) NOT NULL,
        assessed_amount NUMERIC(10, 2) NOT NULL,
        paid_amount NUMERIC(10, 2) NOT NULL,
        dakhila_number VARCHAR(64),
        payment_status VARCHAR(16) NOT NULL,
        FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id)
    );
    """)

    cur.execute("""
    CREATE TABLE litigation_records (
        case_id VARCHAR(32) PRIMARY KEY,
        parcel_id VARCHAR(32) NOT NULL,
        court_name VARCHAR(128) NOT NULL,
        case_number VARCHAR(64) NOT NULL,
        dispute_type VARCHAR(32) NOT NULL,
        filing_date DATE NOT NULL,
        status VARCHAR(32) NOT NULL,
        FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id)
    );
    """)

    cur.execute("""
    CREATE TABLE khas_records (
        khas_id VARCHAR(32) PRIMARY KEY,
        parcel_id VARCHAR(32) NOT NULL UNIQUE,
        khas_category VARCHAR(32) NOT NULL,
        managing_authority VARCHAR(64) NOT NULL DEFAULT 'COLLECTOR_DHAKA',
        is_protected BOOLEAN NOT NULL DEFAULT 1,
        FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id)
    );
    """)

    cur.execute("""
    CREATE TABLE acquisition_zones (
        zone_id VARCHAR(32) PRIMARY KEY,
        project_name VARCHAR(128) NOT NULL,
        gazette_notification_no VARCHAR(64) NOT NULL UNIQUE,
        corridor_geojson TEXT NOT NULL,
        status VARCHAR(32) NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE verification_cases (
        case_id VARCHAR(32) PRIMARY KEY,
        parcel_id VARCHAR(32) NOT NULL,
        finding_code VARCHAR(32) NOT NULL,
        severity VARCHAR(16) NOT NULL,
        risk_score INTEGER NOT NULL,
        explanation_bn TEXT NOT NULL,
        explanation_en TEXT NOT NULL,
        evidence_references TEXT NOT NULL,
        review_status VARCHAR(32) NOT NULL DEFAULT 'PENDING_REVIEW',
        FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id)
    );
    """)

    cur.execute("""
    CREATE TABLE review_logs (
        log_id VARCHAR(32) PRIMARY KEY,
        case_id VARCHAR(32) NOT NULL,
        reviewer_id VARCHAR(64) NOT NULL,
        action VARCHAR(32) NOT NULL,
        reason TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        FOREIGN KEY (case_id) REFERENCES verification_cases(case_id)
    );
    """)

    conn.commit()
    return conn

def generate_fictional_name(rnd: random.Random) -> str:
    first = rnd.choice(BENGALI_FIRST_NAMES)
    last = rnd.choice(BENGALI_LAST_NAMES)
    return f"{first} {last}"

def generate_sample_document_image(doc_id: str, doc_type: str, parcel_id: str, deed_no: str, output_path: str):
    """Generates an authentic synthetic document image with watermarks for OCR testing."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new('RGB', (800, 600), color=(250, 248, 240))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(20, 20), (780, 580)], outline=(100, 80, 50), width=3)
    draw.rectangle([(26, 26), (774, 574)], outline=(150, 130, 100), width=1)

    draw.text((220, 45), "গণপ্রজাতন্ত্রী বাংলাদেশ সরকার", fill=(0, 100, 0))
    draw.text((260, 70), f"ভূমি রেকর্ড ও রেজিস্ট্রেশন দলিল ({doc_type})", fill=(50, 50, 50))
    
    draw.text((120, 110), "SYNTHETIC DEMO DOCUMENT — NOT AN OFFICIAL LAND RECORD", fill=(180, 0, 0))
    draw.line([(50, 135), (750, 135)], fill=(180, 0, 0), width=1)

    draw.text((50, 160), f"DOCUMENT ID: {doc_id}", fill=(0, 0, 0))
    draw.text((50, 190), f"PARCEL REF: {parcel_id}", fill=(0, 0, 0))
    draw.text((50, 220), f"DEED NUMBER: {deed_no}", fill=(0, 0, 0))
    draw.text((50, 250), "DISTRICT: DHAKA, UPAZILA: SAVAR", fill=(0, 0, 0))
    draw.text((50, 280), "MOUZA: AMINBAZAR, J.L. NO: 12", fill=(0, 0, 0))
    draw.text((50, 310), "SCHEDULE: TRANSFER OF TITLE / SAF-KABALA CONVEYANCE", fill=(0, 0, 0))
    draw.text((50, 350), "PROPERTY AREA: 12.50 DECIMALS", fill=(0, 0, 0))
    draw.text((50, 380), "CONSIDERATION VALUE: BDT 4,500,000", fill=(0, 0, 0))
    draw.text((50, 420), "SELLER: FICTIONAL CITIZEN A  -->  BUYER: FICTIONAL CITIZEN B", fill=(0, 0, 0))

    draw.rectangle([(50, 470), (750, 540)], fill=(240, 240, 230), outline=(100, 100, 100))
    draw.text((65, 485), f"CRYPTOGRAPHIC INTEGRITY TOKEN: SHA256-SYNTH-{doc_id}", fill=(80, 80, 80))
    draw.text((65, 510), "VERIFICATION PORTAL: http://127.0.0.1:8000/verify", fill=(0, 80, 160))

    img.save(output_path, "PNG")

    with open(output_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    return sha256

def main():
    parser = argparse.ArgumentParser(description="Bhumi-Sync Synthetic Dataset Generator")
    parser.add_argument("--parcels", type=int, default=1000, help="Number of parcels (1000 for dry run, 100000 for full)")
    parser.add_argument("--owners", type=int, default=200, help="Number of owners (200 for dry run, 20000 for full)")
    parser.add_argument("--seed", type=int, default=20261018, help="Random seed for reproducibility")
    parser.add_argument("--output-db", type=str, default="data/generated/dry_run/landtech_synthetic_dry_run.db")
    parser.add_argument("--export-csv", type=str, default="data/generated/dry_run/csv")
    parser.add_argument("--doc-dir", type=str, default="data/generated/dry_run/documents")
    parser.add_argument("--manifest", type=str, default="data/generated/dry_run/dataset_manifest.json")
    parser.add_argument("--scenario-catalog", type=str, default="data/scenarios/scenario_catalog.csv")
    args = parser.parse_args()

    start_time = time.time()
    rnd = random.Random(args.seed)
    faker = Faker()
    faker.seed_instance(args.seed)

    is_full_scale = (args.parcels >= 50000)
    print(f"=== INITIATING {'FULL-SCALE' if is_full_scale else 'DRY-RUN'} SYNTHETIC GENERATION ===")
    print(f"Seed: {args.seed} | Target Parcels: {args.parcels:,} | Target Owners: {args.owners:,}")
    print(f"Output DB: {args.output_db}")

    conn = setup_database(args.output_db)
    cur = conn.cursor()

    # 1. GENERATE OWNERS
    print(f"Generating {args.owners:,} Fictional Owners...")
    owners_data = []
    for i in range(1, args.owners + 1):
        owner_id = f"OWN-{i:06d}"
        fictional_name = generate_fictional_name(rnd)
        synth_nid_seed = f"SYNTH-NID-{args.seed}-{i:08d}"
        synthetic_nid_hash = hashlib.sha256(synth_nid_seed.encode()).hexdigest()
        contact_masked = f"+8801700-00{rnd.randint(1000, 9999)}"
        owners_data.append((owner_id, fictional_name, synthetic_nid_hash, contact_masked, 'FICTIONAL_CITIZEN_RECORD'))

    cur.executemany("INSERT INTO owners VALUES (?, ?, ?, ?, ?)", owners_data)
    conn.commit()

    # 2. GENERATE ACQUISITION ZONES (5 corridors)
    print("Generating Infrastructure Acquisition Zones...")
    acq_zones = [
        ("ACQ-000001", "Dhaka-Aricha Highway 8-Lane Expansion Project", "DHAKA-GAZ-ARIPA-2024-101",
         json.dumps({"type": "Polygon", "coordinates": [[[90.3150, 23.7900], [90.3200, 23.7900], [90.3200, 23.8300], [90.3150, 23.8300], [90.3150, 23.7900]]]}),
         "SECTION_4_NOTIFIED"),
        ("ACQ-000002", "Savar EPZ Modern Logistics Corridor", "DHAKA-GAZ-ARIPA-2024-102",
         json.dumps({"type": "Polygon", "coordinates": [[[90.2850, 23.8500], [90.2900, 23.8500], [90.2900, 23.8700], [90.2850, 23.8700], [90.2850, 23.8500]]]}),
         "SECTION_7_VERIFIED"),
        ("ACQ-000003", "Turag River Eco-Restoration Buffer Zone", "DHAKA-GAZ-ARIPA-2023-88",
         json.dumps({"type": "Polygon", "coordinates": [[[90.3350, 23.8000], [90.3450, 23.8000], [90.3450, 23.8250], [90.3350, 23.8250], [90.3350, 23.8000]]]}),
         "SECTION_8_AWARDED"),
        ("ACQ-000004", "Birulia-Ashulia Ring Embankment Link", "DHAKA-GAZ-ARIPA-2025-15",
         json.dumps({"type": "Polygon", "coordinates": [[[90.3000, 23.8700], [90.3050, 23.8700], [90.3050, 23.8900], [90.3000, 23.8900], [90.3000, 23.8700]]]}),
         "SECTION_4_NOTIFIED"),
        ("ACQ-000005", "Dhaka Mass Rapid Transit Line-5 (Northern Route)", "DHAKA-GAZ-ARIPA-2024-220",
         json.dumps({"type": "Polygon", "coordinates": [[[90.3250, 23.7800], [90.3300, 23.7800], [90.3300, 23.8100], [90.3250, 23.8100], [90.3250, 23.7800]]]}),
         "SECTION_7_VERIFIED")
    ]
    cur.executemany("INSERT INTO acquisition_zones VALUES (?, ?, ?, ?, ?)", acq_zones)
    conn.commit()

    # 3. CONFIGURE SCENARIOS RANGES
    # Full scale: exactly 500 double-selling cases (101 to 600)
    # Dry run: 10 double-selling cases (101 to 110)
    ds1_start = 101
    ds1_count = 500 if is_full_scale else 10
    ds1_end = ds1_start + ds1_count - 1

    ds2_start = 1001 if is_full_scale else 201
    ds2_count = 15000 if is_full_scale else 50
    ds2_end = ds2_start + ds2_count - 1

    ds3_start = 16001 if is_full_scale else 301
    ds3_count = 250 if is_full_scale else 5
    ds3_end = ds3_start + ds3_count - 1

    ds4_start = 16251 if is_full_scale else 401
    ds4_count = 200 if is_full_scale else 5
    ds4_end = ds4_start + ds4_count - 1

    ds5_start = 16451 if is_full_scale else 501
    ds5_count = 1000 if is_full_scale else 10
    ds5_end = ds5_start + ds5_count - 1

    lit_start = 17451 if is_full_scale else 601
    lit_count = 1500 if is_full_scale else 10
    lit_end = lit_start + lit_count - 1

    khs_start = 18951 if is_full_scale else 701
    khs_count = 1500 if is_full_scale else 15
    khs_end = khs_start + khs_count - 1

    mouza_list = [("Aminbazar", 12), ("Birulia", 24)]

    # Counters
    pow_idx = 1
    deed_idx = 1
    txn_idx = 1
    evt_idx = 1
    mut_idx = 1
    doc_idx = 1
    tax_idx = 1
    lit_idx = 1
    khs_idx = 1
    case_idx = 1
    log_idx = 1

    scenario_catalog = []

    print(f"Generating Parcels and Scenarios (Batched Execution)...")
    batch_size = 10000
    total_parcels = args.parcels

    for batch_start in range(1, total_parcels + 1, batch_size):
        batch_end = min(batch_start + batch_size - 1, total_parcels)
        print(f"  -> Processing parcels {batch_start:,} to {batch_end:,}...")

        parcels_batch = []
        ownership_batch = []
        deeds_batch = []
        txns_batch = []
        events_batch = []
        mutations_batch = []
        documents_batch = []
        tax_batch = []
        lit_batch = []
        khs_batch = []
        cases_batch = []
        logs_batch = []

        for p_num in range(batch_start, batch_end + 1):
            parcel_id = f"BD-PAR-{p_num:06d}"
            mouza_name, jl_num = mouza_list[0] if p_num <= (total_parcels // 2) else mouza_list[1]
            dag_num = 100 + (p_num % 5000)
            khatian_num = 1000 + (p_num % 3000)
            survey_type = rnd.choices(SURVEY_TYPES, weights=SURVEY_TYPE_WEIGHTS, k=1)[0]
            land_class = rnd.choices(LAND_CLASSES, weights=LAND_CLASS_WEIGHTS, k=1)[0]
            area_decimal = round(rnd.uniform(4.0, 45.0), 2)

            base_lat = 23.8000 if mouza_name == "Aminbazar" else 23.8500
            base_lon = 90.3200 if mouza_name == "Aminbazar" else 90.3000
            lat = round(base_lat + rnd.uniform(-0.015, 0.015), 6)
            lon = round(base_lon + rnd.uniform(-0.015, 0.015), 6)

            geojson = json.dumps({
                "type": "Polygon",
                "coordinates": [[
                    [round(lon - 0.0004, 6), round(lat - 0.0004, 6)],
                    [round(lon + 0.0004, 6), round(lat - 0.0004, 6)],
                    [round(lon + 0.0004, 6), round(lat + 0.0004, 6)],
                    [round(lon - 0.0004, 6), round(lat + 0.0004, 6)],
                    [round(lon - 0.0004, 6), round(lat - 0.0004, 6)]
                ]]
            })

            is_disputed = False

            # SCENARIO 1: DS-01 Active Double-Selling
            if ds1_start <= p_num <= ds1_end:
                is_disputed = True
                scenario_seq = p_num - ds1_start + 1
                scn_id = f"SCN-DS1-{scenario_seq:04d}"

                seller = owners_data[(p_num * 3) % len(owners_data)][0]
                buyer1 = owners_data[(p_num * 3 + 1) % len(owners_data)][0]
                buyer2 = owners_data[(p_num * 3 + 2) % len(owners_data)][0]

                pow_id = f"POW-{pow_idx:06d}"
                pow_idx += 1
                ownership_batch.append((pow_id, parcel_id, seller, 1.0000, "2015-01-01", None, None))

                d1_id = f"DEED-{deed_idx:06d}"
                deed_idx += 1
                deed_no_1 = f"SAVAR-{args.seed}-DS1-A{p_num}"
                reg_date_1 = "2024-03-15"
                deeds_batch.append((d1_id, deed_no_1, "Savar Sub-Registry", "SAF_KABALA", parcel_id, seller, buyer1,
                                   "2024-03-10", reg_date_1, area_decimal, round(area_decimal * 300000, 2), "REGISTERED", None))

                t1_id = f"TXN-{txn_idx:06d}"
                txn_idx += 1
                txns_batch.append((t1_id, parcel_id, d1_id, seller, buyer1, reg_date_1, "COMPLETED", "MUTATION_PENDING"))

                m1_id = f"MUT-{mut_idx:06d}"
                mut_idx += 1
                mutations_batch.append((m1_id, f"M-2024-SAVAR-{p_num:05d}", parcel_id, d1_id, buyer1, "2024-03-25", "SUBMITTED", None, None))

                d2_id = f"DEED-{deed_idx:06d}"
                deed_idx += 1
                deed_no_2 = f"SAVAR-{args.seed}-DS1-B{p_num}"
                reg_date_2 = "2024-06-25"
                deeds_batch.append((d2_id, deed_no_2, "Savar Sub-Registry", "SAF_KABALA", parcel_id, seller, buyer2,
                                   "2024-06-20", reg_date_2, area_decimal, round(area_decimal * 320000, 2), "DISPUTED", None))

                t2_id = f"TXN-{txn_idx:06d}"
                txn_idx += 1
                txns_batch.append((t2_id, parcel_id, d2_id, seller, buyer2, reg_date_2, "FLAGGED_FRAUD", "UNLINKED"))

                e1_id = f"EVT-{evt_idx:06d}"
                evt_idx += 1
                events_batch.append((e1_id, parcel_id, seller, buyer1, d1_id, reg_date_1, "SALE_DEED", "INVESTIGATION_PENDING"))

                e2_id = f"EVT-{evt_idx:06d}"
                evt_idx += 1
                events_batch.append((e2_id, parcel_id, seller, buyer2, d2_id, reg_date_2, "SALE_DEED", "CONCURRENT_CONFLICT"))

                case_id = f"CASE-{case_idx:06d}"
                case_idx += 1
                cases_batch.append((
                    case_id, parcel_id, "DS-01", "CRITICAL", 95,
                    f"সতর্কতা: একই বিক্রেতা কর্তৃক দলিল {deed_no_1} সম্পাদনের পর নামজারি নিষ্পত্তির পূর্বেই দলিল {deed_no_2} সম্পাদন করা হয়েছে।",
                    f"Critical Alert: Concurrent unmutated transfer detected ({scn_id}). Prior deed {deed_no_1} mutation remains pending while deed {deed_no_2} was executed.",
                    json.dumps({"scenario_id": scn_id, "deeds": [d1_id, d2_id], "seller": seller, "buyers": [buyer1, buyer2]}),
                    "PENDING_REVIEW"
                ))

                scenario_catalog.append((
                    scn_id, "DS-01_DOUBLE_SELLING", parcel_id, f"{deed_no_1};{deed_no_2}", seller, f"{buyer1};{buyer2}",
                    "DS-01", "CRITICAL", 95, "Active double-selling: prior transfer mutation unresolved; second deed executed."
                ))

            # SCENARIO 2: DS-02 Clean Sequential Transfers
            elif ds2_start <= p_num <= ds2_end:
                owner1 = owners_data[(p_num * 2) % len(owners_data)][0]
                owner2 = owners_data[(p_num * 2 + 1) % len(owners_data)][0]
                owner3 = owners_data[(p_num * 2 + 2) % len(owners_data)][0]

                pow1_id = f"POW-{pow_idx:06d}"
                pow_idx += 1
                ownership_batch.append((pow1_id, parcel_id, owner1, 1.0000, "2010-01-01", "2020-05-15", None))

                d1_id = f"DEED-{deed_idx:06d}"
                deed_idx += 1
                deed_no_1 = f"SAVAR-{args.seed}-SEQ-A{p_num}"
                deeds_batch.append((d1_id, deed_no_1, "Savar Sub-Registry", "SAF_KABALA", parcel_id, owner1, owner2,
                                   "2020-05-10", "2020-05-15", area_decimal, round(area_decimal * 150000, 2), "REGISTERED", None))

                t1_id = f"TXN-{txn_idx:06d}"
                txn_idx += 1
                txns_batch.append((t1_id, parcel_id, d1_id, owner1, owner2, "2020-05-15", "COMPLETED", "MUTATED"))

                m1_id = f"MUT-{mut_idx:06d}"
                mut_idx += 1
                mutations_batch.append((m1_id, f"M-2020-SAVAR-{p_num:05d}", parcel_id, d1_id, owner2, "2020-05-20", "APPROVED", "2020-06-15", 3000 + p_num))

                pow2_id = f"POW-{pow_idx:06d}"
                pow_idx += 1
                ownership_batch.append((pow2_id, parcel_id, owner2, 1.0000, "2020-06-15", "2023-08-10", m1_id))

                d2_id = f"DEED-{deed_idx:06d}"
                deed_idx += 1
                deed_no_2 = f"SAVAR-{args.seed}-SEQ-B{p_num}"
                deeds_batch.append((d2_id, deed_no_2, "Savar Sub-Registry", "SAF_KABALA", parcel_id, owner2, owner3,
                                   "2023-08-05", "2023-08-10", area_decimal, round(area_decimal * 250000, 2), "REGISTERED", None))

                t2_id = f"TXN-{txn_idx:06d}"
                txn_idx += 1
                txns_batch.append((t2_id, parcel_id, d2_id, owner2, owner3, "2023-08-10", "COMPLETED", "MUTATED"))

                m2_id = f"MUT-{mut_idx:06d}"
                mut_idx += 1
                mutations_batch.append((m2_id, f"M-2023-SAVAR-{p_num:05d}", parcel_id, d2_id, owner3, "2023-08-15", "APPROVED", "2023-09-10", 4000 + p_num))

                pow3_id = f"POW-{pow_idx:06d}"
                pow_idx += 1
                ownership_batch.append((pow3_id, parcel_id, owner3, 1.0000, "2023-09-10", None, m2_id))

                e1_id = f"EVT-{evt_idx:06d}"
                evt_idx += 1
                events_batch.append((e1_id, parcel_id, owner1, owner2, d1_id, "2020-05-15", "SALE_DEED", "VERIFIED"))

                e2_id = f"EVT-{evt_idx:06d}"
                evt_idx += 1
                events_batch.append((e2_id, parcel_id, owner2, owner3, d2_id, "2023-08-10", "SALE_DEED", "VERIFIED"))

                case_id = f"CASE-{case_idx:06d}"
                case_idx += 1
                cases_batch.append((
                    case_id, parcel_id, "DS-02", "LOW", 0,
                    f"মালিকানা চেইন সম্পূর্ণ বৈধ। দলিল {deed_no_1} ও {deed_no_2} ধারাবাহিক নামজারির মাধ্যমে সম্পন্ন হয়েছে।",
                    f"Legitimate chain of custody. Deeds {deed_no_1} and {deed_no_2} represent clean sequential conveyances resolved via approved mutations.",
                    json.dumps({"deeds": [d1_id, d2_id]}),
                    "RESOLVED_CLEARED"
                ))

            # SCENARIO 3: DS-03 Area Over-Sale
            elif ds3_start <= p_num <= ds3_end:
                is_disputed = True
                seller = owners_data[p_num % len(owners_data)][0]
                buyer = owners_data[(p_num + 5) % len(owners_data)][0]

                pow_id = f"POW-{pow_idx:06d}"
                pow_idx += 1
                ownership_batch.append((pow_id, parcel_id, seller, 1.0000, "2018-01-01", None, None))

                oversold_area = round(area_decimal + 5.0, 2)
                d_id = f"DEED-{deed_idx:06d}"
                deed_idx += 1
                deed_no = f"SAVAR-{args.seed}-OVS-{p_num}"
                deeds_batch.append((d_id, deed_no, "Savar Sub-Registry", "SAF_KABALA", parcel_id, seller, buyer,
                                   "2024-01-10", "2024-01-15", oversold_area, round(oversold_area * 200000, 2), "DISPUTED", None))

                t_id = f"TXN-{txn_idx:06d}"
                txn_idx += 1
                txns_batch.append((t_id, parcel_id, d_id, seller, buyer, "2024-01-15", "SUSPENDED", "UNLINKED"))

                case_id = f"CASE-{case_idx:06d}"
                case_idx += 1
                cases_batch.append((
                    case_id, parcel_id, "DS-03", "HIGH", 75,
                    f"জমির পরিমাণ অমিল: খতিয়ানে মূল দাগের পরিমাণ {area_decimal} শতক, কিন্তু দলিলে হস্তান্তরিত পরিমাণ {oversold_area} শতক।",
                    f"Area Discrepancy: Deed {deed_no} declares transfer of {oversold_area} decimals exceeding parcel ROR area of {area_decimal} decimals.",
                    json.dumps({"parcel_area": area_decimal, "declared_area": oversold_area, "deed": d_id}),
                    "PENDING_REVIEW"
                ))

            # SCENARIO 4: Khas Government Land
            elif khs_start <= p_num <= khs_end:
                is_disputed = True
                khas_id = f"KHS-{khs_idx:06d}"
                khs_idx += 1
                khs_batch.append((khas_id, parcel_id, "1_NO_GOVERNMENT_KHAS", "COLLECTOR_DHAKA", 1))

                case_id = f"CASE-{case_idx:06d}"
                case_idx += 1
                cases_batch.append((
                    case_id, parcel_id, "P6-ENCROACH", "CRITICAL", 90,
                    "সতর্কতা: অত্র দাগটি সরকারি ১নং খাস খতিয়ানভুক্ত সম্পত্তি। ব্যক্তিপর্যায়ে বিক্রয় বা হস্তান্তর আইনত নিষিদ্ধ।",
                    "Public Land Alert: Parcel is gazetted as 1-No Government Khas Land. Private sale or transfer is legally void ab initio.",
                    json.dumps({"khas_id": khas_id, "category": "1_NO_GOVERNMENT_KHAS"}),
                    "PENDING_REVIEW"
                ))

            # SCENARIO 5: Active Civil Litigation
            elif lit_start <= p_num <= lit_end:
                is_disputed = True
                owner = owners_data[p_num % len(owners_data)][0]
                pow_id = f"POW-{pow_idx:06d}"
                pow_idx += 1
                ownership_batch.append((pow_id, parcel_id, owner, 1.0000, "2019-01-01", None, None))

                lit_id = f"LIT-{lit_idx:06d}"
                lit_idx += 1
                suit_no = f"Title Suit No. {p_num}/2023"
                lit_batch.append((lit_id, parcel_id, "সিনিয়র সহকারী জজ আদালত, সাভার", suit_no,
                                 "INJUNCTION_AGAINST_SALE", "2023-04-12", "ACTIVE_INJUNCTION_STAY"))

                case_id = f"CASE-{case_idx:06d}"
                case_idx += 1
                cases_batch.append((
                    case_id, parcel_id, "DS-05", "MEDIUM", 45,
                    f"আইনি সতর্কতা: অত্র দাগের উপর সহকারী জজ আদালতে দেওয়ানি মামলা ({suit_no}) চলমান ও অস্থায়ী নিষেধাজ্ঞা বলবৎ।",
                    f"Litigation Warning: Active civil title injunction ({suit_no}) issued by Senior Assistant Judge Court, Savar.",
                    json.dumps({"litigation_id": lit_id, "case_number": suit_no}),
                    "PENDING_REVIEW"
                ))

            # DEFAULT NORMAL PARCELS
            else:
                owner = owners_data[p_num % len(owners_data)][0]
                pow_id = f"POW-{pow_idx:06d}"
                pow_idx += 1
                ownership_batch.append((pow_id, parcel_id, owner, 1.0000, "2016-01-01", None, None))

                # Legitimate normal sale for ~30% of standard parcels
                if p_num % 3 == 0:
                    buyer = owners_data[(p_num + 7) % len(owners_data)][0]
                    d_id = f"DEED-{deed_idx:06d}"
                    deed_idx += 1
                    deed_no = f"SAVAR-{args.seed}-{p_num:05d}"
                    reg_date = "2023-11-20"
                    deeds_batch.append((d_id, deed_no, "Savar Sub-Registry", "SAF_KABALA", parcel_id, owner, buyer,
                                       "2023-11-15", reg_date, area_decimal, round(area_decimal * 200000, 2), "REGISTERED", None))

                    t_id = f"TXN-{txn_idx:06d}"
                    txn_idx += 1
                    txns_batch.append((t_id, parcel_id, d_id, owner, buyer, reg_date, "COMPLETED", "MUTATED"))

                    m_id = f"MUT-{mut_idx:06d}"
                    mut_idx += 1
                    mutations_batch.append((m_id, f"M-2023-SAVAR-{p_num:05d}", parcel_id, d_id, buyer, "2023-11-25", "APPROVED", "2023-12-20", 5000 + p_num))

            # Tax records for all parcels
            tax_id = f"TAX-{tax_idx:06d}"
            tax_idx += 1
            holding_no = f"HLD-SAVAR-{mouza_name[:3].upper()}-{p_num:05d}"
            if ds5_start <= p_num <= ds5_end:
                tax_batch.append((tax_id, parcel_id, holding_no, "1430-1431", 12500.00, 0.00, None, "ARREARS_DUE"))
                case_id = f"CASE-{case_idx:06d}"
                case_idx += 1
                cases_batch.append((
                    case_id, parcel_id, "DS-05", "MEDIUM", 40,
                    f"ভূমি উন্নয়ন কর বকেয়া: হোল্ডিং {holding_no}-এ ৩ বছরের ভূমি উন্নয়ন কর (১২,৫০০ টাকা) বকেয়া রয়েছে।",
                    f"Tax Default Alert: Holding {holding_no} has accumulated 3+ years of unpaid land development tax.",
                    json.dumps({"tax_id": tax_id, "arrears_bdt": 12500.00}),
                    "PENDING_REVIEW"
                ))
            else:
                tax_batch.append((tax_id, parcel_id, holding_no, "1430-1431", 450.00, 450.00, f"DAK-2024-{p_num:05d}", "PAID"))

            parcels_batch.append((
                parcel_id, "Dhaka", "Savar", mouza_name, jl_num, dag_num, khatian_num,
                survey_type, land_class, area_decimal, geojson, is_disputed, 'SYNTHETIC_DEMO_RECORD'
            ))

        # Insert batch
        cur.executemany("INSERT INTO parcels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", parcels_batch)
        cur.executemany("INSERT INTO parcel_ownership VALUES (?, ?, ?, ?, ?, ?, ?)", ownership_batch)
        cur.executemany("INSERT INTO deeds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", deeds_batch)
        cur.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", txns_batch)
        cur.executemany("INSERT INTO ownership_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)", events_batch)
        cur.executemany("INSERT INTO mutation_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", mutations_batch)
        cur.executemany("INSERT INTO tax_records VALUES (?, ?, ?, ?, ?, ?, ?, ?)", tax_batch)
        cur.executemany("INSERT INTO litigation_records VALUES (?, ?, ?, ?, ?, ?, ?)", lit_batch)
        cur.executemany("INSERT INTO khas_records VALUES (?, ?, ?, ?, ?)", khs_batch)
        cur.executemany("INSERT INTO verification_cases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", cases_batch)
        conn.commit()

    # 4. REVIEW LOGS FOR FIRST 20 CASES
    cur.execute("SELECT case_id FROM verification_cases LIMIT 20")
    case_ids = [r[0] for r in cur.fetchall()]
    review_logs_data = []
    for cid in case_ids:
        log_id = f"LOG-{log_idx:06d}"
        log_idx += 1
        review_logs_data.append((
            log_id, cid, "OFFICER-SAVAR-01", "REQUESTED_PHYSICAL_INSPECTION",
            "সন্দেহভাজন দলিল যাচাইয়ের জন্য সাব-রেজিস্ট্রি ভলিউম বই তলব ও সরেজমিন তদন্তের নির্দেশ প্রদান।",
            datetime.now(timezone.utc).isoformat()
        ))
    cur.executemany("INSERT INTO review_logs VALUES (?, ?, ?, ?, ?, ?)", review_logs_data)
    conn.commit()

    # 5. GENERATE REPRESENTATIVE PHYSICAL DOCUMENTS (50 files)
    print("Generating Representative Document Images for OCR and Cryptographic Testing...")
    os.makedirs(args.doc_dir, exist_ok=True)
    cur.execute("SELECT deed_id, deed_number, parcel_id FROM deeds LIMIT 50")
    sample_deeds = cur.fetchall()

    documents_data = []
    for deed in sample_deeds:
        d_id, d_no, p_id = deed
        doc_id = f"DOC-{doc_idx:06d}"
        doc_idx += 1
        doc_filename = f"{doc_id}_{d_no.replace('/', '_')}.png"
        doc_rel_path = os.path.join(args.doc_dir, doc_filename)

        sha256 = generate_sample_document_image(doc_id, "DEED_COPY", p_id, d_no, doc_rel_path)
        qr_token = f"QR-TOKEN-{sha256[:16]}"
        extracted_fields = json.dumps({"deed_no": d_no, "parcel_id": p_id, "office": "Savar Sub-Registry"})

        documents_data.append((
            doc_id, p_id, d_id, "DEED_COPY", doc_rel_path, sha256,
            qr_token, "SUCCESS", extracted_fields, "SYNTHETIC_DEMO_DOCUMENT"
        ))

    # Duplicate file fixture (DS-04)
    if len(documents_data) > 0:
        base_doc = documents_data[0]
        dup_doc_id = f"DOC-{doc_idx:06d}"
        doc_idx += 1
        documents_data.append((
            dup_doc_id, base_doc[1], base_doc[2], base_doc[3], base_doc[4],
            base_doc[5], f"QR-TOKEN-DUP-{base_doc[5][:16]}", "SUCCESS",
            base_doc[8], "SYNTHETIC_DEMO_DOCUMENT"
        ))

    cur.executemany("INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", documents_data)
    conn.commit()

    # 6. CREATE INDEXES
    print("Building Performance Indexes...")
    idx_start = time.time()
    cur.execute("CREATE INDEX idx_parcels_mouza_dag ON parcels(mouza, dag_number);")
    cur.execute("CREATE INDEX idx_parcels_khatian ON parcels(khatian_number);")
    cur.execute("CREATE INDEX idx_deeds_parcel_seller ON deeds(parcel_id, seller_id);")
    cur.execute("CREATE INDEX idx_deeds_number ON deeds(deed_number);")
    cur.execute("CREATE INDEX idx_mutation_deed ON mutation_records(deed_id, status);")
    cur.execute("CREATE INDEX idx_tax_parcel ON tax_records(parcel_id, payment_status);")
    cur.execute("CREATE INDEX idx_documents_hash ON documents(sha256_hash);")
    conn.commit()
    print(f"Indexes built in {time.time() - idx_start:.2f} seconds.")

    # Re-enable standard WAL mode for runtime
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")
    conn.commit()

    # 7. EXPORT CSVs (Streamed)
    print(f"Exporting CSVs to {args.export_csv}...")
    os.makedirs(args.export_csv, exist_ok=True)
    tables = [
        "parcels", "owners", "parcel_ownership", "deeds", "transactions",
        "ownership_events", "mutation_records", "documents", "tax_records",
        "litigation_records", "khas_records", "acquisition_zones",
        "verification_cases", "review_logs"
    ]
    manifest_counts = {}
    manifest_checksums = {}

    for tbl in tables:
        csv_file = os.path.join(args.export_csv, f"{tbl}.csv")
        cur.execute(f"SELECT * FROM {tbl}")
        col_names = [d[0] for d in cur.description]

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(col_names)
            row_count = 0
            while True:
                rows = cur.fetchmany(10000)
                if not rows:
                    break
                writer.writerows(rows)
                row_count += len(rows)

        manifest_counts[tbl] = row_count
        with open(csv_file, "rb") as f:
            manifest_checksums[f"{tbl}.csv"] = hashlib.sha256(f.read()).hexdigest()

    # 8. EXPORT SCENARIO CATALOG
    if args.scenario_catalog:
        print(f"Exporting Scenario Catalog to {args.scenario_catalog}...")
        os.makedirs(os.path.dirname(args.scenario_catalog), exist_ok=True)
        with open(args.scenario_catalog, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "scenario_id", "scenario_type", "parcel_id", "deed_references",
                "seller_id", "buyer_references", "expected_finding",
                "expected_severity", "expected_risk_score", "description"
            ])
            writer.writerows(scenario_catalog)

    conn.close()

    # Checksum database
    with open(args.output_db, "rb") as f:
        db_sha256 = hashlib.sha256(f.read()).hexdigest()

    # 9. MANIFEST
    print(f"Writing Manifest to {args.manifest}...")
    manifest = {
        "dataset_name": f"BHUMI_SYNC_SYNTHETIC_DATASET_{'FULL_SCALE' if is_full_scale else 'DRY_RUN'}",
        "schema_version": "1.0.0",
        "generator_script": "generators/generate_synthetic_dataset.py",
        "generator_seed": args.seed,
        "generation_timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "target_scale": {
            "parcels": args.parcels,
            "owners": args.owners
        },
        "actual_row_counts": manifest_counts,
        "database_file": {
            "path": args.output_db,
            "size_bytes": os.path.getsize(args.output_db),
            "sha256_checksum": db_sha256
        },
        "csv_checksums": manifest_checksums,
        "scenario_catalog": {
            "path": args.scenario_catalog,
            "count": len(scenario_catalog)
        },
        "provenance_standards": {
            "all_identities_synthetic": True,
            "zero_real_nid_pii": True,
            "statutory_schema_derivation": "SATA 1950, Registration Act 1908, LDTax Guidelines",
            "compliance_watermark": "SYNTHETIC_DEMO_RECORD"
        }
    }

    os.makedirs(os.path.dirname(args.manifest), exist_ok=True)
    with open(args.manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    total_duration = time.time() - start_time
    print(f"\n=== GENERATION FINISHED IN {total_duration:.2f} SECONDS ===")
    for tbl, count in manifest_counts.items():
        print(f"  - {tbl:22s}: {count:8,d} rows")
    print(f"Total Database Size: {os.path.getsize(args.output_db) / (1024*1024):.2f} MB")
    print(f"Database SHA-256: {db_sha256}")

if __name__ == "__main__":
    main()
