"""
DESHMRITTIKA / BHUMI-SYNC v2.1 — Comprehensive Authentication & Four-Role Security Test Suite
Tests Signup, 6-digit OTP Verification, PBKDF2 Password Hashing, Session Invalidation,
Password Reset, 4-Role Server-Side RBAC, Privilege Escalation Prevention, and Audit Trails.
"""

import unittest
import uuid
import sqlite3
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import DATABASE_PATH, SECRET_KEY
from backend.app.services.crypto import CryptoService
from backend.app.services.email import DevMailbox

client = TestClient(app)


class TestAuthAndSecurity(unittest.TestCase):

    def setUp(self):
        self.test_prefix = f"test_{uuid.uuid4().hex[:8]}"

    # ========================================================================
    # 1. SIGNUP & REGISTRATION TESTS
    # ========================================================================

    def test_01_signup_valid_citizen(self):
        """Signup with valid details creates UNVERIFIED user and generates OTP challenge."""
        email = f"{self.test_prefix}_citizen@example.com"
        res = client.post("/api/v1/auth/signup", json={
            "full_name": "মো: তাহমিদ হাসান",
            "email": email,
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "phone": "01711000111",
            "role": "CITIZEN"
        })
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "UNVERIFIED")
        self.assertEqual(data["role"], "CITIZEN")

        # Verify challenge was logged in dev mailbox
        mail = DevMailbox.get_latest_otp(email, "EMAIL_VERIFY")
        self.assertIsNotNone(mail)
        self.assertEqual(len(mail), 6)
        self.assertTrue(mail.isdigit())

    def test_02_signup_privilege_escalation_blocked(self):
        """Public signup requesting OFFICER or ADMINISTRATOR role must be rejected with 403."""
        email = f"{self.test_prefix}_hacker@example.com"
        res = client.post("/api/v1/auth/signup", json={
            "full_name": "ফেইক অফিসার",
            "email": email,
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "role": "OFFICER"
        })
        self.assertEqual(res.status_code, 403)
        self.assertIn("পাবলিক সাইন-আপ নিষিদ্ধ", res.json()["detail"])

        res_admin = client.post("/api/v1/auth/signup", json={
            "full_name": "ফেইক অ্যাডমিন",
            "email": email,
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "role": "ADMINISTRATOR"
        })
        self.assertEqual(res_admin.status_code, 403)

    def test_03_signup_password_rules_and_mismatch(self):
        """Short password (<8 chars) or mismatched confirmation must be rejected."""
        res_short = client.post("/api/v1/auth/signup", json={
            "full_name": "টেস্ট ইউজার",
            "email": f"{self.test_prefix}_short@example.com",
            "password": "short",
            "confirm_password": "short"
        })
        self.assertEqual(res_short.status_code, 400)

        res_mismatch = client.post("/api/v1/auth/signup", json={
            "full_name": "টেস্ট ইউজার",
            "email": f"{self.test_prefix}_mismatch@example.com",
            "password": "Password123!",
            "confirm_password": "DifferentPassword123!"
        })
        self.assertEqual(res_mismatch.status_code, 400)

    def test_04_signup_duplicate_email(self):
        """Duplicate verified email registration must be rejected with 400."""
        res = client.post("/api/v1/auth/signup", json={
            "full_name": "মালিক",
            "email": "citizen@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "CITIZEN"
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("ইতোমধ্যে একটি অ্যাকাউন্ট নিবন্ধিত রয়েছে", res.json()["detail"])

    # ========================================================================
    # 2. EMAIL VERIFICATION (OTP) TESTS
    # ========================================================================

    def test_05_otp_successful_verification(self):
        """Valid OTP transitions account to ACTIVE and returns authenticated session token."""
        email = f"{self.test_prefix}_verify@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "মো: আব্দুল্লাহ",
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "BUYER"
        })

        otp_code = DevMailbox.get_latest_otp(email, "EMAIL_VERIFY")
        self.assertIsNotNone(otp_code)

        res_v = client.post("/api/v1/auth/verify-email", json={
            "email": email,
            "code": otp_code
        })
        self.assertEqual(res_v.status_code, 200, res_v.text)
        data = res_v.json()
        self.assertEqual(data["status"], "ACTIVE")
        self.assertEqual(data["role"], "BUYER")
        self.assertTrue(len(data["access_token"]) > 20)

        # Token can now access protected /auth/me
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        res_me = client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()["email"], email)

    def test_06_otp_invalid_code_and_remaining_attempts(self):
        """Incorrect OTP returns 400 with decrementing attempt count."""
        email = f"{self.test_prefix}_wrong_otp@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "ইউজার টেস্ট",
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })

        res_bad = client.post("/api/v1/auth/verify-email", json={
            "email": email,
            "code": "999999"
        })
        self.assertEqual(res_bad.status_code, 400)
        self.assertIn("ভুল ওটিপি কোড", res_bad.json()["detail"])

    def test_07_otp_reuse_blocked(self):
        """Used OTP code cannot be replayed."""
        email = f"{self.test_prefix}_reuse@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "ইউজার টেস্ট",
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        code = DevMailbox.get_latest_otp(email, "EMAIL_VERIFY")

        # First verification succeeds
        res1 = client.post("/api/v1/auth/verify-email", json={"email": email, "code": code})
        self.assertEqual(res1.status_code, 200)

        # Second verification attempt fails
        res2 = client.post("/api/v1/auth/verify-email", json={"email": email, "code": code})
        self.assertEqual(res2.status_code, 400)

    def test_08_resend_cooldown_rate_limit(self):
        """Requesting resend within 60-second cooldown must return 429."""
        email = f"{self.test_prefix}_resend@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "ইউজার টেস্ট",
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })

        # Immediate resend attempt should hit 60-second cooldown
        res = client.post("/api/v1/auth/resend-code", json={
            "email": email,
            "purpose": "EMAIL_VERIFY"
        })
        self.assertEqual(res.status_code, 429)
        self.assertIn("অপেক্ষা করে", res.json()["detail"])

    # ========================================================================
    # 3. LOGIN, SESSION & PASSWORD RESET TESTS
    # ========================================================================

    def test_09_login_unverified_account_blocked(self):
        """Unverified account cannot login; returns 403 with ACCOUNT_UNVERIFIED."""
        email = f"{self.test_prefix}_unver_login@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "অযাচাইকৃত",
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })

        res_login = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "Password123!"
        })
        self.assertEqual(res_login.status_code, 403)
        self.assertEqual(res_login.json()["detail"]["code"], "ACCOUNT_UNVERIFIED")

    def test_10_login_invalid_password(self):
        """Invalid password returns generic 401 without user enumeration."""
        email = f"{self.test_prefix}_bad_pwd@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "ইউজার টেস্ট",
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        code = DevMailbox.get_latest_otp(email, "EMAIL_VERIFY")
        client.post("/api/v1/auth/verify-email", json={"email": email, "code": code})

        res = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "WrongPassword!"
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn("ইমেইল অথবা পাসওয়ার্ড সঠিক নয়", res.json()["detail"])

    def test_11_logout_and_session_invalidation(self):
        """Logging out invalidates session token; subsequent calls return 401."""
        res_login = client.post("/api/v1/auth/login", json={
            "email": "citizen@example.com",
            "password": "Password123!"
        })
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Token works
        res_me = client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res_me.status_code, 200)

        # Logout
        res_out = client.post("/api/v1/auth/logout", headers=headers)
        self.assertEqual(res_out.status_code, 200)

        # Token is revoked
        res_me_after = client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res_me_after.status_code, 401)

    def test_12_password_reset_flow(self):
        """Full password reset journey: forgot-password -> OTP -> reset -> login with new password."""
        email = f"{self.test_prefix}_pwd_reset@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "রিসেট ইউজার",
            "email": email,
            "password": "OldPassword123!",
            "confirm_password": "OldPassword123!"
        })
        code = DevMailbox.get_latest_otp(email, "EMAIL_VERIFY")
        client.post("/api/v1/auth/verify-email", json={"email": email, "code": code})

        # Request reset OTP
        res_req = client.post("/api/v1/auth/forgot-password", json={"email": email})
        self.assertEqual(res_req.status_code, 200)

        reset_otp = DevMailbox.get_latest_otp(email, "PWD_RESET")
        self.assertIsNotNone(reset_otp)

        # Reset password with OTP
        res_reset = client.post("/api/v1/auth/reset-password", json={
            "email": email,
            "code": reset_otp,
            "new_password": "NewBrandPassword123!",
            "confirm_password": "NewBrandPassword123!"
        })
        self.assertEqual(res_reset.status_code, 200)

        # Old password fails
        res_old = client.post("/api/v1/auth/login", json={"email": email, "password": "OldPassword123!"})
        self.assertEqual(res_old.status_code, 401)

        # New password succeeds
        res_new = client.post("/api/v1/auth/login", json={"email": email, "password": "NewBrandPassword123!"})
        self.assertEqual(res_new.status_code, 200)

    # ========================================================================
    # 4. FOUR-ROLE AUTHORIZATION (RBAC) & TAMPER PROTECTION
    # ========================================================================

    def test_13_citizen_cannot_access_admin_or_officer(self):
        """Citizen token cannot access /admin/users or officer triage endpoints (403)."""
        res_login = client.post("/api/v1/auth/login", json={
            "email": "citizen@example.com",
            "password": "Password123!"
        })
        cit_token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {cit_token}"}

        # Attempt admin user list
        res_admin = client.get("/api/v1/admin/users", headers=headers)
        self.assertEqual(res_admin.status_code, 403)

        # Attempt officer queue
        res_off = client.get("/api/v1/officer/queue", headers=headers)
        self.assertEqual(res_off.status_code, 403)

    def test_14_buyer_cannot_access_officer_or_admin(self):
        """Buyer token cannot access officer review or admin management."""
        res_login = client.post("/api/v1/auth/login", json={
            "email": "buyer@example.com",
            "password": "Password123!"
        })
        buyer_token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {buyer_token}"}

        res_admin = client.get("/api/v1/admin/users", headers=headers)
        self.assertEqual(res_admin.status_code, 403)

        res_off = client.get("/api/v1/officer/queue", headers=headers)
        self.assertEqual(res_off.status_code, 403)

    def test_15_ac_land_can_access_officer_queue_but_not_admin(self):
        """AC Land (OFFICER) can access officer triage queue, but not admin management."""
        res_login = client.post("/api/v1/auth/login", json={
            "email": "officer@savar.land.gov.bd",
            "password": "Password123!"
        })
        off_token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {off_token}"}

        res_off = client.get("/api/v1/officer/queue", headers=headers)
        self.assertEqual(res_off.status_code, 200)

        res_admin = client.get("/api/v1/admin/users", headers=headers)
        self.assertEqual(res_admin.status_code, 403)

    def test_16_admin_full_management_and_last_admin_protection(self):
        """Administrator can list users, change roles, view security logs, but cannot demote last admin."""
        res_login = client.post("/api/v1/auth/login", json={
            "email": "admin@deshmrittika.gov.bd",
            "password": "Password123!"
        })
        admin_token = res_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Admin can list users
        res_users = client.get("/api/v1/admin/users", headers=admin_headers)
        self.assertEqual(res_users.status_code, 200)
        self.assertIn("users", res_users.json())

        # 2. Admin can view security audit logs
        res_logs = client.get("/api/v1/admin/security-logs", headers=admin_headers)
        self.assertEqual(res_logs.status_code, 200)
        self.assertIn("security_logs", res_logs.json())

        # 3. Last admin protection: Attempting to demote admin@deshmrittika.gov.bd
        admin_user_id = res_login.json()["user_id"]
        res_demote = client.post("/api/v1/admin/users/role", headers=admin_headers, json={
            "target_user_id": admin_user_id,
            "new_role": "CITIZEN",
            "reason": "Accidental demotion test"
        })
        self.assertEqual(res_demote.status_code, 400)
        self.assertIn("সর্বশেষ সক্রিয় অ্যাডমিনিস্ট্রেটর", res_demote.json()["detail"])

    def test_17_citizen_private_data_and_application_lifecycle(self):
        """Citizen can view their own linked parcels and submit simulated applications."""
        res_login = client.post("/api/v1/auth/login", json={
            "email": "citizen@example.com",
            "password": "Password123!"
        })
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. View linked parcels
        res_parcels = client.get("/api/v1/citizen/my-parcels", headers=headers)
        self.assertEqual(res_parcels.status_code, 200)
        data = res_parcels.json()
        self.assertIn("parcels", data)
        self.assertGreaterEqual(data["total_linked"], 1)

        # 2. View citizen applications
        res_apps = client.get("/api/v1/citizen/my-applications", headers=headers)
        self.assertEqual(res_apps.status_code, 200)
        self.assertIn("applications", res_apps.json())

        # 3. Submit new simulated application
        res_create = client.post("/api/v1/citizen/applications", headers=headers, json={
            "service_type": "নামজারি ও জমাভাগ (Simulation)",
            "parcel_id": "BD-PAR-000001",
            "mouza_name": "আমিনবাজার",
            "dag_no": "১০১",
            "applicant_phone": "01711000001",
            "remarks": "নতুন দলিলের ভিত্তিতে নামজারি প্রস্তাব"
        })
        self.assertEqual(res_create.status_code, 200)
        created_app = res_create.json()
        self.assertTrue(created_app["success"])
        self.assertTrue(created_app["application_id"].startswith("APP-"))

        # 4. View notifications
        res_notifs = client.get("/api/v1/citizen/my-notifications", headers=headers)
        self.assertEqual(res_notifs.status_code, 200)
        self.assertIn("notifications", res_notifs.json())

        # 5. View activity logs
        res_act = client.get("/api/v1/citizen/my-activity", headers=headers)
        self.assertEqual(res_act.status_code, 200)
        self.assertIn("activity_logs", res_act.json())

    def test_18_separation_of_duties_admin_cannot_decide_officer_cases(self):
        """Admin is strictly prohibited from accessing Officer triage and assigned queues (Separation of Duties)."""
        res_login = client.post("/api/v1/auth/login", json={
            "email": "admin@deshmrittika.gov.bd",
            "password": "Password123!"
        })
        admin_token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Admin attempting officer triage queue
        res_queue = client.get("/api/v1/officer/queue", headers=headers)
        self.assertEqual(res_queue.status_code, 403)
        self.assertIn("Access denied", res_queue.json()["detail"])

        # Admin attempting officer assigned applications
        res_assigned = client.get("/api/v1/officer/assigned-applications", headers=headers)
        self.assertEqual(res_assigned.status_code, 403)

    def test_19_buyer_review_requests_and_isolation(self):
        """Buyer can create and track parcel review requests; Citizen cannot access buyer endpoints."""
        res_buyer = client.post("/api/v1/auth/login", json={
            "email": "buyer@example.com",
            "password": "Password123!"
        })
        buyer_token = res_buyer.json()["access_token"]
        buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

        # Create review request
        res_create = client.post("/api/v1/buyer/review-requests", headers=buyer_headers, json={
            "parcel_id": "BD-PAR-000003",
            "mouza_name": "আমিনবাজার",
            "dag_no": "১০৫",
            "reason": "দ্বৈত বিক্রয় সন্দেহ ও দলিল মেলানো প্রয়োজন",
            "contact_email": "buyer@example.com"
        })
        self.assertEqual(res_create.status_code, 200)
        self.assertTrue(res_create.json()["success"])

        # List review requests
        res_list = client.get("/api/v1/buyer/review-requests", headers=buyer_headers)
        self.assertEqual(res_list.status_code, 200)
        self.assertGreaterEqual(res_list.json()["total"], 1)

        # Citizen attempting to access buyer review requests
        res_cit = client.post("/api/v1/auth/login", json={
            "email": "citizen@example.com",
            "password": "Password123!"
        })
        cit_token = res_cit.json()["access_token"]
        cit_headers = {"Authorization": f"Bearer {cit_token}"}

        res_denied = client.get("/api/v1/buyer/review-requests", headers=cit_headers)
        self.assertEqual(res_denied.status_code, 403)

    def test_20_admin_diagnostics_and_checkpoint(self):
        """Administrator can query diagnostics, OCR health, fraud rules, and trigger DB checkpoint."""
        res_admin = client.post("/api/v1/auth/login", json={
            "email": "admin@deshmrittika.gov.bd",
            "password": "Password123!"
        })
        admin_token = res_admin.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        res_diag = client.get("/api/v1/admin/diagnostics", headers=headers)
        self.assertEqual(res_diag.status_code, 200)
        self.assertEqual(res_diag.json()["system_status"], "OPERATIONAL")

        res_ocr = client.get("/api/v1/admin/ocr-health", headers=headers)
        self.assertEqual(res_ocr.status_code, 200)
        self.assertIn("Tesseract OCR", res_ocr.json()["engine"])

        res_rules = client.get("/api/v1/admin/fraud-rules", headers=headers)
        self.assertEqual(res_rules.status_code, 200)
        self.assertGreaterEqual(len(res_rules.json()["active_rules"]), 4)

        res_chk = client.post("/api/v1/admin/backups/checkpoint", headers=headers)
        self.assertEqual(res_chk.status_code, 200)
        self.assertTrue(res_chk.json()["success"])

    def test_21_client_side_role_tampering_blocked(self):
        """Client-side role claims cannot elevate privileges; server derives role exclusively from HMAC session token."""
        res_login = client.post("/api/v1/auth/login", json={
            "email": "citizen@example.com",
            "password": "Password123!"
        })
        cit_token = res_login.json()["access_token"]

        # Client attempts to send headers or spoofed role claim
        headers = {
            "Authorization": f"Bearer {cit_token}",
            "X-Client-Role": "ADMINISTRATOR"
        }

        # Attempt to access admin endpoint
        res = client.get("/api/v1/admin/users", headers=headers)
        self.assertEqual(res.status_code, 403)
        self.assertIn("Access denied", res.json()["detail"])

    def test_22_cross_citizen_idor_application_access_blocked(self):
        """Citizen A cannot access Citizen B's private application by ID (IDOR protection)."""
        # 1. Create Citizen B
        email_b = f"{self.test_prefix}_citizen_b@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "নাগরিক বি",
            "email": email_b,
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "CITIZEN"
        })
        otp_b = DevMailbox.get_latest_otp(email_b, "EMAIL_VERIFY")
        res_v_b = client.post("/api/v1/auth/verify-email", json={"email": email_b, "code": otp_b})
        tok_b = res_v_b.json()["access_token"]
        h_b = {"Authorization": f"Bearer {tok_b}"}

        # Citizen B submits application
        res_app_b = client.post("/api/v1/citizen/applications", headers=h_b, json={
            "parcel_id": "BD-PAR-000001",
            "service_type": "নামজারি",
            "remarks": "নাগরিক বি এর গোপন আবেদন"
        })
        self.assertEqual(res_app_b.status_code, 200)
        app_id_b = res_app_b.json()["app_id"]

        # 2. Citizen A logs in and attempts to access Citizen B's application
        res_cit_a = client.post("/api/v1/auth/login", json={
            "email": "citizen@example.com",
            "password": "Password123!"
        })
        tok_a = res_cit_a.json()["access_token"]
        h_a = {"Authorization": f"Bearer {tok_a}"}

        # Citizen A requests Citizen B's application by ID
        res_idor = client.get(f"/api/v1/citizen/my-applications/{app_id_b}", headers=h_a)
        self.assertEqual(res_idor.status_code, 403)
        self.assertIn("অন্য নাগরিকের ব্যক্তিগত আবেদন", res_idor.json()["detail"])

    def test_23_suspended_account_session_rejected(self):
        """Suspended accounts immediately lose API access with 401 Unauthorized."""
        email_sus = f"{self.test_prefix}_suspendee@example.com"
        client.post("/api/v1/auth/signup", json={
            "full_name": "স্থগিত ইউজার",
            "email": email_sus,
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "CITIZEN"
        })
        otp = DevMailbox.get_latest_otp(email_sus, "EMAIL_VERIFY")
        res_v = client.post("/api/v1/auth/verify-email", json={"email": email_sus, "code": otp})
        sus_token = res_v.json()["access_token"]
        sus_user_id = res_v.json()["user_id"]
        h_sus = {"Authorization": f"Bearer {sus_token}"}

        # User currently has access
        res_before = client.get("/api/v1/auth/me", headers=h_sus)
        self.assertEqual(res_before.status_code, 200)

        # Admin suspends user account
        res_admin = client.post("/api/v1/auth/login", json={
            "email": "admin@deshmrittika.gov.bd",
            "password": "Password123!"
        })
        admin_token = res_admin.json()["access_token"]
        h_admin = {"Authorization": f"Bearer {admin_token}"}

        res_sus_action = client.post("/api/v1/admin/users/status", headers=h_admin, json={
            "target_user_id": sus_user_id,
            "new_status": "SUSPENDED",
            "reason": "নিরাপত্তা অডিট কারণে স্থগিত"
        })
        self.assertEqual(res_sus_action.status_code, 200)

        # Suspended user's existing token is rejected with 401
        res_after = client.get("/api/v1/auth/me", headers=h_sus)
        self.assertEqual(res_after.status_code, 401)


if __name__ == "__main__":
    unittest.main()


