"""
Audit Log Model for Compliance (HIPAA, GDPR)
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Action Information
    action = Column(String, nullable=False)  # login, view_patient, create_prediction, etc.
    resource_type = Column(String, nullable=True)  # patient, prediction, user, etc.
    resource_id = Column(String, nullable=True)
    
    # Request Details
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    request_method = Column(String, nullable=True)  # GET, POST, PUT, DELETE
    request_path = Column(String, nullable=True)
    
    # Status
    status_code = Column(Integer, nullable=True)
    success = Column(String, default=True)
    error_message = Column(Text, nullable=True)
    
    # Additional Context
    details = Column(JSON, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id}, timestamp={self.timestamp})>"

