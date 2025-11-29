"""
Deep Learning Model for Data Fusion Scoring
This model replaces manual score calculations with learned predictions
"""
import torch
import torch.nn as nn
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class DataFusionScoringModel(nn.Module):
    """
    Deep Learning model for predicting data fusion scores
    
    Input: Medical record features (cognitive, biomarker, imaging data)
    Output: All fusion scores including:
    - cognitive_score, biomarker_score, imaging_score
    - integrated_fusion_score
    - alzheimer_fusion_score, parkinson_fusion_score
    - correlations (cognitive_biomarker, cognitive_imaging, biomarker_imaging)
    - confidences
    """
    
    def __init__(self, input_dim: int = 20, hidden_dims: list = [128, 64, 32]):
        super(DataFusionScoringModel, self).__init__()
        
        # Feature extraction layers
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.Dropout(0.2))
            prev_dim = hidden_dim
        
        self.feature_extractor = nn.Sequential(*layers)
        
        # Modality score heads
        self.cognitive_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()  # Output 0-1, will be scaled to 0-100
        )
        
        self.biomarker_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        
        self.imaging_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        
        # Confidence heads
        self.cognitive_conf_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
        self.biomarker_conf_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
        self.imaging_conf_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
        # Integrated fusion score head
        self.fusion_head = nn.Sequential(
            nn.Linear(hidden_dims[-1] + 3, 32),  # +3 for modality scores
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        # Correlation heads
        self.cog_bio_corr_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
        self.cog_img_corr_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
        self.bio_img_corr_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
        # Disease-specific fusion heads
        self.alzheimer_fusion_head = nn.Sequential(
            nn.Linear(hidden_dims[-1] + 3, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        self.parkinson_fusion_head = nn.Sequential(
            nn.Linear(hidden_dims[-1] + 3, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        # Alzheimer-specific metrics
        self.alzheimer_concordance_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
        self.alzheimer_alignment_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
        self.alzheimer_hippo_corr_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
        # Parkinson-specific metrics
        self.parkinson_concordance_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
        self.parkinson_alignment_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        
        self.parkinson_corr_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input features [batch_size, input_dim]
        
        Returns:
            Dictionary with all predicted scores
        """
        features = self.feature_extractor(x)
        
        # Modality scores (0-1, will be scaled to 0-100)
        cognitive_score = self.cognitive_head(features) * 100.0
        biomarker_score = self.biomarker_head(features) * 100.0
        imaging_score = self.imaging_head(features) * 100.0
        
        # Confidences (0-1)
        cognitive_conf = self.cognitive_conf_head(features)
        biomarker_conf = self.biomarker_conf_head(features)
        imaging_conf = self.imaging_conf_head(features)
        
        # Correlations (0-1)
        cog_bio_corr = self.cog_bio_corr_head(features)
        cog_img_corr = self.cog_img_corr_head(features)
        bio_img_corr = self.bio_img_corr_head(features)
        
        # Integrated fusion score (uses modality scores as input)
        fusion_input = torch.cat([
            features,
            cognitive_score / 100.0,
            biomarker_score / 100.0,
            imaging_score / 100.0
        ], dim=1)
        integrated_fusion_score = self.fusion_head(fusion_input) * 100.0
        
        # Disease-specific fusion scores
        alzheimer_fusion_score = self.alzheimer_fusion_head(fusion_input) * 100.0
        parkinson_fusion_score = self.parkinson_fusion_head(fusion_input) * 100.0
        
        # Alzheimer-specific metrics
        alzheimer_concordance = self.alzheimer_concordance_head(features) * 100.0
        alzheimer_alignment = self.alzheimer_alignment_head(features) * 100.0
        alzheimer_hippo_corr = self.alzheimer_hippo_corr_head(features) * 100.0
        
        # Parkinson-specific metrics
        parkinson_concordance = self.parkinson_concordance_head(features) * 100.0
        parkinson_alignment = self.parkinson_alignment_head(features) * 100.0
        parkinson_corr = self.parkinson_corr_head(features) * 100.0
        
        return {
            'cognitive_score': cognitive_score,
            'biomarker_score': biomarker_score,
            'imaging_score': imaging_score,
            'cognitive_confidence': cognitive_conf,
            'biomarker_confidence': biomarker_conf,
            'imaging_confidence': imaging_conf,
            'cognitive_biomarker_correlation': cog_bio_corr,
            'cognitive_imaging_correlation': cog_img_corr,
            'biomarker_imaging_correlation': bio_img_corr,
            'integrated_fusion_score': integrated_fusion_score,
            'alzheimer_fusion_score': alzheimer_fusion_score,
            'parkinson_fusion_score': parkinson_fusion_score,
            'alzheimer_concordance': alzheimer_concordance,
            'alzheimer_alignment': alzheimer_alignment,
            'alzheimer_hippo_corr': alzheimer_hippo_corr,
            'parkinson_concordance': parkinson_concordance,
            'parkinson_alignment': parkinson_alignment,
            'parkinson_corr': parkinson_corr,
        }

