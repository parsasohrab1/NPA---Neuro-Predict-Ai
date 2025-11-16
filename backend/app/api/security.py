"""
Security API Endpoints - MFA, Password Management, IP Whitelist, Sessions
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from ..db.session import get_db
from ..models.user import User
from ..models.security import (
    MFASecret, MFAMethod, UserSession, IPWhitelist,
    PasswordPolicy, SecurityLog
)
from ..core.security import get_current_user, get_password_hash, verify_password
from ..services.security_service import SecurityService
from ..core.config import settings

router = APIRouter(prefix="/security", tags=["Security"])


# Schemas
class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]
    provisioning_uri: str


class MFAVerifyRequest(BaseModel):
    code: str


class MFAEnableRequest(BaseModel):
    verification_code: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class IPWhitelistCreate(BaseModel):
    ip_address: str
    ip_range: Optional[str] = None
    description: Optional[str] = None
    expires_at: Optional[datetime] = None


class IPWhitelistResponse(BaseModel):
    id: int
    ip_address: str
    ip_range: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class SecurityLogResponse(BaseModel):
    id: int
    event_type: str
    severity: str
    description: Optional[str]
    ip_address: Optional[str]
    success: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True


# MFA Endpoints
@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Setup MFA for current user"""
    result = await SecurityService.generate_mfa_secret(
        user_id=current_user.id,
        method=MFAMethod.TOTP,
        db=db
    )
    return result


@router.post("/mfa/verify")
async def verify_mfa(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify MFA code"""
    is_valid = await SecurityService.verify_mfa_code(
        user_id=current_user.id,
        code=request.code,
        db=db
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code"
        )
    
    return {"verified": True}


@router.post("/mfa/enable")
async def enable_mfa(
    request: MFAEnableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enable MFA after verification"""
    await SecurityService.enable_mfa(
        user_id=current_user.id,
        verification_code=request.verification_code,
        db=db
    )
    return {"message": "MFA enabled successfully"}


@router.post("/mfa/disable")
async def disable_mfa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disable MFA for current user"""
    result = await db.execute(
        select(MFASecret).where(MFASecret.user_id == current_user.id)
    )
    mfa_secret = result.scalar_one_or_none()
    
    if mfa_secret:
        mfa_secret.is_enabled = False
        await db.commit()
        
        await SecurityService.log_security_event(
            db=db,
            user_id=current_user.id,
            event_type="mfa_disabled",
            severity="warning",
            description="MFA disabled by user"
        )
    
    return {"message": "MFA disabled successfully"}


@router.get("/mfa/status")
async def get_mfa_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get MFA status for current user"""
    result = await db.execute(
        select(MFASecret).where(MFASecret.user_id == current_user.id)
    )
    mfa_secret = result.scalar_one_or_none()
    
    if not mfa_secret:
        return {"enabled": False, "method": None}
    
    return {
        "enabled": mfa_secret.is_enabled,
        "method": mfa_secret.method,
        "is_verified": mfa_secret.is_verified
    }


# Password Management
@router.post("/password/change")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    http_request: Request = None
):
    """Change user password"""
    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        await SecurityService.log_security_event(
            db=db,
            user_id=current_user.id,
            event_type="password_change_failed",
            severity="warning",
            description="Failed password change - incorrect current password",
            ip_address=SecurityService.get_client_ip(http_request) if http_request else None,
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Check password policy
    is_valid, error_message = await SecurityService.check_password_policy(
        request.new_password,
        db
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Check password history
    is_allowed, error_message = await SecurityService.check_password_history(
        current_user.id,
        request.new_password,
        db
    )
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Save old password to history
    await SecurityService.save_password_to_history(
        current_user.id,
        current_user.hashed_password,
        db
    )
    
    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    current_user.password_changed_at = datetime.utcnow()
    await db.commit()
    
    # Log security event
    await SecurityService.log_security_event(
        db=db,
        user_id=current_user.id,
        event_type="password_changed",
        severity="info",
        description="Password changed successfully",
        ip_address=SecurityService.get_client_ip(http_request) if http_request else None,
        success=True
    )
    
    return {"message": "Password changed successfully"}


# IP Whitelist Management
@router.post("/ip-whitelist", response_model=IPWhitelistResponse)
async def create_ip_whitelist(
    ip_data: IPWhitelistCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add IP to whitelist for current user"""
    ip_whitelist = IPWhitelist(
        user_id=current_user.id,
        ip_address=ip_data.ip_address,
        ip_range=ip_data.ip_range,
        description=ip_data.description,
        expires_at=ip_data.expires_at,
        is_active=True
    )
    db.add(ip_whitelist)
    await db.commit()
    await db.refresh(ip_whitelist)
    
    return ip_whitelist


@router.get("/ip-whitelist", response_model=List[IPWhitelistResponse])
async def get_ip_whitelist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get IP whitelist for current user"""
    result = await db.execute(
        select(IPWhitelist).where(IPWhitelist.user_id == current_user.id)
    )
    whitelist = result.scalars().all()
    return whitelist


@router.delete("/ip-whitelist/{whitelist_id}")
async def delete_ip_whitelist(
    whitelist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove IP from whitelist"""
    result = await db.execute(
        select(IPWhitelist).where(
            and_(
                IPWhitelist.id == whitelist_id,
                IPWhitelist.user_id == current_user.id
            )
        )
    )
    ip_whitelist = result.scalar_one_or_none()
    
    if not ip_whitelist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP whitelist entry not found"
        )
    
    await db.delete(ip_whitelist)
    await db.commit()
    
    return {"message": "IP whitelist entry removed"}


# Session Management
@router.get("/sessions", response_model=List[SessionResponse])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all active sessions for current user"""
    result = await db.execute(
        select(UserSession).where(
            and_(
                UserSession.user_id == current_user.id,
                UserSession.is_active == True
            )
        )
    )
    sessions = result.scalars().all()
    return sessions


@router.post("/sessions/{session_id}/revoke")
async def revoke_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke a specific session"""
    result = await db.execute(
        select(UserSession).where(
            and_(
                UserSession.id == session_id,
                UserSession.user_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    await SecurityService.revoke_session(session.session_token, db)
    
    return {"message": "Session revoked successfully"}


@router.post("/sessions/revoke-all")
async def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke all sessions for current user"""
    await SecurityService.revoke_all_user_sessions(current_user.id, db)
    
    return {"message": "All sessions revoked successfully"}


class CSPReport(BaseModel):
    """Minimal CSP report body as per browser report format"""
    csp_report: dict


@router.post("/csp/report")
async def csp_report(
    report: CSPReport,
    request: Request,
):
    """
    Receive CSP violation reports (Report-Only). Store/log for observability.
    For MVP, log to security log; can be extended to persist in DB.
    """
    try:
        details = report.csp_report
    except Exception:
        details = {}
    await SecurityService.log_security_event(
        db=None,
        user_id=None,
        event_type="csp_violation",
        severity="warning",
        description=str(details)[:1000],
        ip_address=SecurityService.get_client_ip(request),
        request_path=request.url.path,
    )
    return {"received": True}


# Security Logs
@router.get("/logs", response_model=List[SecurityLogResponse])
async def get_security_logs(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get security logs for current user (admin can see all)"""
    if current_user.role.value != "admin":
        # Regular users can only see their own logs
        result = await db.execute(
            select(SecurityLog)
            .where(SecurityLog.user_id == current_user.id)
            .order_by(SecurityLog.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
    else:
        # Admins can see all logs
        result = await db.execute(
            select(SecurityLog)
            .order_by(SecurityLog.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
    
    logs = result.scalars().all()
    return logs

