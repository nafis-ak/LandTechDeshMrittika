"""
DESHMRITTIKA / BHUMI-SYNC — Authentication & Four-Role Identity Endpoints
Implements Signup, Email Verification (OTP), Login, Password Reset,
Session Invalidation, Profile Management, and Security Auditing.
"""

import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Query

from backend.app.database import get_db
from backend.app.config import SECRET_KEY
from backend.app.schemas.models import (
    TokenResponse,
    LoginRequest,
    SignupRequest,
    VerifyEmailRequest,
    ResendCodeRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    UserProfile
)
from backend.app.services.crypto import CryptoService
from backend.app.services.email import EmailService, DevMailbox
from backend.app.services.auth import (
    create_user_session,
    verify_session_token,
    revoke_session,
    revoke_all_user_sessions,
    require_authenticated_user,
    log_security_event
)

router = APIRouter(prefix="/auth", tags=["Authentication & Security"])


# ============================================================================
# 1. SIGNUP & EMAIL VERIFICATION
# ============================================================================

@router.post("/signup")
def signup(req: SignupRequest, request: Request, db: sqlite3.Connection = Depends(get_db)):
    """Registers a new citizen or buyer account with an UNVERIFIED status and sends 6-digit OTP."""
    email = req.email.strip().lower()
    full_name = req.full_name.strip()

    # 1. Validate inputs
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="সঠিক ইমেইল ঠিকানা প্রদান করুন।")
    if len(full_name) < 2:
        raise HTTPException(status_code=400, detail="পূর্ণ নাম প্রদান করুন।")
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="পাসওয়ার্ড কমপক্ষে ৮ অক্ষরের হতে হবে।")
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="পাসওয়ার্ড এবং কনফার্ম পাসওয়ার্ড মিলছে না।")

    # 2. Prevent unauthorized public role escalation
    requested_role = (req.role or "CITIZEN").upper().strip()
    if requested_role in ["OFFICER", "ADMINISTRATOR"]:
        raise HTTPException(
            status_code=403,
            detail="সহকারী কমিশনার (ভূমি) বা অ্যাডমিন পদে সরাসরি পাবলিক সাইন-আপ নিষিদ্ধ। শুধুমাত্র অনুমোদিত প্রশাসনিক প্রক্রিয়ায় এই অ্যাকাউন্ট খোলা যায়।"
        )
    if requested_role not in ["CITIZEN", "BUYER"]:
        requested_role = "CITIZEN"

    # 3. Check duplicate email
    cur = db.cursor()
    cur.execute("SELECT user_id, status FROM users WHERE email = ?", (email,))
    existing = cur.fetchone()
    if existing:
        if existing["status"] == "UNVERIFIED":
            # Re-issue OTP for unverified user instead of blocking
            otp_code = CryptoService.generate_numeric_otp(6)
            otp_hash = CryptoService.hash_otp(otp_code, SECRET_KEY)
            now = datetime.now(timezone.utc)
            expires_at = (now + timedelta(minutes=10)).isoformat()
            resend_at = (now + timedelta(seconds=60)).isoformat()

            cur.execute("""
            INSERT INTO auth_challenges (challenge_id, email, user_id, purpose, code_hash, expires_at, attempts, resend_available_at, created_at)
            VALUES (?, ?, ?, 'EMAIL_VERIFY', ?, ?, 0, ?, ?)
            """, (f"CHAL-{uuid.uuid4().hex[:12]}", email, existing["user_id"], otp_hash, expires_at, resend_at, now.isoformat()))
            db.commit()

            EmailService.send_verification_otp(email, full_name, otp_code)
            return {
                "success": True,
                "email": email,
                "status": "UNVERIFIED",
                "message": "অ্যাকাউন্টটি অনিষ্পন্ন রয়েছে। নতুন যাচাইকরণ ওটিপি আপনার ইমেইলে পাঠানো হয়েছে।"
            }
        raise HTTPException(status_code=400, detail="এই ইমেইল দিয়ে ইতোমধ্যে একটি অ্যাকাউন্ট নিবন্ধিত রয়েছে। লগইন করুন।")

    # 4. Hash password and persist unverified account
    user_id = f"USR-{uuid.uuid4().hex[:10].upper()}"
    pwd_hash = CryptoService.hash_password(req.password)
    now_ts = datetime.now(timezone.utc).isoformat()

    cur.execute("""
    INSERT INTO users (user_id, email, password_hash, full_name, phone, role, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, 'UNVERIFIED', ?, ?)
    """, (user_id, email, pwd_hash, full_name, req.phone or "", requested_role, now_ts, now_ts))

    # 5. Generate and store 6-digit OTP challenge
    otp_code = CryptoService.generate_numeric_otp(6)
    otp_hash = CryptoService.hash_otp(otp_code, SECRET_KEY)
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(minutes=10)).isoformat()
    resend_at = (now + timedelta(seconds=60)).isoformat()

    cur.execute("""
    INSERT INTO auth_challenges (challenge_id, email, user_id, purpose, code_hash, expires_at, attempts, resend_available_at, created_at)
    VALUES (?, ?, ?, 'EMAIL_VERIFY', ?, ?, 0, ?, ?)
    """, (f"CHAL-{uuid.uuid4().hex[:12]}", email, user_id, otp_hash, expires_at, resend_at, now_ts))

    db.commit()

    # 6. Dispatch email and log security event
    EmailService.send_verification_otp(email, full_name, otp_code)
    ip_addr = request.client.host if request.client else ""
    log_security_event(db, user_id, email, "SIGNUP_INIT", {"role": requested_role}, ip_addr)

    return {
        "success": True,
        "email": email,
        "role": requested_role,
        "status": "UNVERIFIED",
        "message": "অ্যাকাউন্ট সফলভাবে প্রস্তুত হয়েছে। ৬-সংখ্যার যাচাইকরণ কোড আপনার ইমেইলে প্রেরণ করা হয়েছে।"
    }


