"""
اعتبارسنجی مدل و محاسبه دقت
Model Validation and Accuracy Calculation

این اسکریپت مدل آموزش دیده را اعتبارسنجی می‌کند و دقت آن را محاسبه می‌کند
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from app.services.training import DataLoader, ModelEvaluator
from app.services.ai_model_service import MultiModalNeuralNetwork
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_model(model_path: Path, input_dim: int = 50, device: torch.device = None) -> MultiModalNeuralNetwork:
    """بارگذاری مدل از فایل"""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = MultiModalNeuralNetwork(input_dim=input_dim)
    
    if model_path.exists():
        model.load_state_dict(torch.load(model_path, map_location=device))
        logger.info(f"✅ Loaded model from {model_path}")
    else:
        logger.warning(f"⚠️  Model file not found: {model_path}")
        logger.warning("   Using randomly initialized model")
    
    model.to(device)
    model.eval()
    return model


def main():
    parser = argparse.ArgumentParser(
        description='Validate Model and Calculate Accuracy',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--model-path', type=str, default=None,
                       help='Path to model file (default: from settings or models directory)')
    parser.add_argument('--data-file', type=str, default=None,
                       help='Path to test data CSV file')
    parser.add_argument('--metrics-file', type=str, default=None,
                       help='Path to save metrics JSON (default: models/model_metrics.json)')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for validation')
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("📊 MODEL VALIDATION")
    logger.info("=" * 80)
    
    # Determine model path
    if args.model_path:
        model_path = Path(args.model_path)
    else:
        # Try default location
        model_path = Path(settings.ENSEMBLE_MODEL_PATH)
        if not model_path.exists():
            # Try models directory
            models_dir = Path("models")
            if models_dir.exists():
                model_files = list(models_dir.glob("*.pth"))
                if model_files:
                    model_path = sorted(model_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
                    logger.info(f"   Found model in models directory: {model_path}")
    
    logger.info(f"📁 Model path: {model_path}")
    
    # Determine data file
    if args.data_file:
        data_file = Path(args.data_file)
    else:
        # Default to real data
        project_root = Path(__file__).parent.parent.parent
        data_file = project_root / "data" / "real_data" / "csv" / "real_cognitive_data_complete.csv"
        if not data_file.exists():
            data_file = Path("data") / "real_data" / "csv" / "real_cognitive_data_complete.csv"
    
    logger.info(f"📁 Data file: {data_file}")
    
    if not data_file.exists():
        logger.error(f"❌ Data file not found: {data_file}")
        return 1
    
    # Check device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"🖥️  Device: {device}")
    
    # Load data
    logger.info("📊 Loading test data...")
    data_loader = DataLoader()
    
    try:
        df = data_loader.load_from_csv(str(data_file))
        logger.info(f"✅ Loaded {len(df)} samples")
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        return 1
    
    # Preprocess data
    logger.info("🔧 Preprocessing data...")
    features, alzheimer_labels, parkinson_labels = data_loader.preprocess_data(df)
    
    # Use 20% for validation (or use existing test set)
    from sklearn.model_selection import train_test_split
    _, X_test, _, y_alz_test, _, y_park_test = train_test_split(
        features, alzheimer_labels, parkinson_labels,
        test_size=0.2, random_state=42, stratify=alzheimer_labels
    )
    
    # Normalize
    X_test_scaled = data_loader.scaler.fit_transform(X_test)
    
    # Create data loader
    from app.services.training.data_loader import MedicalDataset
    from torch.utils.data import DataLoader as TorchDataLoader
    
    test_dataset = MedicalDataset(
        X_test_scaled,
        y_alz_test,
        y_park_test
    )
    test_loader = TorchDataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)
    
    logger.info(f"📊 Test set size: {len(test_dataset)}")
    
    # Load model
    logger.info("🧠 Loading model...")
    input_dim = features.shape[1]
    model = load_model(model_path, input_dim=input_dim, device=device)
    
    # Evaluate
    logger.info("📈 Evaluating model...")
    evaluator = ModelEvaluator()
    test_metrics = evaluator.evaluate_model(model, test_loader, device)
    
    # Calculate overall accuracy
    overall_accuracy = (test_metrics['alzheimer']['accuracy'] + test_metrics['parkinson']['accuracy']) / 2
    
    # Display results
    logger.info("=" * 80)
    logger.info("📊 VALIDATION RESULTS")
    logger.info("=" * 80)
    logger.info(f"")
    logger.info(f"Alzheimer's Disease:")
    logger.info(f"   ✅ Accuracy: {test_metrics['alzheimer']['accuracy']:.4f} ({test_metrics['alzheimer']['accuracy']*100:.2f}%)")
    logger.info(f"   📊 Precision: {test_metrics['alzheimer']['precision']:.4f}")
    logger.info(f"   🔍 Recall: {test_metrics['alzheimer']['recall']:.4f}")
    logger.info(f"   🎯 F1-Score: {test_metrics['alzheimer']['f1']:.4f}")
    logger.info(f"")
    logger.info(f"Parkinson's Disease:")
    logger.info(f"   ✅ Accuracy: {test_metrics['parkinson']['accuracy']:.4f} ({test_metrics['parkinson']['accuracy']*100:.2f}%)")
    logger.info(f"   📊 Precision: {test_metrics['parkinson']['precision']:.4f}")
    logger.info(f"   🔍 Recall: {test_metrics['parkinson']['recall']:.4f}")
    logger.info(f"   🎯 F1-Score: {test_metrics['parkinson']['f1']:.4f}")
    logger.info(f"")
    logger.info(f"🎯 Overall Accuracy: {overall_accuracy:.4f} ({overall_accuracy*100:.2f}%)")
    logger.info("=" * 80)
    
    # Save metrics
    metrics = {
        'validation_date': datetime.now().isoformat(),
        'model_path': str(model_path),
        'data_file': str(data_file),
        'test_samples': len(test_dataset),
        'alzheimer': {
            'accuracy': float(test_metrics['alzheimer']['accuracy']),
            'precision': float(test_metrics['alzheimer']['precision']),
            'recall': float(test_metrics['alzheimer']['recall']),
            'f1': float(test_metrics['alzheimer']['f1'])
        },
        'parkinson': {
            'accuracy': float(test_metrics['parkinson']['accuracy']),
            'precision': float(test_metrics['parkinson']['precision']),
            'recall': float(test_metrics['parkinson']['recall']),
            'f1': float(test_metrics['parkinson']['f1'])
        },
        'overall_accuracy': float(overall_accuracy)
    }
    
    # Determine output file
    if args.metrics_file:
        metrics_file = Path(args.metrics_file)
    else:
        metrics_file = Path("models") / "model_metrics.json"
    
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"💾 Saved metrics to {metrics_file}")
    logger.info("=" * 80)
    
    return 0


if __name__ == "__main__":
    exit(main())

