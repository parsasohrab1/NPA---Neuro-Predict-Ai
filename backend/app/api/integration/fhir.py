"""HL7 FHIR R4 adapter endpoints (read/search backed by NeuroPredict DB).

Local Patient/Observation/DiagnosticReport adapters query the NeuroPredict DB.
Remote FHIR proxy endpoints (``/fhir/remote/...``) call ``HL7_FHIR_ENDPOINT``
via httpx and return 503 ``not_configured`` when that env var is unset.
"""
from __future__ import annotations

from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.security import get_current_user
from ...db.session import get_db
from ...models.medical_record import MedicalRecord
from ...models.patient import Patient
from ...models.prediction import Prediction
from ...models.user import User
from ...services.integration.errors import IntegrationError
from ...services.integration.fhir_mappers import (
    build_capability_statement,
    build_searchset_bundle,
    medical_record_to_observations,
    patient_to_fhir,
    prediction_to_diagnostic_report,
)
from ...services.integration.fhir_service import FHIRService

router = APIRouter(prefix="/fhir", tags=["FHIR"])

fhir_remote = FHIRService(
    base_url=settings.HL7_FHIR_BASE_URL,
    remote_endpoint=settings.HL7_FHIR_ENDPOINT,
)


def _raise_integration(exc: IntegrationError) -> None:
    raise HTTPException(status_code=exc.http_status, detail=exc.to_dict())


def _base_url(request: Request) -> str:
    """Public URL prefix where these FHIR resources are served."""
    return f"{request.url.scheme}://{request.url.netloc}{settings.API_V1_PREFIX}/fhir"


def _operation_outcome(severity: str, code: str, diagnostics: str) -> dict[str, Any]:
    """Build a minimal FHIR ``OperationOutcome`` payload."""
    return {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": severity,
                "code": code,
                "diagnostics": diagnostics,
            }
        ],
    }


# --- metadata ---------------------------------------------------------------

@router.get("/metadata")
async def get_capability_statement() -> dict[str, Any]:
    """FHIR ``CapabilityStatement`` (does not require auth, per FHIR spec)."""
    return build_capability_statement()


# --- Patient ----------------------------------------------------------------