@router.post("/verify-email", response_model=TokenResponse)
def verify_email(req: VerifyEmailRequest, request: Request, db: sqlite3.Connection = Depends(get_db)):
    """Verifies 6-digit OTP code, transitions status to ACTIVE, and issues initial authenticated session."""
    email = req.email.strip().lower()
    code = req.code.strip()

    if len(code) != 6 or not code.isdigit():
        raise HTTPException(status_code=400, detail="যাচাইকরণ কোডটি অবশ্যই ৬-সংখ্যার সংখ্যা হতে হবে।")

    cur = db.cursor()
    # Find latest unused challenge for email verification
    cur.execute("""
    SELECT * FROM auth_challenges
    WHERE email = ? AND purpose = 'EMAIL_VERIFY' AND used_at IS NULL
    ORDER BY created_at DESC LIMIT 1
    """, (email,))
    challenge = cur.fetchone()

    if not challenge:
        raise HTTPException(status_code=400, detail="কোনো সক্রিয় যাচাইকরণ কোড পাওয়া যায়নি। অনুগ্রহ করে কোড রি-সেন্ড করুন।")

    # Check attempt limit
    if challenge["attempts"] >= challenge["max_attempts"]:
        raise HTTPException(status_code=429, detail="সর্বোচ্চ চেষ্টা (৫ বার) অতিক্রম হয়েছে। অনুগ্রহ করে নতুন কোড অনুরোধ করুন।")

    # Check expiration
    now = datetime.now(timezone.utc)
    exp_time = datetime.fromisoformat(challenge["expires_at"])
    if now > exp_time:
        raise HTTPException(status_code=400, detail="যাচাইকরণ কোডের ১০ মিনিট মেয়াদ উত্তীর্ণ হয়েছে। নতুন কোড অনুরোধ করুন।")

    # Increment attempt count
    cur.execute("UPDATE auth_challenges SET attempts = attempts + 1 WHERE challenge_id = ?", (challenge["challenge_id"],))
    db.commit()

    # Verify cryptographic digest
    is_valid = CryptoService.verify_otp(code, challenge["code_hash"], SECRET_KEY)
    if not is_valid:
        remaining = challenge["max_attempts"] - (challenge["attempts"] + 1)
        raise HTTPException(
            status_code=400,
            detail=f"ভুল ওটিপি কোড প্রদান করা হয়েছে। অবশিষ্ট চেষ্টা: {max(0, remaining)} বার।"
        )

    # Mark challenge as used
    cur.execute("UPDATE auth_challenges SET used_at = ? WHERE challenge_id = ?", (now.isoformat(), challenge["challenge_id"]))

    # Fetch user & update status to ACTIVE
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="অ্যাকাউন্ট ব্যবহারকারী পাওয়া যায়নি।")

    cur.execute("UPDATE users SET status = 'ACTIVE', updated_at = ? WHERE email = ?", (now.isoformat(), email))
    db.commit()

    # Issue persistent session
    ip_addr = request.client.host if request.client else ""
    user_agent = request.headers.get("user-agent", "")
    token = create_user_session(dict(user), db, remember_me=True, ip_address=ip_addr, user_agent=user_agent)

    log_security_event(db, user["user_id"], email, "EMAIL_VERIFIED", {"role": user["role"]}, ip_addr)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user["user_id"],
        name=user["full_name"],
        role=user["role"],
        status="ACTIVE",
        email=user["email"]
    )


