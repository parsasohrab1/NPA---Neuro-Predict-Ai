# Fix Vite Vulnerabilities Script
# This script updates Vite to the latest version and checks for vulnerabilities

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Vite Security Update Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Function to update Vite in a directory
function Update-Vite {
    param (
        [string]$DirectoryPath,
        [string]$ProjectName
    )
    
    if (-not (Test-Path $DirectoryPath)) {
        Write-Host "⚠️  Directory not found: $DirectoryPath" -ForegroundColor Yellow
        return
    }
    
    Write-Host ""
    Write-Host "📦 Processing $ProjectName..." -ForegroundColor Yellow
    Write-Host "   Path: $DirectoryPath" -ForegroundColor Gray
    
    $packageJsonPath = Join-Path $DirectoryPath "package.json"
    
    if (-not (Test-Path $packageJsonPath)) {
        Write-Host "   ❌ package.json not found" -ForegroundColor Red
        return
    }
    
    # Read current package.json
    $packageJson = Get-Content $packageJsonPath | ConvertFrom-Json
    
    # Check current Vite version
    $currentViteVersion = $packageJson.devDependencies.vite
    Write-Host "   Current Vite version: $currentViteVersion" -ForegroundColor Cyan
    
    # Check for vulnerabilities first
    Write-Host ""
    Write-Host "   🔍 Checking for vulnerabilities..." -ForegroundColor Yellow
    Push-Location $DirectoryPath
    
    try {
        $auditResult = npm audit --json 2>&1
        if ($LASTEXITCODE -eq 0 -or $auditResult -match '"vulnerabilities"') {
            Write-Host "   ⚠️  Vulnerabilities found. Running npm audit fix..." -ForegroundColor Yellow
            npm audit fix --force
        } else {
            Write-Host "   ✅ No critical vulnerabilities found" -ForegroundColor Green
        }
    } catch {
        Write-Host "   ⚠️  Could not run npm audit" -ForegroundColor Yellow
    }
    
    # Update Vite to latest version
    Write-Host ""
    Write-Host "   🔄 Updating Vite to latest version..." -ForegroundColor Yellow
    
    # Update Vite and plugin
    npm install vite@latest @vitejs/plugin-react@latest --save-dev
    
    # Get new version
    $updatedPackageJson = Get-Content $packageJsonPath | ConvertFrom-Json
    $newViteVersion = $updatedPackageJson.devDependencies.vite
    Write-Host "   ✅ Updated to Vite version: $newViteVersion" -ForegroundColor Green
    
    # Check for vulnerabilities again
    Write-Host ""
    Write-Host "   🔍 Re-checking vulnerabilities..." -ForegroundColor Yellow
    npm audit
    
    Pop-Location
    
    Write-Host "   ✅ $ProjectName update complete!" -ForegroundColor Green
}

# Get project root
$projectRoot = $PSScriptRoot
if (-not $projectRoot) {
    $projectRoot = Split-Path -Parent (Get-Location)
}

Write-Host "Project Root: $projectRoot" -ForegroundColor Gray
Write-Host ""

# Update Frontend
$frontendPath = Join-Path $projectRoot "NPA---Neuro-Predict-Ai\frontend"
if (-not (Test-Path $frontendPath)) {
    $frontendPath = Join-Path $projectRoot "frontend"
}

Update-Vite -DirectoryPath $frontendPath -ProjectName "Frontend"

# Update Admin Dashboard
$adminDashboardPath = Join-Path $projectRoot "admin-dashboard"
Update-Vite -DirectoryPath $adminDashboardPath -ProjectName "Admin Dashboard"

# Final audit report
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Final Security Audit" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 Running comprehensive security audit..." -ForegroundColor Yellow
Write-Host ""
Write-Host "For Frontend:" -ForegroundColor Cyan
if (Test-Path $frontendPath) {
    Push-Location $frontendPath
    npm audit
    Pop-Location
}

Write-Host ""
Write-Host "For Admin Dashboard:" -ForegroundColor Cyan
if (Test-Path $adminDashboardPath) {
    Push-Location $adminDashboardPath
    npm audit
    Pop-Location
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  ✅ Vite Update Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test both applications thoroughly" -ForegroundColor White
Write-Host "  2. Check for breaking changes in Vite 7.x" -ForegroundColor White
Write-Host "  3. Update any deprecated configurations" -ForegroundColor White
Write-Host "  4. Run full test suite" -ForegroundColor White
Write-Host ""

