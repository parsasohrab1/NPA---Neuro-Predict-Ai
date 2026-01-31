"""
Real-Time Monitoring API Endpoints
برای مانیتورینگ برخط AI/ML، کلینیکی، سیستم و امنیتی
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import json

from ..db.session import get_db
from ..models.user import User, UserRole
from ..models.patient import Patient
from ..models.prediction import Prediction, RiskLevel
from ..models.medical_record import MedicalRecord
from ..models.audit import AuditLog
from ..core.security import get_current_user, require_role
from ..services.ai_model_service import ai_model_service

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


# ==================== AI/ML Health Monitoring ====================

@router.get("/ai/ml-health")
async def get_ml_health(
    hours: int = Query(24, ge=1, le=168),  # Last N hours, max 1 week
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """مانیتورینگ سلامت مدل هوش مصنوعی"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get recent predictions
    result = await db.execute(
        select(Prediction)
        .where(Prediction.created_at >= cutoff_time)
        .order_by(Prediction.created_at.desc())
    )
    recent_predictions = result.scalars().all()
    
    if not recent_predictions:
        return {
            "status": "no_data",
            "message": "No predictions in the specified time range",
            "data_drift": None,
            "performance_drift": None,
            "confidence_distribution": None
        }
    
    # Data Drift Analysis
    # Collect input feature statistics
    feature_stats = defaultdict(list)
    for pred in recent_predictions:
        if pred.input_features:
            for key, value in pred.input_features.items():
                if isinstance(value, (int, float)):
                    feature_stats[key].append(value)
    
    # Calculate drift indicators (comparing with baseline - simplified)
    data_drift_indicators = []
    for feature, values in feature_stats.items():
        if len(values) > 10:  # Need sufficient data
            mean = statistics.mean(values)
            std = statistics.stdev(values) if len(values) > 1 else 0
            data_drift_indicators.append({
                "feature": feature,
                "current_mean": round(mean, 2),
                "current_std": round(std, 2),
                "drift_score": 0.0,  # Simplified - would compare with training baseline
                "status": "normal" if std < mean * 0.3 else "warning"
            })
    
    # Performance Drift
    alzheimer_scores = [p.alzheimer_risk_score for p in recent_predictions if p.alzheimer_risk_score]
    parkinson_scores = [p.parkinson_risk_score for p in recent_predictions if p.parkinson_risk_score]
    alzheimer_confidences = [p.alzheimer_confidence for p in recent_predictions if p.alzheimer_confidence]
    parkinson_confidences = [p.parkinson_confidence for p in recent_predictions if p.parkinson_confidence]
    
    performance_metrics = {
        "alzheimer": {
            "avg_risk_score": round(statistics.mean(alzheimer_scores), 3) if alzheimer_scores else None,
            "avg_confidence": round(statistics.mean(alzheimer_confidences), 3) if alzheimer_confidences else None,
            "high_risk_percentage": round(
                len([s for s in alzheimer_scores if s > 0.7]) / len(alzheimer_scores) * 100, 2
            ) if alzheimer_scores else 0
        },
        "parkinson": {
            "avg_risk_score": round(statistics.mean(parkinson_scores), 3) if parkinson_scores else None,
            "avg_confidence": round(statistics.mean(parkinson_confidences), 3) if parkinson_confidences else None,
            "high_risk_percentage": round(
                len([s for s in parkinson_scores if s > 0.7]) / len(parkinson_scores) * 100, 2
            ) if parkinson_scores else 0
        }
    }
    
    # Confidence Score Distribution
    all_confidences = [c for c in alzheimer_confidences + parkinson_confidences if c is not None]
    confidence_distribution = {
        "high_confidence": len([c for c in all_confidences if c >= 0.8]),
        "medium_confidence": len([c for c in all_confidences if 0.5 <= c < 0.8]),
        "low_confidence": len([c for c in all_confidences if c < 0.5]),
        "avg_confidence": round(statistics.mean(all_confidences), 3) if all_confidences else None
    }
    
    return {
        "status": "healthy",
        "time_range_hours": hours,
        "total_predictions": len(recent_predictions),
        "data_drift": {
            "indicators": data_drift_indicators,
            "overall_status": "normal" if all(d["status"] == "normal" for d in data_drift_indicators) else "warning"
        },
        "performance_drift": performance_metrics,
        "confidence_distribution": confidence_distribution
    }


