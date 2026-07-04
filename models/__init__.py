"""
models/__init__.py
-------------------
Exposes a single SQLAlchemy `db` instance shared across the app,
and re-exports all ORM models for convenient importing:

    from models import db, User, FileRecord, ...
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User                       # noqa: E402
from .file import FileRecord                  # noqa: E402
from .signature import DigitalSignature       # noqa: E402
from .otp import OTP                          # noqa: E402
from .activity_log import ActivityLog         # noqa: E402
from .password_history import PasswordCheckHistory  # noqa: E402

__all__ = [
    "db",
    "User",
    "FileRecord",
    "DigitalSignature",
    "OTP",
    "ActivityLog",
    "PasswordCheckHistory",
]
