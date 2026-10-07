"""
Reports API Endpoints
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import get_current_active_user, get_current_user
from ..db.session import get_db
from ..models.patient import Patient
from ..models.prediction import DiseaseType, Prediction, RiskLevel
from ..models.user import User
from ..schemas.reports import ClinicalReport, ManagementReport, ResearchReport
from ..services.reporting_service import ReportingService

router = APIRouter(prefix="/reports", tags=["Reports"])

reporting_service = ReportingService()


@router.get("/summary")
async def get_report_summary(
    report_type: str = Query("clinical", regex="^(clinical|research|administrative)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary statistics for reports"""
    # Get date range
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        start = datetime.now() - timedelta(days=30)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
    else:
        end = datetime.now()

    # Count patients
    patients_count = await db.scalar(
        select(func.count(Patient.id))
    )

    # Count predictions
    predictions_count = await db.scalar(
        select(func.count(Prediction.id))
        .where(Prediction.created_at >= start)
        .where(Prediction.created_at <= end)
    )

    # High risk cases
    high_risk_result = await db.execute(
        select(Prediction).where(Prediction.created_at >= start)
        .where(Prediction.created_at <= end)
    )
    high_risk_predictions = high_risk_result.scalars().all()
    high_risk_count = len([p for p in high_risk_predictions if 
                          (hasattr(p, 'alzheimer_risk_level') and p.alzheimer_risk_level == 'high') or
                          (hasattr(p, 'parkinson_risk_level') and p.parkinson_risk_level == 'high')])

    return {
        "report_type": report_type,
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat()
        },
        "statistics": {
            "total_patients": patients_count,
            "total_predictions": predictions_count,
            "high_risk_cases": high_risk_count,
            "low_risk_cases": predictions_count - high_risk_count if predictions_count else 0
        }
    }


@router.get("/predictions-trend")
async def get_predictions_trend(
    days: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get predictions trend over time"""
    start_date = datetime.now() - timedelta(days=days)
    
    result = await db.execute(
        select(
            func.date(Prediction.created_at).label('date'),
            func.count(Prediction.id).label('count')
        )
        .where(Prediction.created_at >= start_date)
        .group_by(func.date(Prediction.created_at))
        .order_by(func.date(Prediction.created_at))
    )
    
    trends = result.all()
    
    return {
        "period_days": days,
        "data": [
            {
                "date": row.date.isoformat(),
                "count": row.count
            }
            for row in trends
        ]
    }


@router.get("/risk-distribution")
async def get_risk_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get risk level distribution"""
    result = await db.execute(select(Prediction))
    predictions = result.scalars().all()
    
    low = 0
    medium = 0
    high = 0
    
    for pred in predictions:
        if (hasattr(pred, 'alzheimer_risk_level') and pred.alzheimer_risk_level == 'high') or \
           (hasattr(pred, 'parkinson_risk_level') and pred.parkinson_risk_level == 'high'):
            high += 1
        elif (hasattr(pred, 'alzheimer_risk_level') and pred.alzheimer_risk_level == 'medium') or \
             (hasattr(pred, 'parkinson_risk_level') and pred.parkinson_risk_level == 'medium'):
            medium += 1
        else:
            low += 1
    
    return {
        "distribution": {
            "low": low,
            "medium": medium,
            "high": high
        },
        "total": len(predictions)
    }


@router.get("/clinical", response_model=ClinicalReport)
async def get_clinical_report(
    patient_id: int,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Patient-centred clinical report: patient summary and latest predictions"""
    try:
        return await reporting_service.clinical_report(db, patient_id, from_date, to_date)
    except ValueError as exc:
        if str(exc) == "patient_not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found",
            ) from exc
        raise


@router.get("/research", response_model=ResearchReport)
async def get_research_report(
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    risk_level: Optional[RiskLevel] = None,
    disease_type: Optional[DiseaseType] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggregate research report over predictions (descriptive statistics by disease type)"""
    return await reporting_service.research_report(
        db, from_date, to_date, risk_level, disease_type
    )


@router.get("/management", response_model=ManagementReport)
async def get_management_report(
    model_version: Optional[str] = None,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Management KPIs: prediction volume, review rate and model-version distribution"""
    return await reporting_service.management_report(db, model_version, from_date, to_date)
