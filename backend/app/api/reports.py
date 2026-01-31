"""
Reports API Endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta

from ..db.session import get_db
from ..models.user import User
from ..models.patient import Patient
from ..models.prediction import Prediction
from ..core.security import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


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
