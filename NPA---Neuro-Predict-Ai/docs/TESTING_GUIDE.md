# راهنمای کامل تست‌های نرم‌افزاری - NeuroPredict-AI

## 📋 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [ساختار تست‌ها](#ساختار-تست‌ها)
3. [اجرای تست‌ها](#اجرای-تست‌ها)
4. [انواع تست‌ها](#انواع-تست‌ها)
5. [Coverage و معیارها](#coverage-و-معیارها)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## مقدمه

این راهنما نحوه اجرا و نگهداری تست‌های نرم‌افزاری پروژه NeuroPredict-AI را شرح می‌دهد.

### اهداف تست

- ✅ **Unit Test Coverage**: > 80%
- ✅ **Integration Test Coverage**: > 70%
- ✅ **E2E Test Coverage**: > 60%
- ✅ **Zero Critical Bugs** در Production
- ✅ **Performance Targets**: Latency < 200ms, Prediction < 3s

---

## ساختار تست‌ها

```
backend/tests/
├── conftest.py                    # Fixtures و Configuration
├── unit/                          # Unit Tests
│   ├── test_core_security.py     # Security functions
│   ├── services/
│   │   └── test_ai_model_service.py
│   └── api/
│       ├── test_auth_api.py
│       └── test_predictions_api.py
├── integration/                   # Integration Tests
│   └── test_api_flow.py
├── e2e/                           # End-to-End Tests
│   └── test_complete_workflows.py
├── performance/                   # Performance Tests
│   └── test_api_performance.py
└── security/                      # Security Tests
    └── test_security.py
```

---

## اجرای تست‌ها

### نصب Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### اجرای تمام تست‌ها

```bash
# Linux/Mac
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh

# Windows
.\scripts\run_tests.ps1

# یا مستقیماً
pytest
```

### اجرای تست‌های خاص

```bash
# فقط Unit Tests
pytest tests/unit/ -m unit

# فقط Integration Tests
pytest tests/integration/ -m integration

# فقط E2E Tests
pytest tests/e2e/ -m e2e

# فقط Performance Tests
pytest tests/performance/ -m performance

# فقط Security Tests
pytest tests/security/ -m security
```

### اجرا با Coverage

```bash
# با گزارش HTML
pytest --cov=app --cov-report=html

# با گزارش terminal
pytest --cov=app --cov-report=term-missing

# با حداقل coverage
pytest --cov=app --cov-fail-under=80
```

### اجرای تست خاص

```bash
# یک فایل
pytest tests/unit/api/test_auth_api.py

# یک کلاس
pytest tests/unit/api/test_auth_api.py::TestLogin

# یک تست
pytest tests/unit/api/test_auth_api.py::TestLogin::test_login_success
```

---

## انواع تست‌ها

### 1. Unit Tests

تست‌های واحد برای توابع و کلاس‌های منفرد

**مثال:**
```python
def test_password_hashing():
    password = "test123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)
```

**اجرا:**
```bash
pytest tests/unit/ -m unit -v
```

### 2. Integration Tests

تست‌های یکپارچگی برای جریان‌های کامل

**مثال:**
```python
async def test_complete_prediction_flow():
    # Login -> Create Patient -> Create Prediction
    ...
```

**اجرا:**
```bash
pytest tests/integration/ -m integration -v
```

### 3. Integration Tests

تست‌های یکپارچه‌سازی برای بررسی کارکرد سیستم‌ها با یکدیگر

**انواع:**
- FHIR Integration Tests
- PACS Integration Tests
- EHR Integration Tests
- HL7 v2 Integration Tests
- Streaming Integration Tests
- Device Integration Tests

**اجرا:**
```bash
pytest tests/integration/ -m integration -v

# Specific integration tests
pytest tests/integration/test_fhir_integration.py -m fhir -v
pytest tests/integration/test_pacs_integration.py -m pacs -v
```

📚 **[Integration Testing Guide](INTEGRATION_TESTING.md)**

### 4. E2E Tests

تست‌های End-to-End برای workflow های کامل کاربر

**مثال:**
```python
async def test_complete_doctor_workflow():
    # Login -> Dashboard -> Patient -> Prediction -> Review
    ...
```

**اجرا:**
```bash
pytest tests/e2e/ -m e2e -v
```

### 5. Performance Tests

تست‌های عملکرد برای بررسی Latency و Throughput

**مثال:**
```python
async def test_prediction_latency():
    # باید در کمتر از 3 ثانیه انجام شود
    ...
```

**اجرا:**
```bash
pytest tests/performance/ -m performance -v
```

### 6. Security Tests

تست‌های امنیتی برای بررسی آسیب‌پذیری‌ها

**مثال:**
```python
async def test_sql_injection():
    # تست SQL injection
    ...
```

**اجرا:**
```bash
pytest tests/security/ -m security -v
```

---

## Coverage و معیارها

### بررسی Coverage

```bash
# گزارش HTML
pytest --cov=app --cov-report=html
open htmlcov/index.html

# گزارش Terminal
pytest --cov=app --cov-report=term-missing
```

### معیارهای Coverage

| نوع تست | هدف | حداقل |
|---------|-----|-------|
| Unit Tests | > 80% | > 75% |
| Integration Tests | > 70% | > 65% |
| Overall | > 75% | > 70% |

### Coverage برای فایل‌های خاص

```bash
# فقط API endpoints
pytest --cov=app.api --cov-report=html

# فقط Services
pytest --cov=app.services --cov-report=html
```

---

## Best Practices

### 1. Isolation

هر تست باید مستقل باشد و به تست‌های دیگر وابسته نباشد:

```python
@pytest.fixture
async def test_user(test_db):
    # هر تست یک user جدید می‌گیرد
    ...
```

### 2. Cleanup

استفاده از fixtures برای cleanup خودکار:

```python
@pytest.fixture
async def test_db():
    # Setup
    ...
    yield session
    # Cleanup (automatic)
    ...
```

### 3. Naming

نام‌گذاری واضح و توصیفی:

```python
def test_login_with_invalid_credentials():
    # نام تست باید واضح باشد
    ...
```

### 4. Assertions

استفاده از assertions معنادار:

```python
# خوب
assert response.status_code == 200
assert "access_token" in response.json()

# بد
assert response  # خیلی کلی
```

### 5. Mocking

Mock کردن external dependencies:

```python
@pytest.fixture
def mock_external_api(monkeypatch):
    def mock_request(*args, **kwargs):
        return {"status": "ok"}
    monkeypatch.setattr("httpx.get", mock_request)
```

---

## Fixtures

### test_db
Database session برای تست‌ها (in-memory SQLite)

```python
async def test_something(test_db):
    # استفاده از test_db
    ...
```

### test_user
کاربر تست با نقش Doctor

```python
async def test_with_user(test_user):
    assert test_user.role == UserRole.DOCTOR
```

### auth_headers
Headers احراز هویت

```python
async def test_protected_endpoint(client, auth_headers):
    response = await client.get("/api/v1/patients", headers=auth_headers)
    assert response.status_code == 200
```

### test_patient, test_medical_record, test_prediction
داده‌های تست آماده

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ --cov=backend/app --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## Troubleshooting

### مشکل: Database connection errors

**راه‌حل:**
```python
# مطمئن شوید که test database در conftest.py درست تنظیم شده است
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

### مشکل: Async test failures

**راه‌حل:**
```python
# از @pytest.mark.asyncio استفاده کنید
@pytest.mark.asyncio
async def test_async_function():
    ...
```

### مشکل: Import errors

**راه‌حل:**
```bash
# مطمئن شوید که در پوشه backend هستید
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)
pytest
```

### مشکل: Coverage کم

**راه‌حل:**
1. بررسی کنید که تمام branches تست شده‌اند
2. از `--cov-branch` استفاده کنید
3. فایل‌های غیرضروری را از coverage حذف کنید

---

## مثال‌های کامل

### مثال 1: Unit Test

```python
def test_password_hashing():
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)
```

### مثال 2: Integration Test

```python
@pytest.mark.asyncio
async def test_complete_prediction_flow(client, test_user, test_db):
    # Login
    login = await client.post("/api/v1/auth/login", ...)
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Patient
    patient = await client.post("/api/v1/patients", ..., headers=headers)
    patient_id = patient.json()["id"]
    
    # Create Prediction
    prediction = await client.post(
        "/api/v1/predictions",
        json={"patient_id": patient_id, ...},
        headers=headers
    )
    assert prediction.status_code == 201
```

### مثال 3: Performance Test

```python
@pytest.mark.asyncio
async def test_prediction_latency(client, auth_headers, test_patient):
    times = []
    for _ in range(10):
        start = time.time()
        response = await client.post("/api/v1/predictions", ...)
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    assert avg_time < 3.0  # Target: < 3 seconds
```

---

## منابع بیشتر

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

## پشتیبانی

برای سوالات و مشکلات:
- Issues: GitHub Issues
- Documentation: `docs/TESTING_ROADMAP.md`
- Email: support@neuropredict-ai.com

