"""
Longitudinal Tracking Models
"""
from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.session import Base


class LongitudinalEpisodeStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class LongitudinalVisitType(str, enum.Enum):
    BASELINE = "baseline"
    FOLLOWUP = "followup"
    THERAPY = "therapy"
    IMAGING = "imaging"
    LAB = "lab"


class MetricCategory(str, enum.Enum):
    COGNITIVE = "cognitive"
    BIOMARKER = "biomarker"
    IMAGING = "imaging"
    FUNCTIONAL = "functional"


class LongitudinalEpisode(Base):
    __tablename__ = "longitudinal_episodes"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(LongitudinalEpisodeStatus), default=LongitudinalEpisodeStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("Patient", back_populates="longitudinal_episodes")
    visits = relationship(
        "LongitudinalVisit",
        back_populates="episode",
        cascade="all, delete-orphan",
        order_by="LongitudinalVisit.visit_date",
    )

    def __repr__(self) -> str:
        return f"<LongitudinalEpisode(id={self.id}, patient_id={self.patient_id}, status={self.status})>"


class LongitudinalVisit(Base):
    __tablename__ = "longitudinal_visits"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("longitudinal_episodes.id"), nullable=False, index=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.id"), nullable=True, index=True)
    imaging_study_id = Column(Integer, ForeignKey("imaging_studies.id"), nullable=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True, index=True)
    visit_date = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    visit_type = Column(Enum(LongitudinalVisitType), default=LongitudinalVisitType.FOLLOWUP, nullable=False)
    notes = Column(Text, nullable=True)
    progression_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    episode = relationship("LongitudinalEpisode", back_populates="visits")
    metrics = relationship(
        "LongitudinalMetric",
        back_populates="visit",
        cascade="all, delete-orphan",
        order_by="LongitudinalMetric.metric_key",
    )
    medical_record = relationship("MedicalRecord", back_populates="longitudinal_visits")
    imaging_study = relationship("ImagingStudy", back_populates="longitudinal_visits")
    prediction = relationship("Prediction", back_populates="longitudinal_visit")

    def __repr__(self) -> str:
        return f"<LongitudinalVisit(id={self.id}, episode_id={self.episode_id}, visit_date={self.visit_date})>"


class LongitudinalMetric(Base):
    __tablename__ = "longitudinal_metrics"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("longitudinal_visits.id"), nullable=False, index=True)
    metric_type = Column(Enum(MetricCategory), nullable=False)
    metric_key = Column(String(128), nullable=False)
    metric_value = Column(Float, nullable=True)
    metric_payload = Column(JSON, nullable=True)
    unit = Column(String(64), nullable=True)
    z_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    visit = relationship("LongitudinalVisit", back_populates="metrics")

    def __repr__(self) -> str:
        return f"<LongitudinalMetric(id={self.id}, visit_id={self.visit_id}, key={self.metric_key})>"


