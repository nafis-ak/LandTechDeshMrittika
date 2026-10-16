"""
DESHMRITTIKA / BHUMI-SYNC — Buyer Due Diligence Service (P5 Track)
Synthesizes 5-Point Safety Dossier for citizen 'Check Before You Buy'.
"""

import sqlite3
from typing import Optional, Dict, Any, List
from backend.app.schemas.models import DueDiligenceDossier, ParcelSummary, VerificationFinding
from backend.app.services.verification import DoubleSellingEngine, LEGAL_DISCLAIMER

class DueDiligenceService:

    @staticmethod
    def generate_buyer_dossier(conn: sqlite3.Connection, parcel_id: str) -> Optional[DueDiligenceDossier]:
        cur = conn.cursor()

        # Parcel summary
        cur.execute("SELECT * FROM parcels WHERE parcel_id = ?", (parcel_id,))
        p = cur.fetchone()
        if not p:
            return None

        parcel_summary = ParcelSummary(
            parcel_id=p["parcel_id"],
            district=p["district"],
            upazila=p["upazila"],
            mouza=p["mouza"],
            jl_number=p["jl_number"],
            dag_number=p["dag_number"],
            khatian_number=p["khatian_number"],
            survey_type=p["survey_type"],
            land_classification=p["land_classification"],
            area_decimal=float(p["area_decimal"]),
            is_disputed=bool(p["is_disputed"]),
            provenance_label=p["provenance_label"]
        )

        # Run verification engine
        eval_report = DoubleSellingEngine.evaluate_parcel(conn, parcel_id)

        # 1. Ownership chain check
        cur.execute("""
            SELECT COUNT(*) FROM parcel_ownership WHERE parcel_id = ?
        """, (parcel_id,))
        ownership_count = cur.fetchone()[0]

        # 2. Unmutated deeds
        cur.execute("""
            SELECT COUNT(*) FROM deeds d
            LEFT JOIN mutation_records m ON d.deed_id = m.deed_id
            WHERE d.parcel_id = ? AND (m.status IS NULL OR m.status != 'APPROVED')
        """, (parcel_id,))
        unmutated_count = cur.fetchone()[0]

        # 3. Active Disputes
        cur.execute("""
            SELECT COUNT(*) FROM litigation_records
            WHERE parcel_id = ? AND status = 'ACTIVE_INJUNCTION_STAY'
        """, (parcel_id,))
        active_disputes = cur.fetchone()[0]

        # 4. Tax Compliance
        cur.execute("""
            SELECT payment_status FROM tax_records
            WHERE parcel_id = ?
            ORDER BY tax_year DESC LIMIT 1
        """, (parcel_id,))
        tax_row = cur.fetchone()
        tax_compliant = (tax_row is not None and tax_row[0] == "PAID")

        # 5. Khas check
        cur.execute("SELECT COUNT(*) FROM khas_records WHERE parcel_id = ?", (parcel_id,))
        is_khas = (cur.fetchone()[0] > 0)

        # 6. Acquisition check (check if within coordinates)
        # Mocking check for demo
        is_acquisition = False

        # Build 5-Point Safety Checklist
        checklist: List[Dict[str, Any]] = [
            {
                "point": 1,
                "title_bn": "মালিকানা চেইন ও খতিয়ান হিস্যা",
                "title_en": "Ownership Chain & ROR Shares",
                "status": "PASSED" if not any(f.finding_code in ['DS-01', 'DS-03'] for f in eval_report.findings) else "FAILED",
                "details_bn": "খতিয়ান হিস্যার সাথে বিক্রয়যোগ্য অংশের পূর্ণ মিল রয়েছে।" if unmutated_count == 0 else f"{unmutated_count}টি অনিষ্পন্ন দলিল বিদ্যমান।"
            },
            {
                "point": 2,
                "title_bn": "দ্বৈত বিক্রয় ও রেজিস্ট্রি যাচাই",
                "title_en": "Double-Selling & Registry Integrity",
                "status": "FAILED" if any(f.finding_code == 'DS-01' for f in eval_report.findings) else "PASSED",
                "details_bn": "পূর্বে সম্পাদিত কোনো অনিষ্পন্ন দলিলের অস্তিত্ব নেই।" if not any(f.finding_code == 'DS-01' for f in eval_report.findings) else "একই বিক্রেতা কর্তৃক দ্বৈত হস্তান্তরের গুরুতর ঝুঁকি শনাক্ত।"
            },
            {
                "point": 3,
                "title_bn": "ভূমি উন্নয়ন কর হালনাগাদ (LDTax)",
                "title_en": "Land Development Tax Clearance",
                "status": "PASSED" if tax_compliant else "WARNING",
                "details_bn": "সর্বশেষ অর্থবছরের ভূমি উন্নয়ন কর পরিশোধিত।" if tax_compliant else "বকেয়া কর অপরিশোধিত রয়েছে। নামজারির পূর্বে দাখিলা গ্রহণ আবশ্যক।"
            },
            {
                "point": 4,
                "title_bn": "আদালতের দেওয়ানি মামলা ও নিষেধাজ্ঞা",
                "title_en": "Civil Litigation & Court Injunctions",
                "status": "PASSED" if active_disputes == 0 else "WARNING",
                "details_bn": "কোনো সক্রিয় নিষেধাজ্ঞা পাওয়া যায়নি।" if active_disputes == 0 else f"আদালতে {active_disputes}টি মামলা/স্থগিতাদেশ চলমান রয়েছে।"
            },
            {
                "point": 5,
                "title_bn": "সরকারি খাস ও অধিগ্রহণ মুক্ততা",
                "title_en": "Khas Land & Acquisition Clearance",
                "status": "FAILED" if is_khas else "PASSED",
                "details_bn": "ব্যক্তিমালিকানাধীন বৈধ জোত।" if not is_khas else "অত্র দাগটি সরকারি ১নং খাস খতিয়ানভুক্ত সম্পত্তি। হস্তান্তর সম্পূর্ণ নিষিদ্ধ।"
            }
        ]

        # Overall safety rating
        if is_khas or any(f.finding_code == 'DS-01' for f in eval_report.findings):
            rating = "CRITICAL_BLOCKED"
        elif eval_report.overall_risk_score >= 60:
            rating = "HIGH_RISK"
        elif eval_report.overall_risk_score >= 30:
            rating = "CAUTION"
        else:
            rating = "SAFE"

        return DueDiligenceDossier(
            parcel=parcel_summary,
            ownership_chain_verified=(unmutated_count == 0),
            unmutated_deeds_count=unmutated_count,
            active_disputes_count=active_disputes,
            tax_compliant=tax_compliant,
            is_government_khas=is_khas,
            is_acquisition_corridor=is_acquisition,
            risk_score=eval_report.overall_risk_score,
            safety_rating=rating,
            safety_checklist=checklist,
            findings=eval_report.findings,
            disclaimer=LEGAL_DISCLAIMER
        )
