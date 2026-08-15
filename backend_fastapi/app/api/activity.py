from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..schemas import BaseModel
from pydantic import BaseModel
from ..models import UserActivity
from ..deps import get_current_user

router = APIRouter(prefix="/api/activity", tags=["activity"])


class ActivityPayload(BaseModel):
    event_type: str
    event_payload: dict = {}


@router.post("/track")
def track_activity(payload: ActivityPayload, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        record = UserActivity(user_id=user.id, event_type=payload.event_type, event_payload=payload.event_payload)
        db.add(record)
        db.commit()
        return {"ok": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
