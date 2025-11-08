"""
Reports API Endpoints
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import require_role
from ..db.session import get_db
from ..models.prediction import DiseaseType, RiskLevel
from ..schemas.reports import (
    ClinicalReport,
    ResearchReport,
    ManagementReport,
    ReportExportRequest,
    ReportExportResponse,
)
from ..services.reporting_service import reporting_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid datetime format")


@router.get(
    "/clinical",
    response_model=ClinicalReport,
    summary="Clinical report for a specific patient",
)
async def get_clinical_report(
    patient_id: int = Query(..., description="Internal patient identifier"),
    start: Optional[str] = Query(None, description="ISO datetime start filter"),
    end: Optional[str] = Query(None, description="ISO datetime end filter"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("doctor")),
):
    try:
        return await reporting_service.clinical_report(
            db=db,
            patient_id=patient_id,
            start=_parse_datetime(start),
            end=_parse_datetime(end),
        )
    except ValueError as exc:
        if str(exc) == "patient_not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found") from exc
        raise


@router.get(
    "/research",
    response_model=ResearchReport,
    summary="Aggregated research report",
)
async def get_research_report(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    disease_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("researcher")),
):
    risk_enum = None
    if risk_level:
        try:
            risk_enum = RiskLevel(risk_level)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid risk level") from exc

    disease_enum = None
    if disease_type:
        try:
            disease_enum = DiseaseType(disease_type)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid disease type") from exc

    return await reporting_service.research_report(
        db=db,
        start=_parse_datetime(start),
        end=_parse_datetime(end),
        risk_level=risk_enum,
        disease_type=disease_enum,
    )


@router.get(
    "/management",
    response_model=ManagementReport,
    summary="Operational management report",
)
async def get_management_report(
    model_version: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    return await reporting_service.management_report(
        db=db,
        model_version=model_version,
        start=_parse_datetime(start),
        end=_parse_datetime(end),
    )


@router.post(
    "/export",
    response_model=ReportExportResponse,
    summary="Export report in desired format",
)
async def export_report(
    request: ReportExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("doctor")),
):
    logger.info(
        "Report export triggered by user %s: type=%s format=%s filters=%s",
        getattr(current_user, "id", "unknown"),
        request.report_type,
        request.format,
        request.filters,
    )

    # Placeholder implementation – integrate with reporting pipeline later
    return ReportExportResponse(
        message="Report export queued",
        report_type=request.report_type,
        format=request.format,
        filters=request.filters,
        generated_at=datetime.utcnow(),
    )

