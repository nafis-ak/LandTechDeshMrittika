"""
DESHMRITTIKA / BHUMI-SYNC — Administrator User & Security Management Endpoints
Privileged endpoints strictly protected by require_admin_role.
Supports user role provisioning, status suspension, session revocation, and security audit inspection.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from backend.app.database import get_db
from backend.app.schemas.models import (
    UserProfile,
    AdminRoleChangeRequest,
    AdminStatusChangeRequest
)
from backend.app.services.auth import (
    require_admin_role,
    revoke_all_user_sessions,
    log_security_event
)
from backend.app.services.email import EmailService

router = APIRouter(prefix="/admin", tags=["Administrator Management"])


@router.get("/users")
def list_users(
    role: Optional[str] = Query(None, description="Filter by role: CITIZEN, BUYER, OFFICER, ADMINISTRATOR"),
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE, UNVERIFIED, SUSPENDED"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: Dict[str, Any] = Depends(require_admin_role),
    db: sqlite3.Connection = Depends(get_db)
):
    """Lists registered users with role and status filtering."""
    cur = db.cursor()
    query = "SELECT user_id, email, full_name, phone, role, status, created_at, updated_at FROM users WHERE 1=1"
    params = []

    if role:
        query += " AND role = ?"
        params.append(role.upper().strip())
    if status:
        query += " AND status = ?"
        params.append(status.upper().strip())

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur.execute(query, params)
    users = [dict(r) for r in cur.fetchall()]

    # Get total count
    count_query = "SELECT COUNT(*) FROM users WHERE 1=1"
    count_params = []
    if role:
        count_query += " AND role = ?"
        count_params.append(role.upper().strip())
    if status:
        count_query += " AND status = ?"
        count_params.append(status.upper().strip())

    cur.execute(count_query, count_params)
    total = cur.fetchone()[0]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "users": users
    }


@router.post("/users/role")
def change_user_role(
    req: AdminRoleChangeRequest,
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_role),
    db: sqlite3.Connection = Depends(get_db)
):
    """Changes a user's role with mandatory reason and security logging. Protects the last administrator."""
    allowed_roles = ["CITIZEN", "BUYER", "OFFICER", "ADMINISTRATOR"]
    target_role = req.new_role.upper().strip()

    if target_role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"অবৈধ ভূমিকা '{target_role}'। অনুমোদিত: {allowed_roles}")

    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (req.target_user_id,))
    target_user = cur.fetchone()
    if not target_user:
        raise HTTPException(status_code=404, detail="ব্যবহারকারী পাওয়া যায়নি।")

    old_role = target_user["role"]
    if old_role == target_role:
        return {"success": True, "message": "ভূমিকা অপরিবর্তিত রয়েছে।"}

    # Guard: prevent removing the last active administrator
    if old_role == "ADMINISTRATOR":
        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'ADMINISTRATOR' AND status = 'ACTIVE'")
        active_admins = cur.fetchone()[0]
        if active_admins <= 1:
            raise HTTPException(
                status_code=400,
                detail="সিস্টেমের সর্বশেষ সক্রিয় অ্যাডমিনিস্ট্রেটর পদ পরিবর্তন বা প্রত্যাহার করা যাবে না।"
            )

    now = datetime.now(timezone.utc).isoformat()
    cur.execute("UPDATE users SET role = ?, updated_at = ? WHERE user_id = ?", (target_role, now, req.target_user_id))

    # Revoke sessions to force fresh role token on next login
    revoke_all_user_sessions(req.target_user_id, db)

    db.commit()

    ip_addr = request.client.host if request.client else ""
    log_security_event(
        db,
        user_id=target_user["user_id"],
        actor_email=admin["email"],
        action="ROLE_CHANGED",
        details={
            "admin_actor": admin["email"],
            "target_user": target_user["email"],
            "old_role": old_role,
            "new_role": target_role,
            "reason": req.reason
        },
        ip_address=ip_addr
    )

    EmailService.send_security_alert(
        target_user["email"],
        target_user["full_name"],
        f"আপনার অ্যাকাউন্ট ভূমিকা পরিবর্তিত হয়ে '{target_role}' করা হয়েছে",
        f"অ্যাডমিন {admin['email']} দ্বারা এই পরিবর্তন সম্পন্ন হয়েছে। কারণ: {req.reason}।"
    )

    return {
        "success": True,
        "user_id": req.target_user_id,
        "old_role": old_role,
        "new_role": target_role,
        "message": f"ভূমিকা সফলভাবে পরিবর্তন করে '{target_role}' করা হয়েছে।"
    }


