"""
Medical Record Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MedicalRecordCreate(BaseModel):
    visit_date: datetime
    visit_type: Optional[str] = None
    mmse_score: Optional[float] = None
    moca_score: Optional[float] = None
    memory_score: Optional[float] = None
    attention_score: Optional[float] = None
    executive_function_score: Optional[float] = None
    amyloid_beta: Optional[float] = None
    tau_protein: Optional[float] = None
    dopamine_level: Optional[float] = None
    apoe_e4_status: Optional[bool] = None
    hippocampal_volume: Optional[float] = None
    cortical_thickness: Optional[float] = None
    ventricular_volume: Optional[float] = None
    white_matter_hyperintensities: Optional[float] = None
    brain_volume_total: Optional[float] = None
    symptoms: Optional[str] = None
    clinical_notes: Optional[str] = None

