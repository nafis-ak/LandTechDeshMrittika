"""
DESHMRITTIKA / BHUMI-SYNC — Smart e-Mutation Bridge Service (P4 Track)
Bridges Sub-Registry deed registration to AC Land e-mutation workflow.
"""

import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from backend.app.schemas.models import MutationPreCheckResponse

class MutationBridgeService:

    @staticmethod
    def run_pre_check(conn: sqlite3.Connection, parcel_id: str, deed_id: str, applicant_id: str) -> MutationPreCheckResponse:
        cur = conn.cursor()

        rejection_reasons = []

        # 1. Check Khas status
        cur.execute("SELECT * FROM khas_records WHERE parcel_id = ?", (parcel_id,))
        is_khas = (cur.fetchone() is not None)
        if is_khas:
            rejection_reasons.append("সরকারি ১নং খাস জমি ব্যক্তিমালিকানায় নামজারিযোগ্য নয় (Khas land is legally non-mutable to private parties).")

        # 2. Check Tax arrears
        cur.execute("SELECT payment_status, assessed_amount, paid_amount FROM tax_records WHERE parcel_id = ? ORDER BY tax_year DESC LIMIT 1", (parcel_id,))
        tax_row = cur.fetchone()
        has_tax_arrears = False
        if tax_row and tax_row[0] == "ARREARS_DUE":
            has_tax_arrears = True
            rejection_reasons.append("বকেয়া ভূমি উন্নয়ন কর অপরিশোধিত রয়েছে (Outstanding LDTax arrears must be cleared).")

        # 3. Check Active Injunction
        cur.execute("SELECT * FROM litigation_records WHERE parcel_id = ? AND status = 'ACTIVE_INJUNCTION_STAY'", (parcel_id,))
        has_injunction = (cur.fetchone() is not None)
        if has_injunction:
            rejection_reasons.append("আদালতের সক্রিয় স্থগিতাদেশ বা নিষেধাজ্ঞা বলবৎ রয়েছে (Active civil court stay in effect).")

        # 4. Check Competing unmutated deed (Double-selling risk)
        cur.execute("""
            SELECT d.deed_number FROM deeds d
            JOIN deeds curr ON d.parcel_id = curr.parcel_id AND d.seller_id = curr.seller_id AND d.deed_id != curr.deed_id
            WHERE curr.deed_id = ?
              AND d.deed_id IN (SELECT deed_id FROM mutation_records WHERE status != 'APPROVED')
        """, (deed_id,))
        competing = cur.fetchall()
        has_competing = len(competing) > 0
        if has_competing:
            rejection_reasons.append(f"একই বিক্রেতা কর্তৃক পূর্ববর্তী অনিষ্পন্ন দলিল ({competing[0][0]}) বিদ্যমান — দ্বৈত বিক্রয় সংক্রান্ত জটিলতা।")

        can_proceed = (len(rejection_reasons) == 0)
        summary_bn = "সকল স্বয়ংক্রিয় প্রাক-যাচাই সফল। ই-নামজারি নথি অনুমোদনের জন্য প্রস্তুত।" if can_proceed else "স্বয়ংক্রিয় প্রাক-যাচাইয়ে আপত্তি পাওয়া গেছে।"

        return MutationPreCheckResponse(
            can_proceed=can_proceed,
            tax_arrears=has_tax_arrears,
            active_injunction=has_injunction,
            is_khas_land=is_khas,
            competing_unmutated_deed=has_competing,
            rejection_reasons=rejection_reasons,
            precheck_summary_bn=summary_bn
        )

    @staticmethod
    def update_mutation_status(conn: sqlite3.Connection, mutation_id: str, new_status: str, officer_id: str) -> bool:
        cur = conn.cursor()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        cur.execute("SELECT * FROM mutation_records WHERE mutation_id = ?", (mutation_id,))
        record = cur.fetchone()
        if not record:
            return False

        if new_status == "APPROVED":
            mutated_khatian = 6000 + int(mutation_id.split("-")[-1])
            cur.execute("""
                UPDATE mutation_records
                SET status = 'APPROVED', decision_date = ?, mutated_khatian_no = ?
                WHERE mutation_id = ?
            """, (now, mutated_khatian, mutation_id))
            # Also update linked transaction
            cur.execute("""
                UPDATE transactions
                SET mutation_link_status = 'MUTATED'
                WHERE deed_id = ?
            """, (record["deed_id"],))
        else:
            cur.execute("""
                UPDATE mutation_records
                SET status = ?
                WHERE mutation_id = ?
            """, (new_status, mutation_id))

        conn.commit()
        return True
