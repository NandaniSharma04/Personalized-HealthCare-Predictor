from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies.deps import get_token
from ..core.database import SessionLocal
from ..services.user_service import UserService
from ..schemas.user import ProfileOut, ProfileUpdate, MedicalProfileOut, MedicalProfileUpdate, SymptomInput, NotificationOut, DashboardOut, FeedbackIn

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/users/me', response_model=ProfileOut)
def get_my_profile(subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    profile = svc.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Profile not found')
    return profile


@router.put('/users/me', response_model=ProfileOut)
def update_my_profile(payload: ProfileUpdate, subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    updated = svc.update_profile(user_id, payload.dict(exclude_none=True))
    return updated


@router.get('/users/me/medical', response_model=MedicalProfileOut)
def get_my_medical(subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    mp = svc.get_medical_profile(user_id)
    if not mp:
        raise HTTPException(status_code=404, detail='Medical profile not found')
    return mp


@router.put('/users/me/medical', response_model=MedicalProfileOut)
def update_my_medical(payload: MedicalProfileUpdate, subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    updated = svc.update_medical_profile(user_id, payload.dict(exclude_none=True))
    return updated


@router.post('/users/me/symptoms')
def submit_symptoms(payload: SymptomInput, subject=Depends(get_token)):
    # Forwards to recommendation/prediction pipeline (ModelService)
    return {"ok": True, "received": payload.symptoms}


@router.get('/users/me/notifications', response_model=list[NotificationOut])
def list_notifications(subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    return svc.list_notifications(user_id)


@router.post('/users/me/notifications/{nid}/read')
def mark_notification_read(nid: int, subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    n = svc.mark_notification_read(nid, user_id)
    if not n:
        raise HTTPException(status_code=404, detail='Notification not found')
    return {"ok": True}


@router.get('/users/me/dashboard', response_model=DashboardOut)
def dashboard(subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    profile = svc.get_profile(user_id)
    medical = svc.get_medical_profile(user_id)
    preds = svc.get_prediction_history(user_id, limit=5)
    recs = svc.get_recommendations(user_id, limit=5)
    notes = svc.list_notifications(user_id)
    unread = sum(1 for n in notes if not n.is_read)
    return {
        'profile': profile,
        'medical': medical,
        'recent_predictions': preds,
        'recent_recommendations': recs,
        'unread_notifications': unread,
    }


@router.get('/users/me/predictions')
def my_predictions(subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    return svc.get_prediction_history(user_id, limit=100)


@router.get('/users/me/recommendations')
def my_recommendations(subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    return svc.get_recommendations(user_id, limit=100)


@router.get('/users/me/activity')
def my_activity(subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    return svc.get_activity(user_id, limit=200)


@router.get('/users/me/saved')
def my_saved(subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    return svc.get_saved_items(user_id)


@router.post('/users/me/feedback')
def submit_feedback(payload: FeedbackIn, subject=Depends(get_token), db: Session = Depends(get_db)):
    user_id = int(subject)
    svc = UserService(db)
    fid = svc.submit_feedback(user_id, payload.target_type, payload.target_id, payload.rating, payload.comment)
    return {"id": fid}

