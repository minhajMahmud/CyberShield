"""
models/user.py
---------------
Users table - authentication, role and 2FA state.
Maps 1:1 onto the `Users` table defined in database.sql.
"""

from datetime import datetime
from flask_login import UserMixin
from models import db


class User(db.Model, UserMixin):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.Enum("user", "admin", name="role_enum"), default="user", nullable=False)

    is_2fa_enabled = db.Column(db.Boolean, default=False, nullable=False)
    twofa_secret = db.Column(db.String(64), nullable=True)

    is_active_flag = db.Column("is_active", db.Boolean, default=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    files = db.relationship("FileRecord", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    signatures = db.relationship("DigitalSignature", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    otps = db.relationship("OTP", backref="owner", lazy="dynamic", cascade="all, delete-orphan")

    # Flask-Login requires an `is_active` property; our column is aliased above.
    @property
    def is_active(self):
        return self.is_active_flag

    def is_locked(self):
        return bool(self.locked_until and self.locked_until > datetime.utcnow())

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
