"""
models/password_history.py
---------------------------
History of password-strength checks. We NEVER store the plaintext
password - only a SHA-256 sample hash and the computed metrics, so
this table is safe even if the database is compromised.
"""

from datetime import datetime
from models import db


class PasswordCheckHistory(db.Model):
    __tablename__ = "Password_Check_History"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id", ondelete="SET NULL"), nullable=True)

    password_hash_sample = db.Column(db.String(255), nullable=False)
    strength_score = db.Column(db.SmallInteger, nullable=False)     # 0-100
    strength_label = db.Column(db.String(20), nullable=False)       # Weak/Fair/Good/Strong/Very Strong
    estimated_crack_time = db.Column(db.String(50), nullable=True)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PasswordCheckHistory score={self.strength_score} label={self.strength_label}>"
