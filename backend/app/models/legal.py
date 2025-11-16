"""
Legal models: Terms of Use acceptance
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from ..db.session import Base


class UserTermsAcceptance(Base):
    __tablename__ = "user_terms_acceptance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    version = Column(String(32), nullable=False, index=True)  # e.g., "fa-1.0-2024-11-20"
    accepted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


