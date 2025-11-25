"""
AI Prediction Model
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..db.session import Base


class DiseaseType(str, enum.Enum):
    ALZHEIMER = "alzheimer"
    PARKINSON = "parkinson"
    BOTH = "both"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Prediction Information
    disease_type = Column(Enum(DiseaseType), nullable=False)
    
    # Alzheimer's Prediction
    alzheimer_risk_score = Column(Float, nullable=True)  # 0-1 probability
    alzheimer_risk_level = Column(Enum(RiskLevel), nullable=True)
    alzheimer_confidence = Column(Float, nullable=True)  # 0-1 confidence interval
    
    # Parkinson's Prediction
    parkinson_risk_score = Column(Float, nullable=True)  # 0-1 probability
    parkinson_risk_level = Column(Enum(RiskLevel), nullable=True)
    parkinson_confidence = Column(Float, nullable=True)  # 0-1 confidence interval
    
    # Model Information
    model_version = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    
    # Input Features Used (stored as JSON)
    input_features = Column(JSON, nullable=True)
    
    # Feature Importance (for explainability)
    feature_importance = Column(JSON, nullable=True)
    # Attention/explainability scores per modality
    attention_scores = Column(JSON, nullable=True)
    
    # Clinical Recommendations
    recommendations = Column(Text, nullable=True)
    follow_up_date = Column(DateTime(timezone=True), nullable=True)
    
    # Report
    report_path = Column(String, nullable=True)  # Path to generated PDF report
    
    # Validation & Review
    is_reviewed = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="predictions")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="predictions")
    longitudinal_visit = relationship("LongitudinalVisit", back_populates="prediction", uselist=False)
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, patient_id={self.patient_id}, disease_type={self.disease_type})>"

