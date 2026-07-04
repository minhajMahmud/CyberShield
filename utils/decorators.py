"""
utils/decorators.py
---------------------
Cross-cutting security helpers: role-based access control, a very
lightweight in-memory rate limiter for login attempts, and file
upload validation (extension whitelist + size check).
"""

import time
from functools import wraps
from collections import defaultdict

from flask import abort, request, flash, redirect, url_for, render_template
from flask_login import current_user

# ---------------------------------------------------------------
# Role-based access control
# ---------------------------------------------------------------


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------
# Simple in-memory rate limiter (sufficient for a class project;
# swap for Flask-Limiter + Redis in a real production deployment)
# ---------------------------------------------------------------

_attempts = defaultdict(list)  # key -> [timestamps]


def rate_limited(max_attempts: int = 5, window_seconds: int = 60):
    """Decorator: limits a view to `max_attempts` calls per `window_seconds`
    per client IP. Used on the login route to slow down brute-force attempts."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Only throttle the actual submission (POST); GET requests just
            # render the form and must never be rate-limited, otherwise a
            # tripped limiter would redirect back to this same route on every
            # subsequent page load and create an infinite redirect loop.
            if request.method != "POST":
                return f(*args, **kwargs)

            key = f"{request.remote_addr}:{f.__name__}"
            now = time.time()
            _attempts[key] = [t for t in _attempts[key] if now - t < window_seconds]
            if len(_attempts[key]) >= max_attempts:
                flash("Too many attempts. Please wait a minute and try again.", "danger")
                return render_template("login.html")
            _attempts[key].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------
# File validation
# ---------------------------------------------------------------


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def validate_file_size(file_stream, max_bytes: int) -> bool:
    file_stream.seek(0, 2)  # seek to end
    size = file_stream.tell()
    file_stream.seek(0)
    return size <= max_bytes
