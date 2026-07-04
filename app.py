"""
app.py
------
CyberShield application entry point.

Wires together:
- SQLAlchemy (models/db)
- Flask-Login (session-based auth)
- Flask-Bcrypt (password hashing)
- Flask-Mail (OTP delivery)
- Flask-WTF CSRF protection (global)
- Security headers + error handlers
- All blueprints (routes/)
"""

import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf import CSRFProtect

from config import config_by_name
from models import db, User

bcrypt = Bcrypt()
mail = Mail()
csrf = CSRFProtect()
login_manager = LoginManager()


def create_app(env: str = None):
    env = env or os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name[env])

    # Ensure storage directories exist
    for folder in (app.config["UPLOAD_FOLDER"], app.config["ENCRYPTED_FOLDER"], app.config["KEYS_FOLDER"]):
        os.makedirs(folder, exist_ok=True)

    # ---- Extensions ----
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ---- Blueprints ----
    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.file_routes import file_bp
    from routes.password_routes import password_bp
    from routes.signature_routes import signature_bp
    from routes.twofa_routes import twofa_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(password_bp)
    app.register_blueprint(signature_bp)
    app.register_blueprint(twofa_bp)
    app.register_blueprint(admin_bp)

    # The password-check JSON API is intentionally exempt from CSRF since it's a
    # same-origin fetch() call with no session side effects beyond a history row.
    csrf.exempt(password_bp)

    # ---- Security headers (defense in depth, complements HTTPS at the proxy) ----
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "img-src 'self' data:;"
        )
        if app.config.get("SESSION_COOKIE_SECURE"):
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response

    # ---- Error handlers ----
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("404.html", forbidden=True), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
