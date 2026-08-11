"""
Drift monitoring for a deployed model.

ModelRegistry answers "which model is active and what did it score at
validation time?" It cannot answer "does that score still hold today?" — once
a model is serving traffic, two things can quietly invalidate it:

1. Feature drift — incoming patient data no longer resembles the population
   the model was trained and validated on.
2. Performance drift — once ground-truth outcomes come back, the deployed
   model's real-world accuracy has fallen away from its validated baseline.

State persists to a JSON file, matching ModelRegistry's own storage pattern —
no database migration is required to start using this.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Population Stability Index conventions used across the credit-risk and
# clinical-ML literature: <0.1 stable, 0.1-0.2 worth a look, >0.2 the
# population has meaningfully changed.
PSI_MODERATE_THRESHOLD = 0.1
PSI_SIGNIFICANT_THRESHOLD = 0.2

# A rolling accuracy drop this large from the validated baseline is treated as
# performance degradation, not noise.
PERFORMANCE_DEGRADATION_THRESHOLD = 0.10


def population_stability_index(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    """
    Compare one feature's distribution now against its distribution at
    training time, binned by the reference distribution's own quantiles.
    """
    reference = reference[~np.isnan(reference)]
    current = current[~np.isnan(current)]
    if len(reference) == 0 or len(current) == 0:
        return 0.0

    edges = np.quantile(reference, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    edges = np.unique(edges)
    if len(edges) < 3:
        # Reference feature has near-zero variance — PSI isn't meaningful here.
        return 0.0

    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)
    ref_pct = np.clip(ref_counts / max(len(reference), 1), 1e-4, None)
    cur_pct = np.clip(cur_counts / max(len(current), 1), 1e-4, None)
    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


class DriftMonitor:
    """Tracks feature and performance drift for one active model version."""

    def __init__(self, state_path: Optional[Path] = None):
        self.state_path = Path(state_path) if state_path else Path("models") / "drift_state.json"
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load()

    def _load(self) -> Dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text())
            except Exception as e:
                logger.warning(f"Could not load drift state: {e}. Starting fresh.")
        return {'reference': {}, 'performance_log': []}

    def _save(self):
        self.state_path.write_text(json.dumps(self.state, indent=2))

    def set_reference_distribution(self, model_version: str, features: np.ndarray,
                                   feature_names: List[str], baseline_metrics: Dict):
        """
        Call once, right after a model is activated (e.g. immediately after
        ModelRegistry.register_and_maybe_activate succeeds), to snapshot the
        training-time feature distribution and validated metrics that future
        drift checks are compared against.
        """
        self.state['reference'] = {
            'model_version': model_version,
            'feature_names': list(feature_names),
            'samples': np.asarray(features).tolist(),
            'baseline_metrics': baseline_metrics,
            'captured_at': datetime.now().isoformat(),
        }
        self._save()
        logger.info(f"Drift reference distribution captured for model {model_version} ({len(features)} samples)")

    def check_feature_drift(self, current_features: np.ndarray) -> Dict:
        """
        Compare a batch of recent production inputs against the reference
        distribution. Call this periodically (e.g. daily/weekly) on a rolling
        window of recent predictions' input features.
        """
        ref = self.state.get('reference')
        if not ref:
            return {
                'status': 'no_reference',
                'message': 'No reference distribution recorded — call set_reference_distribution() first',
            }

        reference = np.array(ref['samples'])
        current_features = np.asarray(current_features)
        per_feature = {}
        for i, name in enumerate(ref['feature_names']):
            psi = population_stability_index(reference[:, i], current_features[:, i])
            severity = (
                'significant' if psi > PSI_SIGNIFICANT_THRESHOLD
                else 'moderate' if psi > PSI_MODERATE_THRESHOLD
                else 'stable'
            )
            per_feature[name] = {'psi': round(psi, 4), 'severity': severity}

        drifted = [n for n, v in per_feature.items() if v['severity'] != 'stable']
        status = (
            'significant_drift' if any(v['severity'] == 'significant' for v in per_feature.values())
            else 'moderate_drift' if drifted
            else 'stable'
        )
        result = {
            'status': status,
            'model_version': ref['model_version'],
            'drifted_features': drifted,
            'per_feature': per_feature,
            'checked_at': datetime.now().isoformat(),
        }
        if status != 'stable':
            logger.warning(f"Feature drift detected ({status}) for model {ref['model_version']}: {drifted}")
        return result

    def record_outcome(self, model_version: str, predicted_proba: float, actual_label: int):
        """
        Feed back one confirmed clinical outcome (e.g. a diagnosis later
        confirmed) so check_performance_drift() has ground truth to compare
        live predictions against.
        """
        self.state.setdefault('performance_log', []).append({
            'model_version': model_version,
            'predicted_proba': float(predicted_proba),
            'actual_label': int(actual_label),
            'recorded_at': datetime.now().isoformat(),
        })
        self._save()

    def check_performance_drift(self, window: int = 50) -> Dict:
        """
        Compare rolling real-world accuracy (over the last `window` confirmed
        outcomes) against the baseline accuracy the active model was validated
        at. Returns 'insufficient_data' until enough outcomes have been fed
        back — a handful of samples would make this noise, not a finding.
        """
        ref = self.state.get('reference')
        log = self.state.get('performance_log', [])
        if not ref:
            return {'status': 'no_reference', 'message': 'No reference distribution recorded'}
        if len(log) < window:
            return {'status': 'insufficient_data', 'have': len(log), 'need': window}

        recent = log[-window:]
        preds = np.array([r['predicted_proba'] >= 0.5 for r in recent]).astype(int)
        actuals = np.array([r['actual_label'] for r in recent])
        rolling_accuracy = float((preds == actuals).mean())

        baseline_accuracy = ref['baseline_metrics'].get('accuracy')
        degraded = (
            baseline_accuracy is not None
            and (baseline_accuracy - rolling_accuracy) > PERFORMANCE_DEGRADATION_THRESHOLD
        )
        result = {
            'status': 'degraded' if degraded else 'stable',
            'model_version': ref['model_version'],
            'rolling_accuracy': rolling_accuracy,
            'baseline_accuracy': baseline_accuracy,
            'window': window,
            'checked_at': datetime.now().isoformat(),
        }
        if degraded:
            logger.warning(
                f"Performance drift detected for model {ref['model_version']}: "
                f"rolling accuracy {rolling_accuracy:.4f} vs. baseline {baseline_accuracy:.4f}"
            )
        return result
