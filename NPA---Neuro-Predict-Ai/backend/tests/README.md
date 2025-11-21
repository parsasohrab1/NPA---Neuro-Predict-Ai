# Testing Guide - NeuroPredict-AI

## ساختار تست‌ها

```
tests/
├── conftest.py              # Pytest fixtures و configuration
├── unit/                    # Unit Tests
│   ├── test_core_security.py
│   ├── services/
│   │   └── test_ai_model_service.py
│   └── api/
│       ├── test_auth_api.py
│       └── test_predictions_api.py
├── integration/            # Integration Tests
│   └── test_api_flow.py
├── performance/            # Performance Tests
│   └── test_api_performance.py
└── security/               # Security Tests
    └── test_security.py
```

## اجرای تست‌ها

### اجرای تمام تست‌ها
```bash
cd backend
pytest
```

### اجرای تست‌های خاص
```bash
# فقط Unit Tests
pytest tests/unit/ -m unit

# فقط Integration Tests
pytest tests/integration/ -m integration

# فقط Performance Tests
pytest tests/performance/ -m performance

# فقط Security Tests
pytest tests/security/ -m security
```

### اجرا با Coverage
```bash
pytest --cov=app --cov-report=html
```

### اجرای تست خاص
```bash
pytest tests/unit/api/test_auth_api.py::TestLogin::test_login_success
```

## Coverage Goals

- **Unit Tests**: > 80%
- **Integration Tests**: > 70%
- **Overall**: > 75%

## انواع تست‌ها

### 1. Unit Tests
تست‌های واحد برای توابع و کلاس‌های منفرد

**مثال:**
```python
def test_password_hashing():
    password = "test123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
```

### 2. Integration Tests
تست‌های یکپارچگی برای جریان‌های کامل

**مثال:**
```python
async def test_complete_prediction_flow():
    # Login -> Create Patient -> Create Prediction
    ...
```

### 3. Performance Tests
تست‌های عملکرد برای بررسی Latency و Throughput

**مثال:**
```python
async def test_prediction_latency():
    # باید در کمتر از 3 ثانیه انجام شود
    ...
```

### 4. Security Tests
تست‌های امنیتی برای بررسی آسیب‌پذیری‌ها

**مثال:**
```python
async def test_sql_injection():
    # تست SQL injection
    ...
```

## Fixtures

### test_db
Database session برای تست‌ها (in-memory SQLite)

### test_user
کاربر تست با نقش Doctor

### test_admin
کاربر تست با نقش Admin

### auth_headers
Headers احراز هویت برای test_user

### test_patient
بیمار تست

### test_medical_record
سوابق پزشکی تست

### test_prediction
پیش‌بینی تست

## Best Practices

1. **Isolation**: هر تست باید مستقل باشد
2. **Cleanup**: استفاده از fixtures برای cleanup
3. **Naming**: نام‌گذاری واضح و توصیفی
4. **Assertions**: استفاده از assertions معنادار
5. **Mocking**: Mock کردن external dependencies

## CI/CD Integration

تست‌ها به صورت خودکار در CI/CD pipeline اجرا می‌شوند:

```yaml
# .github/workflows/tests.yml
- name: Run tests
  run: pytest --cov=app --cov-report=xml
```

## Troubleshooting

### مشکل: Database connection errors
**راه‌حل**: مطمئن شوید که test database در conftest.py درست تنظیم شده است

### مشکل: Async test failures
**راه‌حل**: از `@pytest.mark.asyncio` استفاده کنید و `pytest-asyncio` نصب شده باشد

### مشکل: Import errors
**راه‌حل**: مطمئن شوید که PYTHONPATH درست تنظیم شده است

