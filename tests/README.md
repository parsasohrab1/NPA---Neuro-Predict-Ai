# Testing Guide

This directory contains all test suites for the NeuroPredict-AI project.

## Test Structure

```
tests/
├── e2e/                    # E2E tests with Playwright
│   ├── playwright.config.ts
│   ├── auth.spec.ts
│   ├── patients.spec.ts
│   └── predictions.spec.ts
└── README.md

backend/tests/
├── performance/            # Performance tests
│   ├── test_api_performance.py
│   └── __init__.py
├── security/               # Security tests (SAST/DAST)
│   ├── test_security_vulnerabilities.py
│   └── __init__.py
├── test_auth_api.py        # Unit/Integration tests
├── test_patients_api.py
├── test_predictions_api.py
├── conftest.py             # Pytest fixtures
└── ...
```

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage (target: 70%)
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m performance       # Performance tests
pytest -m security          # Security tests
pytest -m "not slow"        # Exclude slow tests

# Run specific test file
pytest tests/test_auth_api.py

# Run with verbose output
pytest -v
```

### E2E Tests

```bash
cd tests/e2e

# Install Playwright
npm install -D @playwright/test playwright
npx playwright install

# Run all E2E tests
npx playwright test

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific test file
npx playwright test auth.spec.ts

# Generate HTML report
npx playwright show-report
```

## Test Categories

### 1. Unit Tests
- Test individual functions and components
- Fast execution (<100ms per test)
- No external dependencies

### 2. Integration Tests
- Test API endpoints with database
- Test service integrations
- Medium execution time (<1s per test)

### 3. E2E Tests (Playwright)
- Test complete user workflows
- Browser-based testing
- Tests frontend + backend integration

### 4. Performance Tests
- Measure API response times
- Load testing
- Concurrent request handling
- Marked with `@pytest.mark.slow`

### 5. Security Tests (SAST/DAST)
- SQL injection testing
- XSS vulnerability testing
- Authentication/Authorization testing
- Input validation testing
- Rate limiting verification

## Coverage Target

**Target: 70% code coverage**

Current coverage can be checked with:
```bash
pytest --cov=app --cov-report=term-missing
```

Coverage report will show:
- Overall coverage percentage
- Files with low coverage
- Lines not covered by tests

## CI/CD Integration

Tests are configured to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    cd backend
    pytest --cov=app --cov-fail-under=70
    
- name: Run E2E tests
  run: |
    cd tests/e2e
    npx playwright test
```

## Test Data

- Tests use in-memory SQLite database
- Fixtures provide test data (see `conftest.py`)
- Test data is isolated and cleaned after each test

## Writing New Tests

### Backend Test Example

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_example(test_client: AsyncClient):
    response = await test_client.get("/api/v1/endpoint")
    assert response.status_code == 200
```

### E2E Test Example

```typescript
import { test, expect } from '@playwright/test';

test('example test', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toBeVisible();
});
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Naming**: Use descriptive test names
3. **Assertions**: Use specific assertions
4. **Fixtures**: Reuse fixtures from `conftest.py`
5. **Markers**: Use appropriate markers (`@pytest.mark.slow`, etc.)
6. **Coverage**: Aim for high coverage on critical paths

## Troubleshooting

### Tests failing with database errors
- Ensure test database is properly configured
- Check that fixtures are cleaning up after tests

### E2E tests timing out
- Increase timeout in `playwright.config.ts`
- Ensure backend and frontend are running

### Coverage below target
- Run coverage report to see which files need tests
- Focus on critical business logic first
- Add tests for error handling paths

