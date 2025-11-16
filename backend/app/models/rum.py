"""
RUM (Real User Monitoring) and User Feedback models
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from ..db.session import Base


class RUMEvent(Base):
    __tablename__ = "rum_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(64), index=True)  # lcp, cls, inp, fcp, ttfb, js_error, api_error
    value = Column(String(64), nullable=True)    # store as string to avoid precision issues
    metadata = Column(JSON, nullable=True)       # page, path, user_role, user_agent (sanitized), trace_id, etc.
    sampled = Column(String(8), default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key, index=True)
    rating = Column(Integer, nullable=True)        # 1..5 for CSAT/NPS-like score
    comment = Column(Text, nullable=True)          # short comment, no PII
    context = Column(JSON, nullable=True)          # page, feature, trace_id, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


