"""
Patient Schemas
"""
from pydantic import BaseModel, EmailStr
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

