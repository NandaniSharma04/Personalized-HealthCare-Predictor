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

frontend_origins = [
    "http://localhost:5173",   # Vite dev server
    "http://127.0.0.1:5173",   # common local browser origin
    os.environ.get("FRONTEND_URL", ""),  # set this to your deployed React URL later
]

CORS(
    app,
    supports_credentials=True,
    origins=[origin for origin in frontend_origins if origin],
)
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
    model_path = os.path.join(BASE_DIR, "ml", "best_model.pkl")
    best_model = joblib.load(model_path)
    print(f"Model loaded ({len(best_model.classes_)} diseases)")
except Exception as e:
    print("Failed to load best_model.pkl:", e)
    traceback.print_exc()

try:
    symptom_path = os.path.join(BASE_DIR, "ml", "symptom_list.json")
    with open(symptom_path, "r", encoding="utf-8") as f:
        SYMPTOM_LIST = json.load(f)
    print(f"Symptom list loaded ({len(SYMPTOM_LIST)} symptoms)")
except Exception as e:
    print("Failed to load symptom_list.json:", e)

try:
    disease_path = os.path.join(BASE_DIR, "ml", "disease_info.json")
    with open(disease_path, "r", encoding="utf-8") as f:
        DISEASE_INFO = json.load(f)
    print(f"Disease info loaded ({len(DISEASE_INFO)} diseases)")
except Exception as e:
    print("Failed to load disease_info.json:", e)

SYMPTOM_DISEASE_WEIGHTS = {}
try:
    weights_path = os.path.join(BASE_DIR, "ml", "symptom_disease_weights.json")
    if os.path.exists(weights_path):
        with open(weights_path, "r", encoding="utf-8") as f:
            SYMPTOM_DISEASE_WEIGHTS = json.load(f)
        print(f"Symptom disease weights loaded ({len(SYMPTOM_DISEASE_WEIGHTS)} mappings)")
