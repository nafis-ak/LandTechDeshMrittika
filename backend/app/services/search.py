"""
DESHMRITTIKA / BHUMI-SYNC — Universal Search Service
Supports queries by Dag, Khatian, Mouza, Deed Number, and Owner Name.
"""

import sqlite3
from typing import List, Optional, Dict, Any
from backend.app.schemas.models import ParcelSummary, SearchResult

class SearchService:

    @staticmethod
    def search_parcels(
        conn: sqlite3.Connection,
        mouza: Optional[str] = None,
        dag_number: Optional[int] = None,
        khatian_number: Optional[int] = None,
        parcel_id: Optional[str] = None,
        deed_number: Optional[str] = None,
        owner_name: Optional[str] = None,
        survey_type: Optional[str] = None,
        district: Optional[str] = None,
        upazila: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> SearchResult:
        cur = conn.cursor()

        query_parts = ["SELECT p.* FROM parcels p"]
        conditions = []
        params = []

        # Join deeds if searching by deed_number
        if deed_number:
            query_parts.append("JOIN deeds d ON p.parcel_id = d.parcel_id")
            conditions.append("d.deed_number LIKE ?")
            params.append(f"%{deed_number}%")

        # Join owners if searching by owner_name
        if owner_name:
            query_parts.append("""
                JOIN parcel_ownership po ON p.parcel_id = po.parcel_id
                JOIN owners o ON po.owner_id = o.owner_id
            """)
            conditions.append("o.fictional_name LIKE ?")
            params.append(f"%{owner_name}%")

        if parcel_id:
            conditions.append("p.parcel_id = ?")
            params.append(parcel_id.strip())

        if district:
            conditions.append("p.district LIKE ?")
            params.append(f"%{district.strip()}%")

        if upazila:
            conditions.append("p.upazila LIKE ?")
            params.append(f"%{upazila.strip()}%")

        if mouza:
            conditions.append("p.mouza LIKE ?")
            params.append(f"%{mouza.strip()}%")

        if survey_type:
            conditions.append("p.survey_type = ?")
            params.append(survey_type.strip().upper())

        if dag_number:
            conditions.append("p.dag_number = ?")
            params.append(dag_number)

        if khatian_number:
            conditions.append("p.khatian_number = ?")
            params.append(khatian_number)

        base_query = " ".join(query_parts)
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)


        # Count total
        count_query = f"SELECT COUNT(DISTINCT parcel_id) FROM ({base_query}) AS sub"
        cur.execute(count_query, params)
        total_matches = cur.fetchone()[0]

        # Fetch limited records
        paginated_query = f"{base_query} GROUP BY p.parcel_id ORDER BY p.parcel_id LIMIT ? OFFSET ?"
        cur.execute(paginated_query, params + [limit, offset])
        rows = cur.fetchall()

        parcels: List[ParcelSummary] = []
        for r in rows:
            parcels.append(ParcelSummary(
                parcel_id=r["parcel_id"],
                district=r["district"],
                upazila=r["upazila"],
                mouza=r["mouza"],
                jl_number=r["jl_number"],
                dag_number=r["dag_number"],
                khatian_number=r["khatian_number"],
                survey_type=r["survey_type"],
                land_classification=r["land_classification"],
                area_decimal=float(r["area_decimal"]),
                is_disputed=bool(r["is_disputed"]),
                provenance_label=r["provenance_label"]
            ))

        return SearchResult(total_matches=total_matches, parcels=parcels)
