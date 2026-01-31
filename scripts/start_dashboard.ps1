# PowerShell Script to start NeuroPredict-AI Live Dashboard

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting NeuroPredict-AI Live Dashboard" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Navigate to project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Join-Path $scriptPath ".."
Set-Location $projectPath

Write-Host "📦 Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "✅ Services started!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access the dashboards at:" -ForegroundColor Cyan
Write-Host "   - Main Application: http://localhost:3000" -ForegroundColor White
Write-Host "   - Admin Dashboard:  http://localhost:3001" -ForegroundColor White
Write-Host "   - API Documentation: http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "   - Health Check:      http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "📊 Monitoring:" -ForegroundColor Cyan
Write-Host "   - Prometheus:       http://localhost:9090" -ForegroundColor White
Write-Host "   - Grafana:          http://localhost:3001 (if using production compose)" -ForegroundColor White
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "   docker-compose logs -f" -ForegroundColor White
Write-Host ""
Write-Host "To stop services:" -ForegroundColor Yellow
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""

