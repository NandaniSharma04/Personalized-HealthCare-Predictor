from fastapi.testclient import TestClient
import subprocess
import os

# This integration test expects the backend FastAPI app to be available
from backend.app.main import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
