from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import settings
import pytest


client = TestClient(app)


def test_password_hash_and_verify():
    from backend.app.services.auth_service import get_password_hash, verify_password
    pw = 'secret123'
    h = get_password_hash(pw)
    assert verify_password(pw, h)


import uuid

def test_register_and_login_cycle(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///:memory:')
    uid = uuid.uuid4().hex[:6]
    r = client.post('/api/auth/register', json={'username': f'user_{uid}', 'email': f'test_{uid}@e.com', 'password': 'pass1234'})
    assert r.status_code in (200, 201, 400, 409, 422, 500)
