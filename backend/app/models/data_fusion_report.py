"""
Data Fusion Report Model
Patent-pending multi-modal data fusion and interpretation system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..db.session import Base


class FusionConfidence(str, enum.Enum):
    """Confidence level of fusion analysis"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class FusionInterpretation(str, enum.Enum):
    """Overall interpretation from fusion"""
    NORMAL = "normal"
    MILD_CONCERN = "mild_concern"
    MODERATE_CONCERN = "moderate_concern"
    HIGH_CONCERN = "high_concern"
    CRITICAL = "critical"


class DataFusionReport(Base):
    """
    PATENT-PENDING: Multi-Modal Data Fusion Report
    
    This model represents our innovative data fusion methodology that combines:
    1. Cognitive assessment data (MMSE, MoCA, Memory, Attention, Executive)
    2. Biomarker data (Amyloid-beta, Tau, Dopamine, APOE ε4)
    3. Neuroimaging data (MRI volumetric measurements)
    
    The fusion algorithm weighs and correlates these modalities to provide:
    - Integrated risk assessment
    - Cross-modal validation
    - Conflicting data resolution
    - Confidence-weighted interpretation
    - Natural language clinical report
    
    This represents a novel approach to clinical decision support.
    """
    __tablename__ = "data_fusion_reports"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.id"), nullable=True, index=True)
    
    # Report Metadata
    report_version = Column(String(20), default="1.0.0")
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # ============================================================================
    # PATENT-PENDING: Multi-Modal Fusion Scores
    # ============================================================================
    
    # Individual Modality Scores (0-100)
    cognitive_modality_score = Column(Float, nullable=False)
    biomarker_modality_score = Column(Float, nullable=False)
    imaging_modality_score = Column(Float, nullable=False)
    
    # Modality Confidence Weights (0-1) - how reliable each modality is
    cognitive_confidence = Column(Float, nullable=False)
    biomarker_confidence = Column(Float, nullable=False)
    imaging_confidence = Column(Float, nullable=False)
    
    # PATENT-PENDING: Fused Integrated Score (weighted combination)
    integrated_fusion_score = Column(Float, nullable=False, index=True)
    fusion_confidence = Column(SQLEnum(FusionConfidence), nullable=False, index=True)
    
    # ============================================================================
    # PATENT-PENDING: Cross-Modal Correlation Analysis
    # ============================================================================
    
    # Correlation between modalities (-1 to +1)
    cognitive_biomarker_correlation = Column(Float, nullable=False)
    cognitive_imaging_correlation = Column(Float, nullable=False)
    biomarker_imaging_correlation = Column(Float, nullable=False)
    
    # Overall cross-modal consistency (0-100)
    cross_modal_consistency_score = Column(Float, nullable=False)
    
    # Conflicting findings flag
    has_conflicting_findings = Column(Integer, default=0)  # Boolean as int
    
    # ============================================================================
    # PATENT-PENDING: Disease-Specific Fusion Metrics
    # ============================================================================
    
    # Alzheimer's Disease Fusion Score (0-100)
    alzheimer_fusion_score = Column(Float, nullable=False)
    alzheimer_confidence = Column(Float, nullable=False)
    
    # Key AD indicators from fusion
    ad_amyloid_tau_concordance = Column(Float, nullable=False)  # Biomarker agreement
    ad_cognitive_biomarker_alignment = Column(Float, nullable=False)  # Cognitive-biomarker match
    ad_hippocampal_correlation = Column(Float, nullable=False)  # Imaging-clinical match
    
    # Parkinson's Disease Fusion Score (0-100)
    parkinson_fusion_score = Column(Float, nullable=False)
    parkinson_confidence = Column(Float, nullable=False)
    
    # Key PD indicators from fusion
    pd_dopamine_cognitive_concordance = Column(Float, nullable=False)
    pd_motor_cognitive_alignment = Column(Float, nullable=False)
    pd_imaging_biomarker_correlation = Column(Float, nullable=False)
    
    # ============================================================================
    # PATENT-PENDING: Fusion-Based Interpretation
    # ============================================================================
    
    overall_interpretation = Column(SQLEnum(FusionInterpretation), nullable=False, index=True)
    primary_concern = Column(String(100), nullable=True)  # e.g., "Alzheimer's Disease", "Normal Aging"
    
    # Confidence in interpretation (0-100)
    interpretation_confidence = Column(Float, nullable=False)
    
    # Supporting evidence from each modality
    cognitive_evidence = Column(Text, nullable=True)
    biomarker_evidence = Column(Text, nullable=True)
    imaging_evidence = Column(Text, nullable=True)
    
    # ============================================================================
    # PATENT-PENDING: Natural Language Report Generation
    # ============================================================================
    
    # Executive Summary
    executive_summary = Column(Text, nullable=False)
    
    # Detailed Findings
    detailed_findings = Column(Text, nullable=False)
    
    # Risk Assessment
    risk_assessment = Column(Text, nullable=False)
    
    # Clinical Recommendations
    recommendations = Column(Text, nullable=False)
    
    # Follow-up Suggestions
    follow_up_plan = Column(Text, nullable=True)
    
    # ============================================================================
    # PATENT-PENDING: Advanced Analytics
    # ============================================================================
    
    # Temporal progression indicators (if multiple records available)
    progression_rate = Column(Float, nullable=True)  # Change per year
    trajectory_prediction = Column(String(50), nullable=True)  # "stable", "declining", "improving"
    
    # Outlier detection
    has_outlier_findings = Column(Integer, default=0)
    outlier_description = Column(Text, nullable=True)
    
    # Data quality assessment
    data_completeness_score = Column(Float, nullable=False)  # 0-100
    data_quality_notes = Column(Text, nullable=True)
    
    # ============================================================================
    # PATENT CLAIM 3: XAI Dynamic Evidence
    # ============================================================================
    
    # XAI explanations and dynamic evidence (JSON)
    xai_evidence = Column(JSON, nullable=True)  # Stores dynamic evidence from XAI service
    xai_method = Column(String(50), nullable=True)  # Method used: 'integrated_gradients' or 'gradient_saliency'
    has_xai_explanation = Column(Integer, default=0)  # Boolean: whether XAI explanation is available
    
    # ============================================================================
    # Additional Metadata
    # ============================================================================
    
    # JSON field for extensibility and future features
    fusion_metadata = Column(JSON, nullable=True)
    
    # Algorithm version for tracking improvements
    algorithm_version = Column(String(20), default="1.0.0")
    
    # Processing time (for performance monitoring)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # ============================================================================
    # Relationships
    # ============================================================================
    
    patient = relationship("Patient", back_populates="fusion_reports")
    medical_record = relationship("MedicalRecord")
    
    def __repr__(self):
        return (
            f"<DataFusionReport(id={self.id}, patient_id={self.patient_id}, "
            f"interpretation={self.overall_interpretation}, "
            f"fusion_score={self.integrated_fusion_score:.2f})>"
        )
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "medical_record_id": self.medical_record_id,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            
            # Fusion Scores
            "fusion_scores": {
                "cognitive": self.cognitive_modality_score,
                "biomarker": self.biomarker_modality_score,
                "imaging": self.imaging_modality_score,
                "integrated": self.integrated_fusion_score,
                "confidence": self.fusion_confidence.value if self.fusion_confidence else None,
            },
            
            # Cross-Modal Analysis
            "cross_modal": {
                "consistency_score": self.cross_modal_consistency_score,
                "correlations": {
                    "cognitive_biomarker": self.cognitive_biomarker_correlation,
                    "cognitive_imaging": self.cognitive_imaging_correlation,
                    "biomarker_imaging": self.biomarker_imaging_correlation,
                },
                "has_conflicts": bool(self.has_conflicting_findings),
            },
            
            # Disease-Specific
            "disease_analysis": {
                "alzheimer": {
                    "score": self.alzheimer_fusion_score,
                    "confidence": self.alzheimer_confidence,
                    "indicators": {
                        "amyloid_tau_concordance": self.ad_amyloid_tau_concordance,
                        "cognitive_biomarker_alignment": self.ad_cognitive_biomarker_alignment,
                        "hippocampal_correlation": self.ad_hippocampal_correlation,
                    }
                },
                "parkinson": {
                    "score": self.parkinson_fusion_score,
                    "confidence": self.parkinson_confidence,
                    "indicators": {
                        "dopamine_cognitive_concordance": self.pd_dopamine_cognitive_concordance,
                        "motor_cognitive_alignment": self.pd_motor_cognitive_alignment,
                        "imaging_biomarker_correlation": self.pd_imaging_biomarker_correlation,
                    }
                }
            },
            
            # Interpretation
            "interpretation": {
                "overall": self.overall_interpretation.value if self.overall_interpretation else None,
                "primary_concern": self.primary_concern,
                "confidence": self.interpretation_confidence,
                "evidence": {
                    "cognitive": self.cognitive_evidence,
                    "biomarker": self.biomarker_evidence,
                    "imaging": self.imaging_evidence,
                }
            },
            
            # Report Sections
            "report": {
                "executive_summary": self.executive_summary,
                "detailed_findings": self.detailed_findings,
                "risk_assessment": self.risk_assessment,
                "recommendations": self.recommendations,
                "follow_up_plan": self.follow_up_plan,
            },
            
            # Quality Metrics
            "quality": {
                "data_completeness": self.data_completeness_score,
                "has_outliers": bool(self.has_outlier_findings),
                "quality_notes": self.data_quality_notes,
            },
            
            # Metadata
            "metadata": {
                "report_version": self.report_version,
                "algorithm_version": self.algorithm_version,
                "processing_time_ms": self.processing_time_ms,
            }
        }

