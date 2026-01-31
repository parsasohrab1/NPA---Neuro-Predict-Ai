"""
Model Training Service
پیاده‌سازی کامل Training Pipeline برای آموزش مدل
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import json
from datetime import datetime
import pickle
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import StratifiedKFold
import matplotlib.pyplot as plt
import seaborn as sns

from ...core.config import settings
from ..ai_model_service import MultiModalNeuralNetwork

logger = logging.getLogger(__name__)


class NeuroDataset(Dataset):
    """Dataset class for NeuroPredict training data"""
    
    def __init__(self, features: np.ndarray, labels_alzheimer: np.ndarray, 
                 labels_parkinson: np.ndarray):
        self.features = torch.FloatTensor(features)
        self.labels_alzheimer = torch.FloatTensor(labels_alzheimer)
        self.labels_parkinson = torch.FloatTensor(labels_parkinson)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return {
            'features': self.features[idx],
            'alzheimer': self.labels_alzheimer[idx],
            'parkinson': self.labels_parkinson[idx]
        }


class ModelTrainer:
    """Training service for NeuroPredict-AI models"""
    
    def __init__(self, 
                 input_dim: int = 50,
                 hidden_dims: List[int] = [256, 128, 64],
                 device: Optional[torch.device] = None):
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.scaler = None
        self.training_history = []
        self.best_model_state = None
        self.best_metrics = {}
        
        # Create models directory
        self.models_dir = Path(settings.MODELS_DIR if hasattr(settings, 'MODELS_DIR') else "models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ModelTrainer initialized on device: {self.device}")
    
    def prepare_data(self, 
                    data_path: str,
                    test_size: float = 0.2,
                    val_size: float = 0.1,
                    random_seed: int = 42) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Load and prepare training data
        
        Args:
            data_path: Path to CSV file with training data
            test_size: Fraction of data for testing
            val_size: Fraction of data for validation
            random_seed: Random seed for reproducibility
        
        Returns:
            Tuple of (train_loader, val_loader, test_loader)
        """
        logger.info(f"Loading data from {data_path}")
        
        # Load data
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} samples")
        
        # Extract features and labels
        feature_columns = [
            'age', 'gender_encoded', 'education_years',
            'mmse_score', 'moca_score', 'memory_score', 'attention_score', 'executive_function_score',
            'amyloid_beta', 'tau_protein', 'dopamine_level',
            'apoe_e4_status',
            'hippocampal_volume', 'cortical_thickness', 'ventricular_volume',
            'white_matter_hyperintensities', 'brain_volume_total'
        ]
        
        # Add imaging features if available
        imaging_cols = [col for col in df.columns if col.startswith('imaging_feature_')]
        feature_columns.extend(sorted(imaging_cols))
        
        # Ensure we have exactly input_dim features
        available_features = [col for col in feature_columns if col in df.columns]
        if len(available_features) < self.input_dim:
            # Pad with zeros
            missing = self.input_dim - len(available_features)
            for i in range(missing):
                df[f'padding_feature_{i}'] = 0.0
                available_features.append(f'padding_feature_{i}')
        
        X = df[available_features[:self.input_dim]].values.astype(np.float32)
        
        # Extract labels
        y_alzheimer = df['alzheimer_label'].values.astype(np.float32) if 'alzheimer_label' in df.columns else np.zeros(len(df))
        y_parkinson = df['parkinson_label'].values.astype(np.float32) if 'parkinson_label' in df.columns else np.zeros(len(df))
        
        # Handle missing values
        X = np.nan_to_num(X, nan=0.0, posinf=1.0, neginf=0.0)
        
        # Normalize features
        self.scaler = RobustScaler()  # RobustScaler is better for outliers
        X = self.scaler.fit_transform(X)
        
        # Split data
        np.random.seed(random_seed)
        torch.manual_seed(random_seed)
        
        n_total = len(X)
        n_test = int(n_total * test_size)
        n_val = int(n_total * val_size)
        n_train = n_total - n_test - n_val
        
        indices = np.random.permutation(n_total)
        train_indices = indices[:n_train]
        val_indices = indices[n_train:n_train + n_val]
        test_indices = indices[n_train + n_val:]
        
        # Create datasets
        train_dataset = NeuroDataset(
            X[train_indices], 
            y_alzheimer[train_indices], 
            y_parkinson[train_indices]
        )
        val_dataset = NeuroDataset(
            X[val_indices], 
            y_alzheimer[val_indices], 
            y_parkinson[val_indices]
        )
        test_dataset = NeuroDataset(
            X[test_indices], 
            y_alzheimer[test_indices], 
            y_parkinson[test_indices]
        )
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=2)
        val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=2)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=2)
        
        logger.info(f"Data split: Train={n_train}, Val={n_val}, Test={n_test}")
        
        return train_loader, val_loader, test_loader
    
    def create_model(self) -> MultiModalNeuralNetwork:
        """Create model architecture"""
        self.model = MultiModalNeuralNetwork(
            input_dim=self.input_dim,
            hidden_dims=self.hidden_dims
        ).to(self.device)
        return self.model
    
    def train_epoch(self, train_loader: DataLoader, 
                   optimizer: optim.Optimizer,
                   criterion: nn.Module) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        total_alzheimer_loss = 0.0
        total_parkinson_loss = 0.0
        n_batches = 0
        
        for batch in train_loader:
            features = batch['features'].to(self.device)
            alzheimer_labels = batch['alzheimer'].to(self.device).unsqueeze(1)
            parkinson_labels = batch['parkinson'].to(self.device).unsqueeze(1)
            
            optimizer.zero_grad()
            
            # Forward pass
            alzheimer_pred, parkinson_pred = self.model(features)
            
            # Calculate loss
            alzheimer_loss = criterion(alzheimer_pred, alzheimer_labels)
            parkinson_loss = criterion(parkinson_pred, parkinson_labels)
            loss = alzheimer_loss + parkinson_loss
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            total_alzheimer_loss += alzheimer_loss.item()
            total_parkinson_loss += parkinson_loss.item()
            n_batches += 1
        
        return {
            'loss': total_loss / n_batches,
            'alzheimer_loss': total_alzheimer_loss / n_batches,
            'parkinson_loss': total_parkinson_loss / n_batches
        }
    
    def validate(self, val_loader: DataLoader, 
                criterion: nn.Module) -> Dict[str, float]:
        """Validate model"""
        self.model.eval()
        total_loss = 0.0
        total_alzheimer_loss = 0.0
        total_parkinson_loss = 0.0
        n_batches = 0
        
        all_alzheimer_preds = []
        all_parkinson_preds = []
        all_alzheimer_labels = []
        all_parkinson_labels = []
        
        with torch.no_grad():
            for batch in val_loader:
                features = batch['features'].to(self.device)
                alzheimer_labels = batch['alzheimer'].to(self.device).unsqueeze(1)
                parkinson_labels = batch['parkinson'].to(self.device).unsqueeze(1)
                
                alzheimer_pred, parkinson_pred = self.model(features)
                
                alzheimer_loss = criterion(alzheimer_pred, alzheimer_labels)
                parkinson_loss = criterion(parkinson_pred, parkinson_labels)
                loss = alzheimer_loss + parkinson_loss
                
                total_loss += loss.item()
                total_alzheimer_loss += alzheimer_loss.item()
                total_parkinson_loss += parkinson_loss.item()
                n_batches += 1
                
                all_alzheimer_preds.extend(alzheimer_pred.cpu().numpy())
                all_parkinson_preds.extend(parkinson_pred.cpu().numpy())
                all_alzheimer_labels.extend(alzheimer_labels.cpu().numpy())
                all_parkinson_labels.extend(parkinson_labels.cpu().numpy())
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        alzheimer_preds_binary = (np.array(all_alzheimer_preds) > 0.5).astype(int)
        parkinson_preds_binary = (np.array(all_parkinson_preds) > 0.5).astype(int)
        
        alzheimer_labels = np.array(all_alzheimer_labels).astype(int)
        parkinson_labels = np.array(all_parkinson_labels).astype(int)
        
        metrics = {
            'loss': total_loss / n_batches,
            'alzheimer_loss': total_alzheimer_loss / n_batches,
            'parkinson_loss': total_parkinson_loss / n_batches,
            'alzheimer_accuracy': accuracy_score(alzheimer_labels, alzheimer_preds_binary),
            'alzheimer_precision': precision_score(alzheimer_labels, alzheimer_preds_binary, zero_division=0),
            'alzheimer_recall': recall_score(alzheimer_labels, alzheimer_preds_binary, zero_division=0),
            'alzheimer_f1': f1_score(alzheimer_labels, alzheimer_preds_binary, zero_division=0),
            'alzheimer_auc': roc_auc_score(alzheimer_labels, all_alzheimer_preds) if len(np.unique(alzheimer_labels)) > 1 else 0.0,
            'parkinson_accuracy': accuracy_score(parkinson_labels, parkinson_preds_binary),
            'parkinson_precision': precision_score(parkinson_labels, parkinson_preds_binary, zero_division=0),
            'parkinson_recall': recall_score(parkinson_labels, parkinson_preds_binary, zero_division=0),
            'parkinson_f1': f1_score(parkinson_labels, parkinson_preds_binary, zero_division=0),
            'parkinson_auc': roc_auc_score(parkinson_labels, all_parkinson_preds) if len(np.unique(parkinson_labels)) > 1 else 0.0,
        }
        
        return metrics
    
    def train(self,
             train_loader: DataLoader,
             val_loader: DataLoader,
             epochs: int = 100,
             learning_rate: float = 0.001,
             weight_decay: float = 1e-5,
             early_stopping_patience: int = 10,
             save_best: bool = True) -> Dict:
        """
        Train the model
        
        Returns:
            Dictionary with training history and best metrics
        """
        if self.model is None:
            self.create_model()
        
        # Setup optimizer and loss
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        criterion = nn.BCELoss()
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
        
        best_val_loss = float('inf')
        patience_counter = 0
        training_history = []
        
        logger.info(f"Starting training for {epochs} epochs")
        
        for epoch in range(epochs):
            # Train
            train_metrics = self.train_epoch(train_loader, optimizer, criterion)
            
            # Validate
            val_metrics = self.validate(val_loader, criterion)
            
            # Learning rate scheduling
            scheduler.step(val_metrics['loss'])
            
            # Log progress
            logger.info(
                f"Epoch {epoch+1}/{epochs} - "
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Val Loss: {val_metrics['loss']:.4f}, "
                f"Alzheimer F1: {val_metrics['alzheimer_f1']:.4f}, "
                f"Parkinson F1: {val_metrics['parkinson_f1']:.4f}"
            )
            
            # Save best model
            if val_metrics['loss'] < best_val_loss:
                best_val_loss = val_metrics['loss']
                self.best_model_state = self.model.state_dict().copy()
                self.best_metrics = val_metrics.copy()
                patience_counter = 0
                
                if save_best:
                    self.save_model(f"best_model_epoch_{epoch+1}.pth")
            else:
                patience_counter += 1
            
            # Early stopping
            if patience_counter >= early_stopping_patience:
                logger.info(f"Early stopping at epoch {epoch+1}")
                break
            
            training_history.append({
                'epoch': epoch + 1,
                'train': train_metrics,
                'val': val_metrics
            })
        
        # Load best model
        if self.best_model_state:
            self.model.load_state_dict(self.best_model_state)
        
        self.training_history = training_history
        
        return {
            'history': training_history,
            'best_metrics': self.best_metrics,
            'total_epochs': len(training_history)
        }
    
    def save_model(self, filename: str, metadata: Optional[Dict] = None):
        """Save model and metadata"""
        model_path = self.models_dir / filename
        torch.save(self.model.state_dict(), model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Save scaler
        scaler_path = self.models_dir / filename.replace('.pth', '_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save metadata
        if metadata:
            metadata_path = self.models_dir / filename.replace('.pth', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
    
    def load_model(self, model_path: str):
        """Load trained model"""
        if self.model is None:
            self.create_model()
        
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        logger.info(f"Model loaded from {model_path}")
    
    def plot_training_history(self, save_path: Optional[str] = None):
        """Plot training history"""
        if not self.training_history:
            logger.warning("No training history to plot")
            return
        
        epochs = [h['epoch'] for h in self.training_history]
        train_loss = [h['train']['loss'] for h in self.training_history]
        val_loss = [h['val']['loss'] for h in self.training_history]
        
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(epochs, train_loss, label='Train Loss')
        plt.plot(epochs, val_loss, label='Val Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training and Validation Loss')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        alzheimer_f1 = [h['val']['alzheimer_f1'] for h in self.training_history]
        parkinson_f1 = [h['val']['parkinson_f1'] for h in self.training_history]
        plt.plot(epochs, alzheimer_f1, label='Alzheimer F1')
        plt.plot(epochs, parkinson_f1, label='Parkinson F1')
        plt.xlabel('Epoch')
        plt.ylabel('F1 Score')
        plt.title('Validation F1 Scores')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Training plot saved to {save_path}")
        else:
            plt.show()

