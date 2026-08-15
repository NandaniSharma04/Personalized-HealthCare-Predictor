from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..models import Role, User
from ..schemas import BaseModel
from pydantic import BaseModel
from ..deps import require_role

router = APIRouter(prefix="/api/admin", tags=["admin"])


class RoleCreate(BaseModel):
    name: str


class RoleAssign(BaseModel):
    user_id: int
    role_name: str


@router.post("/roles/create")
def create_role(payload: RoleCreate, db: Session = Depends(get_db), current=Depends(require_role("admin"))):
    existing = db.query(Role).filter(Role.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")
    r = Role(name=payload.name)
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"ok": True, "role": {"id": r.id, "name": r.name}}


@router.post("/roles/assign")
def assign_role(payload: RoleAssign, db: Session = Depends(get_db), current=Depends(require_role("admin"))):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = db.query(Role).filter(Role.name == payload.role_name).first()
    if not role:
        role = Role(name=payload.role_name)
        db.add(role)
        db.commit()
        db.refresh(role)
    if role not in user.roles:
        user.roles.append(role)
        db.add(user)
        db.commit()
    return {"ok": True}
