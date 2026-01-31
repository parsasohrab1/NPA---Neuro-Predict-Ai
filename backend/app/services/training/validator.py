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
    
    def validate_model(self,
                      model: torch.nn.Module,
                      test_loader: torch.utils.data.DataLoader,
                      device: torch.device,
                      threshold: float = 0.5) -> Dict:
        """
        Validate model on test set
        
        Args:
            model: Trained model
            test_loader: Test data loader
            device: Device to run on
            threshold: Classification threshold
        
        Returns:
            Dictionary with validation results
        """
        model.eval()
        
        all_alzheimer_preds = []
        all_parkinson_preds = []
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
                all_alzheimer_preds.extend((alzheimer_pred.cpu().numpy() > threshold).astype(int))
                all_parkinson_preds.extend((parkinson_pred.cpu().numpy() > threshold).astype(int))
                all_alzheimer_labels.extend(alzheimer_labels.cpu().numpy())
                all_parkinson_labels.extend(parkinson_labels.cpu().numpy())
        
        # Convert to numpy arrays
        alzheimer_labels = np.array(all_alzheimer_labels).astype(int)
        parkinson_labels = np.array(all_parkinson_labels).astype(int)
        alzheimer_preds = np.array(all_alzheimer_preds).astype(int)
        parkinson_preds = np.array(all_parkinson_preds).astype(int)
        alzheimer_proba = np.array(all_alzheimer_proba).flatten()
        parkinson_proba = np.array(all_parkinson_proba).flatten()
        
        # Calculate metrics for both diseases
        alzheimer_metrics = self.calculate_clinical_metrics(
            alzheimer_labels, alzheimer_preds, alzheimer_proba, "Alzheimer's"
        )
        
        parkinson_metrics = self.calculate_clinical_metrics(
            parkinson_labels, parkinson_preds, parkinson_proba, "Parkinson's"
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

