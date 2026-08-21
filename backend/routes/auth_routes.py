"""
Complete Authentication & Identity Management Routes
"""
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from backend.utils.db import db
from backend.services.auth_service import (
    register_user,
    authenticate_user,
    change_password,
    reset_password
)
from backend.utils.security import require_auth, log_audit

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = data.get("name") or data.get("username") or ""
    email = data.get("email", "")
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "error": "Name, email, and password are required",
            "code": "INVALID_INPUT"
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "error": "Password must be at least 6 characters long",
            "code": "WEAK_PASSWORD"
        }), 400

    try:
        # Public registration must never be allowed to choose a privileged role.
        # Administrator accounts are provisioned separately by a trusted operator.
        user = register_user(name, email, password, role="user")
        # Do NOT auto-login — user must explicitly log in after signup
        return jsonify({
            "success": True,
            "message": "Account created successfully. Please log in.",
            "user": user.to_dict()
        }), 201
    except ValueError as err:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(err),
            "code": "DUPLICATE_USER"
        }), 409
    except Exception as exc:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Registration failed: {str(exc)}",
            "code": "SERVER_ERROR"
        }), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")
    remember = data.get("remember", False)

    if not email or not password:
        return jsonify({
            "success": False,
            "error": "Email and password are required",
            "code": "INVALID_INPUT"
        }), 400

    try:
        user = authenticate_user(email, password)
        if not user:
            return jsonify({
                "success": False,
                "error": "Invalid email or password",
                "code": "INVALID_CREDENTIALS"
            }), 401
        
        login_user(user, remember=remember)
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": user.to_dict()
        }), 200
    except PermissionError as perm_err:
        return jsonify({
            "success": False,
            "error": str(perm_err),
            "code": "ACCOUNT_DISABLED"
        }), 403
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": "Login processing failed",
            "code": "SERVER_ERROR"
        }), 500

@auth_bp.route("/logout", methods=["POST"])
def logout():
    actor = current_user.email if current_user.is_authenticated else "anonymous"
    logout_user()
    log_audit(actor, "LOGOUT", "User", "SUCCESS")
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200

@auth_bp.route("/me", methods=["GET"])
def me():
    if not current_user.is_authenticated:
        return jsonify({
            "success": True,
            "logged_in": False,
            "user": None
        }), 200

    status = getattr(current_user, 'status', 'active')
    if status != "active":
        logout_user()
        return jsonify({
            "success": False,
            "logged_in": False,
            "error": f"Account is {status}",
            "code": "ACCOUNT_DISABLED"
        }), 403

    return jsonify({
        "success": True,
        "logged_in": True,
        "user": current_user.to_dict()
    }), 200

@auth_bp.route("/change-password", methods=["POST"])
@require_auth
def change_user_password():
    data = request.get_json(silent=True) or {}
    old_pw = data.get("old_password", "")
    new_pw = data.get("new_password", "")

    if not old_pw or not new_pw:
        return jsonify({
            "success": False,
            "error": "Old and new password are required",
            "code": "INVALID_INPUT"
        }), 400

    if len(new_pw) < 6:
        return jsonify({
            "success": False,
            "error": "New password must be at least 6 characters long",
            "code": "WEAK_PASSWORD"
        }), 400

    try:
        change_password(current_user, old_pw, new_pw)
        return jsonify({
            "success": True,
            "message": "Password changed successfully"
        }), 200
    except ValueError as err:
        return jsonify({
            "success": False,
            "error": str(err),
            "code": "INVALID_OLD_PASSWORD"
        }), 400

@auth_bp.route("/forgot-password", methods=["POST"])
@auth_bp.route("/forgot", methods=["POST"])
def forgot_password_route():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    new_password = data.get("new_password") or data.get("newPassword")

    if not email:
        return jsonify({
            "success": False,
            "error": "Email is required",
            "code": "INVALID_INPUT"
        }), 400

    if new_password:
        try:
            reset_password(email, new_password)
            return jsonify({
                "success": True,
                "message": "Password reset successfully"
            }), 200
        except ValueError as err:
            return jsonify({
                "success": False,
                "error": str(err),
                "code": "USER_NOT_FOUND"
            }), 404

    return jsonify({
        "success": True,
        "message": "If an account exists, a password reset link has been dispatched"
    }), 200
