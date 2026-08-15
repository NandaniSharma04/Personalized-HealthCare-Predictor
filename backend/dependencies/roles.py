from fastapi import Depends, HTTPException
from ..dependencies.deps import get_token
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models.auth_models import UserRole, Role


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_role(role_name: str):
    def _checker(subject=Depends(get_token), db: Session = Depends(get_db)):
        # subject is user id string
        user_id = int(subject)
        # check roles
        roles = db.query(Role.name).join(UserRole, Role.id == UserRole.role_id).filter(UserRole.user_id == user_id).all()
        names = [r[0] for r in roles]
        if role_name not in names:
            raise HTTPException(status_code=403, detail='Forbidden')
        return True

    return _checker
