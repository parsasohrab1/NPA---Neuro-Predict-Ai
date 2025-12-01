# راه‌اندازی Backend با Fallback برای Redis
# Backend Startup Script with Redis Fallback

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  NeuroPredict-AI Backend Startup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:ENVIRONMENT = "development"
$env:DEBUG = "True"
$env:SECRET_KEY = "zzqnh591ytCa0DRYv-4mL6IZGC2oi3R005yTN3kQGKc"
$env:DATABASE_URL = "sqlite+aiosqlite:///./neuropredict.db"
$env:DATABASE_URL_SYNC = "sqlite:///./neuropredict.db"
$env:HOST = "0.0.0.0"
$env:PORT = "8001"
$env:REDIS_HOST = "localhost"
$env:REDIS_PORT = "6379"
$env:REDIS_DB = "0"
$env:LOG_LEVEL = "INFO"
$env:RATE_LIMIT_ENABLED = "False"
$env:RATE_LIMIT_FAIL_OPEN = "True"
$env:BACKUP_VERIFY_WEEKLY = "False"

Write-Host "Environment variables configured" -ForegroundColor Green
Write-Host "  - Using SQLite database" -ForegroundColor Yellow
Write-Host "  - Server will run on port 8001" -ForegroundColor Yellow
Write-Host "  - Redis optional (will use memory fallback if not available)" -ForegroundColor Yellow
Write-Host ""

# Navigate to backend directory
Set-Location $PSScriptRoot

Write-Host "Starting backend server..." -ForegroundColor Cyan
Write-Host ""

# Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

