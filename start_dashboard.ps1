# Simple PowerShell Script to start NeuroPredict-AI Live Dashboard
# Run from the project root directory (where docker-compose.yml is located)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting NeuroPredict-AI Live Dashboard" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
        Write-Host "   Then run this script again." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Write-Host "   Then run this script again." -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose.yml exists
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ docker-compose.yml not found in current directory" -ForegroundColor Red
    Write-Host "   Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "   Please run this script from the project root directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "📦 Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10

    Write-Host ""
    Write-Host "✅ Services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access the dashboards at:" -ForegroundColor Cyan
    Write-Host "   - Main Application: http://localhost:3000" -ForegroundColor White
    Write-Host "   - Admin Dashboard:  http://localhost:3001" -ForegroundColor White
    Write-Host "   - API Documentation: http://localhost:8000/api/docs" -ForegroundColor White
    Write-Host "   - Health Check:      http://localhost:8000/health" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Useful commands:" -ForegroundColor Cyan
    Write-Host "   View logs:          docker-compose logs -f" -ForegroundColor White
    Write-Host "   Check status:       docker-compose ps" -ForegroundColor White
    Write-Host "   Stop services:      docker-compose down" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Failed to start services. Check the error messages above." -ForegroundColor Red
    Write-Host "   Try: docker-compose logs" -ForegroundColor Yellow
    exit 1
}

