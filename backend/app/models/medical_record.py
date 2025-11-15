"""
Medical Record Model
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.session import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    
    # Visit Information
    visit_date = Column(DateTime(timezone=True), nullable=False, index=True)
    visit_type = Column(String, nullable=True, index=True)  # Initial, Follow-up, etc.
    
    # Cognitive Scores
    mmse_score = Column(Float, nullable=True)  # Mini-Mental State Examination (0-30)
    moca_score = Column(Float, nullable=True)  # Montreal Cognitive Assessment (0-30)
    memory_score = Column(Float, nullable=True)
    attention_score = Column(Float, nullable=True)
    executive_function_score = Column(Float, nullable=True)
    
    # Biomarkers
    amyloid_beta = Column(Float, nullable=True)  # pg/mL
    tau_protein = Column(Float, nullable=True)  # pg/mL
    dopamine_level = Column(Float, nullable=True)  # ng/mL
    
    # Genetic Data
    apoe_e4_status = Column(Boolean, nullable=True)  # APOE ε4 allele presence
    genetic_markers = Column(JSON, nullable=True)  # Additional genetic markers
    
    # MRI Features
    hippocampal_volume = Column(Float, nullable=True)  # mm³
    cortical_thickness = Column(Float, nullable=True)  # mm
    ventricular_volume = Column(Float, nullable=True)  # mm³
    white_matter_hyperintensities = Column(Float, nullable=True)
    brain_volume_total = Column(Float, nullable=True)  # mm³
    
    # Clinical Notes
    symptoms = Column(Text, nullable=True)
    clinical_notes = Column(Text, nullable=True)
    
    # Additional Data
    additional_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    imaging_studies = relationship("ImagingStudy", back_populates="medical_record", cascade="all, delete-orphan")
    longitudinal_visits = relationship("LongitudinalVisit", back_populates="medical_record")
    
    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, patient_id={self.patient_id}, visit_date={self.visit_date})>"

