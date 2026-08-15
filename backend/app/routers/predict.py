from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class PredictRequest(BaseModel):
    symptoms: list[str]


@router.post("/predict")
def predict(req: PredictRequest):
    # Placeholder: call ModelService to get prediction
    return {"disease": "Common Cold", "confidence": 0.78}
