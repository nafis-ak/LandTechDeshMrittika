"""
DESHMRITTIKA / BHUMI-SYNC — Email Dispatcher & Dev Mailbox
Handles email verification codes (OTP), password reset tokens, and security notices.
Provides both SMTP integration for production and a safe Development Adapter for hackathon evaluation.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

# Dev mailbox storage for local evaluation
class DevMailbox:
    recent_messages: List[Dict[str, Any]] = []
    max_history: int = 50

    @classmethod
    def record_message(cls, to_email: str, subject: str, body_text: str, otp_code: Optional[str] = None):
        entry = {
            "to": to_email,
            "subject": subject,
            "body": body_text,
            "otp_code": otp_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        cls.recent_messages.append(entry)
        if len(cls.recent_messages) > cls.max_history:
            cls.recent_messages.pop(0)

        # Write to .dev_mail.log
        try:
            log_path = Path(__file__).resolve().parent.parent.parent.parent / ".dev_mail.log"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\nTIME: {entry['timestamp']}\nTO: {to_email}\nSUBJECT: {subject}\nOTP CODE: {otp_code}\nBODY:\n{body_text}\n{'='*60}\n")
        except Exception as e:
            print(f"[DevMailbox File Log Warning]: {e}")

    @classmethod
    def get_latest_otp(cls, to_email: str, purpose: Optional[str] = None) -> Optional[str]:
        for msg in reversed(cls.recent_messages):
            if msg["to"].lower() == to_email.lower() and msg.get("otp_code"):
                return msg["otp_code"]
        return None

    @classmethod
    def clear(cls):
        cls.recent_messages.clear()


class EmailService:
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "security@deshmrittika.gov.bd")

    @classmethod
    def is_smtp_configured(cls) -> bool:
        return bool(cls.SMTP_HOST and cls.SMTP_USER and cls.SMTP_PASS)

    @classmethod
    def send_verification_otp(cls, to_email: str, recipient_name: str, otp_code: str) -> bool:
        subject = "দেশমৃত্তিকা — আপনার ৬-সংখ্যার ইমেইল যাচাইকরণ ওটিপি কোড"
        body_text = f"""
আসসালামু আলাইকুম {recipient_name},

দেশমৃত্তিকা (DeshMrittika) স্মার্ট ভূমি প্ল্যাটফর্মে অ্যাকাউন্ট নিবন্ধনের জন্য আপনাকে ধন্যবাদ।

আপনার ৬-সংখ্যার একক ওয়ান-টাইম যাচাইকরণ কোডটি হলো:
----------------------------------------
                {otp_code}
----------------------------------------
(কোডটির মেয়াদ আগামী ১০ মিনিট পর্যন্ত কার্যকর থাকবে)

সতর্কতা: এই কোডটি গোপন রাখুন। কোনো কর্মকর্তা বা তৃতীয় পক্ষ কখনোই আপনার ওটিপি জানতে চাইবে না।
যদি আপনি এই অ্যাকাউন্ট খোলার অনুরোধ না করে থাকেন, তবে বার্তাটি উপেক্ষা করুন।

ধন্যবাদান্তে,
নিরাপত্তা ও আইডেন্টিটি বিভাগ
দেশমৃত্তিকা | BHUMI-SYNC
"""
        return cls._dispatch(to_email, subject, body_text, otp_code=otp_code)

    @classmethod
    def send_password_reset_otp(cls, to_email: str, recipient_name: str, otp_code: str) -> bool:
        subject = "দেশমৃত্তিকা — পাসওয়ার্ড রিসেট ভেরিফিকেশন কোড"
        body_text = f"""
সম্মানিত {recipient_name},

আপনার দেশমৃত্তিকা অ্যাকাউন্টের পাসওয়ার্ড পরিবর্তনের জন্য অনুরোধ পাওয়া গেছে।

আপনার পাসওয়ার্ড রিসেট ওটিপি কোডটি হলো:
----------------------------------------
                {otp_code}
----------------------------------------
(কোডটির মেয়াদ আগামী ১০ মিনিট পর্যন্ত কার্যকর থাকবে)

সতর্কতা: আপনি পাসওয়ার্ড রিসেট অনুরোধ না করে থাকলে অবিলম্বে অ্যাকাউন্ট নিরাপত্তা চেক করুন।

ধন্যবাদান্তে,
দেশমৃত্তিকা আইটি সুরক্ষা সেল
"""
        return cls._dispatch(to_email, subject, body_text, otp_code=otp_code)

    @classmethod
    def send_security_alert(cls, to_email: str, recipient_name: str, action_title: str, details: str) -> bool:
        subject = f"দেশমৃত্তিকা নিরাপত্তা সতর্কতা: {action_title}"
        body_text = f"""
সম্মানিত {recipient_name},

আপনার দেশমৃত্তিকা অ্যাকাউন্টে একটি গুরুত্বপূর্ণ নিরাপত্তা পরিবর্তন সম্পন্ন হয়েছে:
• বিষয়: {action_title}
• বিবরণ: {details}
• সময়: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

যদি এই পরিবর্তনটি আপনি না করে থাকেন, তবে সিস্টেম অ্যাডমিনিস্ট্রেটরের সাথে যোগাযোগ করুন।

দেশমৃত্তিকা প্ল্যাটফর্ম
"""
        return cls._dispatch(to_email, subject, body_text, otp_code=None)

    @classmethod
    def _dispatch(cls, to_email: str, subject: str, body_text: str, otp_code: Optional[str] = None) -> bool:
        # Always record in dev mailbox for local observability / testing
        DevMailbox.record_message(to_email, subject, body_text, otp_code=otp_code)

        if not cls.is_smtp_configured():
            # Development Mode
            print(f"\n📧 [DEV EMAIL DISPATCHED] -> To: {to_email} | Subject: '{subject}' | OTP: {otp_code}")
            return True

        # SMTP Delivery
        try:
            msg = MIMEMultipart()
            msg["From"] = f"DeshMrittika Security <{cls.FROM_EMAIL}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body_text, "plain", "utf-8"))

            with smtplib.SMTP(cls.SMTP_HOST, cls.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(cls.SMTP_USER, cls.SMTP_PASS)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"❌ [SMTP Delivery Error to {to_email}]: {e}")
            return False
