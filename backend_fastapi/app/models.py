"""
HealthAI - Complete FastAPI SQLAlchemy 2.0 Declarative ORM Models
Extends database entities while preserving existing user accounts and prediction history.
"""
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Text,
    DateTime,
    Float,
    Table,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ============================================================================
# MANY-TO-MANY USER ROLES
# ============================================================================
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(254), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=True)
    hashed_password = Column(String(512), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    roles = relationship("Role", secondary=user_roles)
    health_profile = relationship("HealthProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    predictions = relationship("PredictionHistory", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    phone = Column(String(30), nullable=True)
    address = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    bio = Column(Text, nullable=True)

class HealthProfile(Base):
    __tablename__ = "health_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    allergies = Column(JSON, nullable=True)
    existing_conditions = Column(JSON, nullable=True)
    current_medications = Column(JSON, nullable=True)
    health_preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="health_profile")

class Disease(Base):
    __tablename__ = "diseases"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    disease_meta = relationship("DiseaseMetadata", back_populates="disease", uselist=False)

class DiseaseMetadata(Base):
    __tablename__ = "disease_metadata"
    id = Column(Integer, primary_key=True)
    disease_id = Column(Integer, ForeignKey("diseases.id"), unique=True)
    medications = Column(JSON)
    diets = Column(JSON)
    workouts = Column(JSON)
    precautions = Column(JSON)
    extra = Column(JSON)
    disease = relationship("Disease", back_populates="disease_meta")

class Symptom(Base):
    __tablename__ = "symptoms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    age = Column(Integer, nullable=True)
    sex = Column(String(16), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PatientSymptom(Base):
    __tablename__ = "patient_symptoms"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    symptom_id = Column(Integer, ForeignKey("symptoms.id"), nullable=False)
    value = Column(Integer, default=0)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    input_vector = Column(JSON)
    predicted_disease = Column(String(255))
    probabilities = Column(JSON)
    explainability = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symptoms_input = Column(JSON, nullable=False)
    predicted_disease = Column(String(120), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False, index=True)
    top_candidates = Column(JSON, nullable=True)
    disease_symptoms = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    medicines = Column(JSON, nullable=True)
    advice = Column(JSON, nullable=True)
    diet = Column(JSON, nullable=True)
    workout = Column(JSON, nullable=True)
    model_version = Column(String(64), nullable=True, default="v1.0.0")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="predictions")

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    recommendation_type = Column(String(50), nullable=False, default="general")
    item = Column(JSON, nullable=False)
    score = Column(Float, nullable=True, default=1.0)
    reason = Column(Text, nullable=True)
    model = Column(String(100), nullable=True, default="HybridRecommender")
    created_at = Column(DateTime, default=datetime.utcnow)

class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SavedRecommendation(Base):
    __tablename__ = "saved_recommendations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserActivity(Base):
    __tablename__ = "user_activity"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    activity_type = Column(String(64), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="activities")

class SearchHistory(Base):
    __tablename__ = "search_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query = Column(String(255), nullable=False)
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    text = Column(Text)
    sentiment_score = Column(Float)
    sentiment_label = Column(String(50))
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SentimentResult(Base):
    __tablename__ = "sentiment_results"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    text = Column(Text, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    sentiment_label = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

class TrainingReport(Base):
    __tablename__ = "training_reports"
    id = Column(Integer, primary_key=True)
    run_id = Column(String(128), unique=True)
    summary = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    version = Column(String(64), nullable=False, unique=True)
    path = Column(String(1024), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelMetric(Base):
    __tablename__ = "model_metrics"
    id = Column(Integer, primary_key=True)
    model_version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False)
    accuracy = Column(Float, nullable=True)
    macro_f1 = Column(Float, nullable=True)
    kl_divergence = Column(Float, nullable=True)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    actor = Column(String(120), nullable=False)
    action = Column(String(128), nullable=False)
    entity = Column(String(128), nullable=True)
    result = Column(String(64), default="SUCCESS")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
