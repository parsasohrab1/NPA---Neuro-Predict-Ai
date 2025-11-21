# Run all tests for NeuroPredict-AI (PowerShell)
# Usage: .\scripts\run_all_tests.ps1

Write-Host "🧪 Running all tests for NeuroPredict-AI" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

# 1. Run unit and integration tests with coverage
Write-Host "`n1. Running backend unit and integration tests..." -ForegroundColor Yellow
Set-Location backend

pytest `
    --cov=app `
    --cov-report=term-missing `
    --cov-report=html `
    --cov-fail-under=70 `
    -v `
    -m "not slow" `
    tests/

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Backend tests passed" -ForegroundColor Green
} else {
    Write-Host "✗ Backend tests failed" -ForegroundColor Red
    Set-Location ..
    exit 1
}

# 2. Run performance tests
Write-Host "`n2. Running performance tests..." -ForegroundColor Yellow
pytest -v -m performance tests/performance/
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Performance tests have warnings" -ForegroundColor Yellow
}

# 3. Run security tests
Write-Host "`n3. Running security tests..." -ForegroundColor Yellow
pytest -v -m security tests/security/
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Security tests have warnings" -ForegroundColor Yellow
}

# 4. Run slow tests (optional)
Write-Host "`n4. Running slow tests (optional)..." -ForegroundColor Yellow
$runSlow = Read-Host "Run slow tests? (y/n)"
if ($runSlow -eq "y" -or $runSlow -eq "Y") {
    pytest -v -m slow tests/
}

Set-Location ..

# 5. Run E2E tests (if Playwright is installed)
if (Test-Path "tests\e2e") {
    Write-Host "`n5. Running E2E tests with Playwright..." -ForegroundColor Yellow
    Set-Location tests\e2e
    if (Get-Command npx -ErrorAction SilentlyContinue) {
        npx playwright test
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠ E2E tests require backend/frontend to be running" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠ npx not found, skipping E2E tests" -ForegroundColor Yellow
    }
    Set-Location ..\..
}

Write-Host "`n✅ All tests completed!" -ForegroundColor Green
Write-Host "Coverage report: backend\htmlcov\index.html" -ForegroundColor Cyan

