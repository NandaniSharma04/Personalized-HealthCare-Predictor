import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.auth_models import User, Role, UserRole, RefreshToken, AuditLog
from ..core.config import settings
import bcrypt

def get_password_hash(password: str) -> str:
    pw_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        pw_bytes = password.encode("utf-8")[:72]
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(pw_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(db: Session, user_id: int) -> str:
    jti = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    rt = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at)
    db.add(rt)
    db.commit()
    return jti


def revoke_refresh_token(db: Session, jti: str):
    rt = db.query(RefreshToken).filter_by(jti=jti).first()
    if rt:
        rt.revoked = True
        db.add(rt)
        db.commit()
        log_audit(db, rt.user_id, 'revoke_refresh', 'refresh_token', rt.id, details=f'revoked jti={jti}')


def validate_refresh_token(db: Session, jti: str) -> RefreshToken | None:
    rt = db.query(RefreshToken).filter_by(jti=jti, revoked=False).first()
    if not rt:
        return None
    if rt.expires_at < datetime.utcnow():
        return None
    return rt


def register_user(db: Session, username: str, email: str, password: str) -> User:
    hashed = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    # assign default USER role if exists
    role = db.query(Role).filter_by(name='USER').first()
    if role:
        ur = UserRole(user_id=user.id, role_id=role.id)
        db.add(ur)
        db.commit()
    log_audit(db, user.id, 'register', 'user', user.id, details='user registered')
    return user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter((User.username == username) | (User.email == username)).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def log_audit(db: Session, user_id: int | None, action: str, object_type: str | None, object_id: int | None, details: str | None = None):
    al = AuditLog(user_id=user_id, action=action, object_type=object_type, object_id=object_id, details=details)
    db.add(al)
    db.commit()