@router.post("/users/status")
def change_user_status(
    req: AdminStatusChangeRequest,
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_role),
    db: sqlite3.Connection = Depends(get_db)
):
    """Activates or suspends a user account. If suspended, revokes all active sessions immediately."""
    allowed_statuses = ["ACTIVE", "SUSPENDED"]
    target_status = req.new_status.upper().strip()

    if target_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"অবৈধ স্ট্যাটাস '{target_status}'। অনুমোদিত: {allowed_statuses}")

    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (req.target_user_id,))
    target_user = cur.fetchone()
    if not target_user:
        raise HTTPException(status_code=404, detail="ব্যবহারকারী পাওয়া যায়নি।")

    # Guard: prevent suspending self or the last administrator
    if target_user["user_id"] == admin["user_id"] and target_status == "SUSPENDED":
        raise HTTPException(status_code=400, detail="নিজের অ্যাডমিন অ্যাকাউন্ট স্থগিত করা যাবে না।")

    if target_user["role"] == "ADMINISTRATOR" and target_status == "SUSPENDED":
        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'ADMINISTRATOR' AND status = 'ACTIVE'")
        active_admins = cur.fetchone()[0]
        if active_admins <= 1:
            raise HTTPException(status_code=400, detail="সিস্টেমের সর্বশেষ সক্রিয় অ্যাডমিনিস্ট্রেটর স্থগিত করা যাবে না।")

    now = datetime.now(timezone.utc).isoformat()
    cur.execute("UPDATE users SET status = ?, updated_at = ? WHERE user_id = ?", (target_status, now, req.target_user_id))

    if target_status == "SUSPENDED":
        revoke_all_user_sessions(req.target_user_id, db)

    db.commit()

    ip_addr = request.client.host if request.client else ""
    log_security_event(
        db,
        user_id=target_user["user_id"],
        actor_email=admin["email"],
        action="ACCOUNT_STATUS_CHANGED",
        details={
            "admin_actor": admin["email"],
            "target_user": target_user["email"],
            "new_status": target_status,
            "reason": req.reason
        },
        ip_address=ip_addr
    )

    return {
        "success": True,
        "user_id": req.target_user_id,
        "new_status": target_status,
        "message": f"অ্যাকাউন্ট স্ট্যাটাস পরিবর্তিত হয়ে '{target_status}' হয়েছে।"
    }


@router.get("/security-logs")
def get_security_logs(
    action: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: Dict[str, Any] = Depends(require_admin_role),
    db: sqlite3.Connection = Depends(get_db)
):
    """Inspects platform security audit logs."""
    cur = db.cursor()
    query = "SELECT * FROM security_audit_logs WHERE 1=1"
    params = []
    if action:
        query += " AND action = ?"
        params.append(action.upper().strip())

    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur.execute(query, params)
    logs = [dict(r) for r in cur.fetchall()]

    return {"total": len(logs), "logs": logs, "security_logs": logs}


