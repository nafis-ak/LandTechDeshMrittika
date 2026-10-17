"""
DESHMRITTIKA / BHUMI-SYNC — Cryptographic & Password Security Service
Implements OWASP/NIST compliant PBKDF2-HMAC-SHA256 password hashing (600,000 iterations),
cryptographic OTP generation, and constant-time token comparison.
"""

import os
import hmac
import hashlib
import secrets
import time
from typing import Tuple

PBKDF2_ITERATIONS = 600_000
HASH_ALGORITHM = 'sha256'
SALT_BYTES = 16

class CryptoService:

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes password using PBKDF2-HMAC-SHA256 with 600,000 iterations and a unique salt."""
        salt = os.urandom(SALT_BYTES)
        key = hashlib.pbkdf2_hmac(HASH_ALGORITHM, password.encode('utf-8'), salt, PBKDF2_ITERATIONS)
        salt_hex = salt.hex()
        key_hex = key.hex()
        return f"pbkdf2_{HASH_ALGORITHM}${PBKDF2_ITERATIONS}${salt_hex}${key_hex}"

    @staticmethod
    def verify_password(password: str, hashed_value: str) -> bool:
        """Verifies plaintext password against stored PBKDF2 hash using constant-time comparison."""
        try:
            if not hashed_value or not hashed_value.startswith('pbkdf2_'):
                return False
            parts = hashed_value.split('$')
            if len(parts) != 4:
                return False
            _, iterations_str, salt_hex, expected_key_hex = parts
            iterations = int(iterations_str)
            salt = bytes.fromhex(salt_hex)
            computed_key = hashlib.pbkdf2_hmac(HASH_ALGORITHM, password.encode('utf-8'), salt, iterations)
            expected_key = bytes.fromhex(expected_key_hex)
            return hmac.compare_digest(computed_key, expected_key)
        except Exception:
            return False

    @staticmethod
    def generate_numeric_otp(length: int = 6) -> str:
        """Generates cryptographically random N-digit numeric OTP."""
        digits = '0123456789'
        return ''.join(secrets.choice(digits) for _ in range(length))

    @staticmethod
    def hash_otp(code: str, secret_salt: str) -> str:
        """Computes keyed digest of OTP to prevent database exposure."""
        return hmac.new(secret_salt.encode('utf-8'), code.strip().encode('utf-8'), hashlib.sha256).hexdigest()

    @staticmethod
    def verify_otp(code: str, stored_hash: str, secret_salt: str) -> bool:
        """Verifies OTP in constant time."""
        computed_hash = CryptoService.hash_otp(code, secret_salt)
        return hmac.compare_digest(computed_hash, stored_hash)

    @staticmethod
    def hash_token(token: str) -> str:
        """Computes SHA-256 hash of a session token for secure database indexing."""
        return hashlib.sha256(token.encode('utf-8')).hexdigest()