@router.post("/resend-code")
def resend_code(req: ResendCodeRequest, db: sqlite3.Connection = Depends(get_db)):
    """Re-issues a fresh 6-digit OTP with a strict 60-second rate-limiting cooldown."""
    email = req.email.strip().lower()
    purpose = req.purpose.upper().strip()

    cur = db.cursor()
    # Check cooldown on recent challenge
    cur.execute("""
    SELECT resend_available_at FROM auth_challenges
    WHERE email = ? AND purpose = ?
    ORDER BY created_at DESC LIMIT 1
    """, (email, purpose))
    last_challenge = cur.fetchone()

    now = datetime.now(timezone.utc)
    if last_challenge:
        cooldown_until = datetime.fromisoformat(last_challenge["resend_available_at"])
        if now < cooldown_until:
            seconds_left = int((cooldown_until - now).total_seconds())
            raise HTTPException(
                status_code=429,
                detail=f"অনুগ্রহ করে {seconds_left} সেকেন্ড অপেক্ষা করে পুনরায় কোড অনুরোধ করুন।"
            )

    # Invalidate older challenges
    cur.execute("UPDATE auth_challenges SET used_at = ? WHERE email = ? AND purpose = ? AND used_at IS NULL",
                (now.isoformat(), email, purpose))

    # Fetch user
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    user_name = user["full_name"] if user else "সম্মানিত ব্যবহারকারী"
    user_id = user["user_id"] if user else None

    # Generate fresh OTP
    otp_code = CryptoService.generate_numeric_otp(6)
    otp_hash = CryptoService.hash_otp(otp_code, SECRET_KEY)
    expires_at = (now + timedelta(minutes=10)).isoformat()
    resend_at = (now + timedelta(seconds=60)).isoformat()

    cur.execute("""
    INSERT INTO auth_challenges (challenge_id, email, user_id, purpose, code_hash, expires_at, attempts, resend_available_at, created_at)
    VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
    """, (f"CHAL-{uuid.uuid4().hex[:12]}", email, user_id, purpose, otp_hash, expires_at, resend_at, now.isoformat()))
    db.commit()

    if purpose == "EMAIL_VERIFY":
        EmailService.send_verification_otp(email, user_name, otp_code)
    else:
        EmailService.send_password_reset_otp(email, user_name, otp_code)

    return {
        "success": True,
        "message": "আপনার ইমেইলে নতুন ৬-সংখ্যার যাচাইকরণ কোড প্রেরণ করা হয়েছে।"
    }


# ============================================================================
# 2. LOGIN & SESSION CREATION
# ============================================================================

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, request: Request, db: sqlite3.Connection = Depends(get_db)):
    """Authenticates credentials against SQLite users table and issues a verified session token."""
    email = req.email.strip().lower()
    ip_addr = request.client.host if request.client else ""

    # Rate limiting check: max 5 failed attempts in last 5 minutes
    cur = db.cursor()
    five_min_ago = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    cur.execute("""
    SELECT COUNT(*) FROM security_audit_logs
    WHERE actor_email = ? AND action = 'LOGIN_FAILED' AND timestamp >= ?
    """, (email, five_min_ago))
    failed_attempts = cur.fetchone()[0]
    if failed_attempts >= 5:
        raise HTTPException(
            status_code=429,
            detail="অতিরিক্ত ব্যর্থ লগইন চেষ্টার কারণে অ্যাকাউন্ট সাময়িকভাবে লক হয়েছে। ৫ মিনিট পর পুনরায় চেষ্টা করুন।"
        )

    # Fetch user from persistent users table
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()

    # Generic credential error to prevent email enumeration
    generic_error = HTTPException(status_code=401, detail="ইমেইল অথবা পাসওয়ার্ড সঠিক নয়।")

    if not user:
        log_security_event(db, None, email, "LOGIN_FAILED", {"reason": "USER_NOT_FOUND"}, ip_addr)
        raise generic_error

    # Verify password hash
    is_valid_pwd = CryptoService.verify_password(req.password, user["password_hash"])
    if not is_valid_pwd:
        log_security_event(db, user["user_id"], email, "LOGIN_FAILED", {"reason": "INVALID_PASSWORD"}, ip_addr)
        raise generic_error

    # Check status
    if user["status"] == "UNVERIFIED":
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ACCOUNT_UNVERIFIED",
                "email": email,
                "message": "আপনার ইমেইল ঠিকানা এখনো যাচাই করা হয়নি। দয়া করে কোড দিয়ে যাচাই সম্পন্ন করুন।"
            }
        )
    if user["status"] == "SUSPENDED":
        raise HTTPException(
            status_code=403,
            detail="নিরাপত্তাজনিত কারণে এই অ্যাকাউন্টটি স্থগিত করা হয়েছে। সিস্টেম অ্যাডমিনের সাথে যোগাযোগ করুন।"
        )

    # Issue session token
    user_agent = request.headers.get("user-agent", "")
    token = create_user_session(dict(user), db, remember_me=req.remember_me, ip_address=ip_addr, user_agent=user_agent)

    log_security_event(db, user["user_id"], email, "LOGIN_SUCCESS", {"role": user["role"]}, ip_addr)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user["user_id"],
        name=user["full_name"],
        role=user["role"],
        status=user["status"],
        email=user["email"]
    )


