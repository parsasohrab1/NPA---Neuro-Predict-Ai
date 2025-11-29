# NeuroPredict-AI Admin Dashboard Startup
# Starts both Backend and Admin Dashboard

Write-Host ""
Write-Host "="*90 -ForegroundColor Cyan
Write-Host "  🚀 NeuroPredict-AI Admin Dashboard Startup" -ForegroundColor Cyan
Write-Host "  راه‌اندازی داشبورد ادمین" -ForegroundColor Cyan
Write-Host "="*90 -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
$projectRoot = "C:\Users\asus\Documents\companies\ithub\AI\products\clones\NPA"
if (-not (Test-Path $projectRoot)) {
    Write-Host "❌ Project directory not found!" -ForegroundColor Red
    Write-Host "   Expected: $projectRoot" -ForegroundColor Yellow
    exit 1
}

Set-Location $projectRoot

# Step 1: Kill existing Node and Python processes
Write-Host "Step 1: Cleaning up existing processes..." -ForegroundColor Yellow
try {
    Get-Process | Where-Object {$_.ProcessName -like "*node*" -or $_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Cleaned up existing processes" -ForegroundColor Green
} catch {
    Write-Host "✓ No processes to clean" -ForegroundColor Green
}
Start-Sleep -Seconds 2

# Step 2: Start Backend in new window
Write-Host ""
Write-Host "Step 2: Starting Backend on port 8001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd '$projectRoot'; .\start_backend.ps1" -WindowStyle Normal
Write-Host "✓ Backend starting in new window..." -ForegroundColor Green
Write-Host "   Waiting 10 seconds for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Step 3: Check if admin dashboard needs dependencies
Write-Host ""
Write-Host "Step 3: Checking admin dashboard..." -ForegroundColor Yellow
$adminPath = Join-Path $projectRoot "admin-dashboard"
Set-Location $adminPath

if (-not (Test-Path "node_modules")) {
    Write-Host "⚠ node_modules not found, installing dependencies..." -ForegroundColor Yellow
    npm install
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Admin dashboard dependencies ready" -ForegroundColor Green
}

# Step 4: Start Admin Dashboard in new window
Write-Host ""
Write-Host "Step 4: Starting Admin Dashboard..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd '$adminPath'; npm run dev" -WindowStyle Normal
Write-Host "✓ Admin Dashboard starting in new window..." -ForegroundColor Green

# Step 5: Wait and provide instructions
Write-Host ""
Write-Host "="*90 -ForegroundColor Green
Write-Host "  ✅ Admin Dashboard is starting..." -ForegroundColor Green
Write-Host "="*90 -ForegroundColor Green
Write-Host ""
Write-Host "⏱️ Please wait ~30-60 seconds for both services to be ready..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📊 Backend Status:" -ForegroundColor Cyan
Write-Host "   Check the Backend window for:" -ForegroundColor White
Write-Host "   ✓ 'Application startup complete'" -ForegroundColor Green
Write-Host "   ✓ 'Uvicorn running on http://0.0.0.0:8001'" -ForegroundColor Green
Write-Host ""
Write-Host "🎨 Admin Dashboard Status:" -ForegroundColor Cyan
Write-Host "   Check the Admin Dashboard window for:" -ForegroundColor White
Write-Host "   ✓ 'VITE vX.X.X ready in XXX ms'" -ForegroundColor Green
Write-Host "   ✓ 'Local: http://localhost:XXXX/'" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access Admin Dashboard:" -ForegroundColor Yellow
Write-Host "   1. Check the Admin Dashboard window for the exact port" -ForegroundColor Cyan
Write-Host "   2. Open browser to the URL shown (usually http://localhost:5173)" -ForegroundColor Cyan
Write-Host "   3. Login with your admin credentials" -ForegroundColor White
Write-Host ""
Write-Host "❌ To Stop:" -ForegroundColor Red
Write-Host "   Close both PowerShell windows (Backend & Admin Dashboard)" -ForegroundColor White
Write-Host "   Or press Ctrl+C in each window" -ForegroundColor White
Write-Host ""
Write-Host "="*90 -ForegroundColor Green
Write-Host "  🎉 Admin Dashboard Ready!" -ForegroundColor Green
Write-Host "="*90 -ForegroundColor Green
Write-Host ""

# Keep this window open for status
Write-Host "Press any key to close this status window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
