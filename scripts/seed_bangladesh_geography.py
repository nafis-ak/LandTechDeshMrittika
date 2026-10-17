"""
DESHMRITTIKA / BHUMI-SYNC — Bangladesh-Wide Administrative Geography Seeder
Populates:
1. All 8 Divisions (BBS Geocode Standard)
2. All 64 Districts (with coordinates and Bengali/English names)
3. 495+ Upazilas across all 64 districts
4. Representative Unions & Municipalities
5. Mouzas & JL numbers (grounded in Savar pilot and key regional centers)
"""

import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "generated" / "full_scale" / "landtech_synthetic.db"

# 1. 8 Divisions
DIVISIONS = [
    {"division_id": "DIV-10", "bbs_code": "10", "name_en": "Barishal", "name_bn": "বরিশাল", "lat": 22.7010, "lon": 90.3535},
    {"division_id": "DIV-20", "bbs_code": "20", "name_en": "Chattogram", "name_bn": "চট্টগ্রাম", "lat": 22.3569, "lon": 91.7832},
    {"division_id": "DIV-30", "bbs_code": "30", "name_en": "Dhaka", "name_bn": "ঢাকা", "lat": 23.8103, "lon": 90.4125},
    {"division_id": "DIV-40", "bbs_code": "40", "name_en": "Khulna", "name_bn": "খুলনা", "lat": 22.8456, "lon": 89.5403},
    {"division_id": "DIV-45", "bbs_code": "45", "name_en": "Mymensingh", "name_bn": "ময়মনসিংহ", "lat": 24.7471, "lon": 90.4203},
    {"division_id": "DIV-50", "bbs_code": "50", "name_en": "Rajshahi", "name_bn": "রাজশাহী", "lat": 24.3636, "lon": 88.6241},
    {"division_id": "DIV-55", "bbs_code": "55", "name_en": "Rangpur", "name_bn": "রংপুর", "lat": 25.7439, "lon": 89.2752},
    {"division_id": "DIV-60", "bbs_code": "60", "name_en": "Sylhet", "name_bn": "সিলেট", "lat": 24.8949, "lon": 91.8687},
]

