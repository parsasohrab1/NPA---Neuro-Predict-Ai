"""
Data Fusion Report Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class FusionScoresResponse(BaseModel):
    """Fusion scores for each modality"""
    cognitive: float = Field(..., ge=0, le=100, description="Cognitive modality score")
    biomarker: float = Field(..., ge=0, le=100, description="Biomarker modality score")
    imaging: float = Field(..., ge=0, le=100, description="Imaging modality score")
    integrated: float = Field(..., ge=0, le=100, description="Integrated fusion score")
    confidence: str = Field(..., description="Confidence level")


class CrossModalAnalysisResponse(BaseModel):
    """Cross-modal correlation analysis"""
    consistency_score: float = Field(..., ge=0, le=100)
    correlations: Dict[str, float]
    has_conflicts: bool


class DiseaseAnalysisResponse(BaseModel):
    """Disease-specific analysis"""
    score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    indicators: Dict[str, float]


class InterpretationResponse(BaseModel):
    """Clinical interpretation"""
    overall: str
    primary_concern: str
    confidence: float
    evidence: Dict[str, str]


class ReportSectionsResponse(BaseModel):
    """Report text sections"""
    executive_summary: str
    detailed_findings: str
    risk_assessment: str
    recommendations: str
    follow_up_plan: Optional[str]


class QualityMetricsResponse(BaseModel):
    """Data quality metrics"""
    data_completeness: float
    has_outliers: bool
    quality_notes: Optional[str]


class FusionMetadataResponse(BaseModel):
    """Report metadata"""
    report_version: str
    algorithm_version: str
    processing_time_ms: Optional[int]


class DataFusionReportResponse(BaseModel):
    """Complete Data Fusion Report Response"""
    id: int
    patient_id: int
    medical_record_id: Optional[int]
    generated_at: datetime
    
    fusion_scores: FusionScoresResponse
    cross_modal: CrossModalAnalysisResponse
    disease_analysis: Dict[str, DiseaseAnalysisResponse]
    interpretation: InterpretationResponse
    report: ReportSectionsResponse
    quality: QualityMetricsResponse
    metadata: FusionMetadataResponse
    
    class Config:
        from_attributes = True


class DataFusionReportCreate(BaseModel):
    """Request to create fusion report"""
    patient_id: int = Field(..., description="Patient ID")
    medical_record_id: Optional[int] = Field(None, description="Specific medical record ID, or use latest")
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "medical_record_id": 123
            }
        }

