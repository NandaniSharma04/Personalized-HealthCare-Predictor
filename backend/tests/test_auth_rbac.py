"""
Comprehensive Test Suite for Authentication & Role-Based Access Control (RBAC)
Tests:
- Valid login
- Invalid login
- Duplicate registration
- Unauthorized request
- User accessing admin API (Forbidden 403)
- Analyst accessing admin-only API (Forbidden 403)
- Account status (disabled/suspended)
- Logout
"""
import uuid
import pytest
from backend.app import create_app
from backend.utils.db import db
from backend.models import User
from backend.utils.security import hash_password

@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    test_app = create_app()
    test_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret"
    })
    with test_app.app_context():
        user = User(name="Regular User", email="test_user@health.ai", password_hash=hash_password("Pass123!"), role="user", status="active")
        analyst = User(name="Health Analyst", email="test_analyst@health.ai", password_hash=hash_password("Pass123!"), role="analyst", status="active")
        admin = User(name="System Admin", email="test_admin@health.ai", password_hash=hash_password("Pass123!"), role="admin", status="active")
        suspended = User(name="Suspended User", email="test_suspended@health.ai", password_hash=hash_password("Pass123!"), role="user", status="suspended")
        
        db.session.add_all([user, analyst, admin, suspended])
        db.session.commit()
        
        yield test_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_valid_login(client):
    res = client.post("/api/auth/login", json={"email": "test_user@health.ai", "password": "Pass123!"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["email"] == "test_user@health.ai"
    assert data["user"]["role"] == "user"

def test_invalid_login(client):
    res = client.post("/api/auth/login", json={"email": "test_user@health.ai", "password": "WrongPassword!"})
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False
    assert data["code"] == "INVALID_CREDENTIALS"

def test_duplicate_registration(client):
    res = client.post("/api/auth/register", json={"name": "Duplicate User", "email": "test_user@health.ai", "password": "NewPassword123!"})
    assert res.status_code == 409
    data = res.get_json()
    assert data["success"] is False
    assert data["code"] == "DUPLICATE_USER"

def test_unauthorized_request(client):
    res = client.get("/api/admin/users")
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False

def test_user_accessing_admin_api_forbidden(client):
    # Login as regular user
    client.post("/api/auth/login", json={"email": "test_user@health.ai", "password": "Pass123!"})
    # Attempt to access Admin API
    res = client.get("/api/admin/users")
    assert res.status_code == 403
    data = res.get_json()
    assert data["success"] is False
    assert data["code"] == "FORBIDDEN"

def test_analyst_accessing_admin_only_api_forbidden(client):
    # Login as analyst
    client.post("/api/auth/login", json={"email": "test_analyst@health.ai", "password": "Pass123!"})
    # Attempt to access Admin API
    res = client.get("/api/admin/users")
    assert res.status_code == 403
    data = res.get_json()
    assert data["success"] is False
    assert data["code"] == "FORBIDDEN"

def test_admin_accessing_admin_api_success(client):
    # Login as admin
    client.post("/api/auth/login", json={"email": "test_admin@health.ai", "password": "Pass123!"})
    # Access Admin API
    res = client.get("/api/admin/users")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["users"]) >= 1

def test_suspended_account_login_blocked(client):
    res = client.post("/api/auth/login", json={"email": "test_suspended@health.ai", "password": "Pass123!"})
    assert res.status_code == 403
    data = res.get_json()
    assert data["success"] is False
    assert data["code"] == "ACCOUNT_DISABLED"

def test_logout_cycle(client):
    # Login
    client.post("/api/auth/login", json={"email": "test_user@health.ai", "password": "Pass123!"})
    me_res = client.get("/api/auth/me")
    assert me_res.get_json()["logged_in"] is True
    
    # Logout
    logout_res = client.post("/api/auth/logout")
    assert logout_res.status_code == 200
    
    # Check session terminated
    me_after = client.get("/api/auth/me")
    assert me_after.get_json()["logged_in"] is False
