"""
Model Evaluation Script
Evaluates a trained model on test data with clinical validation metrics
"""
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from app.services.training import DataLoader, ModelEvaluator, ModelRegistry
from app.services.ai_model_service import MultiModalNeuralNetwork
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/evaluation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Evaluate AI Model for NeuroPredict-AI')
    parser.add_argument('--model-path', type=str, default=None,
                       help='Path to model file')
    parser.add_argument('--model-version', type=str, default=None,
                       help='Model version from registry')
    parser.add_argument('--data-dir', type=str, default=None,
                       help='Directory containing CSV data files')
    parser.add_argument('--csv-file', type=str, default=None,
                       help='Path to CSV file with test data')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for evaluation')
    parser.add_argument('--threshold', type=float, default=0.5,
                       help='Classification threshold')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Directory to save evaluation results')
    
    args = parser.parse_args()
    
    # Create logs directory
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # Create output directory
    output_dir = Path(args.output_dir) if args.output_dir else Path("models")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("NEUROPREDICT-AI MODEL EVALUATION")
    logger.info("=" * 80)
    
    # Check device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    
    # Load model
    logger.info("Loading model...")
    model_path = None
    
    if args.model_path:
        model_path = Path(args.model_path)
    elif args.model_version:
        registry = ModelRegistry(Path(settings.MODEL_REGISTRY_PATH))
        model_entry = registry.get_model(args.model_version)
        if model_entry:
            model_path = Path(model_entry['model_path'])
        else:
            logger.error(f"Model version {args.model_version} not found in registry")
            return
    else:
        # Try to get active model from registry
        registry = ModelRegistry(Path(settings.MODEL_REGISTRY_PATH))
        active_model = registry.get_active_model()
        if active_model:
            model_path = Path(active_model['model_path'])
            logger.info(f"Using active model: {active_model['version']}")
        else:
            # Try default path
            model_path = Path(settings.ENSEMBLE_MODEL_PATH)
            if not model_path.exists():
                logger.error("No model specified and no default model found")
                return
    
    if not model_path or not model_path.exists():
        logger.error(f"Model file not found: {model_path}")
        return
    
    logger.info(f"Loading model from: {model_path}")
    
    # Initialize model
    input_dim = 50  # Default input dimension
    model = MultiModalNeuralNetwork(input_dim=input_dim)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    
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
    
    # Create test dataset (use all data for evaluation if no split)
    # In practice, you should use a separate test set
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Create data loader
    from app.services.training.data_loader import MedicalDataset
    from torch.utils.data import DataLoader as TorchDataLoader
    
    test_dataset = MedicalDataset(features_scaled, alzheimer_labels, parkinson_labels)
    test_loader = TorchDataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)
    
    # Evaluate model
    logger.info("Evaluating model...")
    evaluator = ModelEvaluator()
    test_metrics = evaluator.evaluate_model(model, test_loader, device, threshold=args.threshold)
    
    # Generate clinical report
    report = evaluator.generate_clinical_report(test_metrics)
    logger.info("\n" + report)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"evaluation_report_{timestamp}.txt"
    with open(report_path, 'w') as f:
        f.write(report)
        f.write(f"\n\nModel Path: {model_path}\n")
        f.write(f"Evaluation Date: {datetime.now().isoformat()}\n")
        f.write(f"Threshold: {args.threshold}\n")
    
    logger.info(f"Saved evaluation report to {report_path}")
    
    # Save metrics as JSON
    import json
    metrics_path = output_dir / f"evaluation_metrics_{timestamp}.json"
    with open(metrics_path, 'w') as f:
        json.dump({
            'model_path': str(model_path),
            'evaluation_date': datetime.now().isoformat(),
            'threshold': args.threshold,
            'metrics': test_metrics
        }, f, indent=2)
    
    logger.info(f"Saved evaluation metrics to {metrics_path}")
    
    logger.info("=" * 80)
    logger.info("EVALUATION COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"Report: {report_path}")
    logger.info(f"Metrics: {metrics_path}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

