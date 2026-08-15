"""
HealthAI - Complete Production Database Schema (Flask SQLAlchemy ORM)
Preserves existing user accounts & prediction history while extending platform entities.
"""
from datetime import datetime
from flask_login import UserMixin
from backend.utils.db import db
from backend.utils.security import hash_password, check_password

# ============================================================================
# USER ROLES (MANY-TO-MANY)
# ============================================================================
user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    failed_attempts = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    # Relationships
    roles_rel = db.relationship("Role", secondary=user_roles, backref=db.backref("users", lazy="dynamic"))
    profile = db.relationship("UserProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    health_profile = db.relationship("HealthProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    predictions = db.relationship("PredictionHistory", backref="user", lazy=True, cascade="all, delete-orphan")
    activities = db.relationship("UserActivity", backref="user", lazy=True, cascade="all, delete-orphan")
    search_history = db.relationship("SearchHistory", backref="user", lazy=True, cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = hash_password(password)

    def verify_password(self, password):
        return check_password(password, self.password_hash)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(512), nullable=True)
    bio = db.Column(db.Text, nullable=True)

class HealthProfile(db.Model):
    __tablename__ = "health_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    allergies = db.Column(db.JSON, nullable=True)
    existing_conditions = db.Column(db.JSON, nullable=True)
    current_medications = db.Column(db.JSON, nullable=True)
    health_preferences = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "allergies": self.allergies or [],
            "existing_conditions": self.existing_conditions or [],
            "current_medications": self.current_medications or [],
            "health_preferences": self.health_preferences or {}
        }

class PredictionHistory(db.Model):
    __tablename__ = "prediction_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symptoms_input = db.Column(db.JSON, nullable=False)
    predicted_disease = db.Column(db.String(120), nullable=False, index=True)
    confidence = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False, index=True)
    top_candidates = db.Column(db.JSON, nullable=True)
    disease_symptoms = db.Column(db.JSON, nullable=True)
    description = db.Column(db.Text, nullable=True)
    medicines = db.Column(db.JSON, nullable=True)
    advice = db.Column(db.JSON, nullable=True)
    diet = db.Column(db.JSON, nullable=True)
    workout = db.Column(db.JSON, nullable=True)
    model_version = db.Column(db.String(64), nullable=True, default="v1.0.0")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "symptoms_input": self.symptoms_input or [],
            "predicted_disease": self.predicted_disease or "",
            "confidence": round(float(self.confidence or 0.0), 2),
            "risk_level": self.risk_level or "unknown",
            "top_candidates": self.top_candidates or [],
            "disease_symptoms": self.disease_symptoms or [],
            "description": self.description or "",
            "medicines": self.medicines or [],
            "advice": self.advice or [],
            "diet": self.diet or [],
            "workout": self.workout or [],
            "model_version": self.model_version or "v1.0.0",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    recommendation_type = db.Column(db.String(50), nullable=False, default="general")
    item = db.Column(db.JSON, nullable=False)
    score = db.Column(db.Float, nullable=True, default=1.0)
    reason = db.Column(db.Text, nullable=True)
    model = db.Column(db.String(100), nullable=True, default="HybridRecommender")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class RecommendationFeedback(db.Model):
    __tablename__ = "recommendation_feedback"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recommendation_id = db.Column(db.Integer, db.ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1-5
    feedback_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavedRecommendation(db.Model):
    __tablename__ = "saved_recommendations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recommendation_id = db.Column(db.Integer, db.ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserActivity(db.Model):
    __tablename__ = "user_activity"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    activity_type = db.Column(db.String(64), nullable=False) # login, search, prediction, recommendation view, recommendation save, feedback, logout
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

class SearchHistory(db.Model):
    __tablename__ = "search_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query = db.Column(db.String(255), nullable=False)
    results_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SentimentResult(db.Model):
    __tablename__ = "sentiment_results"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    text = db.Column(db.Text, nullable=False)
    sentiment_score = db.Column(db.Float, nullable=False)
    sentiment_label = db.Column(db.String(50), nullable=False) # POSITIVE, NEGATIVE, NEUTRAL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class ModelVersion(db.Model):
    __tablename__ = "model_versions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(64), nullable=False, unique=True)
    path = db.Column(db.String(1024), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ModelMetric(db.Model):
    __tablename__ = "model_metrics"

    id = db.Column(db.Integer, primary_key=True)
    model_version_id = db.Column(db.Integer, db.ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    macro_f1 = db.Column(db.Float, nullable=True)
    kl_divergence = db.Column(db.Float, nullable=True)
    metrics_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    actor = db.Column(db.String(120), nullable=False)
    action = db.Column(db.String(128), nullable=False)
    entity = db.Column(db.String(128), nullable=True)
    result = db.Column(db.String(64), nullable=True, default="SUCCESS")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)