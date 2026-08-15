"""
Comprehensive Security, Authentication & Role-Based Access Control (RBAC) Module
"""
import bcrypt
from functools import wraps
from flask import jsonify, request
from flask_login import current_user
from backend.utils.db import db

def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    try:
        pw_bytes = password.encode("utf-8")[:72]
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(pw_bytes, hashed_bytes)
    except Exception:
        return False

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                "success": False,
                "error": "Authentication required",
                "code": "UNAUTHORIZED"
            }), 401
        
        status = getattr(current_user, 'status', 'active')
        if status != 'active':
            return jsonify({
                "success": False,
                "error": f"Account is {status}",
                "code": "ACCOUNT_DISABLED"
            }), 403
            
        return f(*args, **kwargs)
    return decorated_function

def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({
                    "success": False,
                    "error": "Authentication required",
                    "code": "UNAUTHORIZED"
                }), 401

            user_status = getattr(current_user, 'status', 'active')
            if user_status != 'active':
                return jsonify({
                    "success": False,
                    "error": f"Account is {user_status}",
                    "code": "ACCOUNT_DISABLED"
                }), 403

            user_role = getattr(current_user, 'role', 'user')
            allowed_roles = set(roles)
            allowed_roles.add("admin") # Admin always has access

            if user_role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "error": f"Access forbidden: Requires one of {list(roles)}",
                    "code": "FORBIDDEN"
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_audit(actor: str, action: str, entity: str = None, result: str = "SUCCESS"):
    try:
        from backend.models import AuditLog
        log_entry = AuditLog(
            actor=actor,
            action=action,
            entity=entity,
            result=result
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        print(f"[SECURITY AUDIT WARN] Failed to log audit event: {err}")
