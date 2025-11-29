# XAI Service - Patent Claim 3 Implementation

## Overview

This document describes the Explainable AI (XAI) service implementation that directly supports **Patent Claim 3** for dynamic evidence generation in the Data Fusion system.

## Patent Claim 3

**Claim 3: System for generating explanations including:**

(a) Computing model gradients with respect to input  
(b) Using Integrated Gradients for accurate attribution  
(c) Mapping attributions to anatomical brain regions  
(d) Visual display of saliency maps for medical interpretation  

## Implementation

### Service: `DataFusionXAIService`

Located in: `backend/app/services/data_fusion_xai_service.py`

### Key Methods

#### 1. `compute_integrated_gradients()` - Patent Claim 3(b)

**Mathematical Formulation:**
```
IG_i(x) = (x_i - baseline_i) × ∫[α=0 to 1] (∂F(baseline + α(x - baseline))/∂x_i) dα
```

**Properties:**
- ✅ **Sensitivity Axiom**: If input and baseline differ in one feature and prediction differs, that feature gets non-zero attribution
- ✅ **Implementation Invariance**: Attributions are identical for functionally equivalent models

**Usage:**
```python
from app.services.data_fusion_xai_service import get_data_fusion_xai_service

xai_service = get_data_fusion_xai_service(model)
result = xai_service.compute_integrated_gradients(
    input_tensor,
    target_output='integrated_fusion_score',
    steps=50
)
```

#### 2. `compute_gradient_saliency()` - Patent Claim 3(a)

**Mathematical Formulation:**
```
S(x) = |∂y/∂x|
```

**Usage:**
```python
result = xai_service.compute_gradient_saliency(
    input_tensor,
    target_output='integrated_fusion_score'
)
```

#### 3. `map_to_anatomical_regions()` - Patent Claim 3(c)

Maps feature attributions to anatomical brain regions:
- Hippocampus
- Cerebral Cortex
- Ventricular System
- White Matter
- Whole Brain

**Usage:**
```python
attributions = result['attribution']
regions = xai_service.map_to_anatomical_regions(attributions)
```

#### 4. `generate_dynamic_evidence()` - Complete Patent Claim 3

Generates comprehensive dynamic evidence including:
- Feature-level attributions
- Anatomical region mapping
- Modality-specific contributions
- Cognitive domain contributions
- Biomarker category contributions
- Clinical interpretation evidence
- Visual saliency map data

**Usage:**
```python
evidence = xai_service.generate_dynamic_evidence(
    medical_record=medical_record,
    patient=patient,
    fusion_scores=fusion_scores,
    method='integrated_gradients'
)
```

## API Endpoints

### 1. Explain Fusion Report

**Endpoint:** `POST /api/v1/data-fusion/{report_id}/explain`

**Parameters:**
- `report_id`: ID of the fusion report
- `method`: XAI method ('integrated_gradients' or 'gradient_saliency')

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "patient_id": 1,
  "medical_record_id": 1,
  "fusion_scores": {...},
  "explanations": {
    "integrated_fusion": {
      "attribution": [...],
      "feature_importance": {...},
      "method": "integrated_gradients"
    }
  },
  "anatomical_regions": {
    "Hippocampus": {
      "total_attribution": 0.45,
      "normalized_attribution": 0.32,
      "features": [...]
    }
  },
  "modality_contributions": {
    "cognitive": 0.35,
    "biomarker": 0.28,
    "imaging": 0.30,
    "demographic": 0.07
  },
  "clinical_evidence": {...},
  "patent_claim_3_support": true
}
```

### 2. Get Saliency Map

**Endpoint:** `GET /api/v1/data-fusion/{report_id}/saliency-map`

**Parameters:**
- `report_id`: ID of the fusion report
- `target_output`: Which output to explain (default: 'integrated_fusion_score')
- `method`: XAI method (default: 'integrated_gradients')

**Response:**
```json
{
  "report_id": 1,
  "target_output": "integrated_fusion_score",
  "method": "integrated_gradients",
  "saliency_data": {
    "feature_attributions": {...},
    "anatomical_regions": {...},
    "modality_heatmap": {...},
    "normalized_attributions": [...]
  },
  "anatomical_regions": {...},
  "patent_claim_3_support": true
}
```

## Integration with Data Fusion Service

The XAI service is automatically integrated into the Data Fusion report generation:

1. When a fusion report is generated with a Deep Learning model
2. Dynamic evidence is automatically computed
3. Evidence is stored in the `xai_evidence` field of `DataFusionReport`
4. The `has_xai_explanation` flag indicates availability

## Feature Mapping

### 20 Input Features

1. **Cognitive (5)**: MMSE, MoCA, Memory, Attention, Executive Function
2. **Biomarkers (4)**: Amyloid-beta, Tau, Dopamine, APOE ε4
3. **Imaging (5)**: Hippocampal volume, Cortical thickness, Ventricular volume, WMH, Total brain volume
4. **Demographics (3)**: Age, Gender, Education
5. **Additional (3)**: Completeness indicators

### Anatomical Region Mapping

- `hippocampal_volume` → Hippocampus
- `cortical_thickness` → Cerebral Cortex
- `ventricular_volume` → Ventricular System
- `white_matter_hyperintensities` → White Matter
- `brain_volume_total` → Whole Brain

## Clinical Interpretation

The XAI service provides:

1. **Primary Modality**: Which modality (cognitive/biomarker/imaging) contributes most
2. **Key Findings**: Top 5 contributing features with interpretations
3. **Supporting Features**: Features that positively support the assessment
4. **Confidence Factors**: Factors affecting confidence in the assessment

## Testing

Run XAI tests:
```bash
cd backend
pytest tests/test_data_fusion_xai.py -v
```

Test coverage includes:
- ✅ Integrated Gradients computation
- ✅ Gradient saliency computation
- ✅ Anatomical region mapping
- ✅ Dynamic evidence generation
- ✅ Patent Claim 3 support verification
- ✅ API endpoint integration

## Performance Considerations

- **Integrated Gradients**: Requires 50 forward/backward passes (configurable)
- **Gradient Saliency**: Single forward/backward pass (faster)
- **Caching**: Consider caching attributions for repeated queries
- **Batch Processing**: Can process multiple reports in batch

## Future Enhancements

1. **SHAP Values**: Add SHAP (SHapley Additive exPlanations) support
2. **Attention Visualization**: For transformer-based models
3. **Counterfactual Explanations**: "What if" scenarios
4. **Feature Interaction Analysis**: Multi-feature interactions
5. **Temporal Attribution**: For longitudinal data

## References

- Sundararajan, M., Taly, A., & Yan, Q. (2017). Axiomatic attribution for deep networks. ICML.
- Simonyan, K., et al. (2013). Deep inside convolutional networks: Visualising image classification models. arXiv.
- Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. NIPS.

## Patent Claim 3 Compliance Checklist

- [x] (a) Computing model gradients with respect to input
- [x] (b) Using Integrated Gradients for accurate attribution
- [x] (c) Mapping attributions to anatomical brain regions
- [x] (d) Visual display data for saliency maps
- [x] Dynamic evidence generation
- [x] API endpoints for explanations
- [x] Integration with Data Fusion Service
- [x] Comprehensive test coverage

