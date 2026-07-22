"""
AI Model Service for Disease Prediction
"""
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None

import asyncio
import json
import numpy as np
from typing import Dict, Tuple, Optional
import logging
from pathlib import Path

from ..core.config import settings
from ..models.prediction import RiskLevel

logger = logging.getLogger(__name__)


class ModelNotReadyError(RuntimeError):
    """Raised when prediction is requested but trained weights are not available."""

    def __init__(self, message: Optional[str] = None):
        super().__init__(
            message
            or (
                "Model weights are missing or not loaded. "
                "Place a state_dict at ENSEMBLE_MODEL_PATH (or activate a registry model) "
                "before running predictions. Mock predictions are disabled outside DEBUG "
                "with ALLOW_MOCK_PREDICTIONS=True."
            )
        )


if TORCH_AVAILABLE:
    class MultiModalNeuralNetwork(nn.Module):
        """
        Multi-modal deep learning model for Alzheimer's and Parkinson's prediction
        Combines imaging features, clinical data, biomarkers, and genetic information
        """
        def __init__(self, input_dim: int = 50, hidden_dims: list = [256, 128, 64]):
            super(MultiModalNeuralNetwork, self).__init__()
            
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
                nn.Sigmoid()
            )
            
            self.parkinson_head = nn.Sequential(
                nn.Linear(hidden_dims[-1], 32),
                nn.ReLU(),
                nn.Linear(32, 1),
                nn.Sigmoid()
            )
        
        def forward(self, x):
            features = self.feature_extractor(x)
            alzheimer_prob = self.alzheimer_head(features)
            parkinson_prob = self.parkinson_head(features)
            return alzheimer_prob, parkinson_prob
else:
    class MultiModalNeuralNetwork:  # type: ignore
        """Stub when torch is unavailable."""
        def __init__(self, *args, **kwargs):
            raise ModelNotReadyError("PyTorch is not available; cannot construct MultiModalNeuralNetwork")


FEATURE_NAMES = [
    'age', 'gender_encoded', 'education_years',
    'mmse_score', 'moca_score', 'memory_score', 'attention_score', 'executive_function_score',
    'amyloid_beta', 'tau_protein', 'dopamine_level',
    'apoe_e4_status',
    'hippocampal_volume', 'cortical_thickness', 'ventricular_volume',
    'white_matter_hyperintensities', 'brain_volume_total',
    *[f'imaging_feature_{i}' for i in range(32)]
]


