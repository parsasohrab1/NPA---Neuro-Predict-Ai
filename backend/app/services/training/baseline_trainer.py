"""
Classical-ML baselines for disease prediction.

The deep MultiModalNeuralNetwork in ai_model_service.py is only worth its added
complexity, training cost, and reduced interpretability if it actually beats a
simple baseline by a meaningful margin. This module trains Logistic Regression
and Random Forest on the same feature matrix and split as the deep model so the
two can be compared fairly, and exposes a helper that turns that comparison into
an explicit go/no-go recommendation instead of assuming the deep model wins.
"""
import logging
from typing import Dict

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

logger = logging.getLogger(__name__)

# class_weight='balanced' mirrors the pos_weight handling used for the deep
# model's loss (see ModelTrainer._compute_pos_weight) so neither side gets an
# unfair advantage from how it handles the same class imbalance.
BASELINE_MODEL_FACTORIES = {
    'logistic_regression': lambda seed: LogisticRegression(
        max_iter=1000, class_weight='balanced', random_state=seed
    ),
    'random_forest': lambda seed: RandomForestClassifier(
        n_estimators=300, max_depth=8, class_weight='balanced',
        random_state=seed, n_jobs=-1,
    ),
}


class BaselineTrainer:
    """Trains and evaluates classical baselines for one disease target."""

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self.fitted_models: Dict[str, object] = {}

    def fit_and_evaluate(self,
                          X_train: np.ndarray, y_train: np.ndarray,
                          X_test: np.ndarray, y_test: np.ndarray,
                          disease_name: str = "disease") -> Dict[str, Dict]:
        """
        Fit each baseline on (X_train, y_train) and score it on (X_test, y_test).
        Pass in the exact same patient-level split used for the deep model —
        comparing against a different split would make the margin meaningless.
        """
        results: Dict[str, Dict] = {}
        for name, factory in BASELINE_MODEL_FACTORIES.items():
            model = factory(self.random_seed)
            model.fit(X_train, y_train)
            proba = model.predict_proba(X_test)[:, 1]
            preds = (proba >= 0.5).astype(int)

            results[name] = {
                'accuracy': float(accuracy_score(y_test, preds)),
                'precision': float(precision_score(y_test, preds, zero_division=0)),
                'recall': float(recall_score(y_test, preds, zero_division=0)),
                'f1': float(f1_score(y_test, preds, zero_division=0)),
                'auc_roc': float(roc_auc_score(y_test, proba)) if len(np.unique(y_test)) > 1 else 0.0,
            }
            self.fitted_models[f"{disease_name}_{name}"] = model
            logger.info(
                f"[baseline:{name}] {disease_name} — "
                f"AUC={results[name]['auc_roc']:.4f} F1={results[name]['f1']:.4f}"
            )
        return results

    @staticmethod
    def deep_model_justified(deep_auc: float, baseline_results: Dict[str, Dict],
                              margin: float = 0.02) -> Dict:
        """
        The deep model earns its complexity only if it beats the best classical
        baseline's AUC-ROC by more than `margin`. Below that, the simpler,
        cheaper, more interpretable baseline should be preferred — an
        interpretable Logistic Regression is also an easier regulatory story
        than an unexplained neural network.

        Returns the comparison plus an explicit boolean verdict — never assume
        the deep model wins by default.
        """
        best_baseline_name = max(baseline_results, key=lambda k: baseline_results[k]['auc_roc'])
        best_baseline_auc = baseline_results[best_baseline_name]['auc_roc']
        margin_achieved = deep_auc - best_baseline_auc
        justified = margin_achieved > margin

        verdict = {
            'deep_auc': deep_auc,
            'best_baseline': best_baseline_name,
            'best_baseline_auc': best_baseline_auc,
            'margin_achieved': margin_achieved,
            'margin_required': margin,
            'deep_model_justified': justified,
        }
        logger.info(
            f"Deep vs. baseline: deep AUC={deep_auc:.4f}, "
            f"best baseline ({best_baseline_name}) AUC={best_baseline_auc:.4f}, "
            f"margin={margin_achieved:+.4f} -> "
            f"{'deep model justified' if justified else 'baseline preferred'}"
        )
        return verdict
