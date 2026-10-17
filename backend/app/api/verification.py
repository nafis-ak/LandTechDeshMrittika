"""
DESHMRITTIKA / BHUMI-SYNC — Verification & Fraud Detection Endpoints
"""

import sqlite3
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.database import get_db
from backend.app.schemas.models import ParcelEvaluationReport
from backend.app.services.verification import DoubleSellingEngine
from backend.app.services.auth import require_officer_role

router = APIRouter(prefix="/verification", tags=["Verification"])

@router.get("/evaluate/{parcel_id}", response_model=ParcelEvaluationReport)
@router.post("/evaluate/{parcel_id}", response_model=ParcelEvaluationReport)
def evaluate_parcel_fraud_risk(parcel_id: str, db: sqlite3.Connection = Depends(get_db)):
    report = DoubleSellingEngine.evaluate_parcel(db, parcel_id)
    if report.overall_status == "PARCEL_NOT_FOUND":
        raise HTTPException(status_code=404, detail=f"Parcel '{parcel_id}' not found.")
    return report

@router.get("/stats")
def get_fraud_risk_stats(db: sqlite3.Connection = Depends(get_db)):
    """
    Returns aggregated counts for Fraud / Risk Analysis Screen:
    - High-risk cases (CRITICAL + HIGH severity)
    - Cases awaiting review (PENDING_REVIEW or UNDER_INVESTIGATION)
    - Confirmed demo fraud scenarios (from fraud_scenarios table)
    - Cleared/Resolved cases (RESOLVED_CLEARED)
    """
    cur = db.cursor()

    cur.execute("""
        SELECT COUNT(*) FROM verification_cases
        WHERE severity IN ('CRITICAL', 'HIGH')
    """)
    high_risk_cases = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM verification_cases
        WHERE review_status IN ('PENDING_REVIEW', 'UNDER_INVESTIGATION')
    """)
    awaiting_review = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM verification_cases WHERE finding_code = 'DS-01'")
    confirmed_demo_scenarios = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM verification_cases
        WHERE review_status = 'RESOLVED_CLEARED'
    """)
    cleared_cases = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM verification_cases")
    total_recorded_cases = cur.fetchone()[0]

    return {
        "high_risk_cases": high_risk_cases,
        "awaiting_review": awaiting_review,
        "confirmed_demo_scenarios": confirmed_demo_scenarios,
        "cleared_cases": cleared_cases,
        "total_recorded_cases": total_recorded_cases,
        "label_clarification": "সিন্থেটিক টেস্ট কেস ও সিমুলেটেড তদন্ত রেকর্ড",
        "disclaimer": "ডেমো ডাটা — স্বয়ংক্রিয় অ্যালার্ট কোনো নিশ্চিত আইনি অপরাধ নয়; এটি পর্যালোচনার জন্য চিহ্নিত সন্দেহজনক কেস।"
    }

@router.get("/cases")
def list_verification_cases(
    finding_code: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search by Case ID, Parcel ID, or Mouza"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db)
):
    cur = db.cursor()
    query = """
        SELECT vc.*, p.mouza, p.dag_number, p.khatian_number, p.area_decimal, p.is_disputed
        FROM verification_cases vc
        JOIN parcels p ON vc.parcel_id = p.parcel_id
        WHERE 1=1
    """
    params = []

    if finding_code:
        query += " AND vc.finding_code = ?"
        params.append(finding_code)
    if severity:
        query += " AND vc.severity = ?"
        params.append(severity)
    if review_status:
        query += " AND vc.review_status = ?"
        params.append(review_status)
    if search:
        s = f"%{search.strip()}%"
        query += " AND (vc.case_id LIKE ? OR vc.parcel_id LIKE ? OR p.mouza LIKE ? OR p.dag_number LIKE ?)"
        params.extend([s, s, s, s])

    # Count total matching
    count_query = f"SELECT COUNT(*) FROM ({query})"
    cur.execute(count_query, params)
    total_matching = cur.fetchone()[0]

    query += " ORDER BY vc.risk_score DESC, vc.case_id ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    return {
        "total": total_matching,
        "count": len(rows),
        "limit": limit,
        "offset": offset,
        "cases": rows
    }


