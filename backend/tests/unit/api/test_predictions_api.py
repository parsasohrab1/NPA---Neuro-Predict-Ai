"""
Unit Tests for Predictions API
"""
import pytest
from httpx import AsyncClient


class TestCreatePrediction:
    """Tests for creating predictions"""
    
    @pytest.mark.asyncio
    async def test_create_prediction_success(
        self, client: AsyncClient, auth_headers, test_patient, test_medical_record
    ):
        """Test successful prediction creation"""
        response = await client.post(
            "/api/v1/predictions",
            json={
                "patient_id": test_patient.id,
                "disease_type": "alzheimer"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "patient_id" in data
        assert "alzheimer" in data
        assert "parkinson" in data
        assert "feature_importance" in data
        assert "recommendations" in data
    
    @pytest.mark.asyncio
    async def test_create_prediction_patient_not_found(
        self, client: AsyncClient, auth_headers
    ):
        """Test prediction with nonexistent patient"""
        response = await client.post(
            "/api/v1/predictions",
            json={
                "patient_id": 99999,
                "disease_type": "alzheimer"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_prediction_no_medical_record(
        self, client: AsyncClient, auth_headers, test_patient, test_db
    ):
        """Test prediction without medical record"""
        # Delete medical record if exists
        from app.models.medical_record import MedicalRecord
        from sqlalchemy import select
        
        result = await test_db.execute(
            select(MedicalRecord).where(MedicalRecord.patient_id == test_patient.id)
        )
        records = result.scalars().all()
        for record in records:
            await test_db.delete(record)
        await test_db.commit()
        
        response = await client.post(
            "/api/v1/predictions",
            json={
                "patient_id": test_patient.id,
                "disease_type": "alzheimer"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_create_prediction_unauthorized(self, client: AsyncClient, test_patient):
        """Test prediction creation without authentication"""
        response = await client.post(
            "/api/v1/predictions",
            json={
                "patient_id": test_patient.id,
                "disease_type": "alzheimer"
            }
        )
        
        assert response.status_code == 401


class TestGetPredictions:
    """Tests for getting predictions"""
    
    @pytest.mark.asyncio
    async def test_get_predictions_list(
        self, client: AsyncClient, auth_headers, test_prediction
    ):
        """Test getting list of predictions"""
        response = await client.get(
            "/api/v1/predictions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
    
    @pytest.mark.asyncio
    async def test_get_prediction_by_id(
        self, client: AsyncClient, auth_headers, test_prediction
    ):
        """Test getting prediction by ID"""
        response = await client.get(
            f"/api/v1/predictions/{test_prediction.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_prediction.id
        assert "patient_id" in data
        assert "alzheimer" in data
    
    @pytest.mark.asyncio
    async def test_get_prediction_not_found(
        self, client: AsyncClient, auth_headers
    ):
        """Test getting nonexistent prediction"""
        response = await client.get(
            "/api/v1/predictions/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestReviewPrediction:
    """Tests for reviewing predictions"""
    
    @pytest.mark.asyncio
    async def test_review_prediction_success(
        self, client: AsyncClient, auth_headers, test_prediction
    ):
        """Test successful prediction review"""
        response = await client.post(
            f"/api/v1/predictions/{test_prediction.id}/review",
            json={
                "review_notes": "Reviewed and confirmed",
                "is_reviewed": True
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_reviewed"] is True
        assert "review_notes" in data

