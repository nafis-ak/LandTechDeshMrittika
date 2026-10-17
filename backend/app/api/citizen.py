"""
DESHMRITTIKA / BHUMI-SYNC — Citizen Personal Workspace & Services API
Server-side RBAC & IDOR-protected endpoints for Citizen role:
- Linked parcels & title timeline
- Mutation & service applications
- Personal notices & summons
- Activity & submission history
"""

import json
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.services.auth import require_authenticated_user, log_security_event

router = APIRouter(prefix="/citizen", tags=["Citizen Workspace"])


def require_citizen_access(user: Dict[str, Any] = Depends(require_authenticated_user)) -> Dict[str, Any]:
    """Ensures user is an authenticated CITIZEN (or administrator conducting auditing)."""
    role = user.get("role")
    if role not in ["CITIZEN", "ADMINISTRATOR"]:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: Role '{role}' lacks permission for citizen personal records."
        )
    return user


class CitizenApplicationCreateRequest(BaseModel):
    parcel_id: str = Field(..., description="Target parcel ID")
    app_type: Optional[str] = Field(None, description="Application type (e.g. MUTATION, CORRECTION, CERTIFIED_COPY)")
    service_type: Optional[str] = Field(None, description="Alternative service type alias")
    details: Dict[str, Any] = Field(default_factory=dict, description="Application metadata")
    mouza_name: Optional[str] = None
    dag_no: Optional[str] = None
    applicant_phone: Optional[str] = None
    remarks: Optional[str] = None


