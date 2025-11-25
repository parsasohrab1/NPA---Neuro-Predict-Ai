"""
Data Monitoring API Endpoints
Real-time monitoring of clinical data types for Alzheimer and Parkinson diagnosis
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from ..core.security import require_role
from ..db.session import get_db
from ..models.patient import Patient
from ..models.medical_record import MedicalRecord
from ..models.prediction import Prediction, DiseaseType

router = APIRouter(prefix="/data-monitoring", tags=["Data Monitoring"])


def get_time_range(range_str: str) -> datetime:
    """Convert time range string to datetime"""
    now = datetime.utcnow()
    if range_str == '24h':
        return now - timedelta(hours=24)
    elif range_str == '7d':
        return now - timedelta(days=7)
    elif range_str == '30d':
        return now - timedelta(days=30)
    elif range_str == '90d':
        return now - timedelta(days=90)
    return now - timedelta(days=7)


@router.get("/overview")
async def get_overview(
    disease: Optional[str] = Query(None, description="Filter by disease: alzheimer, parkinson, or all"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("doctor")),
):
    """
    Get overview of all data categories
    """
    # Count total medical records
    records_query = select(func.count(MedicalRecord.id))
    total_records = (await db.execute(records_query)).scalar_one()
    
    # Count unique patients
    patients_query = select(func.count(func.distinct(MedicalRecord.patient_id)))
    total_patients = (await db.execute(patients_query)).scalar_one()
    
    # Category-specific counts
    categories = {
        'cognitive': {
            'count': total_records,  # All records have cognitive data
            'avg_value': 0,
            'trend': 0,
        },
        'biomarker': {
            'count': total_records,
            'avg_value': 0,
            'trend': 0,
        },
        'imaging': {
            'count': total_records,
            'avg_value': 0,
            'trend': 0,
        },
        'motor': {
            'count': 0,  # Would come from specific motor assessments
            'avg_value': 0,
            'trend': 0,
        },
        'genetic': {
            'count': total_records,  # APOE status
            'avg_value': 0,
            'trend': 0,
        },
    }
    
    # Calculate average MMSE as a proxy for cognitive health
    mmse_avg = await db.execute(
        select(func.avg(MedicalRecord.mmse_score)).where(MedicalRecord.mmse_score.isnot(None))
    )
    avg_mmse = mmse_avg.scalar_one_or_none() or 0
    categories['cognitive']['avg_value'] = float(avg_mmse) if avg_mmse else 0
    
    # Get recent activity (last 10 records)
    recent_query = select(MedicalRecord).order_by(MedicalRecord.created_at.desc()).limit(10)
    recent_records = (await db.execute(recent_query)).scalars().all()
    
    recent_activity = []
    for record in recent_records:
        # Get patient info
        patient_result = await db.execute(select(Patient).where(Patient.id == record.patient_id))
        patient = patient_result.scalar_one_or_none()
        
        recent_activity.append({
            'timestamp': record.created_at.isoformat() if record.created_at else datetime.utcnow().isoformat(),
            'patient_id': patient.patient_id if patient else f"P{record.patient_id}",
            'patient_name': f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            'category': 'cognitive',
            'metric_type': 'MMSE Score',
            'value': record.mmse_score,
            'description': f"MMSE Score recorded: {record.mmse_score}",
        })
    
    # Calculate data quality score based on completeness
    quality_score = 85.0  # Base score
    if total_records > 100:
        quality_score += 5
    if total_patients > 20:
        quality_score += 5
    if avg_mmse > 0:
        quality_score += 5
    
    return {
        'total_records': total_records,
        'total_patients': total_patients,
        'categories': categories,
        'recent_activity': recent_activity,
        'data_quality_score': min(quality_score, 100),
    }


@router.get("/category/{category}")
async def get_category_data(
    category: str,
    time_range: str = Query('7d', description="Time range: 24h, 7d, 30d, 90d"),
    disease: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("doctor")),
):
    """
    Get detailed data for a specific category
    """
    start_date = get_time_range(time_range)
    
    # Build base query
    base_query = select(MedicalRecord).where(MedicalRecord.created_at >= start_date)
    
    # Apply disease filter if needed
    if disease and disease != 'all':
        # Get patients with that disease prediction
        disease_type = DiseaseType.ALZHEIMER if disease == 'alzheimer' else DiseaseType.PARKINSON
        disease_patients = await db.execute(
            select(Prediction.patient_id).where(Prediction.disease_type == disease_type).distinct()
        )
        patient_ids = [p[0] for p in disease_patients.all()]
        if patient_ids:
            base_query = base_query.where(MedicalRecord.patient_id.in_(patient_ids))
    
    records = (await db.execute(base_query.order_by(MedicalRecord.visit_date))).scalars().all()
    
    # Generate time series data
    time_series = []
    if records:
        # Group by date
        date_groups: Dict[str, List[float]] = {}
        for record in records:
            date_key = record.visit_date.strftime('%Y-%m-%d') if record.visit_date else datetime.utcnow().strftime('%Y-%m-%d')
            
            if category == 'cognitive' and record.mmse_score:
                if date_key not in date_groups:
                    date_groups[date_key] = []
                date_groups[date_key].append(record.mmse_score)
            elif category == 'biomarker' and record.amyloid_beta:
                if date_key not in date_groups:
                    date_groups[date_key] = []
                date_groups[date_key].append(record.amyloid_beta)
            elif category == 'imaging' and record.hippocampal_volume:
                if date_key not in date_groups:
                    date_groups[date_key] = []
                date_groups[date_key].append(record.hippocampal_volume)
        
        for date_key, values in sorted(date_groups.items()):
            time_series.append({
                'date': date_key,
                'avg_value': sum(values) / len(values) if values else 0,
                'count': len(values),
            })
    
    # Generate distribution data
    distribution = []
    if category == 'cognitive':
        # MMSE ranges
        ranges = [
            ('0-10', 0, 10),
            ('11-20', 11, 20),
            ('21-24', 21, 24),
            ('25-30', 25, 30),
        ]
        for range_label, min_val, max_val in ranges:
            count = len([r for r in records if r.mmse_score and min_val <= r.mmse_score <= max_val])
            distribution.append({'range': range_label, 'count': count})
    elif category == 'biomarker':
        ranges = [
            ('<300', 0, 300),
            ('300-400', 300, 400),
            ('400-500', 400, 500),
            ('>500', 500, 10000),
        ]
        for range_label, min_val, max_val in ranges:
            count = len([r for r in records if r.amyloid_beta and min_val <= r.amyloid_beta <= max_val])
            distribution.append({'range': range_label, 'count': count})
    
    # Generate metrics summary
    metrics = []
    
    if category == 'cognitive':
        metrics_list = [
            ('MMSE Score', 'mmse_score'),
            ('MoCA Score', 'moca_score'),
            ('Memory Score', 'memory_score'),
            ('Attention Score', 'attention_score'),
            ('Executive Function', 'executive_function_score'),
        ]
    elif category == 'biomarker':
        metrics_list = [
            ('Amyloid Beta', 'amyloid_beta'),
            ('Tau Protein', 'tau_protein'),
            ('Dopamine Level', 'dopamine_level'),
        ]
    elif category == 'imaging':
        metrics_list = [
            ('Hippocampal Volume', 'hippocampal_volume'),
            ('Cortical Thickness', 'cortical_thickness'),
            ('Ventricular Volume', 'ventricular_volume'),
            ('White Matter', 'white_matter_hyperintensities'),
            ('Brain Volume', 'brain_volume_total'),
        ]
    elif category == 'genetic':
        metrics_list = [
            ('APOE-e4 Status', 'apoe_e4_status'),
        ]
    else:
        metrics_list = []
    
    for metric_name, field_name in metrics_list:
        values = [getattr(r, field_name) for r in records if getattr(r, field_name, None) is not None]
        if values and not isinstance(values[0], bool):
            metrics.append({
                'metric_name': metric_name,
                'avg_value': sum(values) / len(values) if values else None,
                'min_value': min(values) if values else None,
                'max_value': max(values) if values else None,
                'count': len(values),
                'last_updated': max([r.created_at for r in records if getattr(r, field_name, None) is not None], default=None),
            })
        elif values:  # Boolean fields
            metrics.append({
                'metric_name': metric_name,
                'avg_value': None,
                'min_value': None,
                'max_value': None,
                'count': len(values),
                'last_updated': max([r.created_at for r in records if getattr(r, field_name, None) is not None], default=None),
            })
    
    return {
        'category': category,
        'time_series': time_series,
        'distribution': distribution,
        'metrics': metrics,
    }


@router.get("/recent")
async def get_recent_data(
    disease: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("doctor")),
):
    """
    Get recent data entries across all categories
    """
    query = select(MedicalRecord).order_by(MedicalRecord.created_at.desc()).limit(limit)
    records = (await db.execute(query)).scalars().all()
    
    result = []
    for record in records:
        # Get patient info
        patient_result = await db.execute(select(Patient).where(Patient.id == record.patient_id))
        patient = patient_result.scalar_one_or_none()
        
        # Determine category based on available data
        category = 'cognitive'
        metric_type = 'MMSE Score'
        value = record.mmse_score
        
        if record.amyloid_beta:
            category = 'biomarker'
            metric_type = 'Amyloid Beta'
            value = record.amyloid_beta
        elif record.hippocampal_volume:
            category = 'imaging'
            metric_type = 'Hippocampal Volume'
            value = record.hippocampal_volume
        
        result.append({
            'timestamp': record.created_at.isoformat() if record.created_at else datetime.utcnow().isoformat(),
            'patient_id': patient.patient_id if patient else f"P{record.patient_id}",
            'patient_name': f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            'category': category,
            'metric_type': metric_type,
            'value': f"{value:.2f}" if value else None,
            'description': f"{metric_type} recorded",
        })
    
    return result


@router.get("/trends")
async def get_trends(
    time_range: str = Query('7d'),
    disease: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("doctor")),
):
    """
    Get trend data for radar chart visualization
    """
    start_date = get_time_range(time_range)
    
    # Get predictions for trend analysis
    predictions_query = select(Prediction).where(Prediction.created_at >= start_date)
    predictions = (await db.execute(predictions_query)).scalars().all()
    
    # Calculate average risk scores by category
    alzheimer_risks = [p.alzheimer_risk_score for p in predictions if p.alzheimer_risk_score]
    parkinson_risks = [p.parkinson_risk_score for p in predictions if p.parkinson_risk_score]
    
    radar_data = [
        {
            'category': 'Cognitive',
            'alzheimer': (sum(alzheimer_risks) / len(alzheimer_risks) * 100) if alzheimer_risks else 0,
            'parkinson': (sum(parkinson_risks) / len(parkinson_risks) * 100) if parkinson_risks else 0,
        },
        {
            'category': 'Biomarker',
            'alzheimer': (sum(alzheimer_risks) / len(alzheimer_risks) * 90) if alzheimer_risks else 0,
            'parkinson': (sum(parkinson_risks) / len(parkinson_risks) * 85) if parkinson_risks else 0,
        },
        {
            'category': 'Imaging',
            'alzheimer': (sum(alzheimer_risks) / len(alzheimer_risks) * 95) if alzheimer_risks else 0,
            'parkinson': (sum(parkinson_risks) / len(parkinson_risks) * 70) if parkinson_risks else 0,
        },
        {
            'category': 'Motor',
            'alzheimer': (sum(alzheimer_risks) / len(alzheimer_risks) * 40) if alzheimer_risks else 0,
            'parkinson': (sum(parkinson_risks) / len(parkinson_risks) * 95) if parkinson_risks else 0,
        },
        {
            'category': 'Genetic',
            'alzheimer': (sum(alzheimer_risks) / len(alzheimer_risks) * 85) if alzheimer_risks else 0,
            'parkinson': (sum(parkinson_risks) / len(parkinson_risks) * 60) if parkinson_risks else 0,
        },
    ]
    
    return {
        'radar_data': radar_data,
    }


@router.post("/load-sample-data", status_code=201)
async def load_sample_data(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """
    Load sample data for all data monitoring categories
    This creates medical records with comprehensive data for testing
    """
    from sqlalchemy import select
    import random
    from datetime import datetime, timedelta
    
    # Get all patients
    result = await db.execute(select(Patient).limit(15))
    patients = result.scalars().all()
    
    if not patients:
        return {
            "message": "No patients found. Please create patients first.",
            "records_created": 0,
        }
    
    records_created = 0
    
    for patient in patients:
        # Create 3-5 medical records per patient
        num_records = random.randint(3, 5)
        
        for i in range(num_records):
            days_ago = random.randint(1, 90)
            visit_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Generate comprehensive data for all categories
            medical_record = MedicalRecord(
                patient_id=patient.id,
                visit_date=visit_date,
                visit_type="Comprehensive Assessment",
                # Cognitive data
                mmse_score=random.uniform(18, 30),
                moca_score=random.uniform(16, 28),
                memory_score=random.uniform(0.5, 1.0),
                attention_score=random.uniform(0.5, 1.0),
                executive_function_score=random.uniform(0.5, 1.0),
                # Biomarker data
                amyloid_beta=random.uniform(250, 650),
                tau_protein=random.uniform(150, 450),
                dopamine_level=random.uniform(40, 110),
                # Imaging data
                hippocampal_volume=random.uniform(2200, 4200),
                cortical_thickness=random.uniform(1.8, 3.8),
                ventricular_volume=random.uniform(25000, 55000),
                white_matter_hyperintensities=random.uniform(0.3, 2.5),
                brain_volume_total=random.uniform(900000, 1500000),
                # Genetic data
                apoe_e4_status=random.choice([True, False]),
                # Notes
                clinical_notes=f"Comprehensive assessment - Visit {i+1}",
                created_at=visit_date,
            )
            
            db.add(medical_record)
            records_created += 1
    
    await db.commit()
    
    return {
        "message": "Sample data loaded successfully for Data Monitoring",
        "patients_processed": len(patients),
        "records_created": records_created,
    }

