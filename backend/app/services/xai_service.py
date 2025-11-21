"""
Explainable AI (XAI) Service
Advanced interpretability methods including Saliency Maps, Integrated Gradients, and SHAP values
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    F = None

from ..models.prediction import RiskLevel

logger = logging.getLogger(__name__)


class XAIService:
    """Service for Explainable AI and model interpretability"""
    
    def __init__(self, model: Optional[nn.Module] = None, device: Optional[torch.device] = None):
        """
        Initialize XAI Service
        
        Args:
            model: PyTorch model for interpretation
            device: Device to run on (cuda or cpu)
        """
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available. XAI features limited.")
            self.model = None
            self.device = None
            return
        
        self.model = model
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device
        
        if self.model:
            self.model.to(self.device)
            self.model.eval()
    
    def compute_saliency_map(
        self, 
        input_tensor: torch.Tensor, 
        target_class: int = 0,
        method: str = "gradient"
    ) -> np.ndarray:
        """
        Compute saliency map for input features
        
        Saliency maps show which input features are most important for the prediction.
        This is particularly useful for MRI images to identify critical brain regions.
        
        Mathematical formulation:
        S(x) = |∂y/∂x|
        where y is the output prediction and x is the input
        
        Args:
            input_tensor: Input tensor (batch_size, features)
            target_class: Target class (0=Alzheimer, 1=Parkinson)
            method: Method to use ('gradient', 'integrated_gradients', 'smoothgrad')
        
        Returns:
            Saliency map as numpy array
        """
        if not TORCH_AVAILABLE or self.model is None:
            raise RuntimeError("PyTorch and model required for saliency maps")
        
        if method == "gradient":
            return self._gradient_saliency(input_tensor, target_class)
        elif method == "integrated_gradients":
            return self._integrated_gradients(input_tensor, target_class)
        elif method == "smoothgrad":
            return self._smoothgrad_saliency(input_tensor, target_class)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _gradient_saliency(
        self, 
        input_tensor: torch.Tensor, 
        target_class: int
    ) -> np.ndarray:
        """
        Compute gradient-based saliency map
        
        Method: Vanilla Gradient Saliency
        S(x) = |∇_x y_c(x)|
        
        where:
        - y_c is the output probability for class c
        - ∇_x is the gradient with respect to input x
        """
        input_tensor = input_tensor.to(self.device).requires_grad_(True)
        
        # Forward pass
        alzheimer_pred, parkinson_pred = self.model(input_tensor)
        output = parkinson_pred if target_class == 1 else alzheimer_pred
        
        # Backward pass
        output.backward()
        
        # Get gradients
        saliency = input_tensor.grad.abs().cpu().numpy()
        
        return saliency[0]  # Remove batch dimension
    
    def _integrated_gradients(
        self,
        input_tensor: torch.Tensor,
        target_class: int,
        baseline: Optional[torch.Tensor] = None,
        steps: int = 50
    ) -> np.ndarray:
        """
        Compute Integrated Gradients attribution
        
        Integrated Gradients provides a principled way to attribute predictions
        to input features by integrating gradients along a path from baseline to input.
        
        Mathematical formulation:
        IG_i(x) = (x_i - baseline_i) × ∫[α=0 to 1] ∂F(baseline + α(x - baseline))/∂x_i dα
        
        This satisfies two axioms:
        1. Sensitivity: If input and baseline differ in one feature and prediction differs,
           that feature gets non-zero attribution
        2. Implementation Invariance: Attributions are identical for functionally equivalent models
        
        Args:
            input_tensor: Input tensor
            target_class: Target class (0=Alzheimer, 1=Parkinson)
            baseline: Baseline tensor (zeros if None)
            steps: Number of integration steps
        
        Returns:
            Integrated Gradients attribution
        """
        input_tensor = input_tensor.to(self.device)
        
        if baseline is None:
            baseline = torch.zeros_like(input_tensor)
        else:
            baseline = baseline.to(self.device)
        
        # Compute path: baseline -> input
        alphas = np.linspace(0, 1, steps)
        integrated_grads = torch.zeros_like(input_tensor)
        
        for alpha in alphas:
            # Interpolate between baseline and input
            interpolated = baseline + alpha * (input_tensor - baseline)
            interpolated.requires_grad_(True)
            
            # Forward pass
            alzheimer_pred, parkinson_pred = self.model(interpolated)
            output = parkinson_pred if target_class == 1 else alzheimer_pred
            
            # Backward pass
            output.backward()
            
            # Accumulate gradients
            integrated_grads += interpolated.grad
        
        # Average and multiply by difference
        integrated_grads /= steps
        attribution = (input_tensor - baseline) * integrated_grads
        
        return attribution.cpu().numpy()[0]
    
    def _smoothgrad_saliency(
        self,
        input_tensor: torch.Tensor,
        target_class: int,
        n_samples: int = 50,
        noise_scale: float = 0.15
    ) -> np.ndarray:
        """
        Compute SmoothGrad saliency map
        
        SmoothGrad reduces noise in saliency maps by averaging gradients
        over multiple noisy versions of the input.
        
        Mathematical formulation:
        S_SmoothGrad(x) = (1/N) Σ_i S(x + N(0, σ²))
        
        where:
        - N is the number of samples
        - σ is the noise scale
        - S is the base saliency method (gradient)
        
        Args:
            input_tensor: Input tensor
            target_class: Target class
            n_samples: Number of noisy samples
            noise_scale: Standard deviation of noise
        
        Returns:
            SmoothGrad saliency map
        """
        input_tensor = input_tensor.to(self.device)
        saliency_maps = []
        
        for _ in range(n_samples):
            # Add Gaussian noise
            noise = torch.randn_like(input_tensor) * noise_scale
            noisy_input = input_tensor + noise
            noisy_input = torch.clamp(noisy_input, 0, 1)  # Keep in valid range
            
            # Compute saliency for noisy input
            saliency = self._gradient_saliency(noisy_input, target_class)
            saliency_maps.append(saliency)
        
        # Average saliency maps
        smooth_saliency = np.mean(saliency_maps, axis=0)
        return smooth_saliency
    
    def compute_feature_attribution_shap(
        self,
        input_tensor: torch.Tensor,
        target_class: int,
        background_data: torch.Tensor,
        n_samples: int = 100
    ) -> np.ndarray:
        """
        Compute SHAP (SHapley Additive exPlanations) values
        
        SHAP values provide a unified framework for explaining model outputs
        based on cooperative game theory.
        
        Mathematical formulation:
        SHAP_i = Σ_{S ⊆ F\{i}} [|S|!(|F| - |S| - 1)! / |F|!] × [f(S ∪ {i}) - f(S)]
        
        where:
        - F is the set of all features
        - S is a subset of features
        - f is the model prediction
        
        Args:
            input_tensor: Input tensor
            target_class: Target class
            background_data: Background/reference data (multiple samples)
            n_samples: Number of samples for approximation
        
        Returns:
            SHAP values for each feature
        """
        if not TORCH_AVAILABLE or self.model is None:
            raise RuntimeError("PyTorch and model required for SHAP")
        
        input_tensor = input_tensor.to(self.device)
        background_data = background_data.to(self.device)
        
        # Simplified SHAP approximation using permutation sampling
        shap_values = torch.zeros_like(input_tensor)
        n_features = input_tensor.shape[1]
        
        # Get baseline prediction (average over background)
        with torch.no_grad():
            baseline_preds = []
            for bg_sample in background_data:
                alz_pred, park_pred = self.model(bg_sample.unsqueeze(0))
                pred = park_pred if target_class == 1 else alz_pred
                baseline_preds.append(pred.item())
            baseline = np.mean(baseline_preds)
        
        # Permutation sampling to approximate SHAP
        for _ in range(n_samples):
            # Random permutation of features
            permutation = np.random.permutation(n_features)
            
            # Sequential feature addition
            current_input = torch.zeros_like(input_tensor)
            prev_pred = baseline
            
            for i, feat_idx in enumerate(permutation):
                # Add feature
                current_input[0, feat_idx] = input_tensor[0, feat_idx]
                
                # Get prediction
                with torch.no_grad():
                    alz_pred, park_pred = self.model(current_input)
                    pred = park_pred if target_class == 1 else alz_pred
                    curr_pred = pred.item()
                
                # Compute marginal contribution
                marginal = curr_pred - prev_pred
                shap_values[0, feat_idx] += marginal
                
                prev_pred = curr_pred
        
        # Average
        shap_values /= n_samples
        
        return shap_values.cpu().numpy()[0]
    
    def generate_saliency_map_for_mri(
        self,
        mri_features: np.ndarray,
        imaging_features: np.ndarray,
        feature_names: List[str],
        target_class: int = 0
    ) -> Dict[str, np.ndarray]:
        """
        Generate saliency map specifically for MRI features
        
        This method creates region-specific saliency maps that can be overlaid
        on MRI images to show which brain regions contribute most to the prediction.
        
        Args:
            mri_features: MRI volumetric features (hippocampal_volume, etc.)
            imaging_features: Deep imaging features (from CNN)
            feature_names: Names of all features
            target_class: Target class (0=Alzheimer, 1=Parkinson)
        
        Returns:
            Dictionary with saliency maps for different feature categories
        """
        # Combine features
        all_features = np.concatenate([mri_features, imaging_features])
        
        # Map features to brain regions
        # MRI volumetric features map to anatomical regions
        region_map = {
            'hippocampal_volume': 'hippocampus',
            'cortical_thickness': 'cortex',
            'ventricular_volume': 'ventricles',
            'white_matter_hyperintensities': 'white_matter',
            'brain_volume_total': 'whole_brain'
        }
        
        # For demonstration, create normalized saliency
        # In production, this would use actual model gradients
        saliency_map = {}
        
        for i, feat_name in enumerate(feature_names):
            if feat_name in region_map:
                region = region_map[feat_name]
                if region not in saliency_map:
                    saliency_map[region] = np.zeros(len(feature_names))
                # Assign importance based on feature value
                saliency_map[region][i] = abs(all_features[i])
        
        # Normalize each region
        for region in saliency_map:
            if saliency_map[region].sum() > 0:
                saliency_map[region] = saliency_map[region] / saliency_map[region].sum()
        
        return saliency_map
    
    def explain_prediction(
        self,
        input_features: np.ndarray,
        prediction_result: Dict,
        feature_names: List[str],
        method: str = "integrated_gradients"
    ) -> Dict[str, any]:
        """
        Generate comprehensive explanation for a prediction
        
        Combines multiple XAI methods to provide a complete explanation:
        - Feature importance
        - Saliency maps
        - Regional attribution (for MRI)
        - Confidence analysis
        
        Args:
            input_features: Input feature vector
            prediction_result: Prediction result from model
            feature_names: Names of features
            method: XAI method to use
        
        Returns:
            Comprehensive explanation dictionary
        """
        if not TORCH_AVAILABLE or self.model is None:
            # Fallback to simple explanation
            return self._simple_explanation(input_features, prediction_result, feature_names)
        
        input_tensor = torch.from_numpy(input_features).unsqueeze(0).float().to(self.device)
        
        explanations = {
            'prediction': prediction_result,
            'feature_importance': {},
            'saliency_maps': {},
            'top_contributing_features': [],
            'confidence_analysis': {}
        }
        
        # Alzheimer's explanation
        if 'alzheimer' in prediction_result:
            alz_saliency = self.compute_saliency_map(
                input_tensor, 
                target_class=0, 
                method=method
            )
            explanations['saliency_maps']['alzheimer'] = alz_saliency.tolist()
            
            # Top contributing features
            feature_importance = dict(zip(feature_names, alz_saliency))
            explanations['feature_importance']['alzheimer'] = feature_importance
            top_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
            explanations['top_contributing_features'].append({
                'disease': 'alzheimer',
                'features': [{'name': name, 'importance': float(importance)} for name, importance in top_features]
            })
        
        # Parkinson's explanation
        if 'parkinson' in prediction_result:
            park_saliency = self.compute_saliency_map(
                input_tensor,
                target_class=1,
                method=method
            )
            explanations['saliency_maps']['parkinson'] = park_saliency.tolist()
            
            # Top contributing features
            feature_importance = dict(zip(feature_names, park_saliency))
            explanations['feature_importance']['parkinson'] = feature_importance
            top_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
            explanations['top_contributing_features'].append({
                'disease': 'parkinson',
                'features': [{'name': name, 'importance': float(importance)} for name, importance in top_features]
            })
        
        # Confidence analysis
        if 'alzheimer' in prediction_result and 'parkinson' in prediction_result:
            alz_risk = prediction_result['alzheimer'].get('risk_score', 0)
            park_risk = prediction_result['parkinson'].get('risk_score', 0)
            
            explanations['confidence_analysis'] = {
                'alzheimer_confidence': prediction_result['alzheimer'].get('confidence', 0),
                'parkinson_confidence': prediction_result['parkinson'].get('confidence', 0),
                'uncertainty': abs(alz_risk - park_risk),  # Lower uncertainty if predictions diverge
                'explanation': self._generate_confidence_explanation(prediction_result)
            }
        
        return explanations
    
    def _simple_explanation(
        self,
        input_features: np.ndarray,
        prediction_result: Dict,
        feature_names: List[str]
    ) -> Dict[str, any]:
        """Fallback simple explanation when PyTorch not available"""
        return {
            'prediction': prediction_result,
            'feature_importance': {},
            'note': 'Advanced XAI methods require PyTorch'
        }
    
    def _generate_confidence_explanation(self, prediction_result: Dict) -> str:
        """Generate human-readable confidence explanation"""
        explanations = []
        
        if 'alzheimer' in prediction_result:
            conf = prediction_result['alzheimer'].get('confidence', 0)
            risk = prediction_result['alzheimer'].get('risk_score', 0)
            if conf > 0.8:
                explanations.append(f"High confidence in Alzheimer's assessment (confidence: {conf:.2%})")
            elif conf > 0.6:
                explanations.append(f"Moderate confidence in Alzheimer's assessment (confidence: {conf:.2%})")
            else:
                explanations.append(f"Low confidence in Alzheimer's assessment - consider additional testing")
        
        if 'parkinson' in prediction_result:
            conf = prediction_result['parkinson'].get('confidence', 0)
            risk = prediction_result['parkinson'].get('risk_score', 0)
            if conf > 0.8:
                explanations.append(f"High confidence in Parkinson's assessment (confidence: {conf:.2%})")
            elif conf > 0.6:
                explanations.append(f"Moderate confidence in Parkinson's assessment (confidence: {conf:.2%})")
            else:
                explanations.append(f"Low confidence in Parkinson's assessment - consider additional testing")
        
        return " ".join(explanations)


# Singleton instance (will be initialized with model)
xai_service = None


def initialize_xai_service(model: nn.Module, device: torch.device):
    """Initialize global XAI service with model"""
    global xai_service
    xai_service = XAIService(model, device)
    return xai_service


