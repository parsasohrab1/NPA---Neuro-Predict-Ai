# Integration Tests - NeuroPredict-AI

## Overview

Integration tests verify that different components of the system work together correctly, including external integrations.

## Test Structure

```
tests/integration/
├── test_api_flow.py              # General API flow tests
├── test_fhir_integration.py      # HL7 FHIR integration tests
├── test_pacs_integration.py      # PACS/DICOM integration tests
├── test_ehr_integration.py       # EHR/HIS integration tests
├── test_hl7v2_integration.py     # HL7 v2 integration tests
├── test_streaming_integration.py # Real-time streaming tests
└── test_device_integration.py    # Medical device integration tests
```

## Running Tests

### Run All Integration Tests

```bash
pytest tests/integration/ -m integration -v
```

### Run Specific Integration Tests

```bash
# FHIR tests
pytest tests/integration/test_fhir_integration.py -m fhir -v

# PACS tests
pytest tests/integration/test_pacs_integration.py -m pacs -v

# EHR tests
pytest tests/integration/test_ehr_integration.py -m ehr -v

# HL7 v2 tests
pytest tests/integration/test_hl7v2_integration.py -m hl7v2 -v

# Streaming tests
pytest tests/integration/test_streaming_integration.py -m streaming -v

# Device tests
pytest tests/integration/test_device_integration.py -m devices -v
```

## Test Categories

### FHIR Integration Tests

Tests for HL7 FHIR API endpoints:
- Patient resource creation
- Observation resource creation
- DiagnosticReport resource creation
- Resource search
- CapabilityStatement

### PACS Integration Tests

Tests for PACS/DICOM integration:
- Query studies
- Retrieve studies
- DICOM file validation
- Modality Worklist
- Metadata parsing

### EHR Integration Tests

Tests for EHR/HIS integration:
- Get patient data
- Get lab results
- Get medications
- Get vital signs
- Sync patient data
- Send predictions

### HL7 v2 Integration Tests

Tests for HL7 v2 message handling:
- ADT^A01 (Admit Patient) messages
- ORU^R01 (Observation Result) messages
- Lab result messages
- Vital signs messages
- Message parsing
- Message validation

### Streaming Integration Tests

Tests for real-time streaming:
- Channel creation
- Message broadcasting
- Connection management
- Data producers
- Statistics

### Device Integration Tests

Tests for medical device integration:
- Start/stop device streams
- Stream status
- Callback registration
- Device data handling

## Mocking External Services

For integration tests that require external services (EHR, PACS, etc.), we use mocking:

```python
from unittest.mock import patch

@patch.object(EHRService, 'get_patient_data')
async def test_get_patient(mock_get):
    mock_get.return_value = {"patient_id": "123"}
    # Test code
```

## Test Data

Test data is created using fixtures defined in `conftest.py`:
- `test_user` - Test user with doctor role
- `test_patient` - Test patient record
- `test_db` - Database session
- `client` - Test HTTP client
- `auth_headers` - Authentication headers

## Notes

- Integration tests may require external services to be configured
- Some tests use mocking to avoid requiring actual external services
- Tests are marked with appropriate markers for filtering
- All tests use async/await for async operations

## Troubleshooting

### Tests Failing Due to Missing Services

If tests fail because external services are not available:
1. Check if service URLs are configured in test environment
2. Use mocking for external services
3. Skip tests that require actual external services

### Database Issues

If tests fail due to database issues:
1. Ensure test database is properly configured
2. Check database migrations are up to date
3. Verify test fixtures are creating data correctly

