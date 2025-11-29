# Data Fusion Service Tests

## Overview

This directory contains comprehensive Unit and Integration tests for the Data Fusion Service, covering both manual calculations and Deep Learning model integration.

## Test Files

### 1. `test_data_fusion_service.py`
**Unit and Integration tests for DataFusionService**

#### Test Coverage:

**Unit Tests:**
- ✅ Cognitive Modality Assessment (5 tests)
  - Complete data
  - Partial data
  - Empty data
  - Single field
  - Extreme values

- ✅ Biomarker Modality Assessment (4 tests)
  - Complete data
  - Alzheimer risk indicators
  - Parkinson risk indicators
  - Normal biomarkers

- ✅ Imaging Modality Assessment (3 tests)
  - Complete data
  - Brain atrophy indicators
  - Normal imaging

- ✅ Cross-Modal Correlations (5 tests)
  - Complete correlations
  - Missing data handling
  - High consistency
  - Low consistency
  - Conflicting modalities

- ✅ Integrated Fusion Score (5 tests)
  - Weighted fusion calculation
  - Unequal confidences
  - No data handling
  - Confidence determination
  - Low consistency impact

- ✅ Disease-Specific Analysis (4 tests)
  - Alzheimer fusion analysis
  - High Alzheimer risk
  - Parkinson fusion analysis
  - High Parkinson risk

- ✅ Feature Extraction (3 tests)
  - Complete feature extraction
  - Missing data handling
  - Feature normalization

- ✅ Data Quality Assessment (4 tests)
  - Completeness assessment
  - Outlier detection
  - Normal values
  - Abnormal values

- ✅ Interpretation Generation (3 tests)
  - Normal interpretation
  - High risk interpretation
  - Conflicting modalities

- ✅ Edge Cases (4 tests)
  - All None values
  - Extreme high values
  - Extreme low values
  - Concurrent generation

**Integration Tests:**
- ✅ Full Report Generation (5 tests)
  - Complete data report
  - Minimal data report
  - Error handling
  - Deep Learning model integration
  - Fallback to manual calculations

### 2. `test_data_fusion_api.py`
**Integration tests for Data Fusion API endpoints**

#### Test Coverage:

**API Endpoint Tests:**
- ✅ Generate Fusion Report (5 tests)
  - POST /api/v1/data-fusion/generate
  - Without medical_record_id (uses latest)
  - Error handling (patient not found)
  - Error handling (record not found)
  - Algorithm version reporting

- ✅ Get Patient Reports (2 tests)
  - GET /api/v1/data-fusion/patient/{patient_id}
  - Empty results handling

- ✅ Get Report by ID (2 tests)
  - GET /api/v1/data-fusion/{report_id}
  - Error handling (not found)

- ✅ Algorithm Version Tests (2 tests)
  - Deep Learning version (2.0.0-DL)
  - Manual version (1.0.0)

**Performance Tests:**
- ✅ Report Generation Performance
  - Response time validation
  - Processing time validation

**Validation Tests:**
- ✅ Input Validation (3 tests)
  - Missing required fields
  - Wrong data types
  - Empty payload

## Running Tests

### Run All Data Fusion Tests
```bash
cd backend
pytest tests/test_data_fusion_service.py tests/test_data_fusion_api.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_data_fusion_service.py::TestCognitiveModalityAssessment -v
```

### Run with Coverage
```bash
pytest tests/test_data_fusion_service.py tests/test_data_fusion_api.py --cov=app.services.data_fusion_service --cov-report=html
```

### Run Only Unit Tests
```bash
pytest tests/test_data_fusion_service.py -k "TestCognitiveModalityAssessment or TestBiomarkerModalityAssessment" -v
```

### Run Only Integration Tests
```bash
pytest tests/test_data_fusion_service.py::TestGenerateFusionReport -v
pytest tests/test_data_fusion_api.py -v
```

## Test Coverage Goals

- **Unit Tests**: >90% coverage for all static methods
- **Integration Tests**: 100% coverage for main workflows
- **API Tests**: 100% coverage for all endpoints
- **Edge Cases**: All identified edge cases covered

## Test Fixtures

### Available Fixtures:
- `sample_patient_complete`: Complete patient with all fields
- `sample_medical_record_complete`: Complete medical record
- `sample_medical_record_minimal`: Minimal medical record
- `mock_dl_model_service`: Mock Deep Learning model service
- `test_session`: Database session for integration tests
- `test_client`: HTTP client for API tests

## Mocking Strategy

### Deep Learning Model Service
The tests use mocks to test both scenarios:
1. **Model Available**: Tests with `is_loaded() = True`
2. **Model Not Available**: Tests with `is_loaded() = False` (fallback)

### Example Mock Usage:
```python
mock_service = Mock(spec=DataFusionModelService)
mock_service.is_loaded.return_value = True
mock_service.predict_scores.return_value = {...}
```

## Test Data

### Complete Test Record:
- **Cognitive**: MMSE=24, MoCA=23, Memory=65, Attention=70, Executive=68
- **Biomarkers**: Amyloid=450, Tau=350, Dopamine=75, APOE ε4=True
- **Imaging**: Hippocampal=2800, Cortical=2.2, Ventricular=45000, WMH=8, Total=1080000

### Minimal Test Record:
- **Cognitive**: MMSE=28 only
- **Biomarkers**: Amyloid=600 only

## Expected Test Results

All tests should pass with:
- ✅ No errors
- ✅ No warnings (unless expected)
- ✅ Coverage >90% for service layer
- ✅ All edge cases handled

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Fast execution (< 30 seconds total)
- No external dependencies (mocked)
- Deterministic results (seeded random)
- Isolated test database

## Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Errors**: Tests use in-memory SQLite, no setup needed

3. **Mock Errors**: Ensure mocks match the actual service interface

4. **Async Errors**: Ensure `pytest-asyncio` is installed and configured

## Adding New Tests

When adding new functionality:

1. **Add Unit Tests** for new static methods
2. **Add Integration Tests** for new workflows
3. **Add API Tests** for new endpoints
4. **Update this README** with new test coverage

## Test Maintenance

- Run tests before committing changes
- Update tests when service logic changes
- Keep test data realistic but minimal
- Document any test-specific assumptions

