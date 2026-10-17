"""
DESHMRITTIKA / BHUMI-SYNC — Land Officials Directory API Endpoints (Phase 4)
Database-backed directory of synthetic demonstration land administration officials and offices.
All profiles are strictly fictional and clearly labelled with DEMO OFFICIAL badges.
"""

import sqlite3
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.database import get_db

router = APIRouter(prefix="/officials", tags=["Land Officials Directory"])

DEMO_DISCLAIMER = (
    "DEMO OFFICIAL — NOT A REAL PERSON. This directory contains purely synthetic demonstration "
    "profiles for hackathon evaluation and does not represent actual government personnel or contacts."
)

DESIGNATIONS_CATALOG = [
    {"code": "AC_LAND", "title_en": "Assistant Commissioner (Land)", "title_bn": "সহকারী কমিশনার (ভূমি)"},
    {"code": "KANUNGO", "title_en": "Kanungo", "title_bn": "কানুনগো"},
    {"code": "SURVEYOR", "title_en": "Senior Surveyor", "title_bn": "সার্ভেয়ার"},
    {"code": "ULAO", "title_en": "Union Land Assistant Officer (Tohsildar)", "title_bn": "ইউনিয়ন ভূমি সহকারী কর্মকর্তা"},
    {"code": "ULSAO", "title_en": "Union Land Sub-Assistant Officer", "title_bn": "ইউনিয়ন ভূমি উপ-সহকারী কর্মকর্তা"},
    {"code": "SUB_REGISTRAR", "title_en": "Sub-Registrar", "title_bn": "সাব-রেজিস্ট্রার"},
    {"code": "PESHKAR", "title_en": "Head Assistant cum Peshkar", "title_bn": "প্রধান সহকারী কাম পেশকার"}
]