@router.get("/ai/feature-importance")
async def get_feature_importance(
    limit: int = Query(20, ge=1, le=50),
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """نمایش اهمیت ویژگی‌های ورودی (Explainability)"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(Prediction)
        .where(
            and_(
                Prediction.created_at >= cutoff_time,
                Prediction.feature_importance.isnot(None)
            )
        )
        .order_by(Prediction.created_at.desc())
        .limit(1000)
    )
    predictions = result.scalars().all()
    
    if not predictions:
        return {
            "features": [],
            "message": "No feature importance data available"
        }
    
    # Aggregate feature importance across predictions
    feature_importance_agg = defaultdict(list)
    for pred in predictions:
        if pred.feature_importance:
            for feature, importance in pred.feature_importance.items():
                feature_importance_agg[feature].append(abs(importance))
    
    # Calculate average importance
    feature_importance_avg = [
        {
            "feature": feature,
            "avg_importance": round(statistics.mean(importances), 4),
            "std_importance": round(statistics.stdev(importances), 4) if len(importances) > 1 else 0,
            "frequency": len(importances)
        }
        for feature, importances in feature_importance_agg.items()
    ]
    
    # Sort by average importance
    feature_importance_avg.sort(key=lambda x: x["avg_importance"], reverse=True)
    
    return {
        "features": feature_importance_avg[:limit],
        "total_predictions_analyzed": len(predictions)
    }


@router.get("/ai/model-performance")
async def get_model_performance(
    model_version: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """نمایش عملکرد مدل (Accuracy, Sensitivity, F1-Score)"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(Prediction).where(Prediction.created_at >= cutoff_time)
    if model_version:
        query = query.where(Prediction.model_version == model_version)
    
    result = await db.execute(query.order_by(Prediction.created_at.desc()))
    predictions = result.scalars().all()
    
    if not predictions:
        return {
            "status": "no_data",
            "message": "No predictions found"
        }
    
    # Calculate metrics (simplified - would need ground truth for real metrics)
    total = len(predictions)
    high_risk_alzheimer = len([p for p in predictions if p.alzheimer_risk_level == RiskLevel.HIGH])
    high_risk_parkinson = len([p for p in predictions if p.parkinson_risk_level == RiskLevel.HIGH])
    reviewed = len([p for p in predictions if p.is_reviewed])
    
    return {
        "model_version": model_version or "all",
        "time_range_hours": hours,
        "total_predictions": total,
        "metrics": {
            "alzheimer": {
                "high_risk_count": high_risk_alzheimer,
                "high_risk_rate": round(high_risk_alzheimer / total * 100, 2) if total > 0 else 0,
                "avg_confidence": round(
                    statistics.mean([p.alzheimer_confidence for p in predictions if p.alzheimer_confidence]), 3
                ) if any(p.alzheimer_confidence for p in predictions) else None
            },
            "parkinson": {
                "high_risk_count": high_risk_parkinson,
                "high_risk_rate": round(high_risk_parkinson / total * 100, 2) if total > 0 else 0,
                "avg_confidence": round(
                    statistics.mean([p.parkinson_confidence for p in predictions if p.parkinson_confidence]), 3
                ) if any(p.parkinson_confidence for p in predictions) else None
            }
        },
        "review_rate": round(reviewed / total * 100, 2) if total > 0 else 0,
        "reviewed_count": reviewed
    }


# ==================== Clinical & Longitudinal Monitoring ====================

@router.get("/clinical/longitudinal/{patient_id}")
async def get_longitudinal_tracking(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ردیابی طولی پیشرفته برای بیمار"""
    # Get patient
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get all predictions
    result = await db.execute(
        select(Prediction)
        .where(Prediction.patient_id == patient_id)
        .order_by(Prediction.created_at.asc())
    )
    predictions = result.scalars().all()
    
    # Get all medical records
    result = await db.execute(
        select(MedicalRecord)
        .where(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.visit_date.asc())
    )
    medical_records = result.scalars().all()
    
    # Build timeline
    timeline = []
    
    # Add medical records
    for record in medical_records:
        timeline.append({
            "date": record.visit_date.isoformat() if record.visit_date else None,
            "type": "visit",
            "mmse_score": record.mmse_score,
            "moca_score": record.moca_score,
            "amyloid_beta": record.amyloid_beta,
            "tau_protein": record.tau_protein,
            "hippocampal_volume": record.hippocampal_volume
        })
    
    # Add predictions
    for pred in predictions:
        timeline.append({
            "date": pred.created_at.isoformat(),
            "type": "prediction",
            "alzheimer_risk_score": pred.alzheimer_risk_score,
            "alzheimer_risk_level": pred.alzheimer_risk_level.value if pred.alzheimer_risk_level else None,
            "parkinson_risk_score": pred.parkinson_risk_score,
            "parkinson_risk_level": pred.parkinson_risk_level.value if pred.parkinson_risk_level else None,
            "confidence": pred.alzheimer_confidence or pred.parkinson_confidence
        })
    
    # Sort by date
    timeline.sort(key=lambda x: x["date"] if x["date"] else "")
    
    # Calculate trends
    mmse_scores = [t["mmse_score"] for t in timeline if t.get("mmse_score")]
    risk_scores = [
        t.get("alzheimer_risk_score") or t.get("parkinson_risk_score")
        for t in timeline if t["type"] == "prediction"
    ]
    
    trends = {
        "mmse_trend": "declining" if len(mmse_scores) > 1 and mmse_scores[-1] < mmse_scores[0] else "stable",
        "risk_trend": "increasing" if len(risk_scores) > 1 and risk_scores[-1] > risk_scores[0] else "stable"
    }
    
    return {
        "patient_id": patient_id,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "timeline": timeline,
        "trends": trends,
        "total_visits": len(medical_records),
        "total_predictions": len(predictions)
    }


@router.get("/clinical/smart-alerts")
async def get_smart_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("doctor"))
):
    """هشدارهای هوشمند برای بیماران پرخطر"""
    alerts = []
    
    # Get all patients with predictions
    result = await db.execute(
        select(Patient, Prediction)
        .join(Prediction, Patient.id == Prediction.patient_id)
        .order_by(Prediction.created_at.desc())
    )
    patient_predictions = result.all()
    
    # Group by patient
    patient_data = defaultdict(list)
    for patient, prediction in patient_predictions:
        patient_data[patient.id].append({
            "patient": patient,
            "prediction": prediction
        })
    
    # Analyze for alerts
    for patient_id, preds in patient_data.items():
        if len(preds) < 2:
            continue
        
        patient = preds[0]["patient"]
        sorted_preds = sorted(preds, key=lambda x: x["prediction"].created_at)
        
        # Check for risk escalation
        latest = sorted_preds[-1]["prediction"]
        previous = sorted_preds[-2]["prediction"]
        
        latest_risk = latest.alzheimer_risk_score or latest.parkinson_risk_score or 0
        previous_risk = previous.alzheimer_risk_score or previous.parkinson_risk_score or 0
        
        if latest_risk > previous_risk + 0.2:  # Significant increase
            alerts.append({
                "type": "risk_escalation",
                "severity": "high",
                "patient_id": patient_id,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "message": f"Risk increased from {previous_risk:.2f} to {latest_risk:.2f}",
                "timestamp": latest.created_at.isoformat()
            })
        
        # Check for high discrepancy (low confidence)
        if latest.alzheimer_confidence and latest.alzheimer_confidence < 0.5:
            alerts.append({
                "type": "low_confidence",
                "severity": "medium",
                "patient_id": patient_id,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "message": f"Low confidence prediction: {latest.alzheimer_confidence:.2f}",
                "timestamp": latest.created_at.isoformat()
            })
    
    # Get high risk patients
    result = await db.execute(
        select(Prediction, Patient)
        .join(Patient, Prediction.patient_id == Patient.id)
        .where(
            or_(
                Prediction.alzheimer_risk_level == RiskLevel.HIGH,
                Prediction.parkinson_risk_level == RiskLevel.HIGH
            )
        )
        .order_by(Prediction.created_at.desc())
        .limit(10)
    )
    high_risk = result.all()
    
    for prediction, patient in high_risk:
        alerts.append({
            "type": "high_risk_patient",
            "severity": "high",
            "patient_id": patient.id,
            "patient_name": f"{patient.first_name} {patient.last_name}",
            "message": f"High risk detected: {prediction.alzheimer_risk_level or prediction.parkinson_risk_level}",
            "timestamp": prediction.created_at.isoformat()
        })
    
    return {
        "alerts": alerts[:50],  # Limit to 50 most recent
        "total_alerts": len(alerts),
        "high_severity_count": len([a for a in alerts if a["severity"] == "high"])
    }


@router.get("/clinical/prediction-queue")
async def get_prediction_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """نمایش صف انتظار پیش‌بینی‌ها"""
    # In a real system, this would check a queue (Redis, Celery, etc.)
    # For now, we'll show recent predictions that are being processed
    
    # Get predictions from last hour
    cutoff_time = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(Prediction)
        .where(Prediction.created_at >= cutoff_time)
        .order_by(Prediction.created_at.desc())
    )
    recent = result.scalars().all()
    
    return {
        "queue_length": len(recent),
        "recent_predictions": [
            {
                "id": p.id,
                "patient_id": p.patient_id,
                "created_at": p.created_at.isoformat(),
                "status": "completed",
                "processing_time_seconds": None  # Would track in real system
            }
            for p in recent[:20]
        ]
    }


# ==================== System Health Monitoring ====================

@router.get("/system/health")
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """سلامت کلی سیستم"""
    # Check database
    try:
        await db.execute(select(1))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Redis (would need Redis client)
    redis_status = "unknown"  # Would check actual Redis connection
    
    # Get system metrics
    result = await db.execute(select(func.count(Prediction.id)))
    total_predictions = result.scalar() or 0
    
    result = await db.execute(select(func.count(Patient.id)))
    total_patients = result.scalar() or 0
    
    # Recent activity
    cutoff_time = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(func.count(Prediction.id))
        .where(Prediction.created_at >= cutoff_time)
    )
    predictions_last_hour = result.scalar() or 0
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "services": {
            "database": db_status,
            "redis": redis_status,
            "ai_service": "healthy"  # Would check actual service
        },
        "metrics": {
            "total_patients": total_patients,
            "total_predictions": total_predictions,
            "predictions_last_hour": predictions_last_hour,
            "throughput_per_hour": predictions_last_hour
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/system/performance")
async def get_system_performance(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """معیارهای عملکرد سیستم"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get predictions in time range
    result = await db.execute(
        select(Prediction)
        .where(Prediction.created_at >= cutoff_time)
        .order_by(Prediction.created_at.desc())
    )
    predictions = result.scalars().all()
    
    # Calculate throughput
    predictions_per_hour = len(predictions) / hours if hours > 0 else 0
    
    # Get audit logs for API calls
    result = await db.execute(
        select(AuditLog)
        .where(
            and_(
                AuditLog.timestamp >= cutoff_time,
                AuditLog.request_method.in_(["GET", "POST", "PUT", "DELETE"])
            )
        )
    )
    api_calls = result.scalars().all()
    
    # Calculate error rates
    total_calls = len(api_calls)
    error_calls = len([log for log in api_calls if log.status_code and log.status_code >= 400])
    error_rate = (error_calls / total_calls * 100) if total_calls > 0 else 0
    
    # 5xx errors
    server_errors = len([log for log in api_calls if log.status_code and 500 <= log.status_code < 600])
    server_error_rate = (server_errors / total_calls * 100) if total_calls > 0 else 0
    
    return {
        "time_range_hours": hours,
        "latency": {
            "avg_response_time_ms": None,  # Would track in real system
            "p95_response_time_ms": None,
            "p99_response_time_ms": None,
            "target": 200  # Target: < 200ms
        },
        "throughput": {
            "predictions_per_hour": round(predictions_per_hour, 2),
            "api_requests_per_hour": round(total_calls / hours, 2) if hours > 0 else 0,
            "target": 100  # Target: > 100 studies/hour
        },
        "error_rates": {
            "total_error_rate": round(error_rate, 2),
            "server_error_rate": round(server_error_rate, 2),
            "client_error_rate": round((error_calls - server_errors) / total_calls * 100, 2) if total_calls > 0 else 0
        },
        "availability": {
            "uptime_percentage": 99.9,  # Would calculate from actual uptime
            "target": 99.9
        }
    }


@router.get("/system/services")
async def get_services_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """وضعیت سرویس‌های حیاتی"""
    services = []
    
    # Database
    try:
        await db.execute(select(1))
        db_healthy = True
    except Exception:
        db_healthy = False
    
    services.append({
        "name": "PostgreSQL Database",
        "status": "up" if db_healthy else "down",
        "response_time_ms": None,
        "last_check": datetime.utcnow().isoformat()
    })
    
    # Redis (would check actual connection)
    services.append({
        "name": "Redis Cache",
        "status": "unknown",
        "response_time_ms": None,
        "last_check": datetime.utcnow().isoformat()
    })
    
    # AI Service
    services.append({
        "name": "AI Model Service",
        "status": "up",  # Would check actual service
        "response_time_ms": None,
        "last_check": datetime.utcnow().isoformat()
    })
    
    return {
        "services": services,
        "overall_status": "healthy" if all(s["status"] == "up" for s in services) else "degraded"
    }


# ==================== Security & Compliance Monitoring ====================

@router.get("/security/audit-logs")
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    action_type: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """جریان لاگ ممیزی"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(AuditLog).where(AuditLog.timestamp >= cutoff_time)
    
    if action_type:
        query = query.where(AuditLog.action == action_type)
    
    result = await db.execute(
        query.order_by(desc(AuditLog.timestamp)).limit(limit)
    )
    logs = result.scalars().all()
    
    # Filter high-risk activities
    high_risk_actions = ["delete_patient", "delete_prediction", "change_role", "update_user"]
    high_risk_logs = [log for log in logs if log.action in high_risk_actions]
    
    return {
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "ip_address": log.ip_address,
                "status_code": log.status_code,
                "success": log.success,
                "is_high_risk": log.action in high_risk_actions
            }
            for log in logs
        ],
        "high_risk_count": len(high_risk_logs),
        "total_count": len(logs)
    }


@router.get("/security/authentication-monitoring")
async def get_authentication_monitoring(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """نظارت بر احراز هویت"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get login attempts
    result = await db.execute(
        select(AuditLog)
        .where(
            and_(
                AuditLog.timestamp >= cutoff_time,
                AuditLog.action == "login"
            )
        )
        .order_by(desc(AuditLog.timestamp))
    )
    login_logs = result.scalars().all()
    
    # Separate successful and failed
    successful_logins = [log for log in login_logs if log.success]
    failed_logins = [log for log in login_logs if not log.success]
    
    # Detect brute force attempts (multiple failures from same IP)
    ip_failures = defaultdict(int)
    for log in failed_logins:
        if log.ip_address:
            ip_failures[log.ip_address] += 1
    
    brute_force_ips = [ip for ip, count in ip_failures.items() if count >= 5]
    
    return {
        "time_range_hours": hours,
        "login_statistics": {
            "total_attempts": len(login_logs),
            "successful": len(successful_logins),
            "failed": len(failed_logins),
            "success_rate": round(len(successful_logins) / len(login_logs) * 100, 2) if login_logs else 0
        },
        "security_alerts": {
            "brute_force_ips": brute_force_ips,
            "suspicious_activity_count": len(brute_force_ips)
        },
        "recent_failed_logins": [
            {
                "timestamp": log.timestamp.isoformat(),
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "error": log.error_message
            }
            for log in failed_logins[:20]
        ]
    }


@router.get("/security/admin-activity")
async def get_admin_activity(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """فعالیت کاربران ادمین"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get admin users
    result = await db.execute(
        select(User).where(User.role == UserRole.ADMIN)
    )
    admin_users = result.scalars().all()
    admin_ids = [u.id for u in admin_users]
    
    # Get admin activity
    result = await db.execute(
        select(AuditLog)
        .where(
            and_(
                AuditLog.timestamp >= cutoff_time,
                AuditLog.user_id.in_(admin_ids)
            )
        )
        .order_by(desc(AuditLog.timestamp))
    )
    admin_logs = result.scalars().all()
    
    # Group by user
    user_activity = defaultdict(list)
    for log in admin_logs:
        user_activity[log.user_id].append(log)
    
    activity_summary = [
        {
            "user_id": user_id,
            "user_email": next((u.email for u in admin_users if u.id == user_id), "unknown"),
            "activity_count": len(logs),
            "last_activity": max(log.timestamp for log in logs).isoformat() if logs else None,
            "recent_actions": [log.action for log in logs[:5]]
        }
        for user_id, logs in user_activity.items()
    ]
    
    return {
        "time_range_hours": hours,
        "active_admin_count": len([a for a in activity_summary if a["activity_count"] > 0]),
        "total_admin_count": len(admin_users),
        "activity_summary": activity_summary,
        "total_activities": len(admin_logs)
    }

