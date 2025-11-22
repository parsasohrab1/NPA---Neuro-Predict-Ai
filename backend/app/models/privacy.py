"""
Privacy & DSR models
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.sql import func
import enum

from ..db.session import Base


class DSRType(str, enum.Enum):
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    RESTRICTION = "restriction"
    PORTABILITY = "portability"


class DSRStatus(str, enum.Enum):
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class DSRRequest(Base):
    __tablename__ = "dsr_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    request_type = Column(Enum(DSRType), nullable=False)
    subject_identifier = Column(String(256), nullable=False, index=True)  # e.g., patient_id/email
    reason = Column(Text, nullable=True)
    status = Column(Enum(DSRStatus), default=DSRStatus.RECEIVED, nullable=False, index=True)
    result_location = Column(String, nullable=True)  # path to export or note
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


