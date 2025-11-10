"""
Model Trainer for Training Pipeline
Handles model training with early stopping and checkpointing
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Optional, Tuple
import logging
from pathlib import Path
import json
from datetime import datetime

from ..ai_model_service import MultiModalNeuralNetwork
from .evaluator import ModelEvaluator

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Trainer for multi-modal neural network"""
    
    def __init__(self, model: MultiModalNeuralNetwork, device: torch.device,
                 model_dir: Optional[Path] = None):
        """
        Initialize trainer
        
        Args:
            model: Model to train
            device: Device to train on (cuda or cpu)
            model_dir: Directory to save models
        """
        self.model = model
        self.device = device
        self.model_dir = model_dir or Path("models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.evaluator = ModelEvaluator()
        self.best_val_loss = float('inf')
        self.training_history = {
            'train_loss': [],
            'val_loss': [],
            'train_alzheimer_acc': [],
            'val_alzheimer_acc': [],
            'train_parkinson_acc': [],
            'val_parkinson_acc': []
        }
    
    def train_epoch(self, train_loader: DataLoader, optimizer: optim.Optimizer,
                   criterion: nn.Module) -> Dict[str, float]:
        """
        Train for one epoch
        
        Args:
            train_loader: Training data loader
            optimizer: Optimizer
            criterion: Loss function
        
        Returns:
            Dictionary with training metrics
        """
        self.model.train()
        total_loss = 0.0
        total_alzheimer_correct = 0
        total_parkinson_correct = 0
        total_samples = 0
        
        for batch in train_loader:
            features = batch['features'].to(self.device)
            alzheimer_labels = batch['alzheimer_label'].to(self.device)
            parkinson_labels = batch['parkinson_label'].to(self.device)
            
            # Forward pass
            optimizer.zero_grad()
            alzheimer_pred, parkinson_pred = self.model(features)
            
            # Calculate loss
            alzheimer_loss = criterion(alzheimer_pred.squeeze(), alzheimer_labels)
            parkinson_loss = criterion(parkinson_pred.squeeze(), parkinson_labels)
            loss = alzheimer_loss + parkinson_loss
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Calculate accuracy
            alzheimer_pred_binary = (alzheimer_pred.squeeze() > 0.5).float()
            parkinson_pred_binary = (parkinson_pred.squeeze() > 0.5).float()
            
            total_alzheimer_correct += (alzheimer_pred_binary == alzheimer_labels).sum().item()
            total_parkinson_correct += (parkinson_pred_binary == parkinson_labels).sum().item()
            total_samples += len(features)
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        alzheimer_acc = total_alzheimer_correct / total_samples
        parkinson_acc = total_parkinson_correct / total_samples
        
        return {
            'loss': avg_loss,
            'alzheimer_accuracy': alzheimer_acc,
            'parkinson_accuracy': parkinson_acc
        }
    
    def validate(self, val_loader: DataLoader, criterion: nn.Module) -> Dict[str, float]:
        """
        Validate model
        
        Args:
            val_loader: Validation data loader
            criterion: Loss function
        
        Returns:
            Dictionary with validation metrics
        """
        self.model.eval()
        total_loss = 0.0
        total_alzheimer_correct = 0
        total_parkinson_correct = 0
        total_samples = 0
        
        all_alzheimer_preds = []
        all_parkinson_preds = []
        all_alzheimer_labels = []
        all_parkinson_labels = []
        
        with torch.no_grad():
            for batch in val_loader:
                features = batch['features'].to(self.device)
                alzheimer_labels = batch['alzheimer_label'].to(self.device)
                parkinson_labels = batch['parkinson_label'].to(self.device)
                
                # Forward pass
                alzheimer_pred, parkinson_pred = self.model(features)
                
                # Calculate loss
                alzheimer_loss = criterion(alzheimer_pred.squeeze(), alzheimer_labels)
                parkinson_loss = criterion(parkinson_pred.squeeze(), parkinson_labels)
                loss = alzheimer_loss + parkinson_loss
                
                # Calculate accuracy
                alzheimer_pred_binary = (alzheimer_pred.squeeze() > 0.5).float()
                parkinson_pred_binary = (parkinson_pred.squeeze() > 0.5).float()
                
                total_alzheimer_correct += (alzheimer_pred_binary == alzheimer_labels).sum().item()
                total_parkinson_correct += (parkinson_pred_binary == parkinson_labels).sum().item()
                total_samples += len(features)
                total_loss += loss.item()
                
                # Store predictions for detailed evaluation
                all_alzheimer_preds.extend(alzheimer_pred.squeeze().cpu().numpy())
                all_parkinson_preds.extend(parkinson_pred.squeeze().cpu().numpy())
                all_alzheimer_labels.extend(alzheimer_labels.cpu().numpy())
                all_parkinson_labels.extend(parkinson_labels.cpu().numpy())
        
        avg_loss = total_loss / len(val_loader)
        alzheimer_acc = total_alzheimer_correct / total_samples
        parkinson_acc = total_parkinson_correct / total_samples
        
        # Calculate clinical metrics
        clinical_metrics = self.evaluator.calculate_clinical_metrics(
            all_alzheimer_preds, all_alzheimer_labels,
            all_parkinson_preds, all_parkinson_labels
        )
        
        metrics = {
            'loss': avg_loss,
            'alzheimer_accuracy': alzheimer_acc,
            'parkinson_accuracy': parkinson_acc,
            **clinical_metrics
        }
        
        return metrics
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader,
             epochs: int = 100, learning_rate: float = 0.001,
             weight_decay: float = 1e-5, patience: int = 10,
             min_delta: float = 0.001) -> Dict:
        """
        Train model with early stopping
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Maximum number of epochs
            learning_rate: Learning rate
            weight_decay: Weight decay for regularization
            patience: Early stopping patience
            min_delta: Minimum change to qualify as improvement
        
        Returns:
            Dictionary with training history and best model path
        """
        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5, verbose=True
        )
        
        best_model_path = None
        patience_counter = 0
        
        logger.info(f"Starting training for {epochs} epochs...")
        logger.info(f"Device: {self.device}")
        logger.info(f"Learning rate: {learning_rate}")
        logger.info(f"Early stopping patience: {patience}")
        
        for epoch in range(epochs):
            # Train
            train_metrics = self.train_epoch(train_loader, optimizer, criterion)
            
            # Validate
            val_metrics = self.validate(val_loader, criterion)
            
            # Update learning rate
            scheduler.step(val_metrics['loss'])
            
            # Store history
            self.training_history['train_loss'].append(train_metrics['loss'])
            self.training_history['val_loss'].append(val_metrics['loss'])
            self.training_history['train_alzheimer_acc'].append(train_metrics['alzheimer_accuracy'])
            self.training_history['val_alzheimer_acc'].append(val_metrics['alzheimer_accuracy'])
            self.training_history['train_parkinson_acc'].append(train_metrics['parkinson_accuracy'])
            self.training_history['val_parkinson_acc'].append(val_metrics['parkinson_accuracy'])
            
            # Log metrics
            logger.info(
                f"Epoch {epoch + 1}/{epochs} - "
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Val Loss: {val_metrics['loss']:.4f}, "
                f"Val Alz Acc: {val_metrics['alzheimer_accuracy']:.4f}, "
                f"Val Park Acc: {val_metrics['parkinson_accuracy']:.4f}"
            )
            
            # Early stopping and checkpointing
            if val_metrics['loss'] < self.best_val_loss - min_delta:
                self.best_val_loss = val_metrics['loss']
                patience_counter = 0
                
                # Save best model
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                best_model_path = self.model_dir / f"best_model_{timestamp}.pth"
                torch.save(self.model.state_dict(), best_model_path)
                logger.info(f"Saved best model to {best_model_path}")
                
                # Save training metrics
                metrics_path = self.model_dir / f"training_metrics_{timestamp}.json"
                with open(metrics_path, 'w') as f:
                    json.dump({
                        'epoch': epoch + 1,
                        'val_loss': val_metrics['loss'],
                        'val_metrics': val_metrics,
                        'training_history': self.training_history
                    }, f, indent=2)
            else:
                patience_counter += 1
            
            # Early stopping
            if patience_counter >= patience:
                logger.info(f"Early stopping at epoch {epoch + 1}")
                break
        
        return {
            'training_history': self.training_history,
            'best_model_path': best_model_path,
            'best_val_loss': self.best_val_loss
        }

