from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..ml.model import load_model
from pathlib import Path
import json
import joblib
from .. import schemas
from ..deps import get_current_user
from ..models import Prediction

router = APIRouter(prefix="/api", tags=["predict"])


def _build_vector_from_input(symptom_list: list[str], req: schemas.PredictRequest) -> list[int]:
    # symptom_list defines ordering
    vec = [0] * len(symptom_list)
    if req.symptom_vector:
        for k, v in req.symptom_vector.items():
            try:
                idx = symptom_list.index(k)
                vec[idx] = int(v)
            except ValueError:
                continue
    if req.symptoms:
        for s in req.symptoms:
            try:
                idx = symptom_list.index(s)
                vec[idx] = 1
            except ValueError:
                continue
    return vec


import sys
from pathlib import Path
import json
import joblib

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

try:
    from backend.ml.predictor import predict_symptoms
except Exception:
    predict_symptoms = None

@router.post("/predict", response_model=schemas.PredictResponse)
def predict(req: schemas.PredictRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    symptom_list_input = req.symptoms or []
    if req.symptom_vector:
        symptom_list_input.extend([k for k, v in req.symptom_vector.items() if v > 0])

    if predict_symptoms and symptom_list_input:
        try:
            res = predict_symptoms(symptom_list_input)
            top_k_items = [
                schemas.PredictionItem(disease=c["disease"], probability=float(c["confidence"])/100.0)
                for c in res.get("top_candidates", [])
            ]
            
            # Persist prediction in DB
            try:
                record = Prediction(
                    patient_id=user.id if user else None,
                    input_vector={"symptoms": symptom_list_input},
                    predicted_disease=res["predicted_disease"],
                    probabilities={c["disease"]: float(c["confidence"])/100.0 for c in res.get("top_candidates", [])}
                )
                db.add(record)
                db.commit()
            except Exception:
                db.rollback()

            return schemas.PredictResponse(
                top_k=top_k_items,
                predicted_disease=res.get("predicted_disease"),
                confidence=res.get("confidence"),
                risk_level=res.get("risk_level"),
                description=res.get("description"),
                medicines=res.get("medicines"),
                advice=res.get("advice"),
                diet=res.get("diet"),
                workout=res.get("workout")
            )
        except Exception as exc:
            pass

    # Fallback to feature vector matrix loading
    sym_file = repo_root / "backend" / "ml" / "symptom_list.json"
    if not sym_file.exists():
        raise HTTPException(status_code=500, detail="Symptom vocabulary not found")
    symptom_list = json.loads(sym_file.read_text(encoding="utf-8"))

    vec = _build_vector_from_input(symptom_list, req)
    model = load_model()

    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba([vec])[0]
            classes = [str(c) for c in getattr(model, "classes_", [])]
            pairs = list(zip(classes, proba))
            pairs.sort(key=lambda x: x[1], reverse=True)
        else:
            pred = model.predict([vec])[0]
            pairs = [(str(pred), 1.0)]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference error: {e}")

    try:
        record = Prediction(patient_id=user.id if user else None, input_vector={"vector": vec}, predicted_disease=pairs[0][0], probabilities={k: float(v) for k, v in pairs[:5]})
        db.add(record)
        db.commit()
    except Exception:
        db.rollback()

    response_items = [schemas.PredictionItem(disease=k, probability=float(v)) for k, v in pairs[:5]]
    return schemas.PredictResponse(top_k=response_items, predicted_disease=pairs[0][0], confidence=round(float(pairs[0][1])*100, 2))
