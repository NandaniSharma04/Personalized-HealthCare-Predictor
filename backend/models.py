# ============================================================================
# DATABASE MODELS
# Save this as: models.py (same folder as app.py)
# ============================================================================

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # user | admin | analyst
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # failed-login tracking (basic brute-force protection)
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    predictions = db.relationship(
        "PredictionHistory", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        # werkzeug's default method (pbkdf2:sha256) is a strong, salted hash.
        # Never store raw_password anywhere, ever.
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def is_locked(self):
        return self.locked_until is not None and self.locked_until > datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


class PredictionHistory(db.Model):
    __tablename__ = "prediction_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    symptoms_input = db.Column(db.JSON, nullable=False)
    predicted_disease = db.Column(db.String(120), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    medicines = db.Column(db.JSON, nullable=True)
    advice = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "predicted_disease": self.predicted_disease,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "medicines": self.medicines,
            "advice": self.advice,
            "created_at": self.created_at.isoformat(),
        }