# ============================================================================
# 3. FORGOT PASSWORD & PASSWORD RESET
# ============================================================================

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, request: Request, db: sqlite3.Connection = Depends(get_db)):
    """Requests 6-digit OTP for password reset without leaking whether account exists."""
    email = req.email.strip().lower()
    generic_msg = "যদি অ্যাকাউন্টটি নিবন্ধিত থাকে, তবে একটি ৬-সংখ্যার পাসওয়ার্ড রিসেট ওটিপি আপনার ইমেইলে প্রেরণ করা হয়েছে।"

    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()

    if not user or user["status"] != "ACTIVE":
        return {"success": True, "message": generic_msg}

    # Generate OTP
    now = datetime.now(timezone.utc)
    otp_code = CryptoService.generate_numeric_otp(6)
    otp_hash = CryptoService.hash_otp(otp_code, SECRET_KEY)
    expires_at = (now + timedelta(minutes=10)).isoformat()
    resend_at = (now + timedelta(seconds=60)).isoformat()

    # Invalidate previous reset challenges
    cur.execute("UPDATE auth_challenges SET used_at = ? WHERE email = ? AND purpose = 'PASSWORD_RESET' AND used_at IS NULL",
                (now.isoformat(), email))

    cur.execute("""
    INSERT INTO auth_challenges (challenge_id, email, user_id, purpose, code_hash, expires_at, attempts, resend_available_at, created_at)
    VALUES (?, ?, ?, 'PASSWORD_RESET', ?, ?, 0, ?, ?)
    """, (f"CHAL-{uuid.uuid4().hex[:12]}", email, user["user_id"], otp_hash, expires_at, resend_at, now.isoformat()))
    db.commit()

    EmailService.send_password_reset_otp(email, user["full_name"], otp_code)
    ip_addr = request.client.host if request.client else ""
    log_security_event(db, user["user_id"], email, "PASSWORD_RESET_REQUEST", {}, ip_addr)

    return {"success": True, "message": generic_msg}


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, request: Request, db: sqlite3.Connection = Depends(get_db)):
    """Verifies password reset OTP, updates password, and revokes all active sessions."""
    email = req.email.strip().lower()
    code = req.code.strip()

    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="নতুন পাসওয়ার্ড কমপক্ষে ৮ অক্ষরের হতে হবে।")
    if req.new_password != req.confirm_password:
        raise HTTPException(status_code=400, detail="পাসওয়ার্ড এবং কনফার্ম পাসওয়ার্ড মিলছে না।")

    cur = db.cursor()
    cur.execute("""
    SELECT * FROM auth_challenges
    WHERE email = ? AND purpose = 'PASSWORD_RESET' AND used_at IS NULL
    ORDER BY created_at DESC LIMIT 1
    """, (email,))
    challenge = cur.fetchone()

    if not challenge:
        raise HTTPException(status_code=400, detail="কোনো সক্রিয় পাসওয়ার্ড রিসেট অনুরোধ পাওয়া যায়নি।")

    # Check attempt limit
    if challenge["attempts"] >= challenge["max_attempts"]:
        raise HTTPException(status_code=429, detail="সর্বোচ্চ চেষ্টা অতিক্রম হয়েছে। অনুগ্রহ করে পুনরায় ওটিপি অনুরোধ করুন।")

    # Check expiration
    now = datetime.now(timezone.utc)
    if now > datetime.fromisoformat(challenge["expires_at"]):
        raise HTTPException(status_code=400, detail="রিসেট ওটিপির ১০ মিনিট মেয়াদ উত্তীর্ণ হয়েছে।")

    # Increment attempts
    cur.execute("UPDATE auth_challenges SET attempts = attempts + 1 WHERE challenge_id = ?", (challenge["challenge_id"],))
    db.commit()

    if not CryptoService.verify_otp(code, challenge["code_hash"], SECRET_KEY):
        raise HTTPException(status_code=400, detail="ভুল রিসেট কোড প্রদান করা হয়েছে।")

    # Mark challenge used
    cur.execute("UPDATE auth_challenges SET used_at = ? WHERE challenge_id = ?", (now.isoformat(), challenge["challenge_id"]))

    # Update password and revoke all existing sessions
    new_hash = CryptoService.hash_password(req.new_password)
    cur.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE email = ?", (new_hash, now.isoformat(), email))

    cur.execute("SELECT user_id, full_name FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    if user:
        revoke_all_user_sessions(user["user_id"], db)
        EmailService.send_security_alert(email, user["full_name"], "পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে", "আপনার অ্যাকাউন্টের পাসওয়ার্ড পরিবর্তিত হওয়ায় পূর্বের সকল ডিভাইস সেশন বাতিল করা হয়েছে।")

    db.commit()
    ip_addr = request.client.host if request.client else ""
    log_security_event(db, user["user_id"] if user else None, email, "PASSWORD_RESET_SUCCESS", {}, ip_addr)

    return {
        "success": True,
        "message": "পাসওয়ার্ড সফলভাবে রিসেট সম্পন্ন হয়েছে। নতুন পাসওয়ার্ড দিয়ে লগইন করুন।"
    }


# ============================================================================
# 4. USER PROFILE & SESSION LOGOUT
# ============================================================================

@router.get("/me", response_model=UserProfile)
def get_current_user_profile(
    user: Dict[str, Any] = Depends(require_authenticated_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns profile information for the authenticated session."""
    cur = db.cursor()
    cur.execute("SELECT user_id, email, full_name, phone, role, status, created_at FROM users WHERE user_id = ?", (user["user_id"],))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="ব্যবহারকারী তথ্য পাওয়া যায়নি।")
    return UserProfile(
        user_id=row["user_id"],
        email=row["email"],
        full_name=row["full_name"],
        phone=row["phone"],
        role=row["role"],
        status=row["status"],
        created_at=row["created_at"]
    )


@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    request: Request,
    user: Dict[str, Any] = Depends(require_authenticated_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """Changes password for an active logged-in user."""
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="নতুন পাসওয়ার্ড কমপক্ষে ৮ অক্ষরের হতে হবে।")
    if req.new_password != req.confirm_password:
        raise HTTPException(status_code=400, detail="নতুন পাসওয়ার্ড এবং কনফার্ম পাসওয়ার্ড মিলছে না।")

    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user["user_id"],))
    u = cur.fetchone()
    if not u or not CryptoService.verify_password(req.old_password, u["password_hash"]):
        raise HTTPException(status_code=400, detail="বর্তমান পাসওয়ার্ডটি সঠিক নয়।")

    now = datetime.now(timezone.utc).isoformat()
    new_hash = CryptoService.hash_password(req.new_password)
    cur.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE user_id = ?", (new_hash, now, user["user_id"]))
    db.commit()

    ip_addr = request.client.host if request.client else ""
    log_security_event(db, user["user_id"], user["email"], "PASSWORD_CHANGED", {}, ip_addr)

    return {"success": True, "message": "পাসওয়ার্ড সফলভাবে পরিবর্তিত হয়েছে।"}


@router.post("/logout")
def logout(
    authorization: str = Header(...),
    user: Dict[str, Any] = Depends(require_authenticated_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """Revokes the active session token."""
    token = authorization.replace("Bearer ", "").strip()
    revoke_session(token, db)
    log_security_event(db, user["user_id"], user["email"], "LOGOUT", {})
    return {"success": True, "message": "লগআউট সফল হয়েছে।"}


@router.post("/logout-all")
def logout_all_sessions(
    user: Dict[str, Any] = Depends(require_authenticated_user),
    db: sqlite3.Connection = Depends(get_db)
):
    """Revokes all active sessions for the user across all devices."""
    revoke_all_user_sessions(user["user_id"], db)
    log_security_event(db, user["user_id"], user["email"], "LOGOUT_ALL_SESSIONS", {})
    return {"success": True, "message": "সকল সক্রিয় ডিভাইস সেশন সফলভাবে বাতিল করা হয়েছে।"}


@router.get("/dev-mailbox")
def get_dev_mailbox(email: Optional[str] = Query(None)):
    """Development evaluation endpoint: returns latest OTP dispatched in dev mode."""
    if email:
        otp = DevMailbox.get_latest_otp(email)
        return {"email": email, "latest_otp": otp}
    return {"recent_messages": DevMailbox.recent_messages}
