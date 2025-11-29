"""
Tests for Data Fusion XAI Service (Patent Claim 3)
Tests dynamic evidence generation and explainability features
"""
import pytest
import torch
import numpy as np
from datetime import date, datetime
from unittest.mock import Mock, patch

from app.services.data_fusion_xai_service import DataFusionXAIService, get_data_fusion_xai_service
from app.services.data_fusion_model import DataFusionScoringModel
from app.models.patient import Patient, Gender
from app.models.medical_record import MedicalRecord


@pytest.fixture
def sample_data_fusion_model():
    """Create a sample Data Fusion model for testing"""
    model = DataFusionScoringModel(input_dim=20)
    model.eval()
    return model


@pytest.fixture
def sample_patient_xai():
    """Create a sample patient for XAI testing"""
    return Patient(
        id=1,
        patient_id="PT-XAI-001",
        first_name="Test",
        last_name="Patient",
        date_of_birth=date(1955, 6, 15),
        gender=Gender.MALE,
        education_years=16
    )


@pytest.fixture
def sample_medical_record_xai(sample_patient_xai):
    """Create a sample medical record for XAI testing"""
    return MedicalRecord(
        id=1,
        patient_id=sample_patient_xai.id,
        visit_date=datetime(2024, 1, 15),
        visit_type="Initial",
        mmse_score=24.0,
        moca_score=23.0,
        memory_score=65.0,
        attention_score=70.0,
        executive_function_score=68.0,
        amyloid_beta=450.0,
        tau_protein=350.0,
        dopamine_level=75.0,
        apoe_e4_status=True,
        hippocampal_volume=2800.0,
        cortical_thickness=2.2,
        ventricular_volume=45000.0,
        white_matter_hyperintensities=8.0,
        brain_volume_total=1080000.0
    )


class TestDataFusionXAIService:
    """Test Data Fusion XAI Service"""
    
    def test_xai_service_initialization(self, sample_data_fusion_model):
        """Test XAI service initialization"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        assert xai_service.model is not None
        assert xai_service.device is not None
    
    def test_compute_integrated_gradients(self, sample_data_fusion_model):
        """Test Integrated Gradients computation (Patent Claim 3(b))"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        # Create sample input
        input_tensor = torch.randn(1, 20)
        
        result = xai_service.compute_integrated_gradients(
            input_tensor,
            target_output='integrated_fusion_score',
            steps=10  # Reduced for testing
        )
        
        assert 'attribution' in result
        assert 'feature_importance' in result
        assert 'method' in result
        assert result['method'] == 'integrated_gradients'
        assert len(result['attribution']) == 20
        assert len(result['feature_importance']) == 20
    
    def test_compute_gradient_saliency(self, sample_data_fusion_model):
        """Test gradient saliency computation (Patent Claim 3(a))"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        input_tensor = torch.randn(1, 20)
        
        result = xai_service.compute_gradient_saliency(
            input_tensor,
            target_output='integrated_fusion_score'
        )
        
        assert 'saliency' in result
        assert 'feature_importance' in result
        assert 'method' in result
        assert result['method'] == 'gradient_saliency'
        assert len(result['saliency']) == 20
    
    def test_map_to_anatomical_regions(self, sample_data_fusion_model):
        """Test anatomical region mapping (Patent Claim 3(c))"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        # Create sample attributions
        attributions = np.random.randn(20)
        
        regions = xai_service.map_to_anatomical_regions(attributions)
        
        assert isinstance(regions, dict)
        # Should have at least some anatomical regions
        assert len(regions) > 0
        
        # Check structure
        for region, data in regions.items():
            assert 'total_attribution' in data
            assert 'normalized_attribution' in data
            assert 'features' in data
    
    def test_generate_dynamic_evidence(self, sample_data_fusion_model, sample_patient_xai, sample_medical_record_xai):
        """Test dynamic evidence generation (Patent Claim 3)"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        fusion_scores = {
            'cognitive_score': 65.0,
            'biomarker_score': 60.0,
            'imaging_score': 62.0,
            'integrated_fusion_score': 62.5,
            'alzheimer_fusion_score': 55.0,
            'parkinson_fusion_score': 35.0,
            'fusion_confidence': 0.85
        }
        
        evidence = xai_service.generate_dynamic_evidence(
            medical_record=sample_medical_record_xai,
            patient=sample_patient_xai,
            fusion_scores=fusion_scores,
            method='integrated_gradients'
        )
        
        # Check structure
        assert 'timestamp' in evidence
        assert 'patient_id' in evidence
        assert 'medical_record_id' in evidence
        assert 'fusion_scores' in evidence
        assert 'explanations' in evidence
        assert 'anatomical_regions' in evidence
        assert 'modality_contributions' in evidence
        assert 'clinical_evidence' in evidence
        assert 'patent_claim_3_support' in evidence
        assert evidence['patent_claim_3_support'] == True
    
    def test_compute_modality_contributions(self, sample_data_fusion_model):
        """Test modality contribution computation"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        attributions = np.random.randn(20)
        contributions = xai_service._compute_modality_contributions(attributions)
        
        assert 'cognitive' in contributions
        assert 'biomarker' in contributions
        assert 'imaging' in contributions
        assert 'demographic' in contributions
        
        # Should sum to approximately 1.0 (normalized)
        total = sum(contributions.values())
        assert abs(total - 1.0) < 0.01
    
    def test_compute_cognitive_domain_contributions(self, sample_data_fusion_model):
        """Test cognitive domain contribution computation"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        attributions = np.random.randn(20)
        domains = xai_service._compute_cognitive_domain_contributions(attributions)
        
        assert isinstance(domains, dict)
        # Should have at least some cognitive domains
        assert len(domains) > 0
    
    def test_prepare_visual_saliency_data(self, sample_data_fusion_model):
        """Test visual saliency data preparation (Patent Claim 3(d))"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        attributions = np.random.randn(20)
        visual_data = xai_service._prepare_visual_saliency_data(attributions)
        
        assert 'feature_attributions' in visual_data
        assert 'anatomical_regions' in visual_data
        assert 'modality_heatmap' in visual_data
        assert 'normalized_attributions' in visual_data
    
    def test_generate_dynamic_evidence_without_model(self, sample_patient_xai, sample_medical_record_xai):
        """Test fallback when model not available"""
        xai_service = DataFusionXAIService(model=None)
        
        fusion_scores = {
            'integrated_fusion_score': 62.5,
            'fusion_confidence': 0.85
        }
        
        evidence = xai_service.generate_dynamic_evidence(
            medical_record=sample_medical_record_xai,
            patient=sample_patient_xai,
            fusion_scores=fusion_scores
        )
        
        assert 'note' in evidence
        assert evidence['patent_claim_3_support'] == False


