# ============================================================
# NeuroPredict-AI Dashboard - راه‌اندازی جامع (بدون اینترنت)
# ============================================================
# این اسکریپت تمام قابلیت‌های لازم برای راه‌اندازی داشبورد را دارد
# - بررسی خودکار مسیر
# - بررسی پیش‌نیازها (Python, Node.js)
# - بررسی پورت‌ها
# - بررسی dependencies
# - راه‌اندازی Backend و Frontend
# - باز کردن خودکار مرورگر
# ============================================================

param(
    [switch]$SkipChecks = $false,
    [switch]$NoBrowser = $false,
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173,
    [switch]$SkipBackend = $false,
    [switch]$SkipFrontend = $false
)

$ErrorActionPreference = "Continue"
$script:ProjectRoot = $PSScriptRoot

# تنظیم encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                          ║" -ForegroundColor Cyan
Write-Host "║   NeuroPredict-AI Dashboard - راه‌اندازی جامع          ║" -ForegroundColor Cyan
Write-Host "║   Dashboard Startup - Complete Version                  ║" -ForegroundColor Cyan
Write-Host "║                                                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $connection
}

# Function to wait for service
function Wait-ForService {
    param(
        [string]$Url,
        [int]$MaxAttempts = 30,
        [int]$DelaySeconds = 2
    )
    $attempt = 0
    while ($attempt -lt $MaxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                return $true
            }
        } catch {
            # Service not ready yet
        }
        $attempt++
        Start-Sleep -Seconds $DelaySeconds
        Write-Host "." -NoNewline -ForegroundColor Yellow
    }
    Write-Host ""
    return $false
}

# ============================================================
# Step 1: Check Prerequisites
# ============================================================
Write-Host "[1/6] بررسی پیش‌نیازها..." -ForegroundColor Yellow

