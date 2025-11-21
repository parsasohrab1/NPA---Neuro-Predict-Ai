# Script to fix security vulnerabilities in npm packages (PowerShell)
# Usage: .\scripts\fix_security_vulnerabilities.ps1

Write-Host "🔒 Fixing Security Vulnerabilities in NeuroPredict-AI" -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Yellow

# Function to fix vulnerabilities in a directory
function Fix-Vulnerabilities {
    param(
        [string]$Dir,
        [string]$Name
    )
    
    Write-Host "`nChecking $Name..." -ForegroundColor Yellow
    
    if (Test-Path "$Dir\package.json") {
        Push-Location $Dir
        
        Write-Host "Running npm audit in $Name..." -ForegroundColor Yellow
        npm audit
        
        Write-Host "Running npm audit fix..." -ForegroundColor Yellow
        $result = npm audit fix 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Vulnerabilities fixed in $Name" -ForegroundColor Green
        } else {
            Write-Host "⚠ Some vulnerabilities may require manual intervention" -ForegroundColor Yellow
        }
        
        Write-Host "Verifying fixes..." -ForegroundColor Yellow
        npm audit
        
        Pop-Location
    } else {
        Write-Host "✗ package.json not found in $Dir" -ForegroundColor Red
    }
}

# Fix frontend
if (Test-Path "frontend") {
    Fix-Vulnerabilities -Dir "frontend" -Name "Frontend"
} else {
    Write-Host "✗ Frontend directory not found" -ForegroundColor Red
}

# Fix admin-dashboard
if (Test-Path "admin-dashboard") {
    Fix-Vulnerabilities -Dir "admin-dashboard" -Name "Admin Dashboard"
} else {
    Write-Host "⚠ Admin Dashboard directory not found" -ForegroundColor Yellow
}

Write-Host "`n✅ Security vulnerability fix process completed!" -ForegroundColor Green
Write-Host "⚠ Note: Some vulnerabilities may only affect development mode" -ForegroundColor Yellow
Write-Host "⚠ Production builds are typically not affected`n" -ForegroundColor Yellow

