from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..schemas import UserCreate, UserOut
from ..models import User
from ..deps import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    # reuse auth register logic via same hashing
    from ..core import security
    hashed = security.get_password_hash(payload.password)
    user = User(email=payload.email, name=payload.name, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
