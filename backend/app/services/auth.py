"""
DESHMRITTIKA / BHUMI-SYNC — Role-Based Access Control & Session Management
Server-side enforced roles: CITIZEN, BUYER, OFFICER, ADMINISTRATOR.
Tracks active sessions, checks revocation, verifies account status, and logs security events.
"""

import hmac
import hashlib
import base64
import json
import time
import uuid
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import Header, HTTPException, Depends, Request

from backend.app.config import SECRET_KEY
from backend.app.database import get_db, get_db_connection
from backend.app.services.crypto import CryptoService

# Helper to log security events
def log_security_event(
    db: sqlite3.Connection,
    user_id: Optional[str],
    actor_email: str,
    action: str,
    details: Dict[str, Any],
    ip_address: str = ""
):
    """Persists security audit log in SQLite."""
    try:
        cur = db.cursor()
        log_id = f"SEC-{uuid.uuid4().hex[:12].upper()}"
        now_ts = datetime.now(timezone.utc).isoformat()
        cur.execute("""
        INSERT INTO security_audit_logs (log_id, user_id, actor_email, action, ip_address, details_json, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (log_id, user_id, actor_email, action, ip_address, json.dumps(details, ensure_ascii=False), now_ts))
        db.commit()
    except Exception as e:
        print(f"[Security Log Error]: {e}")


def create_user_session(
    user_data: Dict[str, Any],
    db: sqlite3.Connection,
    remember_me: bool = False,
    ip_address: str = "",
    user_agent: str = ""
) -> str:
    """Creates a persistent session in user_sessions and returns HMAC-signed session token."""
    session_id = f"SES-{uuid.uuid4().hex[:16]}"
    duration = 30 * 86400 if remember_me else 86400  # 30 days vs 24 hours
    expires_at = int(time.time()) + duration

    payload = {
        "session_id": session_id,
        "user_id": user_data["user_id"],
        "email": user_data["email"],
        "name": user_data.get("full_name") or user_data.get("name", "User"),
        "role": user_data["role"],
        "status": user_data.get("status", "ACTIVE"),
        "exp": expires_at
    }

    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode('utf-8').rstrip('=')

    sig = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode('utf-8').rstrip('=')
    token = f"{payload_b64}.{sig_b64}"

    # Store token hash in user_sessions table
    token_hash = CryptoService.hash_token(token)
    now_ts = datetime.now(timezone.utc).isoformat()
    exp_iso = datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat()

    cur = db.cursor()
    cur.execute("""
    INSERT INTO user_sessions (session_id, user_id, token_hash, ip_address, user_agent, expires_at, is_revoked, created_at)
    VALUES (?, ?, ?, ?, ?, ?, 0, ?)
    """, (session_id, user_data["user_id"], token_hash, ip_address, user_agent, exp_iso, now_ts))
    db.commit()

    return token


def create_session_token(email: str, user_data: Dict[str, Any]) -> str:
    """Stateless fallback session generator for testing compatibility."""
    conn = get_db_connection()
    try:
        token = create_user_session(user_data, conn)
        return token
    finally:
        conn.close()


def verify_session_token(token: str, db: Optional[sqlite3.Connection] = None) -> Optional[Dict[str, Any]]:
    """Verifies HMAC signature, expiry, revocation status, and user active status."""
    try:
        parts = token.split('.')
        if len(parts) != 2:
            return None
        payload_b64, sig_b64 = parts

        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode('utf-8').rstrip('=')

        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return None

        # Pad base64 if needed
        padding = 4 - (len(payload_b64) % 4)
        if padding != 4:
            payload_b64 += '=' * padding

        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8'))
        if payload.get("exp", 0) < int(time.time()):
            return None

        # Check DB session revocation and user status if DB connection available
        if db is not None:
            token_hash = CryptoService.hash_token(token)
            cur = db.cursor()
            cur.execute("""
            SELECT s.is_revoked, u.status, u.role, u.full_name
            FROM user_sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.token_hash = ?
            """, (token_hash,))
            row = cur.fetchone()
            if row:
                if row["is_revoked"] == 1:
                    return None  # Revoked session
                if row["status"] != "ACTIVE":
                    return None  # Unverified or suspended
                # Ensure latest role & name from database
                payload["role"] = row["role"]
                payload["name"] = row["full_name"]
                payload["status"] = row["status"]

        return payload
    except Exception:
        return None


def revoke_session(token: str, db: sqlite3.Connection):
    """Marks single session as revoked."""
    token_hash = CryptoService.hash_token(token)
    cur = db.cursor()
    cur.execute("UPDATE user_sessions SET is_revoked = 1 WHERE token_hash = ?", (token_hash,))
    db.commit()


def revoke_all_user_sessions(user_id: str, db: sqlite3.Connection):
    """Marks all sessions of a user as revoked."""
    cur = db.cursor()
    cur.execute("UPDATE user_sessions SET is_revoked = 1 WHERE user_id = ?", (user_id,))
    db.commit()


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: sqlite3.Connection = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """Optional authentication: extracts user if token is present and valid."""
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").strip()
    return verify_session_token(token, db)


def require_authenticated_user(
    authorization: Optional[str] = Header(None),
    db: sqlite3.Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Requires valid, non-revoked session token of an active account."""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required: missing Authorization header."
        )
    token = authorization.replace("Bearer ", "").strip()
    user = verify_session_token(token, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: invalid, revoked, or expired session token."
        )
    return user


def require_role(allowed_roles: List[str]):
    """Returns dependency enforcing one of the allowed roles."""
    def role_checker(user: Dict[str, Any] = Depends(require_authenticated_user)) -> Dict[str, Any]:
        role = user.get("role")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: Role '{role}' lacks required permission for this operation."
            )
        return user
    return role_checker


def require_officer_role(user: Dict[str, Any] = Depends(require_authenticated_user)) -> Dict[str, Any]:
    """Server-side permission guard: restricts access strictly to OFFICER role (Separation of Duties)."""
    role = user.get("role")
    if role != "OFFICER":
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: Role '{role}' lacks authorized officer review permissions."
        )
    return user


def require_admin_role(user: Dict[str, Any] = Depends(require_authenticated_user)) -> Dict[str, Any]:
    """Server-side permission guard: restricts access exclusively to ADMINISTRATOR role."""
    role = user.get("role")
    if role != "ADMINISTRATOR":
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: Role '{role}' lacks platform administration privileges."
        )
    return user
