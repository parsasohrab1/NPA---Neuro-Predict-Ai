"""
Clinical Validation Framework
فریمورک اعتبارسنجی بالینی برای ارزیابی مدل
"""
import torch
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import json
from datetime import datetime
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, precision_recall_curve,
    confusion_matrix, classification_report
)
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


class ClinicalValidator:
    """Clinical validation service for model evaluation"""
    
    def __init__(self):
        self.validation_results = {}
        self.clinical_metrics = {}
    
    def calculate_clinical_metrics(self,
                                  y_true: np.ndarray,
                                  y_pred: np.ndarray,
                                  y_pred_proba: np.ndarray,
                                  disease_name: str = "disease") -> Dict:
        """
        Calculate comprehensive clinical metrics
        
        Args:
            y_true: True binary labels
            y_pred: Predicted binary labels
            y_pred_proba: Predicted probabilities
            disease_name: Name of disease (for reporting)
        
        Returns:
            Dictionary with all clinical metrics
        """
        # Basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        # AUC-ROC
        try:
            auc_roc = roc_auc_score(y_true, y_pred_proba) if len(np.unique(y_true)) > 1 else 0.0
        except:
            auc_roc = 0.0
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
        
        # Clinical metrics
        sensitivity = recall  # True Positive Rate
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0  # True Negative Rate
        
        # Positive and Negative Predictive Values
        ppv = precision  # Positive Predictive Value
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0  # Negative Predictive Value
        
        # Likelihood Ratios
        lr_positive = sensitivity / (1 - specificity) if (1 - specificity) > 0 else float('inf')
        lr_negative = (1 - sensitivity) / specificity if specificity > 0 else 0.0
        
        # Diagnostic Odds Ratio
        dor = (tp * tn) / (fp * fn) if (fp * fn) > 0 else float('inf')
        
        metrics = {
            'disease': disease_name,
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'auc_roc': float(auc_roc),
            'sensitivity': float(sensitivity),  # True Positive Rate
            'specificity': float(specificity),  # True Negative Rate
            'ppv': float(ppv),  # Positive Predictive Value
            'npv': float(npv),  # Negative Predictive Value
            'lr_positive': float(lr_positive) if lr_positive != float('inf') else None,
            'lr_negative': float(lr_negative),
            'dor': float(dor) if dor != float('inf') else None,
            'confusion_matrix': {
                'tn': int(tn),
                'fp': int(fp),
                'fn': int(fn),
                'tp': int(tp)
            },
            'total_samples': int(len(y_true)),
            'positive_samples': int(np.sum(y_true)),
            'negative_samples': int(len(y_true) - np.sum(y_true))
        }
        
        return metrics

    def compute_optimal_threshold(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> float:
        """
        Youden's J statistic (sensitivity + specificity - 1, maximized) — the
        clinical operating point a threshold of 0.5 was never guaranteed to be.
        Reporting sensitivity/specificity at this threshold, not just at 0.5, is
        what "clinical operating point" means in the roadmap: the point a
        clinician would actually use the model at.
        """
        if len(np.unique(y_true)) < 2:
            logger.warning("Cannot compute optimal threshold with a single class present; defaulting to 0.5")
            return 0.5
        fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
        youden_j = tpr - fpr
        best_threshold = float(thresholds[np.argmax(youden_j)])
        # roc_curve prepends an artificial threshold of +inf (the "classify
        # nothing as positive" point). If Youden's J ties there — e.g. a model
        # with ~no discriminative power — using it would make every
        # prediction negative, which isn't a usable clinical operating point.
        if not np.isfinite(best_threshold):
            logger.warning(
                f"Youden's J selected a non-finite threshold ({best_threshold}), "
                "indicating no discriminative power at this validation pass; falling back to 0.5"
            )
            return 0.5
        return best_threshold

    def compute_calibration(self, y_true: np.ndarray, y_pred_proba: np.ndarray,
                            n_bins: int = 10) -> Dict:
        """
        A model can have a strong AUC-ROC and still be poorly calibrated — e.g.
        report 90% confidence on cases that are only right 60% of the time.
        Calibration is what tells a clinician whether the predicted probability
        can be trusted at face value, not just whether the ranking is correct.
        """
        try:
            prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=n_bins, strategy='quantile')
        except ValueError as e:
            logger.warning(f"Could not compute calibration curve: {e}")
            return {'prob_true': [], 'prob_pred': [], 'expected_calibration_error': None}

        expected_calibration_error = float(np.mean(np.abs(prob_true - prob_pred)))
        return {
            'prob_true': prob_true.tolist(),
            'prob_pred': prob_pred.tolist(),
            'expected_calibration_error': expected_calibration_error,
        }

    def compute_subgroup_metrics(self, y_true: np.ndarray, y_pred_proba: np.ndarray,
                                 subgroups: Dict[str, np.ndarray],
                                 threshold: float = 0.5,
                                 min_group_size: int = 5) -> Dict:
        """
        Break sensitivity/specificity/AUC down by subgroup (e.g. gender,
        age_band) so a fairness gap is visible before deployment rather than
        discovered afterward. Groups smaller than min_group_size are flagged
        rather than scored — a metric from 3 samples is noise, not a finding.

        Args:
            subgroups: e.g. {'gender': array aligned with y_true, 'age_band': ...}
        """
        y_true = np.asarray(y_true)
        y_pred_proba = np.asarray(y_pred_proba)
        y_pred = (y_pred_proba >= threshold).astype(int)

        results: Dict[str, Dict] = {}
        for attr_name, values in subgroups.items():
            values = np.asarray(values)
            if len(values) != len(y_true):
                logger.warning(
                    f"Subgroup '{attr_name}' length ({len(values)}) does not match "
                    f"labels ({len(y_true)}); skipping"
                )
                continue

            results[attr_name] = {}
            for group in sorted(np.unique(values)):
                mask = values == group
                n = int(mask.sum())
                if n < min_group_size:
                    results[attr_name][str(group)] = {
                        'n': n,
                        'note': f'کمتر از {min_group_size} نمونه — نتیجه قابل اتکا نیست',
                    }
                    continue

                yt, yp, ypp = y_true[mask], y_pred[mask], y_pred_proba[mask]
                cm = confusion_matrix(yt, yp, labels=[0, 1])
                tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
                results[attr_name][str(group)] = {
                    'n': n,
                    'sensitivity': float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0,
                    'specificity': float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0,
                    'auc_roc': float(roc_auc_score(yt, ypp)) if len(np.unique(yt)) > 1 else None,
                }
        return results

    def validate_model(self,
                      model: torch.nn.Module,
                      test_loader: torch.utils.data.DataLoader,
                      device: torch.device,
                      threshold: Optional[float] = None,
                      subgroup_features: Optional[Dict[str, np.ndarray]] = None) -> Dict:
        """
        Validate model on test set.

        Args:
            model: Trained model
            test_loader: Test data loader (must be shuffle=False so
                subgroup_features stays aligned to the iteration order)
            device: Device to run on
            threshold: Classification threshold. If None (default), the
                clinical operating point is computed per-disease via Youden's J
                instead of assuming 0.5 is the right cutoff.
            subgroup_features: Optional dict of arrays (e.g. {'gender': ...,
                'age_band': ...}) aligned with the test set, for fairness
                breakdown. Typically trainer.test_subgroups after prepare_data().

        Returns:
            Dictionary with validation results, including calibration and
            (if subgroup_features given) per-subgroup fairness metrics.
        """
        model.eval()

        all_alzheimer_labels = []
        all_parkinson_labels = []
        all_alzheimer_proba = []
        all_parkinson_proba = []

        with torch.no_grad():
            for batch in test_loader:
                features = batch['features'].to(device)
                alzheimer_labels = batch['alzheimer'].to(device)
                parkinson_labels = batch['parkinson'].to(device)

                alzheimer_pred, parkinson_pred = model(features)

                all_alzheimer_proba.extend(alzheimer_pred.cpu().numpy())
                all_parkinson_proba.extend(parkinson_pred.cpu().numpy())
                all_alzheimer_labels.extend(alzheimer_labels.cpu().numpy())
                all_parkinson_labels.extend(parkinson_labels.cpu().numpy())

        # Convert to numpy arrays
        alzheimer_labels = np.array(all_alzheimer_labels).astype(int)
        parkinson_labels = np.array(all_parkinson_labels).astype(int)
        alzheimer_proba = np.array(all_alzheimer_proba).flatten()
        parkinson_proba = np.array(all_parkinson_proba).flatten()

        # Clinical operating point — per disease, not a shared blind 0.5
        alzheimer_threshold = threshold if threshold is not None else self.compute_optimal_threshold(alzheimer_labels, alzheimer_proba)
        parkinson_threshold = threshold if threshold is not None else self.compute_optimal_threshold(parkinson_labels, parkinson_proba)

        alzheimer_preds = (alzheimer_proba >= alzheimer_threshold).astype(int)
        parkinson_preds = (parkinson_proba >= parkinson_threshold).astype(int)

        # Calculate metrics for both diseases
        alzheimer_metrics = self.calculate_clinical_metrics(
            alzheimer_labels, alzheimer_preds, alzheimer_proba, "Alzheimer's"
        )
        alzheimer_metrics['operating_threshold'] = alzheimer_threshold
        alzheimer_metrics['calibration'] = self.compute_calibration(alzheimer_labels, alzheimer_proba)

        parkinson_metrics = self.calculate_clinical_metrics(
            parkinson_labels, parkinson_preds, parkinson_proba, "Parkinson's"
        )
        parkinson_metrics['operating_threshold'] = parkinson_threshold
        parkinson_metrics['calibration'] = self.compute_calibration(parkinson_labels, parkinson_proba)

        if subgroup_features:
            alzheimer_metrics['subgroups'] = self.compute_subgroup_metrics(
                alzheimer_labels, alzheimer_proba, subgroup_features, threshold=alzheimer_threshold
            )
            parkinson_metrics['subgroups'] = self.compute_subgroup_metrics(
                parkinson_labels, parkinson_proba, subgroup_features, threshold=parkinson_threshold
            )

        self.validation_results = {
            'alzheimer': alzheimer_metrics,
            'parkinson': parkinson_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        return self.validation_results
    
    def generate_validation_report(self, 
                                 save_path: Optional[str] = None) -> str:
        """Generate comprehensive validation report"""
        if not self.validation_results:
            return "No validation results available"
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("CLINICAL VALIDATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        for disease, metrics in [('alzheimer', self.validation_results['alzheimer']),
                                 ('parkinson', self.validation_results['parkinson'])]:
            report_lines.append(f"\n{metrics['disease']} Disease Prediction")
            report_lines.append("-" * 80)
            report_lines.append(f"Total Samples: {metrics['total_samples']}")
            report_lines.append(f"Positive Cases: {metrics['positive_samples']}")
            report_lines.append(f"Negative Cases: {metrics['negative_samples']}")
            report_lines.append("")
            
            report_lines.append("Performance Metrics:")
            report_lines.append(f"  Accuracy:        {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
            report_lines.append(f"  Precision (PPV): {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
            report_lines.append(f"  Recall (Sensitivity): {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
            report_lines.append(f"  F1 Score:        {metrics['f1_score']:.4f}")
            report_lines.append(f"  AUC-ROC:         {metrics['auc_roc']:.4f}")
            report_lines.append("")
            
            report_lines.append("Clinical Metrics:")
            report_lines.append(f"  Sensitivity (TPR): {metrics['sensitivity']:.4f} ({metrics['sensitivity']*100:.2f}%)")
            report_lines.append(f"  Specificity (TNR): {metrics['specificity']:.4f} ({metrics['specificity']*100:.2f}%)")
            report_lines.append(f"  PPV:              {metrics['ppv']:.4f} ({metrics['ppv']*100:.2f}%)")
            report_lines.append(f"  NPV:              {metrics['npv']:.4f} ({metrics['npv']*100:.2f}%)")
            report_lines.append("")
            
            if metrics['lr_positive']:
                report_lines.append(f"  LR+ (Positive Likelihood Ratio): {metrics['lr_positive']:.4f}")
            report_lines.append(f"  LR- (Negative Likelihood Ratio): {metrics['lr_negative']:.4f}")
            if metrics['dor']:
                report_lines.append(f"  DOR (Diagnostic Odds Ratio):    {metrics['dor']:.4f}")
            report_lines.append("")
            
            report_lines.append("Confusion Matrix:")
            cm = metrics['confusion_matrix']
            report_lines.append(f"  True Negatives:  {cm['tn']}")
            report_lines.append(f"  False Positives: {cm['fp']}")
            report_lines.append(f"  False Negatives: {cm['fn']}")
            report_lines.append(f"  True Positives:  {cm['tp']}")
            report_lines.append("")

            if 'operating_threshold' in metrics:
                report_lines.append(f"Clinical Operating Threshold (Youden's J): {metrics['operating_threshold']:.4f}")
                report_lines.append("(Sensitivity/Specificity above are reported at this threshold, not a blind 0.5)")
                report_lines.append("")

            calibration = metrics.get('calibration')
            if calibration and calibration.get('expected_calibration_error') is not None:
                report_lines.append(f"Calibration Error (mean |predicted - observed|): {calibration['expected_calibration_error']:.4f}")
                report_lines.append("(Lower is better; a well-ranked model can still be miscalibrated)")
                report_lines.append("")

            subgroups = metrics.get('subgroups')
            if subgroups:
                report_lines.append("Subgroup Fairness Breakdown:")
                for attr_name, groups in subgroups.items():
                    report_lines.append(f"  By {attr_name}:")
                    for group_name, group_metrics in groups.items():
                        if 'note' in group_metrics:
                            report_lines.append(f"    {group_name}: n={group_metrics['n']} — {group_metrics['note']}")
                        else:
                            auc_str = f"{group_metrics['auc_roc']:.4f}" if group_metrics['auc_roc'] is not None else "N/A"
                            report_lines.append(
                                f"    {group_name}: n={group_metrics['n']}, "
                                f"sensitivity={group_metrics['sensitivity']:.4f}, "
                                f"specificity={group_metrics['specificity']:.4f}, "
                                f"AUC={auc_str}"
                            )
                report_lines.append("")

        report_lines.append("=" * 80)
        report_lines.append("FDA/Regulatory Compliance Notes:")
        report_lines.append("- This validation report is for clinical evaluation purposes")
        report_lines.append("- All metrics should be interpreted in clinical context")
        report_lines.append("- Sensitivity and Specificity are key metrics for diagnostic tools")
        report_lines.append("- PPV and NPV depend on disease prevalence in the population")
        report_lines.append("=" * 80)
        
        report_text = "\n".join(report_lines)
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report_text)
            logger.info(f"Validation report saved to {save_path}")
        
        return report_text
    
    def plot_validation_curves(self, save_path: Optional[str] = None):
        """Plot ROC and Precision-Recall curves"""
        if not self.validation_results:
            logger.warning("No validation results to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        for idx, (disease, metrics) in enumerate([('alzheimer', self.validation_results['alzheimer']),
                                                   ('parkinson', self.validation_results['parkinson'])]):
            # Note: We need the actual predictions and labels for curves
            # This is a placeholder - in real implementation, store these during validation
            ax1 = axes[idx, 0]
            ax2 = axes[idx, 1]
            
            # ROC Curve (placeholder - would need actual probabilities)
            ax1.plot([0, 1], [0, 1], 'k--', label='Random')
            ax1.set_xlabel('False Positive Rate')
            ax1.set_ylabel('True Positive Rate')
            ax1.set_title(f"{metrics['disease']} - ROC Curve (AUC={metrics['auc_roc']:.3f})")
            ax1.legend()
            ax1.grid(True)
            
            # Precision-Recall Curve (placeholder)
            ax2.set_xlabel('Recall')
            ax2.set_ylabel('Precision')
            ax2.set_title(f"{metrics['disease']} - Precision-Recall Curve")
            ax2.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Validation curves saved to {save_path}")
        else:
            plt.show()
    
    def plot_confusion_matrices(self, save_path: Optional[str] = None):
        """Plot confusion matrices"""
        if not self.validation_results:
            logger.warning("No validation results to plot")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        for idx, (disease, metrics) in enumerate([('alzheimer', self.validation_results['alzheimer']),
                                                   ('parkinson', self.validation_results['parkinson'])]):
            cm = metrics['confusion_matrix']
            cm_array = np.array([[cm['tn'], cm['fp']],
                                [cm['fn'], cm['tp']]])
            
            sns.heatmap(cm_array, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                       xticklabels=['Negative', 'Positive'],
                       yticklabels=['Negative', 'Positive'])
            axes[idx].set_title(f"{metrics['disease']} - Confusion Matrix")
            axes[idx].set_ylabel('True Label')
            axes[idx].set_xlabel('Predicted Label')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Confusion matrices saved to {save_path}")
        else:
            plt.show()
    
    def save_results(self, filepath: str):
        """Save validation results to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        logger.info(f"Validation results saved to {filepath}")

