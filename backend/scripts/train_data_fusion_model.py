"""
Training Script for Data Fusion Deep Learning Model
Generates training data from existing medical records using current scoring methods,
then trains a Deep Learning model to replace manual calculations.
"""
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
import asyncio
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from app.db.session import AsyncSessionLocal, init_db
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.services.data_fusion_service import DataFusionService
from app.services.data_fusion_model import DataFusionScoringModel
from sqlalchemy import select

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_fusion_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataFusionDataset(Dataset):
    """Dataset for data fusion model training"""
    
    def __init__(self, features: np.ndarray, targets: dict):
        self.features = torch.FloatTensor(features)
        self.targets = {k: torch.FloatTensor(v) for k, v in targets.items()}
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return {
            'features': self.features[idx],
            **{k: v[idx] for k, v in self.targets.items()}
        }


def extract_features(medical_record: MedicalRecord, patient: Patient) -> np.ndarray:
    """
    Extract features from medical record for model input
    
    Returns normalized feature vector
    """
    features = []
    
    # Cognitive features (normalized)
    features.append(medical_record.mmse_score / 30.0 if medical_record.mmse_score is not None else 0.0)
    features.append(medical_record.moca_score / 30.0 if medical_record.moca_score is not None else 0.0)
    features.append(medical_record.memory_score / 100.0 if medical_record.memory_score is not None else 0.0)
    features.append(medical_record.attention_score / 100.0 if medical_record.attention_score is not None else 0.0)
    features.append(medical_record.executive_function_score / 100.0 if medical_record.executive_function_score is not None else 0.0)
    
    # Biomarker features (normalized)
    features.append((medical_record.amyloid_beta - 200) / 800.0 if medical_record.amyloid_beta is not None else 0.0)  # Normalize around 600
    features.append((medical_record.tau_protein - 100) / 700.0 if medical_record.tau_protein is not None else 0.0)  # Normalize around 200
    features.append((medical_record.dopamine_level - 50) / 150.0 if medical_record.dopamine_level is not None else 0.0)  # Normalize around 100
    features.append(1.0 if medical_record.apoe_e4_status else 0.0 if medical_record.apoe_e4_status is not None else 0.0)
    
    # Imaging features (normalized)
    features.append((medical_record.hippocampal_volume - 2000) / 2000.0 if medical_record.hippocampal_volume is not None else 0.0)  # Normalize around 3500
    features.append((medical_record.cortical_thickness - 1.5) / 1.5 if medical_record.cortical_thickness is not None else 0.0)  # Normalize around 2.3
    features.append((medical_record.ventricular_volume - 20000) / 30000.0 if medical_record.ventricular_volume is not None else 0.0)  # Normalize around 30000
    features.append((medical_record.white_matter_hyperintensities - 0) / 20.0 if medical_record.white_matter_hyperintensities is not None else 0.0)
    features.append((medical_record.brain_volume_total - 1000000) / 200000.0 if medical_record.brain_volume_total is not None else 0.0)  # Normalize around 1100000
    
    # Patient demographics
    age = (datetime.now().date() - patient.date_of_birth).days / 365.25
    features.append(age / 100.0)  # Normalize age
    features.append(1.0 if patient.gender.value == 'male' else 0.0)
    features.append((patient.education_years or 12) / 20.0)  # Normalize education
    
    return np.array(features, dtype=np.float32)


