"""
DESHMRITTIKA / BHUMI-SYNC — Linked Parcel Profile Service
Aggregates parcels, deeds, ownership, mutations, taxes, documents, and litigations.
"""

import sqlite3
from typing import Optional, Dict, Any
from backend.app.schemas.models import ParcelDetail

class ParcelProfileService:

    @staticmethod
    def get_parcel_profile(conn: sqlite3.Connection, parcel_id: str) -> Optional[ParcelDetail]:
        cur = conn.cursor()

        # Parcel core
        cur.execute("SELECT * FROM parcels WHERE parcel_id = ?", (parcel_id,))
        p = cur.fetchone()
        if not p:
            return None

        # Current & Historical Owners
        cur.execute("""
            SELECT po.ownership_id, po.ownership_share, po.valid_from, po.valid_to,
                   o.owner_id, o.fictional_name, o.contact_masked, o.synthetic_nid_hash
            FROM parcel_ownership po
            JOIN owners o ON po.owner_id = o.owner_id
            WHERE po.parcel_id = ?
            ORDER BY po.valid_from DESC
        """, (parcel_id,))
        owners = [dict(r) for r in cur.fetchall()]

        # Registered Deeds
        cur.execute("""
            SELECT d.deed_id, d.deed_number, d.sub_registry_office, d.deed_type,
                   d.execution_date, d.registration_date, d.declared_area, d.deed_value_bdt,
                   d.deed_status,
                   s.fictional_name as seller_name, b.fictional_name as buyer_name
            FROM deeds d
            JOIN owners s ON d.seller_id = s.owner_id
            JOIN owners b ON d.buyer_id = b.owner_id
            WHERE d.parcel_id = ?
            ORDER BY d.registration_date DESC
        """, (parcel_id,))
        deeds = [dict(r) for r in cur.fetchall()]

        # e-Mutation Records
        cur.execute("""
            SELECT m.mutation_id, m.case_number, m.application_date, m.status,
                   m.decision_date, m.mutated_khatian_no,
                   o.fictional_name as applicant_name, d.deed_number
            FROM mutation_records m
            JOIN owners o ON m.applicant_id = o.owner_id
            JOIN deeds d ON m.deed_id = d.deed_id
            WHERE m.parcel_id = ?
            ORDER BY m.application_date DESC
        """, (parcel_id,))
        mutations = [dict(r) for r in cur.fetchall()]

        # Tax Status
        cur.execute("SELECT * FROM tax_records WHERE parcel_id = ? ORDER BY tax_year DESC LIMIT 1", (parcel_id,))
        tax_row = cur.fetchone()
        tax_status = dict(tax_row) if tax_row else None

        # Civil Court Litigations
        cur.execute("SELECT * FROM litigation_records WHERE parcel_id = ?", (parcel_id,))
        litigations = [dict(r) for r in cur.fetchall()]

        # Government Khas status
        cur.execute("SELECT * FROM khas_records WHERE parcel_id = ?", (parcel_id,))
        khas_row = cur.fetchone()
        khas_status = dict(khas_row) if khas_row else None

        # Verification Cases
        cur.execute("SELECT * FROM verification_cases WHERE parcel_id = ? ORDER BY risk_score DESC", (parcel_id,))
        vcases = [dict(r) for r in cur.fetchall()]

        return ParcelDetail(
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
            provenance_label=p["provenance_label"],
            coordinates_geojson=p["coordinates_geojson"],
            current_owners=owners,
            historical_deeds=deeds,
            mutations=mutations,
            tax_status=tax_status,
            litigations=litigations,
            khas_status=khas_status,
            verification_cases=vcases
        )