@router.get("/my-parcels")
def get_citizen_parcels(
    citizen: Dict[str, Any] = Depends(require_citizen_access),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns the authenticated citizen's explicitly linked parcels and verified records."""
    cur = db.cursor()
    cur.execute("""
        SELECT cp.link_id, cp.parcel_id, cp.ownership_type, cp.share_percent, cp.khatian_no,
               cp.tax_status, cp.created_at as linked_at,
               p.mouza, p.dag_number, p.area_decimal, p.land_classification, p.is_disputed, p.khatian_number
        FROM citizen_parcels cp
        JOIN parcels p ON cp.parcel_id = p.parcel_id
        WHERE cp.user_id = ?
        ORDER BY cp.created_at DESC
    """, (citizen["user_id"],))

    parcels = [dict(r) for r in cur.fetchall()]
    return {
        "user_id": citizen["user_id"],
        "citizen_name": citizen.get("name", "নাগরিক"),
        "total_linked": len(parcels),
        "parcels": parcels
    }


@router.get("/my-applications")
def get_citizen_applications(
    citizen: Dict[str, Any] = Depends(require_citizen_access),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns the authenticated citizen's submitted service and mutation applications."""
    cur = db.cursor()
    cur.execute("""
        SELECT ca.app_id, ca.parcel_id, ca.app_type, ca.status, ca.details_json,
               ca.hearing_date, ca.officer_notes, ca.created_at, ca.updated_at,
               p.mouza, p.dag_number
        FROM citizen_applications ca
        JOIN parcels p ON ca.parcel_id = p.parcel_id
        WHERE ca.user_id = ?
        ORDER BY ca.created_at DESC
    """, (citizen["user_id"],))

    rows = cur.fetchall()
    apps = []
    for r in rows:
        d = dict(r)
        try:
            d["details"] = json.loads(d["details_json"])
        except Exception:
            d["details"] = {}
        apps.append(d)

    return {
        "user_id": citizen["user_id"],
        "total_applications": len(apps),
        "applications": apps
    }


@router.get("/my-applications/{app_id}")
def get_citizen_application_detail(
    app_id: str,
    citizen: Dict[str, Any] = Depends(require_citizen_access),
    db: sqlite3.Connection = Depends(get_db)
):
    """IDOR Protected: Returns details of a specific application strictly if owned by current citizen."""
    cur = db.cursor()
    cur.execute("""
        SELECT ca.*, p.mouza, p.dag_number, p.area_decimal
        FROM citizen_applications ca
        JOIN parcels p ON ca.parcel_id = p.parcel_id
        WHERE ca.app_id = ?
    """, (app_id,))
    row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="আবেদনটি খুঁজে পাওয়া যায়নি।")

    app_data = dict(row)
    # IDOR Check: Ensure application belongs to requesting user (unless platform admin)
    if app_data["user_id"] != citizen["user_id"] and citizen.get("role") != "ADMINISTRATOR":
        raise HTTPException(
            status_code=403,
            detail="অননুমোদিত প্রবেশাধিকার: আপনি অন্য নাগরিকের ব্যক্তিগত আবেদন পর্যালোচনা করতে পারবেন না।"
        )

    try:
        app_data["details"] = json.loads(app_data["details_json"])
    except Exception:
        app_data["details"] = {}

    return app_data


@router.post("/applications")
def create_citizen_application(
    req: CitizenApplicationCreateRequest,
    citizen: Dict[str, Any] = Depends(require_citizen_access),
    db: sqlite3.Connection = Depends(get_db)
):
    """Submits a new simulated mutation or record-correction application."""
    cur = db.cursor()
    # Verify parcel exists
    cur.execute("SELECT parcel_id, mouza, dag_number FROM parcels WHERE parcel_id = ?", (req.parcel_id,))
    parcel = cur.fetchone()
    if not parcel:
        raise HTTPException(status_code=404, detail=f"পার্সেল আইডি '{req.parcel_id}' বিদ্যমান নেই।")

    cur.execute("SELECT COUNT(*) FROM citizen_applications")
    app_count = cur.fetchone()[0] + 1
    app_id = f"APP-MUT-2026-{app_count:04d}"
    now_ts = datetime.now(timezone.utc).isoformat()

    actual_app_type = req.app_type or req.service_type or "MUTATION"
    details_dict = dict(req.details)
    if req.mouza_name:
        details_dict["mouza_name"] = req.mouza_name
    if req.dag_no:
        details_dict["dag_no"] = req.dag_no
    if req.applicant_phone:
        details_dict["applicant_phone"] = req.applicant_phone
    if req.remarks:
        details_dict["remarks"] = req.remarks

    details_json = json.dumps(details_dict, ensure_ascii=False)

    cur.execute("""
        INSERT INTO citizen_applications (app_id, user_id, parcel_id, app_type, status, details_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'SUBMITTED', ?, ?, ?)
    """, (app_id, citizen["user_id"], req.parcel_id, actual_app_type, details_json, now_ts, now_ts))

    # Add confirmation notification
    notif_id = f"NOTIF-{app_count:04d}"
    cur.execute("""
        INSERT INTO citizen_notifications (notif_id, user_id, title, message, notif_type, is_read, created_at)
        VALUES (?, ?, 'নতুন আবেদন গৃহীত', ?, 'APPLICATION', 0, ?)
    """, (notif_id, citizen["user_id"], f"আপনার আবেদন {app_id} সফলভাবে দাখিল হয়েছে। প্রাথমিক যাচাই শেষে শুনানির তারিখ জানানো হবে।", now_ts))

    db.commit()

    return {
        "success": True,
        "status": "SUCCESS",
        "app_id": app_id,
        "application_id": app_id,
        "parcel_id": req.parcel_id,
        "message": "আবেদনটি সফলভাবে সহকারী কমিশনার (ভূমি) এর যাচাইকরণ ট্রায়াজে প্রেরণ করা হয়েছে।"
    }


@router.get("/my-notifications")
def get_citizen_notifications(
    citizen: Dict[str, Any] = Depends(require_citizen_access),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns official notifications, summons, and alerts for authenticated citizen."""
    cur = db.cursor()
    cur.execute("""
        SELECT notif_id, title, message, notif_type, is_read, created_at
        FROM citizen_notifications
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (citizen["user_id"],))

    notifs = [dict(r) for r in cur.fetchall()]
    return {
        "user_id": citizen["user_id"],
        "unread_count": sum(1 for n in notifs if n["is_read"] == 0),
        "notifications": notifs
    }


@router.post("/notifications/{notif_id}/read")
def mark_notification_read(
    notif_id: str,
    citizen: Dict[str, Any] = Depends(require_citizen_access),
    db: sqlite3.Connection = Depends(get_db)
):
    """Marks a citizen notification as read."""
    cur = db.cursor()
    cur.execute("UPDATE citizen_notifications SET is_read = 1 WHERE notif_id = ? AND user_id = ?",
                (notif_id, citizen["user_id"]))
    db.commit()
    return {"status": "SUCCESS", "notif_id": notif_id}


@router.get("/my-activity")
def get_citizen_activity(
    citizen: Dict[str, Any] = Depends(require_citizen_access),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns personal audit trail and activity history."""
    cur = db.cursor()
    cur.execute("""
        SELECT log_id, action, timestamp, details_json
        FROM security_audit_logs
        WHERE user_id = ? OR actor_email = ?
        ORDER BY timestamp DESC
        LIMIT 20
    """, (citizen["user_id"], citizen.get("email", "")))

    logs = [dict(r) for r in cur.fetchall()]
    return {
        "user_id": citizen["user_id"],
        "activity": logs,
        "activity_logs": logs
    }
