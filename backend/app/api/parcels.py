"""
DESHMRITTIKA / BHUMI-SYNC — Linked Parcel Profile Endpoints
"""

import sqlite3
import json
from fastapi import APIRouter, Depends, HTTPException, Response
from backend.app.database import get_db
from backend.app.schemas.models import ParcelDetail
from backend.app.services.parcel_profile import ParcelProfileService

router = APIRouter(prefix="/parcels", tags=["Parcels"])

@router.get("/{parcel_id}", response_model=ParcelDetail)
def get_parcel_profile(parcel_id: str, db: sqlite3.Connection = Depends(get_db)):
    profile = ParcelProfileService.get_parcel_profile(db, parcel_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Parcel with ID '{parcel_id}' not found.")
    return profile

@router.get("/{parcel_id}/geojson")
def get_parcel_geojson(parcel_id: str, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT coordinates_geojson, parcel_id, mouza, dag_number FROM parcels WHERE parcel_id = ?", (parcel_id,))
    row = cur.fetchone()
    if not row or not row["coordinates_geojson"]:
        raise HTTPException(status_code=404, detail="Parcel geometry not found.")

    geometry = json.loads(row["coordinates_geojson"])
    feature = {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "parcel_id": row["parcel_id"],
            "mouza": row["mouza"],
            "dag_number": row["dag_number"],
            "provenance": "SYNTHETIC_CADASTRAL_VISUALIZATION"
        }
    }
    return Response(content=json.dumps(feature), media_type="application/geo+json")
