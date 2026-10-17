"""
DESHMRITTIKA / BHUMI-SYNC — Database Access Layer
Fast, read-optimized SQLite connection pool with dictionary rows and auth schema bootstrap.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Generator
from backend.app.config import DATABASE_PATH
from backend.app.services.crypto import CryptoService

def init_auth_tables(conn: sqlite3.Connection):
    """Ensures authentication, verification, session, and audit tables exist and seeds demo accounts."""
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT DEFAULT '',
        role TEXT NOT NULL DEFAULT 'CITIZEN',
        status TEXT NOT NULL DEFAULT 'UNVERIFIED',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS auth_challenges (
        challenge_id TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        user_id TEXT,
        purpose TEXT NOT NULL,
        code_hash TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        attempts INTEGER DEFAULT 0,
        max_attempts INTEGER DEFAULT 5,
        resend_available_at TEXT NOT NULL,
        used_at TEXT,
        created_at TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        token_hash TEXT UNIQUE NOT NULL,
        ip_address TEXT DEFAULT '',
        user_agent TEXT DEFAULT '',
        expires_at TEXT NOT NULL,
        is_revoked INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS security_audit_logs (
        log_id TEXT PRIMARY KEY,
        user_id TEXT,
        actor_email TEXT NOT NULL,
        action TEXT NOT NULL,
        ip_address TEXT DEFAULT '',
        details_json TEXT DEFAULT '{}',
        timestamp TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS citizen_parcels (
        link_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        parcel_id TEXT NOT NULL,
        ownership_type TEXT DEFAULT 'INHERITED_AND_MUTATED',
        share_percent REAL DEFAULT 100.0,
        khatian_no TEXT DEFAULT 'RS-1048',
        tax_status TEXT DEFAULT 'PAID_CURRENT_YEAR',
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS citizen_applications (
        app_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        parcel_id TEXT NOT NULL,
        app_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'SUBMITTED',
        details_json TEXT DEFAULT '{}',
        hearing_date TEXT,
        officer_notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS citizen_notifications (
        notif_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        notif_type TEXT NOT NULL DEFAULT 'INFO',
        is_read INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS buyer_review_requests (
        request_id TEXT PRIMARY KEY,
        buyer_id TEXT NOT NULL,
        parcel_id TEXT NOT NULL,
        reason TEXT NOT NULL,
        urgency TEXT DEFAULT 'NORMAL',
        status TEXT DEFAULT 'PENDING_OFFICER_REVIEW',
        ac_land_response TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(buyer_id) REFERENCES users(user_id)
    )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_challenges_email ON auth_challenges(email, purpose);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(token_hash);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_security_logs_email ON security_audit_logs(actor_email);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_citizen_parcels_user ON citizen_parcels(user_id);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_citizen_apps_user ON citizen_applications(user_id);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_citizen_notifs_user ON citizen_notifications(user_id);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_buyer_requests_buyer ON buyer_review_requests(buyer_id);")

    # Seed 4 Standard Role Accounts with default password 'Password123!'
    now_ts = datetime.now(timezone.utc).isoformat()
    default_pwd_hash = CryptoService.hash_password("Password123!")

    seed_users = [
        ("USR-CITIZEN-01", "citizen@example.com", default_pwd_hash, "মো: রফিকুল ইসলাম (নাগরিক)", "01711000001", "CITIZEN", "ACTIVE"),
        ("USR-BUYER-01", "buyer@example.com", default_pwd_hash, "তানভীর আহমেদ (ক্রেতা)", "01811000002", "BUYER", "ACTIVE"),
        ("OFFICER-SAVAR-01", "officer@savar.land.gov.bd", default_pwd_hash, "সহকারী কমিশনার (ভূমি), সাভার", "01911000003", "OFFICER", "ACTIVE"),
        ("USR-ADMIN-01", "admin@deshmrittika.gov.bd", default_pwd_hash, "সিস্টেম অ্যাডমিনিস্ট্রেটর", "01511000004", "ADMINISTRATOR", "ACTIVE"),
    ]

    for uid, email, phash, name, phone, role, status in seed_users:
        c.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        if not c.fetchone():
            c.execute("""
            INSERT INTO users (user_id, email, password_hash, full_name, phone, role, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (uid, email, phash, name, phone, role, status, now_ts, now_ts))

    # Seed explicit linked parcels for USR-CITIZEN-01
    c.execute("SELECT 1 FROM citizen_parcels WHERE user_id = 'USR-CITIZEN-01'")
    if not c.fetchone():
        c.execute("""
        INSERT INTO citizen_parcels (link_id, user_id, parcel_id, ownership_type, share_percent, khatian_no, tax_status, created_at)
        VALUES 
        ('CP-001', 'USR-CITIZEN-01', 'BD-PAR-000001', 'উত্তরাধিকার ও নামজারি সূত্রে', 100.0, 'আরএস-১০৪৮', 'পরিশোধিত (১৪৩১ বঙ্গাব্দ)', ?),
        ('CP-002', 'USR-CITIZEN-01', 'BD-PAR-000002', 'সাফ-কবালা ক্রয় সূত্রে', 100.0, 'বিএস-৫১২', 'পরিশোধিত (১৪৩১ বঙ্গাব্দ)', ?)
        """, (now_ts, now_ts))

    # Seed initial applications for USR-CITIZEN-01
    c.execute("SELECT 1 FROM citizen_applications WHERE user_id = 'USR-CITIZEN-01'")
    if not c.fetchone():
        c.execute("""
        INSERT INTO citizen_applications (app_id, user_id, parcel_id, app_type, status, details_json, hearing_date, officer_notes, created_at, updated_at)
        VALUES 
        ('APP-MUT-2026-001', 'USR-CITIZEN-01', 'BD-PAR-000001', 'ই-নামজারি ও জমাভাগ', 'ULAO_INSPECTION', '{"mouza":"Aminbazar","dag_number":101,"khatian":"RS-1048","proposed_area_dec":20.51}', '২০২৬-১১-০৫', 'তহশিলদার সরেজমিন তদন্ত চলমান। বায়া দলিল যাচাই সম্পন্ন হয়েছে।', ?, ?),
        ('APP-CORR-2026-002', 'USR-CITIZEN-01', 'BD-PAR-000002', 'রেকর্ডীয় করণিক ভুল সংশোধন', 'SUBMITTED', '{"mouza":"Aminbazar","dag_number":102,"correction_field":"পিতার নাম করণিক সংশোধন"}', NULL, 'আবেদন পর্যালোচনার অপেক্ষায়।', ?, ?)
        """, (now_ts, now_ts, now_ts, now_ts))

    # Seed notifications for USR-CITIZEN-01
    c.execute("SELECT 1 FROM citizen_notifications WHERE user_id = 'USR-CITIZEN-01'")
    if not c.fetchone():
        c.execute("""
        INSERT INTO citizen_notifications (notif_id, user_id, title, message, notif_type, is_read, created_at)
        VALUES 
        ('NOTIF-001', 'USR-CITIZEN-01', 'নামজারি আবেদন গ্রহণ', 'আপনার ই-নামজারি আবেদন APP-MUT-2026-001 সফলভাবে সাভার উপজেলা ভূমি অফিসে গৃহীত হয়েছে।', 'APPLICATION', 1, ?),
        ('NOTIF-002', 'USR-CITIZEN-01', 'ভূমি উন্নয়ন কর হালনাগাদ', 'আমিনবাজার মৌজার ১০১ দাগের ১৪৩১ বঙ্গাব্দের ভূমি উন্নয়ন কর সফলভাবে পরিশোধিত হয়েছে।', 'TAX', 0, ?),
        ('NOTIF-003', 'USR-CITIZEN-01', 'শুনানির নোটিশ', 'আবেদন নং APP-MUT-2026-001 এর শুনানি আগামী ০৫ নভেম্বর ২০২৬ তারিখে সহকারী কমিশনার (ভূমি) কার্যালয়ে অনুষ্ঠিত হবে।', 'HEARING', 0, ?)
        """, (now_ts, now_ts, now_ts))

    conn.commit()


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with dict-like row access and verified auth tables."""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI Dependency yielding database connection."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
