"""
Security-related Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..db.session import Base


class MFAMethod(str, enum.Enum):
    TOTP = "totp"  # Time-based One-Time Password
    SMS = "sms"
    EMAIL = "email"


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Session Information
    session_token = Column(String, unique=True, index=True, nullable=False)
    refresh_token = Column(String, unique=True, index=True, nullable=True)
    
    # Security Information
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"


class MFASecret(Base):
    __tablename__ = "mfa_secrets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # MFA Configuration
    method = Column(String, default=MFAMethod.TOTP.value, nullable=False)
    secret_key = Column(String, nullable=False)  # Encrypted TOTP secret
    backup_codes = Column(JSON, nullable=True)  # Encrypted backup codes
    
    # Status
    is_enabled = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Phone/Email for SMS/Email MFA
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="mfa_secret")
    
    def __repr__(self):
        return f"<MFASecret(id={self.id}, user_id={self.user_id}, method={self.method}, is_enabled={self.is_enabled})>"


class IPWhitelist(Base):
    __tablename__ = "ip_whitelist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # IP Information
    ip_address = Column(String, nullable=False, index=True)
    ip_range = Column(String, nullable=True)  # CIDR notation
    description = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="ip_whitelist")
    
    def __repr__(self):
        return f"<IPWhitelist(id={self.id}, ip_address={self.ip_address}, user_id={self.user_id})>"


class PasswordPolicy(Base):
    __tablename__ = "password_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Policy Name
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Password Requirements
    min_length = Column(Integer, default=8)
    max_length = Column(Integer, default=128)
    require_uppercase = Column(Boolean, default=True)
    require_lowercase = Column(Boolean, default=True)
    require_digits = Column(Boolean, default=True)
    require_special_chars = Column(Boolean, default=True)
    special_chars = Column(String, default="!@#$%^&*()_+-=[]{}|;:,.<>?")
    
    # Password History
    prevent_reuse_count = Column(Integer, default=5)  # Prevent reusing last N passwords
    
    # Expiration
    expiration_days = Column(Integer, nullable=True)  # None = no expiration
    warning_days = Column(Integer, default=7)  # Warn user N days before expiration
    
    # Lockout Policy
    max_failed_attempts = Column(Integer, default=5)
    lockout_duration_minutes = Column(Integer, default=30)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PasswordPolicy(id={self.id}, name={self.name}, is_active={self.is_active})>"


class PasswordHistory(Base):
    __tablename__ = "password_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Password Hash
    password_hash = Column(String, nullable=False)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="password_history")
    
    def __repr__(self):
        return f"<PasswordHistory(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"


class SecurityLog(Base):
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Event Information
    event_type = Column(String, nullable=False, index=True)  # login_attempt, password_change, mfa_enabled, etc.
    severity = Column(String, default="info", index=True)  # info, warning, error, critical
    description = Column(Text, nullable=True)
    
    # Request Details
    ip_address = Column(String, nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    request_path = Column(String, nullable=True)
    
    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Additional Context
    metadata = Column(JSON, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="security_logs")
    
    def __repr__(self):
        return f"<SecurityLog(id={self.id}, event_type={self.event_type}, severity={self.severity}, timestamp={self.timestamp})>"


class FailedLoginAttempt(Base):
    __tablename__ = "failed_login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Attempt Information
    username = Column(String, nullable=True, index=True)
    ip_address = Column(String, nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamp
    attempted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="failed_login_attempts")
    
    def __repr__(self):
        return f"<FailedLoginAttempt(id={self.id}, username={self.username}, ip_address={self.ip_address})>"

