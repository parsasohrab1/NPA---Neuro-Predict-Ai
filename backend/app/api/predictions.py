"""
AI Prediction API Endpoints
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from typing import List
from datetime import datetime
from pathlib import Path

from ..db.session import get_db

logger = logging.getLogger(__name__)
from ..models.user import User
from ..models.patient import Patient
from ..models.medical_record import MedicalRecord
from ..models.prediction import Prediction, DiseaseType
from ..schemas.prediction import PredictionRequest, PredictionResponse, PredictionReview
from ..core.security import get_current_user, require_role
from ..core.cache import generate_cache_key, get_cached_response, set_cached_response, invalidate_prediction_cache
from ..services.ai_model_service import ai_model_service
from ..core.config import settings

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("doctor"))
):
    """Create a new disease risk prediction"""
    # Verify patient exists with eager loading
    result = await db.execute(
        select(Patient)
        .where(Patient.id == request.patient_id)
        .options(selectinload(Patient.medical_records))
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {request.patient_id} not found"
        )
    
    # Get latest medical record (already loaded via relationship, but we need to sort)
    medical_records = sorted(
        patient.medical_records,
        key=lambda x: x.visit_date if x.visit_date else datetime.min,
        reverse=True
    )
    medical_record = medical_records[0] if medical_records else None
    
    if not medical_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No medical records found for this patient. Please add medical data first."
        )
    
    # Prepare patient data for prediction
    from datetime import date
    age = (date.today() - patient.date_of_birth).days / 365.25
    
    patient_data = {
        'age': age,
        'gender': patient.gender.value,
        'education_years': patient.education_years or 12,
        'mmse_score': medical_record.mmse_score or 25,
        'moca_score': medical_record.moca_score or 24,
        'memory_score': medical_record.memory_score or 50,
        'attention_score': medical_record.attention_score or 50,
        'executive_function_score': medical_record.executive_function_score or 50,
        'amyloid_beta': medical_record.amyloid_beta or 600,
        'tau_protein': medical_record.tau_protein or 200,
        'dopamine_level': medical_record.dopamine_level or 100,
        'apoe_e4_status': medical_record.apoe_e4_status or False,
        'hippocampal_volume': medical_record.hippocampal_volume or 3500,
        'cortical_thickness': medical_record.cortical_thickness or 2.3,
        'ventricular_volume': medical_record.ventricular_volume or 30000,
        'white_matter_hyperintensities': medical_record.white_matter_hyperintensities or 2,
        'brain_volume_total': medical_record.brain_volume_total or 1100000,
    }
    
    # Run AI prediction
    try:
        prediction_result = await ai_model_service.predict(patient_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during prediction: {str(e)}"
        )
    
    # Create prediction record
    new_prediction = Prediction(
        patient_id=request.patient_id,
        created_by=current_user.id,
        disease_type=request.disease_type,
        alzheimer_risk_score=prediction_result['alzheimer']['risk_score'],
        alzheimer_risk_level=prediction_result['alzheimer']['risk_level'],
        alzheimer_confidence=prediction_result['alzheimer']['confidence'],
        parkinson_risk_score=prediction_result['parkinson']['risk_score'],
        parkinson_risk_level=prediction_result['parkinson']['risk_level'],
        parkinson_confidence=prediction_result['parkinson']['confidence'],
        model_version=prediction_result['model_version'],
        model_name=prediction_result['model_name'],
        input_features=patient_data,
        feature_importance=prediction_result['feature_importance'],
        attention_scores=prediction_result.get('attention_scores'),
        recommendations=prediction_result['recommendations']
    )
    
    db.add(new_prediction)
    await db.commit()
    await db.refresh(new_prediction)
    
    # Invalidate cache
    await invalidate_prediction_cache(patient_id=request.patient_id)
    
    return new_prediction


@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    request: Request,
    patient_id: int = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of predictions with optional patient filter (cached for 5 minutes)"""
    # Generate cache key
    cache_key = generate_cache_key(
        "predictions",
        request=request,
        current_user=current_user,
        patient_id=patient_id,
        skip=skip,
        limit=limit
    )
    
    # Try to get from cache
    cached_result = await get_cached_response(cache_key, expire_seconds=300)
    if cached_result is not None:
        return cached_result
    
    # Query database with eager loading to avoid N+1 queries
    query = select(Prediction).options(
        selectinload(Prediction.patient),  # Load patient relationship
        selectinload(Prediction.created_by_user)  # Load creator relationship
    )
    
    if patient_id:
        query = query.where(Prediction.patient_id == patient_id)
    
    query = query.order_by(Prediction.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    # Cache result
    await set_cached_response(cache_key, predictions, expire_seconds=300)
    
    return predictions


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    request: Request,
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get prediction by ID (cached for 10 minutes)"""
    # Generate cache key
    cache_key = generate_cache_key(
        "prediction",
        request=request,
        current_user=current_user,
        prediction_id=prediction_id
    )
    
    # Try to get from cache
    cached_result = await get_cached_response(cache_key, expire_seconds=600)
    if cached_result is not None:
        return cached_result
    
    # Query database with eager loading to avoid N+1 queries
    result = await db.execute(
        select(Prediction)
        .where(Prediction.id == prediction_id)
        .options(
            selectinload(Prediction.patient),
            selectinload(Prediction.created_by_user),
            selectinload(Prediction.patient).selectinload(Patient.medical_records)
        )
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
    
    # Cache result
    await set_cached_response(cache_key, prediction, expire_seconds=600)
    
    return prediction


@router.get("/{prediction_id}/imaging-studies")
async def get_prediction_imaging_studies(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get imaging studies associated with a prediction (via patient's latest medical record)"""
    from ..models.imaging import ImagingStudy
    
    # Get prediction with eager loading to avoid N+1 queries
    result = await db.execute(
        select(Prediction)
        .where(Prediction.id == prediction_id)
        .options(
            selectinload(Prediction.patient).selectinload(Patient.medical_records).selectinload(MedicalRecord.imaging_studies)
        )
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
    
    # Get latest medical record for patient (already loaded via relationship)
    if not prediction.patient or not prediction.patient.medical_records:
        return []
    
    medical_records = sorted(
        prediction.patient.medical_records,
        key=lambda x: x.visit_date if x.visit_date else datetime.min,
        reverse=True
    )
    medical_record = medical_records[0] if medical_records else None
    
    if not medical_record or not medical_record.imaging_studies:
        return []
    
    # Imaging studies already loaded via relationship
    studies = sorted(
        medical_record.imaging_studies,
        key=lambda x: x.study_date if x.study_date else datetime.min,
        reverse=True
    )
    
    return [
        {
            "id": study.id,
            "study_id": study.study_id,
            "modality": study.modality.value,
            "study_date": study.study_date.isoformat() if study.study_date else None,
            "study_description": study.study_description,
            "image_count": study.image_count,
            "quality_score": study.quality_score,
        }
        for study in studies
    ]


@router.post("/{prediction_id}/review", response_model=PredictionResponse)
async def review_prediction(
    prediction_id: int,
    review: PredictionReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("doctor"))
):
    """Review and approve a prediction"""
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
    
    # Update review information
    prediction.is_reviewed = review.approved
    prediction.reviewed_by = current_user.id
    prediction.reviewed_at = datetime.utcnow()
    prediction.review_notes = review.review_notes
    
    await db.commit()
    await db.refresh(prediction)
    
    # Invalidate cache
    await invalidate_prediction_cache(prediction_id=prediction_id, patient_id=prediction.patient_id)
    
    return prediction


@router.get("/{prediction_id}/explain")
async def explain_prediction(
    prediction_id: int,
    method: str = Query(default="integrated_gradients", regex="^(gradient|integrated_gradients|smoothgrad|shap)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate advanced XAI explanation for a prediction
    
    Methods:
    - gradient: Vanilla gradient saliency
    - integrated_gradients: Integrated Gradients (default, most accurate)
    - smoothgrad: SmoothGrad (noise-reduced saliency)
    - shap: SHAP values (game theory based)
    """
    # Get prediction with all relationships
    result = await db.execute(
        select(Prediction)
        .where(Prediction.id == prediction_id)
        .options(
            selectinload(Prediction.patient),
            selectinload(Prediction.patient).selectinload(Patient.medical_records)
        )
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
    
    # Get patient and medical record
    patient = prediction.patient
    medical_records = sorted(
        patient.medical_records,
        key=lambda x: x.visit_date if x.visit_date else datetime.min,
        reverse=True
    )
    medical_record = medical_records[0] if medical_records else None
    
    if not medical_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No medical record found for patient"
        )
    
    # Prepare patient data for feature extraction
    from datetime import date
    age = (date.today() - patient.date_of_birth).days / 365.25
    
    patient_data = {
        'age': age,
        'gender': patient.gender.value,
        'education_years': patient.education_years or 12,
        'mmse_score': medical_record.mmse_score or 25,
        'moca_score': medical_record.moca_score or 24,
        'memory_score': medical_record.memory_score or 50,
        'attention_score': medical_record.attention_score or 50,
        'executive_function_score': medical_record.executive_function_score or 50,
        'amyloid_beta': medical_record.amyloid_beta or 600,
        'tau_protein': medical_record.tau_protein or 200,
        'dopamine_level': medical_record.dopamine_level or 100,
        'apoe_e4_status': medical_record.apoe_e4_status or False,
        'hippocampal_volume': medical_record.hippocampal_volume or 3500,
        'cortical_thickness': medical_record.cortical_thickness or 2.3,
        'ventricular_volume': medical_record.ventricular_volume or 30000,
        'white_matter_hyperintensities': medical_record.white_matter_hyperintensities or 2,
        'brain_volume_total': medical_record.brain_volume_total or 1100000,
    }
    
    # Extract features
    features = ai_model_service.extract_features(patient_data)
    
    # Prepare prediction result
    prediction_result = {
        'alzheimer': {
            'risk_score': prediction.alzheimer_risk_score or 0,
            'risk_level': prediction.alzheimer_risk_level.value if prediction.alzheimer_risk_level else 'low',
            'confidence': prediction.alzheimer_confidence or 0
        },
        'parkinson': {
            'risk_score': prediction.parkinson_risk_score or 0,
            'risk_level': prediction.parkinson_risk_level.value if prediction.parkinson_risk_level else 'low',
            'confidence': prediction.parkinson_confidence or 0
        }
    }
    
    # Generate XAI explanation
    if ai_model_service.xai_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="XAI service not available (PyTorch required)"
        )
    
    try:
        explanation = ai_model_service.xai_service.explain_prediction(
            features,
            prediction_result,
            ai_model_service.feature_names,
            method=method
        )
        
        return {
            'prediction_id': prediction_id,
            'method': method,
            'explanation': explanation,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating XAI explanation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating explanation: {str(e)}"
        )


@router.get("/{prediction_id}/export/pdf")
async def export_prediction_pdf(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export prediction as PDF report"""
    # Get prediction with all relationships
    result = await db.execute(
        select(Prediction)
        .where(Prediction.id == prediction_id)
        .options(
            selectinload(Prediction.patient),
            selectinload(Prediction.created_by_user),
            selectinload(Prediction.patient).selectinload(Patient.medical_records)
        )
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with ID {prediction_id} not found"
        )
    
    # Generate PDF report
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from io import BytesIO
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.75*inch, leftMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        elements.append(Paragraph("NeuroPredict-AI Prediction Report", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Patient Information
        elements.append(Paragraph("Patient Information", styles['Heading2']))
        patient_data = [
            ["Patient ID:", prediction.patient.patient_id],
            ["Name:", f"{prediction.patient.first_name} {prediction.patient.last_name}"],
            ["Date of Birth:", prediction.patient.date_of_birth.strftime("%Y-%m-%d") if prediction.patient.date_of_birth else "N/A"],
            ["Gender:", prediction.patient.gender.value.capitalize()],
        ]
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(patient_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Prediction Results
        elements.append(Paragraph("Prediction Results", styles['Heading2']))
        
        # Alzheimer's Prediction
        if prediction.alzheimer_risk_score is not None:
            alzheimer_data = [
                ["Disease:", "Alzheimer's Disease"],
                ["Risk Score:", f"{prediction.alzheimer_risk_score:.2%}"],
                ["Risk Level:", prediction.alzheimer_risk_level.value.capitalize() if prediction.alzheimer_risk_level else "N/A"],
                ["Confidence:", f"{prediction.alzheimer_confidence:.2%}" if prediction.alzheimer_confidence else "N/A"],
            ]
            alzheimer_table = Table(alzheimer_data, colWidths=[2*inch, 4*inch])
            alzheimer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(alzheimer_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Parkinson's Prediction
        if prediction.parkinson_risk_score is not None:
            parkinson_data = [
                ["Disease:", "Parkinson's Disease"],
                ["Risk Score:", f"{prediction.parkinson_risk_score:.2%}"],
                ["Risk Level:", prediction.parkinson_risk_level.value.capitalize() if prediction.parkinson_risk_level else "N/A"],
                ["Confidence:", f"{prediction.parkinson_confidence:.2%}" if prediction.parkinson_confidence else "N/A"],
            ]
            parkinson_table = Table(parkinson_data, colWidths=[2*inch, 4*inch])
            parkinson_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(parkinson_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        if prediction.recommendations:
            elements.append(Paragraph("Clinical Recommendations", styles['Heading2']))
            recommendations_style = ParagraphStyle(
                'CustomRecommendations',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                spaceAfter=12
            )
            for line in prediction.recommendations.split('\n'):
                if line.strip():
                    elements.append(Paragraph(line.strip(), recommendations_style))
            elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            'CustomFooter',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer_text = f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | Model: {prediction.model_name or 'N/A'} v{prediction.model_version or 'N/A'}"
        elements.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF data
        buffer.seek(0)
        pdf_data = buffer.read()
        buffer.close()
        
        # Save PDF to file (optional)
        reports_dir = Path(settings.UPLOAD_DIR) / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = reports_dir / f"prediction_{prediction_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path.write_bytes(pdf_data)
        
        # Update prediction with report path
        prediction.report_path = str(pdf_path)
        await db.commit()
        
        # Return PDF as response
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="prediction_{prediction_id}_report.pdf"'
            }
        )
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF generation library (reportlab) not installed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF report: {str(e)}"
        )

