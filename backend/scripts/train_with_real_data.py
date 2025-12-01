"""
آموزش مجدد مدل با داده‌های واقعی بالینی
Retrain Model with Real Clinical Data

این اسکریپت مدل را با داده‌های واقعی جمع‌آوری شده آموزش می‌دهد
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
        logging.FileHandler('logs/training_real_data.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Train AI Model with Real Clinical Data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train with real data (default path)
  python train_with_real_data.py
  
  # Train with custom data file
  python train_with_real_data.py --data-file data/real_data/csv/real_cognitive_data_complete.csv
  
  # Custom training parameters
  python train_with_real_data.py --epochs 200 --batch-size 64 --learning-rate 0.0001
        """
    )
    
    # Data arguments
    parser.add_argument('--data-file', type=str, default=None,
                       help='Path to CSV file with real clinical data (default: data/real_data/csv/real_cognitive_data_complete.csv)')
    parser.add_argument('--data-dir', type=str, default=None,
                       help='Directory containing CSV data files')
    
    # Training arguments
    parser.add_argument('--epochs', type=int, default=150,
                       help='Number of training epochs (default: 150)')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for training (default: 32)')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate (default: 0.001)')
    parser.add_argument('--weight-decay', type=float, default=1e-5,
                       help='Weight decay for regularization (default: 1e-5)')
    parser.add_argument('--patience', type=int, default=15,
                       help='Early stopping patience (default: 15)')
    
    # Data split arguments
    parser.add_argument('--train-ratio', type=float, default=0.7,
                       help='Training set ratio (default: 0.7)')
    parser.add_argument('--val-ratio', type=float, default=0.15,
                       help='Validation set ratio (default: 0.15)')
    parser.add_argument('--test-ratio', type=float, default=0.15,
                       help='Test set ratio (default: 0.15)')
    
    # Model arguments
    parser.add_argument('--model-dir', type=str, default=None,
                       help='Directory to save models (default: models/real_data_trained)')
    parser.add_argument('--version', type=str, default=None,
                       help='Model version (auto-generated if not provided)')
    parser.add_argument('--description', type=str, default="Trained on real clinical data",
                       help='Model description')
    parser.add_argument('--set-active', action='store_true',
                       help='Set this model as active after training')
    
    args = parser.parse_args()
    
    # Create logs directory
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # Determine model directory
    if args.model_dir:
        model_dir = Path(args.model_dir)
    else:
        model_dir = Path("models") / "real_data_trained"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine data file
    if args.data_file:
        data_file = Path(args.data_file)
    else:
        # Default to real data
        project_root = Path(__file__).parent.parent.parent
        data_file = project_root / "data" / "real_data" / "csv" / "real_cognitive_data_complete.csv"
        
        # Fallback to alternative path
        if not data_file.exists():
            data_file = Path("data") / "real_data" / "csv" / "real_cognitive_data_complete.csv"
    
    logger.info("=" * 80)
    logger.info("🚀 NEUROPREDICT-AI MODEL TRAINING WITH REAL CLINICAL DATA")
    logger.info("=" * 80)
    logger.info(f"Data file: {data_file}")
    logger.info(f"Epochs: {args.epochs}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Learning rate: {args.learning_rate}")
    logger.info(f"Train/Val/Test ratio: {args.train_ratio}/{args.val_ratio}/{args.test_ratio}")
    logger.info(f"Model directory: {model_dir}")
    logger.info("=" * 80)
    
    # Check if data file exists
    if not data_file.exists():
        logger.error(f"❌ Data file not found: {data_file}")
        logger.error("   Please run data collection script first:")
        logger.error("   python data/collect_real_clinical_data.py")
        return 1
    
    # Check device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"🖥️  Using device: {device}")
    if device.type == 'cpu':
        logger.warning("⚠️  CUDA not available. Training will be slower on CPU.")
    
    # Load data
    logger.info("📊 Loading data...")
    data_loader = DataLoader(data_dir=args.data_dir)
    
    try:
        df = data_loader.load_from_csv(str(data_file))
        logger.info(f"✅ Loaded {len(df)} samples from real clinical data")
        logger.info(f"   Diagnosis distribution:")
        logger.info(f"   {df['diagnosis'].value_counts().to_dict()}")
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        return 1
    
    # Preprocess data
    logger.info("🔧 Preprocessing data...")
    try:
        features, alzheimer_labels, parkinson_labels = data_loader.preprocess_data(df)
        logger.info(f"✅ Preprocessed {len(features)} samples with {features.shape[1]} features")
    except Exception as e:
        logger.error(f"❌ Error preprocessing data: {e}")
        logger.error("   Make sure the data file has all required columns")
        return 1
    
    # Split data
    logger.info("📂 Splitting data...")
    try:
        data_splits = data_loader.split_data(
            features, alzheimer_labels, parkinson_labels,
            train_ratio=args.train_ratio,
            val_ratio=args.val_ratio,
            test_ratio=args.test_ratio
        )
        logger.info("✅ Data split complete")
    except Exception as e:
        logger.error(f"❌ Error splitting data: {e}")
        return 1
    
    # Create data loaders
    logger.info("🔄 Creating data loaders...")
    dataloaders = data_loader.create_dataloaders(
        data_splits, batch_size=args.batch_size
    )
    
    # Initialize model
    logger.info("🧠 Initializing model...")
    input_dim = features.shape[1]
    model = MultiModalNeuralNetwork(input_dim=input_dim)
    model.to(device)
    
    logger.info(f"   Model input dimension: {input_dim}")
    logger.info(f"   Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Initialize trainer
    trainer = ModelTrainer(model, device, model_dir=model_dir)
    
    # Train model
    logger.info("🏋️  Starting training...")
    logger.info("=" * 80)
    
    try:
        training_results = trainer.train(
            dataloaders['train'],
            dataloaders['val'],
            epochs=args.epochs,
            learning_rate=args.learning_rate,
            weight_decay=args.weight_decay,
            patience=args.patience
        )
        
        logger.info("=" * 80)
        logger.info("✅ Training complete!")
        logger.info(f"   Best validation loss: {training_results['best_val_loss']:.4f}")
        logger.info(f"   Epochs trained: {len(training_results['training_history']['train_loss'])}")
    except Exception as e:
        logger.error(f"❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Load best model
    if training_results['best_model_path']:
        logger.info(f"📥 Loading best model from {training_results['best_model_path']}")
        model.load_state_dict(torch.load(training_results['best_model_path'], map_location=device))
    else:
        logger.warning("⚠️  No best model path found. Using current model state.")
    
    # Evaluate on test set
    logger.info("📊 Evaluating on test set...")
    evaluator = ModelEvaluator()
    
    try:
        test_metrics = evaluator.evaluate_model(model, dataloaders['test'], device)
        
        logger.info("=" * 80)
        logger.info("📈 TEST SET METRICS")
        logger.info("=" * 80)
        logger.info(f"Alzheimer's Disease:")
        logger.info(f"   Accuracy: {test_metrics['alzheimer']['accuracy']:.4f}")
        logger.info(f"   Precision: {test_metrics['alzheimer']['precision']:.4f}")
        logger.info(f"   Recall: {test_metrics['alzheimer']['recall']:.4f}")
        logger.info(f"   F1-Score: {test_metrics['alzheimer']['f1']:.4f}")
        logger.info(f"")
        logger.info(f"Parkinson's Disease:")
        logger.info(f"   Accuracy: {test_metrics['parkinson']['accuracy']:.4f}")
        logger.info(f"   Precision: {test_metrics['parkinson']['precision']:.4f}")
        logger.info(f"   Recall: {test_metrics['parkinson']['recall']:.4f}")
        logger.info(f"   F1-Score: {test_metrics['parkinson']['f1']:.4f}")
        logger.info("=" * 80)
    except Exception as e:
        logger.error(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Generate clinical report
    logger.info("📝 Generating clinical report...")
    try:
        report = evaluator.generate_clinical_report(test_metrics)
        logger.info("\n" + report)
    except Exception as e:
        logger.warning(f"⚠️  Error generating report: {e}")
        report = f"Training completed. Metrics: {test_metrics}"
    
    # Save report
    report_path = model_dir / f"clinical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    logger.info(f"💾 Saved clinical report to {report_path}")
    
    # Save metrics to JSON for dashboard
    metrics_json_path = model_dir / "model_metrics.json"
    metrics_json = {
        'training_date': datetime.now().isoformat(),
        'data_file': str(data_file),
        'training': {
            'best_val_loss': float(training_results['best_val_loss']),
            'epochs_trained': len(training_results['training_history']['train_loss']),
            'training_history': {
                k: [float(v) for v in values] 
                for k, values in training_results['training_history'].items()
            }
        },
        'test_metrics': {
            'alzheimer': {k: float(v) for k, v in test_metrics['alzheimer'].items()},
            'parkinson': {k: float(v) for k, v in test_metrics['parkinson'].items()}
        },
        'overall_accuracy': float((test_metrics['alzheimer']['accuracy'] + test_metrics['parkinson']['accuracy']) / 2)
    }
    
    import json
    with open(metrics_json_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_json, f, indent=2)
    logger.info(f"💾 Saved metrics JSON to {metrics_json_path}")
    
    # Register model
    logger.info("📋 Registering model...")
    registry = ModelRegistry(model_dir / "registry.json")
    
    model_metrics = {
        'training': {
            'best_val_loss': training_results['best_val_loss'],
            'epochs_trained': len(training_results['training_history']['train_loss'])
        },
        'test': test_metrics
    }
    
    version = registry.register_model(
        str(training_results['best_model_path']) if training_results['best_model_path'] else None,
        model_metrics,
        version=args.version,
        description=args.description
    )
    
    logger.info(f"✅ Model registered as version: {version}")
    
    # Set as active if requested
    if args.set_active:
        registry.set_active_model(version)
        logger.info(f"✅ Set model version {version} as active")
        
        # Copy best model to default location
        if training_results['best_model_path']:
            default_model_path = Path(settings.ENSEMBLE_MODEL_PATH)
            default_model_path.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy(training_results['best_model_path'], default_model_path)
            logger.info(f"📋 Copied model to default location: {default_model_path}")
    
    # Final summary
    logger.info("=" * 80)
    logger.info("🎉 TRAINING COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"📁 Model directory: {model_dir}")
    logger.info(f"📊 Best model: {training_results['best_model_path']}")
    logger.info(f"🔢 Model version: {version}")
    logger.info(f"📈 Overall accuracy: {metrics_json['overall_accuracy']:.2%}")
    logger.info(f"📄 Clinical report: {report_path}")
    logger.info(f"📊 Metrics JSON: {metrics_json_path}")
    logger.info("=" * 80)
    logger.info("")
    logger.info("💡 Next steps:")
    logger.info("   1. Review the clinical report")
    logger.info("   2. Check model metrics JSON for dashboard integration")
    logger.info("   3. If satisfied, use --set-active flag to activate the model")
    logger.info("=" * 80)
    
    return 0


if __name__ == "__main__":
    exit(main())

