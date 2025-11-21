"""
Generate Synthetic Training Data and Train a Model
Creates realistic synthetic medical data and trains an AI model for demonstration
"""
import sys
import argparse
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from app.services.training import DataLoader, ModelTrainer, ModelEvaluator, ModelRegistry
from app.services.ai_model_service import MultiModalNeuralNetwork
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def generate_synthetic_data(n_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic medical data that mimics real clinical patterns
    
    Args:
        n_samples: Number of samples to generate
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with synthetic medical data
    """
    np.random.seed(seed)
    logger.info(f"Generating {n_samples} synthetic samples...")
    
    data = []
    
    for i in range(n_samples):
        # Determine disease status first
        disease_prob = np.random.random()
        if disease_prob < 0.3:  # 30% Alzheimer's
            diagnosis = 'Alzheimer'
            # Alzheimer's patterns
            age = np.random.normal(75, 8)  # Older population
            mmse = np.random.normal(20, 4)  # Lower cognitive scores
            moca = np.random.normal(18, 4)
            memory_score = np.random.normal(35, 10)
            amyloid_beta = np.random.normal(650, 100)  # Higher amyloid
            tau_protein = np.random.normal(350, 80)  # Higher tau
            dopamine = np.random.normal(90, 15)  # Normal dopamine
            hippocampal_volume = np.random.normal(2500, 400)  # Reduced volume
            cortical_thickness = np.random.normal(2.0, 0.3)  # Thinner cortex
        elif disease_prob < 0.5:  # 20% Parkinson's
            diagnosis = 'Parkinson'
            # Parkinson's patterns
            age = np.random.normal(70, 7)
            mmse = np.random.normal(26, 3)  # Better cognitive scores
            moca = np.random.normal(24, 3)
            memory_score = np.random.normal(55, 12)
            amyloid_beta = np.random.normal(550, 80)
            tau_protein = np.random.normal(220, 60)
            dopamine = np.random.normal(60, 20)  # Lower dopamine
            hippocampal_volume = np.random.normal(3200, 500)
            cortical_thickness = np.random.normal(2.4, 0.3)
        else:  # 50% Normal
            diagnosis = 'Normal'
            # Normal patterns
            age = np.random.normal(65, 10)
            mmse = np.random.normal(28, 2)  # Higher cognitive scores
            moca = np.random.normal(26, 2)
            memory_score = np.random.normal(75, 10)
            amyloid_beta = np.random.normal(500, 80)
            tau_protein = np.random.normal(180, 50)
            dopamine = np.random.normal(110, 15)  # Normal dopamine
            hippocampal_volume = np.random.normal(3800, 500)
            cortical_thickness = np.random.normal(2.6, 0.3)
        
        # Clip values to realistic ranges
        age = max(50, min(95, age))
        mmse = max(0, min(30, mmse))
        moca = max(0, min(30, moca))
        memory_score = max(0, min(100, memory_score))
        amyloid_beta = max(200, min(1000, amyloid_beta))
        tau_protein = max(50, min(600, tau_protein))
        dopamine = max(30, min(150, dopamine))
        hippocampal_volume = max(1500, min(5000, hippocampal_volume))
        cortical_thickness = max(1.5, min(3.5, cortical_thickness))
        
        # Other features
        gender = np.random.choice(['Male', 'Female'])
        education_years = np.random.choice([8, 12, 14, 16, 18, 20], p=[0.1, 0.2, 0.15, 0.25, 0.2, 0.1])
        attention_score = np.random.normal(65 if diagnosis == 'Normal' else 50, 12)
        executive_function_score = np.random.normal(68 if diagnosis == 'Normal' else 48, 12)
        apoe_e4_status = np.random.choice([0, 1], p=[0.7, 0.3])  # 30% have APOE-e4
        
        # MRI features
        ventricular_volume = np.random.normal(35000, 8000)
        white_matter_hyperintensities = np.random.exponential(2) if diagnosis != 'Normal' else np.random.exponential(1)
        white_matter_hyperintensities = min(10, white_matter_hyperintensities)
        brain_volume_total = np.random.normal(1200000, 100000)
        
        # Clip additional features
        attention_score = max(0, min(100, attention_score))
        executive_function_score = max(0, min(100, executive_function_score))
        ventricular_volume = max(20000, min(70000, ventricular_volume))
        brain_volume_total = max(900000, min(1500000, brain_volume_total))
        
        data.append({
            'age': age,
            'gender': gender,
            'education_years': education_years,
            'mmse_score': mmse,
            'moca_score': moca,
            'memory_score': memory_score,
            'attention_score': attention_score,
            'executive_function_score': executive_function_score,
            'amyloid_beta': amyloid_beta,
            'tau_protein': tau_protein,
            'dopamine_level': dopamine,
            'apoe_e4_status': apoe_e4_status,
            'hippocampal_volume': hippocampal_volume,
            'cortical_thickness': cortical_thickness,
            'ventricular_volume': ventricular_volume,
            'white_matter_hyperintensities': white_matter_hyperintensities,
            'brain_volume_total': brain_volume_total,
            'diagnosis': diagnosis
        })
    
    df = pd.DataFrame(data)
    logger.info(f"Generated {len(df)} samples")
    logger.info(f"Diagnosis distribution:\n{df['diagnosis'].value_counts()}")
    
    return df


def main():
    parser = argparse.ArgumentParser(
        description='Generate synthetic data and train AI model for NeuroPredict-AI'
    )
    parser.add_argument('--samples', type=int, default=1000,
                       help='Number of synthetic samples to generate')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for training')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Output directory for data and models')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip training and only generate data')
    parser.add_argument('--set-active', action='store_true',
                       help='Set trained model as active')
    
    args = parser.parse_args()
    
    # Create directories
    output_dir = Path(args.output_dir) if args.output_dir else Path("data/synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "csv").mkdir(parents=True, exist_ok=True)
    
    Path("logs").mkdir(parents=True, exist_ok=True)
    Path("models").mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("SYNTHETIC DATA GENERATION AND MODEL TRAINING")
    logger.info("=" * 80)
    logger.info(f"Samples: {args.samples}")
    logger.info(f"Epochs: {args.epochs}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Output directory: {output_dir}")
    logger.info("=" * 80)
    
    # Generate synthetic data
    df = generate_synthetic_data(n_samples=args.samples)
    
    # Save synthetic data
    csv_path = output_dir / "csv" / "synthetic_dataset.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"Saved synthetic data to {csv_path}")
    
    if args.skip_training:
        logger.info("Skipping training (--skip-training flag set)")
        return
    
    # Check device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    
    # Initialize data loader
    data_loader = DataLoader(data_dir=str(output_dir / "csv"))
    
    # Preprocess data
    logger.info("Preprocessing data...")
    features, alzheimer_labels, parkinson_labels = data_loader.preprocess_data(df)
    
    # Split data
    logger.info("Splitting data...")
    data_splits = data_loader.split_data(
        features, alzheimer_labels, parkinson_labels,
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15
    )
    
    # Create data loaders
    logger.info("Creating data loaders...")
    dataloaders = data_loader.create_dataloaders(
        data_splits, batch_size=args.batch_size
    )
    
    # Initialize model
    logger.info("Initializing model...")
    input_dim = features.shape[1]
    model = MultiModalNeuralNetwork(input_dim=input_dim)
    model.to(device)
    
    # Initialize trainer
    model_dir = Path("models")
    trainer = ModelTrainer(model, device, model_dir=model_dir)
    
    # Train model
    logger.info("Starting training...")
    training_results = trainer.train(
        dataloaders['train'],
        dataloaders['val'],
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        patience=10
    )
    
    # Load best model
    if training_results['best_model_path']:
        logger.info(f"Loading best model from {training_results['best_model_path']}")
        model.load_state_dict(torch.load(training_results['best_model_path'], map_location=device))
    else:
        logger.warning("No best model found, using current model state")
    
    # Evaluate on test set
    logger.info("Evaluating on test set...")
    evaluator = ModelEvaluator()
    test_metrics = evaluator.evaluate_model(model, dataloaders['test'], device)
    
    # Generate clinical report
    report = evaluator.generate_clinical_report(test_metrics)
    logger.info("\n" + report)
    
    # Save report
    report_path = model_dir / f"clinical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    logger.info(f"Saved clinical report to {report_path}")
    
    # Register model
    logger.info("Registering model...")
    registry = ModelRegistry(model_dir / "registry.json")
    
    model_metrics = {
        'training': {
            'best_val_loss': training_results['best_val_loss'],
            'epochs_trained': len(training_results['training_history']['train_loss'])
        },
        'test': test_metrics
    }
    
    version = registry.register_model(
        Path(training_results['best_model_path']),
        model_metrics,
        version=f"synthetic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        description=f"Model trained on {args.samples} synthetic samples"
    )
    
    # Set as active if requested
    if args.set_active:
        registry.set_active_model(version)
        logger.info(f"Set model version {version} as active")
        
        # Copy to default location
        if training_results['best_model_path']:
            default_model_path = Path(settings.ENSEMBLE_MODEL_PATH)
            import shutil
            shutil.copy(training_results['best_model_path'], default_model_path)
            logger.info(f"Copied model to default location: {default_model_path}")
    
    logger.info("=" * 80)
    logger.info("TRAINING COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"Best model: {training_results['best_model_path']}")
    logger.info(f"Model version: {version}")
    logger.info(f"Test metrics saved to: {report_path}")
    logger.info("=" * 80)
    logger.info("\n⚠️  IMPORTANT NOTES:")
    logger.info("1. This model was trained on SYNTHETIC data for demonstration purposes")
    logger.info("2. It is NOT suitable for clinical use in production")
    logger.info("3. For production use, train on real, validated medical data")
    logger.info("4. Clinical validation studies are required before deployment")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

