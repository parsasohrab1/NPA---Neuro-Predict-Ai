#!/usr/bin/env python3
"""
Training and Validation Script
اسکریپت کامل برای آموزش و اعتبارسنجی مدل

End-to-end pipeline: patient-level split -> (optional) cross-validation ->
class-weighted deep model training -> baseline comparison -> clinical
validation with calibration/subgroup fairness -> gated registry activation ->
drift reference capture. Every stage logs why it made the call it made, so a
reviewer can audit a run without re-deriving it from raw numbers.
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
from app.services.training.baseline_trainer import BaselineTrainer
from app.services.training.model_registry import ModelRegistry
from app.services.training.drift_monitor import DriftMonitor

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
    parser.add_argument('--cross-validate', action='store_true',
                       help='Run k-fold cross-validation before the final train/test run '
                            '(multiplies training time by --n-folds; off by default)')
    parser.add_argument('--n-folds', type=int, default=5,
                       help='Number of folds for --cross-validate')
    parser.add_argument('--baseline-margin', type=float, default=0.02,
                       help='Minimum AUC-ROC margin the deep model must beat the best '
                            'classical baseline by to be considered justified')
    parser.add_argument('--force-activate', action='store_true',
                       help='Register and activate the model even if it fails the quality '
                            'gate — an explicit human override, logged as such')

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("NeuroPredict-AI Model Training and Validation")
    logger.info("=" * 80)
    logger.info(f"Data file: {args.data}")
    logger.info(f"Epochs: {args.epochs}")
    logger.info(f"Learning rate: {args.lr}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Seed: {args.seed}")
    logger.info("")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    trainer = ModelTrainer(input_dim=50, hidden_dims=[256, 128, 64])

    # --- Optional: k-fold cross-validation, before committing to one split ---
    cv_summary = None
    if args.cross_validate:
        logger.info(f"Running {args.n_folds}-fold cross-validation (seed={args.seed})...")
        cv_summary = trainer.cross_validate(
            data_path=args.data, n_splits=args.n_folds,
            epochs=min(args.epochs, 30), learning_rate=args.lr, random_seed=args.seed,
        )
        logger.info(f"Cross-validation summary: {cv_summary['summary']}")

    # --- Patient-level split (see ModelTrainer.prepare_data) ---
    logger.info("Preparing data...")
    train_loader, val_loader, test_loader = trainer.prepare_data(
        data_path=args.data, test_size=0.2, val_size=0.1, random_seed=args.seed
    )
    logger.info(f"Split method: {trainer.split_method}; class pos_weights: {trainer.pos_weights}")

    # --- Deep model: class-weighted training (see ModelTrainer._weighted_bce) ---
    logger.info("Creating model architecture...")
    trainer.create_model()

    logger.info("Starting training...")
    training_results = trainer.train(
        train_loader=train_loader, val_loader=val_loader,
        epochs=args.epochs, learning_rate=args.lr,
        early_stopping_patience=args.early_stopping, save_best=True, seed=args.seed,
    )
    logger.info("Training completed!")
    logger.info(f"Best validation metrics: {training_results['best_metrics']}")

    # --- Baseline comparison, on the exact same split (see BaselineTrainer) ---
    logger.info("Training classical baselines (Logistic Regression, Random Forest) for comparison...")
    train_features = train_loader.dataset.features.numpy()
    train_alz_labels = train_loader.dataset.labels_alzheimer.numpy().astype(int)
    train_park_labels = train_loader.dataset.labels_parkinson.numpy().astype(int)
    test_features = test_loader.dataset.features.numpy()
    test_alz_labels = test_loader.dataset.labels_alzheimer.numpy().astype(int)
    test_park_labels = test_loader.dataset.labels_parkinson.numpy().astype(int)

    baseline_trainer = BaselineTrainer(random_seed=args.seed)
    baseline_alzheimer = baseline_trainer.fit_and_evaluate(
        train_features, train_alz_labels, test_features, test_alz_labels, disease_name="alzheimer"
    )
    baseline_parkinson = baseline_trainer.fit_and_evaluate(
        train_features, train_park_labels, test_features, test_park_labels, disease_name="parkinson"
    )

    # --- Clinical validation: operating threshold, calibration, subgroup fairness ---
    logger.info("Validating on test set...")
    validator = ClinicalValidator()
    validation_results = validator.validate_model(
        model=trainer.model, test_loader=test_loader, device=trainer.device,
        subgroup_features=trainer.test_subgroups or None,
    )

    # Comparison must use the SAME test-set AUC the deep model was just judged
    # on, or the "justified" verdict is meaningless.
    justification = {
        'alzheimer': BaselineTrainer.deep_model_justified(
            validation_results['alzheimer']['auc_roc'], baseline_alzheimer, margin=args.baseline_margin
        ),
        'parkinson': BaselineTrainer.deep_model_justified(
            validation_results['parkinson']['auc_roc'], baseline_parkinson, margin=args.baseline_margin
        ),
    }

    # Generate reports
    logger.info("Generating validation report...")
    report = validator.generate_validation_report()
    print("\n" + report)
    print("\nBaseline comparison:")
    for disease, verdict in justification.items():
        print(
            f"  {disease}: deep AUC={verdict['deep_auc']:.4f} vs. best baseline "
            f"({verdict['best_baseline']}) AUC={verdict['best_baseline_auc']:.4f} "
            f"-> {'deep model justified' if verdict['deep_model_justified'] else 'BASELINE PREFERRED — deep complexity not earning its keep'}"
        )

    # --- Gated registry activation — NOT automatic; see ModelRegistry ---
    gate_metrics = {
        'alzheimer_auc_roc': validation_results['alzheimer']['auc_roc'],
        'parkinson_auc_roc': validation_results['parkinson']['auc_roc'],
    }
    full_metadata = {
        'training_results': training_results,
        'validation_results': validation_results,
        'cross_validation': cv_summary,
        'baseline_comparison': {'alzheimer': baseline_alzheimer, 'parkinson': baseline_parkinson},
        'baseline_justification': justification,
        'timestamp': timestamp,
        'config': {'epochs': args.epochs, 'learning_rate': args.lr, 'batch_size': args.batch_size},
    }

    model_filename = f"model_{timestamp}.pth"
    trainer.save_model(model_filename, metadata=full_metadata)

    registry = ModelRegistry()
    registration = registry.register_and_maybe_activate(
        model_path=trainer.models_dir / model_filename,
        metrics=full_metadata,
        gate_metrics=gate_metrics,
        version=timestamp,
        description=f"Trained on {args.data}",
        force=args.force_activate,
    )
    logger.info(f"Registry outcome: {registration}")

    # --- Drift reference capture — only for a model that actually went live ---
    if registration['activated']:
        drift_monitor = DriftMonitor()
        drift_monitor.set_reference_distribution(
            model_version=registration['version'],
            features=train_features,
            feature_names=[f"f{i}" for i in range(train_features.shape[1])],
            baseline_metrics={
                'accuracy': (validation_results['alzheimer']['accuracy'] + validation_results['parkinson']['accuracy']) / 2,
            },
        )
        logger.info("Drift reference distribution captured for the newly-activated model.")
    else:
        logger.warning(
            "Model was not activated — no drift reference captured. "
            "See registration['gate']['checks'] above for why."
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
    logger.info(f"Model registered: {registration['registered']}, activated: {registration['activated']}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
