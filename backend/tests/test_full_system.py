"""
Comprehensive End-to-End System Test Suite for Personalized Healthcare Predictor
"""
import pytest
from backend.app import create_app
from backend.utils.db import db
from backend.models import User, PredictionHistory, HealthProfile, UserProfile, Recommendation, Notification, UserActivity
from backend.ml.predictor import predict_symptoms, get_model_metadata

@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    test_app = create_app()
    test_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_e2e_secret_key"
    })
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# ============================================================================
# 1. AUTH & USER LIFECYCLE TESTS
# ============================================================================
def test_user_signup_and_duplicate_handling(client):
    res = client.post("/api/auth/register", json={
        "name": "Alice Patient",
        "email": "alice@test.local",
        "password": "SecurePassword123!",
        "role": "user"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["email"] == "alice@test.local"

    # Duplicate signup rejected with 409
    res_dup = client.post("/api/auth/register", json={
        "name": "Alice Duplicate",
        "email": "alice@test.local",
        "password": "AnotherPassword123!"
    })
    assert res_dup.status_code == 409
    assert res_dup.get_json()["code"] == "DUPLICATE_USER"

def test_login_and_wrong_password(client):
    client.post("/api/auth/register", json={
        "name": "Alice Patient",
        "email": "alice@test.local",
        "password": "SecurePassword123!",
        "role": "user"
    })

    # 1. Wrong password
    res_wrong = client.post("/api/auth/login", json={
        "email": "alice@test.local",
        "password": "WrongPassword!"
    })
    assert res_wrong.status_code == 401
    assert res_wrong.get_json()["success"] is False

    # 2. Correct login
    res_ok = client.post("/api/auth/login", json={
        "email": "alice@test.local",
        "password": "SecurePassword123!"
    })
    assert res_ok.status_code == 200
    assert res_ok.get_json()["user"]["name"] == "Alice Patient"

    # 3. Check /api/auth/me
    res_me = client.get("/api/auth/me")
    assert res_me.status_code == 200
    assert res_me.get_json()["user"]["email"] == "alice@test.local"

    # 4. Logout
    res_logout = client.post("/api/auth/logout")
    assert res_logout.status_code == 200

# ============================================================================
# 2. RBAC & SECURITY PRIVILEGE ESCALATION TESTS
# ============================================================================
def test_rbac_privilege_escalation_prevention(client):
    client.post("/api/auth/register", json={
        "name": "Alice Patient",
        "email": "alice@test.local",
        "password": "SecurePassword123!",
        "role": "user"
    })
    client.post("/api/auth/register", json={
        "name": "Bob Analyst",
        "email": "bob@analyst.local",
        "password": "AnalystPassword123!",
        "role": "analyst"
    })
    client.post("/api/auth/register", json={
        "name": "Charlie Admin",
        "email": "charlie@admin.local",
        "password": "AdminPassword123!",
        "role": "admin"
    })

    # A. Test Unauthenticated Access
    client.post("/api/auth/logout")
    res_unauth = client.get("/api/admin/users")
    assert res_unauth.status_code in [401, 403]

    # B. Test User -> Admin Access (Must be Forbidden 403)
    client.post("/api/auth/login", json={"email": "alice@test.local", "password": "SecurePassword123!"})
    res_user_admin = client.get("/api/admin/users")
    assert res_user_admin.status_code == 403

    # C. Test Analyst -> Admin Access (Must be Forbidden 403)
    client.post("/api/auth/logout")
    client.post("/api/auth/login", json={"email": "bob@analyst.local", "password": "AnalystPassword123!"})
    res_analyst_admin = client.get("/api/admin/users")
    assert res_analyst_admin.status_code == 403
    # But Analyst CAN access Analyst telemetry
    res_analyst_ok = client.get("/api/analytics/model-performance")
    assert res_analyst_ok.status_code == 200

    # D. Test Admin Access (Must be Authorized 200)
    client.post("/api/auth/logout")
    client.post("/api/auth/login", json={"email": "charlie@admin.local", "password": "AdminPassword123!"})
    res_admin_ok = client.get("/api/admin/users")
    assert res_admin_ok.status_code == 200
    assert len(res_admin_ok.get_json()["users"]) >= 3

# ============================================================================
# 3. ML INFERENCE & EDGE CASES
# ============================================================================
def test_ml_predictor_pipeline_and_edge_cases():
    meta = get_model_metadata()
    assert meta["status"] == "PRODUCTION_READY"
    assert meta["input_features"] == 230
    assert meta["input_classes"] == 100

    pred = predict_symptoms(["fever", "cough", "fatigue"])
    assert "predicted_disease" in pred
    assert pred["confidence"] > 0
    assert pred["risk_level"] in ["low", "medium", "high"]
    assert "disclaimer" in pred
    assert len(pred["top_candidates"]) >= 1

    # Case insensitivity
    pred_case = predict_symptoms(["  FEVER  ", "Cough"])
    assert pred_case["confidence"] > 0

    # Unknown symptoms handling (raises ValueError)
    with pytest.raises(ValueError):
        predict_symptoms(["unknown_symptom_xyz_123"])

    # Empty symptoms handling (raises ValueError)
    with pytest.raises(ValueError):
        predict_symptoms([])

def test_prediction_api_endpoint(client):
    client.post("/api/auth/register", json={
        "name": "Alice Patient",
        "email": "alice@test.local",
        "password": "SecurePassword123!",
        "role": "user"
    })
    client.post("/api/auth/login", json={"email": "alice@test.local", "password": "SecurePassword123!"})
    
    # Valid prediction via API
    res = client.post("/api/predict", json={"symptoms": ["headache", "dizziness", "nausea"]})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "predicted_disease" in data

    # Malformed request
    res_malformed = client.post("/api/predict", json={"symptoms": []})
    assert res_malformed.status_code == 400

# ============================================================================
# 4. RECOMMENDATIONS & FEEDBACK SYSTEM
# ============================================================================
def test_recommendation_pipeline_and_feedback(client):
    client.post("/api/auth/register", json={
        "name": "Alice Patient",
        "email": "alice@test.local",
        "password": "SecurePassword123!",
        "role": "user"
    })
    client.post("/api/auth/login", json={"email": "alice@test.local", "password": "SecurePassword123!"})

    # 1. Get multi-category recommendations for a valid dataset disease
    res = client.post("/api/recommendations", json={"disease": "Panic disorder"})
    assert res.status_code == 200
    recs = res.get_json()["recommendations"]
    assert len(recs) > 0
    categories = {r["category"] for r in recs}
    assert "medicine" in categories
    assert "precaution" in categories

    # 2. Save recommendation
    res_save = client.post("/api/recommendations/save", json={
        "recommendation_id": 1,
        "title": "Breathing Exercises",
        "notes": "Follow daily"
    })
    assert res_save.status_code == 201
    assert res_save.get_json()["success"] is True

    # 3. Submit feedback rating (1-5)
    res_fb = client.post("/api/recommendations/feedback", json={
        "recommendation_id": 1,
        "rating": 5,
        "feedback_text": "Extremely helpful advice."
    })
    assert res_fb.status_code == 200
    assert res_fb.get_json()["rating"] == 5

# ============================================================================
# 5. USER PORTAL, ACTIVITY & NOTIFICATIONS
# ============================================================================
def test_user_portal_activity_and_notifications(client):
    client.post("/api/auth/register", json={
        "name": "Alice Patient",
        "email": "alice@test.local",
        "password": "SecurePassword123!",
        "role": "user"
    })
    client.post("/api/auth/login", json={"email": "alice@test.local", "password": "SecurePassword123!"})

    # Trigger a prediction first
    client.post("/api/predict", json={"symptoms": ["headache", "dizziness"]})

    # 1. User Dashboard endpoint
    res_dash = client.get("/api/user/dashboard")
    assert res_dash.status_code == 200
    dash = res_dash.get_json()
    assert dash["success"] is True
    assert "kpi_stats" in dash
    assert dash["kpi_stats"]["predictions_completed"] >= 1
    assert "health_insights" in dash

    # 2. Health Profile update
    res_hp = client.put("/api/user/health-profile", json={
        "age": 28,
        "gender": "female",
        "allergies": ["Penicillin"],
        "existing_conditions": ["Mild Asthma"],
        "current_medications": ["Inhaler"]
    })
    assert res_hp.status_code == 200
    assert res_hp.get_json()["health_profile"]["age"] == 28

    # 3. Activity Timeline
    res_act = client.get("/api/user/activity")
    assert res_act.status_code == 200
    activities = res_act.get_json()["activities"]
    assert len(activities) > 0
    act_types = [a["type"] for a in activities]
    assert "PREDICTION" in act_types or "PROFILE_UPDATE" in act_types

    # 4. Notifications
    res_notes = client.get("/api/user/notifications")
    assert res_notes.status_code == 200
    notes = res_notes.get_json()["notifications"]
    assert len(notes) > 0

    # Mark notification read
    note_id = notes[0]["id"]
    res_read = client.put(f"/api/user/notifications/{note_id}/read")
    assert res_read.status_code == 200

# ============================================================================
# 6. ADMIN DASHBOARD & GOVERNANCE APIS
# ============================================================================
def test_admin_governance_analytics(client):
    client.post("/api/auth/register", json={
        "name": "Charlie Admin",
        "email": "charlie@admin.local",
        "password": "AdminPassword123!",
        "role": "admin"
    })
    client.post("/api/auth/login", json={"email": "charlie@admin.local", "password": "AdminPassword123!"})

    # 1. Dashboard analytics
    res_analytics = client.get("/api/admin/dashboard-analytics?timeframe=7_days")
    assert res_analytics.status_code == 200
    data = res_analytics.get_json()
    assert data["success"] is True
    assert data["kpi_cards"]["total_users"] >= 1
    assert data["model_analytics"]["accuracy"] > 85.0
    assert data["system_status"]["api_health"] == "OPTIMAL"

    # 2. Healthcare content datasets
    res_diseases = client.get("/api/admin/diseases")
    assert res_diseases.status_code == 200
    assert res_diseases.get_json()["total_diseases"] >= 100

    # 3. Settings update
    res_settings = client.put("/api/admin/settings", json={
        "system_name": "HealthAI Enterprise",
        "maintenance_mode": False,
        "allow_registrations": True,
        "confidence_threshold": 55.0,
        "notification_email": "admin@healthai.local"
    })
    assert res_settings.status_code == 200

# ============================================================================
# 7. ANALYST DASHBOARD & DATA QUALITY APIS
# ============================================================================
def test_analyst_data_quality_and_sentiment(client):
    client.post("/api/auth/register", json={
        "name": "Bob Analyst",
        "email": "bob@analyst.local",
        "password": "AnalystPassword123!",
        "role": "analyst"
    })
    client.post("/api/auth/login", json={"email": "bob@analyst.local", "password": "AnalystPassword123!"})

    # 1. Model performance
    res_mp = client.get("/api/analytics/model-performance")
    assert res_mp.status_code == 200
    assert res_mp.get_json()["metrics"]["accuracy"] > 85.0

    # 2. Data quality audit
    res_dq = client.get("/api/analytics/data-quality")
    assert res_dq.status_code == 200
    dq = res_dq.get_json()
    assert dq["dataset_statistics"]["canonical_features"] == 230
    assert dq["quality_audit"]["missing_null_values"] == 0

    # 3. Sentiment breakdown
    res_sent = client.get("/api/analytics/sentiment")
    assert res_sent.status_code == 200
    assert "sentiment_breakdown" in res_sent.get_json()
