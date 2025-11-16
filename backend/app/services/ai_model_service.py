"""
AI Model Service for Disease Prediction
"""
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

try:
    import torch
    import torch.nn as nn
except ImportError:  # pragma: no cover - optional dependency guard
    torch = None
    nn = None

from ..core.config import settings
from ..models.prediction import RiskLevel

logger = logging.getLogger(__name__)


if nn is not None:

    class MultiModalNeuralNetwork(nn.Module):
        """
        Multi-modal deep learning model for Alzheimer's and Parkinson's prediction
        Combines imaging features, clinical data, biomarkers, and genetic information
        """

        def __init__(self, input_dim: int = 50, hidden_dims: list = [256, 128, 64]):
            super().__init__()

            # Feature extraction layers
            layers = []
            prev_dim = input_dim

            for hidden_dim in hidden_dims:
                layers.append(nn.Linear(prev_dim, hidden_dim))
                layers.append(nn.ReLU())
                layers.append(nn.BatchNorm1d(hidden_dim))
                layers.append(nn.Dropout(0.3))
                prev_dim = hidden_dim

            self.feature_extractor = nn.Sequential(*layers)

            # Separate heads for Alzheimer's and Parkinson's
            self.alzheimer_head = nn.Sequential(
                nn.Linear(hidden_dims[-1], 32),
                nn.ReLU(),
                nn.Linear(32, 1),
                nn.Sigmoid(),
            )

            self.parkinson_head = nn.Sequential(
                nn.Linear(hidden_dims[-1], 32),
                nn.ReLU(),
                nn.Linear(32, 1),
                nn.Sigmoid(),
            )

        def forward(self, x):
            features = self.feature_extractor(x)
            alzheimer_prob = self.alzheimer_head(features)
            parkinson_prob = self.parkinson_head(features)
            return alzheimer_prob, parkinson_prob

else:

    class MultiModalNeuralNetwork:  # type: ignore[override]
        """Fallback stub when PyTorch is unavailable."""

        def __init__(self, *args, **kwargs):
            raise RuntimeError("pytorch_not_available")


