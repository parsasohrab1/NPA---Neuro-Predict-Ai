"""
Query Optimization Service
سرویس بهینه‌سازی Query ها
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
import logging

from ..core.cache import cache_service

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Service for optimizing database queries"""
    
    @staticmethod
    async def get_patient_with_records_optimized(
        session: AsyncSession,
        patient_id: int,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get patient with medical records (optimized with eager loading)
        
        Args:
            session: Database session
            patient_id: Patient ID
            use_cache: Whether to use cache
        
        Returns:
            Patient data with records
        """
        # Try cache first
        if use_cache:
            cached = await cache_service.get("patient", f"full:{patient_id}")
            if cached:
                return cached
        
        from ...models.patient import Patient
        from ...models.medical_record import MedicalRecord
        
        # Use eager loading to avoid N+1 queries
        result = await session.execute(
            select(Patient)
            .options(selectinload(Patient.medical_records))
            .where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()
        
        if not patient:
            return None
        
        # Convert to dict
        patient_data = {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            "gender": patient.gender,
            "email": patient.email,
            "phone": patient.phone,
            "medical_records": [
                {
                    "id": record.id,
                    "visit_date": record.visit_date.isoformat() if record.visit_date else None,
                    "mmse_score": record.mmse_score,
                    "moca_score": record.moca_score
                }
                for record in patient.medical_records
            ]
        }
        
        # Cache result
        if use_cache:
            await cache_service.set("patient", f"full:{patient_id}", patient_data, ttl=300)
        
        return patient_data
    
    @staticmethod
    async def get_predictions_paginated(
        session: AsyncSession,
        patient_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get predictions with pagination (optimized)
        
        Args:
            session: Database session
            patient_id: Optional patient ID filter
            page: Page number
            page_size: Items per page
            use_cache: Whether to use cache
        
        Returns:
            Paginated predictions
        """
        from ...models.prediction import Prediction
        
        # Cache key
        cache_key = f"predictions:{patient_id}:{page}:{page_size}"
        
        if use_cache:
            cached = await cache_service.get("prediction", cache_key)
            if cached:
                return cached
        
        # Build query
        query = select(Prediction)
        
        if patient_id:
            query = query.where(Prediction.patient_id == patient_id)
        
        # Get total count
        count_query = select(func.count()).select_from(Prediction)
        if patient_id:
            count_query = count_query.where(Prediction.patient_id == patient_id)
        
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        offset = (page - 1) * page_size
        query = query.order_by(Prediction.created_at.desc()).limit(page_size).offset(offset)
        
        result = await session.execute(query)
        predictions = result.scalars().all()
        
        # Convert to dict
        predictions_data = [
            {
                "id": pred.id,
                "patient_id": pred.patient_id,
                "disease_type": pred.disease_type,
                "risk_level": pred.risk_level,
                "risk_score": pred.risk_score,
                "confidence": pred.confidence,
                "created_at": pred.created_at.isoformat() if pred.created_at else None
            }
            for pred in predictions
        ]
        
        response = {
            "items": predictions_data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        # Cache result (shorter TTL for paginated results)
        if use_cache:
            await cache_service.set("prediction", cache_key, response, ttl=60)
        
        return response
    
    @staticmethod
    async def bulk_get_patients(
        session: AsyncSession,
        patient_ids: List[int],
        use_cache: bool = True
    ) -> Dict[int, Dict[str, Any]]:
        """
        Get multiple patients efficiently (bulk operation)
        
        Args:
            session: Database session
            patient_ids: List of patient IDs
            use_cache: Whether to use cache
        
        Returns:
            Dictionary mapping patient_id to patient data
        """
        from ...models.patient import Patient
        
        result = {}
        uncached_ids = []
        
        # Check cache for each patient
        if use_cache:
            for patient_id in patient_ids:
                cached = await cache_service.get("patient", str(patient_id))
                if cached:
                    result[patient_id] = cached
                else:
                    uncached_ids.append(patient_id)
        else:
            uncached_ids = patient_ids
        
        # Fetch uncached patients
        if uncached_ids:
            query = select(Patient).where(Patient.id.in_(uncached_ids))
            query_result = await session.execute(query)
            patients = query_result.scalars().all()
            
            for patient in patients:
                patient_data = {
                    "id": patient.id,
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                    "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                    "gender": patient.gender,
                    "email": patient.email,
                    "phone": patient.phone
                }
                result[patient.id] = patient_data
                
                # Cache individual patient
                if use_cache:
                    await cache_service.set("patient", str(patient.id), patient_data, ttl=300)
        
        return result

