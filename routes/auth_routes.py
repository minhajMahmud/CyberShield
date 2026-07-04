"""
routes/auth_routes.py
-----------------------
Registration, login (with optional 2FA challenge), logout, and the
profile page. Implements: bcrypt password hashing, account lockout
after repeated failures, activity logging, and CSRF-protected forms
(via Flask-WTF, enabled globally in app.py).
"""

from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from models import db, User, ActivityLog, OTP
from utils.decorators import rate_limited
from utils.otp_utils import generate_numeric_otp, otp_expiry, verify_totp

auth_bp = Blueprint("auth", __name__)


def _client_meta():
    return request.remote_addr, request.headers.get("User-Agent", "")[:255]


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        from app import bcrypt

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([username, email, password]):
            flash("Please fill in all required fields.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email is already registered.", "danger")
            return render_template("register.html")

        # Store registration data in session temporarily - DON'T create user yet
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        
        session["pending_registration"] = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password_hash": hashed
        }
        
        # Generate verification code and store in session
        otp_code = generate_numeric_otp()
        session["pending_otp"] = {
            "code": otp_code,
            "expires_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        }

        # Try to send verification email
        from app import mail
        from flask_mail import Message

        try:
            msg = Message(
                subject="Verify Your CyberShield Account",
                recipients=[email],
                body=f"""
Welcome to CyberShield!

Thank you for registering with CyberShield - Your Secure Digital Security Platform.

Your email verification code is: {otp_code}

This code will expire in 30 minutes.

Please enter this code on the verification page to complete your registration and activate your account.

If you didn't create this account, please ignore this email.

Best regards,
CyberShield Security Team
                """
            )
            mail.send(msg)
            flash("Registration successful! A verification code has been sent to your email.", "success")
            flash(f"Check {email} for your verification code.", "info")
            return redirect(url_for("auth.verify_email"))
        except Exception as e:
            # Clear session if email fails
            session.pop("pending_registration", None)
            session.pop("pending_otp", None)
            flash("Registration failed: Unable to send verification email.", "danger")
            flash(f"Please check your email address and try again. Error: {str(e)}", "warning")
            return redirect(url_for("auth.register"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@rate_limited(max_attempts=5, window_seconds=60)
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        from app import bcrypt

        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        ip, agent = _client_meta()

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            if user:
                user.failed_attempts += 1
                if user.failed_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                db.session.commit()
            ActivityLog.record(user.id if user else None, "LOGIN_FAILED", identifier, ip, agent, "failure")
            flash("Invalid username/email or password.", "danger")
            return render_template("login.html")

        if user.is_locked():
            flash("Account temporarily locked due to repeated failed attempts. Try again later.", "danger")
            return render_template("login.html")

        if not user.is_active:
            flash("This account has been disabled. Contact an administrator.", "danger")
            return render_template("login.html")

        # Reset failed-attempt counter on success
        user.failed_attempts = 0
        user.locked_until = None
        db.session.commit()

        # Debug: Check 2FA status
        print(f"[DEBUG] User: {user.username}")
        print(f"[DEBUG] is_2fa_enabled: {user.is_2fa_enabled}")
        print(f"[DEBUG] twofa_secret exists: {bool(user.twofa_secret)}")

        if user.is_2fa_enabled:
            # Stash pending user id in session; full login completes after OTP verification
            session["pending_2fa_user_id"] = user.id
            
            # If user has TOTP configured (Google Authenticator), use that
            # Otherwise fall back to email OTP
            if user.twofa_secret:
                flash("Enter the 6-digit code from your Google Authenticator app.", "info")
            else:
                # Fallback: Generate email OTP (should not happen if 2FA properly configured)
                otp = OTP(
                    user_id=user.id,
                    otp_code=generate_numeric_otp(),
                    purpose="login",
                    expires_at=otp_expiry(),
                )
                db.session.add(otp)
                db.session.commit()
                flash(f"Your OTP code is: {otp.otp_code} (Valid for 5 minutes)", "info")

            return redirect(url_for("auth.verify_login_otp"))

        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        ActivityLog.record(user.id, "LOGIN_SUCCESS", None, ip, agent)
        return redirect(url_for("dashboard.home"))

    return render_template("login.html")


@auth_bp.route("/login/verify-otp", methods=["GET", "POST"])
def verify_login_otp():
    user_id = session.get("pending_2fa_user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    ip, agent = _client_meta()

    if request.method == "POST":
        code = request.form.get("otp_code", "").strip()

        verified = False
        # Prioritize TOTP (Google Authenticator) if configured
        if user.twofa_secret:
            verified = verify_totp(user.twofa_secret, code)
        else:
            # Fallback: Check email OTP
            otp = (
                OTP.query.filter_by(user_id=user.id, purpose="login", is_used=False)
                .order_by(OTP.id.desc())
                .first()
            )
            if otp and not otp.is_expired() and otp.otp_code == code:
                otp.is_used = True
                db.session.commit()
                verified = True
            elif otp:
                otp.attempts += 1
                db.session.commit()

        if verified:
            session.pop("pending_2fa_user_id", None)
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            ActivityLog.record(user.id, "LOGIN_2FA_SUCCESS", None, ip, agent)
            return redirect(url_for("dashboard.home"))

        ActivityLog.record(user.id, "LOGIN_2FA_FAILED", None, ip, agent, "failure")
        flash("Invalid or expired code.", "danger")

    return render_template("login.html", otp_stage=True)


@auth_bp.route("/logout")
@login_required
def logout():
    ip, agent = _client_meta()
    ActivityLog.record(current_user.id, "LOGOUT", None, ip, agent)
    logout_user()
    flash("You have been logged out.", "info")
    
    # Return logout page with session clearing script
    return render_template("logout.html")


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.full_name = request.form.get("full_name", current_user.full_name)
        db.session.commit()
        flash("Profile updated.", "success")
    return render_template("profile.html")


@auth_bp.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    # Check if there's pending registration
    pending_reg = session.get("pending_registration")
    pending_otp = session.get("pending_otp")
    
    if not pending_reg or not pending_otp:
        flash("No pending email verification. Please register first.", "warning")
        return redirect(url_for("auth.register"))

    email = pending_reg["email"]
    
    # Check if OTP expired
    expires_at = datetime.fromisoformat(pending_otp["expires_at"])
    if datetime.utcnow() > expires_at:
        session.pop("pending_registration", None)
        session.pop("pending_otp", None)
        flash("Verification code has expired. Please register again.", "danger")
        return redirect(url_for("auth.register"))

    if request.method == "POST":
        code = request.form.get("otp_code", "").strip()
        ip, agent = _client_meta()

        if code == pending_otp["code"]:
            # Code is correct - NOW create the user in database
            from app import bcrypt
            
            user = User(
                username=pending_reg["username"],
                email=pending_reg["email"],
                full_name=pending_reg["full_name"],
                password_hash=pending_reg["password_hash"],
                email_verified=True  # Already verified
            )
            db.session.add(user)
            db.session.commit()
            
            # Clear session
            session.pop("pending_registration", None)
            session.pop("pending_otp", None)
            
            ActivityLog.record(user.id, "REGISTER", "Account created and email verified", ip, agent)
            flash("Email verified successfully! Your account has been created. You can now log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Invalid verification code. Please try again.", "danger")

    return render_template("verify_email.html", email=email)


@auth_bp.route("/verify-email/resend", methods=["POST"])
def resend_verification():
    pending_reg = session.get("pending_registration")
    
    if not pending_reg:
        flash("No pending email verification.", "warning")
        return redirect(url_for("auth.register"))

    email = pending_reg["email"]
    
    # Generate new OTP
    otp_code = generate_numeric_otp()
    session["pending_otp"] = {
        "code": otp_code,
        "expires_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    }

    # Send new verification code via email
    from app import mail
    from flask_mail import Message

    try:
        msg = Message(
            subject="New Verification Code - CyberShield",
            recipients=[email],
            body=f"""
Your new CyberShield verification code is: {otp_code}

This code will expire in 30 minutes.

Please enter this code on the verification page to complete your registration.

If you didn't request this code, please ignore this email.

Best regards,
CyberShield Security Team
            """
        )
        mail.send(msg)
        flash("A new verification code has been sent to your email!", "success")
    except Exception as e:
        flash(f"Failed to send verification code. Please try registering again.", "danger")
        flash(f"Error: {str(e)}", "warning")

    return redirect(url_for("auth.verify_email"))
