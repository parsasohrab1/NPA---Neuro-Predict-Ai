# NeuroPredict-AI Admin Dashboard with Data Fusion Reports
# Starts Backend and Admin Dashboard

Write-Host ""
Write-Host "="*90 -ForegroundColor Magenta
Write-Host "  🎯 NeuroPredict-AI Admin Dashboard + Data Fusion Reports" -ForegroundColor Magenta
Write-Host "  داشبورد مدیریت با گزارش‌های Data Fusion" -ForegroundColor Magenta
Write-Host "="*90 -ForegroundColor Magenta
Write-Host ""

$projectRoot = "C:\Users\asus\Documents\companies\ithub\AI\products\clones\NPA"
if (-not (Test-Path $projectRoot)) {
    Write-Host "❌ Project directory not found!" -ForegroundColor Red
    exit 1
}

Set-Location $projectRoot

# Kill existing processes
Write-Host "Step 1: Cleaning up..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start Backend
Write-Host ""
Write-Host "Step 2: Starting Backend (port 8001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd '$projectRoot'; .\start_backend.ps1" -WindowStyle Normal
Write-Host "✓ Backend starting..." -ForegroundColor Green
Start-Sleep -Seconds 10

# Check admin-dashboard dependencies
Write-Host ""
Write-Host "Step 3: Checking Admin Dashboard..." -ForegroundColor Yellow
$adminPath = Join-Path $projectRoot "admin-dashboard"
Set-Location $adminPath

if (-not (Test-Path "node_modules")) {
    Write-Host "⚠ Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start Admin Dashboard
Write-Host ""
Write-Host "Step 4: Starting Admin Dashboard (port 5174)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd '$adminPath'; npm run dev" -WindowStyle Normal
Write-Host "✓ Admin Dashboard starting..." -ForegroundColor Green

Write-Host ""
Write-Host "="*90 -ForegroundColor Green
Write-Host "  ✅ Services Starting..." -ForegroundColor Green
Write-Host "="*90 -ForegroundColor Green
Write-Host ""
Write-Host "⏱️ Please wait ~60 seconds..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Access Admin Dashboard:" -ForegroundColor Cyan
Write-Host "   http://localhost:5174" -ForegroundColor Magenta
Write-Host ""
Write-Host "📋 In the LEFT SIDEBAR, you will see:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   ╔════════════════════════════════════════╗" -ForegroundColor DarkGray
Write-Host "   ║  System Overview                       ║" -ForegroundColor White
Write-Host "   ║  Disease Tracking                      ║" -ForegroundColor White
Write-Host "   ║  Data Monitoring                       ║" -ForegroundColor White
Write-Host "   ║  3D Analysis                           ║" -ForegroundColor White
Write-Host "   ║  " -NoNewline -ForegroundColor DarkGray
Write-Host "✨ Data Fusion Reports" -NoNewline -BackgroundColor DarkMagenta -ForegroundColor White
Write-Host " [PATENT]" -NoNewline -ForegroundColor Yellow
Write-Host "  ║" -ForegroundColor DarkGray
Write-Host "   ║  Reports                               ║" -ForegroundColor White
Write-Host "   ║  Longitudinal                          ║" -ForegroundColor White
Write-Host "   ║  Users                                 ║" -ForegroundColor White
Write-Host "   ║  Roles & Permissions                   ║" -ForegroundColor White
Write-Host "   ║  Models                                ║" -ForegroundColor White
Write-Host "   ║  Audit Logs                            ║" -ForegroundColor White
Write-Host "   ║  System Settings                       ║" -ForegroundColor White
Write-Host "   ╚════════════════════════════════════════╝" -ForegroundColor DarkGray
Write-Host ""
Write-Host "✨ Data Fusion Reports Features:" -ForegroundColor Magenta
Write-Host "   • Purple gradient styling (Patent-pending indicator)" -ForegroundColor White
Write-Host "   • PATENT badge next to menu item" -ForegroundColor White
Write-Host "   • Dark theme optimized for admin dashboard" -ForegroundColor White
Write-Host "   • Full multi-modal data fusion functionality" -ForegroundColor White
Write-Host "   • Generate reports for any patient (1-500)" -ForegroundColor White
Write-Host "   • View detailed fusion analysis" -ForegroundColor White
Write-Host "   • Download reports as text files" -ForegroundColor White
Write-Host "   • Cross-modal correlation visualization" -ForegroundColor White
Write-Host ""
Write-Host "🎯 How to Use:" -ForegroundColor Yellow
Write-Host "   1. Click on '✨ Data Fusion Reports' (purple gradient item)" -ForegroundColor White
Write-Host "   2. Enter Patient ID (1-500)" -ForegroundColor White
Write-Host "   3. Click 'Generate Fusion Report'" -ForegroundColor White
Write-Host "   4. View generated reports in the list" -ForegroundColor White
Write-Host "   5. Click any report card for full details" -ForegroundColor White
Write-Host "   6. Download reports if needed" -ForegroundColor White
Write-Host ""
Write-Host "💡 Key Differences:" -ForegroundColor Yellow
Write-Host "   • Dark theme (slate-900/800)" -ForegroundColor White
Write-Host "   • Admin-focused layout" -ForegroundColor White
Write-Host "   • Integrated with other admin tools" -ForegroundColor White
Write-Host "   • Same fusion algorithm as main app" -ForegroundColor White
Write-Host ""
Write-Host "❌ To Stop:" -ForegroundColor Red
Write-Host "   Close both PowerShell windows" -ForegroundColor White
Write-Host ""
Write-Host "="*90 -ForegroundColor Green
Write-Host "  🎉 Admin Dashboard Ready! http://localhost:5174 " -ForegroundColor Green
Write-Host "="*90 -ForegroundColor Green
Write-Host ""

Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

