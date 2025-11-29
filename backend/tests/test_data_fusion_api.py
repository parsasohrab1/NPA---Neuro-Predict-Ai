"""
Integration Tests for Data Fusion API Endpoints
Tests the complete API workflow including request/response handling
"""
import pytest
from datetime import date, datetime
from httpx import AsyncClient

from app.models.patient import Patient, Gender
from app.models.medical_record import MedicalRecord
from app.models.data_fusion_report import DataFusionReport


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestDataFusionAPI:
    """Test Data Fusion API endpoints"""
    
    @pytest.mark.asyncio
    async def test_generate_fusion_report_endpoint(
        self, test_client: AsyncClient, sample_patient: Patient, sample_medical_record: MedicalRecord
    ):
        """Test POST /api/v1/data-fusion/generate endpoint"""
        # Create request payload
        payload = {
            "patient_id": sample_patient.id,
            "medical_record_id": sample_medical_record.id
        }
        
        response = await test_client.post("/api/v1/data-fusion/generate", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert "patient_id" in data
        assert "medical_record_id" in data
        assert "cognitive_modality_score" in data
        assert "biomarker_modality_score" in data
        assert "imaging_modality_score" in data
        assert "integrated_fusion_score" in data
        assert "executive_summary" in data
        assert "detailed_findings" in data
        assert "risk_assessment" in data
        assert "recommendations" in data
        assert "algorithm_version" in data
        
        # Check score ranges
        assert 0 <= data["cognitive_modality_score"] <= 100
        assert 0 <= data["biomarker_modality_score"] <= 100
        assert 0 <= data["imaging_modality_score"] <= 100
        assert 0 <= data["integrated_fusion_score"] <= 100
    
    @pytest.mark.asyncio
    async def test_generate_fusion_report_without_medical_record_id(
        self, test_client: AsyncClient, sample_patient: Patient, sample_medical_record: MedicalRecord
    ):
        """Test generating report using latest medical record"""
        payload = {
            "patient_id": sample_patient.id
            # medical_record_id not provided
        }
        
        response = await test_client.post("/api/v1/data-fusion/generate", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["patient_id"] == sample_patient.id
        assert data["medical_record_id"] == sample_medical_record.id
    
    @pytest.mark.asyncio
    async def test_generate_fusion_report_patient_not_found(
        self, test_client: AsyncClient
    ):
        """Test error handling for non-existent patient"""
        payload = {
            "patient_id": 99999,
            "medical_record_id": 1
        }
        
        response = await test_client.post("/api/v1/data-fusion/generate", json=payload)
        
        assert response.status_code == 500  # Should return error
        # The service raises ValueError which becomes 500
    
    @pytest.mark.asyncio
    async def test_generate_fusion_report_medical_record_not_found(
        self, test_client: AsyncClient, sample_patient: Patient
    ):
        """Test error handling for non-existent medical record"""
        payload = {
            "patient_id": sample_patient.id,
            "medical_record_id": 99999
        }
        
        response = await test_client.post("/api/v1/data-fusion/generate", json=payload)
        
        assert response.status_code == 500  # Should return error
    
    @pytest.mark.asyncio
    async def test_get_patient_fusion_reports(
        self, test_client: AsyncClient, test_session, sample_patient: Patient, sample_medical_record: MedicalRecord
    ):
        """Test GET /api/v1/data-fusion/patient/{patient_id} endpoint"""
        # First generate a report
        from app.services.data_fusion_service import DataFusionService
        report = await DataFusionService.generate_fusion_report(
            patient_id=sample_patient.id,
            medical_record_id=sample_medical_record.id,
            db=test_session
        )
        test_session.add(report)
        await test_session.commit()
        
        # Get reports
        response = await test_client.get(f"/api/v1/data-fusion/patient/{sample_patient.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["patient_id"] == sample_patient.id
    
    @pytest.mark.asyncio
    async def test_get_patient_fusion_reports_empty(
        self, test_client: AsyncClient, sample_patient: Patient
    ):
        """Test getting reports for patient with no reports"""
        response = await test_client.get(f"/api/v1/data-fusion/patient/{sample_patient.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_fusion_report_by_id(
        self, test_client: AsyncClient, test_session, sample_patient: Patient, sample_medical_record: MedicalRecord
    ):
        """Test GET /api/v1/data-fusion/{report_id} endpoint"""
        # Generate and save report
        from app.services.data_fusion_service import DataFusionService
        report = await DataFusionService.generate_fusion_report(
            patient_id=sample_patient.id,
            medical_record_id=sample_medical_record.id,
            db=test_session
        )
        test_session.add(report)
        await test_session.commit()
        await test_session.refresh(report)
        
        # Get report by ID
        response = await test_client.get(f"/api/v1/data-fusion/{report.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report.id
        assert data["patient_id"] == sample_patient.id
    
    @pytest.mark.asyncio
    async def test_get_fusion_report_not_found(self, test_client: AsyncClient):
        """Test error handling for non-existent report"""
        response = await test_client.get("/api/v1/data-fusion/99999")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_fusion_report_algorithm_version(
        self, test_client: AsyncClient, sample_patient: Patient, sample_medical_record: MedicalRecord, monkeypatch
    ):
        """Test that algorithm version is correctly reported"""
        # Mock DL model to be loaded
        from unittest.mock import Mock
        from app.services.data_fusion_model_service import DataFusionModelService
        
        mock_service = Mock(spec=DataFusionModelService)
        mock_service.is_loaded.return_value = True
        mock_service.predict_scores.return_value = {
            'cognitive_score': 65.0,
            'biomarker_score': 60.0,
            'imaging_score': 62.0,
            'cognitive_confidence': 0.85,
            'biomarker_confidence': 0.80,
            'imaging_confidence': 0.82,
            'cognitive_biomarker_correlation': 0.75,
            'cognitive_imaging_correlation': 0.78,
            'biomarker_imaging_correlation': 0.72,
            'integrated_fusion_score': 62.5,
            'alzheimer_fusion_score': 55.0,
            'parkinson_fusion_score': 35.0,
            'alzheimer_concordance': 70.0,
            'alzheimer_alignment': 68.0,
            'alzheimer_hippo_corr': 72.0,
            'parkinson_concordance': 50.0,
            'parkinson_alignment': 45.0,
            'parkinson_corr': 48.0,
        }
        
        monkeypatch.setattr(
            'app.services.data_fusion_service.get_data_fusion_model_service',
            lambda: mock_service
        )
        
        payload = {
            "patient_id": sample_patient.id,
            "medical_record_id": sample_medical_record.id
        }
        
        response = await test_client.post("/api/v1/data-fusion/generate", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["algorithm_version"] == "2.0.0-DL"
    
    @pytest.mark.asyncio
    async def test_fusion_report_manual_algorithm_version(
        self, test_client: AsyncClient, sample_patient: Patient, sample_medical_record: MedicalRecord, monkeypatch
    ):
        """Test that manual algorithm version is used when DL model not available"""
        # Mock DL model to be not loaded
        from unittest.mock import Mock
        from app.services.data_fusion_model_service import DataFusionModelService
        
        mock_service = Mock(spec=DataFusionModelService)
        mock_service.is_loaded.return_value = False
        
        monkeypatch.setattr(
            'app.services.data_fusion_service.get_data_fusion_model_service',
            lambda: mock_service
        )
        
        payload = {
            "patient_id": sample_patient.id,
            "medical_record_id": sample_medical_record.id
        }
        
        response = await test_client.post("/api/v1/data-fusion/generate", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["algorithm_version"] == "1.0.0"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestDataFusionPerformance:
    """Test performance characteristics of data fusion"""
    
    @pytest.mark.asyncio
    async def test_report_generation_performance(
        self, test_client: AsyncClient, sample_patient: Patient, sample_medical_record: MedicalRecord
    ):
        """Test that report generation completes in reasonable time"""
        import time
        
        payload = {
            "patient_id": sample_patient.id,
            "medical_record_id": sample_medical_record.id
        }
        
        start_time = time.time()
        response = await test_client.post("/api/v1/data-fusion/generate", json=payload)
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 201
        assert elapsed_time < 5.0  # Should complete in under 5 seconds
        
        data = response.json()
        assert data["processing_time_ms"] > 0
        assert data["processing_time_ms"] < 5000  # Processing time should be reasonable


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestDataFusionValidation:
    """Test input validation and error handling"""
    
    @pytest.mark.asyncio
    async def test_invalid_payload_missing_patient_id(self, test_client: AsyncClient):
        """Test error handling for missing patient_id"""
        payload = {
            "medical_record_id": 1
        }
        
        response = await test_client.post("/api/v1/data-fusion/generate", json=payload)
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_invalid_payload_wrong_types(self, test_client: AsyncClient):
        """Test error handling for wrong data types"""
        payload = {
            "patient_id": "not_a_number",
            "medical_record_id": "also_not_a_number"
        }
        
        response = await test_client.post("/api/v1/data-fusion/generate", json=payload)
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_empty_payload(self, test_client: AsyncClient):
        """Test error handling for empty payload"""
        response = await test_client.post("/api/v1/data-fusion/generate", json={})
        
        # Should return validation error
        assert response.status_code in [400, 422]

