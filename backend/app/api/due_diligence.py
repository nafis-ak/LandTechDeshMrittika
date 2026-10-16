"""
DESHMRITTIKA / BHUMI-SYNC — Buyer Due Diligence Endpoints (P5 Track)
"""

import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from backend.app.database import get_db
from backend.app.schemas.models import DueDiligenceDossier
from backend.app.services.due_diligence import DueDiligenceService

router = APIRouter(prefix="/due-diligence", tags=["Due Diligence"])

@router.get("/{parcel_id}", response_model=DueDiligenceDossier)
def get_due_diligence_report(parcel_id: str, db: sqlite3.Connection = Depends(get_db)):
    dossier = DueDiligenceService.generate_buyer_dossier(db, parcel_id)
    if not dossier:
        raise HTTPException(status_code=404, detail=f"Parcel with ID '{parcel_id}' not found.")
    return dossier
