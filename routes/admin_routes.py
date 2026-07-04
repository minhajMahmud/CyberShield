"""
routes/admin_routes.py
--------------------------
Admin dashboard: user management + system-wide activity log view.
Protected by the @admin_required decorator (role='admin' only).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from models import db, User, ActivityLog, FileRecord, DigitalSignature
from utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@login_required
@admin_required
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    stats = {
        "total_users": User.query.count(),
        "total_files": FileRecord.query.filter_by(is_deleted=False).count(),
        "total_signatures": DigitalSignature.query.count(),
        "users_with_2fa": User.query.filter_by(is_2fa_enabled=True).count(),
    }
    recent_logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(25).all()
    return render_template("admin_dashboard.html", users=users, stats=stats, recent_logs=recent_logs)


@admin_bp.route("/admin/users/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@admin_required
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active_flag = not user.is_active_flag
    db.session.commit()
    flash(f"User '{user.username}' {'enabled' if user.is_active_flag else 'disabled'}.", "info")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/users/<int:user_id>/make-admin", methods=["POST"])
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.role = "admin"
    db.session.commit()
    flash(f"User '{user.username}' is now an admin.", "success")
    return redirect(url_for("admin.dashboard"))
