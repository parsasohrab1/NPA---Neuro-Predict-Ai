# NeuroPredict-AI Full Dashboard Startup
# Starts both Backend and Frontend with Data Fusion Reports

Write-Host ""
Write-Host "="*90 -ForegroundColor Cyan
Write-Host "  🚀 NeuroPredict-AI Full Dashboard Startup" -ForegroundColor Cyan
Write-Host "  راه‌اندازی کامل داشبورد با Data Fusion Reports" -ForegroundColor Cyan
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

# Step 1: Kill existing Node processes
Write-Host "Step 1: Cleaning up existing processes..." -ForegroundColor Yellow
try {
    Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force -ErrorAction SilentlyContinue
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

# Step 3: Check if frontend needs rebuild
Write-Host ""
Write-Host "Step 3: Checking frontend..." -ForegroundColor Yellow
$frontendPath = Join-Path $projectRoot "frontend"
Set-Location $frontendPath

if (-not (Test-Path "node_modules")) {
    Write-Host "⚠ node_modules not found, installing dependencies..." -ForegroundColor Yellow
    npm install
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Frontend dependencies ready" -ForegroundColor Green
}

# Step 4: Start Frontend in new window
Write-Host ""
Write-Host "Step 4: Starting Frontend on port 5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd '$frontendPath'; npm run dev" -WindowStyle Normal
Write-Host "✓ Frontend starting in new window..." -ForegroundColor Green

# Step 5: Wait and provide instructions
Write-Host ""
Write-Host "="*90 -ForegroundColor Green
Write-Host "  ✅ Dashboard is starting..." -ForegroundColor Green
Write-Host "="*90 -ForegroundColor Green
Write-Host ""
Write-Host "⏱️ Please wait ~30-60 seconds for both services to be ready..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📊 Backend Status:" -ForegroundColor Cyan
Write-Host "   Check the Backend window for:" -ForegroundColor White
Write-Host "   ✓ 'Application startup complete'" -ForegroundColor Green
Write-Host "   ✓ 'Uvicorn running on http://0.0.0.0:8001'" -ForegroundColor Green
Write-Host ""
Write-Host "🎨 Frontend Status:" -ForegroundColor Cyan
Write-Host "   Check the Frontend window for:" -ForegroundColor White
Write-Host "   ✓ 'VITE vX.X.X ready in XXX ms'" -ForegroundColor Green
Write-Host "   ✓ 'Local: http://localhost:5173/'" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access Dashboard:" -ForegroundColor Yellow
Write-Host "   1. Open browser: http://localhost:5173" -ForegroundColor Cyan
Write-Host "   2. Login with your credentials" -ForegroundColor White
Write-Host "   3. Look at the LEFT SIDEBAR, you will see:" -ForegroundColor White
Write-Host ""
Write-Host "      📊 Dashboard" -ForegroundColor White
Write-Host "      👥 Patients" -ForegroundColor White
Write-Host "      🔬 New Prediction" -ForegroundColor White
Write-Host "      ✨ Data Fusion Reports" -ForegroundColor Magenta -NoNewline
Write-Host "  ← CLICK HERE!" -ForegroundColor Green
Write-Host "      ⚙️ Settings" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Data Fusion Reports Features:" -ForegroundColor Yellow
Write-Host "   • Patent-pending multi-modal data fusion" -ForegroundColor White
Write-Host "   • Enter Patient ID to generate fusion report" -ForegroundColor White
Write-Host "   • View cognitive, biomarker, and imaging analysis" -ForegroundColor White
Write-Host "   • Cross-modal correlation detection" -ForegroundColor White
Write-Host "   • Automated conflict resolution" -ForegroundColor White
Write-Host "   • Natural language clinical reports" -ForegroundColor White
Write-Host "   • Download reports as text files" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   • Use Patient IDs: 1, 2, 3, etc. (up to 500)" -ForegroundColor White
Write-Host "   • Click 'Generate Fusion Report' to create new reports" -ForegroundColor White
Write-Host "   • Click on any report card to view full details" -ForegroundColor White
Write-Host "   • Look for purple gradient styling (patent-pending feature)" -ForegroundColor White
Write-Host ""
Write-Host "❌ To Stop:" -ForegroundColor Red
Write-Host "   Close both PowerShell windows (Backend & Frontend)" -ForegroundColor White
Write-Host "   Or press Ctrl+C in each window" -ForegroundColor White
Write-Host ""
Write-Host "="*90 -ForegroundColor Green
Write-Host "  🎉 Dashboard Ready! Open http://localhost:5173 " -ForegroundColor Green
Write-Host "="*90 -ForegroundColor Green
Write-Host ""

# Keep this window open for status
Write-Host "Press any key to close this status window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