@router.get("/cases/{case_id}")
def get_verification_case_detail(case_id: str, db: sqlite3.Connection = Depends(get_db)):
    """
    Returns full investigation dossier for a specific fraud/verification case.
    """
    cur = db.cursor()
    cur.execute("""
        SELECT vc.*, p.district, p.upazila, p.mouza, p.jl_number, p.dag_number,
               p.khatian_number, p.area_decimal, p.land_classification, p.is_disputed,
               p.coordinates_geojson, p.provenance_label
        FROM verification_cases vc
        JOIN parcels p ON vc.parcel_id = p.parcel_id
        WHERE vc.case_id = ?
    """, (case_id,))
    case_row = cur.fetchone()
    if not case_row:
        raise HTTPException(status_code=404, detail=f"Case with ID '{case_id}' not found.")

    case_dict = dict(case_row)
    parcel_id = case_dict["parcel_id"]

    # 1. Registered deeds on this parcel
    cur.execute("""
        SELECT d.deed_id, d.deed_number, d.sub_registry_office, d.deed_type,
               d.execution_date, d.registration_date, d.declared_area, d.deed_value_bdt,
               d.deed_status, s.fictional_name as seller_name, b.fictional_name as buyer_name
        FROM deeds d
        JOIN owners s ON d.seller_id = s.owner_id
        JOIN owners b ON d.buyer_id = b.owner_id
        WHERE d.parcel_id = ?
        ORDER BY d.registration_date DESC
    """, (parcel_id,))
    deeds = [dict(d) for d in cur.fetchall()]

    # 2. Review logs & audit history
    cur.execute("""
        SELECT rl.log_id, rl.case_id, rl.reviewer_id, rl.action, rl.reason, rl.timestamp,
               u.full_name as reviewer_name, u.role as reviewer_role
        FROM review_logs rl
        LEFT JOIN users u ON rl.reviewer_id = u.user_id
        WHERE rl.case_id = ?
        ORDER BY rl.timestamp DESC
    """, (case_id,))
    review_logs = [dict(l) for l in cur.fetchall()]

    # 3. Rule specifications
    rule_explanations = {
        "DS-01": {
            "name_bn": "পূর্ববর্তী হস্তান্তর গোপনপূর্বক দ্বৈত সাফ-কবালা বিক্রয়",
            "statutory_ref": "দণ্ডবিধি ১৮৬০ ধারা ৪২০/৪৬৮/৪৭১ ও রেজিস্ট্রেশন আইন ১৯০৮ ধারা ৫২ক",
            "trigger_condition": "একই বিক্রেতা কর্তৃক কোনো জমির সম্পূর্ণ বা অংশবিশেষ হস্তান্তরের পর পুনরায় অপর ক্রেতার কাছে বিক্রয় চুক্তি/দলিল সম্পাদন।",
            "recommended_action": "অবিলম্বে রেজিস্ট্রেশন স্থগিতকরণ এবং সহকারী কমিশনার (ভূমি) ট্রায়াজে শুনানির তলব।"
        },
        "DS-03": {
            "name_bn": "অননুমোদিত ও অমীমাংসিত মধ্যবর্তী বায়া হস্তান্তর",
            "statutory_ref": "রাষ্ট্রীয় অধিগ্রহণ ও প্রজাস্বত্ব আইন ১৯৫০ (SATA 1950) ধারা ১৪৩",
            "trigger_condition": "হস্তান্তর দলিলের পর নামজারি খতিয়ান সম্পন্ন না করেই পরবর্তী হস্তান্তর সম্পাদন।",
            "recommended_action": "বায়া দলিলের ধারাবাহিক রেকর্ড ও খারিজ খতিয়ান দাখিলের নির্দেশ প্রদান।"
        },
        "AREA-01": {
            "name_bn": "খতিয়ান হিস্যার চেয়ে অতিরিক্ত জমি বিক্রয় অসঙ্গতি",
            "statutory_ref": "ভূমি সংস্কার আইন ২০২৩ ও ট্রান্সফার অব প্রপার্টি অ্যাক্ট ১৮৮২",
            "trigger_condition": "রেকর্ডে বিক্রেতার মালিকানাধীন অংশের চেয়ে বেশি জমি বিক্রয় দলিলের তফসিলভুক্ত করা হয়েছে।",
            "recommended_action": "রেকর্ডীয় হিস্যা যাচাই সাপেক্ষে অতিরিক্ত অংশ বাদ দিয়ে সংশোধন আদেশ প্রদান।"
        }
    }

    rule_meta = rule_explanations.get(case_dict["finding_code"], {
        "name_bn": f"স্বয়ংক্রিয় অ্যালার্ট কোড {case_dict['finding_code']}",
        "statutory_ref": "ভূমি জরিপ ও রেজিস্ট্রেশন বিধিমালা",
        "trigger_condition": case_dict.get("narrative", "সন্দেহজনক প্যাটার্ন পরিলক্ষিত হয়েছে।"),
        "recommended_action": "নথি তলব ও রাজস্ব যাচাই।"
    })

    rule_specification = {
        "rule_code": case_dict["finding_code"],
        "name_bn": rule_meta["name_bn"],
        "title_bn": rule_meta["name_bn"],
        "statutory_reference": rule_meta["statutory_ref"],
        "statutory_name": rule_meta["name_bn"],
        "description_bn": rule_meta["trigger_condition"],
        "trigger_logic": rule_meta["trigger_condition"],
        "recommended_action": rule_meta["recommended_action"]
    }

    return {
        "case": case_dict,
        "rule_meta": rule_meta,
        "rule_specification": rule_specification,
        "deeds": deeds,
        "registered_deeds": deeds,
        "review_logs": review_logs,
        "disclaimer": "ডেমো ডাটা — এটি কোনো অফিশিয়াল তদন্ত রিপোর্ট নয়; সিমুলেটেড এআই রিস্ক ট্রায়াজ।"
    }


class CaseReviewActionRequest(BaseModel):
    action: str
    reason: str
    officer_role: Optional[str] = "AC_LAND"


@router.post("/cases/{case_id}/review")
def review_case_decision_alias(
    case_id: str,
    req: CaseReviewActionRequest,
    officer: dict = Depends(require_officer_role),
    db: sqlite3.Connection = Depends(get_db)
):
    from backend.app.schemas.models import ReviewDecisionRequest
    from backend.app.api.officer import record_review_decision
    decision_req = ReviewDecisionRequest(case_id=case_id, action=req.action, reason=req.reason)
    res = record_review_decision(decision_req, officer, db)
    new_status = "APPROVED_LEGITIMATE" if req.action == "APPROVED_LEGITIMATE" else "UNDER_INVESTIGATION"
    res["new_status"] = new_status
    return res


