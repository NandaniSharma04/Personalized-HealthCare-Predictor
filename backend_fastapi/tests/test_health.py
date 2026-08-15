from fastapi.testclient import TestClient
try:
    from backend_fastapi.app.main import app
except ModuleNotFoundError:
    from app.main import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