# 2. All 64 Districts
DISTRICTS = [
    # Barishal Division (6)
    {"district_id": "DIST-04", "division_id": "DIV-10", "bbs_code": "04", "name_en": "Barguna", "name_bn": "বরগুনা", "lat": 22.1587, "lon": 90.1256},
    {"district_id": "DIST-06", "division_id": "DIV-10", "bbs_code": "06", "name_en": "Barishal", "name_bn": "বরিশাল", "lat": 22.7010, "lon": 90.3535},
    {"district_id": "DIST-09", "division_id": "DIV-10", "bbs_code": "09", "name_en": "Bhola", "name_bn": "ভোলা", "lat": 22.6859, "lon": 90.6481},
    {"district_id": "DIST-42", "division_id": "DIV-10", "bbs_code": "42", "name_en": "Jhalokati", "name_bn": "ঝালকাঠি", "lat": 22.6406, "lon": 90.1987},
    {"district_id": "DIST-78", "division_id": "DIV-10", "bbs_code": "78", "name_en": "Patuakhali", "name_bn": "পটুয়াখালী", "lat": 22.3596, "lon": 90.3299},
    {"district_id": "DIST-79", "division_id": "DIV-10", "bbs_code": "79", "name_en": "Pirojpur", "name_bn": "পিরোজপুর", "lat": 22.5841, "lon": 89.9720},

    # Chattogram Division (11)
    {"district_id": "DIST-03", "division_id": "DIV-20", "bbs_code": "03", "name_en": "Bandarban", "name_bn": "বান্দরবান", "lat": 22.1953, "lon": 92.2184},
    {"district_id": "DIST-12", "division_id": "DIV-20", "bbs_code": "12", "name_en": "Brahmanbaria", "name_bn": "ব্রাহ্মণবাড়িয়া", "lat": 23.9571, "lon": 91.1119},
    {"district_id": "DIST-13", "division_id": "DIV-20", "bbs_code": "13", "name_en": "Chandpur", "name_bn": "চাঁদপুর", "lat": 23.2333, "lon": 90.6667},
    {"district_id": "DIST-15", "division_id": "DIV-20", "bbs_code": "15", "name_en": "Chattogram", "name_bn": "চট্টগ্রাম", "lat": 22.3569, "lon": 91.7832},
    {"district_id": "DIST-22", "division_id": "DIV-20", "bbs_code": "22", "name_en": "Cox's Bazar", "name_bn": "কক্সবাজার", "lat": 21.4272, "lon": 92.0058},
    {"district_id": "DIST-19", "division_id": "DIV-20", "bbs_code": "19", "name_en": "Cumilla", "name_bn": "কুমিল্লা", "lat": 23.4682, "lon": 91.1788},
    {"district_id": "DIST-30", "division_id": "DIV-20", "bbs_code": "30", "name_en": "Feni", "name_bn": "ফেনী", "lat": 23.0159, "lon": 91.3976},
    {"district_id": "DIST-46", "division_id": "DIV-20", "bbs_code": "46", "name_en": "Khagrachhari", "name_bn": "খাগড়াছড়ি", "lat": 23.1193, "lon": 91.9847},
    {"district_id": "DIST-51", "division_id": "DIV-20", "bbs_code": "51", "name_en": "Lakshmipur", "name_bn": "লক্ষ্মীপুর", "lat": 22.9425, "lon": 90.8412},
    {"district_id": "DIST-75", "division_id": "DIV-20", "bbs_code": "75", "name_en": "Noakhali", "name_bn": "নোয়াখালী", "lat": 22.8696, "lon": 91.0994},
    {"district_id": "DIST-84", "division_id": "DIV-20", "bbs_code": "84", "name_en": "Rangamati", "name_bn": "রাঙ্গামাটি", "lat": 22.7324, "lon": 92.2985},

    # Dhaka Division (13)
    {"district_id": "DIST-26", "division_id": "DIV-30", "bbs_code": "26", "name_en": "Dhaka", "name_bn": "ঢাকা", "lat": 23.8103, "lon": 90.4125},
    {"district_id": "DIST-29", "division_id": "DIV-30", "bbs_code": "29", "name_en": "Faridpur", "name_bn": "ফরিদপুর", "lat": 23.6071, "lon": 89.8429},
    {"district_id": "DIST-33", "division_id": "DIV-30", "bbs_code": "33", "name_en": "Gazipur", "name_bn": "গাজীপুর", "lat": 24.0023, "lon": 90.4264},
    {"district_id": "DIST-35", "division_id": "DIV-30", "bbs_code": "35", "name_en": "Gopalganj", "name_bn": "গোপালগঞ্জ", "lat": 23.0051, "lon": 89.8266},
    {"district_id": "DIST-48", "division_id": "DIV-30", "bbs_code": "48", "name_en": "Kishoreganj", "name_bn": "কিশোরগঞ্জ", "lat": 24.4449, "lon": 90.7766},
    {"district_id": "DIST-54", "division_id": "DIV-30", "bbs_code": "54", "name_en": "Madaripur", "name_bn": "মাদারীপুর", "lat": 23.1641, "lon": 90.1897},
    {"district_id": "DIST-56", "division_id": "DIV-30", "bbs_code": "56", "name_en": "Manikganj", "name_bn": "মানিকগঞ্জ", "lat": 23.8644, "lon": 90.0047},
    {"district_id": "DIST-59", "division_id": "DIV-30", "bbs_code": "59", "name_en": "Munshiganj", "name_bn": "মুন্সীগঞ্জ", "lat": 23.5422, "lon": 90.5305},
    {"district_id": "DIST-67", "division_id": "DIV-30", "bbs_code": "67", "name_en": "Narayanganj", "name_bn": "নারায়ণগঞ্জ", "lat": 23.6337, "lon": 90.4965},
    {"district_id": "DIST-68", "division_id": "DIV-30", "bbs_code": "68", "name_en": "Narsingdi", "name_bn": "নরসিংদী", "lat": 23.9193, "lon": 90.7176},
    {"district_id": "DIST-82", "division_id": "DIV-30", "bbs_code": "82", "name_en": "Rajbari", "name_bn": "রাজবাড়ী", "lat": 23.7574, "lon": 89.6445},
    {"district_id": "DIST-86", "division_id": "DIV-30", "bbs_code": "86", "name_en": "Shariatpur", "name_bn": "শরীয়তপুর", "lat": 23.2423, "lon": 90.4348},
    {"district_id": "DIST-93", "division_id": "DIV-30", "bbs_code": "93", "name_en": "Tangail", "name_bn": "টাঙ্গাইল", "lat": 24.2513, "lon": 89.9167},

    # Khulna Division (10)
    {"district_id": "DIST-01", "division_id": "DIV-40", "bbs_code": "01", "name_en": "Bagerhat", "name_bn": "বাগেরহাট", "lat": 22.6516, "lon": 89.7859},
    {"district_id": "DIST-18", "division_id": "DIV-40", "bbs_code": "18", "name_en": "Chuadanga", "name_bn": "চুয়াডাঙ্গা", "lat": 23.6402, "lon": 88.8418},
    {"district_id": "DIST-41", "division_id": "DIV-40", "bbs_code": "41", "name_en": "Jashore", "name_bn": "যশোর", "lat": 23.1664, "lon": 89.2182},
    {"district_id": "DIST-44", "division_id": "DIV-40", "bbs_code": "44", "name_en": "Jhenaidah", "name_bn": "ঝিনাইদহ", "lat": 23.5450, "lon": 89.1539},
    {"district_id": "DIST-47", "division_id": "DIV-40", "bbs_code": "47", "name_en": "Khulna", "name_bn": "খুলনা", "lat": 22.8456, "lon": 89.5403},
    {"district_id": "DIST-50", "division_id": "DIV-40", "bbs_code": "50", "name_en": "Kushtia", "name_bn": "কুষ্টিয়া", "lat": 23.9013, "lon": 89.1204},
    {"district_id": "DIST-55", "division_id": "DIV-40", "bbs_code": "55", "name_en": "Magura", "name_bn": "মাগুরা", "lat": 23.4873, "lon": 89.4199},
    {"district_id": "DIST-57", "division_id": "DIV-40", "bbs_code": "57", "name_en": "Meherpur", "name_bn": "মেহেরপুর", "lat": 23.7622, "lon": 88.6318},
    {"district_id": "DIST-65", "division_id": "DIV-40", "bbs_code": "65", "name_en": "Narail", "name_bn": "নড়াইল", "lat": 23.1725, "lon": 89.5127},
    {"district_id": "DIST-87", "division_id": "DIV-40", "bbs_code": "87", "name_en": "Satkhira", "name_bn": "সাতক্ষীরা", "lat": 22.7185, "lon": 89.0705},

    # Mymensingh Division (4)
    {"district_id": "DIST-39", "division_id": "DIV-45", "bbs_code": "39", "name_en": "Jamalpur", "name_bn": "জামালপুর", "lat": 24.9375, "lon": 89.9378},
    {"district_id": "DIST-61", "division_id": "DIV-45", "bbs_code": "61", "name_en": "Mymensingh", "name_bn": "ময়মনসিংহ", "lat": 24.7471, "lon": 90.4203},
    {"district_id": "DIST-72", "division_id": "DIV-45", "bbs_code": "72", "name_en": "Netrokona", "name_bn": "নেত্রকোণা", "lat": 24.8709, "lon": 90.7279},
    {"district_id": "DIST-89", "division_id": "DIV-45", "bbs_code": "89", "name_en": "Sherpur", "name_bn": "শেরপুর", "lat": 25.0205, "lon": 90.0153},

    # Rajshahi Division (8)
    {"district_id": "DIST-10", "division_id": "DIV-50", "bbs_code": "10", "name_en": "Bogura", "name_bn": "বগুড়া", "lat": 24.8465, "lon": 89.3777},
    {"district_id": "DIST-38", "division_id": "DIV-50", "bbs_code": "38", "name_en": "Joypurhat", "name_bn": "জয়পুরহাট", "lat": 25.1015, "lon": 89.0277},
    {"district_id": "DIST-64", "division_id": "DIV-50", "bbs_code": "64", "name_en": "Naogaon", "name_bn": "নওগাঁ", "lat": 24.7936, "lon": 88.9318},
    {"district_id": "DIST-69", "division_id": "DIV-50", "bbs_code": "69", "name_en": "Natore", "name_bn": "নাটোর", "lat": 24.4206, "lon": 89.0003},
    {"district_id": "DIST-70", "division_id": "DIV-50", "bbs_code": "70", "name_en": "Chapainawabganj", "name_bn": "চাঁপাইনবাবগঞ্জ", "lat": 24.5965, "lon": 88.2775},
    {"district_id": "DIST-76", "division_id": "DIV-50", "bbs_code": "76", "name_en": "Pabna", "name_bn": "পাবনা", "lat": 24.0064, "lon": 89.2372},
    {"district_id": "DIST-81", "division_id": "DIV-50", "bbs_code": "81", "name_en": "Rajshahi", "name_bn": "রাজশাহী", "lat": 24.3636, "lon": 88.6241},
    {"district_id": "DIST-88", "division_id": "DIV-50", "bbs_code": "88", "name_en": "Sirajganj", "name_bn": "সিরাজগঞ্জ", "lat": 24.4534, "lon": 89.7008},

    # Rangpur Division (8)
    {"district_id": "DIST-27", "division_id": "DIV-55", "bbs_code": "27", "name_en": "Dinajpur", "name_bn": "দিনাজপুর", "lat": 25.6217, "lon": 88.6355},
    {"district_id": "DIST-32", "division_id": "DIV-55", "bbs_code": "32", "name_en": "Gaibandha", "name_bn": "গাইবান্ধা", "lat": 25.3288, "lon": 89.5408},
    {"district_id": "DIST-49", "division_id": "DIV-55", "bbs_code": "49", "name_en": "Kurigram", "name_bn": "কুড়িগ্রাম", "lat": 25.8054, "lon": 89.6362},
    {"district_id": "DIST-52", "division_id": "DIV-55", "bbs_code": "52", "name_en": "Lalmonirhat", "name_bn": "লালমনিরহাট", "lat": 25.9923, "lon": 89.2847},
    {"district_id": "DIST-73", "division_id": "DIV-55", "bbs_code": "73", "name_en": "Nilphamari", "name_bn": "নীলফামারী", "lat": 25.9318, "lon": 88.8560},
    {"district_id": "DIST-77", "division_id": "DIV-55", "bbs_code": "77", "name_en": "Panchagarh", "name_bn": "পঞ্চগড়", "lat": 26.3411, "lon": 88.5542},
    {"district_id": "DIST-85", "division_id": "DIV-55", "bbs_code": "85", "name_en": "Rangpur", "name_bn": "রংপুর", "lat": 25.7439, "lon": 89.2752},
    {"district_id": "DIST-94", "division_id": "DIV-55", "bbs_code": "94", "name_en": "Thakurgaon", "name_bn": "ঠাকুরগাঁও", "lat": 26.0337, "lon": 88.4617},

    # Sylhet Division (4)
    {"district_id": "DIST-36", "division_id": "DIV-60", "bbs_code": "36", "name_en": "Habiganj", "name_bn": "হবিগঞ্জ", "lat": 24.3749, "lon": 91.4155},
    {"district_id": "DIST-58", "division_id": "DIV-60", "bbs_code": "58", "name_en": "Moulvibazar", "name_bn": "মৌলভীবাজার", "lat": 24.4829, "lon": 91.7774},
    {"district_id": "DIST-90", "division_id": "DIV-60", "bbs_code": "90", "name_en": "Sunamganj", "name_bn": "সুনামগঞ্জ", "lat": 25.0658, "lon": 91.3950},
    {"district_id": "DIST-91", "division_id": "DIV-60", "bbs_code": "91", "name_en": "Sylhet", "name_bn": "সিলেট", "lat": 24.8949, "lon": 91.8687},
]

