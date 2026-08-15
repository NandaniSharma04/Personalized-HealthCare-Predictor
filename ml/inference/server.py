from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="ML Inference")


class PredictRequest(BaseModel):
    symptoms: list[str]


@app.post("/predict")
def predict(req: PredictRequest):
    # Simple rule-based placeholder for inference
    if "fever" in [s.lower() for s in req.symptoms]:
        return {"disease": "Flu", "confidence": 0.86}
    return {"disease": "Common Cold", "confidence": 0.6}
