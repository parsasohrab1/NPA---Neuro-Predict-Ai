# NeuroPredict-AI Complete Frontend Rebuild Script
# این اسکریپت Frontend را از نو می‌سازد

Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  Frontend Complete Rebuild" -ForegroundColor Cyan
Write-Host "  بازسازی کامل Frontend" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill all Node processes
Write-Host "Step 1: Killing all Node processes..." -ForegroundColor Yellow
try {
    Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✓ All Node processes stopped" -ForegroundColor Green
} catch {
    Write-Host "✓ No Node processes running" -ForegroundColor Green
}
Start-Sleep -Seconds 2

# Step 2: Navigate to frontend directory
Write-Host ""
Write-Host "Step 2: Navigating to frontend directory..." -ForegroundColor Yellow
$frontendPath = "C:\Users\asus\Documents\companies\ithub\AI\products\clones\NPA\frontend"
if (Test-Path $frontendPath) {
    Set-Location $frontendPath
    Write-Host "✓ In frontend directory: $frontendPath" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend directory not found!" -ForegroundColor Red
    Write-Host "  Trying relative path..." -ForegroundColor Yellow
    Set-Location frontend
}

# Step 3: Remove old build artifacts
Write-Host ""
Write-Host "Step 3: Removing old build artifacts..." -ForegroundColor Yellow
Write-Host "  Removing node_modules..." -ForegroundColor Gray
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Write-Host "  Removing dist..." -ForegroundColor Gray
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Write-Host "  Removing .vite..." -ForegroundColor Gray
Remove-Item -Recurse -Force .vite -ErrorAction SilentlyContinue
Write-Host "  Removing package-lock.json..." -ForegroundColor Gray
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
Write-Host "✓ Old artifacts removed" -ForegroundColor Green

# Step 4: Clean npm cache
Write-Host ""
Write-Host "Step 4: Cleaning npm cache..." -ForegroundColor Yellow
npm cache clean --force 2>$null
Write-Host "✓ npm cache cleaned" -ForegroundColor Green

# Step 5: Install dependencies
Write-Host ""
Write-Host "Step 5: Installing dependencies..." -ForegroundColor Yellow
Write-Host "  This may take 2-3 minutes..." -ForegroundColor Gray
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ npm install failed!" -ForegroundColor Red
    Write-Host "  Please check the error messages above" -ForegroundColor Yellow
    exit 1
}

# Step 6: Start dev server
Write-Host ""
Write-Host "Step 6: Starting Frontend Dev Server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "="*80 -ForegroundColor Green
Write-Host "  Frontend is starting..." -ForegroundColor Green
Write-Host "  Wait for 'ready' message (~30 seconds)" -ForegroundColor Green
Write-Host ""
Write-Host "  Then visit: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "  You should see:" -ForegroundColor Yellow
Write-Host "  - Login page with username/password" -ForegroundColor White
Write-Host "  - 🧠 NeuroPredict-AI logo" -ForegroundColor White
Write-Host "  - Theme switcher" -ForegroundColor White
Write-Host ""
Write-Host "  After login, check Sidebar for:" -ForegroundColor Yellow
Write-Host "  - ✨ Data Fusion Reports (with purple gradient)" -ForegroundColor Magenta
Write-Host "="*80 -ForegroundColor Green
Write-Host ""

npm run dev

