"""
DESHMRITTIKA / BHUMI-SYNC — Land Intelligence Dashboard Endpoints
Provides live aggregated counts, recent activity logs, and curated demo parcels.
"""

import sqlite3
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from backend.app.database import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: sqlite3.Connection = Depends(get_db)):
    """
    Returns real database-backed metrics for the overview dashboard:
    - Total demo parcels
    - High-risk records (CRITICAL + HIGH severity)
    - Pending verification cases
    - Completed mutation applications
    - Recent activity logs (privacy-filtered)
    - Sample showcase parcels
    """
    cur = db.cursor()

    # 1. Total parcels
    cur.execute("SELECT COUNT(*) FROM parcels")
    total_parcels = cur.fetchone()[0]

    # 2. High-risk records (CRITICAL + HIGH)
    cur.execute("""
        SELECT COUNT(*) FROM verification_cases
        WHERE severity IN ('CRITICAL', 'HIGH')
    """)
    high_risk_records = cur.fetchone()[0]

    # 3. Pending verification
    cur.execute("""
        SELECT COUNT(*) FROM verification_cases
        WHERE review_status IN ('PENDING_REVIEW', 'UNDER_INVESTIGATION')
    """)
    pending_verification = cur.fetchone()[0]

    # 4. Completed applications (mutations approved)
    cur.execute("""
        SELECT COUNT(*) FROM mutation_records
        WHERE status = 'APPROVED'
    """)
    completed_applications = cur.fetchone()[0]

    # 5. Recent activity logs (from review_logs & citizen_applications)
    cur.execute("""
        SELECT rl.log_id, rl.case_id, rl.action, rl.reason, rl.timestamp,
               vc.parcel_id, p.mouza, p.dag_number
        FROM review_logs rl
        JOIN verification_cases vc ON rl.case_id = vc.case_id
        JOIN parcels p ON vc.parcel_id = p.parcel_id
        ORDER BY rl.timestamp DESC
        LIMIT 6
    """)
    review_rows = cur.fetchall()

    recent_activity = []
    action_labels = {
        "APPROVED_LEGITIMATE": {"bn": "রেকর্ড সঠিক হিসেবে অনুমোদিত", "badge": "success", "icon": "✓"},
        "REJECTED_FRAUD_FLAG": {"bn": "দ্বৈত হস্তান্তর সন্দেহে স্থগিতাদেশ", "badge": "danger", "icon": "🚨"},
        "REQUESTED_PHYSICAL_INSPECTION": {"bn": "সরেজমিন তদন্ত ও বালাম বহি তলব", "badge": "warning", "icon": "🔍"}
    }

    for r in review_rows:
        meta = action_labels.get(r["action"], {"bn": r["action"], "badge": "secondary", "icon": "📋"})
        recent_activity.append({
            "id": r["log_id"],
            "case_id": r["case_id"],
            "parcel_id": r["parcel_id"],
            "mouza": r["mouza"],
            "dag_number": r["dag_number"],
            "action": r["action"],
            "action_text_bn": meta["bn"],
            "badge_type": meta["badge"],
            "icon": meta["icon"],
            "reason_summary": r["reason"][:80] + ("..." if len(r["reason"]) > 80 else ""),
            "timestamp": r["timestamp"]
        })

    # If review_logs are fewer than 4, fill with recent applications
    if len(recent_activity) < 4:
        cur.execute("""
            SELECT ca.app_id, ca.parcel_id, ca.app_type, ca.status, ca.created_at,
                   p.mouza, p.dag_number
            FROM citizen_applications ca
            JOIN parcels p ON ca.parcel_id = p.parcel_id
            ORDER BY ca.created_at DESC
            LIMIT 4
        """)
        for ca in cur.fetchall():
            recent_activity.append({
                "id": ca["app_id"],
                "case_id": ca["app_id"],
                "parcel_id": ca["parcel_id"],
                "mouza": ca["mouza"],
                "dag_number": ca["dag_number"],
                "action": ca["status"],
                "action_text_bn": "ই-নামজারি আবেদন দাখিল" if ca["status"] == "SUBMITTED" else "শুনানি নির্ধারিত",
                "badge_type": "info" if ca["status"] == "SUBMITTED" else "warning",
                "icon": "📝",
                "reason_summary": f"{ca['app_type']} আবেদন দাখিল সম্পন্ন হয়েছে।",
                "timestamp": ca["created_at"]
            })

    # 6. Sample showcase parcels across different risk categories
    sample_parcels = [
        {
            "parcel_id": "BD-PAR-000101",
            "dag_number": 101,
            "khatian_number": 501,
            "mouza": "Aminbazar",
            "mouza_bn": "আমিনবাজার",
            "upazila_bn": "সাভার",
            "district_bn": "ঢাকা",
            "preset_key": "ds1",
            "risk_type": "CRITICAL_BLOCKED",
            "risk_label_bn": "দ্বৈত বিক্রয় অ্যালার্ট (DS-01)",
            "risk_badge": "danger",
            "risk_score": 95,
            "area_decimal": 10.0,
            "lat": 23.7845,
            "lon": 90.3120,
            "description_bn": "একই বিক্রেতা কর্তৃক ২০১৬ ও ২০২৩ সালে দুটি ভিন্ন দলিলের মাধ্যমে দ্বৈত বিক্রয়ের অপচেষ্টা।"
        },
        {
            "parcel_id": "BD-PAR-001001",
            "dag_number": 1001,
            "khatian_number": 1205,
            "mouza": "Birulia",
            "mouza_bn": "বিরুলিয়া",
            "upazila_bn": "সাভার",
            "district_bn": "ঢাকা",
            "preset_key": "ds2",
            "risk_type": "SAFE",
            "risk_label_bn": "নির্দোষ হস্তান্তর (DS-02)",
            "risk_badge": "success",
            "risk_score": 10,
            "area_decimal": 15.5,
            "lat": 23.8340,
            "lon": 90.3210,
            "description_bn": "সিএস, এসএ, আরএস থেকে বিএস পর্যন্ত বায়া দলিল শৃঙ্খল সম্পূর্ণ অটুট ও খাজনা পরিশোধিত।"
        },
        {
            "parcel_id": "BD-PAR-000205",
            "dag_number": 205,
            "khatian_number": 1,
            "mouza": "Savar",
            "mouza_bn": "সাভার পৌরসভা",
            "upazila_bn": "সাভার",
            "district_bn": "ঢাকা",
            "preset_key": "khas",
            "risk_type": "CRITICAL_BLOCKED",
            "risk_label_bn": "১-নং সরকারি খাস জমি",
            "risk_badge": "danger",
            "risk_score": 100,
            "area_decimal": 25.0,
            "lat": 23.8450,
            "lon": 90.2610,
            "description_bn": "গণপ্রজাতন্ত্রী বাংলাদেশ সরকারের পক্ষে জেলা প্রশাসক অনুকূলে সংরক্ষিত খাল ও নদী তীরের জমি।"
        },
        {
            "parcel_id": "BD-PAR-000304",
            "dag_number": 304,
            "khatian_number": 680,
            "mouza": "Aminbazar",
            "mouza_bn": "আমিনবাজার",
            "upazila_bn": "সাভার",
            "district_bn": "ঢাকা",
            "preset_key": "acq",
            "risk_type": "HIGH_RISK",
            "risk_label_bn": "মেট্রোরেল লাইন-৫ অধিগ্রহণ রুট",
            "risk_badge": "warning",
            "risk_score": 75,
            "area_decimal": 12.2,
            "lat": 23.7890,
            "lon": 90.3180,
            "description_bn": "ঢাকা ম্যাস ট্রানজিট কোম্পানি লিমিটেড (ডিএমটিসিএল) প্রকল্প অধিগ্রহণ করিডোরের আওতাভুক্ত।"
        }
    ]

    return {
        "status": "SUCCESS",
        "summary": {
            "total_parcels": total_parcels,
            "high_risk_records": high_risk_records,
            "pending_verification": pending_verification,
            "completed_applications": completed_applications
        },
        "recent_activity": recent_activity,
        "sample_parcels": sample_parcels,
        "disclaimer": "ডেমো ডাটা — এটি কোনো অফিশিয়াল সরকারি ভূমি জরিপ বা রেকর্ড নয়।"
    }
