# راهنمای Integration Testing - NeuroPredict-AI

## 📋 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [ساختار تست‌ها](#ساختار-تست‌ها)
3. [اجرای تست‌ها](#اجرای-تست‌ها)
4. [انواع Integration Tests](#انواع-integration-tests)
5. [Mocking External Services](#mocking-external-services)
6. [Best Practices](#best-practices)

---

## مقدمه

Integration Tests برای بررسی صحت کارکرد یکپارچه‌سازی‌های مختلف سیستم با یکدیگر و با سیستم‌های خارجی استفاده می‌شوند.

### Coverage

- ✅ HL7 FHIR Integration
- ✅ PACS/DICOM Integration
- ✅ EHR/HIS Integration
- ✅ HL7 v2 Integration
- ✅ Real-time Streaming
- ✅ Medical Device Integration

---

## ساختار تست‌ها

```
backend/tests/integration/
├── test_api_flow.py              # General API flow tests
├── test_fhir_integration.py      # HL7 FHIR integration tests
├── test_pacs_integration.py      # PACS/DICOM integration tests
├── test_ehr_integration.py       # EHR/HIS integration tests
├── test_hl7v2_integration.py     # HL7 v2 integration tests
├── test_streaming_integration.py # Real-time streaming tests
└── test_device_integration.py    # Medical device integration tests
```

---

## اجرای تست‌ها

### اجرای تمام Integration Tests

```bash
cd backend
pytest tests/integration/ -m integration -v
```

### اجرای تست‌های خاص

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

### اجرا با Coverage

```bash
pytest tests/integration/ -m integration --cov=app.services.integration --cov-report=html
```

---

## انواع Integration Tests

### 1. FHIR Integration Tests

تست‌های یکپارچه‌سازی HL7 FHIR:

- ✅ ایجاد Patient Resource
- ✅ ایجاد Observation Resource
- ✅ ایجاد DiagnosticReport Resource
- ✅ جستجوی Resources
- ✅ CapabilityStatement
- ✅ Resource Validation
- ✅ Bundle Creation

**مثال:**
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_patient_resource(client, auth_headers):
    response = await client.post(
        "/api/v1/fhir/Patient",
        json={"name": "John Doe", ...},
        headers=auth_headers
    )
    assert response.status_code == 200
```

### 2. PACS Integration Tests

تست‌های یکپارچه‌سازی PACS/DICOM:

- ✅ Query Studies
- ✅ Retrieve Study
- ✅ Validate DICOM File
- ✅ Modality Worklist
- ✅ DICOM Metadata Parsing

**مثال:**
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_studies(client, auth_headers):
    response = await client.get(
        "/api/v1/pacs/studies?patient_id=PATIENT123",
        headers=auth_headers
    )
    assert response.status_code == 200
```

### 3. EHR Integration Tests

تست‌های یکپارچه‌سازی EHR/HIS:

- ✅ دریافت اطلاعات بیمار
- ✅ دریافت نتایج آزمایش
- ✅ دریافت داروها
- ✅ دریافت علائم حیاتی
- ✅ همگام‌سازی داده
- ✅ ارسال پیش‌بینی

**مثال:**
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_patient_from_ehr(client, auth_headers):
    with patch.object(EHRService, 'get_patient_data') as mock_get:
        mock_get.return_value = {"patient_id": "123"}
        response = await client.get(
            "/api/v1/ehr/patients/123",
            headers=auth_headers
        )
```

### 4. HL7 v2 Integration Tests

تست‌های یکپارچه‌سازی HL7 v2:

- ✅ ایجاد ADT^A01 Message
- ✅ ایجاد ORU^R01 Message
- ✅ ایجاد Lab Result Message
- ✅ ایجاد Vital Signs Message
- ✅ Parse Message
- ✅ Validate Message

**مثال:**
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_admit_message(client, auth_headers):
    response = await client.post(
        "/api/v1/hl7v2/admit",
        json={...},
        headers=auth_headers
    )
    assert response.status_code == 200
```

### 5. Streaming Integration Tests

تست‌های Real-time Streaming:

- ✅ ایجاد Channel
- ✅ Broadcast Message
- ✅ Connection Management
- ✅ Data Producers
- ✅ Statistics

**مثال:**
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_broadcast_message(client, auth_headers):
    await PredictionStreamProducer.stream_prediction_result(...)
    stats = realtime_service.get_channel_stats(channel_id)
    assert stats["message_count"] > 0
```

### 6. Device Integration Tests

تست‌های Medical Device Integration:

- ✅ Start/Stop Stream
- ✅ Stream Status
- ✅ Callback Registration
- ✅ Device Data Handling

**مثال:**
```python
@pytest.mark.asyncio
@pytest.mark.integration
def test_device_streaming_service():
    device_service = DeviceStreamingService()
    success = asyncio.run(device_service.start_stream(...))
    assert success == True
```

---

## Mocking External Services

برای تست‌هایی که نیاز به external services دارند، از mocking استفاده می‌کنیم:

### Example: Mocking EHR Service

```python
from unittest.mock import patch

@pytest.mark.asyncio
async def test_ehr_integration():
    with patch.object(EHRService, 'get_patient_data') as mock_get:
        mock_get.return_value = {
            "patient_id": "123",
            "name": "John Doe"
        }
        
        # Test code
        result = await ehr_service.get_patient_data("123")
        assert result["patient_id"] == "123"
```

### Example: Mocking HTTP Requests

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_ehr_http_request():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await ehr_service.get_patient_data("123")
```

---

## Best Practices

### 1. Test Isolation

هر تست باید مستقل باشد:

```python
@pytest.fixture
async def clean_channel():
    # Setup
    channel_id = "test:channel"
    yield channel_id
    # Cleanup
    if channel_id in realtime_service.channels:
        del realtime_service.channels[channel_id]
```

### 2. Use Fixtures

از fixtures برای setup استفاده کنید:

```python
@pytest.fixture
async def test_patient(test_db):
    # Create test patient
    ...
    yield patient
    # Cleanup
```

### 3. Mock External Dependencies

برای external services از mocking استفاده کنید:

```python
@patch.object(ExternalService, 'method')
async def test_integration(mock_method):
    mock_method.return_value = expected_result
    # Test code
```

### 4. Test Error Cases

تست‌های error cases را هم بنویسید:

```python
async def test_invalid_fhir_resource(client, auth_headers):
    response = await client.post(
        "/api/v1/fhir/Patient",
        json={"invalid": "data"},
        headers=auth_headers
    )
    assert response.status_code == 400
```

### 5. Async/Await

از async/await برای async operations استفاده کنید:

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result is not None
```

---

## Test Data

### Fixtures

Fixtures در `conftest.py` تعریف شده‌اند:

- `test_db` - Database session
- `test_user` - Test user
- `test_patient` - Test patient
- `client` - HTTP test client
- `auth_headers` - Authentication headers

### Test Data Creation

```python
@pytest.fixture
async def test_patient_data(test_db):
    patient = Patient(
        first_name="Test",
        last_name="Patient",
        ...
    )
    test_db.add(patient)
    await test_db.commit()
    return patient
```

---

## Troubleshooting

### مشکل: External Service Not Available

**راه‌حل:**
- از mocking استفاده کنید
- Skip tests که نیاز به actual service دارند
- از test doubles استفاده کنید

### مشکل: Database Issues

**راه‌حل:**
- مطمئن شوید که test database درست تنظیم شده است
- از transactions برای isolation استفاده کنید
- Cleanup را در fixtures انجام دهید

### مشکل: Async Test Failures

**راه‌حل:**
- از `@pytest.mark.asyncio` استفاده کنید
- مطمئن شوید که `asyncio_mode = auto` در pytest.ini است
- از `await` برای async operations استفاده کنید

---

## Coverage Goals

| Category | Target | Current |
|----------|--------|---------|
| FHIR Integration | > 80% | - |
| PACS Integration | > 70% | - |
| EHR Integration | > 70% | - |
| HL7 v2 Integration | > 80% | - |
| Streaming Integration | > 75% | - |
| Device Integration | > 70% | - |

---

## منابع بیشتر

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

## پشتیبانی

برای سوالات و مشکلات:
- Testing Team: testing@neuropredict-ai.com
- Technical Support: support@neuropredict-ai.com

