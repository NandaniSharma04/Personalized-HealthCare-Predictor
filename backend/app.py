# ============================================================================
# MAIN FLASK APP
# Save this as: app.py
# ============================================================================

import os
import traceback
import pickle
import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from models import db, User, PredictionHistory
from auth import auth_bp

load_dotenv()

# Build an absolute path for the database, and make sure the folder exists
# BEFORE Flask-SQLAlchemy tries to open a connection to it. Using a relative
# path here is what was causing "unable to open database file".
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)
DEFAULT_DB_PATH = os.path.join(INSTANCE_DIR, "medicare.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-this-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Cookies: strong defaults. In production behind HTTPS, also set SESSION_COOKIE_SECURE=True.
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production"

CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",   # Vite dev server
    os.environ.get("FRONTEND_URL", ""),  # set this to your deployed React URL later
])
db.init_app(app)
app.register_blueprint(auth_bp)

# ----------------------------------------------------------------------------
# LOGIN MANAGER
# ----------------------------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    # React expects JSON, not a redirect to a server-rendered login page.
    return jsonify({"success": False, "error": "Please log in to continue."}), 401


# ----------------------------------------------------------------------------
# RATE LIMITING (protects /api/login and /api/signup from brute-force / spam)
# ----------------------------------------------------------------------------
limiter = Limiter(get_remote_address, app=app, default_limits=[])
limiter.limit("10 per minute")(auth_bp)

# ----------------------------------------------------------------------------
# LOAD ML MODELS
# ----------------------------------------------------------------------------
print("Loading models...")
best_model = None
label_encoder = None
try:
    best_model = joblib.load("ml/best_model.pkl")
    print("Model loaded")
except Exception as e:
    print("Failed to load best_model.pkl:", e)
    traceback.print_exc()

try:
    with open("ml/disease_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)
    print("Label encoder loaded")
except Exception as e:
    print("Failed to load disease_encoder.pkl:", e)
    traceback.print_exc()

try:
    with open("ml/medicine_database.pkl", "rb") as f:
        MEDICINE_DB = pickle.load(f)
except Exception:
    MEDICINE_DB = {}

# Keep your existing COMPLETE_MEDICINE_DB dictionary here (copy it in from
# your original app.py -- omitted here for brevity, nothing about it changes).
from medicine_data import COMPLETE_MEDICINE_DB  # noqa: E402

# ----------------------------------------------------------------------------
# HISTORY -- React's Dashboard page fetches this
# ----------------------------------------------------------------------------
@app.route("/api/history", methods=["GET"])
@login_required
def history():
    records = (
        PredictionHistory.query.filter_by(user_id=current_user.id)
        .order_by(PredictionHistory.created_at.desc())
        .all()
    )
    return jsonify({"history": [r.to_dict() for r in records]}), 200


# ----------------------------------------------------------------------------
# HEALTH CHECK
# ----------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": best_model is not None,
        "encoder_loaded": label_encoder is not None,
        "db_connected": True,
    })


# ----------------------------------------------------------------------------
# PREDICT -- now requires login and saves to history
# ----------------------------------------------------------------------------
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        fever = int(data.get("fever", 0))
        cough = int(data.get("cough", 0))
        fatigue = int(data.get("fatigue", 0))
        difficulty_breathing = int(data.get("breathing", 0))
        age = int(data.get("age", 30))
        gender = int(data.get("gender", 0))
        blood_pressure = int(data.get("bloodPressure", 1))
        cholesterol = int(data.get("cholesterol", 1))

        if best_model is None or label_encoder is None:
            return jsonify({"success": False, "error": "Model not loaded"}), 500

        input_df = pd.DataFrame({
            "fever": [fever], "cough": [cough], "fatigue": [fatigue],
            "difficulty_breathing": [difficulty_breathing], "age": [age],
            "gender": ["male" if gender == 1 else "female"],
            "blood_pressure": [blood_pressure], "cholesterol_level": [cholesterol],
        })
        input_df["age_scaled"] = input_df["age"]
        input_df["bp_scaled"] = input_df["blood_pressure"]
        input_df["chol_scaled"] = input_df["cholesterol_level"]
        input_df["outcome_variable"] = 0
        input_df["risk_level"] = 0

        prediction = best_model.predict(input_df)[0]
        probabilities = best_model.predict_proba(input_df)[0]
        predicted_disease = label_encoder.classes_[prediction]
        confidence = float(probabilities[prediction] * 100)

        symptom_count = fever + cough + fatigue + difficulty_breathing
        if symptom_count >= 3 and (age > 60 or blood_pressure == 2):
            risk_level = "high"
        elif symptom_count >= 2:
            risk_level = "medium"
        else:
            risk_level = "low"

        treatment = COMPLETE_MEDICINE_DB.get(predicted_disease, {
            "medicines": ["Consult a doctor for specific treatment"],
            "advice": ["Schedule an appointment with a healthcare provider"],
        })

        # Save to this user's history -- this is the "personalized" part.
        record = PredictionHistory(
            user_id=current_user.id,
            symptoms_input=data,
            predicted_disease=predicted_disease,
            confidence=round(confidence, 2),
            risk_level=risk_level,
            medicines=treatment.get("medicines", []),
            advice=treatment.get("advice", []),
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            "success": True,
            "disease": predicted_disease,
            "confidence": round(confidence, 2),
            "risk": risk_level,
            "medicines": treatment.get("medicines", []),
            "advice": treatment.get("advice", []),
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables ready")
    app.run(debug=True, host="0.0.0.0", port=5000)