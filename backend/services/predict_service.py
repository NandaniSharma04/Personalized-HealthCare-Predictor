"""
Prediction Service connecting ML inference engine with database persistence, activity tracking, and notifications.
"""
from backend.utils.db import db
from backend.models import PredictionHistory
from backend.ml.predictor import predict_symptoms
from backend.utils.activity_tracker import track_activity, create_notification

def run_prediction(symptoms: list[str], user_id: int | None = None) -> dict:
    result = predict_symptoms(symptoms)
    
    # Ensure frontend-compatible alias keys are always populated
    disease = result.get("predicted_disease", "Unknown")
    conf = float(result.get("confidence", 0.0))
    risk = result.get("risk_level", "unknown")
    precautions = result.get("advice") or result.get("precautions") or []
    medications = result.get("medicines") or result.get("medications") or []
    
    result["disease"] = disease
    result["risk"] = risk
    result["precautions"] = precautions
    result["medications"] = medications

    if user_id:
        try:
            record = PredictionHistory(
                user_id=user_id,
                symptoms_input=symptoms,
                predicted_disease=disease,
                confidence=conf,
                risk_level=risk,
                top_candidates=result.get("top_candidates", []),
                disease_symptoms=result.get("disease_symptoms", []),
                description=result.get("description", ""),
                medicines=medications,
                advice=precautions,
                diet=result.get("diet", []),
                workout=result.get("workout", [])
            )
            db.session.add(record)
            db.session.commit()

            # Track activity & generate system notifications
            track_activity(user_id, "PREDICTION", {"disease": disease, "confidence": conf, "risk_level": risk})
            create_notification(user_id, "Prediction Completed", f"Health evaluation completed for {disease} ({conf}% confidence).")
            create_notification(user_id, "New Recommendation Available", f"A personalized care plan has been generated for {disease}.")
        except Exception as err:
            db.session.rollback()
            print(f"[PREDICT SERVICE WARN] Failed to save prediction history: {err}")
            
    return result

def get_user_predictions(user_id: int, limit: int = 50) -> list[dict]:
    records = PredictionHistory.query.filter_by(user_id=user_id).order_by(PredictionHistory.created_at.desc()).limit(limit).all()
    track_activity(user_id, "VIEW_PREDICTION", {"count": len(records)})
    return [r.to_dict() for r in records]
