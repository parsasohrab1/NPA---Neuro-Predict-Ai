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

    # Minimum clinical metrics a model must clear before it can become the
    # active model. Keyed to match ClinicalValidator's flattened output
    # (e.g. {'alzheimer_auc_roc': ..., 'parkinson_auc_roc': ...}). Callers may
    # override per-call via register_and_maybe_activate(thresholds=...).
    DEFAULT_QUALITY_THRESHOLDS: Dict[str, float] = {
        'alzheimer_auc_roc': 0.75,
        'parkinson_auc_roc': 0.75,
    }

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

    def passes_quality_gate(self, gate_metrics: Dict, thresholds: Optional[Dict] = None) -> Dict:
        """
        Check flattened clinical metrics (e.g. {'alzheimer_auc_roc': 0.81, ...})
        against minimum thresholds. Returns per-check pass/fail so a human
        reviewing a rejected run can see exactly which metric fell short,
        instead of a single opaque True/False.
        """
        thresholds = thresholds or self.DEFAULT_QUALITY_THRESHOLDS
        checks = {}
        for key, min_value in thresholds.items():
            actual = gate_metrics.get(key)
            checks[key] = {
                'required': min_value,
                'actual': actual,
                'passed': actual is not None and actual >= min_value,
            }
        return {'passed': all(c['passed'] for c in checks.values()), 'checks': checks}

    def register_and_maybe_activate(self, model_path: Path, metrics: Dict,
                                    gate_metrics: Dict,
                                    version: Optional[str] = None,
                                    description: Optional[str] = None,
                                    thresholds: Optional[Dict] = None,
                                    force: bool = False) -> Dict:
        """
        The only sanctioned path from a training run to a live model.

        register_model() and set_active_model() are NOT called automatically
        after every run — only once `gate_metrics` clears `thresholds` (or a
        human explicitly overrides via force=True, which is logged as such). A
        run that fails the gate is neither registered nor activated: it leaves
        no registry entry, so registry.list_models() only ever shows models
        that were actually considered fit to serve (or were force-activated,
        which is visible in the logs).

        Args:
            gate_metrics: flattened metrics checked against `thresholds`,
                e.g. {'alzheimer_auc_roc': ..., 'parkinson_auc_roc': ...}
                (see ClinicalValidator.validate_model()).
            force: activate despite a failed gate — an explicit human decision,
                never a default. Still gets registered and logged with the
                failed checks so the override is auditable.

        Returns:
            {'version': str | None, 'gate': {...}, 'registered': bool, 'activated': bool}
        """
        gate = self.passes_quality_gate(gate_metrics, thresholds)

        if not gate['passed'] and not force:
            logger.warning(f"Model NOT registered — failed quality gate: {gate['checks']}")
            return {'version': None, 'gate': gate, 'registered': False, 'activated': False}

        version = self.register_model(model_path, metrics, version=version, description=description)
        self.set_active_model(version)

        if not gate['passed'] and force:
            logger.warning(
                f"Model {version} registered and force-activated despite failing "
                f"quality gate: {gate['checks']}"
            )
        else:
            logger.info(f"Model {version} passed quality gate and is now active: {gate['checks']}")

        return {'version': version, 'gate': gate, 'registered': True, 'activated': True}

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
                return self._with_weights_status(model)
        return None

    def list_models(self) -> List[Dict]:
        """List all registered models, annotated with real weight-file status"""
        return [self._with_weights_status(model) for model in self.registry['models']]

    def get_latest_model(self) -> Optional[Dict]:
        """Get the latest model by creation date"""
        if not self.registry['models']:
            return None

        return self._with_weights_status(
            max(self.registry['models'], key=lambda x: x['created_at'])
        )

    def _with_weights_status(self, model: Dict) -> Dict:
        """
        Attach whether the model's weight file actually exists on disk.

        The registry is just JSON metadata — nothing stops an entry from
        claiming training metrics for a version whose .pth file was never
        produced (or was deleted). Callers (e.g. the admin API) must not
        present metrics as validated/active without checking this.
        """
        annotated = dict(model)
        model_path = model.get('model_path')
        annotated['weights_available'] = bool(model_path) and Path(model_path).exists()
        return annotated

