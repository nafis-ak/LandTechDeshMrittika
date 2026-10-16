"""
DESHMRITTIKA / BHUMI-SYNC — Smart e-Mutation Endpoints (P4 Track)
"""

import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from backend.app.database import get_db
from backend.app.schemas.models import MutationPreCheckRequest, MutationPreCheckResponse
from backend.app.services.mutation import MutationBridgeService
from backend.app.services.auth import require_officer_role

router = APIRouter(prefix="/mutations", tags=["e-Mutation"])

@router.post("/pre-check", response_model=MutationPreCheckResponse)
def pre_check_mutation(req: MutationPreCheckRequest, db: sqlite3.Connection = Depends(get_db)):
    return MutationBridgeService.run_pre_check(
        conn=db,
        parcel_id=req.parcel_id,
        deed_id=req.deed_id,
        applicant_id=req.applicant_id
    )

@router.post("/{mutation_id}/status")
def update_mutation_status(
    mutation_id: str,
    new_status: str,
    officer: dict = Depends(require_officer_role),
    db: sqlite3.Connection = Depends(get_db)
):
    valid_statuses = ['SUBMITTED', 'ULAO_INSPECTION', 'HEARING_DCR_PENDING', 'APPROVED', 'REJECTED']
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status '{new_status}'. Allowed: {valid_statuses}")

    success = MutationBridgeService.update_mutation_status(db, mutation_id, new_status, officer["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail=f"Mutation record '{mutation_id}' not found.")

    return {"status": "SUCCESS", "mutation_id": mutation_id, "updated_to": new_status, "officer": officer["user_id"]}