# 3. Comprehensive Upazila mapping for all 64 districts (all ~495 Upazilas)
# We structure this by district_id -> list of (bbs_suffix, name_en, name_bn, lat_offset, lon_offset)
UPAZILA_DATA = {
    # Dhaka (DIST-26)
    "DIST-26": [
        ("72", "Savar", "সাভার", 23.8560, 90.2600),
        ("14", "Dhamrai", "ধামরাই", 23.9167, 90.2167),
        ("38", "Keraniganj", "কেরানীগঞ্জ", 23.6833, 90.3167),
        ("18", "Dohar", "দোহার", 23.5939, 90.1256),
        ("62", "Nawabganj", "নবাবগঞ্জ", 23.6667, 90.1667),
        ("50", "Mirpur", "মিরপুর", 23.8055, 90.3685),
        ("52", "Mohammadpur", "মোহাম্মদপুর", 23.7542, 90.3619),
        ("32", "Gulshan", "গুলশান", 23.7925, 90.4078),
        ("20", "Dhanmondi", "ধানমন্ডি", 23.7461, 90.3742),
        ("90", "Uttara", "উত্তরা", 23.8759, 90.3795),
        ("85", "Tejgaon", "তেজগাঁও", 23.7598, 90.3912),
        ("75", "Ramna", "রমনা", 23.7372, 90.4011)
    ],
    # Gazipur (DIST-33)
    "DIST-33": [
        ("30", "Gazipur Sadar", "গাজীপুর সদর", 24.0023, 90.4264),
        ("32", "Kaliakair", "কালিয়াকৈর", 24.0750, 90.2167),
        ("34", "Kaliganj", "কালীগঞ্জ", 23.9917, 90.5667),
        ("36", "Kapasia", "কাপাসিয়া", 24.1167, 90.5667),
        ("86", "Sreepur", "শ্রীপুর", 24.2000, 90.4667)
    ],
    # Narayanganj (DIST-67)
    "DIST-67": [
        ("58", "Narayanganj Sadar", "নারায়ণগঞ্জ সদর", 23.6337, 90.4965),
        ("04", "Araihazar", "আড়াইহাজার", 23.7833, 90.6500),
        ("06", "Bandar", "বন্দর", 23.5917, 90.5250),
        ("68", "Rupganj", "রূপগঞ্জ", 23.7917, 90.5167),
        ("02", "Sonargaon", "সোনারগাঁও", 23.6500, 90.6000)
    ],
    # Manikganj (DIST-56)
    "DIST-56": [
        ("46", "Manikganj Sadar", "মানিকগঞ্জ সদর", 23.8644, 90.0047),
        ("10", "Daulatpur", "দৌলতপুর", 23.9833, 89.8333),
        ("22", "Ghior", "ঘিওর", 23.8833, 89.8333),
        ("28", "Harirampur", "হরিরামপুর", 23.7333, 89.9667),
        ("70", "Saturia", "সাটুরিয়া", 23.9500, 90.0167),
        ("78", "Shivalaya", "শিবালয়", 23.8333, 89.7833),
        ("82", "Singair", "সিংগাইর", 23.8167, 90.1500)
    ],
    # Munshiganj (DIST-59)
    "DIST-59": [
        ("56", "Munshiganj Sadar", "মুন্সীগঞ্জ সদর", 23.5422, 90.5305),
        ("24", "Gazaria", "গজারিয়া", 23.5500, 90.6000),
        ("44", "Lohajang", "লৌহজং", 23.4667, 90.3333),
        ("74", "Sirajdikhan", "সিরাজদিখান", 23.5833, 90.3667),
        ("84", "Sreenagar", "শ্রীনগর", 23.5333, 90.2833),
        ("94", "Tongibari", "টঙ্গীবাড়ী", 23.5000, 90.4500)
    ],
    # Narsingdi (DIST-68)
    "DIST-68": [
        ("60", "Narsingdi Sadar", "নরসিংদী সদর", 23.9193, 90.7176),
        ("07", "Belabo", "বেলাবো", 24.1000, 90.8500),
        ("52", "Monohardi", "মনোহরদী", 24.1333, 90.7000),
        ("63", "Palash", "পলাশ", 23.9500, 90.6167),
        ("64", "Raipura", "রায়পুরা", 23.9833, 90.8667),
        ("76", "Shibpur", "শিবপুর", 24.0333, 90.7333)
    ],
    # Tangail (DIST-93)
    "DIST-93": [
        ("95", "Tangail Sadar", "টাঙ্গাইল সদর", 24.2513, 89.9167),
        ("05", "Basail", "বাসাইল", 24.2167, 90.0500),
        ("09", "Bhuapur", "ভুয়াপুর", 24.4667, 89.8667),
        ("19", "Delduar", "দেলদুয়ার", 24.1500, 89.9667),
        ("23", "Dhanbari", "ধনবাড়ী", 24.6667, 89.8667),
        ("38", "Ghatail", "ঘাটাইল", 24.5000, 90.0000),
        ("47", "Gopalpur", "গোপালপুর", 24.5500, 89.9167),
        ("57", "Kalihati", "কালিহাতী", 24.3833, 90.0000),
        ("66", "Madhupur", "মধুপুর", 24.6167, 90.0333),
        ("76", "Mirzapur", "মির্জাপুর", 24.1000, 90.1000),
        ("85", "Nagarpur", "নাগরপুর", 24.0500, 89.8667),
        ("90", "Sakhipur", "সখীপুর", 24.3167, 90.1667)
    ],
    # Faridpur (DIST-29)
    "DIST-29": [
        ("47", "Faridpur Sadar", "ফরিদপুর সদর", 23.6071, 89.8429),
        ("03", "Alfadanga", "আলফাডাঙ্গা", 23.2833, 89.7000),
        ("10", "Bhanga", "ভাঙ্গা", 23.3833, 89.9833),
        ("18", "Boalmari", "বোয়ালমারী", 23.3833, 89.6833),
        ("21", "Charbhadrasan", "চরভদ্রাসন", 23.6000, 90.0167),
        ("56", "Madhukhali", "মধুখালী", 23.5500, 89.6333),
        ("62", "Nagarkanda", "নগরকান্দা", 23.4167, 89.8833),
        ("84", "Sadarpur", "সদরপুর", 23.4833, 90.0333),
        ("90", "Saltha", "সালথা", 23.4667, 89.7833)
    ],
    # Gopalganj (DIST-35)
    "DIST-35": [
        ("32", "Gopalganj Sadar", "গোপালগঞ্জ সদর", 23.0051, 89.8266),
        ("43", "Kashiani", "কাশিয়ানী", 23.2167, 89.7000),
        ("48", "Kotalipara", "কোটালীপাড়া", 22.9833, 90.0000),
        ("51", "Muksudpur", "মুকসুদপুর", 23.3167, 89.8667),
        ("86", "Tungipara", "টুঙ্গিপাড়া", 22.9000, 89.9000)
    ],
    # Madaripur (DIST-54)
    "DIST-54": [
        ("40", "Madaripur Sadar", "মাদারীপুর সদর", 23.1641, 90.1897),
        ("44", "Kalkini", "কালকিনি", 23.0667, 90.2333),
        ("80", "Rajoir", "রাজৈর", 23.2000, 89.9333),
        ("87", "Shibchar", "শিবচর", 23.3500, 90.1667)
    ],
    # Rajbari (DIST-82)
    "DIST-82": [
        ("76", "Rajbari Sadar", "রাজবাড়ী সদর", 23.7574, 89.6445),
        ("07", "Baliakandi", "বালিয়াকান্দি", 23.6333, 89.5500),
        ("29", "Goalandaghat", "গোয়ালন্দঘাট", 23.7333, 89.7667),
        ("73", "Pangsha", "পাংশা", 23.7833, 89.4167),
        ("77", "Kalukhali", "কালুখালী", 23.7167, 89.5000)
    ],
    # Shariatpur (DIST-86)
    "DIST-86": [
        ("69", "Shariatpur Sadar", "শরীয়তপুর সদর", 23.2423, 90.4348),
        ("14", "Bhedarganj", "ভেদরগঞ্জ", 23.1500, 90.4333),
        ("25", "Damudya", "ডামুড্যা", 23.1333, 90.4333),
        ("36", "Gosairhat", "গোসাইরহাট", 23.0667, 90.4667),
        ("65", "Naria", "নড়িয়া", 23.3167, 90.4167),
        ("94", "Zajira", "জাজিরা", 23.3500, 90.3167)
    ],
    # Kishoreganj (DIST-48)
    "DIST-48": [
        ("49", "Kishoreganj Sadar", "কিশোরগঞ্জ সদর", 24.4449, 90.7766),
        ("02", "Austagram", "অষ্টগ্রাম", 24.2667, 91.1167),
        ("06", "Bajitpur", "বাজিতপুর", 24.2167, 90.9500),
        ("11", "Bhairab", "ভৈরব", 24.0500, 90.9833),
        ("27", "Hossainpur", "হোসেনপুর", 24.4167, 90.6500),
        ("33", "Itna", "ইটনা", 24.5333, 91.0833),
        ("42", "Karimganj", "করিমগঞ্জ", 24.4667, 90.8833),
        ("45", "Katiadi", "কটিয়াদী", 24.2500, 90.8000),
        ("54", "Kuliarchar", "কুলিয়ারচর", 24.1500, 90.9000),
        ("59", "Mithamain", "মিঠামইন", 24.4333, 91.0500),
        ("79", "Nikli", "নিকলী", 24.3167, 90.9333),
        ("92", "Pakundia", "পাকুন্দিয়া", 24.3333, 90.6833),
        ("96", "Tarail", "তাড়াইল", 24.5500, 90.8667)
    ],

    # Chattogram (DIST-15)
    "DIST-15": [
        ("41", "Chattogram Sadar", "চট্টগ্রাম সদর", 22.3569, 91.7832),
        ("04", "Anwara", "আনোয়ারা", 22.2167, 91.9167),
        ("08", "Banshkhali", "বাঁশখালী", 22.0500, 91.9500),
        ("12", "Boalkhali", "বোয়ালখালী", 22.3833, 91.9167),
        ("18", "Chandanaish", "চন্দনাইশ", 22.2167, 92.0500),
        ("33", "Fatikchhari", "ফটিকছড়ি", 22.6833, 91.7833),
        ("37", "Hathazari", "হাটহাজারী", 22.5000, 91.8000),
        ("47", "Lohagara", "লোহাগাড়া", 22.0000, 92.1000),
        ("53", "Mirsharai", "মীরসরাই", 22.7667, 91.5833),
        ("61", "Patiya", "পটিয়া", 22.3000, 91.9833),
        ("70", "Rangunia", "রাঙ্গুনিয়া", 22.4667, 92.0500),
        ("74", "Raozan", "রাউজান", 22.5333, 91.9167),
        ("78", "Sandwip", "সন্দ্বীপ", 22.5000, 91.4333),
        ("82", "Satkania", "সাতকানিয়া", 22.1000, 92.0500),
        ("86", "Sitakunda", "সীতাকুণ্ড", 22.6167, 91.6667),
        ("43", "Karnaphuli", "কর্ণফুলী", 22.2833, 91.8500)
    ],
    # Cox's Bazar (DIST-22)
    "DIST-22": [
        ("24", "Cox's Bazar Sadar", "কক্সবাজার সদর", 21.4272, 92.0058),
        ("16", "Chakaria", "চকরিয়া", 21.7833, 92.0833),
        ("45", "Kutubdia", "কুতুবদিয়া", 21.8167, 91.8500),
        ("49", "Maheshkhali", "মহেশখালী", 21.5500, 91.9667),
        ("56", "Pekua", "পেকুয়া", 21.8000, 91.9833),
        ("66", "Ramu", "রামু", 21.4500, 92.1000),
        ("90", "Teknaf", "টেকনাফ", 20.8667, 92.3000),
        ("94", "Ukhia", "উখিয়া", 21.2833, 92.1333)
    ],
    # Cumilla (DIST-19)
    "DIST-19": [
        ("33", "Cumilla Adarsha Sadar", "কুমিল্লা আদর্শ সদর", 23.4682, 91.1788),
        ("09", "Barura", "বরুড়া", 23.3667, 91.0500),
        ("15", "Brahmanpara", "ব্রাহ্মণপাড়া", 23.6167, 91.1167),
        ("18", "Burichang", "বুড়িচং", 23.5500, 91.1333),
        ("27", "Chandina", "চান্দিনা", 23.4833, 91.0000),
        ("31", "Chauddagram", "চৌদ্দগ্রাম", 23.2167, 91.3167),
        ("36", "Daudkandi", "দাউদকান্দি", 23.5333, 90.7167),
        ("40", "Debidwar", "দেবিদ্বার", 23.6000, 90.9833),
        ("54", "Homna", "হোমনা", 23.6833, 90.7833),
        ("67", "Laksam", "লাকসাম", 23.2500, 91.1333),
        ("72", "Muradnagar", "মুরাদনগর", 23.6333, 90.9333),
        ("75", "Nangalkot", "নাঙ্গলকোট", 23.1667, 91.2000),
        ("81", "Meghna", "মেঘনা", 23.6167, 90.6667),
        ("87", "Titas", "তিতাস", 23.5833, 90.8000),
        ("94", "Monohargonj", "মনোহরগঞ্জ", 23.1833, 91.1000)
    ],
    # Sylhet (DIST-91)
    "DIST-91": [
        ("62", "Sylhet Sadar", "সিলেট সদর", 24.8949, 91.8687),
        ("08", "Balaganj", "বালাগঞ্জ", 24.6667, 91.8333),
        ("17", "Beanibazar", "বিয়ানীবাজার", 24.8333, 92.1667),
        ("20", "Bishwanath", "বিশ্বনাথ", 24.7833, 91.7667),
        ("27", "Companiganj", "কোম্পানীগঞ্জ", 25.0833, 91.7500),
        ("31", "Fenchuganj", "ফেঞ্চুগঞ্জ", 24.7000, 91.9500),
        ("35", "Golapganj", "গোলাপগঞ্জ", 24.8667, 92.0167),
        ("38", "Gowainghat", "গোয়াইনঘাট", 25.1000, 92.0000),
        ("41", "Jaintiapur", "জৈন্তাপুর", 25.1333, 92.1167),
        ("53", "Kanaighat", "কানাইঘাট", 25.0167, 92.2667),
        ("94", "Zakiganj", "জকিগঞ্জ", 24.8833, 92.3667),
        ("23", "Dakshin Surma", "দক্ষিণ সুরমা", 24.8333, 91.8667),
        ("60", "Osmaninagar", "ওসমানীনগর", 24.7167, 91.7333)
    ],
    # Rajshahi (DIST-81)
    "DIST-81": [
        ("72", "Rajshahi Sadar (Boalia)", "রাজশাহী সদর (বোয়ালিয়া)", 24.3636, 88.6241),
        ("10", "Bagha", "বাঘা", 24.1833, 88.8333),
        ("12", "Bagmara", "বাগমারা", 24.5667, 88.8000),
        ("25", "Charghat", "চারঘাট", 24.2833, 88.7500),
        ("34", "Durgapur", "দুর্গাপুর", 24.4500, 88.7667),
        ("43", "Godagari", "গোদাগাড়ী", 24.4667, 88.3333),
        ("53", "Mohanpur", "মোহনপুর", 24.5500, 88.6500),
        ("70", "Paba", "পবা", 24.4333, 88.6167),
        ("82", "Puthia", "পুঠিয়া", 24.3667, 88.8333),
        ("94", "Tanore", "তানোর", 24.5833, 88.5833)
    ],
    # Bogura (DIST-10)
    "DIST-10": [
        ("20", "Bogura Sadar", "বগুড়া সদর", 24.8465, 89.3777),
        ("06", "Adamdighi", "আদমদীঘি", 24.7833, 89.0500),
        ("27", "Dhunat", "ধুনট", 24.6833, 89.5333),
        ("33", "Dhupchanchia", "দুপচাঁচিয়া", 24.8667, 89.1667),
        ("40", "Gabtali", "গাবতলী", 24.8833, 89.5000),
        ("54", "Kahaloo", "কাহালু", 24.8333, 89.2667),
        ("67", "Nandigram", "নন্দীগ্রাম", 24.6833, 89.1833),
        ("81", "Sariakandi", "সারিয়াকান্দি", 24.8833, 89.6500),
        ("88", "Shajahanpur", "শাজাহানপুর", 24.7667, 89.4000),
        ("94", "Sherpur", "শেরপুর", 24.6667, 89.4167),
        ("95", "Shibganj", "শিবগঞ্জ", 24.9833, 89.3167),
        ("97", "Sonatola", "সোনাতলা", 25.0000, 89.5000)
    ],
    # Khulna (DIST-47)
    "DIST-47": [
        ("51", "Khulna Sadar (Kotwali)", "খুলনা সদর (কোতোয়ালী)", 22.8456, 89.5403),
        ("12", "Batiaghata", "বটিয়াঘাটা", 22.7500, 89.5167),
        ("17", "Dacope", "দাকোপ", 22.5667, 89.5167),
        ("21", "Dighalia", "দিঘলিয়া", 22.9000, 89.5333),
        ("30", "Dumuria", "ডুমুরিয়া", 22.8000, 89.4167),
        ("40", "Koyra", "কয়রা", 22.3500, 89.3000),
        ("64", "Paikgachha", "পাইকগাছা", 22.5833, 89.3333),
        ("69", "Phultala", "ফুলতলা", 22.9667, 89.4667),
        ("75", "Rupsha", "রূপসা", 22.8333, 89.5833),
        ("94", "Terokhada", "তেরখাদা", 22.9333, 89.6667)
    ],
    # Barishal (DIST-06)
    "DIST-06": [
        ("51", "Barishal Sadar (Kotwali)", "বরিশাল সদর (কোতোয়ালী)", 22.7010, 90.3535),
        ("02", "Agailjhara", "আগৈলঝাড়া", 22.9667, 90.1500),
        ("03", "Babuganj", "বাবুগঞ্জ", 22.8333, 90.3167),
        ("07", "Bakerganj", "বাকেরগঞ্জ", 22.5500, 90.3833),
        ("10", "Banaripara", "বানারীপাড়া", 22.7833, 90.1667),
        ("32", "Gaurnadi", "গৌরনদী", 22.9667, 90.2333),
        ("36", "Hizla", "হিজলা", 22.9000, 90.5000),
        ("62", "Mehendiganj", "মেহেন্দীগঞ্জ", 22.8167, 90.5333),
        ("69", "Muladi", "মুলাদী", 22.9167, 90.4167),
        ("94", "Wazirpur", "উজিরপুর", 22.8167, 90.2500)
    ],
    # Rangpur (DIST-85)
    "DIST-85": [
        ("49", "Rangpur Sadar", "রংপুর সদর", 25.7439, 89.2752),
        ("03", "Badarganj", "বদরগঞ্জ", 25.6833, 89.0500),
        ("27", "Gangachhara", "গংগাচড়া", 25.8500, 89.2167),
        ("42", "Kaunia", "কাউনিয়া", 25.7667, 89.4167),
        ("58", "Mithapukur", "মিঠাপুকুর", 25.5833, 89.2833),
        ("73", "Pirgachha", "পীরগাছা", 25.5833, 89.4000),
        ("76", "Pirganj", "পীরগঞ্জ", 25.4167, 89.3167),
        ("92", "Taraganj", "তারাগঞ্জ", 25.8167, 89.0167)
    ],
    # Mymensingh (DIST-61)
    "DIST-61": [
        ("52", "Mymensingh Sadar", "ময়মনসিংহ সদর", 24.7471, 90.4203),
        ("16", "Bhaluka", "ভালুকা", 24.3833, 90.3833),
        ("20", "Dhobaura", "ধোবাউড়া", 25.1000, 90.5833),
        ("24", "Fulbaria", "ফুলবাড়ীয়া", 24.6333, 90.2667),
        ("31", "Gaffargaon", "গফরগাঁও", 24.4333, 90.5500),
        ("38", "Gauripur", "গৌরীপুর", 24.7667, 90.5667),
        ("43", "Haluaghat", "হালুয়াঘাট", 25.1333, 90.3500),
        ("47", "Ishwarganj", "ঈশ্বরগঞ্জ", 24.6833, 90.6000),
        ("65", "Muktagachha", "মুক্তাগাছা", 24.7667, 90.2667),
        ("72", "Nandail", "নান্দাইল", 24.5667, 90.6833),
        ("81", "Phulpur", "ফুলপুর", 24.9500, 90.3500),
        ("85", "Trishal", "ত্রিশাল", 24.5833, 90.4000),
        ("94", "Tara Khanda", "তারাকান্দা", 24.8667, 90.4167)
    ]
}

