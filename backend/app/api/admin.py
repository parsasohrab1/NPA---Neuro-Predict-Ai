"""
Admin Dashboard API Endpoints
Aggregates monitoring, user management, model registry, audit logs, and security settings
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import get_current_user, require_role
from ..db.session import get_db
from ..models.audit import AuditLog
from ..models.security import PasswordPolicy, SecurityLog
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserResponse, UserUpdate
from ..services.monitoring_service import MonitoringService

try:
    from ..services.training.model_registry import ModelRegistry
except Exception:
    ModelRegistry = None  # type: ignore


router = APIRouter(prefix="/admin", tags=["Admin"])


# -------- Overview (System Monitoring) --------
@router.get("/system/overview")
async def get_system_overview(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin")),
) -> Dict[str, Any]:
    """
    Overview data for dashboard summary cards and charts.
    - CPU, Memory, Disk
    - Basic counts: users, patients, predictions
    - Recent alerts (security logs errors/warnings)
    """
    health = await MonitoringService.get_health_status(db)
    metrics = await MonitoringService.get_metrics(db)

    counts: Dict[str, int] = {"users": 0, "patients": 0, "predictions": 0}
    try:
        # Users
        result = await db.execute(select(func.count()).select_from(text("users")))
        counts["users"] = int(result.scalar() or 0)
        # Patients
        result = await db.execute(select(func.count()).select_from(text("patients")))
        counts["patients"] = int(result.scalar() or 0)
        # Predictions
        result = await db.execute(select(func.count()).select_from(text("predictions")))
        counts["predictions"] = int(result.scalar() or 0)
    except Exception:
        # Tables may not exist in all environments; keep counts at 0
        pass

    # Recent security alerts (warnings/errors/critical)
    recent_alerts: List[Dict[str, Any]] = []
    try:
        result = await db.execute(
            select(SecurityLog)
            .where(SecurityLog.severity.in_(["warning", "error", "critical"]))
            .order_by(SecurityLog.timestamp.desc())
            .limit(10)
        )
        logs = result.scalars().all()
        for log in logs:
            recent_alerts.append(
                {
                    "id": log.id,
                    "event_type": log.event_type,
                    "severity": log.severity,
                    "timestamp": log.timestamp,
                    "description": log.description,
                    "ip_address": log.ip_address,
                    "success": log.success,
                }
            )
    except Exception:
        pass

    return {
        "health": health,
        "metrics": metrics.get("metrics", {}),
        "counts": counts,
        "recent_alerts": recent_alerts,
    }


@router.get("/system/activity-feed")
async def get_activity_feed(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin")),
) -> List[Dict[str, Any]]:
    """
    Get recent activity feed combining audit logs and system events
    """
    activities: List[Dict[str, Any]] = []
    
    # Get recent audit logs
    try:
        result = await db.execute(
            select(AuditLog)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        logs = result.scalars().all()
        for log in logs:
            activities.append({
                "id": f"audit_{log.id}",
                "type": "info",
                "message": f"{log.action} - {log.resource_type}",
                "timestamp": log.timestamp.isoformat(),
                "details": {
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "user_id": log.user_id,
                }
            })
    except Exception:
        pass
    
    # Get recent security events
    try:
        result = await db.execute(
            select(SecurityLog)
            .order_by(SecurityLog.timestamp.desc())
            .limit(10)
        )
        logs = result.scalars().all()
        for log in logs:
            activity_type = "info"
            if log.severity == "error" or log.severity == "critical":
                activity_type = "error"
            elif log.severity == "warning":
                activity_type = "warning"
            elif log.success:
                activity_type = "success"
            
            activities.append({
                "id": f"security_{log.id}",
                "type": activity_type,
                "message": f"{log.event_type}: {log.description}",
                "timestamp": log.timestamp.isoformat(),
                "details": {
                    "event_type": log.event_type,
                    "severity": log.severity,
                    "success": log.success,
                }
            })
    except Exception:
        pass
    
    # Sort by timestamp and return most recent
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:limit]


# -------- Users & Roles --------
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    role: Optional[UserRole] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    search: Optional[str] = Query(default=None, description="search by email, username, full_name"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin")),
):
    query = select(User)
    conditions = []
    if role:
        conditions.append(User.role == role)
    if is_active is not None:
        conditions.append(User.is_active == is_active)
    if search:
        like = f"%{search}%"
        conditions.append(or_(User.email.ilike(like), User.username.ilike(like), User.full_name.ilike(like)))
    if conditions:
        query = query.where(and_(*conditions))
    query = query.order_by(User.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin")),
):
    # Uniqueness check
    existing = await db.execute(
        select(User).where(or_(User.email == body.email, User.username == body.username))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User with this email or username already exists")

    # Basic password policy is applied in auth.register; replicate minimal here
    from ..core.security import get_password_hash

    new_user = User(
        email=body.email,
        username=body.username,
        full_name=body.full_name,
        hashed_password=get_password_hash(body.password),
        role=body.role,
        license_number=body.license_number,
        department=body.department,
        institution=body.institution,
        is_active=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin")),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.email is not None:
        user.email = body.email
    if body.full_name is not None:
        user.full_name = body.full_name
    if body.role is not None:
        user.role = body.role
    if body.license_number is not None:
        user.license_number = body.license_number
    if body.department is not None:
        user.department = body.department
    if body.institution is not None:
        user.institution = body.institution
    if body.is_active is not None:
        user.is_active = body.is_active

    await db.commit()
    await db.refresh(user)
    return user


# -------- Model Management --------
@router.get("/models")
async def list_models(
    current_user = Depends(require_role("admin")),
):
    if ModelRegistry is None:
        return {"models": [], "current_model": None, "note": "ModelRegistry unavailable"}
    registry = ModelRegistry()
    return {"models": registry.list_models(), "current_model": registry.get_active_model()}


class ActivateModelRequest(dict):
    version: str  # typed hint for editors; FastAPI will accept body as dict with 'version'


@router.post("/models/activate")
async def activate_model(
    body: Dict[str, str],
    current_user = Depends(require_role("admin")),
):
    if "version" not in body:
        raise HTTPException(status_code=400, detail="Missing 'version'")
    if ModelRegistry is None:
        raise HTTPException(status_code=400, detail="ModelRegistry unavailable")
    registry = ModelRegistry()
    ok = registry.set_active_model(body["version"])
    if not ok:
        raise HTTPException(status_code=404, detail="Model version not found")
    return {"message": "Model activated", "version": body["version"]}


# -------- Audit Logs --------
@router.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[int] = Query(default=None),
    action: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin")),
):
    query = select(AuditLog)
    conditions = []
    if user_id is not None:
        conditions.append(AuditLog.user_id == user_id)
    if action:
        conditions.append(AuditLog.action.ilike(f"%{action}%"))
    if date_from:
        conditions.append(AuditLog.timestamp >= date_from)
    if date_to:
        conditions.append(AuditLog.timestamp <= date_to)
    if conditions:
        query = query.where(and_(*conditions))
    query = query.order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "ip_address": log.ip_address,
            "status_code": log.status_code,
            "success": log.success,
            "timestamp": log.timestamp,
            "details": log.details,
        }
        for log in logs
    ]


# -------- Security Settings (Password Policy) --------
@router.get("/settings/security/password-policy")
async def get_password_policy(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin")),
):
    result = await db.execute(
        select(PasswordPolicy).where(
            and_(PasswordPolicy.is_active == True, PasswordPolicy.is_default == True)
        )
    )
    policy = result.scalar_one_or_none()
    if not policy:
        # Minimal default if none is defined in DB
        return {
            "min_length": 8,
            "max_length": 128,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digits": True,
            "require_special_chars": True,
            "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?",
            "prevent_reuse_count": 5,
            "expiration_days": None,
            "warning_days": 7,
            "max_failed_attempts": 5,
            "lockout_duration_minutes": 30,
        }
    return {
        "id": policy.id,
        "name": policy.name,
        "description": policy.description,
        "min_length": policy.min_length,
        "max_length": policy.max_length,
        "require_uppercase": policy.require_uppercase,
        "require_lowercase": policy.require_lowercase,
        "require_digits": policy.require_digits,
        "require_special_chars": policy.require_special_chars,
        "special_chars": policy.special_chars,
        "prevent_reuse_count": policy.prevent_reuse_count,
        "expiration_days": policy.expiration_days,
        "warning_days": policy.warning_days,
        "max_failed_attempts": policy.max_failed_attempts,
        "lockout_duration_minutes": policy.lockout_duration_minutes,
        "is_active": policy.is_active,
        "is_default": policy.is_default,
        "updated_at": policy.updated_at,
    }


@router.put("/settings/security/password-policy")
async def update_password_policy(
    body: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin")),
):
    result = await db.execute(
        select(PasswordPolicy).where(
            and_(PasswordPolicy.is_active == True, PasswordPolicy.is_default == True)
        )
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Default password policy not found")

    # Update allowed fields
    for field in [
        "min_length",
        "max_length",
        "require_uppercase",
        "require_lowercase",
        "require_digits",
        "require_special_chars",
        "special_chars",
        "prevent_reuse_count",
        "expiration_days",
        "warning_days",
        "max_failed_attempts",
        "lockout_duration_minutes",
        "description",
        "name",
    ]:
        if field in body:
            setattr(policy, field, body[field])

    await db.commit()
    await db.refresh(policy)
    return {"message": "Password policy updated", "id": policy.id}


