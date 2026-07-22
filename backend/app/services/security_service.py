"""
Security Service - MFA, Password Policies, IP Whitelist, Session Management
"""
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from ipaddress import ip_address, ip_network
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, delete
from fastapi import HTTPException, status, Request
import secrets
import hashlib

from ..models.security import (
    MFASecret, MFAMethod, UserSession, IPWhitelist,
    PasswordPolicy, PasswordHistory, SecurityLog, FailedLoginAttempt
)
from ..models.user import User
from ..core.security import get_password_hash, verify_password
from ..core.config import settings
from ..core.crypto import encrypt_text, decrypt_text
import jwt as pyjwt
from jose import jwt as jose_jwt
import redis.asyncio as redis
import time
import json


def _encrypt_backup_codes(codes: List[str]) -> str:
    """Encrypt backup codes as a Fernet ciphertext of JSON list."""
    return encrypt_text(json.dumps(codes))


def _decrypt_backup_codes(stored) -> List[str]:
    """Decrypt backup codes; supports legacy plaintext list for migration."""
    if stored is None:
        return []
    if isinstance(stored, list):
        # Legacy unencrypted storage
        return [str(c).upper() for c in stored]
    if isinstance(stored, str):
        plain = decrypt_text(stored)
        if plain is None:
            # Might already be a JSON string without encryption (unlikely)
            try:
                parsed = json.loads(stored)
                if isinstance(parsed, list):
                    return [str(c).upper() for c in parsed]
            except Exception:
                return []
            return []
        try:
            parsed = json.loads(plain)
            if isinstance(parsed, list):
                return [str(c).upper() for c in parsed]
        except Exception:
            return []
    return []


