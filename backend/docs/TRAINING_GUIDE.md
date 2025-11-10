# Training Guide - NeuroPredict-AI

## Overview

This guide explains how to train the AI models for NeuroPredict-AI using real data with clinical validation.

## Prerequisites

1. **Data Preparation**: Ensure you have training data in CSV format with the following columns:
   - Demographics: `age`, `gender`, `education_years`
   - Cognitive Scores: `mmse_score`, `moca_score`, `memory_score`, `attention_score`, `executive_function_score`
   - Biomarkers: `amyloid_beta`, `tau_protein`, `dopamine_level`
   - Genetic: `apoe_e4_status`
   - MRI Features: `hippocampal_volume`, `cortical_thickness`, `ventricular_volume`, `white_matter_hyperintensities`, `brain_volume_total`
   - Labels: `diagnosis` (Normal, Alzheimer, Parkinson)

2. **Environment Setup**: Install required dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Directory Structure**: Ensure the following directories exist:
   - `data/data/csv/` - For CSV data files
   - `models/` - For saved models
   - `logs/` - For training logs

## Training Pipeline

### 1. Basic Training

Train a model with default settings:

```bash
cd backend
python scripts/train_model.py
```

This will:
- Load data from `data/data/csv/sample_dataset_complete.csv`
- Split data into train (70%), validation (15%), and test (15%) sets
- Train the model for up to 100 epochs with early stopping
- Save the best model to `models/`
- Generate clinical validation metrics
- Register the model in the model registry

### 2. Custom Training

Train with custom parameters:

```bash
python scripts/train_model.py \
    --csv-file path/to/your/data.csv \
    --epochs 200 \
    --batch-size 64 \
    --learning-rate 0.0001 \
    --patience 20 \
    --train-ratio 0.8 \
    --val-ratio 0.1 \
    --test-ratio 0.1 \
    --set-active
```

### 3. Training Arguments

- `--data-dir`: Directory containing CSV data files
- `--csv-file`: Path to specific CSV file
- `--epochs`: Number of training epochs (default: 100)
- `--batch-size`: Batch size for training (default: 32)
- `--learning-rate`: Learning rate (default: 0.001)
- `--weight-decay`: Weight decay for regularization (default: 1e-5)
- `--patience`: Early stopping patience (default: 10)
- `--train-ratio`: Training set ratio (default: 0.7)
- `--val-ratio`: Validation set ratio (default: 0.15)
- `--test-ratio`: Test set ratio (default: 0.15)
- `--model-dir`: Directory to save models (default: models/)
- `--version`: Model version (auto-generated if not provided)
- `--description`: Model description
- `--set-active`: Set this model as active after training

## Model Evaluation

### Evaluate a Trained Model

```bash
python scripts/evaluate_model.py \
    --model-version <version> \
    --csv-file path/to/test/data.csv \
    --threshold 0.5
```

### Evaluation Arguments

- `--model-path`: Path to model file
- `--model-version`: Model version from registry
- `--data-dir`: Directory containing CSV data files
- `--csv-file`: Path to CSV file with test data
- `--batch-size`: Batch size for evaluation (default: 32)
- `--threshold`: Classification threshold (default: 0.5)
- `--output-dir`: Directory to save evaluation results

## Clinical Validation Metrics

The training pipeline calculates comprehensive clinical validation metrics:

### For Each Disease (Alzheimer's and Parkinson's):

1. **Accuracy**: Overall classification accuracy
2. **Sensitivity (Recall)**: True Positive Rate - ability to identify positive cases
3. **Specificity**: True Negative Rate - ability to identify negative cases
4. **Precision (PPV)**: Positive Predictive Value - proportion of positive predictions that are correct
5. **Negative Predictive Value (NPV)**: Proportion of negative predictions that are correct
6. **F1-Score**: Harmonic mean of precision and recall
7. **AUC-ROC**: Area Under the Receiver Operating Characteristic Curve
8. **Optimal Threshold**: Best threshold based on Youden's J statistic
9. **Confusion Matrix**: Detailed breakdown of predictions

