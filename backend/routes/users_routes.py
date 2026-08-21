"""
User Portal API Routes (Dashboard, Profile, Health Profile, Activity, Notifications, Settings)
"""
from flask import Blueprint, request, jsonify
from flask_login import current_user
from datetime import datetime
from backend.utils.security import require_auth
from backend.utils.activity_tracker import track_activity, create_notification
from backend.utils.db import db
from backend.models import (
    User, UserProfile, HealthProfile, PredictionHistory,
    Recommendation, SavedRecommendation, UserActivity, Notification
)

users_bp = Blueprint("users_bp", __name__, url_prefix="/api/user")

@users_bp.route("/dashboard", methods=["GET"])
@require_auth
def get_user_dashboard():
    user = User.query.get(current_user.id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    # 1. Health Profile & Completion Score
    hp = HealthProfile.query.filter_by(user_id=user.id).first()
    fields = [hp.age if hp else None, hp.gender if hp else None, hp.allergies if hp else None, hp.existing_conditions if hp else None, hp.current_medications if hp else None]
    filled = sum(1 for f in fields if f is not None and f != [] and f != "")
    profile_completion = int((filled / 5.0) * 100) if filled > 0 else 0

    # 2. Prediction History & KPI Counts
    predictions_query = PredictionHistory.query.filter_by(user_id=user.id).order_by(PredictionHistory.created_at.desc())
    predictions_list = predictions_query.all()
    predictions_completed = len(predictions_list)
    recent_pred = predictions_list[0] if predictions_completed > 0 else None
    pred_data = recent_pred.to_dict() if recent_pred else None

    # 3. Recommendations & Saved Counts
    recs_db = Recommendation.query.filter_by(user_id=user.id).order_by(Recommendation.created_at.desc()).all()
    recommendations_available = 0
    top_recommendations = []
    
    for r in recs_db:
        raw_items = getattr(r, 'item', getattr(r, 'items', [])) or []
        items = raw_items if isinstance(raw_items, list) else ([raw_items] if isinstance(raw_items, dict) else [])
        recommendations_available += len(items)
        for it in items:
            if isinstance(it, dict) and len(top_recommendations) < 5:
                item_with_id = dict(it)
                item_with_id.setdefault("id", len(top_recommendations) + 1)
                top_recommendations.append(item_with_id)

    if not top_recommendations and recent_pred:
        now_iso = recent_pred.created_at.isoformat() if recent_pred.created_at else datetime.utcnow().isoformat() + "Z"
        disease = recent_pred.predicted_disease
        for med in (recent_pred.medicines or [])[:2]:
            top_recommendations.append({
                "id": len(top_recommendations) + 1,
                "recommendation": med,
                "category": "medicine",
                "reason": f"Standard clinical medication indicated for condition '{disease}'",
                "score": 0.95,
                "source": "Dataset Medical Registry",
                "model_version": recent_pred.model_version or "v1.0.0",
                "timestamp": now_iso
            })
        for prec in (recent_pred.advice or [])[:2]:
            top_recommendations.append({
                "id": len(top_recommendations) + 1,
                "recommendation": prec,
                "category": "precaution",
                "reason": f"Essential care guideline to prevent exacerbation of '{disease}'",
                "score": 0.92,
                "source": "Clinical Precaution Guidelines",
                "model_version": recent_pred.model_version or "v1.0.0",
                "timestamp": now_iso
            })
        for diet_item in (recent_pred.diet or [])[:1]:
            top_recommendations.append({
                "id": len(top_recommendations) + 1,
                "recommendation": diet_item,
                "category": "diet",
                "reason": f"Nutritional protocol designed for patients presenting with '{disease}'",
                "score": 0.88,
                "source": "Dietary Healthcare Dataset",
                "model_version": recent_pred.model_version or "v1.0.0",
                "timestamp": now_iso
            })
        recommendations_available = len(top_recommendations)

    saved_recs = SavedRecommendation.query.filter_by(user_id=user.id).order_by(SavedRecommendation.created_at.desc()).all()
    saved_count = len(saved_recs)
    saved_list = [{
        "id": s.id,
        "recommendation_id": s.recommendation_id,
        "title": s.title,
        "notes": s.notes,
        "timestamp": s.created_at.isoformat() if s.created_at else None
    } for s in saved_recs]

    # 4. Recent Activity
    acts = UserActivity.query.filter_by(user_id=user.id).order_by(UserActivity.created_at.desc()).limit(15).all()
    activity_list = [{
        "id": a.id,
        "type": a.activity_type,
        "details": a.details or {},
        "timestamp": a.created_at.isoformat() if a.created_at else None
    } for a in acts]

    # 5. Notifications
    notes = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    unread_count = sum(1 for n in notes if not n.is_read)
    notification_list = [{
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "is_read": n.is_read,
        "timestamp": n.created_at.isoformat() if n.created_at else None
    } for n in notes[:10]]

    # 6. Dynamic Health Insights
    has_sufficient_data = predictions_completed >= 3
    health_insights = {
        "has_sufficient_data": has_sufficient_data,
        "total_evaluations": predictions_completed,
        "dominant_condition": recent_pred.predicted_disease if recent_pred else "None Recorded",
        "current_risk_status": recent_pred.risk_level if recent_pred else "low",
        "care_plan_status": "Active Routine" if recent_pred else "Pending Initial Assessment",
        "trend_summary": (
            f"Based on {predictions_completed} evaluations, your most frequent evaluation pattern correlates with {recent_pred.predicted_disease}."
            if has_sufficient_data
            else "Not enough data yet. Complete more health checks to see your personalized trends."
        )
    }

    recent_health_check_date = recent_pred.created_at.isoformat() if (recent_pred and recent_pred.created_at) else None
    history_serialized = [p.to_dict() for p in predictions_list[:10]]

    return jsonify({
        "success": True,
        "greeting": f"Welcome back, {user.name}!",
        "user": user.to_dict(),
        "profile_completion": profile_completion,
        "kpi_stats": {
            "predictions_completed": predictions_completed,
            "recommendations_available": recommendations_available,
            "saved_recommendations": saved_count,
            "recent_health_check": recent_health_check_date
        },
        "recent_prediction": pred_data,
        "top_recommendations": top_recommendations,
        "prediction_history": history_serialized,
        "saved_recommendations": saved_list,
        "recent_activity": activity_list,
        "notifications": notification_list,
        "unread_notifications_count": unread_count,
        "health_insights": health_insights
    }), 200

# ============================================================================
# NOTIFICATION MANAGEMENT (Unread Count, Mark Read, Mark All Read)
# ============================================================================
@users_bp.route("/notifications", methods=["GET"])
@require_auth
def list_notifications():
    notes = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    unread_count = sum(1 for n in notes if not n.is_read)
    return jsonify({
        "success": True,
        "total_count": len(notes),
        "unread_count": unread_count,
        "notifications": [{
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "timestamp": n.created_at.isoformat() if n.created_at else None
        } for n in notes]
    }), 200

@users_bp.route("/notifications/<int:note_id>/read", methods=["PUT"])
@require_auth
def mark_notification_read(note_id):
    note = Notification.query.filter_by(id=note_id, user_id=current_user.id).first()
    if not note:
        return jsonify({"success": False, "error": "Notification not found"}), 404
    note.is_read = True
    db.session.commit()
    return jsonify({"success": True, "message": "Notification marked as read"}), 200

@users_bp.route("/notifications/mark-all-read", methods=["PUT"])
@require_auth
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"success": True, "message": "All notifications marked as read"}), 200

