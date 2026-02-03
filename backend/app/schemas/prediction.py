"""
Prediction Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..models.prediction import DiseaseType, RiskLevel


# --- Clinical Explainability (Explainable AI for physicians) ---


class ClinicalFeatureImportanceItem(BaseModel):
    """Single feature with clinical labels and interpretation."""
    feature_key: str
    clinical_label_fa: str
    clinical_label_en: str
    importance: float = Field(..., ge=0.0, le=1.0)
    interpretation_fa: Optional[str] = None
    interpretation_en: Optional[str] = None


class CohortDiseaseSummary(BaseModel):
    """Cohort distribution summary for one disease (Alzheimer or Parkinson)."""
    patient_percentile: Optional[float] = None
    cohort_min: Optional[float] = None
    cohort_p25: Optional[float] = None
    cohort_median: Optional[float] = None
    cohort_p75: Optional[float] = None
    cohort_max: Optional[float] = None
    cohort_size: Optional[int] = None
    summary_fa: Optional[str] = None
    summary_en: Optional[str] = None


class CohortComparison(BaseModel):
    """Comparison of this patient's risk to a similar cohort."""
    cohort_size: int = 0
    cohort_description_fa: Optional[str] = None
    cohort_description_en: Optional[str] = None
    alzheimer: Optional[CohortDiseaseSummary] = None
    parkinson: Optional[CohortDiseaseSummary] = None


class ProgressionVisualization(BaseModel):
    """Data for neurological progression visualization."""
    has_longitudinal_data: bool = False
    trend_data: Optional[Dict[str, Any]] = None
    recommended_follow_up_months: int = 12
    trajectory_summary_fa: Optional[str] = None
    trajectory_summary_en: Optional[str] = None
    risk_context: Optional[Dict[str, str]] = None


class ClinicalExplanation(BaseModel):
    """Full clinical explainability: feature importance, cohort comparison, progression."""
    clinical_feature_importance: List[ClinicalFeatureImportanceItem] = Field(default_factory=list)
    cohort_comparison: Optional[CohortComparison] = None
    progression_visualization: Optional[ProgressionVisualization] = None


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
    clinical_explanation: Optional[ClinicalExplanation] = Field(
        None,
        description="Explainable AI for physicians: clinical feature importance, cohort comparison, progression",
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

