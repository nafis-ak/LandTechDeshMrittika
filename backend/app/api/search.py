"""
DESHMRITTIKA / BHUMI-SYNC — Universal Search Endpoints
"""

import sqlite3
from typing import Optional
from fastapi import APIRouter, Depends, Query
from backend.app.database import get_db
from backend.app.schemas.models import SearchResult
from backend.app.services.search import SearchService

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("", response_model=SearchResult)
def search_parcels(
    mouza: Optional[str] = Query(None, description="Cadastral Mouza Name (Aminbazar, Birulia)"),
    dag: Optional[int] = Query(None, description="Survey Plot / Dag Number"),
    khatian: Optional[int] = Query(None, description="Record of Rights / Khatian Number"),
    parcel_id: Optional[str] = Query(None, description="Exact Parcel ID (e.g. BD-PAR-000101)"),
    deed_number: Optional[str] = Query(None, description="Registered Deed Number"),
    owner_name: Optional[str] = Query(None, description="Proprietor Bengali Name"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db)
):
    return SearchService.search_parcels(
        conn=db,
        mouza=mouza,
        dag_number=dag,
        khatian_number=khatian,
        parcel_id=parcel_id,
        deed_number=deed_number,
        owner_name=owner_name,
        limit=limit,
        offset=offset
    )
