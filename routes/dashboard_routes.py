"""
routes/dashboard_routes.py
-----------------------------
Authenticated user dashboard - quick stats + recent activity.
"""

from datetime import datetime
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import FileRecord, DigitalSignature, ActivityLog

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def home():
    file_count = FileRecord.query.filter_by(user_id=current_user.id, is_deleted=False).count()
    signature_count = DigitalSignature.query.filter_by(user_id=current_user.id).count()
    
    # Count password checks from activity log
    password_check_count = ActivityLog.query.filter_by(
        user_id=current_user.id, 
        action="PASSWORD_CHECK"
    ).count()
    
    recent_activity = (
        ActivityLog.query.filter_by(user_id=current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )
    
    current_time = datetime.now().strftime('%b %d, %Y %H:%M')
    
    return render_template(
        "dashboard.html",
        file_count=file_count,
        signature_count=signature_count,
        password_check_count=password_check_count,
        recent_activity=recent_activity,
        current_time=current_time,
    )
