"""
DESHMRITTIKA / BHUMI-SYNC — Document Integrity & OCR Endpoints (P1 & P2 Tracks)
"""

import sqlite3
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from backend.app.database import get_db
from backend.app.schemas.models import DocumentVerifyResponse
from backend.app.services.integrity import CryptographicIntegrityService
from backend.app.services.ocr import DocumentOCRService

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/verify-integrity", response_model=DocumentVerifyResponse)
async def verify_document_integrity(
    file: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db)
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    return CryptographicIntegrityService.verify_document_bytes(db, content)

@router.post("/upload-ocr")
async def upload_document_ocr(
    file: UploadFile = File(...)
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    result = DocumentOCRService.process_document(content, file.filename or "uploaded.png")
    return result
