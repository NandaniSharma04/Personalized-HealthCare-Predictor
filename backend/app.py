# ============================================================================
# MAIN FLASK APP
# Save this as: app.py
# ============================================================================

import os
import json
import traceback
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
SYMPTOM_LIST = []
DISEASE_INFO = {}

try:
    best_model = joblib.load("ml/best_model.pkl")
    print(f"Model loaded ({len(best_model.classes_)} diseases)")
except Exception as e:
    print("Failed to load best_model.pkl:", e)
    traceback.print_exc()

try:
    with open("ml/symptom_list.json") as f:
        SYMPTOM_LIST = json.load(f)
    print(f"Symptom list loaded ({len(SYMPTOM_LIST)} symptoms)")
except Exception as e:
    print("Failed to load symptom_list.json:", e)

try:
    with open("ml/disease_info.json") as f:
        DISEASE_INFO = json.load(f)
    print(f"Disease info loaded ({len(DISEASE_INFO)} diseases)")
except Exception as e:
    print("Failed to load disease_info.json:", e)


# ----------------------------------------------------------------------------
# SYMPTOMS -- React's checker fetches this to build the searchable list
# ----------------------------------------------------------------------------
@app.route("/api/symptoms", methods=["GET"])
def get_symptoms():
    return jsonify({"symptoms": SYMPTOM_LIST}), 200


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
        "symptom_count": len(SYMPTOM_LIST),
        "disease_count": len(DISEASE_INFO),
        "db_connected": True,
    })


# ----------------------------------------------------------------------------
# PREDICT -- now requires login and saves to history
# Expects: { "symptoms": ["fever", "cough", ...] }  (keys must match /api/symptoms)
# ----------------------------------------------------------------------------
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    try:
        data = request.get_json()
        if not data or "symptoms" not in data:
            return jsonify({"success": False, "error": "No symptoms provided"}), 400

        selected = set(data.get("symptoms", []))
        if not selected:
            return jsonify({"success": False, "error": "Select at least one symptom"}), 400

        if best_model is None:
            return jsonify({"success": False, "error": "Model not loaded"}), 500

        # Build the 0/1 feature vector in the exact column order the model expects
        row = {s: (1 if s in selected else 0) for s in SYMPTOM_LIST}
        input_df = pd.DataFrame([row])[SYMPTOM_LIST]

        probabilities = best_model.predict_proba(input_df)[0]
        top_idx = int(np.argmax(probabilities))
        predicted_disease = best_model.classes_[top_idx]
        confidence = float(probabilities[top_idx] * 100)

        # Risk heuristic: how confident the model is + how many symptoms were given
        if confidence >= 40 and len(selected) >= 4:
            risk_level = "high"
        elif confidence >= 20 or len(selected) >= 2:
            risk_level = "medium"
        else:
            risk_level = "low"

        info = DISEASE_INFO.get(predicted_disease, {})
        description = info.get("description", "No description available for this condition.")
        precautions = info.get("precautions", ["Consult a doctor for guidance."])
        medications = info.get("medications", ["Consult a doctor for specific medication."])
        diet = info.get("diet", [])
        workout = info.get("workout", [])

        # Save to this user's history -- this is the "personalized" part.
        record = PredictionHistory(
            user_id=current_user.id,
            symptoms_input=list(selected),
            predicted_disease=predicted_disease,
            confidence=round(confidence, 2),
            risk_level=risk_level,
            medicines=medications,
            advice=precautions,
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            "success": True,
            "disease": predicted_disease,
            "confidence": round(confidence, 2),
            "risk": risk_level,
            "description": description,
            "precautions": precautions,
            "medications": medications,
            "diet": diet,
            "workout": workout,
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables ready")
    app.run(debug=True, host="0.0.0.0", port=5000)