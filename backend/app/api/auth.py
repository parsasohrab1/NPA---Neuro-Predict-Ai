"""
Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional

from ..db.session import get_db
from ..models.user import User
from ..models.security import MFASecret
from ..schemas.user import UserCreate, UserResponse, Token, MFALoginRequest
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_user,
    decode_token,
)
from ..core.config import settings
from ..services.security_service import SecurityService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Optional bearer for logout (blacklist when present)
_optional_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False,
)


def _create_mfa_pending_token(user_id: int) -> str:
    """Short-lived JWT proving password auth succeeded; does not grant API access."""
    return create_access_token(
        data={"sub": str(user_id), "mfa_pending": user_id},
        expires_delta=timedelta(minutes=5),
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
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
        institution=user_data.institution
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token (or MFA challenge if MFA is enabled)."""
    # Find user
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
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

    # MFA gate: do not issue full access tokens until MFA verified
    mfa_result = await db.execute(
        select(MFASecret).where(MFASecret.user_id == user.id)
    )
    mfa_secret = mfa_result.scalar_one_or_none()
    if mfa_secret and mfa_secret.is_enabled:
        return Token(
            access_token=None,
            refresh_token=None,
            token_type="bearer",
            mfa_required=True,
            mfa_token=_create_mfa_pending_token(user.id),
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        mfa_required=False,
        mfa_token=None,
    )


@router.post("/login/mfa", response_model=Token)
async def login_mfa(
    payload: MFALoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Complete MFA login: verify mfa_token + TOTP/backup code, then issue real tokens."""
    try:
        claims = decode_token(payload.mfa_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA token",
        )

    mfa_pending = claims.get("mfa_pending")
    if mfa_pending is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not an MFA pending token",
        )
    user_id = int(mfa_pending)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA session",
        )

    ok = await SecurityService.verify_mfa_code(user_id, payload.code, db)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code",
        )

    user.last_login = datetime.utcnow()
    await db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        mfa_required=False,
        mfa_token=None,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current logged-in user information"""
    return current_user


@router.post("/logout")
async def logout(
    request: Request,
    token: Optional[str] = Depends(_optional_oauth2),
    current_user: User = Depends(get_current_user),
):
    """Logout current user and blacklist the bearer token when present."""
    # Prefer explicit dependency token; fall back to Authorization header
    bearer = token
    if not bearer:
        auth = request.headers.get("Authorization") or ""
        if auth.lower().startswith("bearer "):
            bearer = auth.split(" ", 1)[1].strip()
    if bearer:
        await SecurityService.blacklist_token(bearer)
    return {"message": "Successfully logged out"}


@router.post("/create-test-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_test_admin(
    db: AsyncSession = Depends(get_db)
):
    """Create a test admin user (Development only)"""
    from ..models.user import UserRole
    
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in development mode"
        )
    
    # Check if admin exists
    result = await db.execute(
        select(User).where(User.username == 'admin')
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return existing
    
    # Create admin
    admin = User(
        email="admin@neuropredict.ai",
        username="admin",
        full_name="System Administrator",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
        institution="NeuroPredict-AI"
    )
    
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    return admin