# Generic generator for remaining 49 districts to guarantee 100% of 64 districts have Sadar + 3-5 upazilas
DEFAULT_DISTRICT_UPAZILAS = {
    # Barishal Division
    "DIST-04": [("01", "Barguna Sadar", "বরগুনা সদর"), ("02", "Amtali", "আমতলী"), ("03", "Bamna", "বামনা"), ("04", "Betagi", "বেতাগী"), ("05", "Patharghata", "পাথরঘাটা"), ("06", "Taltali", "তালতলী")],
    "DIST-09": [("01", "Bhola Sadar", "ভোলা সদর"), ("02", "Burhanuddin", "বোরহানউদ্দিন"), ("03", "Char Fasson", "চরফ্যাশন"), ("04", "Daulatkhan", "দৌলতখান"), ("05", "Lalmohan", "লালমোহন"), ("06", "Monpura", "মনপুরা"), ("07", "Tazumuddin", "তজুমদ্দিন")],
    "DIST-42": [("01", "Jhalokati Sadar", "ঝালকাঠি সদর"), ("02", "Kathalia", "কাঠালিয়া"), ("03", "Nalchity", "নলছিটি"), ("04", "Rajapur", "রাজাপুর")],
    "DIST-78": [("01", "Patuakhali Sadar", "পটুয়াখালী সদর"), ("02", "Bauphal", "বাউফল"), ("03", "Dashmina", "দশমিনা"), ("04", "Galachipa", "গলাচিপা"), ("05", "Kalapara", "কলাপাড়া"), ("06", "Mirzaganj", "মির্জাগঞ্জ"), ("07", "Rangabali", "রাঙ্গাবালী"), ("08", "Dumki", "দুমকি")],
    "DIST-79": [("01", "Pirojpur Sadar", "পিরোজপুর সদর"), ("02", "Bhandaria", "ভান্ডারিয়া"), ("03", "Kawkhali", "কাউখালী"), ("04", "Mathbaria", "মঠবাড়ীয়া"), ("05", "Nazirpur", "নাজিরপুর"), ("06", "Nesarabad", "নেছারাবাদ"), ("07", "Zianagar (Indurkani)", "ইন্দুরকানী")],

    # Chattogram Division
    "DIST-03": [("01", "Bandarban Sadar", "বান্দরবান সদর"), ("02", "Ali Kadam", "আলীকদম"), ("03", "Lama", "লামা"), ("04", "Naikhongchhari", "নাইক্ষ্যংছড়ি"), ("05", "Rowangchhari", "রোয়াংছড়ি"), ("06", "Ruma", "রুমা"), ("07", "Thanchi", "থানচি")],
    "DIST-12": [("01", "Brahmanbaria Sadar", "ব্রাহ্মণবাড়িয়া সদর"), ("02", "Ashuganj", "আশুগঞ্জ"), ("03", "Bancharampur", "বাঞ্ছারামপুর"), ("04", "Kasba", "কসবা"), ("05", "Nabinagar", "নবীনগর"), ("06", "Nasirnagar", "নাসিরনগর"), ("07", "Sarail", "সরাইল"), ("08", "Akhaura", "আখাউড়া"), ("09", "Bijoynagar", "বিজয়নগর")],
    "DIST-13": [("01", "Chandpur Sadar", "চাঁদপুর সদর"), ("02", "Faridganj", "ফরিদগঞ্জ"), ("03", "Haimchar", "হাইমচর"), ("04", "Haziganj", "হাজীগঞ্জ"), ("05", "Kachua", "কচুয়া"), ("06", "Matlab Dakshin", "মতলব দক্ষিণ"), ("07", "Matlab Uttar", "মতলব উত্তর"), ("08", "Shahrasti", "শাহরাস্তি")],
    "DIST-30": [("01", "Feni Sadar", "ফেনী সদর"), ("02", "Chhagalnaiya", "ছাগলনাইয়া"), ("03", "Daganbhuiyan", "দাগনভূঞা"), ("04", "Parshuram", "পরশুরাম"), ("05", "Fulgazi", "ফুলগাজী"), ("06", "Sonagazi", "সোনাগাজী")],
    "DIST-46": [("01", "Khagrachhari Sadar", "খাগড়াছড়ি সদর"), ("02", "Dighinala", "দিঘীনালা"), ("03", "Lakshmichhari", "লক্ষ্মীছড়ি"), ("04", "Mahalchhari", "মহালছড়ি"), ("05", "Manikchhari", "মানিকছড়ি"), ("06", "Matiranga", "মাটিরাঙ্গা"), ("07", "Panchhari", "পানছড়ি"), ("08", "Ramgarh", "রামগড়"), ("09", "Guimara", "গুইমারা")],
    "DIST-51": [("01", "Lakshmipur Sadar", "লক্ষ্মীপুর সদর"), ("02", "Raipur", "রায়পুর"), ("03", "Ramganj", "রামগঞ্জ"), ("04", "Ramgati", "রামগতি"), ("05", "Kamalnagar", "কমলনগর")],
    "DIST-75": [("01", "Noakhali Sadar (Sudharam)", "নোয়াখালী সদর (সুধারাম)"), ("02", "Begumganj", "বেগমগঞ্জ"), ("03", "Chatkhil", "চাটখিল"), ("04", "Companiganj", "কোম্পানীগঞ্জ"), ("05", "Hatiya", "হাতিয়া"), ("06", "Senbagh", "সেনবাগ"), ("07", "Sonaimuri", "সোনাইমুড়ী"), ("08", "Subarnachar", "সুবর্ণচর"), ("09", "Kabirhat", "কবিরহাট")],
    "DIST-84": [("01", "Rangamati Sadar", "রাঙ্গামাটি সদর"), ("02", "Bagaichhari", "বাঘাইছড়ি"), ("03", "Barkal", "বরকল"), ("04", "Belaichhari", "বিলাইছড়ি"), ("05", "Juraichhari", "জুরাইছড়ি"), ("06", "Kaptai", "কাপ্তাই"), ("07", "Kawkhali", "কাউখালী"), ("08", "Langadu", "লংগদু"), ("09", "Naniarchar", "নানিয়ারচর"), ("10", "Rajasthali", "রাজস্থলী")],

    # Khulna Division
    "DIST-01": [("01", "Bagerhat Sadar", "বাগেরহাট সদর"), ("02", "Chitalmari", "চিতলমারী"), ("03", "Fakirhat", "ফকিরহাট"), ("04", "Kachua", "কচুয়া"), ("05", "Mollahat", "মোল্লাহাট"), ("06", "Mongla", "মোংলা"), ("07", "Morrelganj", "মোড়েলগঞ্জ"), ("08", "Rampal", "রামপাল"), ("09", "Sarankhola", "শরণখোলা")],
    "DIST-18": [("01", "Chuadanga Sadar", "চুয়াডাঙ্গা সদর"), ("02", "Alamdanga", "আলমডাঙ্গা"), ("03", "Damurhuda", "দামুড়হুদা"), ("04", "Jibannagar", "জীবননগর")],
    "DIST-41": [("01", "Jashore Sadar", "যশোর সদর"), ("02", "Abhaynagar", "অভয়নগর"), ("03", "Bagherpara", "বাঘারপাড়া"), ("04", "Chaugachha", "চৌগাছা"), ("05", "Jhikargachha", "ঝিকরগাছা"), ("06", "Keshabpur", "কেশবপুর"), ("07", "Manirampur", "মণিরামপুর"), ("08", "Sharsha", "শার্শা")],
    "DIST-44": [("01", "Jhenaidah Sadar", "ঝিনাইদহ সদর"), ("02", "Harinakundu", "হরিণাকুণ্ডু"), ("03", "Kaliganj", "কালীগঞ্জ"), ("04", "Kotchandpur", "কোটচাঁদপুর"), ("05", "Maheshpur", "মহেশপুর"), ("06", "Shailkupa", "শৈলকূপা")],
    "DIST-50": [("01", "Kushtia Sadar", "কুষ্টিয়া সদর"), ("02", "Bheramara", "ভেড়ামারা"), ("03", "Daulatpur", "দৌলতপুর"), ("04", "Khoksa", "খোকসা"), ("05", "Kumarkhali", "কুমারখালী"), ("06", "Mirpur", "মিরপুর")],
    "DIST-55": [("01", "Magura Sadar", "মাগুরা সদর"), ("02", "Mohammadpur", "মোহাম্মদপুর"), ("03", "Shalikha", "শালিখা"), ("04", "Sreepur", "শ্রীপুর")],
    "DIST-57": [("01", "Meherpur Sadar", "মেহেরপুর সদর"), ("02", "Gangni", "গাংনী"), ("03", "Mujibnagar", "মুজিবনগর")],
    "DIST-65": [("01", "Narail Sadar", "নড়াইল সদর"), ("02", "Kalia", "কালিয়া"), ("03", "Lohagara", "লোহাগাড়া")],
    "DIST-87": [("01", "Satkhira Sadar", "সাতক্ষীরা সদর"), ("02", "Assasuni", "আশাশুনি"), ("03", "Debhata", "দেবহাটা"), ("04", "Kalaroa", "কলারোয়া"), ("05", "Kaliganj", "কালীগঞ্জ"), ("06", "Shyamnagar", "শ্যামনগর"), ("07", "Tala", "তালা")],

    # Mymensingh Division
    "DIST-39": [("01", "Jamalpur Sadar", "জামালপুর সদর"), ("02", "Bakshiganj", "বকশীগঞ্জ"), ("03", "Dewanganj", "দেওয়ানগঞ্জ"), ("04", "Islampur", "ইসলামপুর"), ("05", "Madarganj", "মাদারগঞ্জ"), ("06", "Melandaha", "মেলান্দহ"), ("07", "Sarishabari", "সরিষাবাড়ী")],
    "DIST-72": [("01", "Netrokona Sadar", "নেত্রকোণা সদর"), ("02", "Atpara", "আটপাড়া"), ("03", "Barhatta", "বারহাট্টা"), ("04", "Durgapur", "দুর্গাপুর"), ("05", "Khaliajuri", "খালিয়াজুরী"), ("06", "Kalmakanda", "কলমাকান্দা"), ("07", "Kendua", "কেন্দুয়া"), ("08", "Madan", "মদন"), ("09", "Mohanganj", "মোহনগঞ্জ"), ("10", "Purbadhala", "পূর্বধলা")],
    "DIST-89": [("01", "Sherpur Sadar", "শেরপুর সদর"), ("02", "Jhenaigati", "ঝিনাইগাতী"), ("03", "Nakla", "নকলা"), ("04", "Nalitabari", "নালিতাবাড়ী"), ("05", "Sreebardi", "শ্রীবরদী")],

    # Rajshahi Division
    "DIST-38": [("01", "Joypurhat Sadar", "জয়পুরহাট সদর"), ("02", "Akkelpur", "আক্কেলপুর"), ("03", "Kalai", "কালাই"), ("04", "Khetlal", "খেতলাল"), ("05", "Panchbibi", "পাঁচবিবি")],
    "DIST-64": [("01", "Naogaon Sadar", "নওগাঁ সদর"), ("02", "Atrai", "আত্রাই"), ("03", "Badalgachhi", "বদলগাছী"), ("04", "Dhamoirhat", "ধামইরহাট"), ("05", "Manda", "মান্দা"), ("06", "Mohadevpur", "মহাদেবপুর"), ("07", "Niamatpur", "নিয়ামতপুর"), ("08", "Patnitala", "পত্নীতলা"), ("09", "Porsha", "পোরশা"), ("10", "Raninagar", "রাণীনগর"), ("11", "Sapahar", "সাপাহার")],
    "DIST-69": [("01", "Natore Sadar", "নাটোর সদর"), ("02", "Bagatipara", "বাগাতিপাড়া"), ("03", "Baraigram", "বড়াইগ্রাম"), ("04", "Gurudaspur", "গুরুদাসপুর"), ("05", "Lalpur", "লালপুর"), ("06", "Singra", "সিংড়া"), ("07", "Naldanga", "নলডাঙ্গা")],
    "DIST-70": [("01", "Chapainawabganj Sadar", "চাঁপাইনবাবগঞ্জ সদর"), ("02", "Bholahat", "ভোলাহাট"), ("03", "Gomastapur", "গোমস্তাপুর"), ("04", "Nachole", "নাচোল"), ("05", "Shibganj", "শিবগঞ্জ")],
    "DIST-76": [("01", "Pabna Sadar", "পাবনা সদর"), ("02", "Atgharia", "আটঘরিয়া"), ("03", "Bera", "বেড়া"), ("04", "Bhangura", "ভাঙ্গুড়া"), ("05", "Chatmohar", "চাটমোহর"), ("06", "Faridpur", "ফরিদপুর"), ("07", "Ishwardi", "ঈশ্বরদী"), ("08", "Santhia", "সাঁথিয়া"), ("09", "Sujanagar", "সুজানগর")],
    "DIST-88": [("01", "Sirajganj Sadar", "সিরাজগঞ্জ সদর"), ("02", "Belkuchi", "বেলকুচি"), ("03", "Chauhali", "চৌহালী"), ("04", "Kamarkhanda", "কামারখন্দ"), ("05", "Kazipur", "কাজীপুর"), ("06", "Rayganj", "রায়গঞ্জ"), ("07", "Shahjadpur", "শাহজাদপুর"), ("08", "Tarash", "তাড়াশ"), ("09", "Ullahpara", "উল্লাপাড়া")],

    # Rangpur Division
    "DIST-27": [("01", "Dinajpur Sadar", "দিনাজপুর সদর"), ("02", "Birampur", "বিরামপুর"), ("03", "Birganj", "বীরগঞ্জ"), ("04", "Biral", "বিরল"), ("05", "Bochaganj", "বোচাগঞ্জ"), ("06", "Chirirbandar", "চিরিরবন্দর"), ("07", "Phulbari", "ফুলবাড়ী"), ("08", "Ghoraghat", "ঘোড়াঘাট"), ("09", "Hakimpur", "হাকিমপুর"), ("10", "Kaharole", "কাহারোল"), ("11", "Khansama", "খানসামা"), ("12", "Nawabganj", "নবাবগঞ্জ"), ("13", "Parbatipur", "পার্বতীপুর")],
    "DIST-32": [("01", "Gaibandha Sadar", "গাইবান্ধা সদর"), ("02", "Fulchhari", "ফুলছড়ি"), ("03", "Gobindaganj", "গোবিন্দগঞ্জ"), ("04", "Palashbari", "পলাশবাড়ী"), ("05", "Sadullapur", "সাদুল্যাপুর"), ("06", "Saghata", "সাঘাটা"), ("07", "Sundarganj", "সুন্দরগঞ্জ")],
    "DIST-49": [("01", "Kurigram Sadar", "কুড়িগ্রাম সদর"), ("02", "Bhurungamari", "ভুরুঙ্গামারী"), ("03", "Char Rajibpur", "চর রাজিবপুর"), ("04", "Chilmari", "চিলমারী"), ("05", "Phulbari", "ফুলবাড়ী"), ("06", "Nageshwari", "নাগেশ্বরী"), ("07", "Rajarhat", "রাজারহাট"), ("08", "Raomari", "রৌমারী"), ("09", "Ulipur", "উলিপুর")],
    "DIST-52": [("01", "Lalmonirhat Sadar", "লালমনিরহাট সদর"), ("02", "Aditmari", "আদিতমারী"), ("03", "Hatibandha", "হাতীবান্ধা"), ("04", "Kaliganj", "কালীগঞ্জ"), ("05", "Patgram", "পাটগ্রাম")],
    "DIST-73": [("01", "Nilphamari Sadar", "নীলফামারী সদর"), ("02", "Dimla", "ডিমলা"), ("03", "Domar", "ডোমার"), ("04", "Jaldhaka", "জলঢাকা"), ("05", "Kishoreganj", "কিশোরগঞ্জ"), ("06", "Saidpur", "সৈয়দপুর")],
    "DIST-77": [("01", "Panchagarh Sadar", "পঞ্চগড় সদর"), ("02", "Atwari", "আটোয়ারী"), ("03", "Boda", "বোদা"), ("04", "Debiganj", "দেবীগঞ্জ"), ("05", "Tetulia", "তেঁতুলিয়া")],
    "DIST-94": [("01", "Thakurgaon Sadar", "ঠাকুরগাঁও সদর"), ("02", "Baliadangi", "বালিয়াডাঙ্গী"), ("03", "Haripur", "হরিপুর"), ("04", "Pirganj", "পীরগঞ্জ"), ("05", "Ranisankhail", "রাণীশংকৈল")],

    # Sylhet Division
    "DIST-36": [("01", "Habiganj Sadar", "হবিগঞ্জ সদর"), ("02", "Ajmiriganj", "আজমিরীগঞ্জ"), ("03", "Bahubal", "বাহুবল"), ("04", "Baniachong", "বানিয়াচং"), ("05", "Chunarughat", "চুনারুঘাট"), ("06", "Lakhai", "লাখাই"), ("07", "Madhabpur", "মাধবপুর"), ("08", "Nabiganj", "নবীগঞ্জ"), ("09", "Shayestaganj", "শায়েস্তাগঞ্জ")],
    "DIST-58": [("01", "Moulvibazar Sadar", "মৌলভীবাজার সদর"), ("02", "Barlekha", "বড়লেখা"), ("03", "Kamalganj", "কমলগঞ্জ"), ("04", "Kulaura", "কুলাউড়া"), ("05", "Rajnagar", "রাজনগর"), ("06", "Sreemangal", "শ্রীমঙ্গল"), ("07", "Juri", "জুড়ী")],
    "DIST-90": [("01", "Sunamganj Sadar", "সুনামগঞ্জ সদর"), ("02", "Bishwamvarpur", "বিশ্বম্ভরপুর"), ("03", "Chhatak", "ছাতক"), ("04", "Derai", "দিরাই"), ("05", "Dharampasha", "ধর্মপাশা"), ("06", "Dowarabazar", "দোয়ারাবাজার"), ("07", "Jagannathpur", "জগন্নাথপুর"), ("08", "Jamalganj", "জামালগঞ্জ"), ("09", "Shantiganj (South Sunamganj)", "শান্তিগঞ্জ"), ("10", "Sullah", "শাল্লা"), ("11", "Tahirpur", "তাহিরপুর"), ("12", "Madhyanagar", "মধ্যনগর")]
}

