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
from sklearn.model_selection import StratifiedKFold, GroupShuffleSplit, StratifiedGroupKFold
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
        self.last_seed: Optional[int] = None
        self.split_method: Optional[str] = None
        # Raw (unscaled) attributes for the test split, keyed by name (e.g. 'gender',
        # 'age_band'), aligned index-for-index with the test set — used for subgroup
        # fairness analysis in ClinicalValidator. Populated by prepare_data().
        self.test_subgroups: Dict[str, np.ndarray] = {}
        # Class imbalance weights computed from the training split, keyed by
        # target name ('alzheimer', 'parkinson') — see _compute_pos_weight().
        self.pos_weights: Dict[str, float] = {}
        
        # Create models directory
        self.models_dir = Path(settings.MODELS_DIR if hasattr(settings, 'MODELS_DIR') else "models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ModelTrainer initialized on device: {self.device}")
    
    def _extract_features_labels(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Shared column-selection logic for prepare_data() and cross_validate(), so
        the two don't drift into extracting different feature sets from the same
        CSV. Returns raw (unscaled) X and the two binary label arrays.
        """
        feature_columns = [
            'age', 'gender_encoded', 'education_years',
            'mmse_score', 'moca_score', 'memory_score', 'attention_score', 'executive_function_score',
            'amyloid_beta', 'tau_protein', 'dopamine_level',
            'apoe_e4_status',
            'hippocampal_volume', 'cortical_thickness', 'ventricular_volume',
            'white_matter_hyperintensities', 'brain_volume_total'
        ]
        imaging_cols = [col for col in df.columns if col.startswith('imaging_feature_')]
        feature_columns.extend(sorted(imaging_cols))

        available_features = [col for col in feature_columns if col in df.columns]
        if len(available_features) < self.input_dim:
            missing = self.input_dim - len(available_features)
            for i in range(missing):
                df[f'padding_feature_{i}'] = 0.0
                available_features.append(f'padding_feature_{i}')

        X = df[available_features[:self.input_dim]].values.astype(np.float32)
        y_alzheimer = df['alzheimer_label'].values.astype(np.float32) if 'alzheimer_label' in df.columns else np.zeros(len(df), dtype=np.float32)
        y_parkinson = df['parkinson_label'].values.astype(np.float32) if 'parkinson_label' in df.columns else np.zeros(len(df), dtype=np.float32)
        X = np.nan_to_num(X, nan=0.0, posinf=1.0, neginf=0.0)
        return X, y_alzheimer, y_parkinson

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

        patient_ids = df['patient_id'].values if 'patient_id' in df.columns else None
        if patient_ids is None:
            logger.warning(
                "No 'patient_id' column found. Falling back to row-level splitting, "
                "which risks train/val/test leakage if any patient contributes more "
                "than one row (e.g. multiple visits)."
            )

        # Extract features and labels (shared with cross_validate())
        X, y_alzheimer, y_parkinson = self._extract_features_labels(df)

        # Normalize features
        self.scaler = RobustScaler()  # RobustScaler is better for outliers
        X = self.scaler.fit_transform(X)
        
        # Split data
        np.random.seed(random_seed)
        torch.manual_seed(random_seed)
        self.last_seed = random_seed

        n_total = len(X)

        if patient_ids is not None:
            n_unique_patients = len(np.unique(patient_ids))
            logger.info(f"Splitting by patient_id ({n_unique_patients} unique patients) to prevent leakage")

            gss_test = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_seed)
            temp_indices, test_indices = next(gss_test.split(X, y_alzheimer, groups=patient_ids))

            val_fraction_of_temp = val_size / (1.0 - test_size)
            gss_val = GroupShuffleSplit(n_splits=1, test_size=val_fraction_of_temp, random_state=random_seed)
            train_rel, val_rel = next(
                gss_val.split(X[temp_indices], y_alzheimer[temp_indices], groups=patient_ids[temp_indices])
            )
            train_indices = temp_indices[train_rel]
            val_indices = temp_indices[val_rel]

            assert set(np.unique(patient_ids[train_indices])).isdisjoint(patient_ids[val_indices]), \
                "Patient leakage between train and val"
            assert set(np.unique(patient_ids[train_indices])).isdisjoint(patient_ids[test_indices]), \
                "Patient leakage between train and test"
            assert set(np.unique(patient_ids[val_indices])).isdisjoint(patient_ids[test_indices]), \
                "Patient leakage between val and test"

            self.split_method = 'group_by_patient_id'
        else:
            n_test = int(n_total * test_size)
            n_val = int(n_total * val_size)
            n_train = n_total - n_test - n_val

            indices = np.random.permutation(n_total)
            train_indices = indices[:n_train]
            val_indices = indices[n_train:n_train + n_val]
            test_indices = indices[n_train + n_val:]

            self.split_method = 'row_level_fallback'

        # Capture raw (unscaled) subgroup attributes for the test split, used later
        # for fairness analysis (see ClinicalValidator.compute_subgroup_metrics).
        # Built here — before scaling — so bands reflect real ages, not z-scores.
        self.test_subgroups = {}
        if 'gender' in df.columns:
            self.test_subgroups['gender'] = df['gender'].values[test_indices]
        if 'age' in df.columns:
            self.test_subgroups['age_band'] = pd.cut(
                df['age'].values[test_indices], bins=[0, 65, 200], labels=['under_65', '65_plus']
            ).astype(str)

        # Class imbalance weights from the TRAIN split only (never test/val, to
        # avoid leaking label-distribution information into evaluation).
        self.pos_weights = {
            'alzheimer': self._compute_pos_weight(y_alzheimer[train_indices]),
            'parkinson': self._compute_pos_weight(y_parkinson[train_indices]),
        }
        logger.info(f"Class imbalance pos_weights (train split): {self.pos_weights}")

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
        
        logger.info(
            f"Data split ({self.split_method}, seed={random_seed}): "
            f"Train={len(train_indices)}, Val={len(val_indices)}, Test={len(test_indices)}"
        )
        
        return train_loader, val_loader, test_loader

    @staticmethod
    def _compute_pos_weight(labels: np.ndarray) -> float:
        """
        Ratio of negative to positive samples in a binary label array, for use as
        a per-sample loss weight. Both diseases are minority classes here (most
        patients are Normal), so without this the model can reach low loss by
        under-predicting the positive class entirely.

        Returns 1.0 (no reweighting) if a class is completely absent — a ratio
        against zero positives is undefined and would blow up the loss.
        """
        n_pos = float(np.sum(labels == 1))
        n_neg = float(np.sum(labels == 0))
        if n_pos == 0 or n_neg == 0:
            return 1.0
        return n_neg / n_pos

    def create_model(self) -> MultiModalNeuralNetwork:
        """Create model architecture"""
        self.model = MultiModalNeuralNetwork(
            input_dim=self.input_dim,
            hidden_dims=self.hidden_dims
        ).to(self.device)
        return self.model
    
    def _weighted_bce(self, pred: torch.Tensor, target: torch.Tensor, pos_weight: float) -> torch.Tensor:
        """
        Binary cross-entropy with a higher penalty for missing the minority
        (positive) class. Computed per-batch since torch.nn.BCELoss takes a
        fixed `weight` tensor shaped like the input rather than a scalar
        pos_weight (that convenience is BCEWithLogitsLoss-only, and the model
        already applies Sigmoid internally).
        """
        weights = torch.where(
            target == 1,
            torch.full_like(target, pos_weight),
            torch.ones_like(target),
        )
        return nn.functional.binary_cross_entropy(pred, target, weight=weights)

    def train_epoch(self, train_loader: DataLoader,
                   optimizer: optim.Optimizer) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        total_alzheimer_loss = 0.0
        total_parkinson_loss = 0.0
        n_batches = 0
        alz_pos_weight = self.pos_weights.get('alzheimer', 1.0)
        park_pos_weight = self.pos_weights.get('parkinson', 1.0)

        for batch in train_loader:
            features = batch['features'].to(self.device)
            alzheimer_labels = batch['alzheimer'].to(self.device).unsqueeze(1)
            parkinson_labels = batch['parkinson'].to(self.device).unsqueeze(1)

            optimizer.zero_grad()

            # Forward pass
            alzheimer_pred, parkinson_pred = self.model(features)

            # Calculate loss (class-weighted — see _weighted_bce)
            alzheimer_loss = self._weighted_bce(alzheimer_pred, alzheimer_labels, alz_pos_weight)
            parkinson_loss = self._weighted_bce(parkinson_pred, parkinson_labels, park_pos_weight)
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
    
    def validate(self, val_loader: DataLoader) -> Dict[str, float]:
        """Validate model"""
        self.model.eval()
        total_loss = 0.0
        total_alzheimer_loss = 0.0
        total_parkinson_loss = 0.0
        n_batches = 0
        alz_pos_weight = self.pos_weights.get('alzheimer', 1.0)
        park_pos_weight = self.pos_weights.get('parkinson', 1.0)

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

                alzheimer_loss = self._weighted_bce(alzheimer_pred, alzheimer_labels, alz_pos_weight)
                parkinson_loss = self._weighted_bce(parkinson_pred, parkinson_labels, park_pos_weight)
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
             save_best: bool = True,
             seed: Optional[int] = None) -> Dict:
        """
        Train the model

        Args:
            seed: Random seed for this training run. If omitted, falls back to
                the seed captured by prepare_data() (self.last_seed), so the run
                that produced this exact model is always reproducible from the
                returned/saved metadata.

        Returns:
            Dictionary with training history and best metrics
        """
        if self.model is None:
            self.create_model()

        seed = seed if seed is not None else self.last_seed
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)
        self.last_seed = seed

        # Setup optimizer (loss is class-weighted BCE — see _weighted_bce)
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)

        best_val_loss = float('inf')
        patience_counter = 0
        training_history = []

        logger.info(f"Starting training for {epochs} epochs (seed={seed})")

        for epoch in range(epochs):
            # Train
            train_metrics = self.train_epoch(train_loader, optimizer)

            # Validate
            val_metrics = self.validate(val_loader)
            
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
            'total_epochs': len(training_history),
            'seed': seed,
            'pos_weights': self.pos_weights,
            'split_method': self.split_method,
        }

    def cross_validate(self,
                       data_path: str,
                       n_splits: int = 5,
                       epochs: int = 30,
                       learning_rate: float = 0.001,
                       random_seed: int = 42) -> Dict:
        """
        K-fold cross-validation, grouped by patient_id and stratified by the
        Alzheimer's label, so no single train/val/test split can make the
        reported metrics look better (or worse) than the model actually is.

        A single split is cheap to get lucky (or unlucky) on with a dataset this
        small; folding over the whole dataset and reporting mean +/- std is what
        makes the eventual go/no-go registry decision (see ModelRegistry.
        passes_quality_gate) trustworthy.

        Falls back to plain StratifiedKFold (no grouping) if patient_id is
        missing — with the same leakage caveat as prepare_data().

        Returns:
            Dict with per-fold metrics, per-metric mean/std, and the seed used
            for the fold assignment (for reproducibility).
        """
        logger.info(f"Loading data from {data_path} for {n_splits}-fold cross-validation")
        df = pd.read_csv(data_path)
        X, y_alzheimer, y_parkinson = self._extract_features_labels(df)
        patient_ids = df['patient_id'].values if 'patient_id' in df.columns else None

        if patient_ids is not None:
            splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=random_seed)
            split_iter = splitter.split(X, y_alzheimer, groups=patient_ids)
            split_method = 'stratified_group_k_fold'
        else:
            logger.warning(
                "No 'patient_id' column found. Cross-validating with plain "
                "StratifiedKFold, which risks train/val leakage if any patient "
                "contributes more than one row."
            )
            splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_seed)
            split_iter = splitter.split(X, y_alzheimer)
            split_method = 'stratified_k_fold_row_level'

        fold_metrics: List[Dict] = []
        for fold_idx, (train_idx, val_idx) in enumerate(split_iter, start=1):
            logger.info(f"--- Fold {fold_idx}/{n_splits} ---")

            fold_scaler = RobustScaler()
            X_train = fold_scaler.fit_transform(X[train_idx])
            X_val = fold_scaler.transform(X[val_idx])

            self.pos_weights = {
                'alzheimer': self._compute_pos_weight(y_alzheimer[train_idx]),
                'parkinson': self._compute_pos_weight(y_parkinson[train_idx]),
            }

            train_loader = DataLoader(
                NeuroDataset(X_train, y_alzheimer[train_idx], y_parkinson[train_idx]),
                batch_size=32, shuffle=True
            )
            val_loader = DataLoader(
                NeuroDataset(X_val, y_alzheimer[val_idx], y_parkinson[val_idx]),
                batch_size=32, shuffle=False
            )

            # Fresh model per fold — folds must not share learned weights.
            self.create_model()
            result = self.train(
                train_loader, val_loader,
                epochs=epochs, learning_rate=learning_rate,
                early_stopping_patience=max(5, epochs // 4),
                save_best=False, seed=random_seed + fold_idx,
            )
            fold_metrics.append({'fold': fold_idx, **result['best_metrics']})

        metric_keys = [k for k in fold_metrics[0].keys() if k != 'fold']
        summary = {
            key: {
                'mean': float(np.mean([f[key] for f in fold_metrics])),
                'std': float(np.std([f[key] for f in fold_metrics])),
            }
            for key in metric_keys
        }

        logger.info(f"Cross-validation ({split_method}, seed={random_seed}) summary:")
        for key, stats in summary.items():
            logger.info(f"  {key}: {stats['mean']:.4f} +/- {stats['std']:.4f}")

        return {
            'n_splits': n_splits,
            'split_method': split_method,
            'seed': random_seed,
            'folds': fold_metrics,
            'summary': summary,
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

        # Reproducibility fields are always recorded, even for intermediate
        # per-epoch checkpoints, so any saved .pth can be traced back to the
        # exact seed and split that produced it.
        full_metadata = {
            'seed': self.last_seed,
            'split_method': self.split_method,
            'pos_weights': self.pos_weights,
            **(metadata or {}),
        }
        metadata_path = self.models_dir / filename.replace('.pth', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(full_metadata, f, indent=2)
    
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

