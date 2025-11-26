# NeuroPredict-AI Frontend Restart Script
# This script safely restarts the frontend development server

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Frontend Restart Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill all node processes
Write-Host "Step 1: Stopping all Node processes..." -ForegroundColor Yellow
try {
    Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✓ All Node processes stopped" -ForegroundColor Green
} catch {
    Write-Host "✓ No Node processes to stop" -ForegroundColor Green
}
Start-Sleep -Seconds 2

# Step 2: Pull latest changes
Write-Host ""
Write-Host "Step 2: Pulling latest changes from Git..." -ForegroundColor Yellow
git pull origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Latest changes pulled successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ Git pull had issues, continuing anyway..." -ForegroundColor Yellow
}

# Step 3: Navigate to frontend
Write-Host ""
Write-Host "Step 3: Navigating to frontend directory..." -ForegroundColor Yellow
Set-Location frontend

# Step 4: Install dependencies (optional, uncomment if needed)
# Write-Host ""
# Write-Host "Step 4: Installing dependencies..." -ForegroundColor Yellow
# npm install

# Step 5: Start dev server
Write-Host ""
Write-Host "Step 5: Starting Frontend Dev Server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Frontend Dev Server Starting..." -ForegroundColor Green
Write-Host "  Wait for 'ready' message, then visit:" -ForegroundColor Green
Write-Host "  http://localhost:5173/data-fusion" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

npm run dev
