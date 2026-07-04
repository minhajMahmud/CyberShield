"""
models/file.py
---------------
Metadata for AES-256-GCM encrypted files. Encrypted bytes live on
disk under /encrypted; only metadata + key wrapping info lives here.
"""

from datetime import datetime
from models import db


class FileRecord(db.Model):
    __tablename__ = "Files"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id", ondelete="CASCADE"), nullable=False)

    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), unique=True, nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)

    encryption_iv = db.Column(db.String(64), nullable=False)      # base64 IV/nonce
    encrypted_dek = db.Column(db.String(255), nullable=False)     # per-file key wrapped by master key
    checksum_sha256 = db.Column(db.String(64), nullable=False)    # integrity hash of plaintext

    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    signatures = db.relationship("DigitalSignature", backref="file", lazy="dynamic")

    def __repr__(self):
        return f"<FileRecord {self.original_filename} user={self.user_id}>"
