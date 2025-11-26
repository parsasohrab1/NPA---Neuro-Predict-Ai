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


@router.get(
    "/stats",
    summary="Get database statistics for reports",
)
async def get_reports_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Get basic statistics about available data for reports
    """
    from sqlalchemy import select, func
    from ..models.patient import Patient
    from ..models.prediction import Prediction
    from ..models.medical_record import MedicalRecord
    
    # Count patients
    patient_count_result = await db.execute(select(func.count(Patient.id)))
    patient_count = patient_count_result.scalar_one()
    
    # Count predictions
    prediction_count_result = await db.execute(select(func.count(Prediction.id)))
    prediction_count = prediction_count_result.scalar_one()
    
    # Count medical records
    medical_record_count_result = await db.execute(select(func.count(MedicalRecord.id)))
    medical_record_count = medical_record_count_result.scalar_one()
    
    # Get sample patient IDs
    sample_patients_result = await db.execute(
        select(Patient.id, Patient.patient_id, Patient.first_name, Patient.last_name).limit(5)
    )
    sample_patients = [
        {
            "id": row[0],
            "patient_identifier": row[1],
            "name": f"{row[2]} {row[3]}",
        }
        for row in sample_patients_result.all()
    ]
    
    return {
        "total_patients": patient_count,
        "total_predictions": prediction_count,
        "total_medical_records": medical_record_count,
        "sample_patients": sample_patients,
        "status": "ready" if prediction_count > 0 else "no_data",
    }


@router.post(
    "/load-sample-data",
    status_code=status.HTTP_201_CREATED,
    summary="Load sample data for reports testing",
)
async def load_sample_data(
    db: AsyncSession = Depends(get_db),
):
    """
    Load sample patients, medical records, and predictions for reports testing.
    This is useful for populating the Reports tab with demo data.
    """
    from ..models.patient import Patient
    from ..models.medical_record import MedicalRecord
    from ..models.prediction import Prediction
    from sqlalchemy import select
    from datetime import date, timedelta
    import random
    
    total_patients = 0
    total_records = 0
    total_predictions = 0
    
    # Sample data configuration
    sample_patients = [
        {"first_name": "John", "last_name": "Doe", "age": 65, "gender": "MALE", "education_years": 16},
        {"first_name": "Jane", "last_name": "Smith", "age": 72, "gender": "FEMALE", "education_years": 14},
        {"first_name": "Robert", "last_name": "Johnson", "age": 68, "gender": "MALE", "education_years": 12},
        {"first_name": "Mary", "last_name": "Williams", "age": 70, "gender": "FEMALE", "education_years": 18},
        {"first_name": "Michael", "last_name": "Brown", "age": 75, "gender": "MALE", "education_years": 10},
        {"first_name": "Patricia", "last_name": "Jones", "age": 69, "gender": "FEMALE", "education_years": 15},
        {"first_name": "David", "last_name": "Garcia", "age": 73, "gender": "MALE", "education_years": 13},
        {"first_name": "Linda", "last_name": "Martinez", "age": 67, "gender": "FEMALE", "education_years": 16},
        {"first_name": "Richard", "last_name": "Davis", "age": 71, "gender": "MALE", "education_years": 11},
        {"first_name": "Barbara", "last_name": "Rodriguez", "age": 74, "gender": "FEMALE", "education_years": 17},
    ]
    
    for i, patient_data in enumerate(sample_patients):
        patient_id = f"RPT_{1000 + i}"
        
        # Check if patient already exists
        result = await db.execute(select(Patient).where(Patient.patient_id == patient_id))
        existing_patient = result.scalar_one_or_none()
        if existing_patient:
            continue
        
        # Create patient
        dob = date.today() - timedelta(days=patient_data["age"] * 365)
        patient = Patient(
            patient_id=patient_id,
            first_name=patient_data["first_name"],
            last_name=patient_data["last_name"],
            date_of_birth=dob,
            gender=Patient.Gender[patient_data["gender"]],
            education_years=patient_data["education_years"],
        )
        
        db.add(patient)
        await db.flush()
        total_patients += 1
        
        # Create 2-4 medical records for each patient
        num_records = random.randint(2, 4)
        for j in range(num_records):
            days_ago = 30 * (num_records - j)
            visit_date = date.today() - timedelta(days=days_ago)
            
            medical_record = MedicalRecord(
                patient_id=patient.id,
                visit_date=visit_date,
                visit_type="Follow-up" if j > 0 else "Initial",
                mmse_score=random.uniform(20, 30),
                moca_score=random.uniform(18, 28),
                memory_score=random.uniform(0.5, 1.0),
                attention_score=random.uniform(0.5, 1.0),
                executive_function_score=random.uniform(0.5, 1.0),
                amyloid_beta=random.uniform(300, 600),
                tau_protein=random.uniform(200, 400),
                dopamine_level=random.uniform(50, 100),
                apoe_e4_status=random.choice([True, False]),
                hippocampal_volume=random.uniform(2500, 4000),
                cortical_thickness=random.uniform(2.0, 3.5),
                ventricular_volume=random.uniform(30000, 50000),
                white_matter_hyperintensities=random.uniform(0.5, 2.0),
                brain_volume_total=random.uniform(1000000, 1400000),
                clinical_notes=f"Report sample visit {j+1}",
            )
            
            db.add(medical_record)
            await db.flush()
            total_records += 1
            
            # Create prediction for each medical record
            # Generate realistic risk scores
            if patient_data["age"] > 72:
                alzheimer_risk = random.uniform(0.6, 0.9)
                parkinson_risk = random.uniform(0.4, 0.7)
            elif patient_data["age"] > 68:
                alzheimer_risk = random.uniform(0.3, 0.6)
                parkinson_risk = random.uniform(0.2, 0.5)
            else:
                alzheimer_risk = random.uniform(0.1, 0.4)
                parkinson_risk = random.uniform(0.1, 0.3)
            
            alzheimer_level = (
                RiskLevel.HIGH if alzheimer_risk >= 0.66
                else RiskLevel.MEDIUM if alzheimer_risk >= 0.33
                else RiskLevel.LOW
            )
            parkinson_level = (
                RiskLevel.HIGH if parkinson_risk >= 0.66
                else RiskLevel.MEDIUM if parkinson_risk >= 0.33
                else RiskLevel.LOW
            )
            
            prediction = Prediction(
                patient_id=patient.id,
                disease_type=DiseaseType.BOTH,
                alzheimer_risk_score=alzheimer_risk,
                parkinson_risk_score=parkinson_risk,
                alzheimer_risk_level=alzheimer_level,
                parkinson_risk_level=parkinson_level,
                model_version=random.choice(["v1.0.0_baseline", "v1.1.0_alzheimer_tuned"]),
                recommendations=f"Regular monitoring recommended. Risk level: {alzheimer_level.value}",
                created_at=datetime.utcnow() - timedelta(days=days_ago),
                is_reviewed=random.choice([True, False]),
            )
            
            db.add(prediction)
            total_predictions += 1
    
    await db.commit()
    
    return {
        "message": "Sample data loaded successfully for Reports",
        "total_patients": total_patients,
        "total_records": total_records,
        "total_predictions": total_predictions,
    }
