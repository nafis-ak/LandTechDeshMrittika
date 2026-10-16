"""
DESHMRITTIKA / BHUMI-SYNC — Role-Based Access Control & Authentication
Server-side enforced roles: CITIZEN, BUYER, OFFICER, ADMINISTRATOR.
"""

import hmac
import hashlib
import base64
import json
import time
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, Depends
from backend.app.config import SECRET_KEY, DEMO_USERS

def create_session_token(email: str, user_data: Dict[str, Any]) -> str:
    """Generates an HMAC-signed token encoding user credentials and role."""
    payload = {
        "email": email,
        "user_id": user_data["user_id"],
        "name": user_data["name"],
        "role": user_data["role"],
        "exp": int(time.time()) + 86400  # 24 hours
    }
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode('utf-8').rstrip('=')

    sig = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode('utf-8').rstrip('=')

    return f"{payload_b64}.{sig_b64}"

def verify_session_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies HMAC signature and expiration of session token."""
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

        return payload
    except Exception:
        return None

def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Optional authentication: extracts user if token is present."""
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").strip()
    return verify_session_token(token)

def require_authenticated_user(authorization: str = Header(...)) -> Dict[str, Any]:
    """Requires valid session token."""
    token = authorization.replace("Bearer ", "").strip()
    user = verify_session_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed: invalid or expired session token.")
    return user

def require_officer_role(user: Dict[str, Any] = Depends(require_authenticated_user)) -> Dict[str, Any]:
    """Server-side permission guard: restricts access to OFFICER and ADMINISTRATOR roles."""
    role = user.get("role")
    if role not in ["OFFICER", "ADMINISTRATOR"]:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: Role '{role}' lacks authorized officer review permissions."
        )
    return user
