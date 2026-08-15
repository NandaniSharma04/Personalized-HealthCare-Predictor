from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..monitoring.monitor import baseline_symptom_distribution, current_symptom_distribution_from_predictions, kl_divergence, prediction_metrics
from ..deps import require_any_role, get_current_user
from typing import Dict

router = APIRouter(prefix="/api/monitor", tags=["monitor"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), current=Depends(get_current_user)):
    # require analyst or admin
    _ = require_any_role(["analyst", "admin"])(current)
    metrics = prediction_metrics(db)
    return {"metrics": metrics}


@router.get("/drift")
def drift(db: Session = Depends(get_db), window: int = 500, current=Depends(get_current_user)):
    _ = require_any_role(["analyst", "admin"])(current)
    baseline = baseline_symptom_distribution()
    current = current_symptom_distribution_from_predictions(db, limit=window)
    if not baseline or not current:
        raise HTTPException(status_code=404, detail="Baseline or current distribution not available")
    # align keys
    keys = [k for k in baseline.keys() if k in current]
    p = [baseline[k] for k in keys]
    q = [current[k] for k in keys]
    from ..monitoring.monitor import kl_divergence as _kl

    score = _kl(p, q)
    # also return per-symptom delta
    deltas = {k: current[k] - baseline[k] for k in keys}
    return {"kl_divergence": score, "deltas": deltas}
