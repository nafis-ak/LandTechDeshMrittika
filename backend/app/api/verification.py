"""
DESHMRITTIKA / BHUMI-SYNC — Verification & Fraud Detection Endpoints
"""

import sqlite3
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.database import get_db
from backend.app.schemas.models import ParcelEvaluationReport
from backend.app.services.verification import DoubleSellingEngine

router = APIRouter(prefix="/verification", tags=["Verification"])

@router.get("/evaluate/{parcel_id}", response_model=ParcelEvaluationReport)
@router.post("/evaluate/{parcel_id}", response_model=ParcelEvaluationReport)
def evaluate_parcel_fraud_risk(parcel_id: str, db: sqlite3.Connection = Depends(get_db)):
    report = DoubleSellingEngine.evaluate_parcel(db, parcel_id)
    if report.overall_status == "PARCEL_NOT_FOUND":
        raise HTTPException(status_code=404, detail=f"Parcel '{parcel_id}' not found.")
    return report

@router.get("/cases")
def list_verification_cases(
    finding_code: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db)
):
    cur = db.cursor()
    query = "SELECT * FROM verification_cases WHERE 1=1"
    params = []

    if finding_code:
        query += " AND finding_code = ?"
        params.append(finding_code)
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    if review_status:
        query += " AND review_status = ?"
        params.append(review_status)

    query += " ORDER BY risk_score DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    return {"total": len(rows), "cases": rows}
