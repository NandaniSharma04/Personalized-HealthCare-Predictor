"""
Authentication & User Identity Service with Activity Tracking & Notifications
"""
from datetime import datetime
from backend.utils.db import db
from backend.models import User
from backend.utils.security import hash_password, check_password, log_audit
from backend.utils.activity_tracker import track_activity, create_notification

def register_user(name: str, email: str, password: str, role: str = "user") -> User:
    email_clean = email.strip().lower()
    existing = User.query.filter_by(email=email_clean).first()
    if existing:
        log_audit(email_clean, "REGISTER", "User", "FAILED_DUPLICATE")
        raise ValueError("User with this email already exists")
    
    user = User(
        name=name.strip(),
        email=email_clean,
        password_hash=hash_password(password),
        role=role,
        status="active"
    )
    db.session.add(user)
    db.session.commit()
    
    track_activity(user.id, "REGISTER", {"role": role})
    create_notification(user.id, "Welcome to HealthAI", "Your account has been created. Start by checking your symptoms or completing your health profile.")
    log_audit(email_clean, "REGISTER", "User", "SUCCESS")
    return user

def authenticate_user(email: str, password: str) -> User | None:
    email_clean = email.strip().lower()
    user = User.query.filter_by(email=email_clean).first()
    if not user:
        log_audit(email_clean, "LOGIN", "User", "FAILED_NOT_FOUND")
        return None
    
    if not check_password(password, user.password_hash):
        user.failed_attempts = (user.failed_attempts or 0) + 1
        db.session.commit()
        log_audit(email_clean, "LOGIN", "User", "FAILED_INVALID_PASSWORD")
        return None

    if user.status != "active":
        log_audit(email_clean, "LOGIN", "User", f"FAILED_ACCOUNT_{user.status.upper()}")
        raise PermissionError(f"Account is {user.status}")

    user.failed_attempts = 0
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    track_activity(user.id, "LOGIN", {"timestamp": user.last_login.isoformat()})
    log_audit(email_clean, "LOGIN", "User", "SUCCESS")
    return user

def change_password(user: User, old_password: str, new_password: str) -> bool:
    if not check_password(old_password, user.password_hash):
        log_audit(user.email, "CHANGE_PASSWORD", "User", "FAILED_INVALID_OLD_PASSWORD")
        raise ValueError("Invalid current password")
    
    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    track_activity(user.id, "SECURITY_EVENT", {"action": "change_password"})
    create_notification(user.id, "Security Alert", "Your account password was recently changed.")
    log_audit(user.email, "CHANGE_PASSWORD", "User", "SUCCESS")
    return True

def reset_password(email: str, new_password: str) -> bool:
    email_clean = email.strip().lower()
    user = User.query.filter_by(email=email_clean).first()
    if not user:
        log_audit(email_clean, "FORGOT_PASSWORD", "User", "FAILED_NOT_FOUND")
        raise ValueError("No account associated with this email")
    
    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    track_activity(user.id, "SECURITY_EVENT", {"action": "reset_password"})
    create_notification(user.id, "Security Alert", "Your account password was reset successfully.")
    log_audit(email_clean, "FORGOT_PASSWORD", "User", "SUCCESS")
    return True
