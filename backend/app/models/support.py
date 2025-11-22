"""
Support Ticketing Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..db.session import Base


class TicketSeverity(str, enum.Enum):
    SEV1 = "sev-1"
    SEV2 = "sev-2"
    SEV3 = "sev-3"
    SEV4 = "sev-4"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    request_id = Column(String(64), nullable=True, index=True)
    reporter_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    severity = Column(Enum(TicketSeverity), nullable=False, default=TicketSeverity.SEV3)
    domain = Column(String(32), nullable=True)  # fe/be/infra/integration
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN, index=True)
    owner = Column(String(120), nullable=True)  # team/assignee
    meta_data = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)  # for MTTA
    resolved_at = Column(DateTime(timezone=True), nullable=True)      # for MTTR
    closed_at = Column(DateTime(timezone=True), nullable=True)

    updates = relationship("SupportUpdate", back_populates="ticket", cascade="all, delete-orphan")


class SupportUpdate(Base):
    __tablename__ = "support_updates"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    author_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    ticket = relationship("SupportTicket", back_populates="updates")


