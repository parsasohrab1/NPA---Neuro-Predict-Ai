"""
Prediction Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from ..models.prediction import DiseaseType, RiskLevel


class PredictionRequest(BaseModel):
    patient_id: int
    disease_type: DiseaseType = DiseaseType.BOTH
    include_imaging: bool = True
    include_biomarkers: bool = True
    include_genetic: bool = True


class AlzheimerPrediction(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0.0, le=1.0)


class ParkinsonPrediction(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0.0, le=1.0)


class PredictionResponse(BaseModel):
    id: int
    patient_id: int
    disease_type: DiseaseType
    
    alzheimer_prediction: Optional[AlzheimerPrediction] = None
    parkinson_prediction: Optional[ParkinsonPrediction] = None
    
    model_version: Optional[str] = None
    model_name: Optional[str] = None

    feature_importance: Optional[Dict[str, float]] = None
    attention_scores: Optional[Dict[str, float]] = Field(
        None,
        description="Explainability: modality weights MRI, Biomarker, Cognitive (sum = 1.0)",
    )
    recommendations: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    
    is_reviewed: bool = False
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    
    created_at: datetime
    created_by: int
    
    class Config:
        from_attributes = True


class PredictionReview(BaseModel):
    review_notes: str
    approved: bool = True

