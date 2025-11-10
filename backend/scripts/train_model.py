"""
Training Script for AI Models
Trains the multi-modal neural network on real data with clinical validation
"""
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

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


def main():
    parser = argparse.ArgumentParser(description='Train AI Model for NeuroPredict-AI')
    parser.add_argument('--data-dir', type=str, default=None,
                       help='Directory containing CSV data files')
    parser.add_argument('--csv-file', type=str, default=None,
                       help='Path to CSV file with training data')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for training')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--weight-decay', type=float, default=1e-5,
                       help='Weight decay for regularization')
    parser.add_argument('--patience', type=int, default=10,
                       help='Early stopping patience')
    parser.add_argument('--train-ratio', type=float, default=0.7,
                       help='Training set ratio')
    parser.add_argument('--val-ratio', type=float, default=0.15,
                       help='Validation set ratio')
    parser.add_argument('--test-ratio', type=float, default=0.15,
                       help='Test set ratio')
    parser.add_argument('--model-dir', type=str, default=None,
                       help='Directory to save models')
    parser.add_argument('--version', type=str, default=None,
                       help='Model version (auto-generated if not provided)')
    parser.add_argument('--description', type=str, default=None,
                       help='Model description')
    parser.add_argument('--set-active', action='store_true',
                       help='Set this model as active after training')
    
    args = parser.parse_args()
    
    # Create logs directory
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # Create models directory
    model_dir = Path(args.model_dir) if args.model_dir else Path("models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("NEUROPREDICT-AI MODEL TRAINING")
    logger.info("=" * 80)
    logger.info(f"Data directory: {args.data_dir}")
    logger.info(f"CSV file: {args.csv_file}")
    logger.info(f"Epochs: {args.epochs}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Learning rate: {args.learning_rate}")
    logger.info(f"Train/Val/Test ratio: {args.train_ratio}/{args.val_ratio}/{args.test_ratio}")
    logger.info("=" * 80)
    
    # Check device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    
    # Load data
    logger.info("Loading data...")
    data_loader = DataLoader(data_dir=args.data_dir)
    
    if args.csv_file:
        df = data_loader.load_from_csv(args.csv_file)
    else:
        df = data_loader.load_from_csv()
    
    # Preprocess data
    logger.info("Preprocessing data...")
    features, alzheimer_labels, parkinson_labels = data_loader.preprocess_data(df)
    
    # Split data
    logger.info("Splitting data...")
    data_splits = data_loader.split_data(
        features, alzheimer_labels, parkinson_labels,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
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
    trainer = ModelTrainer(model, device, model_dir=model_dir)
    
    # Train model
    logger.info("Starting training...")
    training_results = trainer.train(
        dataloaders['train'],
        dataloaders['val'],
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        patience=args.patience
    )
    
    # Load best model
    if training_results['best_model_path']:
        logger.info(f"Loading best model from {training_results['best_model_path']}")
        model.load_state_dict(torch.load(training_results['best_model_path'], map_location=device))
    
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
        training_results['best_model_path'],
        model_metrics,
        version=args.version,
        description=args.description
    )
    
    # Set as active if requested
    if args.set_active:
        registry.set_active_model(version)
        logger.info(f"Set model version {version} as active")
    
    # Copy best model to default location if it's the active model
    if args.set_active and training_results['best_model_path']:
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


if __name__ == "__main__":
    main()

