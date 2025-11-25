# ============================================================
# اسکریپت کامل Backup داشبورد NeuroPredict-AI
# ============================================================

param(
    [string]$BackupLocation = ".\backups",
    [switch]$SkipDatabase = $false,
    [switch]$SkipWheels = $false,
    [switch]$Compress = $true
)

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backupDir = "$BackupLocation\dashboard_backup_$timestamp"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ایجاد Backup کامل از داشبورد NeuroPredict-AI" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ایجاد پوشه backup
if (-not (Test-Path $BackupLocation)) {
    New-Item -ItemType Directory -Path $BackupLocation -Force | Out-Null
}
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "✓ پوشه backup ایجاد شد: $backupDir" -ForegroundColor Green
Write-Host ""

# 1. Backup فایل‌های اصلی
Write-Host "[1/6] Backup فایل‌های اصلی..." -ForegroundColor Yellow
$itemsToBackup = @(
    "admin-dashboard",
    "backend",
    "docker-compose.yml",
    "run_dashboard_offline.ps1",
    "DASHBOARD_BACKUP_GUIDE.md",
    "create_full_backup.ps1"
)

$excludePatterns = @(
    "node_modules",
    "__pycache__",
    "*.pyc",
    ".git",
    "*.log",
    "uploads",
    "backups"
)

