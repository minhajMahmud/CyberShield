"""
routes/twofa_routes.py
--------------------------
Two-Factor Authentication settings: enable/disable, TOTP QR setup,
and resending email OTP codes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db, OTP, ActivityLog
from utils.otp_utils import (
    generate_totp_secret, get_totp_uri, verify_totp,
    generate_qr_code_base64, generate_numeric_otp, otp_expiry,
)

twofa_bp = Blueprint("twofa", __name__)


@twofa_bp.route("/2fa-settings", methods=["GET"])
@login_required
def settings():
    qr_code = None
    totp_uri = None
    if not current_user.is_2fa_enabled:
        # Prepare (but don't yet save) a fresh secret for setup
        if not current_user.twofa_secret:
            current_user.twofa_secret = generate_totp_secret()
            db.session.commit()
        totp_uri = get_totp_uri(current_user.twofa_secret, current_user.email)
        qr_code = generate_qr_code_base64(totp_uri)

    return render_template("twofa_settings.html", qr_code=qr_code)


@twofa_bp.route("/2fa-settings/enable", methods=["POST"])
@login_required
def enable():
    code = request.form.get("otp_code", "").strip()
    if current_user.twofa_secret and verify_totp(current_user.twofa_secret, code):
        current_user.is_2fa_enabled = True
        db.session.commit()
        ActivityLog.record(current_user.id, "2FA_ENABLED", None, request.remote_addr,
                            request.headers.get("User-Agent", "")[:255])
        flash("Two-Factor Authentication enabled successfully.", "success")
    else:
        flash("Invalid authenticator code. Please try again.", "danger")
    return redirect(url_for("twofa.settings"))


@twofa_bp.route("/2fa-settings/disable", methods=["POST"])
@login_required
def disable():
    current_user.is_2fa_enabled = False
    current_user.twofa_secret = None
    db.session.commit()
    ActivityLog.record(current_user.id, "2FA_DISABLED", None, request.remote_addr,
                        request.headers.get("User-Agent", "")[:255])
    flash("Two-Factor Authentication disabled.", "info")
    return redirect(url_for("twofa.settings"))


@twofa_bp.route("/login/resend-otp", methods=["POST"])
def resend_otp():
    from flask import session
    from models import User

    user_id = session.get("pending_2fa_user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    otp = OTP(user_id=user.id, otp_code=generate_numeric_otp(), purpose="login", expires_at=otp_expiry())
    db.session.add(otp)
    db.session.commit()

    # Display OTP code on screen (email service removed)
    flash(f"Your new OTP code is: {otp.otp_code} (Valid for 5 minutes)", "info")

    return redirect(url_for("auth.verify_login_otp"))
