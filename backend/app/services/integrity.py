"""
DESHMRITTIKA / BHUMI-SYNC — Cryptographic Integrity Service (P2 Track)
SHA-256 Checksum computation, tamper detection, and QR verification.
"""

import sqlite3
import hashlib
from typing import Optional
from backend.app.schemas.models import DocumentVerifyResponse

class CryptographicIntegrityService:

    @staticmethod
    def calculate_sha256(file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    @staticmethod
    def verify_document_bytes(conn: sqlite3.Connection, file_bytes: bytes) -> DocumentVerifyResponse:
        calculated_hash = hashlib.sha256(file_bytes).hexdigest()
        cur = conn.cursor()

        cur.execute("SELECT * FROM documents WHERE sha256_hash = ?", (calculated_hash,))
        doc = cur.fetchone()

        if doc:
            return DocumentVerifyResponse(
                is_authentic=True,
                matched_document_id=doc["document_id"],
                parcel_id=doc["parcel_id"],
                deed_id=doc["deed_id"],
                document_type=doc["document_type"],
                status_label="VERIFIED_AUTHENTIC",
                provenance_label=doc["provenance_label"]
            )
        else:
            return DocumentVerifyResponse(
                is_authentic=False,
                matched_document_id=None,
                parcel_id=None,
                deed_id=None,
                document_type=None,
                status_label="TAMPER_DETECTED_OR_UNREGISTERED",
                provenance_label="UNKNOWN_OR_MODIFIED_DOCUMENT"
            )
