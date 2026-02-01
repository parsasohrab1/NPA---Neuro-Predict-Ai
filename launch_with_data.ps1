# NeuroPredict-AI - Launch with Generated Data
# Uses: data/data/csv/sample_dataset_complete.csv, data/real_data/csv/real_dataset_complete.csv

$ErrorActionPreference = "Continue"
$projectRoot = $PSScriptRoot
if (-not $projectRoot) { $projectRoot = Get-Location }

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NeuroPredict-AI - Launch with Data" -ForegroundColor Cyan
Write-Host "  Launch with generated data" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Prepare data - copy from large_dataset if sample_dataset_complete doesn't exist
$sampleCsv = Join-Path $projectRoot "data\data\csv\sample_dataset_complete.csv"
$syntheticCsv = Join-Path $projectRoot "data\large_dataset\synthetic\synthetic_patients_complete.csv"

if (-not (Test-Path $sampleCsv) -and (Test-Path $syntheticCsv)) {
    Write-Host "Step 0: Preparing data from generator..." -ForegroundColor Yellow
    $csvDir = Join-Path $projectRoot "data\data\csv"
    if (-not (Test-Path $csvDir)) { New-Item -ItemType Directory -Path $csvDir -Force | Out-Null }
    # Take first 200 rows from synthetic for sample
    $synthetic = Import-Csv $syntheticCsv | Select-Object -First 200
    $synthetic | Export-Csv $sampleCsv -NoTypeInformation
    Write-Host "  Created sample_dataset_complete.csv from synthetic data" -ForegroundColor Green
} elseif (Test-Path $sampleCsv) {
    Write-Host "Step 0: Sample data exists: sample_dataset_complete.csv" -ForegroundColor Green
} else {
    Write-Host "Step 0: Run data/generate_sample_data.py first to create sample data" -ForegroundColor Yellow
}

# Step 2: Start Backend
Write-Host ""
Write-Host "Step 1: Starting Backend (port 8001)..." -ForegroundColor Yellow
$backendCmd = "cd '$projectRoot\backend'; " +
    "`$env:ENVIRONMENT='development'; `$env:DEBUG='True'; " +
    "`$env:SECRET_KEY='zzqnh591ytCa0DRYv-4mL6IZGC2oi3R005yTN3kQGKc'; " +
    "`$env:DATABASE_URL='sqlite+aiosqlite:///./neuropredict.db'; `$env:PORT='8001'; " +
    "python -m uvicorn app.main:app --host 0.0.0.0 --port 8001"
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCmd -WindowStyle Normal
Write-Host "  Backend starting in new window..." -ForegroundColor Green

# Step 3: Wait for backend
Write-Host ""
Write-Host "Step 2: Waiting for backend to be ready (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
$maxRetries = 10
$retry = 0
$backendReady = $false
while ($retry -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host "  Backend is ready!" -ForegroundColor Green
            break
        }
    } catch { }
    $retry++
    Start-Sleep -Seconds 2
}
if (-not $backendReady) {
    Write-Host "  Backend may still be starting. Continuing..." -ForegroundColor Yellow
}

# Step 4: Load sample data via API
Write-Host ""
Write-Host "Step 3: Loading sample data (200 patients)..." -ForegroundColor Yellow
try {
    $loadResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/disease-tracking/load-sample-datasets" `
        -Method POST -ContentType "application/json" -TimeoutSec 120
    Write-Host "  Loaded: $($loadResponse.total_patients) patients, $($loadResponse.total_records) records, $($loadResponse.total_predictions) predictions" -ForegroundColor Green
    if ($loadResponse.skipped -gt 0) {
        Write-Host "  (Skipped $($loadResponse.skipped) - already exist. Use Clear All Data in dashboard to reload)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Could not load sample data. You can load it manually from Disease Tracking dashboard." -ForegroundColor Yellow
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
}

# Step 5: Start Admin Dashboard
Write-Host ""
Write-Host "Step 4: Starting Admin Dashboard (port 3000)..." -ForegroundColor Yellow
$adminPath = Join-Path $projectRoot "admin-dashboard"
if (-not (Test-Path (Join-Path $adminPath "node_modules"))) {
    Write-Host "  Installing admin-dashboard dependencies..." -ForegroundColor Gray
    Push-Location $adminPath; npm install 2>&1 | Out-Null; Pop-Location
}
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd '$adminPath'; npm run dev" -WindowStyle Normal
Write-Host "  Admin Dashboard starting..." -ForegroundColor Green

# Step 6: Start Frontend
Write-Host ""
Write-Host "Step 5: Starting Frontend (port 3001)..." -ForegroundColor Yellow
$frontendPath = Join-Path $projectRoot "frontend"
if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Write-Host "  Installing frontend dependencies..." -ForegroundColor Gray
    Push-Location $frontendPath; npm install 2>&1 | Out-Null; Pop-Location
}
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd '$frontendPath'; npm run dev" -WindowStyle Normal
Write-Host "  Frontend starting..." -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Launch Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  Admin Dashboard:  http://localhost:3000" -ForegroundColor White
Write-Host "  Frontend (Main):  http://localhost:3001" -ForegroundColor White
Write-Host "  Backend API:      http://localhost:8001" -ForegroundColor White
Write-Host "  API Docs:         http://localhost:8001/api/docs" -ForegroundColor White
Write-Host ""
Write-Host "Data loaded from:" -ForegroundColor Cyan
Write-Host "  - data/data/csv/sample_dataset_complete.csv" -ForegroundColor Gray
Write-Host "  - data/real_data/csv/real_dataset_complete.csv" -ForegroundColor Gray
Write-Host ""
Write-Host "Both Admin and Frontend proxy API calls to backend (port 8001)" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop: Close the 3 PowerShell windows (Backend, Admin, Frontend)" -ForegroundColor Yellow
Write-Host ""