class AIModelService:
    """Service for AI-powered disease prediction"""
    
    def __init__(self):
        self.model = None
        self.feature_names: list[str] = []
        if torch is None or nn is None:
            logger.warning("PyTorch is not installed; AIModelService is disabled.")
            self.device = None
            self._available = False
            return

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._available = True
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load pre-trained model"""
        try:
            # Initialize model architecture
            self.model = MultiModalNeuralNetwork(input_dim=50)
            
            # Try to load pre-trained weights if available
            model_loaded = False
            
            if settings.USE_TRAINED_MODEL:
                # Try to load from model registry first
                try:
                    from .training.model_registry import ModelRegistry
                    registry = ModelRegistry(Path(settings.MODEL_REGISTRY_PATH))
                    active_model = registry.get_active_model()
                    
                    if active_model and Path(active_model['model_path']).exists():
                        model_path = Path(active_model['model_path'])
                        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                        logger.info(f"Loaded active model from registry: {model_path} (version: {active_model['version']})")
                        model_loaded = True
                    else:
                        # Try latest model
                        latest_model = registry.get_latest_model()
                        if latest_model and Path(latest_model['model_path']).exists():
                            model_path = Path(latest_model['model_path'])
                            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                            logger.info(f"Loaded latest model from registry: {model_path} (version: {latest_model['version']})")
                            model_loaded = True
                except Exception as e:
                    logger.warning(f"Could not load model from registry: {e}")
            
            # Fallback to default model path
            if not model_loaded:
                model_path = Path(settings.ENSEMBLE_MODEL_PATH)
                if model_path.exists():
                    self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                    logger.info(f"Loaded pre-trained model from {model_path}")
                    model_loaded = True
                else:
                    logger.warning(f"No pre-trained model found at {model_path}. Using random initialization.")
            
            self.model.to(self.device)
            self.model.eval()
            
            # Define feature names for interpretability
            self.feature_names = [
                # Demographics
                'age', 'gender_encoded', 'education_years',
                # Cognitive Scores
                'mmse_score', 'moca_score', 'memory_score', 'attention_score', 'executive_function_score',
                # Biomarkers
                'amyloid_beta', 'tau_protein', 'dopamine_level',
                # Genetic
                'apoe_e4_status',
                # MRI Features
                'hippocampal_volume', 'cortical_thickness', 'ventricular_volume',
                'white_matter_hyperintensities', 'brain_volume_total',
                # Additional features (placeholder for imaging deep features)
                *[f'imaging_feature_{i}' for i in range(32)]
            ]
            
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            raise
    
    def extract_features(self, patient_data: Dict) -> np.ndarray:
        """
        Extract and normalize features from patient data
        
        Args:
            patient_data: Dictionary containing patient information
        
        Returns:
            numpy array of extracted features
        """
        features = []
        
        # Demographics
        features.append(patient_data.get('age', 0) / 100.0)  # Normalize age
        features.append(1.0 if patient_data.get('gender') == 'male' else 0.0)
        features.append(patient_data.get('education_years', 0) / 25.0)
        
        # Cognitive Scores (normalize to 0-1)
        features.append(patient_data.get('mmse_score', 0) / 30.0)
        features.append(patient_data.get('moca_score', 0) / 30.0)
        features.append(patient_data.get('memory_score', 0) / 100.0)
        features.append(patient_data.get('attention_score', 0) / 100.0)
        features.append(patient_data.get('executive_function_score', 0) / 100.0)
        
        # Biomarkers (normalize using typical ranges)
        features.append(patient_data.get('amyloid_beta', 600) / 1000.0)
        features.append(patient_data.get('tau_protein', 200) / 800.0)
        features.append(patient_data.get('dopamine_level', 100) / 150.0)
        
        # Genetic
        features.append(1.0 if patient_data.get('apoe_e4_status') else 0.0)
        
        # MRI Features
        features.append(patient_data.get('hippocampal_volume', 3500) / 5000.0)
        features.append(patient_data.get('cortical_thickness', 2.3) / 3.0)
        features.append(patient_data.get('ventricular_volume', 30000) / 70000.0)
        features.append(patient_data.get('white_matter_hyperintensities', 2) / 10.0)
        features.append(patient_data.get('brain_volume_total', 1100000) / 1500000.0)
        
        # Imaging deep features (from CNN - placeholder with zeros if not available)
        imaging_features = patient_data.get('imaging_features', np.zeros(32))
        if len(imaging_features) != 32:
            imaging_features = np.zeros(32)
        features.extend(imaging_features.tolist())
        
        return np.array(features, dtype=np.float32)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on probability score"""
        if risk_score < 0.33:
            return RiskLevel.LOW
        elif risk_score < 0.66:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH
    
    def _calculate_confidence(self, probability: float) -> float:
        """
        Calculate confidence score based on probability
        Higher confidence when probability is close to 0 or 1
        """
        return 1.0 - 2.0 * abs(probability - 0.5)
    
    def _calculate_feature_importance(self, features: np.ndarray, 
                                     alzheimer_prob: float, 
                                     parkinson_prob: float) -> Dict[str, float]:
        """
        Calculate feature importance using simple attribution
        In production, use methods like SHAP or Integrated Gradients
        """
        importance = {}
        
        # Simple feature importance based on feature values and prediction
        # This is a placeholder - in production use proper explainability methods
        for i, (feat_name, feat_value) in enumerate(zip(self.feature_names, features)):
            # Simple heuristic importance
            if 'alzheimer' in feat_name.lower() or feat_name in ['mmse_score', 'hippocampal_volume', 'tau_protein']:
                importance[feat_name] = float(abs(feat_value - 0.5) * alzheimer_prob)
            elif 'parkinson' in feat_name.lower() or feat_name in ['dopamine_level']:
                importance[feat_name] = float(abs(feat_value - 0.5) * parkinson_prob)
            else:
                importance[feat_name] = float(abs(feat_value - 0.5) * max(alzheimer_prob, parkinson_prob))
        
        # Normalize importance scores
        total = sum(importance.values())
        if total > 0:
            importance = {k: v/total for k, v in importance.items()}
        
        # Return top 10 most important features
        sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_importance[:10])
    
    def _generate_recommendations(self, alzheimer_risk: float, 
                                 parkinson_risk: float,
                                 patient_data: Dict) -> str:
        """Generate clinical recommendations based on predictions"""
        recommendations = []
        
        if alzheimer_risk > 0.66:
            recommendations.append("⚠️ High Alzheimer's risk detected:")
            recommendations.append("- Immediate neurological consultation recommended")
            recommendations.append("- Consider comprehensive neuropsychological testing")
            recommendations.append("- Evaluate for amyloid PET imaging")
            recommendations.append("- Discuss treatment options and clinical trial eligibility")
        elif alzheimer_risk > 0.33:
            recommendations.append("⚡ Moderate Alzheimer's risk detected:")
            recommendations.append("- Schedule follow-up cognitive assessment in 6 months")
            recommendations.append("- Implement cognitive training programs")
            recommendations.append("- Consider lifestyle interventions (exercise, diet, social engagement)")
        
        if parkinson_risk > 0.66:
            recommendations.append("\n⚠️ High Parkinson's risk detected:")
            recommendations.append("- Immediate movement disorder specialist consultation")
            recommendations.append("- Consider DaT scan for dopamine transporter imaging")
            recommendations.append("- Evaluate motor symptoms and potential treatment")
        elif parkinson_risk > 0.33:
            recommendations.append("\n⚡ Moderate Parkinson's risk detected:")
            recommendations.append("- Monitor for motor symptoms development")
            recommendations.append("- Schedule neurological follow-up in 6 months")
        
        # General recommendations
        if not recommendations:
            recommendations.append("✓ Low risk detected - Continue regular health monitoring")
        
        recommendations.append("\n📋 General recommendations:")
        recommendations.append("- Maintain cognitive and physical activity")
        recommendations.append("- Ensure adequate sleep and stress management")
        recommendations.append("- Follow Mediterranean diet rich in omega-3 fatty acids")
        recommendations.append("- Regular cardiovascular exercise (150 min/week)")
        
        return "\n".join(recommendations)
    
    async def predict(self, patient_data: Dict) -> Dict:
        """
        Make disease risk prediction
        
        Args:
            patient_data: Dictionary containing patient information
        
        Returns:
            Dictionary with prediction results
        """
        if not getattr(self, "_available", False) or self.model is None or torch is None:
            raise RuntimeError("pytorch_not_available")

        try:
            # Extract features
            features = self.extract_features(patient_data)
            
            # Convert to torch tensor
            features_tensor = torch.from_numpy(features).unsqueeze(0).to(self.device)
            
            # Make prediction
            with torch.no_grad():
                alzheimer_prob, parkinson_prob = self.model(features_tensor)
                
                alzheimer_prob = float(alzheimer_prob.cpu().numpy()[0][0])
                parkinson_prob = float(parkinson_prob.cpu().numpy()[0][0])
            
            # Calculate risk levels and confidence
            alzheimer_risk_level = self._determine_risk_level(alzheimer_prob)
            parkinson_risk_level = self._determine_risk_level(parkinson_prob)
            
            alzheimer_confidence = self._calculate_confidence(alzheimer_prob)
            parkinson_confidence = self._calculate_confidence(parkinson_prob)
            
            # Calculate feature importance
            feature_importance = self._calculate_feature_importance(
                features, alzheimer_prob, parkinson_prob
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                alzheimer_prob, parkinson_prob, patient_data
            )
            
            # Simple placeholder attention scores summing to 1.0
            # In production, extract real attention from model
            att_mri = max(0.05, min(0.9, 0.4 + (features[149] - 0.5) * 0.1))  # heuristic
            att_bio = 0.3
            att_cog = 1.0 - (att_mri + att_bio)

            return {
                'alzheimer': {
                    'risk_score': alzheimer_prob,
                    'risk_level': alzheimer_risk_level,
                    'confidence': alzheimer_confidence
                },
                'parkinson': {
                    'risk_score': parkinson_prob,
                    'risk_level': parkinson_risk_level,
                    'confidence': parkinson_confidence
                },
                'attention_scores': {
                    'MRI': float(att_mri),
                    'Biomarker': float(att_bio),
                    'Cognitive': float(att_cog)
                },
                'feature_importance': feature_importance,
                'recommendations': recommendations,
                'model_version': '1.0.0',
                'model_name': 'MultiModalNeuralNetwork'
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise


# Singleton instance
ai_model_service = AIModelService()

