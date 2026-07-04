"""
models/otp.py
-------------
One-time-passcodes used for login verification, enabling 2FA, and
password-reset flows.
"""

from datetime import datetime
from models import db


class OTP(db.Model):
    __tablename__ = "OTP"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id", ondelete="CASCADE"), nullable=False)

    otp_code = db.Column(db.String(10), nullable=False)
    purpose = db.Column(
        db.Enum("login", "enable_2fa", "reset_password", "email_verification", name="otp_purpose_enum"),
        default="login",
        nullable=False,
    )
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<OTP user={self.user_id} purpose={self.purpose} used={self.is_used}>"
