# ============================================================================
# AUTHENTICATION ROUTES (Blueprint)
# Save this as: auth.py (same folder as app.py)
# Handles: signup, login, logout, and brute-force protection.
# ============================================================================

import re
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user

from models import db, User

auth_bp = Blueprint("auth", __name__)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 10

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_password_strength(password):
    """Returns (is_valid, message). Mirrors the frontend meter so the
    server never trusts client-side validation alone."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must include at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must include at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must include at least one number."
    return True, "OK"


# ----------------------------------------------------------------------------
# SIGNUP
# ----------------------------------------------------------------------------
@auth_bp.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"success": False, "error": "All fields are required."}), 400

    if not EMAIL_RE.match(email):
        return jsonify({"success": False, "error": "Please enter a valid email address."}), 400

    valid, msg = validate_password_strength(password)
    if not valid:
        return jsonify({"success": False, "error": msg}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "An account with that email already exists."}), 409

    user = User(name=name, email=email, role="user")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return jsonify({"success": True, "user": user.to_dict()}), 201


# ----------------------------------------------------------------------------
# LOGIN
# ----------------------------------------------------------------------------
@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    remember = bool(data.get("remember", False))

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()

    # Same generic error whether the email doesn't exist or the password is
    # wrong -- don't reveal which one, that helps attackers enumerate emails.
    generic_error = {"success": False, "error": "Invalid email or password."}

    if not user:
        return jsonify(generic_error), 401

    if user.is_locked():
        minutes_left = int((user.locked_until - datetime.utcnow()).total_seconds() // 60) + 1
        return jsonify({
            "success": False,
            "error": f"Account temporarily locked due to too many failed attempts. Try again in {minutes_left} minute(s)."
        }), 423

    if not user.check_password(password):
        user.failed_attempts = (user.failed_attempts or 0) + 1
        if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
            user.failed_attempts = 0
        db.session.commit()
        return jsonify(generic_error), 401

    # successful login -- reset any failed-attempt counters
    user.failed_attempts = 0
    user.locked_until = None
    db.session.commit()

    login_user(user, remember=remember)
    return jsonify({"success": True, "user": user.to_dict()}), 200


# ----------------------------------------------------------------------------
# LOGOUT
# ----------------------------------------------------------------------------
@auth_bp.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    return jsonify({"success": True}), 200


# ----------------------------------------------------------------------------
# CURRENT USER (used by the frontend to check login state on page load)
# ----------------------------------------------------------------------------
@auth_bp.route("/api/me", methods=["GET"])
def me():
    if current_user.is_authenticated:
        return jsonify({"logged_in": True, "user": current_user.to_dict()}), 200
    return jsonify({"logged_in": False}), 200