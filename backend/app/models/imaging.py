"""
Medical Imaging Models
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..db.session import Base


class ImagingModality(str, enum.Enum):
    MRI = "MRI"
    PET = "PET"
    FMRI = "fMRI"
    CT = "CT"
    SPECT = "SPECT"


class ImagingStudy(Base):
    __tablename__ = "imaging_studies"
    
    id = Column(Integer, primary_key=True, index=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.id"), nullable=False)
    
    # Study Information
    study_id = Column(String, unique=True, index=True, nullable=False)  # DICOM Study Instance UID
    study_date = Column(DateTime(timezone=True), nullable=False)
    modality = Column(Enum(ImagingModality), nullable=False)
    
    # File Information
    dicom_path = Column(String, nullable=True)  # Path to DICOM files
    processed_path = Column(String, nullable=True)  # Path to processed images
    thumbnail_path = Column(String, nullable=True)
    
    # Study Metadata
    series_count = Column(Integer, default=0)
    image_count = Column(Integer, default=0)
    study_description = Column(String, nullable=True)
    protocol_name = Column(String, nullable=True)
    
    # Quality Metrics
    quality_score = Column(Float, nullable=True)  # 0-1 score
    is_valid = Column(String, default=True)
    quality_notes = Column(Text, nullable=True)
    
    # Extracted Features (stored as JSON)
    extracted_features = Column(JSON, nullable=True)
    
    # Processing Status
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    medical_record = relationship("MedicalRecord", back_populates="imaging_studies")
    
    def __repr__(self):
        return f"<ImagingStudy(id={self.id}, study_id={self.study_id}, modality={self.modality})>"