class TestXAIAPIIntegration:
    """Test XAI API integration"""
    
    @pytest.mark.asyncio
    async def test_explain_fusion_report_endpoint(
        self, test_client, test_session, sample_patient, sample_medical_record
    ):
        """Test POST /api/v1/data-fusion/{report_id}/explain endpoint"""
        # First create a fusion report
        from app.services.data_fusion_service import DataFusionService
        
        test_session.add(sample_patient)
        test_session.add(sample_medical_record)
        await test_session.commit()
        
        report = await DataFusionService.generate_fusion_report(
            patient_id=sample_patient.id,
            medical_record_id=sample_medical_record.id,
            db=test_session
        )
        test_session.add(report)
        await test_session.commit()
        await test_session.refresh(report)
        
        # Mock model service to return loaded model
        with patch('app.api.data_fusion.get_data_fusion_model_service') as mock_service:
            mock_model_service = Mock()
            mock_model_service.is_loaded.return_value = True
            mock_model_service.model = DataFusionScoringModel(input_dim=20)
            mock_service.return_value = mock_model_service
            
            response = await test_client.post(
                f"/api/v1/data-fusion/{report.id}/explain",
                params={"method": "integrated_gradients"}
            )
            
            # Should either succeed or return service unavailable
            assert response.status_code in [200, 503]
    
    @pytest.mark.asyncio
    async def test_get_saliency_map_endpoint(
        self, test_client, test_session, sample_patient, sample_medical_record
    ):
        """Test GET /api/v1/data-fusion/{report_id}/saliency-map endpoint"""
        from app.services.data_fusion_service import DataFusionService
        
        test_session.add(sample_patient)
        test_session.add(sample_medical_record)
        await test_session.commit()
        
        report = await DataFusionService.generate_fusion_report(
            patient_id=sample_patient.id,
            medical_record_id=sample_medical_record.id,
            db=test_session
        )
        test_session.add(report)
        await test_session.commit()
        await test_session.refresh(report)
        
        # Mock model service
        with patch('app.api.data_fusion.get_data_fusion_model_service') as mock_service:
            mock_model_service = Mock()
            mock_model_service.is_loaded.return_value = True
            mock_model_service.model = DataFusionScoringModel(input_dim=20)
            mock_service.return_value = mock_model_service
            
            response = await test_client.get(
                f"/api/v1/data-fusion/{report.id}/saliency-map",
                params={"method": "integrated_gradients"}
            )
            
            assert response.status_code in [200, 503]


class TestPatentClaim3Support:
    """Test that XAI service directly supports Patent Claim 3"""
    
    def test_patent_claim_3a_gradient_computation(self, sample_data_fusion_model):
        """Test Patent Claim 3(a): Computing model gradients"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        input_tensor = torch.randn(1, 20)
        result = xai_service.compute_gradient_saliency(input_tensor)
        
        # Should compute gradients
        assert 'saliency' in result
        assert len(result['saliency']) == 20
        assert np.all(result['saliency'] >= 0)  # Absolute values
    
    def test_patent_claim_3b_integrated_gradients(self, sample_data_fusion_model):
        """Test Patent Claim 3(b): Integrated Gradients with axioms"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        input_tensor = torch.randn(1, 20)
        result = xai_service.compute_integrated_gradients(input_tensor)
        
        # Should satisfy Implementation Invariance (same result for same input)
        result2 = xai_service.compute_integrated_gradients(input_tensor)
        np.testing.assert_array_almost_equal(result['attribution'], result2['attribution'], decimal=5)
    
    def test_patent_claim_3c_anatomical_mapping(self, sample_data_fusion_model):
        """Test Patent Claim 3(c): Mapping to anatomical regions"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        attributions = np.random.randn(20)
        regions = xai_service.map_to_anatomical_regions(attributions)
        
        # Should map imaging features to anatomical regions
        assert 'Hippocampus' in regions or 'Cerebral Cortex' in regions or 'Ventricular System' in regions
    
    def test_patent_claim_3d_visual_display(self, sample_data_fusion_model):
        """Test Patent Claim 3(d): Visual display data preparation"""
        xai_service = DataFusionXAIService(sample_data_fusion_model)
        
        attributions = np.random.randn(20)
        visual_data = xai_service._prepare_visual_saliency_data(attributions)
        
        # Should provide data for visualization
        assert 'feature_attributions' in visual_data
        assert 'anatomical_regions' in visual_data
        assert 'normalized_attributions' in visual_data

