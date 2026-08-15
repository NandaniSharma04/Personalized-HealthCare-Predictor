"""
Recommendation API Routes
Exposes disease, medication, precaution, diet, workout, and TF-IDF content similarity recommendations.
"""
from flask import Blueprint, request, jsonify
from flask_login import current_user
from backend.services.recommend_service import (
    get_recommendations_for_disease,
    save_user_recommendation,
    submit_recommendation_feedback
)

recommend_bp = Blueprint("recommend_bp", __name__, url_prefix="/api/recommendations")

@recommend_bp.route("", methods=["POST"])
@recommend_bp.route("/", methods=["POST"])
def get_recommendations():
    data = request.get_json(silent=True) or {}
    disease = data.get("disease") or data.get("predicted_disease") or ""
    if not disease:
        return jsonify({
            "success": False,
            "error": "Please provide a disease name for recommendations",
            "code": "INVALID_INPUT"
        }), 400

    uid = current_user.id if current_user.is_authenticated else None
    recs = get_recommendations_for_disease(disease, user_id=uid)
    return jsonify({
        "success": True,
        "disease": disease,
        "count": len(recs),
        "recommendations": recs
    }), 200

@recommend_bp.route("/save", methods=["POST"])
def save_recommendation():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "error": "Login required to save recommendations"}), 401
    
    data = request.get_json(silent=True) or {}
    rec_id = data.get("recommendation_id")
    if not rec_id:
        return jsonify({"success": False, "error": "recommendation_id is required"}), 400

    saved = save_user_recommendation(
        user_id=current_user.id,
        recommendation_id=int(rec_id),
        title=data.get("title"),
        notes=data.get("notes")
    )
    return jsonify({"success": True, "saved": saved}), 201

@recommend_bp.route("/feedback", methods=["POST"])
def post_feedback():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "error": "Login required to submit feedback"}), 401

    data = request.get_json(silent=True) or {}
    rec_id = data.get("recommendation_id")
    rating = data.get("rating")
    if not rec_id or rating is None:
        return jsonify({"success": False, "error": "recommendation_id and rating (1-5) are required"}), 400

    res = submit_recommendation_feedback(
        user_id=current_user.id,
        recommendation_id=int(rec_id),
        rating=int(rating),
        feedback_text=data.get("feedback_text")
    )
    return jsonify({"success": True, **res}), 200
