"""
Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..db.session import get_db
from ..models.user import User
from ..models.security import MFASecret
from ..schemas.user import UserCreate, UserResponse, Token
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_user,
    decode_token
)
from ..services.security_service import SecurityService
from ..core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


class MFAVerifyRequest(BaseModel):
    mfa_code: str
    pre_auth_token: str


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
        # MFA required - issue temporary pre-auth token and require MFA verification
        # Store user_id temporarily in Redis for MFA verification (expires in 5 minutes)
        from ..core.security import create_access_token
        from ..core.config import settings
        pre_auth_token = create_access_token(
            data={
                "sub": str(user.id),
                "type": "mfa_preauth",
                "mfa_required": True
            },
            expires_delta=timedelta(minutes=5)
        )
        
        # Store in Redis for MFA verification
        import redis.asyncio as redis
        try:
            redis_client = redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                decode_responses=True
            )
            await redis_client.setex(
                f"mfa_preauth:{user.id}",
                300,  # 5 minutes
                pre_auth_token
            )
            await redis_client.close()
        except Exception:
            pass  # If Redis fails, continue - MFA will still work via DB
        
        return {
            "access_token": pre_auth_token,
            "refresh_token": None,
            "token_type": "bearer",
            "mfa_required": True,
            "message": "MFA code required. Please call /api/v1/auth/login/mfa with the MFA code."
        }
    
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
        "mfa_required": False
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current logged-in user information"""
    return current_user


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=Token)
async def refresh_token(
    payload: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Issue a new access token using a valid refresh token"""
    # Check blacklist
    if await SecurityService.is_token_blacklisted(payload.refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    # Validate refresh token
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token type")
    except HTTPException:
        raise

    user_id = int(data.get("sub"))

    # Ensure user exists and active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    # Issue new tokens (MVP: keep refresh, rotate access)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = payload.refresh_token

    # Record session (optional new session per refresh)
    expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    client_ip = SecurityService.get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "Unknown")
    await SecurityService.create_session(
        user_id=user.id,
        session_token=access_token,
        refresh_token=refresh_token,
        ip_address=client_ip,
        user_agent=user_agent,
        expires_at=expires_at,
        db=db
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


class LogoutRequest(BaseModel):
    refresh_token: str


@router.post("/login/mfa", response_model=Token)
async def verify_mfa_login(
    request_data: MFAVerifyRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Verify MFA code and complete login"""
    # Verify pre-auth token
    try:
        payload = decode_token(request_data.pre_auth_token)
        if payload.get("type") != "mfa_preauth":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid pre-auth token"
            )
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired pre-auth token"
        )
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Verify MFA code
    mfa_valid = await SecurityService.verify_mfa_code(
        user_id=user.id,
        code=request_data.mfa_code,
        db=db
    )
    
    if not mfa_valid:
        await SecurityService.log_security_event(
            db=db,
            user_id=user.id,
            event_type="mfa_verification_failed",
            severity="warning",
            description="Invalid MFA code provided",
            ip_address=SecurityService.get_client_ip(http_request),
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code"
        )
    
    # MFA verified - issue full tokens
    client_ip = SecurityService.get_client_ip(http_request)
    user_agent = http_request.headers.get("User-Agent", "Unknown")
    
    # Reset failed login count
    await SecurityService.reset_failed_login_count(user.id, db)
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create full tokens
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
    
    # Log successful MFA login
    await SecurityService.log_security_event(
        db=db,
        user_id=user.id,
        event_type="login_success_mfa",
        severity="info",
        description="User logged in successfully with MFA",
        ip_address=client_ip,
        user_agent=user_agent,
        success=True
    )
    
    # Invalidate pre-auth token in Redis
    import redis.asyncio as redis
    try:
        redis_client = redis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            decode_responses=True
        )
        await redis_client.delete(f"mfa_preauth:{user.id}")
        await redis_client.close()
    except Exception:
        pass
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout current user:
    - Blacklist provided refresh token
    - Revoke all active sessions for the user
    """
    # Blacklist the refresh token
    try:
        data = decode_token(body.refresh_token)
        exp = int(data.get("exp"))
    except Exception:
        exp = None  # type: ignore
    await SecurityService.blacklist_token(body.refresh_token, exp)

    # Revoke all sessions
    await SecurityService.revoke_all_user_sessions(current_user.id, db)

    return {"message": "Logged out"}