async def _resolve_patient(db: AsyncSession, patient_id: str) -> Optional[Patient]:
    """Resolve a Patient by numeric internal id or by external ``patient_id``."""
    stmt = select(Patient)
    if patient_id.isdigit():
        stmt = stmt.where(Patient.id == int(patient_id))
    else:
        stmt = stmt.where(Patient.patient_id == patient_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.get("/Patient/{patient_id}")
async def read_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Read a Patient by id (internal numeric id or external ``patient_id``)."""
    patient = await _resolve_patient(db, patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_operation_outcome("error", "not-found", f"Patient '{patient_id}' not found"),
        )
    return patient_to_fhir(patient)


@router.get("/Patient")
async def search_patient(
    request: Request,
    identifier: Optional[str] = Query(None, description="External patient identifier"),
    _id: Optional[str] = Query(None, alias="_id"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Search Patient by ``identifier`` or ``_id`` (returns a searchset Bundle)."""
    stmt = select(Patient)
    if _id and _id.isdigit():
        stmt = stmt.where(Patient.id == int(_id))
    if identifier:
        stmt = stmt.where(Patient.patient_id == identifier)
    result = await db.execute(stmt.limit(50))
    patients = list(result.scalars().all())
    return build_searchset_bundle(
        (patient_to_fhir(p) for p in patients),
        base_url=_base_url(request),
    )


# --- Observation ------------------------------------------------------------

@router.get("/Observation")
async def search_observation(
    request: Request,
    subject: Optional[str] = Query(None, description="Patient/{id} reference"),
    patient: Optional[str] = Query(None, description="Patient id (shortcut)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Search Observations for a patient (vital signs / labs / cognitive scores)."""
    pid: Optional[str] = patient
    if subject and subject.startswith("Patient/"):
        pid = subject.split("/", 1)[1]
    if not pid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_operation_outcome(
                "error",
                "invalid",
                "subject=Patient/{id} or patient={id} query parameter is required",
            ),
        )
    target = await _resolve_patient(db, pid)
    if target is None:
        return build_searchset_bundle((), base_url=_base_url(request))

    result = await db.execute(
        select(MedicalRecord)
        .where(MedicalRecord.patient_id == target.id)
        .order_by(MedicalRecord.visit_date.desc())
        .limit(20)
    )
    records = list(result.scalars().all())
    observations: list[dict[str, Any]] = []
    for record in records:
        observations.extend(medical_record_to_observations(record))
    return build_searchset_bundle(observations, base_url=_base_url(request))


# --- DiagnosticReport -------------------------------------------------------

@router.get("/DiagnosticReport/{report_id}")
async def read_diagnostic_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Read a DiagnosticReport for a stored prediction."""
    if not report_id.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_operation_outcome("error", "invalid", "DiagnosticReport id must be numeric"),
        )
    result = await db.execute(select(Prediction).where(Prediction.id == int(report_id)))
    prediction = result.scalar_one_or_none()
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_operation_outcome("error", "not-found", "DiagnosticReport not found"),
        )
    return prediction_to_diagnostic_report(prediction)


@router.get("/DiagnosticReport")
async def search_diagnostic_report(
    request: Request,
    subject: Optional[str] = Query(None),
    patient: Optional[str] = Query(None),
    status_param: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Search DiagnosticReports by patient (status filter is currently no-op)."""
    pid: Optional[str] = patient
    if subject and subject.startswith("Patient/"):
        pid = subject.split("/", 1)[1]

    stmt = select(Prediction)
    if pid:
        target = await _resolve_patient(db, pid)
        if target is None:
            return build_searchset_bundle((), base_url=_base_url(request))
        stmt = stmt.where(Prediction.patient_id == target.id)
    stmt = stmt.order_by(Prediction.created_at.desc()).limit(50)

    result = await db.execute(stmt)
    predictions = list(result.scalars().all())
    return build_searchset_bundle(
        (prediction_to_diagnostic_report(p) for p in predictions),
        base_url=_base_url(request),
    )


# --- ImagingStudy (local index not implemented) -----------------------------

@router.get("/ImagingStudy")
async def search_imaging_study(
    request: Request,
    patient: Optional[str] = Query(None),
    modality: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """ImagingStudy search — local DICOM index is not exposed as FHIR yet.

    Returns HTTP 501 with an explicit ``not_implemented`` payload rather than
    an empty 200 searchset that looks like a successful green path.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "status": "not_implemented",
            "detail": (
                "Local ImagingStudy FHIR search is not implemented. "
                "Use /fhir/remote/ImagingStudy when HL7_FHIR_ENDPOINT is configured, "
                "or PACS DICOM APIs for imaging retrieval."
            ),
        },
    )


# --- Remote FHIR proxy (requires HL7_FHIR_ENDPOINT) -------------------------

@router.get("/remote/status")
async def remote_fhir_status(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Report whether a remote FHIR base URL is configured."""
    configured = fhir_remote.is_remote_configured()
    return {
        "status": "configured" if configured else "not_configured",
        "detail": (
            f"Remote FHIR endpoint: {fhir_remote.remote_endpoint}"
            if configured
            else "HL7_FHIR_ENDPOINT is not set; remote search/read return 503."
        ),
    }


@router.get("/remote/{resource_type}")
async def remote_search_resources(
    resource_type: str,
    request: Request,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Proxy FHIR search to ``HL7_FHIR_ENDPOINT`` (503 if not configured)."""
    params = dict(request.query_params)
    try:
        return fhir_remote.search_resources(resource_type, params)
    except IntegrationError as e:
        _raise_integration(e)
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"status": "upstream_error", "detail": str(e)},
        )


@router.get("/remote/{resource_type}/{resource_id}")
async def remote_read_resource(
    resource_type: str,
    resource_id: str,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Proxy FHIR read to ``HL7_FHIR_ENDPOINT`` (503 if not configured)."""
    try:
        return fhir_remote.read_resource(resource_type, resource_id)
    except IntegrationError as e:
        _raise_integration(e)
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"status": "upstream_error", "detail": str(e)},
        )