# 4. Unions (detailed for pilot areas)
UNIONS = [
    # Savar (UPZ-2672)
    {"union_id": "UNI-SAV-01", "upazila_id": "UPZ-2672", "bbs_code": "01", "name_en": "Aminbazar", "name_bn": "আমিনবাজার"},
    {"union_id": "UNI-SAV-02", "upazila_id": "UPZ-2672", "bbs_code": "02", "name_en": "Birulia", "name_bn": "বিরুলিয়া"},
    {"union_id": "UNI-SAV-03", "upazila_id": "UPZ-2672", "bbs_code": "03", "name_en": "Kaundia", "name_bn": "কাউন্দিয়া"},
    {"union_id": "UNI-SAV-04", "upazila_id": "UPZ-2672", "bbs_code": "04", "name_en": "Tetuljhora", "name_bn": "তেঁতুলঝোড়া"},
    {"union_id": "UNI-SAV-05", "upazila_id": "UPZ-2672", "bbs_code": "05", "name_en": "Ashulia", "name_bn": "আশুলিয়া"},
    {"union_id": "UNI-SAV-06", "upazila_id": "UPZ-2672", "bbs_code": "06", "name_en": "Bhakurta", "name_bn": "ভাকুর্তা"},
    {"union_id": "UNI-SAV-07", "upazila_id": "UPZ-2672", "bbs_code": "07", "name_en": "Pathalia", "name_bn": "পাথালিয়া"},
    {"union_id": "UNI-SAV-08", "upazila_id": "UPZ-2672", "bbs_code": "08", "name_en": "Shimulia", "name_bn": "শিমুলিয়া"},
    {"union_id": "UNI-SAV-09", "upazila_id": "UPZ-2672", "bbs_code": "09", "name_en": "Yarpur", "name_bn": "ইয়ারপুর"},
    {"union_id": "UNI-SAV-10", "upazila_id": "UPZ-2672", "bbs_code": "10", "name_en": "Dhamsona", "name_bn": "ধামসোনা"},
    {"union_id": "UNI-SAV-11", "upazila_id": "UPZ-2672", "bbs_code": "11", "name_en": "Savar Pourashava", "name_bn": "সাভার পৌরসভা"},

    # Dhamrai (UPZ-2614)
    {"union_id": "UNI-DHA-01", "upazila_id": "UPZ-2614", "bbs_code": "01", "name_en": "Amta", "name_bn": "আমতা"},
    {"union_id": "UNI-DHA-02", "upazila_id": "UPZ-2614", "bbs_code": "02", "name_en": "Baisakhali", "name_bn": "বাইশাকান্দা"},
    {"union_id": "UNI-DHA-03", "upazila_id": "UPZ-2614", "bbs_code": "03", "name_en": "Dhamrai Sadar", "name_bn": "ধামরাই সদর"},

    # Keraniganj (UPZ-2638)
    {"union_id": "UNI-KER-01", "upazila_id": "UPZ-2638", "bbs_code": "01", "name_en": "Aganagar", "name_bn": "আগানগর"},
    {"union_id": "UNI-KER-02", "upazila_id": "UPZ-2638", "bbs_code": "02", "name_en": "Kalatia", "name_bn": "কলাতিয়া"},
    {"union_id": "UNI-KER-03", "upazila_id": "UPZ-2638", "bbs_code": "03", "name_en": "Ruhitpur", "name_bn": "রোহিতপুর"},

    # Gazipur Sadar (UPZ-3330)
    {"union_id": "UNI-GAZ-01", "upazila_id": "UPZ-3330", "bbs_code": "01", "name_en": "Baria", "name_bn": "বাড়িয়া"},
    {"union_id": "UNI-GAZ-02", "upazila_id": "UPZ-3330", "bbs_code": "02", "name_en": "Basan", "name_bn": "বাসন"},
    {"union_id": "UNI-GAZ-03", "upazila_id": "UPZ-3330", "bbs_code": "03", "name_en": "Mirzapur (Gazipur)", "name_bn": "মির্জাপুর"},

    # Patiya (UPZ-1561)
    {"union_id": "UNI-PAT-01", "upazila_id": "UPZ-1561", "bbs_code": "01", "name_en": "Kachuai", "name_bn": "কচুয়াই"},
    {"union_id": "UNI-PAT-02", "upazila_id": "UPZ-1561", "bbs_code": "02", "name_en": "Haidgaon", "name_bn": "হাইদগাঁও"},

    # Sylhet Sadar (UPZ-9162)
    {"union_id": "UNI-SYL-01", "upazila_id": "UPZ-9162", "bbs_code": "01", "name_en": "Jalalabad", "name_bn": "জালালাবাদ"},
    {"union_id": "UNI-SYL-02", "upazila_id": "UPZ-9162", "bbs_code": "02", "name_en": "Hatkhola", "name_bn": "হাটখোলা"}
]

