import requests


class ModelService:
    """Thin client to call the ML inference service.

    Usage: inject `ModelService()` where needed and call `predict(symptoms)`.
    """

    def __init__(self, url: str = "http://ml-service:8500"):
        self.url = url

    def predict(self, symptoms: list[str]) -> dict:
        try:
            r = requests.post(f"{self.url}/predict", json={"symptoms": symptoms}, timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception:
            return {"disease": "unknown", "confidence": 0.0}