class SecurityService:
    """Security service for MFA, password policies, IP whitelist, and session management"""
    _redis_client: Optional[redis.Redis] = None

    @staticmethod
    async def _get_redis() -> Optional[redis.Redis]:
        if SecurityService._redis_client is None:
            try:
                SecurityService._redis_client = redis.from_url(
                    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                    decode_responses=True
                )
            except Exception:
                SecurityService._redis_client = None
        return SecurityService._redis_client

    @staticmethod
    async def blacklist_token(token: str, expires_at_unix: Optional[int] = None):
        """
        Blacklist a token in Redis until it expires.
        """
        client = await SecurityService._get_redis()
        if not client:
            return  # silently ignore if redis not available
        ttl = 0
        if expires_at_unix is not None:
            now = int(time.time())
            ttl = max(expires_at_unix - now, 0)
        else:
            # Try to decode JWT to get exp
            try:
                payload = jose_jwt.get_unverified_claims(token)  # type: ignore
                exp = int(payload.get("exp", 0))
                now = int(time.time())
                ttl = max(exp - now, 0)
            except Exception:
                ttl = 3600
        key = f"blacklist:{token}"
        try:
            if ttl > 0:
                await client.setex(key, ttl, "1")
            else:
                await client.set(key, "1")
        except Exception:
            pass

    @staticmethod
    async def is_token_blacklisted(token: str) -> bool:
        client = await SecurityService._get_redis()
        if not client:
            return False
        try:
            val = await client.get(f"blacklist:{token}")
            return val == "1"
        except Exception:
            return False
    
    @staticmethod
    async def generate_mfa_secret(user_id: int, method: MFAMethod = MFAMethod.TOTP, db: AsyncSession = None) -> dict:
        """Generate MFA secret for user"""
        # Check if user already has MFA
        result = await db.execute(
            select(MFASecret).where(MFASecret.user_id == user_id)
        )
        existing_mfa = result.scalar_one_or_none()
        
        if method == MFAMethod.TOTP:
            # Generate TOTP secret
            secret = pyotp.random_base32()
            
            if existing_mfa:
                existing_mfa.secret_key = encrypt_text(secret)
                existing_mfa.method = method.value
                existing_mfa.is_verified = False
                mfa_secret = existing_mfa
            else:
                mfa_secret = MFASecret(
                    user_id=user_id,
                    method=method.value,
                    secret_key=encrypt_text(secret),
                    is_enabled=False,
                    is_verified=False
                )
                db.add(mfa_secret)
            
            # Generate backup codes
            backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
            # store encrypted JSON string to avoid leaking individual codes
            mfa_secret.backup_codes = _encrypt_backup_codes(backup_codes)
            
            await db.commit()
            await db.refresh(mfa_secret)
            
            # Generate QR code
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=f"user_{user_id}",
                issuer_name=settings.APP_NAME
            )
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                "secret": secret,
                "qr_code": f"data:image/png;base64,{qr_code_base64}",
                "backup_codes": backup_codes,
                "provisioning_uri": provisioning_uri
            }
        
        return {"error": "Unsupported MFA method"}
    
    @staticmethod
    async def verify_mfa_code(user_id: int, code: str, db: AsyncSession) -> bool:
        """Verify MFA code"""
        result = await db.execute(
            select(MFASecret).where(
                and_(
                    MFASecret.user_id == user_id,
                    MFASecret.is_enabled == True
                )
            )
        )
        mfa_secret = result.scalar_one_or_none()
        
        if not mfa_secret:
            return False
        
        if mfa_secret.method == MFAMethod.TOTP.value:
            secret = decrypt_text(mfa_secret.secret_key) or ""
            totp = pyotp.TOTP(secret)
            # Check if code is valid (current or previous/next window for clock skew)
            if totp.verify(code, valid_window=1):
                mfa_secret.last_used = datetime.utcnow()
                await db.commit()
                return True
        
        # Check backup codes (decrypt at verify time)
        codes = _decrypt_backup_codes(mfa_secret.backup_codes)
        code_upper = code.upper()
        if codes and code_upper in codes:
            codes.remove(code_upper)
            mfa_secret.backup_codes = _encrypt_backup_codes(codes)
            mfa_secret.last_used = datetime.utcnow()
            await db.commit()
            return True
        
        return False
    
    @staticmethod
    async def enable_mfa(user_id: int, verification_code: str, db: AsyncSession) -> bool:
        """Enable MFA after verification"""
        result = await db.execute(
            select(MFASecret).where(MFASecret.user_id == user_id)
        )
        mfa_secret = result.scalar_one_or_none()
        
        if not mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA secret not found. Please generate one first."
            )
        
        # Verify code
        if mfa_secret.method == MFAMethod.TOTP.value:
            secret = decrypt_text(mfa_secret.secret_key) or ""
            totp = pyotp.TOTP(secret)
            if not totp.verify(verification_code, valid_window=1):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification code"
                )
        
        mfa_secret.is_enabled = True
        mfa_secret.is_verified = True
        await db.commit()
        
        # Log security event
        await SecurityService.log_security_event(
            db=db,
            user_id=user_id,
            event_type="mfa_enabled",
            severity="info",
            description="MFA enabled successfully"
        )
        
        return True
    
    @staticmethod
    async def check_password_policy(password: str, db: AsyncSession) -> Tuple[bool, Optional[str]]:
        """Check if password meets policy requirements"""
        # Get active password policy
        result = await db.execute(
            select(PasswordPolicy).where(
                and_(
                    PasswordPolicy.is_active == True,
                    PasswordPolicy.is_default == True
                )
            )
        )
        policy = result.scalar_one_or_none()
        
        # Default policy if none exists
        if not policy:
            policy = PasswordPolicy(
                min_length=8,
                max_length=128,
                require_uppercase=True,
                require_lowercase=True,
                require_digits=True,
                require_special_chars=True,
                special_chars="!@#$%^&*()_+-=[]{}|;:,.<>?"
            )
        
        # Check length
        if len(password) < policy.min_length:
            return False, f"Password must be at least {policy.min_length} characters long"
        
        if len(password) > policy.max_length:
            return False, f"Password must be at most {policy.max_length} characters long"
        
        # Check requirements
        if policy.require_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if policy.require_lowercase and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if policy.require_digits and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if policy.require_special_chars:
            special_chars = set(policy.special_chars)
            if not any(c in special_chars for c in password):
                return False, f"Password must contain at least one special character: {policy.special_chars}"
        
        return True, None
    
    @staticmethod
    async def check_password_history(user_id: int, new_password: str, db: AsyncSession) -> Tuple[bool, Optional[str]]:
        """Check if password was recently used"""
        result = await db.execute(
            select(PasswordPolicy).where(
                and_(
                    PasswordPolicy.is_active == True,
                    PasswordPolicy.is_default == True
                )
            )
        )
        policy = result.scalar_one_or_none()
        
        if not policy or policy.prevent_reuse_count == 0:
            return True, None
        
        # Get recent password history
        result = await db.execute(
            select(PasswordHistory)
            .where(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(policy.prevent_reuse_count)
        )
        recent_passwords = result.scalars().all()
        
        # Check if new password matches any recent password
        for password_history in recent_passwords:
            if verify_password(new_password, password_history.password_hash):
                return False, f"Password cannot be one of the last {policy.prevent_reuse_count} passwords"
        
        return True, None
    
    @staticmethod
    async def save_password_to_history(user_id: int, password_hash: str, db: AsyncSession):
        """Save password to history"""
        password_history = PasswordHistory(
            user_id=user_id,
            password_hash=password_hash
        )
        db.add(password_history)
        
        # Get policy to limit history size
        result = await db.execute(
            select(PasswordPolicy).where(
                and_(
                    PasswordPolicy.is_active == True,
                    PasswordPolicy.is_default == True
                )
            )
        )
        policy = result.scalar_one_or_none()
        
        if policy and policy.prevent_reuse_count > 0:
            # Delete old password history beyond prevent_reuse_count
            result = await db.execute(
                select(PasswordHistory.id)
                .where(PasswordHistory.user_id == user_id)
                .order_by(PasswordHistory.created_at.desc())
                .offset(policy.prevent_reuse_count)
            )
            old_ids = [row[0] for row in result.all()]
            if old_ids:
                await db.execute(
                    delete(PasswordHistory).where(PasswordHistory.id.in_(old_ids))
                )
        
        await db.commit()
    
    @staticmethod
    async def check_ip_whitelist(user_id: int, ip_address: str, db: AsyncSession) -> bool:
        """Check if IP address is whitelisted for user"""
        # Get user's IP whitelist
        result = await db.execute(
            select(IPWhitelist).where(
                and_(
                    IPWhitelist.user_id == user_id,
                    IPWhitelist.is_active == True,
                    or_(
                        IPWhitelist.expires_at.is_(None),
                        IPWhitelist.expires_at > datetime.utcnow()
                    )
                )
            )
        )
        whitelist_entries = result.scalars().all()
        
        if not whitelist_entries:
            # No whitelist means all IPs are allowed
            return True
        
        client_ip = ip_address(ip_address)
        
        for entry in whitelist_entries:
            # Check exact IP match
            if entry.ip_address == ip_address:
                return True
            
            # Check IP range (CIDR)
            if entry.ip_range:
                try:
                    network = ip_network(entry.ip_range, strict=False)
                    if client_ip in network:
                        return True
                except ValueError:
                    continue
        
        return False
    
    @staticmethod
    async def create_session(
        user_id: int,
        session_token: str,
        refresh_token: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
        expires_at: datetime,
        db: AsyncSession
    ) -> UserSession:
        """Create a new user session"""
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session
    
    @staticmethod
    async def revoke_session(session_token: str, db: AsyncSession) -> bool:
        """Revoke a session"""
        result = await db.execute(
            select(UserSession).where(UserSession.session_token == session_token)
        )
        session = result.scalar_one_or_none()
        
        if session:
            session.is_active = False
            session.is_revoked = True
            session.revoked_at = datetime.utcnow()
            await db.commit()
            return True
        
        return False
    
    @staticmethod
    async def revoke_all_user_sessions(user_id: int, db: AsyncSession):
        """Revoke all sessions for a user"""
        result = await db.execute(
            select(UserSession).where(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True
                )
            )
        )
        sessions = result.scalars().all()
        
        for session in sessions:
            session.is_active = False
            session.is_revoked = True
            session.revoked_at = datetime.utcnow()
        
        await db.commit()
    
    @staticmethod
    async def cleanup_expired_sessions(db: AsyncSession):
        """Clean up expired sessions"""
        await db.execute(
            delete(UserSession).where(
                and_(
                    UserSession.expires_at < datetime.utcnow(),
                    UserSession.is_active == False
                )
            )
        )
        await db.commit()
    
    @staticmethod
    async def log_security_event(
        db: AsyncSession,
        user_id: Optional[int],
        event_type: str,
        severity: str = "info",
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_path: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        """Log a security event"""
        security_log = SecurityLog(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            success=success,
            error_message=error_message,
            metadata=metadata
        )
        db.add(security_log)
        await db.commit()
    
    @staticmethod
    async def record_failed_login(
        username: Optional[str],
        user_id: Optional[int],
        ip_address: Optional[str],
        user_agent: Optional[str],
        db: AsyncSession
    ):
        """Record a failed login attempt"""
        failed_attempt = FailedLoginAttempt(
            username=username,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(failed_attempt)
        
        # Update user's failed login count
        if user_id:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.failed_login_count += 1
                
                # Check if user should be locked
                result = await db.execute(
                    select(PasswordPolicy).where(
                        and_(
                            PasswordPolicy.is_active == True,
                            PasswordPolicy.is_default == True
                        )
                    )
                )
                policy = result.scalar_one_or_none()
                
                if policy and user.failed_login_count >= policy.max_failed_attempts:
                    user.is_locked = True
                    user.locked_until = datetime.utcnow() + timedelta(minutes=policy.lockout_duration_minutes)
                    
                    await SecurityService.log_security_event(
                        db=db,
                        user_id=user_id,
                        event_type="account_locked",
                        severity="warning",
                        description=f"Account locked due to {user.failed_login_count} failed login attempts",
                        ip_address=ip_address
                    )
        
        await db.commit()
    
    @staticmethod
    async def reset_failed_login_count(user_id: int, db: AsyncSession):
        """Reset failed login count after successful login"""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.failed_login_count = 0
            if user.is_locked and user.locked_until and user.locked_until < datetime.utcnow():
                user.is_locked = False
                user.locked_until = None
            await db.commit()
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers (proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"

