from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from .db.session import get_db
from .core import security
from .models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = security.decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(role_name: str):
    def _checker(current_user: User = Depends(get_current_user)):
        names = [r.name for r in current_user.roles]
        if role_name not in names:
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return current_user

    return _checker


def require_any_role(role_names: list[str]):
    def _checker(current_user: User = Depends(get_current_user)):
        names = [r.name for r in current_user.roles]
        if not any(r in names for r in role_names):
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return current_user

    return _checker
