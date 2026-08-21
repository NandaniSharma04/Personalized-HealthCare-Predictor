"""
Prediction Routes (Symptom Disease Predictor)
"""
from flask import Blueprint, request, jsonify
from flask_login import current_user
from backend.services.predict_service import run_prediction, get_user_predictions

predict_bp = Blueprint("predict_bp", __name__)

@predict_bp.route("/api/predict", methods=["POST"])
@predict_bp.route("/predict", methods=["POST"])
@predict_bp.route("/api/predict_disease", methods=["POST"])
def predict():
    if not current_user.is_authenticated:
        return jsonify({
            "success": False,
            "error": "Authentication required. Please log in to perform disease prediction.",
            "code": "UNAUTHORIZED"
        }), 401

    data = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms") or data.get("selectedSymptoms") or data.get("symptom") or []
    
    if isinstance(symptoms, str):
        symptoms = [s.strip() for s in symptoms.split(",") if s.strip()]

    if not isinstance(symptoms, list) or len(symptoms) == 0:
        return jsonify({"success": False, "error": "Please select at least one symptom to run clinical prediction."}), 400
        
    try:
        uid = current_user.id
        res = run_prediction(symptoms, user_id=uid)
        return jsonify({"success": True, **res}), 200
    except ValueError as val_err:
        return jsonify({"success": False, "error": str(val_err)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

@predict_bp.route("/api/history", methods=["GET"])
@predict_bp.route("/api/prediction/history", methods=["GET"])
def history():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "error": "Login required to access prediction history"}), 401
    preds = get_user_predictions(current_user.id)
    return jsonify({"success": True, "predictions": preds}), 200
