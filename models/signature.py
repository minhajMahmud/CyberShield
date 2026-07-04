"""
models/signature.py
--------------------
Records of RSA-2048 digital signature generation & verification.
"""

from datetime import datetime
from models import db


class DigitalSignature(db.Model):
    __tablename__ = "Digital_Signatures"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id", ondelete="CASCADE"), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey("Files.id", ondelete="SET NULL"), nullable=True)

    document_name = db.Column(db.String(255), nullable=False)
    document_hash = db.Column(db.String(128), nullable=False)      # SHA-256 hex digest
    signature_value = db.Column(db.Text, nullable=False)           # base64 signature
    public_key = db.Column(db.Text, nullable=False)                # PEM
    private_key_encrypted = db.Column(db.Text, nullable=True)      # PEM, AES-wrapped at rest

    status = db.Column(
        db.Enum("signed", "verified", "failed", "tampered", name="sig_status_enum"),
        default="signed",
        nullable=False,
    )
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DigitalSignature {self.document_name} status={self.status}>"