@router.get("")
def list_officials(
    division_id: Optional[str] = Query(None, description="Filter by Division ID"),
    district_id: Optional[str] = Query(None, description="Filter by District ID"),
    upazila_id: Optional[str] = Query(None, description="Filter by Upazila ID"),
    designation: Optional[str] = Query(None, description="Filter by Designation Code (e.g. AC_LAND, ULAO)"),
    designation_code: Optional[str] = Query(None, description="Filter by Designation Code alias"),
    office_type: Optional[str] = Query(None, description="Filter by Office Type (e.g. AC_LAND_OFFICE, UNION_LAND_OFFICE)"),
    search: Optional[str] = Query(None, description="Search by name, designation, or office"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns synthetic demo land officials matching filters."""
    desig_filter = designation or designation_code
    cur = db.cursor()
    query = """
        SELECT o.official_id, o.name_en, o.name_bn, o.designation_en, o.designation_bn, o.designation_code,
               o.employee_number_demo, o.email_demo, o.phone_demo, o.portrait_image,
               o.jurisdiction_en, o.jurisdiction_bn, o.status, o.provenance,
               off.office_id, off.office_name_en, off.office_name_bn, off.office_type,
               off.address_en, off.address_bn, off.latitude, off.longitude,
               div.name_en as division_name_en, div.name_bn as division_name_bn,
               dist.name_en as district_name_en, dist.name_bn as district_name_bn,
               upz.name_en as upazila_name_en, upz.name_bn as upazila_name_bn
        FROM land_officials o
        JOIN land_offices off ON o.office_id = off.office_id
        JOIN geo_divisions div ON off.division_id = div.division_id
        JOIN geo_districts dist ON off.district_id = dist.district_id
        JOIN geo_upazilas upz ON off.upazila_id = upz.upazila_id
        WHERE 1=1
    """
    params = []

    if division_id:
        query += " AND off.division_id = ?"
        params.append(division_id)
    if district_id:
        query += " AND off.district_id = ?"
        params.append(district_id)
    if upazila_id:
        query += " AND off.upazila_id = ?"
        params.append(upazila_id)
    if desig_filter:
        query += " AND o.designation_code = ?"
        params.append(desig_filter)
    if office_type:
        query += " AND off.office_type = ?"
        params.append(office_type)
    if search:
        search_pat = f"%{search.strip()}%"
        query += """ AND (
            o.name_en LIKE ? OR o.name_bn LIKE ? OR
            o.designation_en LIKE ? OR o.designation_bn LIKE ? OR
            off.office_name_en LIKE ? OR off.office_name_bn LIKE ?
        )"""
        params.extend([search_pat] * 6)

    # Count total
    count_query = f"SELECT COUNT(*) FROM ({query})"
    cur.execute(count_query, params)
    total_count = cur.fetchone()[0]

    # Add sorting and pagination
    query += " ORDER BY o.designation_code ASC, o.name_en ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]

    return {
        "total": total_count,
        "count": len(rows),
        "limit": limit,
        "offset": offset,
        "officials": rows,
        "disclaimer": DEMO_DISCLAIMER
    }

@router.get("/meta/designations")
def get_designation_metadata():
    """Returns the list of supported land administration designations."""
    return {
        "designations": DESIGNATIONS_CATALOG
    }

@router.get("/offices")
def list_offices(
    division_id: Optional[str] = Query(None),
    district_id: Optional[str] = Query(None),
    upazila_id: Optional[str] = Query(None),
    office_type: Optional[str] = Query(None),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns land administration offices with geographical coordinates."""
    cur = db.cursor()
    query = """
        SELECT off.*,
               div.name_en as division_name_en, div.name_bn as division_name_bn,
               dist.name_en as district_name_en, dist.name_bn as district_name_bn,
               upz.name_en as upazila_name_en, upz.name_bn as upazila_name_bn,
               (SELECT COUNT(*) FROM land_officials o WHERE o.office_id = off.office_id) as total_staff
        FROM land_offices off
        JOIN geo_divisions div ON off.division_id = div.division_id
        JOIN geo_districts dist ON off.district_id = dist.district_id
        JOIN geo_upazilas upz ON off.upazila_id = upz.upazila_id
        WHERE 1=1
    """
    params = []
    if division_id:
        query += " AND off.division_id = ?"
        params.append(division_id)
    if district_id:
        query += " AND off.district_id = ?"
        params.append(district_id)
    if upazila_id:
        query += " AND off.upazila_id = ?"
        params.append(upazila_id)
    if office_type:
        query += " AND off.office_type = ?"
        params.append(office_type)

    query += " ORDER BY off.division_id, off.district_id, off.upazila_id, off.office_name_en"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]

    return {
        "total": len(rows),
        "offices": rows,
        "disclaimer": "Demo land administration offices. Contact information is reserved for demonstration."
    }

@router.get("/offices/{office_id}")
def get_office_detail(office_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Returns specific office detail with staff roster."""
    cur = db.cursor()
    cur.execute("""
        SELECT off.*,
               div.name_en as division_name_en, div.name_bn as division_name_bn,
               dist.name_en as district_name_en, dist.name_bn as district_name_bn,
               upz.name_en as upazila_name_en, upz.name_bn as upazila_name_bn
        FROM land_offices off
        JOIN geo_divisions div ON off.division_id = div.division_id
        JOIN geo_districts dist ON off.district_id = dist.district_id
        JOIN geo_upazilas upz ON off.upazila_id = upz.upazila_id
        WHERE off.office_id = ?
    """, (office_id,))
    office = cur.fetchone()
    if not office:
        raise HTTPException(status_code=404, detail="কার্যালয়টি খুঁজে পাওয়া যায়নি (Office not found).")

    # Fetch staff
    cur.execute("""
        SELECT official_id, name_en, name_bn, designation_en, designation_bn, designation_code,
               employee_number_demo, email_demo, phone_demo, portrait_image, jurisdiction_en, jurisdiction_bn, status
        FROM land_officials
        WHERE office_id = ?
        ORDER BY designation_code ASC
    """, (office_id,))
    staff = [dict(s) for s in cur.fetchall()]

    res = dict(office)
    res["staff"] = staff
    res["disclaimer"] = DEMO_DISCLAIMER
    return res

@router.get("/{official_id}")
def get_official_detail(official_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Returns full profile of a single synthetic land official."""
    cur = db.cursor()
    cur.execute("""
        SELECT o.*,
               off.office_name_en, off.office_name_bn, off.office_type,
               off.address_en, off.address_bn, off.latitude, off.longitude,
               div.name_en as division_name_en, div.name_bn as division_name_bn,
               dist.name_en as district_name_en, dist.name_bn as district_name_bn,
               upz.name_en as upazila_name_en, upz.name_bn as upazila_name_bn
        FROM land_officials o
        JOIN land_offices off ON o.office_id = off.office_id
        JOIN geo_divisions div ON off.division_id = div.division_id
        JOIN geo_districts dist ON off.district_id = dist.district_id
        JOIN geo_upazilas upz ON off.upazila_id = upz.upazila_id
        WHERE o.official_id = ?
    """, (official_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="কর্মকর্তার প্রোফাইল খুঁজে পাওয়া যায়নি (Official not found).")

    res = dict(row)
    res["disclaimer"] = DEMO_DISCLAIMER
    return res
