"""
models/activity_log.py
-----------------------
Security audit trail. Every sensitive action (login, upload,
signature, 2FA change, admin action) writes a row here.
"""

from datetime import datetime
from models import db


class ActivityLog(db.Model):
    __tablename__ = "Activity_Log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id", ondelete="SET NULL"), nullable=True)

    action = db.Column(db.String(100), nullable=False)         # e.g. LOGIN_SUCCESS, FILE_UPLOAD
    description = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    status = db.Column(
        db.Enum("success", "failure", "warning", name="log_status_enum"),
        default="success",
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def record(user_id, action, description=None, ip=None, agent=None, status="success"):
        """Convenience helper used throughout the app to write a log entry."""
        entry = ActivityLog(
            user_id=user_id,
            action=action,
            description=description,
            ip_address=ip,
            user_agent=agent,
            status=status,
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    def __repr__(self):
        return f"<ActivityLog {self.action} user={self.user_id} status={self.status}>"
