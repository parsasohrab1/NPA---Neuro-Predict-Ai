# راه‌اندازی ساده Dashboard
# Simple Dashboard Startup Script

Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  🚀 NeuroPredict-AI Dashboard - راه‌اندازی سریع" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot
if (-not $projectRoot) {
    $projectRoot = Get-Location
}

# Kill existing processes
Write-Host "📋 Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -eq "python" -or ($_.ProcessName -eq "node" -and $_.Path -notlike "*cursor*")} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "✅ Cleaned up" -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "🔧 Starting Backend Server (Port 8001)..." -ForegroundColor Cyan
Write-Host "   Opening in new window..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", `
    "cd '$projectRoot\backend'; " + `
    "`$env:ENVIRONMENT='development'; " + `
    "`$env:DEBUG='True'; " + `
    "`$env:SECRET_KEY='zzqnh591ytCa0DRYv-4mL6IZGC2oi3R005yTN3kQGKc'; " + `
    "`$env:DATABASE_URL='sqlite+aiosqlite:///./neuropredict.db'; " + `
    "`$env:PORT='8001'; " + `
    "python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload" `
    -WindowStyle Normal
Write-Host "✅ Backend window opened" -ForegroundColor Green
Write-Host ""

# Wait for backend
Write-Host "⏳ Waiting 10 seconds for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host ""

# Start Dashboard
Write-Host "🎨 Starting Admin Dashboard (Port 5173)..." -ForegroundColor Cyan
Write-Host "   Opening in new window..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", `
    "cd '$projectRoot\admin-dashboard'; npm run dev" `
    -WindowStyle Normal
Write-Host "✅ Dashboard window opened" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "="*80 -ForegroundColor Green
Write-Host "  ✅ Dashboard Starting!" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access URLs:" -ForegroundColor Cyan
Write-Host "   🎨 Admin Dashboard: http://localhost:5173" -ForegroundColor Magenta
Write-Host "   🔧 Backend API:     http://localhost:8001" -ForegroundColor Magenta
Write-Host "   📊 API Health:      http://localhost:8001/health" -ForegroundColor Magenta
Write-Host "   📚 API Docs:        http://localhost:8001/api/docs" -ForegroundColor Magenta
Write-Host ""
Write-Host "⏱️  Please wait 30-60 seconds for services to fully start" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Check the opened PowerShell windows for:" -ForegroundColor White
Write-Host "   • Backend: Look for 'Application startup complete'" -ForegroundColor Gray
Write-Host "   • Dashboard: Look for 'Local: http://localhost:5173'" -ForegroundColor Gray
Write-Host ""
Write-Host "❌ To Stop:" -ForegroundColor Red
Write-Host "   Close both PowerShell windows" -ForegroundColor White
Write-Host ""
Write-Host "="*80 -ForegroundColor Green
Write-Host ""

