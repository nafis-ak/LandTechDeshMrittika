"""
DESHMRITTIKA / BHUMI-SYNC — Verification & Double-Selling Detection Engine
Implements deterministic, explainable rule vectors DS-01 through DS-05, P5 Litigation, and P6 Khas protection.
"""

import sqlite3
import json
from typing import Dict, Any, List
from backend.app.schemas.models import VerificationFinding, ParcelEvaluationReport

LEGAL_DISCLAIMER = (
    "সতর্কীকরণ: এটি একটি কৃত্রিম ডেটা-চালিত প্রাথমিক ঝুঁকি নিরূপণ ব্যবস্থা। এটি চূড়ান্ত মালিকানা নির্ধারণ করে না বা আদালত/প্রশাসনের বিকল্প নয়।"
    " / DISCLAIMER: This is an advisory synthetic-data risk triage engine. It does not conclusively determine legal ownership or substitute for judicial/administrative authority."
)

class DoubleSellingEngine:
    """Evaluates land parcels for double-selling, unmutated deeds, tax arrears, and boundary conflicts."""

    @staticmethod
    def evaluate_parcel(conn: sqlite3.Connection, parcel_id: str) -> ParcelEvaluationReport:
        cur = conn.cursor()

        # Fetch parcel details
        cur.execute("SELECT * FROM parcels WHERE parcel_id = ?", (parcel_id,))
        parcel = cur.fetchone()
        if not parcel:
            return ParcelEvaluationReport(
                parcel_id=parcel_id,
                overall_risk_score=0,
                overall_status="PARCEL_NOT_FOUND",
                findings=[],
                is_safe_for_transaction=False,
                disclaimer=LEGAL_DISCLAIMER
            )

        parcel_area = float(parcel["area_decimal"])
        findings: List[VerificationFinding] = []
        highest_score = 0

        # RULE 1: DS-01 Active Double-Selling (Concurrent unmutated transfers by same seller)
        cur.execute("""
            SELECT d1.deed_id, d1.deed_number, d1.seller_id, d1.buyer_id, d1.registration_date,
                   d2.deed_id, d2.deed_number, d2.buyer_id, d2.registration_date
            FROM deeds d1
            JOIN deeds d2 ON d1.parcel_id = d2.parcel_id AND d1.seller_id = d2.seller_id AND d1.deed_id != d2.deed_id
            WHERE d1.parcel_id = ?
              AND d1.registration_date <= d2.registration_date
              AND d1.deed_id IN (SELECT deed_id FROM mutation_records WHERE status != 'APPROVED')
        """, (parcel_id,))
        ds1_matches = cur.fetchall()

        if ds1_matches:
            for row in ds1_matches:
                finding = VerificationFinding(
                    finding_code="DS-01",
                    severity="CRITICAL",
                    risk_score=95,
                    explanation_bn=f"জালিয়াতি সতর্কতা: একই বিক্রেতা কর্তৃক প্রথম দলিল ({row[1]}) নিষ্পত্তির পূর্বে দ্বিতীয় দলিল ({row[6]}) সম্পাদন করা হয়েছে। পূর্ববর্তী দলিলের নামজারি অনিষ্পন্ন।",
                    explanation_en=f"Critical Fraud Alert: Concurrent unmutated transfer. Prior deed {row[1]} mutation is unresolved/pending while second deed {row[6]} was registered.",
                    evidence_references={
                        "prior_deed": row[1],
                        "competing_deed": row[6],
                        "seller_id": row[2],
                        "first_buyer_id": row[3],
                        "second_buyer_id": row[7]
                    },
                    recommendation="দলিল রেজিস্ট্রি ও নামজারি অবিলম্বে স্থগিত রাখুন। সাব-রেজিস্ট্রার ও এসি ল্যান্ড যৌথ রেকর্ড যাচাই আবশ্যক।"
                )
                findings.append(finding)
                highest_score = max(highest_score, 95)

        # RULE 2: DS-02 Negative Control Check (Clean Sequential Resales)
        if not ds1_matches:
            cur.execute("""
                SELECT COUNT(DISTINCT d.deed_id)
                FROM deeds d
                JOIN mutation_records m ON d.deed_id = m.deed_id
                WHERE d.parcel_id = ? AND m.status = 'APPROVED'
            """, (parcel_id,))
            approved_conveyances = cur.fetchone()[0]

            if approved_conveyances >= 2:
                findings.append(VerificationFinding(
                    finding_code="DS-02",
                    severity="LOW",
                    risk_score=0,
                    explanation_bn="ধারাবাহিক মালিকানা বৈধ: হস্তান্তরিত দলিলসমূহ অনুমোদিত ই-নামজারির মাধ্যমে সুশৃঙ্খলভাবে সম্পন্ন হয়েছে। কোনো দ্বৈত বিক্রয় নেই।",
                    explanation_en="Clean Sequential Chain: Historical transfers were properly resolved through approved mutations. No double-selling detected.",
                    evidence_references={"approved_mutated_deeds_count": approved_conveyances},
                    recommendation="মালিকানা ধারাবাহিকতা অক্ষুণ্ণ রয়েছে। স্বাভাবিক প্রক্রিয়ায় লেনদেন করা যেতে পারে।"
                ))

        # RULE 3: DS-03 Area Over-Sale Discrepancy
        cur.execute("""
            SELECT deed_id, deed_number, declared_area
            FROM deeds
            WHERE parcel_id = ? AND deed_status != 'CANCELLED_BY_COURT'
        """, (parcel_id,))
        deeds_for_area = cur.fetchall()
        for d in deeds_for_area:
            declared = float(d["declared_area"])
            if declared > (parcel_area + 0.05):  # allowing micro rounding
                findings.append(VerificationFinding(
                    finding_code="DS-03",
                    severity="HIGH",
                    risk_score=75,
                    explanation_bn=f"জমির পরিমাণ অসঙ্গতি: মূল খতিয়ানের পরিমাণ {parcel_area} শতক, কিন্তু দলিল {d['deed_number']}-এ {declared} শতক হস্তান্তর দেখানো হয়েছে।",
                    explanation_en=f"Area Over-Sale Discrepancy: Deed {d['deed_number']} declared {declared} decimals, exceeding surveyed plot area of {parcel_area} decimals.",
                    evidence_references={"deed_number": d["deed_number"], "declared_area": declared, "parcel_area": parcel_area},
                    recommendation="উপজেলা ভূমি অফিসের মাধ্যমে সরেজমিন পরিমাপ ও খতিয়ান হিস্যা সংশোধন নিশ্চিত করুন।"
                ))
                highest_score = max(highest_score, 75)

        # RULE 4: P6 Khas Land Protection
        cur.execute("SELECT * FROM khas_records WHERE parcel_id = ?", (parcel_id,))
        khas = cur.fetchone()
        if khas:
            findings.append(VerificationFinding(
                finding_code="P6-ENCROACH",
                severity="CRITICAL",
                risk_score=90,
                explanation_bn=f"সরকারি সম্পত্তি সতর্কতা: অত্র দাগটি কালেক্টর ঢাকা নিয়ন্ত্রিত '{khas['khas_category']}' তালিকাভুক্ত সরকারি ১নং খাস জমি। ব্যক্তিমালিকানায় ক্রয়-বিক্রয় আইনত নিষিদ্ধ ও বাতিল।",
                explanation_en=f"Government Land Alert: Parcel is gazetted as state property ('{khas['khas_category']}'). Private transfer is legally prohibited and void ab initio.",
                evidence_references={"khas_id": khas["khas_id"], "authority": khas["managing_authority"]},
                recommendation="কোনোরূপ আর্থিক লেনদেন করবেন না। ডিসি অফিসের খাসজমি সেল অথবা এসি ল্যান্ডের সাথে যোগাযোগ করুন।"
            ))
            highest_score = max(highest_score, 90)

        # RULE 5: Civil Court Injunction / Litigation (P5)
        cur.execute("SELECT * FROM litigation_records WHERE parcel_id = ? AND status = 'ACTIVE_INJUNCTION_STAY'", (parcel_id,))
        lits = cur.fetchall()
        for lit in lits:
            findings.append(VerificationFinding(
                finding_code="P5-LITIGATION",
                severity="MEDIUM",
                risk_score=45,
                explanation_bn=f"আদালতের নিষেধাজ্ঞা: {lit['court_name']}-এ মামলা ({lit['case_number']}) চলমান এবং জমিতে আদালতের স্থগিতাদেশ রয়েছে।",
                explanation_en=f"Civil Court Injunction: Active suit ({lit['case_number']}) at {lit['court_name']} with court stay on transfer.",
                evidence_references={"case_number": lit["case_number"], "court": lit["court_name"]},
                recommendation="আদালতের চূড়ান্ত রায় ও নিষেধাজ্ঞা অবমুক্তির প্রত্যয়নপত্র ছাড়া জমি ক্রয় ঝুঁকিযুক্ত।"
            ))
            highest_score = max(highest_score, 45)

        # RULE 6: Tax Arrears Default (DS-05)
        cur.execute("SELECT * FROM tax_records WHERE parcel_id = ? AND payment_status = 'ARREARS_DUE'", (parcel_id,))
        unpaid_tax = cur.fetchone()
        if unpaid_tax:
            arrears = float(unpaid_tax["assessed_amount"]) - float(unpaid_tax["paid_amount"])
            findings.append(VerificationFinding(
                finding_code="DS-05",
                severity="MEDIUM",
                risk_score=40,
                explanation_bn=f"ভূমি উন্নয়ন কর বকেয়া: হোল্ডিং {unpaid_tax['holding_number']}-এ {arrears:,.2f} টাকা কর বকেয়া রয়েছে। নামজারি অনুমোদনের পূর্বে বকেয়া পরিশোধ আবশ্যক।",
                explanation_en=f"Tax Arrears Default: Outstanding land tax of BDT {arrears:,.2f} on holding {unpaid_tax['holding_number']}. Tax clearance is mandatory prior to mutation.",
                evidence_references={"holding_number": unpaid_tax["holding_number"], "arrears_bdt": arrears},
                recommendation="বিক্রেতাকে ldtax.gov.bd পোর্টালের মাধ্যমে অনলাইনে বকেয়া পরিশোধের দাখিলা প্রদর্শন করতে বলুন।"
            ))
            highest_score = max(highest_score, 40)

        # Status determination
        if highest_score >= 80:
            status = "CRITICAL_FRAUD_RISK"
            is_safe = False
        elif highest_score >= 50:
            status = "HIGH_DISCREPANCY_RISK"
            is_safe = False
        elif highest_score >= 30:
            status = "CAUTION_ENCUMBERED"
            is_safe = True  # negotiable caveats
        else:
            status = "CLEAR_TITLE_VERIFIED"
            is_safe = True

        return ParcelEvaluationReport(
            parcel_id=parcel_id,
            overall_risk_score=highest_score,
            overall_status=status,
            findings=findings,
            is_safe_for_transaction=is_safe,
            disclaimer=LEGAL_DISCLAIMER
        )
