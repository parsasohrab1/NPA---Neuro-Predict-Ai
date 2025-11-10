"""
Model Registry for Versioning and Management
"""
import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Registry for managing model versions"""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize model registry
        
        Args:
            registry_path: Path to registry file. If None, uses default models/registry.json
        """
        if registry_path is None:
            registry_path = Path("models") / "registry.json"
        
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load registry from file"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load registry: {e}. Creating new registry.")
                return {'models': [], 'current_model': None}
        else:
            return {'models': [], 'current_model': None}
    
    def _save_registry(self):
        """Save registry to file"""
        try:
            with open(self.registry_path, 'w') as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save registry: {e}")
    
    def register_model(self, model_path: Path, metrics: Dict,
                      version: Optional[str] = None,
                      description: Optional[str] = None) -> str:
        """
        Register a new model version
        
        Args:
            model_path: Path to model file
            metrics: Training/evaluation metrics
            version: Model version (if None, auto-generated)
            description: Model description
        
        Returns:
            Model version string
        """
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_entry = {
            'version': version,
            'model_path': str(model_path),
            'created_at': datetime.now().isoformat(),
            'metrics': metrics,
            'description': description or f"Model trained on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            'is_active': False
        }
        
        self.registry['models'].append(model_entry)
        self._save_registry()
        
        logger.info(f"Registered model version {version}")
        return version
    
    def set_active_model(self, version: str) -> bool:
        """
        Set a model version as active
        
        Args:
            version: Model version to activate
        
        Returns:
            True if successful, False otherwise
        """
        # Deactivate all models
        for model in self.registry['models']:
            model['is_active'] = False
        
        # Activate specified model
        for model in self.registry['models']:
            if model['version'] == version:
                model['is_active'] = True
                self.registry['current_model'] = version
                self._save_registry()
                logger.info(f"Activated model version {version}")
                return True
        
        logger.warning(f"Model version {version} not found")
        return False
    
    def get_active_model(self) -> Optional[Dict]:
        """Get the currently active model"""
        if self.registry['current_model']:
            return self.get_model(self.registry['current_model'])
        return None
    
    def get_model(self, version: str) -> Optional[Dict]:
        """Get model by version"""
        for model in self.registry['models']:
            if model['version'] == version:
                return model
        return None
    
    def list_models(self) -> List[Dict]:
        """List all registered models"""
        return self.registry['models']
    
    def get_latest_model(self) -> Optional[Dict]:
        """Get the latest model by creation date"""
        if not self.registry['models']:
            return None
        
        return max(self.registry['models'], key=lambda x: x['created_at'])

