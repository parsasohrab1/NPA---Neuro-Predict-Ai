"""
PATENT CLAIM 3: Explainable AI Service for Data Fusion
Dynamic Evidence Generation supporting Patent Claim 3

Patent Claim 3: System for generating explanations including:
(a) Computing model gradients with respect to input
(b) Using Integrated Gradients for accurate attribution
(c) Mapping attributions to anatomical brain regions
(d) Visual display of saliency maps for medical interpretation
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging

from .data_fusion_model import DataFusionScoringModel
from ..models.medical_record import MedicalRecord
from ..models.patient import Patient

logger = logging.getLogger(__name__)


class DataFusionXAIService:
    """
    PATENT CLAIM 3: Explainable AI Service for Data Fusion Model
    
    This service implements dynamic evidence generation that directly supports
    Patent Claim 3 by providing:
    1. Gradient-based saliency computation
    2. Integrated Gradients attribution
    3. Anatomical region mapping
    4. Dynamic evidence generation for clinical interpretation
    """
    
    # Feature names for Data Fusion Model (20 features)
    FEATURE_NAMES = [
        # Cognitive (5)
        'mmse_score', 'moca_score', 'memory_score', 'attention_score', 'executive_function_score',
        # Biomarkers (4)
        'amyloid_beta', 'tau_protein', 'dopamine_level', 'apoe_e4_status',
        # Imaging (5)
        'hippocampal_volume', 'cortical_thickness', 'ventricular_volume', 
        'white_matter_hyperintensities', 'brain_volume_total',
        # Demographics (3)
        'age', 'gender', 'education_years',
        # Additional (3)
        'cognitive_completeness', 'biomarker_completeness', 'imaging_completeness'
    ]
    
    # Anatomical region mapping for imaging features
    ANATOMICAL_REGIONS = {
        'hippocampal_volume': 'Hippocampus',
        'cortical_thickness': 'Cerebral Cortex',
        'ventricular_volume': 'Ventricular System',
        'white_matter_hyperintensities': 'White Matter',
        'brain_volume_total': 'Whole Brain'
    }
    
    # Cognitive domain mapping
    COGNITIVE_DOMAINS = {
        'mmse_score': 'Global Cognition',
        'moca_score': 'Global Cognition',
        'memory_score': 'Memory',
        'attention_score': 'Attention',
        'executive_function_score': 'Executive Function'
    }
    
    # Biomarker category mapping
    BIOMARKER_CATEGORIES = {
        'amyloid_beta': 'Alzheimer Biomarker',
        'tau_protein': 'Alzheimer Biomarker',
        'dopamine_level': 'Parkinson Biomarker',
        'apoe_e4_status': 'Genetic Risk Factor'
    }
    
    def __init__(self, model: Optional[DataFusionScoringModel] = None, device: Optional[torch.device] = None):
        """
        Initialize Data Fusion XAI Service
        
        Args:
            model: Trained DataFusionScoringModel
            device: Device to run on (cuda or cpu)
        """
        self.model = model
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device
        
        if self.model:
            self.model.to(self.device)
            self.model.eval()
    
    def compute_integrated_gradients(
        self,
        input_tensor: torch.Tensor,
        target_output: str = 'integrated_fusion_score',
        baseline: Optional[torch.Tensor] = None,
        steps: int = 50
    ) -> Dict[str, np.ndarray]:
        """
        PATENT CLAIM 3(b): Compute Integrated Gradients for accurate attribution
        
        Mathematical formulation:
        IG_i(x) = (x_i - baseline_i) × ∫[α=0 to 1] (∂F(x' + α(x - x')) / ∂x_i) dα
        
        This satisfies two axioms:
        1. Sensitivity: If input and baseline differ in one feature and prediction differs,
           that feature gets non-zero attribution
        2. Implementation Invariance: Attributions are identical for functionally equivalent models
        
        Args:
            input_tensor: Input feature tensor [batch_size, features]
            target_output: Which output to explain ('integrated_fusion_score', 'cognitive_score', etc.)
            baseline: Baseline tensor (zeros if None)
            steps: Number of integration steps
        
        Returns:
            Dictionary with attributions for each feature
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Cannot compute Integrated Gradients.")
        
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
            outputs = self.model(interpolated)
            target = outputs[target_output]
            
            # Backward pass
            target.backward(torch.ones_like(target))
            
            # Accumulate gradients
            integrated_grads += interpolated.grad
        
        # Average and multiply by difference
        integrated_grads /= steps
        attribution = (input_tensor - baseline) * integrated_grads
        
        # Convert to numpy and create feature-wise attribution
        attribution_np = attribution.cpu().detach().numpy()[0]
        
        return {
            'attribution': attribution_np,
            'feature_importance': dict(zip(self.FEATURE_NAMES, attribution_np)),
            'method': 'integrated_gradients',
            'steps': steps
        }
    
    def compute_gradient_saliency(
        self,
        input_tensor: torch.Tensor,
        target_output: str = 'integrated_fusion_score'
    ) -> Dict[str, np.ndarray]:
        """
        PATENT CLAIM 3(a): Compute gradient-based saliency map
        
        Mathematical formulation:
        S(x) = |∂y/∂x|
        
        where y is the output prediction and x is the input
        
        Args:
            input_tensor: Input feature tensor
            target_output: Which output to explain
        
        Returns:
            Dictionary with saliency map
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Cannot compute saliency.")
        
        input_tensor = input_tensor.to(self.device).requires_grad_(True)
        
        # Forward pass
        outputs = self.model(input_tensor)
        target = outputs[target_output]
        
        # Backward pass
        target.backward(torch.ones_like(target))
        
        # Get gradients
        saliency = input_tensor.grad.abs().cpu().detach().numpy()[0]
        
        return {
            'saliency': saliency,
            'feature_importance': dict(zip(self.FEATURE_NAMES, saliency)),
            'method': 'gradient_saliency'
        }
    
    def map_to_anatomical_regions(
        self,
        attributions: np.ndarray
    ) -> Dict[str, Dict[str, float]]:
        """
        PATENT CLAIM 3(c): Map attributions to anatomical brain regions
        
        Maps feature attributions to anatomical regions for clinical interpretation
        
        Args:
            attributions: Feature attribution array
        
        Returns:
            Dictionary mapping anatomical regions to their total attribution
        """
        region_attributions = {}
        
        # Map imaging features to anatomical regions
        for i, feature_name in enumerate(self.FEATURE_NAMES):
            if feature_name in self.ANATOMICAL_REGIONS:
                region = self.ANATOMICAL_REGIONS[feature_name]
                if region not in region_attributions:
                    region_attributions[region] = {
                        'total_attribution': 0.0,
                        'features': []
                    }
                region_attributions[region]['total_attribution'] += abs(attributions[i])
                region_attributions[region]['features'].append({
                    'feature': feature_name,
                    'attribution': float(attributions[i])
                })
        
        # Normalize by total attribution
        total = sum(r['total_attribution'] for r in region_attributions.values())
        if total > 0:
            for region in region_attributions:
                region_attributions[region]['normalized_attribution'] = \
                    region_attributions[region]['total_attribution'] / total
        else:
            for region in region_attributions:
                region_attributions[region]['normalized_attribution'] = 0.0
        
        return region_attributions
    
    def generate_dynamic_evidence(
        self,
        medical_record: MedicalRecord,
        patient: Patient,
        fusion_scores: Dict[str, float],
        method: str = 'integrated_gradients'
    ) -> Dict[str, Any]:
        """
        PATENT CLAIM 3: Generate dynamic evidence for clinical interpretation
        
        This method generates comprehensive, dynamic evidence that directly supports
        Patent Claim 3 by providing:
        1. Feature-level attributions
        2. Anatomical region mapping
        3. Modality-specific contributions
        4. Clinical interpretation guidance
        
        Args:
            medical_record: Medical record with patient data
            patient: Patient information
            fusion_scores: Predicted fusion scores
            method: XAI method to use ('integrated_gradients' or 'gradient_saliency')
        
        Returns:
            Comprehensive dynamic evidence dictionary
        """
        if self.model is None:
            logger.warning("Model not loaded. Generating simplified evidence.")
            return self._generate_simplified_evidence(medical_record, patient, fusion_scores)
        
        # Extract features
        from .data_fusion_service import DataFusionService
        features = DataFusionService._extract_features_for_model(medical_record, patient)
        features_tensor = torch.FloatTensor(features).unsqueeze(0).to(self.device)
        
        # Compute attributions for key outputs
        evidence = {
            'timestamp': datetime.now().isoformat(),
            'patient_id': patient.id,
            'medical_record_id': medical_record.id,
            'fusion_scores': fusion_scores,
            'explanations': {},
            'anatomical_regions': {},
            'modality_contributions': {},
            'clinical_evidence': {},
            'patent_claim_3_support': True
        }
        
        # Explain integrated fusion score
        if method == 'integrated_gradients':
            ig_result = self.compute_integrated_gradients(
                features_tensor,
                target_output='integrated_fusion_score'
            )
            evidence['explanations']['integrated_fusion'] = ig_result
            attributions = ig_result['attribution']
        else:
            saliency_result = self.compute_gradient_saliency(
                features_tensor,
                target_output='integrated_fusion_score'
            )
            evidence['explanations']['integrated_fusion'] = saliency_result
            attributions = saliency_result['saliency']
        
        # Map to anatomical regions (PATENT CLAIM 3(c))
        evidence['anatomical_regions'] = self.map_to_anatomical_regions(attributions)
        
        # Modality-specific contributions
        evidence['modality_contributions'] = self._compute_modality_contributions(attributions)
        
        # Cognitive domain contributions
        evidence['cognitive_domains'] = self._compute_cognitive_domain_contributions(attributions)
        
        # Biomarker category contributions
        evidence['biomarker_categories'] = self._compute_biomarker_category_contributions(attributions)
        
        # Top contributing features
        top_features = sorted(
            zip(self.FEATURE_NAMES, attributions),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:10]
        evidence['top_contributing_features'] = [
            {
                'feature': name,
                'attribution': float(attr),
                'category': self._get_feature_category(name)
            }
            for name, attr in top_features
        ]
        
        # Clinical evidence generation
        evidence['clinical_evidence'] = self._generate_clinical_evidence(
            attributions,
            fusion_scores,
            medical_record,
            patient
        )
        
        # Visual saliency map data (PATENT CLAIM 3(d))
        evidence['visual_saliency'] = self._prepare_visual_saliency_data(attributions)
        
        return evidence
    
    def _compute_modality_contributions(self, attributions: np.ndarray) -> Dict[str, float]:
        """Compute contribution of each modality"""
        contributions = {
            'cognitive': 0.0,
            'biomarker': 0.0,
            'imaging': 0.0,
            'demographic': 0.0
        }
        
        # Cognitive features (indices 0-4)
        contributions['cognitive'] = float(np.sum(np.abs(attributions[0:5])))
        
        # Biomarker features (indices 5-8)
        contributions['biomarker'] = float(np.sum(np.abs(attributions[5:9])))
        
        # Imaging features (indices 9-13)
        contributions['imaging'] = float(np.sum(np.abs(attributions[9:14])))
        
        # Demographic features (indices 14-16)
        contributions['demographic'] = float(np.sum(np.abs(attributions[14:17])))
        
        # Normalize
        total = sum(contributions.values())
        if total > 0:
            for key in contributions:
                contributions[key] /= total
        
        return contributions
    
    def _compute_cognitive_domain_contributions(self, attributions: np.ndarray) -> Dict[str, float]:
        """Compute contribution of each cognitive domain"""
        domain_contributions = {}
        
        for i, feature_name in enumerate(self.FEATURE_NAMES):
            if feature_name in self.COGNITIVE_DOMAINS:
                domain = self.COGNITIVE_DOMAINS[feature_name]
                if domain not in domain_contributions:
                    domain_contributions[domain] = 0.0
                domain_contributions[domain] += abs(attributions[i])
        
        # Normalize
        total = sum(domain_contributions.values())
        if total > 0:
            for domain in domain_contributions:
                domain_contributions[domain] /= total
        
        return domain_contributions
    
    def _compute_biomarker_category_contributions(self, attributions: np.ndarray) -> Dict[str, float]:
        """Compute contribution of each biomarker category"""
        category_contributions = {}
        
        for i, feature_name in enumerate(self.FEATURE_NAMES):
            if feature_name in self.BIOMARKER_CATEGORIES:
                category = self.BIOMARKER_CATEGORIES[feature_name]
                if category not in category_contributions:
                    category_contributions[category] = 0.0
                category_contributions[category] += abs(attributions[i])
        
        # Normalize
        total = sum(category_contributions.values())
        if total > 0:
            for category in category_contributions:
                category_contributions[category] /= total
        
        return category_contributions
    
    def _get_feature_category(self, feature_name: str) -> str:
        """Get category for a feature"""
        if feature_name in self.ANATOMICAL_REGIONS:
            return 'Imaging'
        elif feature_name in self.COGNITIVE_DOMAINS:
            return 'Cognitive'
        elif feature_name in self.BIOMARKER_CATEGORIES:
            return 'Biomarker'
        elif feature_name in ['age', 'gender', 'education_years']:
            return 'Demographic'
        else:
            return 'Other'
    
    def _generate_clinical_evidence(
        self,
        attributions: np.ndarray,
        fusion_scores: Dict[str, float],
        medical_record: MedicalRecord,
        patient: Patient
    ) -> Dict[str, Any]:
        """Generate clinical interpretation evidence"""
        evidence = {
            'primary_modality': None,
            'key_findings': [],
            'supporting_features': [],
            'conflicting_indicators': [],
            'confidence_factors': []
        }
        
        # Determine primary contributing modality
        modality_contributions = self._compute_modality_contributions(attributions)
        primary_modality = max(modality_contributions.items(), key=lambda x: x[1])[0]
        evidence['primary_modality'] = primary_modality
        
        # Identify key findings
        top_features = sorted(
            zip(self.FEATURE_NAMES, attributions),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]
        
        for feature_name, attr in top_features:
            if abs(attr) > 0.1:  # Significant contribution
                evidence['key_findings'].append({
                    'feature': feature_name,
                    'contribution': float(attr),
                    'interpretation': self._interpret_feature_contribution(feature_name, attr, medical_record)
                })
        
        # Supporting features
        positive_contributions = [f for f in top_features if f[1] > 0]
        evidence['supporting_features'] = [
            {'feature': name, 'contribution': float(attr)}
            for name, attr in positive_contributions[:3]
        ]
        
        # Confidence factors
        if fusion_scores.get('fusion_confidence'):
            evidence['confidence_factors'].append({
                'factor': 'Model Confidence',
                'value': fusion_scores['fusion_confidence'],
                'interpretation': 'High' if fusion_scores['fusion_confidence'] > 0.8 else 'Moderate' if fusion_scores['fusion_confidence'] > 0.5 else 'Low'
            })
        
        return evidence
    
    def _interpret_feature_contribution(
        self,
        feature_name: str,
        attribution: float,
        medical_record: MedicalRecord
    ) -> str:
        """Generate human-readable interpretation of feature contribution"""
        feature_value = getattr(medical_record, feature_name, None)
        
        if feature_name == 'hippocampal_volume' and feature_value:
            if attribution > 0.1:
                return f"Hippocampal volume ({feature_value:.0f} mm³) is a strong positive indicator"
            elif attribution < -0.1:
                return f"Reduced hippocampal volume ({feature_value:.0f} mm³) indicates risk"
        
        elif feature_name == 'amyloid_beta' and feature_value:
            if attribution < -0.1:
                return f"Low amyloid-beta ({feature_value:.0f} pg/mL) strongly supports Alzheimer's risk"
        
        elif feature_name == 'mmse_score' and feature_value:
            if attribution < -0.1:
                return f"MMSE score ({feature_value:.1f}) indicates cognitive impairment"
        
        return f"Feature {feature_name} contributes {'positively' if attribution > 0 else 'negatively'} to the assessment"
    
    def _prepare_visual_saliency_data(self, attributions: np.ndarray) -> Dict[str, Any]:
        """
        PATENT CLAIM 3(d): Prepare visual saliency map data
        
        Prepares data structure for visual display of saliency maps
        """
        return {
            'feature_attributions': {
                name: float(attr) for name, attr in zip(self.FEATURE_NAMES, attributions)
            },
            'anatomical_regions': self.map_to_anatomical_regions(attributions),
            'modality_heatmap': self._compute_modality_contributions(attributions),
            'normalized_attributions': (attributions / (np.abs(attributions).max() + 1e-8)).tolist()
        }
    
    def _generate_simplified_evidence(
        self,
        medical_record: MedicalRecord,
        patient: Patient,
        fusion_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Fallback simplified evidence when model not available"""
        return {
            'timestamp': datetime.now().isoformat(),
            'patient_id': patient.id,
            'medical_record_id': medical_record.id,
            'fusion_scores': fusion_scores,
            'note': 'Advanced XAI requires trained model. Using simplified evidence.',
            'patent_claim_3_support': False
        }


# Global instance
_data_fusion_xai_service = None


def get_data_fusion_xai_service(model: Optional[DataFusionScoringModel] = None) -> DataFusionXAIService:
    """Get or create the global Data Fusion XAI service instance"""
    global _data_fusion_xai_service
    if _data_fusion_xai_service is None or model is not None:
        _data_fusion_xai_service = DataFusionXAIService(model)
    return _data_fusion_xai_service

