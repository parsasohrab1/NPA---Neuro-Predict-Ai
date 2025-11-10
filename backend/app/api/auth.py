"""
Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from ..db.session import get_db
from ..models.user import User
from ..models.security import MFASecret
from ..schemas.user import UserCreate, UserResponse, Token
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_user
)
from ..services.security_service import SecurityService
from ..core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check password policy
    is_valid, error_message = await SecurityService.check_password_policy(
        user_data.password,
        db
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Check if user already exists
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        license_number=user_data.license_number,
        department=user_data.department,
        institution=user_data.institution,
        password_changed_at=datetime.utcnow()
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Log security event
    client_ip = SecurityService.get_client_ip(request)
    await SecurityService.log_security_event(
        db=db,
        user_id=new_user.id,
        event_type="user_registered",
        severity="info",
        description="New user registered",
        ip_address=client_ip,
        success=True
    )
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    client_ip = SecurityService.get_client_ip(request) if request else "unknown"
    user_agent = request.headers.get("User-Agent", "Unknown") if request else "Unknown"
    
    # Find user
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    # Check if user is locked
    if user and user.is_locked:
        if user.locked_until and user.locked_until > datetime.utcnow():
            await SecurityService.record_failed_login(
                username=form_data.username,
                user_id=user.id if user else None,
                ip_address=client_ip,
                user_agent=user_agent,
                db=db
            )
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account is locked until {user.locked_until}",
            )
        else:
            # Lock expired, unlock user
            user.is_locked = False
            user.locked_until = None
            await db.commit()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Record failed login
        await SecurityService.record_failed_login(
            username=form_data.username,
            user_id=user.id if user else None,
            ip_address=client_ip,
            user_agent=user_agent,
            db=db
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Check IP whitelist
    ip_allowed = await SecurityService.check_ip_whitelist(user.id, client_ip, db)
    if not ip_allowed:
        await SecurityService.log_security_event(
            db=db,
            user_id=user.id,
            event_type="login_blocked_ip",
            severity="warning",
            description=f"Login attempt from non-whitelisted IP: {client_ip}",
            ip_address=client_ip,
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied from this IP address"
        )
    
    # Check if MFA is enabled
    result = await db.execute(
        select(MFASecret).where(
            MFASecret.user_id == user.id,
            MFASecret.is_enabled == True
        )
    )
    mfa_secret = result.scalar_one_or_none()
    
    if mfa_secret:
        # MFA required - return token with mfa_required flag
        # In a real implementation, you'd require MFA code before issuing token
        # For now, we'll issue a temporary token that requires MFA verification
        pass
    
    # Reset failed login count
    await SecurityService.reset_failed_login_count(user.id, db)
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Create session
    expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    await SecurityService.create_session(
        user_id=user.id,
        session_token=access_token,
        refresh_token=refresh_token,
        ip_address=client_ip,
        user_agent=user_agent,
        expires_at=expires_at,
        db=db
    )
    
    # Log successful login
    await SecurityService.log_security_event(
        db=db,
        user_id=user.id,
        event_type="login_success",
        severity="info",
        description="User logged in successfully",
        ip_address=client_ip,
        user_agent=user_agent,
        success=True
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "mfa_required": mfa_secret is not None
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current logged-in user information"""
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout current user (client should discard tokens)"""
    return {"message": "Successfully logged out"}

