"""
DESHMRITTIKA / BHUMI-SYNC — Backend Configuration
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database selection: full-scale if available, fallback to dry-run
FULL_SCALE_DB = BASE_DIR / "data" / "generated" / "full_scale" / "landtech_synthetic.db"
DRY_RUN_DB = BASE_DIR / "data" / "generated" / "dry_run" / "landtech_synthetic_dry_run.db"

if FULL_SCALE_DB.exists():
    DEFAULT_DB_PATH = str(FULL_SCALE_DB)
elif DRY_RUN_DB.exists():
    DEFAULT_DB_PATH = str(DRY_RUN_DB)
else:
    DEFAULT_DB_PATH = str(FULL_SCALE_DB)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
DATABASE_PATH = os.getenv("DATABASE_PATH", DEFAULT_DB_PATH)

DOCUMENTS_DIR = BASE_DIR / "data" / "generated" / "full_scale" / "documents"
if not DOCUMENTS_DIR.exists():
    DOCUMENTS_DIR = BASE_DIR / "data" / "generated" / "dry_run" / "documents"

SECRET_KEY = os.getenv("SECRET_KEY", "deshmrittika-smart-landtech-secret-token-2026")
ALGORITHM = "HS256"

# Demo User Accounts (Strictly Fictional Credentials)
DEMO_USERS = {
    "citizen@example.com": {
        "user_id": "USR-CITIZEN-01",
        "name": "মো: রফিকুল ইসলাম (Citizen)",
        "role": "CITIZEN",
        "password_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # empty / mock demo hash
    },
    "buyer@example.com": {
        "user_id": "USR-BUYER-01",
        "name": "তানভীর আহমেদ (Prospective Buyer)",
        "role": "BUYER",
        "password_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "officer@savar.land.gov.bd": {
        "user_id": "OFFICER-SAVAR-01",
        "name": "সহকারী কমিশনার (ভূমি), সাভার",
        "role": "OFFICER",
        "password_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "admin@deshmrittika.gov.bd": {
        "user_id": "USR-ADMIN-01",
        "name": "System Administrator",
        "role": "ADMINISTRATOR",
        "password_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
}
