"""
DESHMRITTIKA / BHUMI-SYNC — Administrative Geography API Endpoints (Phase 2)
Provides normalized Bangladesh administrative hierarchy:
Divisions (8) -> Districts (64) -> Upazilas (501) -> Unions -> Mouzas with JL numbers.
"""

import sqlite3
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.database import get_db

router = APIRouter(prefix="/geography", tags=["Administrative Geography"])

@router.get("/divisions")
def get_divisions(db: sqlite3.Connection = Depends(get_db)):
    """Returns all 8 administrative divisions of Bangladesh."""
    cur = db.cursor()
    cur.execute("""
        SELECT division_id, bbs_code, name_en, name_bn, latitude, longitude, source_ref
        FROM geo_divisions
        ORDER BY bbs_code ASC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    return {
        "total": len(rows),
        "divisions": rows,
        "disclaimer": "Official BBS Administrative Divisions of Bangladesh."
    }

@router.get("/districts")
def get_districts(
    division_id: Optional[str] = Query(None, description="Filter by Division ID (e.g. DIV-30 for Dhaka)"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns all 64 districts or districts belonging to a specific division."""
    cur = db.cursor()
    if division_id:
        cur.execute("""
            SELECT district_id, division_id, bbs_code, name_en, name_bn, latitude, longitude, source_ref
            FROM geo_districts
            WHERE division_id = ?
            ORDER BY name_en ASC
        """, (division_id,))
    else:
        cur.execute("""
            SELECT district_id, division_id, bbs_code, name_en, name_bn, latitude, longitude, source_ref
            FROM geo_districts
            ORDER BY division_id ASC, name_en ASC
        """)
    rows = [dict(r) for r in cur.fetchall()]
    return {
        "division_id": division_id,
        "total": len(rows),
        "districts": rows
    }

@router.get("/upazilas")
def get_upazilas(
    district_id: Optional[str] = Query(None, description="Filter by District ID (e.g. DIST-26 for Dhaka)"),
    limit: int = Query(100, ge=1, le=600),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns upazilas/thanas, optionally filtered by district."""
    cur = db.cursor()
    if district_id:
        cur.execute("""
            SELECT upazila_id, district_id, bbs_code, name_en, name_bn, latitude, longitude, source_ref
            FROM geo_upazilas
            WHERE district_id = ?
            ORDER BY name_en ASC
            LIMIT ? OFFSET ?
        """, (district_id, limit, offset))
    else:
        cur.execute("""
            SELECT upazila_id, district_id, bbs_code, name_en, name_bn, latitude, longitude, source_ref
            FROM geo_upazilas
            ORDER BY district_id ASC, name_en ASC
            LIMIT ? OFFSET ?
        """, (limit, offset))
    rows = [dict(r) for r in cur.fetchall()]

    # Total count
    if district_id:
        cur.execute("SELECT COUNT(*) FROM geo_upazilas WHERE district_id = ?", (district_id,))
    else:
        cur.execute("SELECT COUNT(*) FROM geo_upazilas")
    total_count = cur.fetchone()[0]

    return {
        "district_id": district_id,
        "total": total_count,
        "count": len(rows),
        "limit": limit,
        "offset": offset,
        "upazilas": rows
    }

@router.get("/unions")
def get_unions(
    upazila_id: Optional[str] = Query(None, description="Filter by Upazila ID (e.g. UPZ-2672 for Savar)"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns unions/municipalities for an upazila."""
    cur = db.cursor()
    if upazila_id:
        cur.execute("""
            SELECT union_id, upazila_id, bbs_code, name_en, name_bn, source_ref
            FROM geo_unions
            WHERE upazila_id = ?
            ORDER BY name_en ASC
        """, (upazila_id,))
    else:
        cur.execute("""
            SELECT union_id, upazila_id, bbs_code, name_en, name_bn, source_ref
            FROM geo_unions
            ORDER BY upazila_id ASC, name_en ASC
        """)
    rows = [dict(r) for r in cur.fetchall()]
    return {
        "upazila_id": upazila_id,
        "total": len(rows),
        "unions": rows,
        "coverage_note": "Unions are populated for pilot and major upazilas; additional areas will be added as verified government gazettes are ingested."
    }

@router.get("/mouzas")
def get_mouzas(
    upazila_id: Optional[str] = Query(None, description="Filter by Upazila ID"),
    union_id: Optional[str] = Query(None, description="Filter by Union ID"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns mouzas with JL numbers and cadastral survey readiness flags."""
    cur = db.cursor()
    query = """
        SELECT m.mouza_id, m.upazila_id, m.union_id, m.name_en, m.name_bn, m.jl_number,
               m.has_cadastral_survey, m.has_boundary_polygon, m.source_ref,
               u.name_en as upazila_name_en, u.name_bn as upazila_name_bn,
               d.name_en as district_name_en, d.name_bn as district_name_bn
        FROM geo_mouzas m
        JOIN geo_upazilas u ON m.upazila_id = u.upazila_id
        JOIN geo_districts d ON u.district_id = d.district_id
        WHERE 1=1
    """
    params = []
    if upazila_id:
        query += " AND m.upazila_id = ?"
        params.append(upazila_id)
    if union_id:
        query += " AND m.union_id = ?"
        params.append(union_id)

    query += " ORDER BY m.name_en ASC"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    return {
        "upazila_id": upazila_id,
        "union_id": union_id,
        "total": len(rows),
        "coverage_status": "COMPLETE_PILOT" if len(rows) > 0 else "INCOMPLETE_OFFICIAL_DATA",
        "mouzas": rows,
        "disclaimer": "Administrative mouza directory records presence and JL number. Cadastral polygon boundaries are available where has_boundary_polygon=1."
    }

@router.get("/search")
def search_geography(
    q: str = Query(..., min_length=2, description="Search term in Bengali or English"),
    limit: int = Query(20, ge=1, le=100),
    db: sqlite3.Connection = Depends(get_db)
):
    """Universal search across Divisions, Districts, Upazilas, Unions, and Mouzas."""
    cur = db.cursor()
    search_pat = f"%{q.strip()}%"
    results: List[Dict[str, Any]] = []

    # 1. Search Divisions
    cur.execute("""
        SELECT division_id as id, name_en, name_bn, 'DIVISION' as level,
               latitude, longitude, name_en as display_name
        FROM geo_divisions
        WHERE name_en LIKE ? OR name_bn LIKE ?
        LIMIT ?
    """, (search_pat, search_pat, limit))
    results.extend([dict(r) for r in cur.fetchall()])

    # 2. Search Districts
    cur.execute("""
        SELECT d.district_id as id, d.name_en, d.name_bn, 'DISTRICT' as level,
               d.latitude, d.longitude,
               d.name_en || ', ' || div.name_en as display_name,
               div.name_en as division_name_en, div.name_bn as division_name_bn
        FROM geo_districts d
        JOIN geo_divisions div ON d.division_id = div.division_id
        WHERE d.name_en LIKE ? OR d.name_bn LIKE ?
        LIMIT ?
    """, (search_pat, search_pat, limit))
    results.extend([dict(r) for r in cur.fetchall()])

    # 3. Search Upazilas
    cur.execute("""
        SELECT u.upazila_id as id, u.name_en, u.name_bn, 'UPAZILA' as level,
               u.latitude, u.longitude,
               u.name_en || ', ' || dist.name_en || ', ' || div.name_en as display_name,
               dist.name_en as district_name_en, dist.name_bn as district_name_bn,
               div.name_en as division_name_en, div.name_bn as division_name_bn
        FROM geo_upazilas u
        JOIN geo_districts dist ON u.district_id = dist.district_id
        JOIN geo_divisions div ON dist.division_id = div.division_id
        WHERE u.name_en LIKE ? OR u.name_bn LIKE ?
        LIMIT ?
    """, (search_pat, search_pat, limit))
    results.extend([dict(r) for r in cur.fetchall()])

    # 4. Search Mouzas
    cur.execute("""
        SELECT m.mouza_id as id, m.name_en, m.name_bn, 'MOUZA' as level,
               u.latitude, u.longitude,
               m.name_en || ' (JL: ' || m.jl_number || '), ' || u.name_en || ', ' || dist.name_en as display_name,
               m.jl_number, m.has_boundary_polygon,
               u.name_en as upazila_name_en, u.name_bn as upazila_name_bn,
               dist.name_en as district_name_en, dist.name_bn as district_name_bn
        FROM geo_mouzas m
        JOIN geo_upazilas u ON m.upazila_id = u.upazila_id
        JOIN geo_districts dist ON u.district_id = dist.district_id
        WHERE m.name_en LIKE ? OR m.name_bn LIKE ?
        LIMIT ?
    """, (search_pat, search_pat, limit))
    results.extend([dict(r) for r in cur.fetchall()])

    return {
        "query": q,
        "total_matches": len(results),
        "results": results[:limit]
    }
