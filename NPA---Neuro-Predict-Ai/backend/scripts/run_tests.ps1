# PowerShell script to run all tests with coverage

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "NeuroPredict-AI Test Suite" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Run tests
Write-Host "Running Unit Tests..." -ForegroundColor Yellow
pytest tests/unit/ -v --cov=app --cov-report=term-missing --cov-report=html -m unit

Write-Host ""
Write-Host "Running Integration Tests..." -ForegroundColor Yellow
pytest tests/integration/ -v -m integration

Write-Host ""
Write-Host "Running E2E Tests..." -ForegroundColor Yellow
pytest tests/e2e/ -v -m e2e

Write-Host ""
Write-Host "Running Performance Tests..." -ForegroundColor Yellow
pytest tests/performance/ -v -m performance

Write-Host ""
Write-Host "Running Security Tests..." -ForegroundColor Yellow
pytest tests/security/ -v -m security

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "All tests completed!" -ForegroundColor Green
Write-Host "Coverage report: htmlcov/index.html" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

