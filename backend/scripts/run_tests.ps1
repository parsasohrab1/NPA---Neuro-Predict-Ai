# PowerShell script to run tests with coverage report

Write-Host "🧪 Running NeuroPredict-AI Tests" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
}

# Run tests with coverage
Write-Host "Running tests with coverage..." -ForegroundColor Yellow
pytest `
    --cov=app `
    --cov-report=html:htmlcov `
    --cov-report=term-missing `
    --cov-report=xml `
    -v `
    tests/

# Check if coverage report exists
if (Test-Path "htmlcov\index.html") {
    Write-Host ""
    Write-Host "📁 Coverage report generated in htmlcov\index.html" -ForegroundColor Green
    Write-Host "Open it in your browser to view detailed coverage" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️  Coverage report not generated" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Tests completed!" -ForegroundColor Green

