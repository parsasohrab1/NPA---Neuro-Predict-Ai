# Data Fusion Deep Learning Model

## Overview

The Data Fusion Service now uses a Deep Learning model to predict fusion scores instead of manual calculations. The model is trained on existing medical records to learn the scoring patterns.

## Architecture

### Model: `DataFusionScoringModel`

A multi-output neural network that predicts:
- **Modality Scores**: cognitive_score, biomarker_score, imaging_score (0-100)
- **Confidences**: cognitive_confidence, biomarker_confidence, imaging_confidence (0-1)
- **Correlations**: cognitive_biomarker, cognitive_imaging, biomarker_imaging (0-1)
- **Integrated Scores**: integrated_fusion_score, alzheimer_fusion_score, parkinson_fusion_score (0-100)
- **Disease-Specific Metrics**: Various concordance and alignment scores

### Input Features (20 features)

1. **Cognitive (5)**: MMSE, MoCA, Memory, Attention, Executive Function
2. **Biomarkers (4)**: Amyloid-beta, Tau, Dopamine, APOE ε4
3. **Imaging (5)**: Hippocampal volume, Cortical thickness, Ventricular volume, WMH, Total brain volume
4. **Demographics (3)**: Age, Gender, Education years
5. **Additional (3)**: Derived features

## Training

### Step 1: Generate Training Data

The training script automatically:
1. Loads medical records from the database
2. Uses current `DataFusionService` methods to generate ground truth scores
3. Extracts features from each record
4. Creates training/validation/test splits

### Step 2: Train the Model

```bash
cd backend
python scripts/train_data_fusion_model.py \
    --limit 1000 \
    --epochs 100 \
    --batch-size 32 \
    --learning-rate 0.001 \
    --model-dir backend/models
```

### Parameters

- `--limit`: Maximum number of records to use (None = all)
- `--epochs`: Number of training epochs (default: 100)
- `--batch-size`: Batch size (default: 32)
- `--learning-rate`: Learning rate (default: 0.001)
- `--model-dir`: Directory to save models (default: backend/models)

### Step 3: Model Files

After training, the following files are created:
- `data_fusion_model_YYYYMMDD_HHMMSS.pth`: Trained model weights
- `data_fusion_scaler.pkl`: Feature scaler for normalization

## Usage

### Automatic Loading

The `DataFusionModelService` automatically:
1. Searches for trained models in `backend/models/`
2. Loads the latest model
3. Falls back to manual calculations if no model is found

### Manual Usage

```python
from app.services.data_fusion_model_service import get_data_fusion_model_service

service = get_data_fusion_model_service()
if service.is_loaded():
    features = extract_features(medical_record, patient)
    predictions = service.predict_scores(features)
```

## Integration

The `DataFusionService.generate_fusion_report()` method:
1. Checks if a trained model is available
2. Uses the model if available (algorithm_version: "2.0.0-DL")
3. Falls back to manual calculations if not (algorithm_version: "1.0.0")

## Model Performance

The model should achieve:
- **MSE Loss**: < 0.01 on validation set
- **Score Accuracy**: ±5 points from ground truth
- **Correlation Accuracy**: ±0.1 from ground truth

## Retraining

Retrain the model when:
- New data patterns emerge
- Scoring logic changes significantly
- Model performance degrades
- New features are added

## Notes

- The model uses the same feature extraction as training
- All features are normalized using StandardScaler
- Missing features are set to 0.0 (normalized)
- The model supports batch inference for efficiency