class AIModelService:
    """Service for AI-powered disease prediction"""

    def __init__(self):
        self.use_mock = False
        self.model_ready = False
        self.model = None
        self.feature_names = list(FEATURE_NAMES)
        self.device = None
        self._prediction_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_PREDICTIONS)
        self._initialize_model()

    @staticmethod
    def _mock_allowed() -> bool:
        return bool(settings.DEBUG and settings.ALLOW_MOCK_PREDICTIONS)

    def _resolve_weight_path(self) -> Optional[Path]:
        """Resolve weight file from ENSEMBLE_MODEL_PATH or active registry entry."""
        model_path = Path(settings.ENSEMBLE_MODEL_PATH)
        if model_path.exists():
            return model_path

        registry_candidates = [
            Path(settings.MODELS_DIR) / "registry.json",
            Path("models") / "registry.json",
        ]
        for registry_path in registry_candidates:
            if not registry_path.exists():
                continue
            try:
                with open(registry_path, "r", encoding="utf-8") as f:
                    registry = json.load(f)
                active = None
                current = registry.get("current_model")
                for entry in registry.get("models", []):
                    if entry.get("is_active") or entry.get("version") == current:
                        active = entry
                        if entry.get("is_active"):
                            break
                if active and active.get("model_path"):
                    candidate = Path(active["model_path"])
                    if candidate.exists():
                        return candidate
            except Exception as e:
                logger.warning(f"Could not read model registry {registry_path}: {e}")
        return None
    
    def _initialize_model(self):
        """Initialize or load pre-trained model. Fail closed if weights are missing."""
        if not TORCH_AVAILABLE:
            logger.warning("Torch not available.")
            if self._mock_allowed():
                self.use_mock = True
                self.model_ready = False
                logger.warning("DEBUG+ALLOW_MOCK_PREDICTIONS: mock predictions enabled.")
            else:
                self.use_mock = False
                self.model_ready = False
                logger.error("Torch unavailable and mock predictions not allowed. model_ready=False.")
            return
        
        try:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            weight_path = self._resolve_weight_path()

            if weight_path is None:
                # Do NOT use random weights for production inference.
                self.model = None
                self.model_ready = False
                self.use_mock = self._mock_allowed()
                logger.error(
                    f"No pre-trained weights at {settings.ENSEMBLE_MODEL_PATH} "
                    "(or active registry path). model_ready=False. "
                    "Random initialization is not used for inference."
                )
                if self.use_mock:
                    logger.warning("DEBUG+ALLOW_MOCK_PREDICTIONS: mock predictions enabled.")
                return

            self.model = MultiModalNeuralNetwork(input_dim=50)
            self.model.load_state_dict(torch.load(weight_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
            self.model_ready = True
            self.use_mock = False
            logger.info(f"Loaded pre-trained model from {weight_path}")
            
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            self.model = None
            self.model_ready = False
            self.use_mock = self._mock_allowed()
            if self.use_mock:
                logger.warning("Falling back to mock predictions (DEBUG+ALLOW_MOCK_PREDICTIONS).")
            else:
                logger.error("Model init failed; mock fallback disabled. model_ready=False.")
    
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
        features.extend(np.asarray(imaging_features, dtype=np.float32).tolist())
        
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

    def _compute_attention_scores(self, feature_importance: Dict[str, float]) -> Dict[str, float]:
        """
        Derive modality attention scores (MRI, Biomarker, Cognitive) from feature_importance.
        SRS: explainability per modality. Normalized so sum = 1.0.
        """
        mri_keys = {
            "hippocampal_volume", "cortical_thickness", "ventricular_volume",
            "white_matter_hyperintensities", "brain_volume_total",
        } | {f"imaging_feature_{i}" for i in range(32)}
        biomarker_keys = {"amyloid_beta", "tau_protein", "dopamine_level", "apoe_e4_status"}
        cognitive_keys = {
            "age", "gender_encoded", "education_years",
            "mmse_score", "moca_score", "memory_score", "attention_score", "executive_function_score",
        }
        mri = sum(feature_importance.get(k, 0.0) for k in mri_keys)
        biomarker = sum(feature_importance.get(k, 0.0) for k in biomarker_keys)
        cognitive = sum(feature_importance.get(k, 0.0) for k in cognitive_keys)
        total = mri + biomarker + cognitive
        if total <= 0:
            return {"MRI": 1.0 / 3, "Biomarker": 1.0 / 3, "Cognitive": 1.0 / 3}
        return {
            "MRI": round(mri / total, 4),
            "Biomarker": round(biomarker / total, 4),
            "Cognitive": round(cognitive / total, 4),
        }

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

    def _mock_predict(self, patient_data: Dict) -> Dict:
        """Deterministic heuristic mock — only used when explicitly allowed in DEBUG."""
        age = patient_data.get('age', 65)
        mmse = patient_data.get('mmse_score', 25) / 30.0
        tau = patient_data.get('tau_protein', 200) / 800.0
        dopamine = patient_data.get('dopamine_level', 100) / 150.0

        # Deterministic (no random.uniform) so non-dev never gets silent random fallbacks
        alzheimer_prob = max(0.1, min(0.9, (100 - age) / 100.0 + (1 - mmse) * 0.3 + tau * 0.2))
        parkinson_prob = max(0.1, min(0.9, (100 - age) / 120.0 + (1.0 - dopamine) * 0.15))

        alzheimer_risk_level = self._determine_risk_level(alzheimer_prob)
        parkinson_risk_level = self._determine_risk_level(parkinson_prob)
        feature_importance = {
            'age': 0.25,
            'mmse_score': 0.20,
            'tau_protein': 0.15,
            'hippocampal_volume': 0.12,
            'moca_score': 0.10,
            'dopamine_level': 0.08,
            'apoe_e4_status': 0.05,
            'cortical_thickness': 0.03,
            'ventricular_volume': 0.02
        }
        attention_scores = self._compute_attention_scores(feature_importance)
        recommendations = self._generate_recommendations(
            alzheimer_prob, parkinson_prob, patient_data
        )
        return {
            'alzheimer': {
                'risk_score': alzheimer_prob,
                'risk_level': alzheimer_risk_level,
                'confidence': self._calculate_confidence(alzheimer_prob)
            },
            'parkinson': {
                'risk_score': parkinson_prob,
                'risk_level': parkinson_risk_level,
                'confidence': self._calculate_confidence(parkinson_prob)
            },
            'feature_importance': feature_importance,
            'attention_scores': attention_scores,
            'recommendations': recommendations,
            'model_version': '1.0.0-mock',
            'model_name': 'MockPredictionModel'
        }

    def _run_inference_sync(self, patient_data: Dict) -> Dict:
        """
        Synchronous model inference (CPU/GPU-bound).
        Run via asyncio.to_thread() so the event loop is not blocked.
        """
        features = self.extract_features(patient_data)
        features_tensor = torch.from_numpy(features).unsqueeze(0).to(self.device)
        with torch.no_grad():
            alzheimer_prob, parkinson_prob = self.model(features_tensor)
            alzheimer_prob = float(alzheimer_prob.cpu().numpy()[0][0])
            parkinson_prob = float(parkinson_prob.cpu().numpy()[0][0])
        alzheimer_risk_level = self._determine_risk_level(alzheimer_prob)
        parkinson_risk_level = self._determine_risk_level(parkinson_prob)
        alzheimer_confidence = self._calculate_confidence(alzheimer_prob)
        parkinson_confidence = self._calculate_confidence(parkinson_prob)
        feature_importance = self._calculate_feature_importance(
            features, alzheimer_prob, parkinson_prob
        )
        attention_scores = self._compute_attention_scores(feature_importance)
        recommendations = self._generate_recommendations(
            alzheimer_prob, parkinson_prob, patient_data
        )
        return {
            "alzheimer": {
                "risk_score": alzheimer_prob,
                "risk_level": alzheimer_risk_level,
                "confidence": alzheimer_confidence,
            },
            "parkinson": {
                "risk_score": parkinson_prob,
                "risk_level": parkinson_risk_level,
                "confidence": parkinson_confidence,
            },
            "feature_importance": feature_importance,
            "attention_scores": attention_scores,
            "recommendations": recommendations,
            "model_version": "1.0.0",
            "model_name": "MultiModalNeuralNetwork",
        }

    async def predict(self, patient_data: Dict) -> Dict:
        """
        Make disease risk prediction
        
        Args:
            patient_data: Dictionary containing patient information
        
        Returns:
            Dictionary with prediction results

        Raises:
            ModelNotReadyError: if weights are missing and mock is not allowed
        """
        try:
            if not self.model_ready:
                if self.use_mock and self._mock_allowed():
                    return self._mock_predict(patient_data)
                raise ModelNotReadyError()

            # Limit concurrent inferences to avoid overload (config: MAX_CONCURRENT_PREDICTIONS)
            async with self._prediction_semaphore:
                return await asyncio.to_thread(self._run_inference_sync, patient_data)

        except ModelNotReadyError:
            raise
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise


# Singleton instance
ai_model_service = AIModelService()
