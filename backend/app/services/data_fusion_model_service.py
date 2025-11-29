"""
Service for loading and using the trained Data Fusion Deep Learning Model
"""
import torch
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging
import pickle

from .data_fusion_model import DataFusionScoringModel
from .data_fusion_xai_service import get_data_fusion_xai_service
from ..core.config import settings

logger = logging.getLogger(__name__)


class DataFusionModelService:
    """Service for using trained data fusion model"""
    
    def __init__(self):
        self.model: Optional[DataFusionScoringModel] = None
        self.scaler = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load the trained model and scaler"""
        try:
            # Try to find the latest model
            model_dir = Path(settings.MODEL_REGISTRY_PATH).parent if hasattr(settings, 'MODEL_REGISTRY_PATH') else Path("backend/models")
            
            # Look for data fusion model files
            model_files = list(model_dir.glob("data_fusion_model_*.pth"))
            scaler_file = model_dir / "data_fusion_scaler.pkl"
            
            if not model_files:
                logger.warning("No trained data fusion model found. Using manual calculations.")
                return
            
            # Load latest model
            latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"Loading data fusion model from {latest_model}")
            
            checkpoint = torch.load(latest_model, map_location=self.device)
            
            # Initialize model
            input_dim = checkpoint.get('input_dim', 20)
            self.model = DataFusionScoringModel(input_dim=input_dim)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            
            # Load scaler
            if scaler_file.exists():
                with open(scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info(f"Loaded scaler from {scaler_file}")
            else:
                logger.warning("Scaler file not found. Model may not work correctly.")
            
            self._loaded = True
            logger.info("Data fusion model loaded successfully")
            
            # Initialize XAI service with loaded model
            try:
                from .data_fusion_xai_service import get_data_fusion_xai_service
                get_data_fusion_xai_service(self.model)
                logger.info("Data Fusion XAI service initialized")
            except Exception as e:
                logger.warning(f"Could not initialize XAI service: {e}")
            
        except Exception as e:
            logger.error(f"Error loading data fusion model: {e}")
            logger.warning("Falling back to manual calculations")
            self._loaded = False
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._loaded
    
    def predict_scores(self, features: np.ndarray) -> Dict[str, float]:
        """
        Predict all fusion scores from features
        
        Args:
            features: Feature array [20] - normalized features from medical record
        
        Returns:
            Dictionary with all predicted scores
        """
        if not self._loaded or self.model is None:
            raise RuntimeError("Model not loaded. Cannot make predictions.")
        
        # Normalize features if scaler is available
        if self.scaler is not None:
            features = self.scaler.transform(features.reshape(1, -1))
        else:
            features = features.reshape(1, -1)
        
        # Convert to tensor
        features_tensor = torch.FloatTensor(features).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(features_tensor)
        
        # Convert to numpy and extract values
        results = {}
        for key, value in outputs.items():
            val = value.cpu().numpy()[0]
            if isinstance(val, np.ndarray):
                val = val[0] if len(val) > 0 else 0.0
            
            # Scale scores back to 0-100 range
            if key.endswith('_score') or key in ['alzheimer_concordance', 'alzheimer_alignment', 
                                                  'alzheimer_hippo_corr', 'parkinson_concordance',
                                                  'parkinson_alignment', 'parkinson_corr']:
                results[key] = float(val)
            else:
                # Confidences and correlations are already 0-1
                results[key] = float(val)
        
        return results


# Global instance
_data_fusion_model_service = None


def get_data_fusion_model_service() -> DataFusionModelService:
    """Get or create the global data fusion model service instance"""
    global _data_fusion_model_service
    if _data_fusion_model_service is None:
        _data_fusion_model_service = DataFusionModelService()
    return _data_fusion_model_service

