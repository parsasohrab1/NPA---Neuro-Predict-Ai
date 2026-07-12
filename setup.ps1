# NeuroPredict-AI Setup Script for Windows

Write-Host "🧠 NeuroPredict-AI Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker and Docker Compose are installed" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "✅ .env file created. Please edit it with your configuration." -ForegroundColor Green
}

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "backend\uploads\dicom" | Out-Null
New-Item -ItemType Directory -Force -Path "backend\uploads\mri" | Out-Null
New-Item -ItemType Directory -Force -Path "backend\models" | Out-Null
New-Item -ItemType Directory -Force -Path "backend\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "frontend\dist" | Out-Null
New-Item -ItemType Directory -Force -Path "admin-dashboard\dist" | Out-Null

Write-Host ""
Write-Host "🚀 Starting services with Docker Compose..." -ForegroundColor Cyan
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow
docker-compose exec -T backend python scripts/init_db.py

Write-Host ""
Write-Host "👤 Creating admin user..." -ForegroundColor Yellow
docker-compose exec -T backend python scripts/create_admin.py

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access URLs:" -ForegroundColor Cyan
Write-Host "   Frontend:     http://localhost:3000"
Write-Host "   Admin:        http://localhost:3001"
Write-Host "   Backend API:  http://localhost:8001"
Write-Host "   API Docs:     http://localhost:8001/api/docs"
Write-Host ""
Write-Host "🔐 Default Credentials:" -ForegroundColor Yellow
Write-Host "   Username: admin"
Write-Host "   Password: admin123"
Write-Host ""
Write-Host "⚠️  Remember to change the default password in production!" -ForegroundColor Red
Write-Host ""
Write-Host "📚 Documentation: docs/" -ForegroundColor Cyan
Write-Host ""