if (-not $SkipChecks) {
    # Check Python
    if (-not (Test-Command "python")) {
        Write-Host "❌ Python یافت نشد. لطفاً Python را نصب کنید." -ForegroundColor Red
        Write-Host "   دانلود از: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
    $pythonVersion = python --version 2>&1
    Write-Host "   ✓ Python: $pythonVersion" -ForegroundColor Green

    # Check Node.js
    if (-not (Test-Command "node")) {
        Write-Host "❌ Node.js یافت نشد. لطفاً Node.js را نصب کنید." -ForegroundColor Red
        Write-Host "   دانلود از: https://nodejs.org/" -ForegroundColor Yellow
        exit 1
    }
    $nodeVersion = node --version
    Write-Host "   ✓ Node.js: $nodeVersion" -ForegroundColor Green

    # Check npm
    if (-not (Test-Command "npm")) {
        Write-Host "❌ npm یافت نشد. لطفاً npm را نصب کنید." -ForegroundColor Red
        exit 1
    }
    $npmVersion = npm --version
    Write-Host "   ✓ npm: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "   ⚠ بررسی‌ها رد شد" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 2: Check Project Structure
# ============================================================
Write-Host "[2/6] بررسی ساختار پروژه..." -ForegroundColor Yellow

$requiredDirs = @(
    "backend",
    "admin-dashboard"
)

$backendDir = "$script:ProjectRoot\backend"
$frontendDir = "$script:ProjectRoot\admin-dashboard"

# جستجو در پوشه والد اگر در دایرکتوری فعلی یافت نشد
if (-not (Test-Path $backendDir)) {
    $parentDir = Split-Path $script:ProjectRoot -Parent
    if (Test-Path "$parentDir\backend") {
        $script:ProjectRoot = $parentDir
        $backendDir = "$script:ProjectRoot\backend"
        $frontendDir = "$script:ProjectRoot\admin-dashboard"
        Set-Location $script:ProjectRoot
    }
}

foreach ($dir in $requiredDirs) {
    $dirPath = "$script:ProjectRoot\$dir"
    if (-not (Test-Path $dirPath)) {
        Write-Host "❌ پوشه '$dir' یافت نشد" -ForegroundColor Red
        Write-Host "   دایرکتوری فعلی: $script:ProjectRoot" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "   ✓ $dir" -ForegroundColor Green
}

Write-Host ""

# ============================================================
# Step 3: Check Dependencies
# ============================================================
Write-Host "[3/6] بررسی وابستگی‌ها..." -ForegroundColor Yellow

# Check Python dependencies
if (Test-Path "$backendDir\requirements.txt") {
    Write-Host "   بررسی Python packages..." -ForegroundColor Cyan
    $pythonPackages = @("fastapi", "uvicorn", "sqlalchemy", "pydantic")
    $missingPackages = @()
    
    foreach ($package in $pythonPackages) {
        $result = python -c "import $package" 2>&1
        if ($LASTEXITCODE -ne 0) {
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Host "   ⚠ برخی packages نصب نشده‌اند: $($missingPackages -join ', ')" -ForegroundColor Yellow
        Write-Host "   💡 برای نصب: cd backend && pip install -r requirements.txt" -ForegroundColor Cyan
    } else {
        Write-Host "   ✓ Python packages آماده" -ForegroundColor Green
    }
}

# Check Node.js dependencies
if (Test-Path "$frontendDir\node_modules") {
    Write-Host "   ✓ Node modules موجود است" -ForegroundColor Green
} else {
    Write-Host "   ⚠ node_modules یافت نشد" -ForegroundColor Yellow
    Write-Host "   💡 برای نصب: cd admin-dashboard && npm install" -ForegroundColor Cyan
    $install = Read-Host "   آیا می‌خواهید الان نصب کنید؟ (Y/N)"
    if ($install -eq "Y" -or $install -eq "y") {
        Push-Location $frontendDir
        npm install
        Pop-Location
    }
}

Write-Host ""

# ============================================================
# Step 4: Check Ports
# ============================================================
Write-Host "[4/6] بررسی پورت‌ها..." -ForegroundColor Yellow

if (Test-Port $BackendPort) {
    Write-Host "   ⚠ پورت $BackendPort در حال استفاده است" -ForegroundColor Yellow
    $restart = Read-Host "   آیا می‌خواهید دوباره راه‌اندازی کنید؟ (Y/N)"
    if ($restart -ne "Y" -and $restart -ne "y") {
        $SkipBackend = $true
    }
}

if (Test-Port $FrontendPort) {
    Write-Host "   ⚠ پورت $FrontendPort در حال استفاده است" -ForegroundColor Yellow
    $restart = Read-Host "   آیا می‌خواهید دوباره راه‌اندازی کنید؟ (Y/N)"
    if ($restart -ne "Y" -and $restart -ne "y") {
        $SkipFrontend = $true
    }
}

Write-Host ""

# ============================================================
# Step 5: Setup Environment
# ============================================================
Write-Host "[5/6] تنظیم محیط..." -ForegroundColor Yellow

$env:PYTHONUNBUFFERED = "1"
$env:ENVIRONMENT = "development"
$env:DEBUG = "True"
$env:VITE_API_URL = "http://localhost:$BackendPort"

# Check for .env file
if (Test-Path "$backendDir\.env") {
    Write-Host "   ✓ فایل .env یافت شد" -ForegroundColor Green
} else {
    Write-Host "   ⚠ فایل .env یافت نشد - استفاده از مقادیر پیش‌فرض" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 6: Start Services
# ============================================================
Write-Host "[6/6] راه‌اندازی سرویس‌ها..." -ForegroundColor Yellow

$backendProcess = $null
$frontendProcess = $null

# Start Backend
if (-not $SkipBackend) {
    Write-Host "   راه‌اندازی Backend..." -ForegroundColor Cyan
    try {
        Push-Location $backendDir
        
        if (Test-Port $BackendPort) {
            Write-Host "   ⚠ Backend در حال اجرا است" -ForegroundColor Yellow
        } else {
            $backendProcess = Start-Process -FilePath "python" `
                -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$BackendPort", "--reload" `
                -WorkingDirectory $backendDir `
                -PassThru `
                -WindowStyle Normal
            
            Write-Host "   ⏳ منتظر راه‌اندازی Backend..." -ForegroundColor Yellow
            if (Wait-ForService "http://localhost:$BackendPort/health" -MaxAttempts 30) {
                Write-Host "   ✓ Backend راه‌اندازی شد" -ForegroundColor Green
            } else {
                Write-Host "   ⚠ Backend در حال راه‌اندازی است..." -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "   ❌ خطا در راه‌اندازی Backend: $_" -ForegroundColor Red
    } finally {
        Pop-Location
    }
} else {
    Write-Host "   ⏭ Backend رد شد" -ForegroundColor Yellow
}

Write-Host ""

# Start Frontend
if (-not $SkipFrontend) {
    Write-Host "   راه‌اندازی Frontend..." -ForegroundColor Cyan
    try {
        Push-Location $frontendDir
        
        if (Test-Port $FrontendPort) {
            Write-Host "   ⚠ Frontend در حال اجرا است" -ForegroundColor Yellow
        } else {
            $frontendProcess = Start-Process -FilePath "npm" `
                -ArgumentList "run", "dev" `
                -WorkingDirectory $frontendDir `
                -PassThru `
                -WindowStyle Normal
            
            Write-Host "   ⏳ منتظر راه‌اندازی Frontend..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            
            if (Test-Port $FrontendPort) {
                Write-Host "   ✓ Frontend راه‌اندازی شد" -ForegroundColor Green
            } else {
                Write-Host "   ⚠ Frontend در حال راه‌اندازی است..." -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "   ❌ خطا در راه‌اندازی Frontend: $_" -ForegroundColor Red
    } finally {
        Pop-Location
    }
} else {
    Write-Host "   ⏭ Frontend رد شد" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Summary
# ============================================================
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "║   ✅ داشبورد با موفقیت راه‌اندازی شد!                  ║" -ForegroundColor Green
Write-Host "║   ✅ Dashboard Started Successfully!                     ║" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 دسترسی به داشبوردها:" -ForegroundColor Cyan
Write-Host "   - Admin Dashboard:  http://localhost:$FrontendPort" -ForegroundColor White
Write-Host "   - Disease Tracking: http://localhost:$FrontendPort/disease-tracking" -ForegroundColor White
Write-Host "   - System Overview:  http://localhost:$FrontendPort/" -ForegroundColor White
Write-Host "   - API Documentation: http://localhost:$BackendPort/api/docs" -ForegroundColor White
Write-Host "   - Health Check:     http://localhost:$BackendPort/health" -ForegroundColor White
Write-Host ""
Write-Host "📊 اطلاعات سرویس‌ها:" -ForegroundColor Cyan
Write-Host "   - Backend Port:  $BackendPort" -ForegroundColor White
Write-Host "   - Frontend Port: $FrontendPort" -ForegroundColor White
Write-Host "   - Project Root:  $script:ProjectRoot" -ForegroundColor White
Write-Host ""
Write-Host "📌 نکات مهم:" -ForegroundColor Yellow
Write-Host "   - برای توقف سرویس‌ها، پنجره‌های PowerShell را ببندید" -ForegroundColor White
Write-Host "   - اگر خطایی دیدید، پنجره‌های Backend و Frontend را بررسی کنید" -ForegroundColor White
Write-Host ""

# Open browser
if (-not $NoBrowser) {
    Start-Sleep -Seconds 3
    Write-Host "🌐 باز کردن مرورگر..." -ForegroundColor Cyan
    Start-Process "http://localhost:$FrontendPort"
    Start-Sleep -Seconds 1
    Start-Process "http://localhost:$FrontendPort/disease-tracking"
}

Write-Host ""
Write-Host "⏸  در حال اجرا... (برای توقف Ctrl+C را فشار دهید)" -ForegroundColor Yellow
Write-Host ""

try {
    # Keep script running
    while ($true) {
        Start-Sleep -Seconds 10
    }
} catch {
    Write-Host ""
    Write-Host "🛑 توقف سرویس‌ها..." -ForegroundColor Yellow
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($frontendProcess -and -not $frontendProcess.HasExited) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ سرویس‌ها متوقف شدند" -ForegroundColor Green
}

