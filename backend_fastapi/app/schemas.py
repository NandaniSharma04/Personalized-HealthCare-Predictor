from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str]
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str]

    class Config:
        orm_mode = True


class SymptomOut(BaseModel):
    name: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int]


class RoleOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class PredictRequest(BaseModel):
    # either provide symptom names or a mapping
    symptoms: Optional[list[str]] = None
    symptom_vector: Optional[dict[str, int]] = None


class PredictionItem(BaseModel):
    disease: str
    probability: float


class PredictResponse(BaseModel):
    top_k: list[PredictionItem]
    explainability: Optional[dict] = None
    predicted_disease: Optional[str] = None
    confidence: Optional[float] = None
    risk_level: Optional[str] = None
    description: Optional[str] = None
    medicines: Optional[list[str]] = None
    advice: Optional[list[str]] = None
    diet: Optional[list[str]] = None
    workout: Optional[list[str]] = None


class FeedbackCreate(BaseModel):
    text: str
    source: Optional[str] = None
    metadata: Optional[dict] = None


class FeedbackOut(BaseModel):
    id: int
    user_id: Optional[int]
    text: str
    sentiment_score: float
    sentiment_label: str
    metadata: Optional[dict]

    class Config:
        orm_mode = True


