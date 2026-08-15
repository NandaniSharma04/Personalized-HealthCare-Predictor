from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..deps import require_any_role
from ..models import TrainingReport, ModelVersion, Prediction, Disease, Symptom, Patient, User
from ..schemas import RoleOut
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

router = APIRouter(prefix="/api/analyst", tags=["analyst"])


@router.get("/training-reports")
def list_training_reports(db: Session = Depends(get_db), current=Depends(require_any_role(["analyst", "admin"]))):
    rows = db.query(TrainingReport).order_by(TrainingReport.created_at.desc()).limit(50).all()
    return [{"run_id": r.run_id, "summary": r.summary, "created_at": r.created_at.isoformat() if r.created_at else None} for r in rows]


@router.get("/model-versions")
def list_model_versions(db: Session = Depends(get_db), current=Depends(require_any_role(["analyst", "admin"]))):
    rows = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).limit(50).all()
    return [{"id": r.id, "name": r.name, "version": r.version, "metrics": r.metrics, "created_at": r.created_at.isoformat() if r.created_at else None} for r in rows]


@router.get("/prediction-stats")
def prediction_stats(days: int = 7, db: Session = Depends(get_db), current=Depends(require_any_role(["analyst", "admin"]))):
    since = datetime.utcnow() - timedelta(days=days)
    q = db.query(Prediction.predicted_disease, func.count(Prediction.id)).filter(Prediction.created_at >= since).group_by(Prediction.predicted_disease)
    # import func locally
    from sqlalchemy import func
    rows = q.all()
    return {r[0]: int(r[1]) for r in rows}


@router.get("/data-summary")
def data_summary(db: Session = Depends(get_db), current=Depends(require_any_role(["analyst", "admin"]))):
    counts = {}
    counts["users"] = db.query(User).count()
    counts["patients"] = db.query(Patient).count()
    counts["diseases"] = db.query(Disease).count()
    counts["symptoms"] = db.query(Symptom).count()
    counts["predictions"] = db.query(Prediction).count()
    return counts


@router.get("/feature-importance")
def feature_importance(db: Session = Depends(get_db), current=Depends(require_any_role(["analyst", "admin"]))):
    # Try to read latest training report for feature importance
    report = db.query(TrainingReport).order_by(TrainingReport.created_at.desc()).first()
    if report and report.summary and isinstance(report.summary, dict):
        fi = report.summary.get("feature_importances") or report.summary.get("feature_importance")
        if fi:
            return fi
    # Fallback: try to read backend/ml/training_report.json file
    repo_root = Path(__file__).resolve().parents[3]
    tr_file = repo_root / "backend" / "ml" / "training_report.json"
    if tr_file.exists():
        data = json.loads(tr_file.read_text(encoding="utf-8"))
        return data.get("feature_importances") or data
    raise HTTPException(status_code=404, detail="No feature importance data found")
