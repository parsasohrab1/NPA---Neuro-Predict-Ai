"""
Model Evaluator for Clinical Validation
Calculates clinical metrics including sensitivity, specificity, AUC, etc.
"""
import numpy as np
from typing import Dict, Tuple, List
import logging
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    precision_recall_curve, roc_curve
)

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluator for clinical validation metrics"""
    
    def calculate_clinical_metrics(self, alzheimer_preds: List[float],
                                   alzheimer_labels: List[float],
                                   parkinson_preds: List[float],
                                   parkinson_labels: List[float],
                                   threshold: float = 0.5) -> Dict:
        """
        Calculate comprehensive clinical validation metrics
        
        Args:
            alzheimer_preds: Alzheimer's predictions (probabilities)
            alzheimer_labels: Alzheimer's true labels
            parkinson_preds: Parkinson's predictions (probabilities)
            parkinson_labels: Parkinson's true labels
            threshold: Classification threshold
        
        Returns:
            Dictionary with clinical metrics
        """
        alzheimer_preds = np.array(alzheimer_preds)
        alzheimer_labels = np.array(alzheimer_labels)
        parkinson_preds = np.array(parkinson_preds)
        parkinson_labels = np.array(parkinson_labels)
        
        metrics = {}
        
        # Alzheimer's metrics
        alzheimer_binary_preds = (alzheimer_preds >= threshold).astype(int)
        metrics['alzheimer'] = self._calculate_disease_metrics(
            alzheimer_preds, alzheimer_binary_preds, alzheimer_labels, 'Alzheimer'
        )
        
        # Parkinson's metrics
        parkinson_binary_preds = (parkinson_preds >= threshold).astype(int)
        metrics['parkinson'] = self._calculate_disease_metrics(
            parkinson_preds, parkinson_binary_preds, parkinson_labels, 'Parkinson'
        )
        
        return metrics
    
    def _calculate_disease_metrics(self, pred_probs: np.ndarray,
                                   pred_binary: np.ndarray,
                                   true_labels: np.ndarray,
                                   disease_name: str) -> Dict:
        """
        Calculate metrics for a single disease
        
        Args:
            pred_probs: Prediction probabilities
            pred_binary: Binary predictions
            true_labels: True labels
            disease_name: Name of the disease
        
        Returns:
            Dictionary with metrics
        """
        # Basic metrics
        accuracy = accuracy_score(true_labels, pred_binary)
        precision = precision_score(true_labels, pred_binary, zero_division=0)
        recall = recall_score(true_labels, pred_binary, zero_division=0)
        f1 = f1_score(true_labels, pred_binary, zero_division=0)
        
        # Clinical metrics (Sensitivity = Recall, Specificity = TN / (TN + FP))
        tn, fp, fn, tp = confusion_matrix(true_labels, pred_binary).ravel()
        sensitivity = recall  # True Positive Rate
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0  # True Negative Rate
        ppv = precision  # Positive Predictive Value
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0  # Negative Predictive Value
        
        # AUC-ROC
        try:
            auc_roc = roc_auc_score(true_labels, pred_probs)
        except ValueError:
            auc_roc = 0.0
            logger.warning(f"Could not calculate AUC-ROC for {disease_name} (possibly only one class present)")
        
        # Calculate optimal threshold (Youden's J statistic)
        try:
            fpr, tpr, thresholds = roc_curve(true_labels, pred_probs)
            youden_j = tpr - fpr
            optimal_idx = np.argmax(youden_j)
            optimal_threshold = thresholds[optimal_idx]
        except ValueError:
            optimal_threshold = 0.5
            logger.warning(f"Could not calculate optimal threshold for {disease_name}")
        
        metrics = {
            'accuracy': float(accuracy),
            'sensitivity': float(sensitivity),  # Recall / True Positive Rate
            'specificity': float(specificity),  # True Negative Rate
            'precision': float(precision),  # Positive Predictive Value
            'negative_predictive_value': float(npv),
            'f1_score': float(f1),
            'auc_roc': float(auc_roc),
            'optimal_threshold': float(optimal_threshold),
            'confusion_matrix': {
                'true_negatives': int(tn),
                'false_positives': int(fp),
                'false_negatives': int(fn),
                'true_positives': int(tp)
            },
            'prevalence': float(true_labels.mean()),
            'positive_rate': float(pred_binary.mean())
        }
        
        logger.info(f"{disease_name} Metrics:")
        logger.info(f"  Accuracy: {accuracy:.4f}")
        logger.info(f"  Sensitivity: {sensitivity:.4f}")
        logger.info(f"  Specificity: {specificity:.4f}")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  F1-Score: {f1:.4f}")
        logger.info(f"  AUC-ROC: {auc_roc:.4f}")
        
        return metrics
    
    def evaluate_model(self, model, test_loader, device, threshold: float = 0.5) -> Dict:
        """
        Evaluate model on test set
        
        Args:
            model: Trained model
            test_loader: Test data loader
            device: Device to run on
            threshold: Classification threshold
        
        Returns:
            Dictionary with evaluation metrics
        """
        model.eval()
        all_alzheimer_preds = []
        all_parkinson_preds = []
        all_alzheimer_labels = []
        all_parkinson_labels = []
        
        import torch
        
        with torch.no_grad():
            for batch in test_loader:
                features = batch['features'].to(device)
                alzheimer_labels = batch['alzheimer_label'].to(device)
                parkinson_labels = batch['parkinson_label'].to(device)
                
                alzheimer_pred, parkinson_pred = model(features)
                
                all_alzheimer_preds.extend(alzheimer_pred.squeeze().cpu().numpy())
                all_parkinson_preds.extend(parkinson_pred.squeeze().cpu().numpy())
                all_alzheimer_labels.extend(alzheimer_labels.cpu().numpy())
                all_parkinson_labels.extend(parkinson_labels.cpu().numpy())
        
        # Calculate metrics
        metrics = self.calculate_clinical_metrics(
            all_alzheimer_preds, all_alzheimer_labels,
            all_parkinson_preds, all_parkinson_labels,
            threshold=threshold
        )
        
        return metrics
    
    def generate_clinical_report(self, metrics: Dict) -> str:
        """
        Generate a clinical validation report
        
        Args:
            metrics: Dictionary with evaluation metrics
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("CLINICAL VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        for disease_name in ['alzheimer', 'parkinson']:
            if disease_name in metrics:
                disease_metrics = metrics[disease_name]
                report.append(f"{disease_name.upper()} DISEASE PREDICTION")
                report.append("-" * 80)
                report.append(f"Accuracy:              {disease_metrics['accuracy']:.4f}")
                report.append(f"Sensitivity (Recall):  {disease_metrics['sensitivity']:.4f}")
                report.append(f"Specificity:           {disease_metrics['specificity']:.4f}")
                report.append(f"Precision (PPV):       {disease_metrics['precision']:.4f}")
                report.append(f"Negative Predictive Value: {disease_metrics['negative_predictive_value']:.4f}")
                report.append(f"F1-Score:              {disease_metrics['f1_score']:.4f}")
                report.append(f"AUC-ROC:               {disease_metrics['auc_roc']:.4f}")
                report.append(f"Optimal Threshold:     {disease_metrics['optimal_threshold']:.4f}")
                report.append("")
                report.append("Confusion Matrix:")
                cm = disease_metrics['confusion_matrix']
                report.append(f"  True Negatives:  {cm['true_negatives']}")
                report.append(f"  False Positives: {cm['false_positives']}")
                report.append(f"  False Negatives: {cm['false_negatives']}")
                report.append(f"  True Positives:  {cm['true_positives']}")
                report.append("")
                report.append(f"Prevalence:        {disease_metrics['prevalence']:.4f}")
                report.append(f"Positive Rate:     {disease_metrics['positive_rate']:.4f}")
                report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)

