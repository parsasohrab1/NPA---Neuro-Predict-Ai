#!/usr/bin/env python3
"""
Training and Validation Script
اسکریپت کامل برای آموزش و اعتبارسنجی مدل
"""
import sys
import argparse
from pathlib import Path
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.training.trainer import ModelTrainer
from app.services.training.validator import ClinicalValidator
from app.core.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Train and validate NeuroPredict-AI model')
    parser.add_argument('--data', type=str, required=True,
                       help='Path to training data CSV file')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--lr', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size')
    parser.add_argument('--output-dir', type=str, default='models',
                       help='Output directory for models')
    parser.add_argument('--early-stopping', type=int, default=10,
                       help='Early stopping patience')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed')
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("NeuroPredict-AI Model Training and Validation")
    logger.info("=" * 80)
    logger.info(f"Data file: {args.data}")
    logger.info(f"Epochs: {args.epochs}")
    logger.info(f"Learning rate: {args.lr}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info("")
    
    # Initialize trainer
    trainer = ModelTrainer(
        input_dim=50,
        hidden_dims=[256, 128, 64]
    )
    
    # Prepare data
    logger.info("Preparing data...")
    train_loader, val_loader, test_loader = trainer.prepare_data(
        data_path=args.data,
        test_size=0.2,
        val_size=0.1,
        random_seed=args.seed
    )
    
    # Create model
    logger.info("Creating model architecture...")
    trainer.create_model()
    
    # Train model
    logger.info("Starting training...")
    training_results = trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=args.epochs,
        learning_rate=args.lr,
        early_stopping_patience=args.early_stopping,
        save_best=True
    )
    
    logger.info("Training completed!")
    logger.info(f"Best validation metrics: {training_results['best_metrics']}")
    
    # Validate on test set
    logger.info("Validating on test set...")
    validator = ClinicalValidator()
    validation_results = validator.validate_model(
        model=trainer.model,
        test_loader=test_loader,
        device=trainer.device
    )
    
    # Generate reports
    logger.info("Generating validation report...")
    report = validator.generate_validation_report()
    print("\n" + report)
    
    # Save results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save model
    model_filename = f"model_{timestamp}.pth"
    trainer.save_model(
        model_filename,
        metadata={
            'training_results': training_results,
            'validation_results': validation_results,
            'timestamp': timestamp,
            'config': {
                'epochs': args.epochs,
                'learning_rate': args.lr,
                'batch_size': args.batch_size
            }
        }
    )
    
    # Save validation results
    validator.save_results(output_dir / f"validation_results_{timestamp}.json")
    
    # Save report
    report_path = output_dir / f"validation_report_{timestamp}.txt"
    validator.generate_validation_report(str(report_path))
    
    # Generate plots
    logger.info("Generating plots...")
    trainer.plot_training_history(str(output_dir / f"training_history_{timestamp}.png"))
    validator.plot_confusion_matrices(str(output_dir / f"confusion_matrices_{timestamp}.png"))
    
    logger.info("=" * 80)
    logger.info("Training and validation completed successfully!")
    logger.info(f"Results saved to: {output_dir}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