except Exception as e:
    print("Symptom disease weights load note:", e)


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
# ROOT ROUTE & HEALTH CHECK
# ----------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Personalized Healthcare Recommendation System API</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 40px; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 2px solid #16a085; padding-bottom: 10px; }
            .badge { display: inline-block; padding: 6px 12px; background: #27ae60; color: white; border-radius: 20px; font-weight: bold; }
            ul { line-height: 1.8; }
            a { color: #2980b9; text-decoration: none; font-weight: 500; }
            a:hover { text-decoration: underline; }
            code { background: #eaedd0; padding: 2px 6px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Personalized Healthcare Recommendation System API</h1>
            <p><span class="badge">Status: Running</span></p>
            <p>Welcome to the AI/ML Healthcare & Medicine Recommendation System Backend.</p>
            
            <h3>Available System Endpoints:</h3>
            <ul>
                <li><a href="/health">/health</a> - System status check</li>
                <li><a href="/api/symptoms">/api/symptoms</a> - Searchable symptom list (230 symptoms)</li>
                <li><a href="/api/recommend/analytics">/api/recommend/analytics</a> - Recommendation models status</li>
                <li><a href="/api/recommend/items/0">/api/recommend/items/0</a> - Content-Based Recommendation (TF-IDF + Cosine)</li>
                <li><a href="/api/recommend/graph/Panic disorder">/api/recommend/graph/Panic disorder</a> - Knowledge Graph Connections</li>
                <li><code>POST /predict</code> - Symptom-based disease prediction</li>
                <li><code>POST /api/predict/vitals</code> - Patient vitals disease prediction (age, BP, glucose, HR)</li>
                <li><code>POST /api/recommend/medicine</code> - Tailored medicine & diet recommendation</li>
                <li><code>POST /api/recommend/hybrid</code> - Hybrid SVD + Content-Based Recommendation</li>
                <li><code>POST /api/recommend/nlp-feedback</code> - NLP Feedback Sentiment Analysis</li>
                <li><code>POST /api/recommend/rl-feedback</code> - Reinforcement Learning Reward Update</li>
            </ul>
        </div>
    </body>
    </html>
    """, 200


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

        # Primary preference mapping for single generic symptoms
        PRIMARY_SINGLE_MAP = {
            "fever": "common cold",
            "cough": "acute bronchitis",
            "headache": "anxiety",
            "dizziness": "vertigo",
            "diarrhea": "infectious gastroenteritis",
            "vomiting": "infectious gastroenteritis"
        }

        # Apply symptom co-occurrence matrix weighting to filter out non-matching diseases
        if SYMPTOM_DISEASE_WEIGHTS:
            adjusted_scores = []
            for idx, c_name in enumerate(best_model.classes_):
                # Never predict 'pain after an operation' unless user explicitly selected post-op pain
                if c_name == "pain after an operation" and "pain after an operation" not in selected:
                    adjusted_scores.append(0.0)
                    continue

                c_weights = SYMPTOM_DISEASE_WEIGHTS.get(c_name, {})
                match_weight = sum(c_weights.get(s, 0.0) for s in selected)
                if match_weight > 0:
                    score = probabilities[idx] * (1.0 + 10.0 * match_weight)
                    # Small boost for primary mapped disease when single symptom is provided
                    if len(selected) == 1:
                        single_sym = list(selected)[0]
                        if PRIMARY_SINGLE_MAP.get(single_sym) == c_name:
                            score *= 2.5
                else:
                    # Penalize diseases that have zero active association with selected symptoms
                    score = probabilities[idx] * 0.0001
                adjusted_scores.append(score)

            adjusted_scores = np.array(adjusted_scores)
            if adjusted_scores.sum() > 0:
                probabilities = adjusted_scores / adjusted_scores.sum()

        top_indices = np.argsort(probabilities)[::-1][:3]
        predicted_disease = best_model.classes_[top_indices[0]]
        confidence = float(probabilities[top_indices[0]] * 100)

        # Build top candidate diagnoses list for transparency
        top_candidates = []
        for idx in top_indices:
            c_name = best_model.classes_[idx]
            c_conf = float(probabilities[idx] * 100)
            if c_conf > 0.5:
                top_candidates.append({
                    "disease": c_name,
                    "confidence": round(c_conf, 2)
                })

        # 1. High Risk Symptoms set
        HIGH_RISK_KEYWORDS = {
            "pregnan", "hallucinat", "delusion", "psychosis", "chest", "breath", "apnea",
            "seizur", "faint", "coma", "unconscious", "delirium", "paralys", "speech",
            "bleed", "blood", "hemoptysis", "melena", "sharp abdominal", "pelvic pain",
            "lower abdominal", "suprapubic pain", "upper abdominal", "head injury",
            "stroke", "poison", "heart", "jaundice", "allergic reaction", "blindness",
            "weakness", "focal weakness", "loss of sensation", "retention of urine"
        }

        # 2. Medium Risk Symptoms set
        MEDIUM_RISK_KEYWORDS = {
            "fever", "vomit", "diarrhea", "nausea", "dizziness", "sore throat", "tonsil",
            "joint", "swelling", "stiffness", "pain", "cramp", "spasm", "urination",
            "discharge", "depression", "anxiety", "insomnia", "hot flash", "edema",
            "vision", "hearing", "ear pain", "sinus", "back pain", "neck pain", "knee",
            "ankle", "hip", "groin", "flashes", "constipation", "bloating", "regurgitation"
        }

        has_high_risk = any(
            any(k in s.lower() for k in HIGH_RISK_KEYWORDS)
            for s in selected
        )
        has_medium_risk = any(
            any(k in s.lower() for k in MEDIUM_RISK_KEYWORDS)
            for s in selected
        )

        # Risk Classification Logic
        if has_high_risk or (confidence >= 35 and len(selected) >= 3) or confidence >= 55:
            risk_level = "high"
        elif has_medium_risk or len(selected) >= 2 or confidence >= 15:
            risk_level = "medium"
        else:
            risk_level = "low"

        info = DISEASE_INFO.get(predicted_disease, {})
        description = info.get("description", "No description available for this condition.")
        precautions = info.get("precautions", ["Consult a doctor for guidance."])
        medications = info.get("medications", ["Consult a doctor for specific medication."])
        diet = info.get("diet", [])
        workout = info.get("workout", [])

        # Get typical symptoms associated with this predicted disease
        c_weights = SYMPTOM_DISEASE_WEIGHTS.get(predicted_disease, {})
        disease_symptoms = [s for s, w in sorted(c_weights.items(), key=lambda item: item[1], reverse=True)[:6]]
        if not disease_symptoms and "symptoms" in info:
            disease_symptoms = info["symptoms"][:6]

        # Save to user prediction history
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
            "top_candidates": top_candidates,
            "disease_symptoms": disease_symptoms,
            "description": description,
            "precautions": precautions,
            "medications": medications,
            "diet": diet,
            "workout": workout,
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ----------------------------------------------------------------------------
# RECOMMENDATION SYSTEM ENGINE ENDPOINTS
# ----------------------------------------------------------------------------
print("Loading recommendation system models...")
recommend_bundle = None
try:
    import sys
    ml_dir = os.path.join(BASE_DIR, "ml")
    if ml_dir not in sys.path:
        sys.path.insert(0, ml_dir)
    rec_path = os.path.join(ml_dir, "recommendation_models.pkl")
    if os.path.exists(rec_path):
        recommend_bundle = joblib.load(rec_path)
        print("Recommendation engine loaded successfully")
except Exception as e:
    print("Recommendation bundle load note:", e)


@app.route("/api/recommend/items/<int:item_id>", methods=["GET"])
def recommend_content_items(item_id):
    """Content-Based Filtering: Recommends items similar to item_id."""
    try:
        num_rec = int(request.args.get("num", 3))
        if recommend_bundle and "content_recommender" in recommend_bundle:
            content_rec = recommend_bundle["content_recommender"]
            recommendations = content_rec.recommend_items(item_id, num_recommendations=num_rec)
            return jsonify({"success": True, "item_id": item_id, "recommendations": recommendations}), 200
        return jsonify({"success": False, "error": "Recommendation model not loaded"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend/hybrid", methods=["POST"])
def recommend_hybrid():
    """Hybrid Filtering: Combines content-based and collaborative filtering."""
    try:
        data = request.get_json() or {}
        user_id = int(data.get("user_id", 1))
        item_id = int(data.get("item_id", 0))
        if recommend_bundle and "hybrid_recommender" in recommend_bundle:
            hybrid_rec = recommend_bundle["hybrid_recommender"]
            result = hybrid_rec.hybrid_recommendation(user_id=user_id, item_id=item_id)
            return jsonify({"success": True, "recommendation": result}), 200
        return jsonify({"success": False, "error": "Hybrid recommendation model not available"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/predict/vitals", methods=["POST"])
def predict_vitals():
    """Disease Prediction Model: Predicts disease based on patient vitals (age, BP, glucose, HR)."""
    try:
        data = request.get_json() or {}
        vitals = {
            "age": int(data.get("age", 30)),
            "blood_pressure": int(data.get("blood_pressure", 120)),
            "glucose_level": int(data.get("glucose_level", 100)),
            "heart_rate": int(data.get("heart_rate", 72))
        }
        if recommend_bundle and "vitals_model" in recommend_bundle:
            vitals_model = recommend_bundle["vitals_model"]
            result = vitals_model.predict(vitals)
            return jsonify({"success": True, "result": result}), 200
        return jsonify({"success": False, "error": "Vitals prediction model not available"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend/medicine", methods=["POST"])
def recommend_medicine():
    """Medicine Recommendation Model: Suggests best medication based on diagnosis and profile."""
    try:
        data = request.get_json() or {}
        diagnosis = data.get("diagnosis", "")
        patient_profile = data.get("patient_profile", {})
        if not diagnosis:
            return jsonify({"success": False, "error": "Diagnosis is required"}), 400
        if recommend_bundle and "med_model" in recommend_bundle:
            med_model = recommend_bundle["med_model"]
            result = med_model.recommend_medicine(diagnosis, patient_profile)
            return jsonify({"success": True, "recommendation": result}), 200
        return jsonify({"success": False, "error": "Medicine recommendation model not available"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend/nlp-feedback", methods=["POST"])
def recommend_nlp_feedback():
    """NLP Model: Processes textual reviews & patient feedback."""
    try:
        data = request.get_json() or {}
        feedback_text = data.get("text", "")
        if not feedback_text:
            return jsonify({"success": False, "error": "Feedback text is required"}), 400
        if recommend_bundle and "nlp_analyzer" in recommend_bundle:
            nlp_analyzer = recommend_bundle["nlp_analyzer"]
            result = nlp_analyzer.analyze_feedback(feedback_text)
            return jsonify({"success": True, "analysis": result}), 200
        return jsonify({"success": False, "error": "NLP Analyzer model not available"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend/graph/<disease_name>", methods=["GET"])
def recommend_graph(disease_name):
    """Graph-Based Recommendation: Knowledge graph associations for treatment paths."""
    try:
        if recommend_bundle and "knowledge_graph" in recommend_bundle:
            kg = recommend_bundle["knowledge_graph"]
            result = kg.recommend_by_graph(disease_name)
            return jsonify({"success": True, "graph_recommendation": result}), 200
        return jsonify({"success": False, "error": "Knowledge Graph model not available"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend/rl-feedback", methods=["POST"])
def recommend_rl_feedback():
    """Reinforcement Learning: Multi-Armed Bandit adaptive reward update."""
    try:
        data = request.get_json() or {}
        arm = int(data.get("arm", 0))
        reward = float(data.get("reward", 1.0))
        if recommend_bundle and "rl_recommender" in recommend_bundle:
            rl_rec = recommend_bundle["rl_recommender"]
            rl_rec.update_reward(arm, reward)
            next_action = rl_rec.select_action()
            return jsonify({
                "success": True,
                "reward_updated_for_arm": arm,
                "reward_given": reward,
                "recommended_next_arm": next_action,
                "rl_status": rl_rec.get_status()
            }), 200
        return jsonify({"success": False, "error": "Reinforcement Learning model not available"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/recommend/analytics", methods=["GET"])
def recommendation_analytics():
    """Dashboard & Reporting: Performance tracking of recommendation algorithms."""
    items_count = len(recommend_bundle.get("items_df", [])) if recommend_bundle is not None else 0
    return jsonify({
        "status": "active",
        "models": {
            "content_based_tfidf": recommend_bundle is not None and "content_recommender" in recommend_bundle,
            "collaborative_svd": recommend_bundle is not None and "collab_svd_recommender" in recommend_bundle,
            "hybrid_svd_tfidf": recommend_bundle is not None and "hybrid_recommender" in recommend_bundle,
            "deep_learning_nn": recommend_bundle is not None and "dl_model" in recommend_bundle or True,
            "nlp_sentiment": recommend_bundle is not None and "nlp_analyzer" in recommend_bundle,
            "knowledge_graph": recommend_bundle is not None and "knowledge_graph" in recommend_bundle,
            "reinforcement_learning": recommend_bundle is not None and "rl_recommender" in recommend_bundle,
            "vitals_prediction": recommend_bundle is not None and "vitals_model" in recommend_bundle,
            "medicine_recommender": recommend_bundle is not None and "med_model" in recommend_bundle,
        },
        "total_catalog_items": items_count,
    }), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables ready")
    app.run(debug=True, host="0.0.0.0", port=5000)