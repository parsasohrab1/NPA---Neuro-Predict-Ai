"""
Patient Schemas
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date, datetime
from ..models.patient import Gender


class PatientBase(BaseModel):
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    education_years: Optional[int] = None
    medical_history: Optional[str] = None
    family_history: Optional[str] = None
    current_medications: Optional[str] = None

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("patient_id must not be empty")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        from datetime import date as _date
        if v >= _date.today():
            raise ValueError("date_of_birth must be in the past")
        return v


class PatientCreate(PatientBase):
    assigned_doctor_id: Optional[int] = None


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    education_years: Optional[int] = None
    medical_history: Optional[str] = None
    family_history: Optional[str] = None
    current_medications: Optional[str] = None
    assigned_doctor_id: Optional[int] = None


class PatientResponse(PatientBase):
    id: int
    assigned_doctor_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

