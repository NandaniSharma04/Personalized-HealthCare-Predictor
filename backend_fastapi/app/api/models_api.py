from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from ..ml.train_pipeline import train_model
from ..db.session import get_db
from sqlalchemy.orm import Session
from ..models import ModelVersion, TrainingReport
from ..deps import require_role
from pathlib import Path
import joblib, json

router = APIRouter(prefix="/api/models", tags=["models"])


def _background_train_and_record(db: Session, model_path: Path):
    report = train_model(model_output=model_path)
    model_folder = report.get("model_folder") or str(model_path.parent)
    mv = ModelVersion(name="rf_disease_predictor", version="v1", metrics=report.get("metrics"), path=str(model_folder))
    db.add(mv)
    db.commit()
    db.refresh(mv)
    # prefer MLflow run id if present
    run_id = report.get("mlflow_run_id") or f"run_{mv.id}"
    tr = TrainingReport(run_id=run_id, summary=report)
    db.add(tr)
    db.commit()


@router.post("/train")
def train_endpoint(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current=Depends(require_role("admin"))):
    try:
        repo_root = Path(__file__).resolve().parents[3]
        model_path = repo_root / "backend" / "ml" / "best_model.pkl"
        # schedule background job
        background_tasks.add_task(_background_train_and_record, db, model_path)
        return {"ok": True, "message": "Training started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