async def generate_training_data(limit: int = None) -> tuple:
    """
    Generate training data from existing medical records
    
    Uses current DataFusionService methods to generate ground truth scores
    """
    logger.info("Generating training data from database...")
    
    async with AsyncSessionLocal() as db:
        # Query medical records with patients
        query = select(MedicalRecord).join(Patient)
        if limit:
            query = query.limit(limit)
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        logger.info(f"Found {len(records)} medical records")
        
        if len(records) == 0:
            raise ValueError("No medical records found in database")
        
        features_list = []
        targets = {
            'cognitive_score': [],
            'biomarker_score': [],
            'imaging_score': [],
            'cognitive_confidence': [],
            'biomarker_confidence': [],
            'imaging_confidence': [],
            'cognitive_biomarker_correlation': [],
            'cognitive_imaging_correlation': [],
            'biomarker_imaging_correlation': [],
            'integrated_fusion_score': [],
            'alzheimer_fusion_score': [],
            'parkinson_fusion_score': [],
            'alzheimer_concordance': [],
            'alzheimer_alignment': [],
            'alzheimer_hippo_corr': [],
            'parkinson_concordance': [],
            'parkinson_alignment': [],
            'parkinson_corr': [],
        }
        
        valid_count = 0
        
        for record in records:
            try:
                # Get patient
                patient_result = await db.execute(
                    select(Patient).where(Patient.id == record.patient_id)
                )
                patient = patient_result.scalar_one_or_none()
                
                if not patient:
                    continue
                
                # Extract features
                features = extract_features(record, patient)
                features_list.append(features)
                
                # Generate ground truth scores using current methods
                cog_score, cog_conf = DataFusionService._assess_cognitive_modality(record)
                bio_score, bio_conf = DataFusionService._assess_biomarker_modality(record)
                img_score, img_conf = DataFusionService._assess_imaging_modality(record)
                
                # Calculate correlations
                correlations = DataFusionService._calculate_cross_modal_correlations(
                    record, cog_score, bio_score, img_score
                )
                
                # Integrated fusion score
                integrated_score = DataFusionService._calculate_integrated_fusion_score(
                    cog_score, bio_score, img_score, cog_conf, bio_conf, img_conf
                )
                
                # Disease-specific analysis
                ad_analysis = DataFusionService._analyze_alzheimer_fusion(record, patient)
                pd_analysis = DataFusionService._analyze_parkinson_fusion(record, patient)
                
                # Store targets
                targets['cognitive_score'].append(cog_score / 100.0)
                targets['biomarker_score'].append(bio_score / 100.0)
                targets['imaging_score'].append(img_score / 100.0)
                targets['cognitive_confidence'].append(cog_conf)
                targets['biomarker_confidence'].append(bio_conf)
                targets['imaging_confidence'].append(img_conf)
                targets['cognitive_biomarker_correlation'].append(correlations['cognitive_biomarker'])
                targets['cognitive_imaging_correlation'].append(correlations['cognitive_imaging'])
                targets['biomarker_imaging_correlation'].append(correlations['biomarker_imaging'])
                targets['integrated_fusion_score'].append(integrated_score / 100.0)
                targets['alzheimer_fusion_score'].append(ad_analysis['score'] / 100.0)
                targets['parkinson_fusion_score'].append(pd_analysis['score'] / 100.0)
                targets['alzheimer_concordance'].append(ad_analysis['amyloid_tau_concordance'] / 100.0)
                targets['alzheimer_alignment'].append(ad_analysis['cognitive_biomarker_alignment'] / 100.0)
                targets['alzheimer_hippo_corr'].append(ad_analysis['hippocampal_correlation'] / 100.0)
                targets['parkinson_concordance'].append(pd_analysis['dopamine_cognitive_concordance'] / 100.0)
                targets['parkinson_alignment'].append(pd_analysis['motor_cognitive_alignment'] / 100.0)
                targets['parkinson_corr'].append(pd_analysis['imaging_biomarker_correlation'] / 100.0)
                
                valid_count += 1
                
            except Exception as e:
                logger.warning(f"Error processing record {record.id}: {e}")
                continue
        
        logger.info(f"Generated {valid_count} valid training samples")
        
        if valid_count == 0:
            raise ValueError("No valid training samples generated")
        
        features_array = np.array(features_list)
        targets_dict = {k: np.array(v) for k, v in targets.items()}
        
        return features_array, targets_dict


