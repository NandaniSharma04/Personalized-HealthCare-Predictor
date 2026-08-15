from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from ..ml.recommender import recommend_by_disease, recommend_by_text
from ..ml import cf_service
from ..deps import get_current_user, require_role
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
from ..models import Recommendation
from ..db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


class RecommendRequest(BaseModel):
    disease: Optional[str] = None
    text: Optional[str] = None
    top_k: int = 5
    user_id: Optional[int] = None
    alpha: float = 0.6  # weight for CF vs content (alpha*CF + (1-alpha)*content)


class InteractionPayload(BaseModel):
    item: str
    rating: Optional[float] = 1.0


@router.post("/content")
def recommend_content(req: RecommendRequest, user=Depends(get_current_user)):
    if req.disease:
        results = recommend_by_disease(req.disease, top_k=req.top_k)
    elif req.text:
        results = recommend_by_text(req.text, top_k=req.top_k)
    else:
        raise HTTPException(status_code=400, detail="Provide `disease` or `text` in request")
    return {"results": [{"disease": d, "score": s} for d, s in results]}


@router.post("/interaction")
def record_interaction(payload: InteractionPayload, user=Depends(get_current_user)):
    uid = user.id if user else "anon"
    cf_service.append_interaction(str(uid), payload.item, payload.rating or 1.0)
    return {"ok": True}


@router.post("/train_cf")
def train_cf(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current=Depends(require_role("admin"))):
    # run training in background
    background_tasks.add_task(cf_service.train_cf_model)
    return {"ok": True, "message": "CF training started in background"}


@router.post("/hybrid")
def recommend_hybrid(req: RecommendRequest, user=Depends(get_current_user)):
    # get content candidates (top 50)
    if req.text:
        content = recommend_by_text(req.text, top_k=50)
    elif req.disease:
        content = recommend_by_disease(req.disease, top_k=50)
    else:
        raise HTTPException(status_code=400, detail="Provide `disease` or `text` in request")

    items = [d for d, _ in content]
    cf_model = cf_service.load_cf_model()

    results = []
    for d, content_score in content:
        cf_score = None
        if cf_model is not None and user is not None:
            try:
                pred = cf_model.predict(str(user.id), str(d))
                cf_score = float(pred.est)
            except Exception:
                cf_score = None
        # normalize cf_score to 0-1 if possible (Surprise predictions are typically 1-5)
        if cf_score is not None:
            cf_score_norm = (cf_score - 1.0) / 4.0
        else:
            cf_score_norm = 0.0
        # content_score is cosine similarity [0,1]
        combined = req.alpha * cf_score_norm + (1 - req.alpha) * float(content_score)
        results.append((d, combined, float(content_score), cf_score))

    results.sort(key=lambda x: x[1], reverse=True)
    top = results[: req.top_k]
    return {"results": [{"disease": d, "score": s, "content_score": cs, "cf_score": cf} for d, s, cs, cf in top]}
