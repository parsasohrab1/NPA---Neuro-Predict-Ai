"""
Reporting Schemas
"""
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from ..models.prediction import DiseaseType, RiskLevel


class ClinicalPatientSummary(BaseModel):
    id: int
    patient_identifier: str
    full_name: str
    age: float = Field(..., ge=0)
    gender: str


class ClinicalPredictionSummary(BaseModel):
    id: int
    created_at: datetime
    disease_type: DiseaseType
    alzheimer_risk_score: Optional[float] = Field(None, ge=0, le=1)
    alzheimer_risk_level: Optional[RiskLevel] = None
    parkinson_risk_score: Optional[float] = Field(None, ge=0, le=1)
    parkinson_risk_level: Optional[RiskLevel] = None
    recommendations: Optional[str] = None


class ClinicalReport(BaseModel):
    patient: ClinicalPatientSummary
    predictions: List[ClinicalPredictionSummary]
    last_medical_record_at: Optional[datetime] = None
    pending_follow_up: bool = False


class ResearchAggregation(BaseModel):
    disease_type: DiseaseType
    risk_level: Optional[RiskLevel] = None
    count: int


class ResearchReport(BaseModel):
    total_predictions: int
    unique_patients: int
    aggregation: List[ResearchAggregation]
    timeframe_start: Optional[datetime] = None
    timeframe_end: Optional[datetime] = None


class ManagementKpi(BaseModel):
    total_predictions: int
    reviewed_predictions: int
    active_patients: int
    avg_response_time_ms: Optional[float] = None


class ManagementAlert(BaseModel):
    title: str
    severity: str
    description: str
    created_at: datetime


class ManagementReport(BaseModel):
    kpi: ManagementKpi
    model_version_distribution: Dict[str, int]
    alerts: List[ManagementAlert]


class ReportExportRequest(BaseModel):
    report_type: str
    format: str = Field(..., pattern="^(pdf|excel|csv)$")
    filters: Dict[str, Optional[str]] = Field(default_factory=dict)


class ReportExportResponse(BaseModel):
    message: str
    report_type: str
    format: str
    filters: Dict[str, Optional[str]]
    generated_at: datetime


