"""
Data Loader for Training Pipeline
Loads and preprocesses data from CSV files and database
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Optional
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import torch
from torch.utils.data import Dataset, DataLoader as TorchDataLoader

logger = logging.getLogger(__name__)


class MedicalDataset(Dataset):
    """PyTorch Dataset for medical data"""
    
    def __init__(self, features: np.ndarray, alzheimer_labels: np.ndarray, 
                 parkinson_labels: np.ndarray):
        self.features = torch.FloatTensor(features)
        self.alzheimer_labels = torch.FloatTensor(alzheimer_labels)
        self.parkinson_labels = torch.FloatTensor(parkinson_labels)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return {
            'features': self.features[idx],
            'alzheimer_label': self.alzheimer_labels[idx],
            'parkinson_label': self.parkinson_labels[idx]
        }


class DataLoader:
    """Data loader for training pipeline"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize data loader
        
        Args:
            data_dir: Directory containing CSV files. If None, uses default data directory
        """
        if data_dir is None:
            # Default to data directory in project root
            # Try multiple possible paths
            current_file = Path(__file__)
            # backend/app/services/training/data_loader.py -> project root
            project_root = current_file.parent.parent.parent.parent.parent
            data_dir = project_root / "data" / "data" / "csv"
            
            # If that doesn't exist, try alternative path
            if not data_dir.exists():
                # Try data/data/csv from backend directory
                backend_dir = current_file.parent.parent.parent.parent
                data_dir = backend_dir.parent / "data" / "data" / "csv"
        
        self.data_dir = Path(data_dir)
        self.scaler = StandardScaler()
        self.feature_names = []

    @staticmethod
    def _derive_imaging_proxy_features(df: pd.DataFrame, n: int = 32) -> np.ndarray:
        """
        Derive deterministic 32-d proxy imaging features from available MRI numeric fields
        when dedicated imaging_feature_* columns are missing or all zeros.
        """
        n_samples = len(df)
        # Prefer explicit imaging_feature columns when present and non-zero
        has_explicit = all(f"imaging_feature_{i}" in df.columns for i in range(n))
        if has_explicit:
            mat = np.column_stack([df[f"imaging_feature_{i}"].astype(float).values for i in range(n)])
            if not np.allclose(mat, 0.0):
                return mat.astype(np.float64)

        hipp = df["hippocampal_volume"].astype(float).fillna(3500).values / 5000.0 if "hippocampal_volume" in df.columns else np.full(n_samples, 0.7)
        cort = df["cortical_thickness"].astype(float).fillna(2.3).values / 3.0 if "cortical_thickness" in df.columns else np.full(n_samples, 0.77)
        vent = df["ventricular_volume"].astype(float).fillna(30000).values / 70000.0 if "ventricular_volume" in df.columns else np.full(n_samples, 0.43)
        wmh = (
            df["white_matter_hyperintensities"].astype(float).fillna(2).values / 10.0
            if "white_matter_hyperintensities" in df.columns
            else np.full(n_samples, 0.2)
        )
        brain = (
            df["brain_volume_total"].astype(float).fillna(1100000).values / 1500000.0
            if "brain_volume_total" in df.columns
            else np.full(n_samples, 0.73)
        )
        # Expand deterministically to n dims via products / ratios / polynomials
        cols = [
            hipp, cort, vent, wmh, brain,
            hipp * cort, hipp * vent, cort * brain, vent * wmh, brain * hipp,
            hipp ** 2, cort ** 2, vent ** 2, wmh ** 2, brain ** 2,
            np.abs(hipp - vent), np.abs(cort - wmh), np.abs(brain - hipp),
            hipp / (cort + 1e-6), vent / (brain + 1e-6), wmh / (hipp + 1e-6),
            (hipp + cort + brain) / 3.0, (vent + wmh) / 2.0,
            np.sqrt(np.clip(hipp, 0, None)), np.sqrt(np.clip(brain, 0, None)),
            np.clip(hipp - 0.5, -1, 1), np.clip(vent - 0.5, -1, 1),
            np.sin(hipp * np.pi), np.cos(vent * np.pi),
            hipp * cort * brain, vent * wmh * hipp, (hipp + brain) - (vent + wmh),
        ]
        mat = np.column_stack(cols)
        if mat.shape[1] < n:
            pad = np.zeros((n_samples, n - mat.shape[1]))
            mat = np.column_stack([mat, pad])
        return mat[:, :n].astype(np.float64)
        
    def load_from_csv(self, csv_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load data from CSV file
        
        Args:
            csv_path: Path to CSV file. If None, uses sample_dataset_complete.csv
        
        Returns:
            DataFrame with loaded data
        """
        if csv_path is None:
            csv_path = self.data_dir / "sample_dataset_complete.csv"
        else:
            csv_path = Path(csv_path)
        
        if not csv_path.exists():
            raise FileNotFoundError(f"Data file not found: {csv_path}")
        
        logger.info(f"Loading data from {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} samples")
        
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Preprocess data and extract features and labels
        
        Args:
            df: DataFrame with raw data
        
        Returns:
            Tuple of (features, alzheimer_labels, parkinson_labels)
        """
        logger.info("Preprocessing data...")
        
        # Extract features (same as in ai_model_service.py)
        features_list = []
        
        # Demographics
        features_list.append((df['age'] / 100.0).values)
        # Gender encoding: handle multiple formats
        gender_map = {
            'Male': 1.0, 'male': 1.0, 'M': 1.0, 'm': 1.0,
            'Female': 0.0, 'female': 0.0, 'F': 0.0, 'f': 0.0
        }
        gender_encoded = df['gender'].map(gender_map).fillna(0.0)
        features_list.append(gender_encoded.values)
        features_list.append((df['education_years'] / 25.0).values)
        
        # Cognitive Scores
        features_list.append((df['mmse_score'] / 30.0).values)
        features_list.append((df['moca_score'] / 30.0).values)
        features_list.append((df.get('memory_score', pd.Series([50] * len(df))) / 100.0).values)
        features_list.append((df.get('attention_score', pd.Series([50] * len(df))) / 100.0).values)
        features_list.append((df.get('executive_function_score', pd.Series([50] * len(df))) / 100.0).values)
        
        # Biomarkers
        features_list.append((df['amyloid_beta'] / 1000.0).values)
        features_list.append((df['tau_protein'] / 800.0).values)
        features_list.append((df['dopamine_level'] / 150.0).values)
        
        # Genetic
        features_list.append((df['apoe_e4_status'].astype(float)).values)
        
        # MRI Features
        hipp = (df['hippocampal_volume'] / 5000.0).values
        cort = (df['cortical_thickness'] / 3.0).values
        vent = (df['ventricular_volume'] / 70000.0).values
        wmh = (df.get('white_matter_hyperintensities', pd.Series([2] * len(df))) / 10.0).values
        brain = (df.get('brain_volume_total', pd.Series([1100000] * len(df))) / 1500000.0).values
        features_list.append(hipp)
        features_list.append(cort)
        features_list.append(vent)
        features_list.append(wmh)
        features_list.append(brain)
        
        # Imaging features: use real columns if present, else deterministic MRI proxies
        # (never leave as silent all-zeros when MRI numerics are available)
        imaging_proxy = self._derive_imaging_proxy_features(df, n=32)
        for i in range(32):
            features_list.append(imaging_proxy[:, i])
        
        # Stack all features
        features = np.column_stack(features_list)
        
        # Store feature names
        self.feature_names = [
            'age', 'gender_encoded', 'education_years',
            'mmse_score', 'moca_score', 'memory_score', 'attention_score', 'executive_function_score',
            'amyloid_beta', 'tau_protein', 'dopamine_level',
            'apoe_e4_status',
            'hippocampal_volume', 'cortical_thickness', 'ventricular_volume',
            'white_matter_hyperintensities', 'brain_volume_total',
            *[f'imaging_feature_{i}' for i in range(32)]
        ]
        
        # Extract labels from diagnosis column
        # Label encoding: Normal=0, Alzheimer=1, Parkinson=2
        diagnosis_map = {
            'Normal': 0,
            'Alzheimer': 1,
            'Parkinson': 2,
            'normal': 0,
            'alzheimer': 1,
            'parkinson': 2
        }
        
        # Create binary labels for Alzheimer's (1 if Alzheimer, 0 otherwise)
        alzheimer_labels = df['diagnosis'].map(diagnosis_map).fillna(0)
        alzheimer_labels = (alzheimer_labels == 1).astype(float).values
        
        # Create binary labels for Parkinson's (1 if Parkinson, 0 otherwise)
        parkinson_labels = df['diagnosis'].map(diagnosis_map).fillna(0)
        parkinson_labels = (parkinson_labels == 2).astype(float).values
        
        logger.info(f"Features shape: {features.shape}")
        logger.info(f"Alzheimer labels - Positive: {alzheimer_labels.sum()}, Negative: {len(alzheimer_labels) - alzheimer_labels.sum()}")
        logger.info(f"Parkinson labels - Positive: {parkinson_labels.sum()}, Negative: {len(parkinson_labels) - parkinson_labels.sum()}")
        
        return features, alzheimer_labels, parkinson_labels
    
    def split_data(self, features: np.ndarray, alzheimer_labels: np.ndarray,
                   parkinson_labels: np.ndarray, 
                   train_ratio: float = 0.7, val_ratio: float = 0.15,
                   test_ratio: float = 0.15, random_state: int = 42) -> Dict:
        """
        Split data into train, validation, and test sets
        
        Args:
            features: Feature matrix
            alzheimer_labels: Alzheimer's labels
            parkinson_labels: Parkinson's labels
            train_ratio: Ratio for training set
            val_ratio: Ratio for validation set
            test_ratio: Ratio for test set
            random_state: Random seed
        
        Returns:
            Dictionary with train, val, test splits
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"
        
        logger.info(f"Splitting data: Train={train_ratio}, Val={val_ratio}, Test={test_ratio}")
        
        # First split: train + val vs test
        test_size = test_ratio
        X_temp, X_test, y_alz_temp, y_alz_test, y_park_temp, y_park_test = train_test_split(
            features, alzheimer_labels, parkinson_labels,
            test_size=test_size, random_state=random_state, stratify=alzheimer_labels
        )
        
        # Second split: train vs val
        val_size = val_ratio / (train_ratio + val_ratio)
        X_train, X_val, y_alz_train, y_alz_val, y_park_train, y_park_val = train_test_split(
            X_temp, y_alz_temp, y_park_temp,
            test_size=val_size, random_state=random_state, stratify=y_alz_temp
        )
        
        # Normalize features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        logger.info(f"Train set: {len(X_train)} samples")
        logger.info(f"Validation set: {len(X_val)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        return {
            'train': {
                'features': X_train_scaled,
                'alzheimer_labels': y_alz_train,
                'parkinson_labels': y_park_train
            },
            'val': {
                'features': X_val_scaled,
                'alzheimer_labels': y_alz_val,
                'parkinson_labels': y_park_val
            },
            'test': {
                'features': X_test_scaled,
                'alzheimer_labels': y_alz_test,
                'parkinson_labels': y_park_test
            },
            'scaler': self.scaler
        }
    
    def create_dataloaders(self, data_splits: Dict, batch_size: int = 32,
                          shuffle: bool = True) -> Dict:
        """
        Create PyTorch DataLoaders from data splits
        
        Args:
            data_splits: Dictionary with train, val, test splits
            batch_size: Batch size for training
            shuffle: Whether to shuffle training data
        
        Returns:
            Dictionary with PyTorch DataLoaders
        """
        train_dataset = MedicalDataset(
            data_splits['train']['features'],
            data_splits['train']['alzheimer_labels'],
            data_splits['train']['parkinson_labels']
        )
        
        val_dataset = MedicalDataset(
            data_splits['val']['features'],
            data_splits['val']['alzheimer_labels'],
            data_splits['val']['parkinson_labels']
        )
        
        test_dataset = MedicalDataset(
            data_splits['test']['features'],
            data_splits['test']['alzheimer_labels'],
            data_splits['test']['parkinson_labels']
        )
        
        train_loader = TorchDataLoader(train_dataset, batch_size=batch_size, shuffle=shuffle)
        val_loader = TorchDataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        test_loader = TorchDataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        
        return {
            'train': train_loader,
            'val': val_loader,
            'test': test_loader
        }