foreach ($item in $itemsToBackup) {
    if (Test-Path $item) {
        try {
            if ((Get-Item $item).PSIsContainer) {
                # برای پوشه‌ها، فایل‌های خاص را exclude کنیم
                $destPath = "$backupDir\$item"
                New-Item -ItemType Directory -Path $destPath -Force | Out-Null
                
                Get-ChildItem -Path $item -Recurse | Where-Object {
                    $shouldExclude = $false
                    foreach ($pattern in $excludePatterns) {
                        if ($_.FullName -like "*\$pattern\*" -or $_.Name -like $pattern) {
                            $shouldExclude = $true
                            break
                        }
                    }
                    -not $shouldExclude
                } | ForEach-Object {
                    $relativePath = $_.FullName.Substring((Resolve-Path $item).Path.Length + 1)
                    $destFile = Join-Path $destPath $relativePath
                    $destDir = Split-Path $destFile -Parent
                    if (-not (Test-Path $destDir)) {
                        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                    }
                    Copy-Item -Path $_.FullName -Destination $destFile -Force
                }
            } else {
                Copy-Item -Path $item -Destination "$backupDir\$item" -Force
            }
            Write-Host "  ✓ $item" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠ خطا در کپی $item : $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ⚠ $item یافت نشد" -ForegroundColor Yellow
    }
}
Write-Host ""

# 2. Backup دیتابیس
if (-not $SkipDatabase) {
    Write-Host "[2/6] Backup دیتابیس..." -ForegroundColor Yellow
    $dbBackupFile = "$backupDir\database_backup.sql"
    try {
        # بررسی اینکه آیا Docker container در حال اجرا است
        $containerRunning = docker ps --filter "name=neuropredict-db" --format "{{.Names}}" 2>&1
        if ($containerRunning -like "*neuropredict-db*") {
            docker exec neuropredict-db pg_dump -U postgres neuropredict_db > $dbBackupFile 2>&1
            if ($LASTEXITCODE -eq 0 -and (Test-Path $dbBackupFile) -and (Get-Item $dbBackupFile).Length -gt 0) {
                Write-Host "  ✓ Backup دیتابیس ایجاد شد" -ForegroundColor Green
            } else {
                Write-Host "  ⚠ خطا در backup دیتابیس (فایل خالی یا خطا)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  ⚠ Docker container یافت نشد - رد شد" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ⚠ خطا در backup دیتابیس: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "[2/6] Backup دیتابیس رد شد (--SkipDatabase)" -ForegroundColor Yellow
}
Write-Host ""

# 3. Backup Python packages
if (-not $SkipWheels) {
    Write-Host "[3/6] Backup Python packages..." -ForegroundColor Yellow
    $wheelsDir = "$backupDir\python_wheels"
    New-Item -ItemType Directory -Path $wheelsDir -Force | Out-Null
    try {
        if (Test-Path "backend\requirements.txt") {
            Push-Location backend
            pip download -r requirements.txt -d $wheelsDir 2>&1 | Out-Null
            pip freeze > "$backupDir\requirements_freeze.txt" 2>&1
            Pop-Location
            if ((Get-ChildItem $wheelsDir -ErrorAction SilentlyContinue).Count -gt 0) {
                Write-Host "  ✓ Python packages دانلود شدند" -ForegroundColor Green
            } else {
                Write-Host "  ⚠ هیچ package ای دانلود نشد" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  ⚠ requirements.txt یافت نشد" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ⚠ خطا در backup Python packages: $_" -ForegroundColor Yellow
        Pop-Location -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "[3/6] Backup Python packages رد شد (--SkipWheels)" -ForegroundColor Yellow
}
Write-Host ""

# 4. Backup Node.js packages info
Write-Host "[4/6] Backup Node.js packages info..." -ForegroundColor Yellow
try {
    if (Test-Path "admin-dashboard\package-lock.json") {
        Copy-Item -Path "admin-dashboard\package-lock.json" -Destination "$backupDir\package-lock.json" -Force
        Write-Host "  ✓ package-lock.json کپی شد" -ForegroundColor Green
    }
    if (Test-Path "admin-dashboard\package.json") {
        Copy-Item -Path "admin-dashboard\package.json" -Destination "$backupDir\package.json" -Force
        Write-Host "  ✓ package.json کپی شد" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ خطا در backup Node.js info: $_" -ForegroundColor Yellow
}
Write-Host ""

# 5. Backup فایل‌های تنظیمات
Write-Host "[5/6] Backup فایل‌های تنظیمات..." -ForegroundColor Yellow
$configFiles = @(
    "backend\.env",
    "backend\alembic.ini",
    "admin-dashboard\.env",
    "admin-dashboard\vite.config.ts",
    "admin-dashboard\tsconfig.json",
    "admin-dashboard\tailwind.config.js"
)

foreach ($file in $configFiles) {
    if (Test-Path $file) {
        try {
            $destPath = "$backupDir\$file"
            $destDir = Split-Path $destPath -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            Copy-Item -Path $file -Destination $destPath -Force
            Write-Host "  ✓ $file" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠ خطا در کپی $file : $_" -ForegroundColor Yellow
        }
    }
}
Write-Host ""

# 6. ایجاد فایل README برای backup
Write-Host "[6/6] ایجاد فایل README..." -ForegroundColor Yellow
$readmeContent = @"
# Dashboard Backup - $timestamp

این backup در تاریخ $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ایجاد شده است.

## محتویات:

- **admin-dashboard/**: کد کامل داشبورد ادمین (بدون node_modules)
- **backend/**: کد کامل backend (بدون __pycache__)
- **database_backup.sql**: Backup دیتابیس PostgreSQL (اگر موجود باشد)
- **python_wheels/**: Python packages برای نصب offline (اگر موجود باشد)
- **requirements_freeze.txt**: لیست کامل Python packages نصب شده
- **package-lock.json**: لیست کامل Node.js packages
- **package.json**: تنظیمات Node.js packages

## راه‌اندازی مجدد (Offline):

### پیش‌نیازها:
- Python 3.8+ نصب شده
- Node.js 18+ و npm نصب شده
- PostgreSQL (اختیاری - برای restore دیتابیس)

### مراحل:

1. **Restore فایل‌ها:**
   ```powershell
   # کپی backup به مکان مورد نظر
   Copy-Item -Path "$backupDir" -Destination ".\restored_dashboard" -Recurse
   ```

2. **نصب Python packages (اگر python_wheels موجود است):**
   ```powershell
   cd restored_dashboard\backend
   pip install --no-index --find-links ..\python_wheels -r requirements.txt
   ```

3. **نصب Node.js packages:**
   ```powershell
   cd restored_dashboard\admin-dashboard
   npm ci
   # یا اگر npm ci کار نکرد:
   npm install
   ```

4. **Restore دیتابیس (اگر database_backup.sql موجود است):**
   ```powershell
   # با Docker:
   Get-Content restored_dashboard\database_backup.sql | docker exec -i neuropredict-db psql -U postgres -d neuropredict_db
   
   # یا بدون Docker:
   psql -U postgres -h localhost -d neuropredict_db < restored_dashboard\database_backup.sql
   ```

5. **راه‌اندازی داشبورد:**
   ```powershell
   cd restored_dashboard
   .\run_dashboard_offline.ps1
   ```

## دسترسی:

- Admin Dashboard: http://localhost:5173
- Disease Tracking: http://localhost:5173/disease-tracking
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

## نکات:

- اگر python_wheels موجود نیست، باید به اینترنت متصل شوید و `pip install -r requirements.txt` را اجرا کنید
- اگر database_backup.sql موجود نیست، دیتابیس باید از ابتدا ایجاد شود
- برای جزئیات بیشتر، فایل DASHBOARD_BACKUP_GUIDE.md را مطالعه کنید

"@
$readmeContent | Out-File -FilePath "$backupDir\README.md" -Encoding utf8
Write-Host "  ✓ README ایجاد شد" -ForegroundColor Green
Write-Host ""

# فشرده‌سازی (اختیاری)
if ($Compress) {
    Write-Host "فشرده‌سازی backup..." -ForegroundColor Yellow
    $zipFile = "$BackupLocation\dashboard_backup_$timestamp.zip"
    try {
        Compress-Archive -Path $backupDir -DestinationPath $zipFile -Force
        $zipSize = (Get-Item $zipFile).Length / 1MB
        Write-Host "✓ Backup فشرده شد: $zipFile ($([math]::Round($zipSize, 2)) MB)" -ForegroundColor Green
        
        # حذف پوشه اصلی (اختیاری - comment کنید اگر می‌خواهید نگه دارید)
        # Remove-Item -Path $backupDir -Recurse -Force
    } catch {
        Write-Host "⚠ خطا در فشرده‌سازی: $_" -ForegroundColor Yellow
        Write-Host "  Backup در پوشه باقی مانده: $backupDir" -ForegroundColor Yellow
    }
}

# خلاصه
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  ✅ Backup با موفقیت ایجاد شد!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "مکان backup:" -ForegroundColor Cyan
if ($Compress -and (Test-Path $zipFile)) {
    Write-Host "  📦 فایل فشرده: $zipFile" -ForegroundColor White
    Write-Host "  📁 پوشه اصلی: $backupDir" -ForegroundColor White
} else {
    Write-Host "  📁 پوشه: $backupDir" -ForegroundColor White
}
Write-Host ""
Write-Host "حجم:" -ForegroundColor Cyan
if ($Compress -and (Test-Path $zipFile)) {
    $size = (Get-Item $zipFile).Length / 1MB
    Write-Host "  📊 $([math]::Round($size, 2)) MB (فشرده شده)" -ForegroundColor White
} else {
    $size = (Get-ChildItem $backupDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  📊 $([math]::Round($size, 2)) MB" -ForegroundColor White
}
Write-Host ""
Write-Host "برای راه‌اندازی مجدد، فایل README.md در backup را مطالعه کنید." -ForegroundColor Yellow
Write-Host ""

