"""
Unit Tests for AI Model Service
"""
import pytest
import numpy as np
from app.services.ai_model_service import AIModelService, MultiModalNeuralNetwork


class TestAIModelService:
    """Tests for AI Model Service"""
    
    def test_service_initialization(self):
        """Test service initialization"""
        service = AIModelService()
        assert service is not None
        assert len(service.feature_names) > 0
    
    def test_feature_extraction(self):
        """Test feature extraction from patient data"""
        service = AIModelService()
        
        patient_data = {
            'age': 70,
            'gender': 'male',
            'education_years': 12,
            'mmse_score': 25,
            'moca_score': 24,
            'memory_score': 50,
            'attention_score': 50,
            'executive_function_score': 50,
            'amyloid_beta': 600,
            'tau_protein': 200,
            'dopamine_level': 100,
            'apoe_e4_status': False,
            'hippocampal_volume': 3500,
            'cortical_thickness': 2.3,
            'ventricular_volume': 30000,
            'white_matter_hyperintensities': 2,
            'brain_volume_total': 1100000
        }
        
        features = service.extract_features(patient_data)
        
        assert features is not None
        assert isinstance(features, np.ndarray)
        assert len(features) == 50
        assert all(isinstance(f, (int, float, np.floating)) for f in features)
    
    def test_prediction_with_valid_data(self):
        """Test prediction with valid patient data"""
        service = AIModelService()
        
        patient_data = {
            'age': 70,
            'gender': 'male',
            'education_years': 12,
            'mmse_score': 25,
            'moca_score': 24,
            'memory_score': 50,
            'attention_score': 50,
            'executive_function_score': 50,
            'amyloid_beta': 600,
            'tau_protein': 200,
            'dopamine_level': 100,
            'apoe_e4_status': False,
            'hippocampal_volume': 3500,
            'cortical_thickness': 2.3,
            'ventricular_volume': 30000,
            'white_matter_hyperintensities': 2,
            'brain_volume_total': 1100000
        }
        
        import asyncio
        result = asyncio.run(service.predict(patient_data))
        
        assert result is not None
        assert 'alzheimer' in result
        assert 'parkinson' in result
        assert 'feature_importance' in result
        assert 'recommendations' in result
        
        # Check Alzheimer prediction
        assert 'risk_score' in result['alzheimer']
        assert 'risk_level' in result['alzheimer']
        assert 'confidence' in result['alzheimer']
        assert 0 <= result['alzheimer']['risk_score'] <= 1
        assert 0 <= result['alzheimer']['confidence'] <= 1
    
    def test_prediction_with_missing_data(self):
        """Test prediction with missing optional data"""
        service = AIModelService()
        
        patient_data = {
            'age': 70,
            'gender': 'male'
        }
        
        import asyncio
        result = asyncio.run(service.predict(patient_data))
        
        assert result is not None
        assert 'alzheimer' in result
        assert 'parkinson' in result
    
    def test_risk_level_determination(self):
        """Test risk level determination"""
        service = AIModelService()
        
        # Low risk
        assert service._determine_risk_level(0.2).value == "low"
        
        # Medium risk
        assert service._determine_risk_level(0.5).value == "medium"
        
        # High risk
        assert service._determine_risk_level(0.8).value == "high"
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        service = AIModelService()
        
        # High confidence (close to 0 or 1)
        assert service._calculate_confidence(0.9) > 0.7
        assert service._calculate_confidence(0.1) > 0.7
        
        # Low confidence (close to 0.5)
        assert service._calculate_confidence(0.5) < 0.3
    
    def test_feature_importance_calculation(self):
        """Test feature importance calculation"""
        service = AIModelService()
        
        features = np.random.rand(50)
        alzheimer_prob = 0.7
        parkinson_prob = 0.5
        
        importance = service._calculate_feature_importance(
            features, alzheimer_prob, parkinson_prob
        )
        
        assert importance is not None
        assert isinstance(importance, dict)
        assert len(importance) <= 10  # Top 10 features


class TestMultiModalNeuralNetwork:
    """Tests for MultiModalNeuralNetwork model"""
    
    def test_model_initialization(self):
        """Test model initialization"""
        model = MultiModalNeuralNetwork(input_dim=50)
        assert model is not None
    
    def test_model_forward_pass(self):
        """Test model forward pass"""
        import torch
        
        model = MultiModalNeuralNetwork(input_dim=50)
        model.eval()
        
        # Create dummy input
        x = torch.randn(1, 50)
        
        with torch.no_grad():
            alzheimer_prob, parkinson_prob = model(x)
        
        assert alzheimer_prob is not None
        assert parkinson_prob is not None
        assert 0 <= alzheimer_prob.item() <= 1
        assert 0 <= parkinson_prob.item() <= 1