def train_model(features: np.ndarray, targets: dict, 
                epochs: int = 100, batch_size: int = 32,
                learning_rate: float = 0.001, model_dir: Path = None):
    """
    Train the data fusion scoring model
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    
    # Normalize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Split data
    train_features, val_features, train_targets, val_targets = train_test_split(
        features_scaled, targets, test_size=0.2, random_state=42
    )
    
    # Create datasets
    train_dataset = DataFusionDataset(train_features, train_targets)
    val_dataset = DataFusionDataset(val_features, val_targets)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Initialize model
    input_dim = features_scaled.shape[1]
    model = DataFusionScoringModel(input_dim=input_dim)
    model.to(device)
    
    # Loss function - MSE for regression
    criterion = nn.MSELoss()
    
    # Optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, verbose=True
    )
    
    # Training loop
    best_val_loss = float('inf')
    patience = 10
    patience_counter = 0
    best_model_path = None
    
    logger.info(f"Starting training for {epochs} epochs...")
    logger.info(f"Training samples: {len(train_dataset)}, Validation samples: {len(val_dataset)}")
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        for batch in train_loader:
            optimizer.zero_grad()
            
            features_batch = batch['features'].to(device)
            outputs = model(features_batch)
            
            # Calculate loss for all targets
            loss = 0.0
            for key in targets.keys():
                target_batch = batch[key].to(device)
                if key.endswith('_score') or key.endswith('_correlation') or key.endswith('_confidence') or \
                   key in ['alzheimer_concordance', 'alzheimer_alignment', 'alzheimer_hippo_corr',
                           'parkinson_concordance', 'parkinson_alignment', 'parkinson_corr']:
                    pred_key = key
                    if key == 'alzheimer_concordance':
                        pred_key = 'alzheimer_concordance'
                    elif key == 'alzheimer_alignment':
                        pred_key = 'alzheimer_alignment'
                    elif key == 'alzheimer_hippo_corr':
                        pred_key = 'alzheimer_hippo_corr'
                    elif key == 'parkinson_concordance':
                        pred_key = 'parkinson_concordance'
                    elif key == 'parkinson_alignment':
                        pred_key = 'parkinson_alignment'
                    elif key == 'parkinson_corr':
                        pred_key = 'parkinson_corr'
                    
                    if pred_key in outputs:
                        loss += criterion(outputs[pred_key].squeeze() / 100.0 if 'score' in pred_key else outputs[pred_key].squeeze(), 
                                        target_batch)
            
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch in val_loader:
                features_batch = batch['features'].to(device)
                outputs = model(features_batch)
                
                loss = 0.0
                for key in targets.keys():
                    target_batch = batch[key].to(device)
                    pred_key = key
                    if key in ['alzheimer_concordance', 'alzheimer_alignment', 'alzheimer_hippo_corr',
                               'parkinson_concordance', 'parkinson_alignment', 'parkinson_corr']:
                        pred_key = key
                    
                    if pred_key in outputs:
                        loss += criterion(outputs[pred_key].squeeze() / 100.0 if 'score' in pred_key else outputs[pred_key].squeeze(), 
                                        target_batch)
                
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        
        # Update learning rate
        scheduler.step(val_loss)
        
        logger.info(f"Epoch {epoch + 1}/{epochs} - Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            
            if model_dir:
                model_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                best_model_path = model_dir / f"data_fusion_model_{timestamp}.pth"
                torch.save({
                    'model_state_dict': model.state_dict(),
                    'scaler': scaler,
                    'input_dim': input_dim,
                    'epoch': epoch + 1,
                    'val_loss': val_loss,
                }, best_model_path)
                logger.info(f"Saved best model to {best_model_path}")
        else:
            patience_counter += 1
        
        # Early stopping
        if patience_counter >= patience:
            logger.info(f"Early stopping at epoch {epoch + 1}")
            break
    
    # Save scaler
    if model_dir and best_model_path:
        scaler_path = model_dir / "data_fusion_scaler.pkl"
        import pickle
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        logger.info(f"Saved scaler to {scaler_path}")
    
    return best_model_path, scaler


async def main():
    parser = argparse.ArgumentParser(description='Train Data Fusion Deep Learning Model')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of records to use for training')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for training')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--model-dir', type=str, default='backend/models',
                       help='Directory to save models')
    
    args = parser.parse_args()
    
    # Create logs directory
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    await init_db()
    
    try:
        # Generate training data
        features, targets = await generate_training_data(limit=args.limit)
        
        # Train model
        model_dir = Path(args.model_dir)
        model_path, scaler = train_model(
            features, targets,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            model_dir=model_dir
        )
        
        logger.info("=" * 80)
        logger.info("TRAINING COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"Best model saved to: {model_path}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