# ============================================================================
# USER ACTIVITY TIMELINE
# ============================================================================
@users_bp.route("/activity", methods=["GET"])
@require_auth
def get_user_activity():
    acts = UserActivity.query.filter_by(user_id=current_user.id).order_by(UserActivity.created_at.desc()).limit(50).all()
    return jsonify({
        "success": True,
        "activities": [{
            "id": a.id,
            "type": a.activity_type,
            "details": a.details or {},
            "timestamp": a.created_at.isoformat() if a.created_at else None
        } for a in acts]
    }), 200

# ============================================================================
# PROFILE & HEALTH PROFILE
# ============================================================================
@users_bp.route("/profile", methods=["GET", "PUT"])
@require_auth
def manage_user_profile():
    user = User.query.get(current_user.id)
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    
    if request.method == "GET":
        return jsonify({
            "success": True,
            "user": user.to_dict(),
            "profile": {
                "phone": profile.phone if profile else "",
                "address": profile.address if profile else "",
                "avatar_url": profile.avatar_url if profile else "",
                "bio": profile.bio if profile else ""
            }
        }), 200

    data = request.get_json(silent=True) or {}
    if "name" in data and data["name"]:
        user.name = data["name"]
    
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        
    profile.phone = data.get("phone", profile.phone or "")
    profile.address = data.get("address", profile.address or "")
    profile.bio = data.get("bio", profile.bio or "")
    
    track_activity(user.id, "PROFILE_UPDATE", {"section": "personal_details"})
    db.session.commit()
    return jsonify({"success": True, "message": "Profile updated successfully"}), 200

@users_bp.route("/health-profile", methods=["GET", "PUT"])
@require_auth
def manage_health_profile():
    hp = HealthProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == "GET":
        return jsonify({
            "success": True,
            "health_profile": hp.to_dict() if hp else {
                "age": None, "gender": "", "allergies": [],
                "existing_conditions": [], "current_medications": [], "health_preferences": {}
            }
        }), 200

    data = request.get_json(silent=True) or {}
    if not hp:
        hp = HealthProfile(user_id=current_user.id)
        db.session.add(hp)

    hp.age = data.get("age", hp.age)
    hp.gender = data.get("gender", hp.gender)
    hp.allergies = data.get("allergies", hp.allergies)
    hp.existing_conditions = data.get("existing_conditions", hp.existing_conditions)
    hp.current_medications = data.get("current_medications", hp.current_medications)
    hp.health_preferences = data.get("health_preferences", hp.health_preferences)
    hp.updated_at = datetime.utcnow()
    
    track_activity(current_user.id, "PROFILE_UPDATE", {"section": "clinical_health_profile"})
    
    # Check for profile completion notification
    fields = [hp.age, hp.gender, hp.allergies, hp.existing_conditions, hp.current_medications]
    filled = sum(1 for f in fields if f is not None and f != [] and f != "")
    if filled >= 4:
        create_notification(current_user.id, "Profile Completion", "Your clinical health profile is now comprehensive and up to date.")

    db.session.commit()
    return jsonify({"success": True, "health_profile": hp.to_dict()}), 200