# 5. Mouzas with JL numbers (Grounded in current parcels & regional cadastral sheets)
MOUZAS = [
    # Savar Mouzas (Current 100,000 parcels reside in Aminbazar JL 12 and Birulia JL 24)
    {"mouza_id": "MOUZA-SAVAR-AMINBAZAR", "upazila_id": "UPZ-2672", "union_id": "UNI-SAV-01", "name_en": "Aminbazar", "name_bn": "আমিনবাজার", "jl_number": "12", "has_survey": 1, "has_poly": 1},
    {"mouza_id": "MOUZA-SAVAR-BIRULIA", "upazila_id": "UPZ-2672", "union_id": "UNI-SAV-02", "name_en": "Birulia", "name_bn": "বিরুলিয়া", "jl_number": "24", "has_survey": 1, "has_poly": 1},
    {"mouza_id": "MOUZA-SAVAR-KAUNDIA", "upazila_id": "UPZ-2672", "union_id": "UNI-SAV-03", "name_en": "Kaundia", "name_bn": "কাউন্দিয়া", "jl_number": "15", "has_survey": 1, "has_poly": 0},
    {"mouza_id": "MOUZA-SAVAR-TETULJHORA", "upazila_id": "UPZ-2672", "union_id": "UNI-SAV-04", "name_en": "Tetuljhora", "name_bn": "তেঁতুলঝোড়া", "jl_number": "18", "has_survey": 1, "has_poly": 0},
    {"mouza_id": "MOUZA-SAVAR-ASHULIA", "upazila_id": "UPZ-2672", "union_id": "UNI-SAV-05", "name_en": "Ashulia", "name_bn": "আশুলিয়া", "jl_number": "05", "has_survey": 1, "has_poly": 0},
    {"mouza_id": "MOUZA-SAVAR-BHAKURTA", "upazila_id": "UPZ-2672", "union_id": "UNI-SAV-06", "name_en": "Bhakurta", "name_bn": "ভাকুর্তা", "jl_number": "28", "has_survey": 1, "has_poly": 0},

    # Dhamrai Mouzas
    {"mouza_id": "MOUZA-DHA-DHAMRAI", "upazila_id": "UPZ-2614", "union_id": "UNI-DHA-03", "name_en": "Dhamrai", "name_bn": "ধামরাই", "jl_number": "08", "has_survey": 1, "has_poly": 0},
    {"mouza_id": "MOUZA-DHA-BAISAKANDA", "upazila_id": "UPZ-2614", "union_id": "UNI-DHA-02", "name_en": "Baisakanda", "name_bn": "বাইশাকান্দা", "jl_number": "14", "has_survey": 0, "has_poly": 0},

    # Gazipur Sadar Mouzas
    {"mouza_id": "MOUZA-GAZ-JOYDEBPUR", "upazila_id": "UPZ-3330", "union_id": "UNI-GAZ-02", "name_en": "Joydebpur", "name_bn": "জয়দেবপুর", "jl_number": "35", "has_survey": 1, "has_poly": 0},
    {"mouza_id": "MOUZA-GAZ-CHOWRASTA", "upazila_id": "UPZ-3330", "union_id": "UNI-GAZ-02", "name_en": "Chowrasta", "name_bn": "চৌরাস্তা", "jl_number": "41", "has_survey": 1, "has_poly": 0},

    # Patiya Mouzas
    {"mouza_id": "MOUZA-PAT-PATIYA", "upazila_id": "UPZ-1561", "union_id": "UNI-PAT-01", "name_en": "Patiya", "name_bn": "পটিয়া", "jl_number": "52", "has_survey": 1, "has_poly": 0},

    # Sylhet Sadar Mouzas
    {"mouza_id": "MOUZA-SYL-AMBERKHANA", "upazila_id": "UPZ-9162", "union_id": "UNI-SYL-01", "name_en": "Amberkhana", "name_bn": "আম্বরখানা", "jl_number": "02", "has_survey": 1, "has_poly": 0},
    {"mouza_id": "MOUZA-SYL-ZINDABAZAR", "upazila_id": "UPZ-9162", "union_id": "UNI-SYL-01", "name_en": "Zindabazar", "name_bn": "জিন্দাবাজার", "jl_number": "03", "has_survey": 1, "has_poly": 0},

    # Duplicate mouza name demonstration (Mirzapur exists in multiple districts)
    {"mouza_id": "MOUZA-GAZ-MIRZAPUR", "upazila_id": "UPZ-3330", "union_id": "UNI-GAZ-03", "name_en": "Mirzapur", "name_bn": "মির্জাপুর", "jl_number": "60", "has_survey": 1, "has_poly": 0},
    {"mouza_id": "MOUZA-TAN-MIRZAPUR", "upazila_id": "UPZ-9376", "union_id": None, "name_en": "Mirzapur", "name_bn": "মির্জাপুর", "jl_number": "01", "has_survey": 1, "has_poly": 0}
]

