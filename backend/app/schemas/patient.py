"""
Patient Schemas
"""
import re

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date, datetime
from ..models.patient import Gender


# Person names: letters (any script), digits, spaces and . ' ’ - only.
# Rejects markup/script payloads (<, >, :, (, ", =, ...) at the API boundary.
_NAME_PATTERN = re.compile(r"^[\w\s.'’\-]+$")


def _validate_person_name(value):
    if value is None:
        return value
    value = value.strip()
    if not value or not _NAME_PATTERN.fullmatch(value):
        raise ValueError(
            "Name may only contain letters, digits, spaces, apostrophes, periods and hyphens"
        )
    return value


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

    @field_validator("first_name", "last_name")
    @classmethod
    def _check_name(cls, value):
        return _validate_person_name(value)


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

    @field_validator("first_name", "last_name")
    @classmethod
    def _check_name(cls, value):
        return _validate_person_name(value)


class PatientResponse(PatientBase):
    id: int
    assigned_doctor_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

