"""
DESHMRITTIKA / BHUMI-SYNC — Officer Triage Queue & Audit Trail Endpoints
Server-side RBAC enforced: Accessible only to OFFICER and ADMINISTRATOR roles.
"""

import sqlite3
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.database import get_db
from backend.app.schemas.models import ReviewDecisionRequest
from backend.app.services.auth import require_officer_role

router = APIRouter(prefix="/officer", tags=["Officer Review"])

@router.get("/queue")
def get_officer_triage_queue(
    severity: str = Query(None, description="Filter by severity: CRITICAL, HIGH, MEDIUM, LOW"),
    limit: int = Query(50, ge=1, le=200),
    officer: dict = Depends(require_officer_role),
    db: sqlite3.Connection = Depends(get_db)
):
    cur = db.cursor()
    query = """
        SELECT vc.*, p.mouza, p.dag_number, p.area_decimal
        FROM verification_cases vc
        JOIN parcels p ON vc.parcel_id = p.parcel_id
        WHERE vc.review_status IN ('PENDING_REVIEW', 'UNDER_INVESTIGATION')
    """
    params = []
    if severity:
        query += " AND vc.severity = ?"
        params.append(severity)

    query += " ORDER BY vc.risk_score DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    cases = [dict(r) for r in cur.fetchall()]
    return {
        "officer": officer["name"],
        "role": officer["role"],
        "pending_count": len(cases),
        "queue": cases
    }

@router.post("/decision")
def record_review_decision(
    req: ReviewDecisionRequest,
    officer: dict = Depends(require_officer_role),
    db: sqlite3.Connection = Depends(get_db)
):
    allowed_actions = ['APPROVED_LEGITIMATE', 'REJECTED_FRAUD_FLAG', 'REQUESTED_PHYSICAL_INSPECTION']
    if req.action not in allowed_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action '{req.action}'. Allowed: {allowed_actions}")

    cur = db.cursor()
    cur.execute("SELECT * FROM verification_cases WHERE case_id = ?", (req.case_id,))
    case = cur.fetchone()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case with ID '{req.case_id}' not found.")

    # Generate log ID
    cur.execute("SELECT COUNT(*) FROM review_logs")
    log_count = cur.fetchone()[0] + 1
    log_id = f"LOG-{log_count:06d}"
    now_ts = datetime.now(timezone.utc).isoformat()

    # Insert review log
    cur.execute("""
        INSERT INTO review_logs (log_id, case_id, reviewer_id, action, reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (log_id, req.case_id, officer["user_id"], req.action, req.reason, now_ts))

    # Update case status
    new_status = "RESOLVED_CLEARED" if req.action == "APPROVED_LEGITIMATE" else "UNDER_INVESTIGATION"
    cur.execute("""
        UPDATE verification_cases
        SET review_status = ?
        WHERE case_id = ?
    """, (new_status, req.case_id))

    db.commit()

    return {
        "status": "SUCCESS",
        "log_id": log_id,
        "case_id": req.case_id,
        "action": req.action,
        "reviewer": officer["user_id"],
        "timestamp": now_ts
    }

@router.get("/audit-logs")
def get_audit_trail(
    limit: int = Query(50, ge=1, le=200),
    officer: dict = Depends(require_officer_role),
    db: sqlite3.Connection = Depends(get_db)
):
    cur = db.cursor()
    cur.execute("""
        SELECT rl.*, vc.parcel_id, vc.finding_code
        FROM review_logs rl
        JOIN verification_cases vc ON rl.case_id = vc.case_id
        ORDER BY rl.timestamp DESC
        LIMIT ?
    """, (limit,))
    logs = [dict(r) for r in cur.fetchall()]
    return {"total": len(logs), "audit_logs": logs}