## Model Registry

The model registry tracks all trained models with their versions, metrics, and metadata.

### View Registered Models

```python
from app.services.training import ModelRegistry
from app.core.config import settings
from pathlib import Path

registry = ModelRegistry(Path(settings.MODEL_REGISTRY_PATH))
models = registry.list_models()

for model in models:
    print(f"Version: {model['version']}")
    print(f"Created: {model['created_at']}")
    print(f"Active: {model['is_active']}")
    print(f"Metrics: {model['metrics']}")
```

### Set Active Model

```python
registry.set_active_model('20240101_120000')
```

## Using Trained Models

Once a model is trained and registered, the AI model service will automatically load it:

1. **Automatic Loading**: If `USE_TRAINED_MODEL=True` in config, the service will:
   - First try to load the active model from registry
   - Fall back to the latest model if no active model
   - Fall back to default model path
   - Use random initialization if no model found

2. **Manual Loading**: You can specify which model to use by setting it as active in the registry.

## Data Format

### Required CSV Columns

The training data CSV should contain the following columns:

- `patient_id`: Patient identifier
- `age`: Age in years
- `gender`: Gender (Male/Female/male/female/M/F/m/f)
- `education_years`: Years of education
- `mmse_score`: MMSE score (0-30)
- `moca_score`: MoCA score (0-30)
- `memory_score`: Memory score (0-100)
- `attention_score`: Attention score (0-100)
- `executive_function_score`: Executive function score (0-100)
- `amyloid_beta`: Amyloid beta level
- `tau_protein`: Tau protein level
- `dopamine_level`: Dopamine level
- `apoe_e4_status`: APOE ε4 status (0 or 1)
- `hippocampal_volume`: Hippocampal volume
- `cortical_thickness`: Cortical thickness
- `ventricular_volume`: Ventricular volume
- `white_matter_hyperintensities`: White matter hyperintensities
- `brain_volume_total`: Total brain volume
- `diagnosis`: Diagnosis label (Normal/Alzheimer/Parkinson)

### Optional Columns

- `visit_date`: Visit date (for temporal analysis)
- `imaging_features`: Pre-extracted imaging features (if available)

## Best Practices

1. **Data Quality**: Ensure data is clean, complete, and properly labeled
2. **Data Split**: Use stratified splitting to maintain class distribution
3. **Cross-Validation**: Consider k-fold cross-validation for small datasets
4. **Hyperparameter Tuning**: Experiment with different learning rates, batch sizes, and architectures
5. **Early Stopping**: Use early stopping to prevent overfitting
6. **Model Versioning**: Always register models with descriptive versions and descriptions
7. **Clinical Validation**: Validate models on independent test sets before deployment
8. **Monitoring**: Monitor model performance over time and retrain as needed

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**: Reduce batch size or use CPU
2. **Data Not Found**: Check CSV file path and data directory
3. **Model Not Loading**: Verify model path and registry entries
4. **Poor Performance**: Check data quality, try different hyperparameters, or collect more data

### Logs

Training logs are saved to:
- `logs/training.log` - Training progress
- `logs/evaluation.log` - Evaluation results
- `models/training_metrics_*.json` - Training metrics
- `models/clinical_report_*.txt` - Clinical validation reports

## Next Steps

1. **Collect Real Data**: Gather real medical data with proper consent and ethical approval
2. **Data Augmentation**: Consider data augmentation techniques for small datasets
3. **Feature Engineering**: Extract more meaningful features from raw data
4. **Model Architecture**: Experiment with different architectures (CNN, RNN, Transformer)
5. **Ensemble Methods**: Combine multiple models for better performance
6. **Clinical Validation**: Conduct clinical validation studies with medical partners
7. **Regulatory Approval**: Obtain necessary regulatory approvals (FDA 510(k), CE marking)

## References

- [PyTorch Documentation](https://pytorch.org/docs/)
- [scikit-learn Documentation](https://scikit-learn.org/stable/)
- [Clinical Validation Guidelines](https://www.fda.gov/medical-devices)

