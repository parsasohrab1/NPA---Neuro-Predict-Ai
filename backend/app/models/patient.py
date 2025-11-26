"""
Patient Model
"""
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..db.session import Base


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True, nullable=False)  # Hospital/External ID
    
    # Demographic Information
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False, index=True)
    
    # Contact Information
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    
    # Medical Information
    education_years = Column(Integer, nullable=True)
    medical_history = Column(Text, nullable=True)
    family_history = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)
    
    # Assigned Doctor
    assigned_doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assigned_doctor = relationship("User", back_populates="patients")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="patient", cascade="all, delete-orphan")
    longitudinal_episodes = relationship(
        "LongitudinalEpisode",
        back_populates="patient",
        cascade="all, delete-orphan",
        order_by="LongitudinalEpisode.start_date",
    )
    fusion_reports = relationship("DataFusionReport", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, patient_id={self.patient_id}, name={self.first_name} {self.last_name})>"

