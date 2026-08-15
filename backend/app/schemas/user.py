from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date


class ProfileOut(BaseModel):
    user_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    dob: Optional[date]
    gender: Optional[str]
    address: Optional[str]

    class Config:
        orm_mode = True


class ProfileUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    dob: Optional[date]
    gender: Optional[str]
    address: Optional[str]


class MedicalProfileOut(BaseModel):
    id: int
    user_id: int
    blood_type: Optional[str]
    allergies: Optional[str]
    chronic_conditions: Optional[str]
    medications: Optional[str]

    class Config:
        orm_mode = True


class MedicalProfileUpdate(BaseModel):
    blood_type: Optional[str]
    allergies: Optional[str]
    chronic_conditions: Optional[str]
    medications: Optional[str]


class SymptomInput(BaseModel):
    symptoms: List[str] = Field(..., min_items=1)


class DashboardOut(BaseModel):
    profile: Optional[ProfileOut]
    medical: Optional[MedicalProfileOut]
    recent_predictions: Optional[List[dict]]
    recent_recommendations: Optional[List[dict]]
    unread_notifications: int

    class Config:
        orm_mode = True


class FeedbackIn(BaseModel):
    target_type: Optional[str]
    target_id: Optional[int]
    rating: Optional[int]
    comment: Optional[str]



class NotificationOut(BaseModel):
    id: int
    message: str
    payload: Optional[dict]
    is_read: bool

    class Config:
        orm_mode = True
