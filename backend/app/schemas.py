import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    skin_tone: Optional[str] = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    age: int
    gender: str
    skin_tone: str


class LesionCreate(BaseModel):
    body_part: str
    label: Optional[str] = None


class CaptureOut(BaseModel):
    id: int
    image_path: str
    heatmap_path: Optional[str] = None
    classification: str
    confidence: float
    urgency: str
    gemini_report: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class LesionOut(BaseModel):
    id: int
    body_part: str
    label: Optional[str] = None
    created_at: datetime.datetime
    captures: list[CaptureOut] = []

    class Config:
        from_attributes = True


class LesionSummary(BaseModel):
    id: int
    body_part: str
    label: Optional[str] = None
    latest_classification: Optional[str] = None
    latest_urgency: Optional[str] = None
    latest_created_at: Optional[datetime.datetime] = None
    change_status: Optional[str] = None  # "new" | "no_change" | "changed"

    class Config:
        from_attributes = True


class CaptureDetail(CaptureOut):
    lesion_id: int
    body_part: str
    lesion_label: Optional[str] = None


class ClinicOut(BaseModel):
    name: str
    address: str
    lat: float
    lng: float
    distance_km: float
    phone: str
