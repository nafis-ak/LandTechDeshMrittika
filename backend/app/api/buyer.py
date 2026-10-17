"""
DESHMRITTIKA / BHUMI-SYNC — Buyer Due Diligence & Review Request API
Server-side RBAC endpoints for Buyer role:
- Review request creation and tracking
- Parcel comparison assistance
- Sanitized due diligence without sensitive personal NIDs
"""

import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.services.auth import require_authenticated_user

router = APIRouter(prefix="/buyer", tags=["Buyer Due Diligence"])


def require_buyer_access(user: Dict[str, Any] = Depends(require_authenticated_user)) -> Dict[str, Any]:
    """Ensures user is an authenticated BUYER (or administrator)."""
    role = user.get("role")
    if role not in ["BUYER", "ADMINISTRATOR"]:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: Role '{role}' lacks permission for buyer review operations."
        )
    return user


class BuyerReviewRequest(BaseModel):
    parcel_id: str = Field(..., description="Target parcel ID to request review for")
    reason: str = Field(..., description="Reason for suspicious transfer review")
    urgency: str = Field("NORMAL", description="Urgency: NORMAL, HIGH, URGENT")
    mouza_name: Optional[str] = None
    dag_no: Optional[str] = None
    contact_email: Optional[str] = None


@router.post("/review-requests")
def submit_buyer_review_request(
    req: BuyerReviewRequest,
    buyer: Dict[str, Any] = Depends(require_buyer_access),
    db: sqlite3.Connection = Depends(get_db)
):
    """Submits a verification review request to the AC Land office for a suspect parcel."""
    cur = db.cursor()
    cur.execute("SELECT parcel_id, mouza, dag_number FROM parcels WHERE parcel_id = ?", (req.parcel_id,))
    parcel = cur.fetchone()
    if not parcel:
        raise HTTPException(status_code=404, detail=f"পার্সেল আইডি '{req.parcel_id}' বিদ্যমান নেই।")

    cur.execute("SELECT COUNT(*) FROM buyer_review_requests")
    count = cur.fetchone()[0] + 1
    req_id = f"BRR-2026-{count:04d}"
    now_ts = datetime.now(timezone.utc).isoformat()

    cur.execute("""
        INSERT INTO buyer_review_requests (request_id, buyer_id, parcel_id, reason, urgency, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'PENDING_OFFICER_REVIEW', ?)
    """, (req_id, buyer["user_id"], req.parcel_id, req.reason, req.urgency, now_ts))

    db.commit()

    return {
        "success": True,
        "status": "SUCCESS",
        "request_id": req_id,
        "parcel_id": req.parcel_id,
        "message": "আপনার পুনঃযাচাই আবেদনটি সহকারী কমিশনার (ভূমি) কার্যালয়ের ট্রায়াজে অন্তর্ভুক্ত করা হয়েছে।"
    }


@router.get("/review-requests")
def list_buyer_review_requests(
    buyer: Dict[str, Any] = Depends(require_buyer_access),
    db: sqlite3.Connection = Depends(get_db)
):
    """Lists all review requests submitted by the current buyer."""
    cur = db.cursor()
    cur.execute("""
        SELECT brr.*, p.mouza, p.dag_number, p.area_decimal, p.is_disputed
        FROM buyer_review_requests brr
        JOIN parcels p ON brr.parcel_id = p.parcel_id
        WHERE brr.buyer_id = ?
        ORDER BY brr.created_at DESC
    """, (buyer["user_id"],))

    requests = [dict(r) for r in cur.fetchall()]
    return {
        "buyer_id": buyer["user_id"],
        "total": len(requests),
        "total_requests": len(requests),
        "requests": requests
    }
