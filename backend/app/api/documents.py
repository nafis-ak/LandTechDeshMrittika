"""
DESHMRITTIKA / BHUMI-SYNC — Document Integrity & OCR Endpoints (P1 & P2 Tracks)
"""

import sqlite3
from typing import Optional
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
    file: UploadFile = File(...),
    preprocess_mode: str = Form("enhance_contrast"),
    rotate_deg: int = Form(0),
    lang_override: Optional[str] = Form(None)
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    result = DocumentOCRService.process_document(
        file_bytes=content,
        filename=file.filename or "uploaded.png",
        preprocess_mode=preprocess_mode,
        rotate_deg=rotate_deg,
        lang_override=lang_override
    )
    return result

@router.get("/sample-deed")
def get_sample_deed():
    from fastapi.responses import FileResponse
    from backend.app.config import BASE_DIR
    sample_path = BASE_DIR / "frontend" / "assets" / "samples" / "sample_deed_authentic.png"
    if sample_path.exists():
        return FileResponse(str(sample_path), media_type="image/png", filename="sample_deed_authentic.png")
    raise HTTPException(status_code=404, detail="Sample deed not found")

@router.get("/sample-pdf")
def get_sample_pdf():
    from fastapi.responses import FileResponse
    from backend.app.config import BASE_DIR
    sample_path = BASE_DIR / "frontend" / "assets" / "samples" / "sample_khatian.pdf"
    if sample_path.exists():
        return FileResponse(str(sample_path), media_type="application/pdf", filename="sample_khatian.pdf")
    raise HTTPException(status_code=404, detail="Sample PDF not found")

