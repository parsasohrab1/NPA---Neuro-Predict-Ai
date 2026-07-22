"""
PACS Integration API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from typing import Optional
import os
from pathlib import Path

from ...services.integration.pacs_service import PACSService
from ...services.integration.errors import IntegrationError
from ...core.security import get_current_user
from ...core.config import settings
from ...models.user import User

router = APIRouter(prefix="/pacs", tags=["PACS"])

# Initialize PACS service
pacs_service = PACSService(
    pacs_server_url=settings.PACS_SERVER_URL,
    ae_title=settings.PACS_AE_TITLE,
)


def _raise_integration(exc: IntegrationError) -> None:
    raise HTTPException(status_code=exc.http_status, detail=exc.to_dict())


@router.get("/studies")
async def query_studies(
    patient_id: Optional[str] = Query(None),
    patient_name: Optional[str] = Query(None),
    study_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """
    جستجوی مطالعات در PACS (DIMSE C-FIND).

    Returns 503 when PACS is not configured, 501 when DIMSE is not implemented.
    """
    try:
        studies = pacs_service.query_patient_studies(
            patient_id=patient_id,
            patient_name=patient_name,
            study_date=study_date,
        )
        return {
            "status": "success",
            "count": len(studies),
            "studies": studies,
        }
    except IntegrationError as e:
        _raise_integration(e)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying PACS: {str(e)}",
        )


@router.get("/studies/{study_instance_uid}")
async def get_study(
    study_instance_uid: str,
    current_user: User = Depends(get_current_user),
):
    """
    دریافت مطالعه از PACS (C-MOVE/C-GET).

    Returns 503/501 when remote PACS is unavailable or unimplemented.
    """
    try:
        datasets = pacs_service.retrieve_study(study_instance_uid)
        return {
            "status": "success",
            "study_instance_uid": study_instance_uid,
            "images_count": len(datasets),
        }
    except IntegrationError as e:
        _raise_integration(e)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving study: {str(e)}",
        )


@router.post("/upload")
async def upload_dicom(
    file: UploadFile = File(...),
    patient_id: Optional[str] = None,
    study_description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    آپلود فایل DICOM به PACS (local validate + remote C-STORE).

    Local validation still runs; remote store returns 503/501 when not ready.
    """
    try:
        upload_dir = Path(settings.DICOM_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / file.filename

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        validation = pacs_service.validate_dicom_file(str(file_path))

        if not validation["valid"]:
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid DICOM file",
                    "errors": validation["errors"],
                    "warnings": validation["warnings"],
                },
            )

        metadata = pacs_service.parse_dicom_metadata(str(file_path))

        final_patient_id = patient_id or metadata.get("patient_id")
        final_study_description = study_description or metadata.get("study_description", "")

        try:
            success = pacs_service.store_dicom(
                dicom_file_path=str(file_path),
                patient_id=final_patient_id,
                study_description=final_study_description,
            )
        except IntegrationError as e:
            _raise_integration(e)

        if success:
            return {
                "status": "success",
                "message": "DICOM file uploaded successfully",
                "metadata": metadata,
            }
        raise HTTPException(status_code=500, detail="Failed to store DICOM in PACS")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading DICOM: {str(e)}",
        )


@router.get("/worklist")
async def get_worklist(
    patient_id: Optional[str] = Query(None),
    scheduled_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """
    دریافت Modality Worklist از PACS.

    Returns 503/501 when remote PACS is unavailable or unimplemented.
    """
    try:
        worklist = pacs_service.get_modality_worklist(
            patient_id=patient_id,
            scheduled_date=scheduled_date,
        )
        return {
            "status": "success",
            "count": len(worklist),
            "worklist": worklist,
        }
    except IntegrationError as e:
        _raise_integration(e)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving worklist: {str(e)}",
        )


@router.get("/status")
async def pacs_status(current_user: User = Depends(get_current_user)):
    """Report whether remote PACS DIMSE is configured (does not probe the peer)."""
    configured = pacs_service.is_configured()
    return {
        "status": "configured" if configured else "not_configured",
        "detail": (
            f"PACS peer set to {pacs_service.pacs_server_url}"
            if configured
            else "PACS_SERVER_URL is not set; DIMSE operations return 503."
        ),
        "ae_title": pacs_service.ae_title,
    }


@router.post("/validate")
async def validate_dicom_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """اعتبارسنجی فایل DICOM محلی (نیازی به PACS remote ندارد)."""
    try:
        upload_dir = Path(settings.DICOM_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / file.filename

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        validation = pacs_service.validate_dicom_file(str(file_path))
        os.remove(file_path)
        return validation

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validating DICOM: {str(e)}",
        )
