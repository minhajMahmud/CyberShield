"""
utils/otp_utils.py
--------------------
Two-Factor Authentication helpers.

Supports two OTP flavours:
1. Email OTP - a random 6-digit numeric code, stored (hashed is
   overkill here since it's single-use + short-lived, but we do
   enforce expiry + one-time use) in the OTP table, emailed via
   Flask-Mail, and checked against user input.
2. TOTP (Time-based One-Time Password, RFC 6238) via `pyotp` - the
   classic "Google Authenticator" style app-based 2FA, backed by a
   per-user base32 secret and delivered to the user as a QR code
   (via `qrcode`) they scan once during setup.
"""

import io
import base64
import random
import string
from datetime import datetime, timedelta

import pyotp
import qrcode


# ---------------------------------------------------------------
# Email OTP (6-digit numeric code)
# ---------------------------------------------------------------

def generate_numeric_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def otp_expiry(seconds: int = 300) -> datetime:
    return datetime.utcnow() + timedelta(seconds=seconds)


# ---------------------------------------------------------------
# TOTP (authenticator-app based 2FA)
# ---------------------------------------------------------------

def generate_totp_secret() -> str:
    """Generate a new base32 secret for a user's authenticator app."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, account_email: str, issuer_name: str = "CyberShield") -> str:
    """Build the otpauth:// URI that authenticator apps consume."""
    return pyotp.totp.TOTP(secret).provisioning_uri(name=account_email, issuer_name=issuer_name)


def verify_totp(secret: str, code: str) -> bool:
    """Verify a 6-digit TOTP code against the user's secret (allowing 1 step drift)."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_qr_code_base64(data: str) -> str:
    """Generate a QR code PNG for the given data, returned as a base64 data-URI string."""
    img = qrcode.make(data)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"
