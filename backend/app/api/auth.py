"""
DESHMRITTIKA / BHUMI-SYNC — Auth Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from backend.app.schemas.models import LoginRequest, TokenResponse
from backend.app.config import DEMO_USERS
from backend.app.services.auth import create_session_token, require_authenticated_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    email = req.email.strip().lower()
    if email not in DEMO_USERS:
        raise HTTPException(status_code=401, detail="Invalid demo credentials. Use documented demo accounts.")

    user_info = DEMO_USERS[email]
    token = create_session_token(email, user_info)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user_info["user_id"],
        name=user_info["name"],
        role=user_info["role"]
    )

@router.get("/me")
def get_me(user: dict = Depends(require_authenticated_user)):
    return user
