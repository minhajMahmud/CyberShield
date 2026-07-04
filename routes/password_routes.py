"""
routes/password_routes.py
-----------------------------
Password Strength Checker module. Works for both anonymous
visitors (no history saved with a user_id) and logged-in users
(history saved against their account). The plaintext password is
NEVER stored - only a SHA-256 sample hash for record-keeping.
"""

import hashlib
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user

from models import db, PasswordCheckHistory
from utils.password_checker import check_password_strength

password_bp = Blueprint("password", __name__)


@password_bp.route("/password-checker", methods=["GET"])
def password_checker_page():
    return render_template("password_checker.html")


@password_bp.route("/api/password-check", methods=["POST"])
def password_check_api():
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")

    if not password:
        return jsonify({"error": "No password provided"}), 400

    result = check_password_strength(password)

    history = PasswordCheckHistory(
        user_id=current_user.id if current_user.is_authenticated else None,
        password_hash_sample=hashlib.sha256(password.encode()).hexdigest(),
        strength_score=result["score"],
        strength_label=result["label"],
        estimated_crack_time=result["estimated_crack_time"],
    )
    db.session.add(history)
    db.session.commit()
    
    # Log activity for dashboard stats
    if current_user.is_authenticated:
        from models import ActivityLog
        ActivityLog.record(
            current_user.id, 
            "PASSWORD_CHECK", 
            f"Strength: {result['label']}", 
            request.remote_addr,
            request.headers.get("User-Agent", "")[:255]
        )

    return jsonify(result)
