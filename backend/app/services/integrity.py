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
    def verify_document_bytes(conn: sqlite3.Connection, file_bytes: bytes, reference_hash: Optional[str] = None) -> DocumentVerifyResponse:
        calculated_hash = hashlib.sha256(file_bytes).hexdigest()
        cur = conn.cursor()

        cur.execute("SELECT * FROM documents WHERE sha256_hash = ?", (calculated_hash,))
        doc = cur.fetchone()

        ref_clean = reference_hash.strip().lower() if reference_hash else None
        calc_clean = calculated_hash.lower()

        if ref_clean:
            if calc_clean == ref_clean:
                comparison_status = "MATCHES_SUPPLIED_REFERENCE"
            else:
                comparison_status = "DOES_NOT_MATCH_SUPPLIED_REFERENCE"
        elif doc:
            comparison_status = "MATCHED_REGISTERED_DOCUMENT"
        else:
            comparison_status = "HASH_CALCULATED_UNREGISTERED"

        if doc:
            return DocumentVerifyResponse(
                is_authentic=True,
                matched_document_id=doc["document_id"],
                parcel_id=doc["parcel_id"],
                deed_id=doc["deed_id"],
                document_type=doc["document_type"],
                status_label="VERIFIED_AUTHENTIC",
                provenance_label=doc["provenance_label"],
                calculated_hash=calculated_hash,
                reference_hash=ref_clean,
                comparison_status=comparison_status
            )
        else:
            return DocumentVerifyResponse(
                is_authentic=bool(ref_clean and calc_clean == ref_clean),
                matched_document_id=None,
                parcel_id=None,
                deed_id=None,
                document_type=None,
                status_label="MATCHES_SUPPLIED_REFERENCE" if (ref_clean and calc_clean == ref_clean) else "TAMPER_DETECTED_OR_UNREGISTERED",
                provenance_label="PUBLIC_CALCULATED_HASH",
                calculated_hash=calculated_hash,
                reference_hash=ref_clean,
                comparison_status=comparison_status
            )