def seed_geography():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS geo_divisions (
        division_id TEXT PRIMARY KEY,
        bbs_code TEXT UNIQUE NOT NULL,
        name_en TEXT NOT NULL,
        name_bn TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        source_ref TEXT DEFAULT 'BBS_GEOCODE_2024'
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS geo_districts (
        district_id TEXT PRIMARY KEY,
        division_id TEXT NOT NULL,
        bbs_code TEXT UNIQUE NOT NULL,
        name_en TEXT NOT NULL,
        name_bn TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        source_ref TEXT DEFAULT 'BBS_GEOCODE_2024',
        FOREIGN KEY(division_id) REFERENCES geo_divisions(division_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS geo_upazilas (
        upazila_id TEXT PRIMARY KEY,
        district_id TEXT NOT NULL,
        bbs_code TEXT,
        name_en TEXT NOT NULL,
        name_bn TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        source_ref TEXT DEFAULT 'BBS_GEOCODE_2024',
        FOREIGN KEY(district_id) REFERENCES geo_districts(district_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS geo_unions (
        union_id TEXT PRIMARY KEY,
        upazila_id TEXT NOT NULL,
        bbs_code TEXT,
        name_en TEXT NOT NULL,
        name_bn TEXT NOT NULL,
        source_ref TEXT DEFAULT 'BBS_GEOCODE_2024',
        FOREIGN KEY(upazila_id) REFERENCES geo_upazilas(upazila_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS geo_mouzas (
        mouza_id TEXT PRIMARY KEY,
        upazila_id TEXT NOT NULL,
        union_id TEXT,
        name_en TEXT NOT NULL,
        name_bn TEXT NOT NULL,
        jl_number TEXT,
        has_cadastral_survey INTEGER DEFAULT 0,
        has_boundary_polygon INTEGER DEFAULT 0,
        source_ref TEXT DEFAULT 'DLRS_CADASTRAL_INDEX',
        FOREIGN KEY(upazila_id) REFERENCES geo_upazilas(upazila_id),
        FOREIGN KEY(union_id) REFERENCES geo_unions(union_id)
    );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_geo_districts_div ON geo_districts(division_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_geo_upazilas_dist ON geo_upazilas(district_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_geo_unions_upz ON geo_unions(upazila_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_geo_mouzas_upz ON geo_mouzas(upazila_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_geo_mouzas_union ON geo_mouzas(union_id);")

    # Insert Divisions
    print(f"Seeding {len(DIVISIONS)} divisions...")
    for d in DIVISIONS:
        cur.execute("""
        INSERT OR REPLACE INTO geo_divisions (division_id, bbs_code, name_en, name_bn, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (d["division_id"], d["bbs_code"], d["name_en"], d["name_bn"], d["lat"], d["lon"]))

    # Insert Districts
    print(f"Seeding {len(DISTRICTS)} districts...")
    for dist in DISTRICTS:
        cur.execute("""
        INSERT OR REPLACE INTO geo_districts (district_id, division_id, bbs_code, name_en, name_bn, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (dist["district_id"], dist["division_id"], dist["bbs_code"], dist["name_en"], dist["name_bn"], dist["lat"], dist["lon"]))

    # Insert Upazilas
    total_upazilas = 0
    # First detailed upazilas
    for dist_id, upz_list in UPAZILA_DATA.items():
        for bbs_suf, name_en, name_bn, u_lat, u_lon in upz_list:
            upz_id = f"UPZ-{dist_id.split('-')[-1]}{bbs_suf}"
            cur.execute("""
            INSERT OR REPLACE INTO geo_upazilas (upazila_id, district_id, bbs_code, name_en, name_bn, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (upz_id, dist_id, bbs_suf, name_en, name_bn, u_lat, u_lon))
            total_upazilas += 1

    # Second generic upazilas for remaining districts
    for dist_id, upz_list in DEFAULT_DISTRICT_UPAZILAS.items():
        dist_meta = next((d for d in DISTRICTS if d["district_id"] == dist_id), None)
        base_lat = dist_meta["lat"] if dist_meta else 23.8
        base_lon = dist_meta["lon"] if dist_meta else 90.4
        for idx, (bbs_suf, name_en, name_bn) in enumerate(upz_list):
            upz_id = f"UPZ-{dist_id.split('-')[-1]}{bbs_suf}"
            # slightly jitter coordinate for map visualization
            u_lat = base_lat + (idx * 0.04) - 0.08
            u_lon = base_lon + (idx * 0.04) - 0.08
            cur.execute("""
            INSERT OR REPLACE INTO geo_upazilas (upazila_id, district_id, bbs_code, name_en, name_bn, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (upz_id, dist_id, bbs_suf, name_en, name_bn, u_lat, u_lon))
            total_upazilas += 1

    print(f"Seeded {total_upazilas} upazilas across all 64 districts!")

    # Insert Unions
    print(f"Seeding {len(UNIONS)} sample unions...")
    for u in UNIONS:
        cur.execute("""
        INSERT OR REPLACE INTO geo_unions (union_id, upazila_id, bbs_code, name_en, name_bn)
        VALUES (?, ?, ?, ?, ?)
        """, (u["union_id"], u["upazila_id"], u["bbs_code"], u["name_en"], u["name_bn"]))

    # Insert Mouzas
    print(f"Seeding {len(MOUZAS)} mouzas...")
    for m in MOUZAS:
        cur.execute("""
        INSERT OR REPLACE INTO geo_mouzas (mouza_id, upazila_id, union_id, name_en, name_bn, jl_number, has_cadastral_survey, has_boundary_polygon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (m["mouza_id"], m["upazila_id"], m["union_id"], m["name_en"], m["name_bn"], m["jl_number"], m["has_survey"], m["has_poly"]))

    conn.commit()
    conn.close()
    print("Administrative geography database seeding completed successfully!")

if __name__ == "__main__":
    seed_geography()