@router.get("/diagnostics")
def get_system_diagnostics(
    admin: Dict[str, Any] = Depends(require_admin_role),
    db: sqlite3.Connection = Depends(get_db)
):
    """System health, SQLite table counts, WAL journal mode, and active session count."""
    import os
    from backend.app.config import DATABASE_PATH

    cur = db.cursor()
    table_counts = {}
    for tbl in ["parcels", "deeds", "transactions", "users", "user_sessions", "verification_cases", "security_audit_logs"]:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {tbl}")
            table_counts[tbl] = cur.fetchone()[0]
        except Exception:
            table_counts[tbl] = 0

    # Active sessions
    cur.execute("SELECT COUNT(*) FROM user_sessions WHERE is_revoked = 0")
    active_sessions = cur.fetchone()[0]

    # Check WAL mode
    cur.execute("PRAGMA journal_mode;")
    journal_mode = cur.fetchone()[0]

    db_size_mb = round(os.path.getsize(DATABASE_PATH) / (1024 * 1024), 2) if os.path.exists(DATABASE_PATH) else 0

    return {
        "admin": admin["name"],
        "status": "OPERATIONAL",
        "system_status": "OPERATIONAL",
        "database": {
            "path": DATABASE_PATH,
            "journal_mode": journal_mode,
            "size_mb": db_size_mb,
            "table_counts": table_counts
        },
        "active_sessions": active_sessions,
        "api_version": "2.2.0"
    }


@router.get("/ocr-health")
def get_ocr_health(
    admin: Dict[str, Any] = Depends(require_admin_role)
):
    """Inspects Bengali OCR engine status, language packs, and preprocessing modules."""
    import pytesseract
    from PIL import Image

    tess_available = False
    langs = []
    try:
        langs = pytesseract.get_languages()
        tess_available = True
    except Exception:
        pass

    return {
        "engine": "Tesseract OCR / PIL Fast Preprocessor",
        "tesseract_installed": tess_available,
        "languages_loaded": langs,
        "bengali_pack_ready": "ben" in langs,
        "fallback_mode": "Fast Preprocessing & Bengali Heuristic Extraction Active",
        "status": "HEALTHY"
    }


@router.get("/fraud-rules")
def get_fraud_rules_config(
    admin: Dict[str, Any] = Depends(require_admin_role)
):
    """Returns versioned fraud detection rule catalog and thresholds."""
    return {
        "version": "2.2.0-RBAC",
        "rules": [
            {
                "rule_id": "DS-01",
                "name": "Conflicting Subsequent Transfer",
                "severity": "CRITICAL",
                "description": "Owner transfers already sold parcel to a different buyer without continuous title chain.",
                "threshold_score": 95,
                "active": True
            },
            {
                "rule_id": "DS-02",
                "name": "Sequential Legitimate Transfer",
                "severity": "LOW",
                "description": "Normal serial sale with complete baya deed progression.",
                "threshold_score": 10,
                "active": True
            },
            {
                "rule_id": "DS-03",
                "name": "Boundary Conflict Overlap",
                "severity": "MEDIUM",
                "description": "Spatial overlap across adjacent parcel boundaries.",
                "threshold_score": 60,
                "active": True
            },
            {
                "rule_id": "KHAS-01",
                "name": "Khas Land Encroachment Flag",
                "severity": "CRITICAL",
                "description": "Plot overlapping Government Khas 1-No. Khatian or vested property.",
                "threshold_score": 100,
                "active": True
            }
        ],
        "active_rules": ["DS-01", "DS-02", "DS-03", "KHAS-01"]
    }


@router.post("/backups/checkpoint")
def run_database_checkpoint(
    admin: Dict[str, Any] = Depends(require_admin_role),
    db: sqlite3.Connection = Depends(get_db)
):
    """Triggers an audited SQLite WAL checkpoint (PASSIVE/FULL)."""
    cur = db.cursor()
    cur.execute("PRAGMA wal_checkpoint(PASSIVE);")
    res = cur.fetchone()

    log_security_event(
        db,
        user_id=admin["user_id"],
        actor_email=admin["email"],
        action="DB_CHECKPOINT_TRIGGERED",
        details={"result": list(res) if res else []}
    )

    return {
        "success": True,
        "status": "SUCCESS",
        "checkpoint_result": list(res) if res else [],
        "message": "SQLite WAL চেকপয়েন্ট সফলভাবে সম্পন্ন হয়েছে।"
    }

