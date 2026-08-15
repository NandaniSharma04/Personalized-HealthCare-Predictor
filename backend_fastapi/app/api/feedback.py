from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..deps import get_current_user, require_role
from ..models import Feedback, UserActivity
from ..ml.sentiment import analyze_sentiment
from ..schemas import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackOut)
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        sentiment = analyze_sentiment(payload.text)
        fb = Feedback(user_id=user.id if user else None, text=payload.text, sentiment_score=sentiment["score"], sentiment_label=sentiment["label"], metadata=payload.metadata)
        db.add(fb)
        db.commit()
        db.refresh(fb)

        ua = UserActivity(user_id=user.id if user else None, event_type="feedback_submitted", event_payload={"feedback_id": fb.id, "sentiment": sentiment})
        db.add(ua)
        db.commit()

        return fb
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[FeedbackOut])
def list_feedback(db: Session = Depends(get_db), current=Depends(require_role("analyst"))):
    return db.query(Feedback).order_by(Feedback.created_at.desc()).limit(200).all()
