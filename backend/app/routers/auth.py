from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from ..schemas.auth import UserCreate, LoginRequest, Token, RefreshRequest
from ..services.auth_service import register_user, authenticate_user, create_access_token, create_refresh_token, revoke_refresh_token, validate_refresh_token, log_audit
from ..core.database import SessionLocal
from ..dependencies.deps import get_token

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/auth/register', status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    user = register_user(db, payload.username, payload.email, payload.password)
    return {"id": user.id, "username": user.username, "email": user.email}


@router.post('/auth/login', response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    access = create_access_token({"sub": str(user.id)})
    refresh_jti = create_refresh_token(db, user.id)
    # return refresh token as opaque value (jti)
    return {"access_token": access, "token_type": "bearer", "refresh_token": refresh_jti}


@router.post('/auth/logout')
def logout(payload: RefreshRequest, db: Session = Depends(get_db), subject=Depends(get_token)):
    # revoke provided refresh token
    revoke_refresh_token(db, payload.refresh_token)
    log_audit(db, int(subject), 'logout', None, None, details='user logged out')
    return {"ok": True}


@router.post('/auth/refresh', response_model=Token)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    rt = validate_refresh_token(db, payload.refresh_token)
    if not rt:
        raise HTTPException(status_code=401, detail='Invalid refresh token')
    # rotate refresh token
    revoke_refresh_token(db, payload.refresh_token)
    new_jti = create_refresh_token(db, rt.user_id)
    access = create_access_token({"sub": str(rt.user_id)})
    return {"access_token": access, "token_type": "bearer", "refresh_token": new_jti}
