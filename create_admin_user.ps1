# PowerShell Script to Create Admin User
# Simple script to create admin user via API

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Create Admin User - NeuroPredict AI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
Write-Host "[1/3] Checking Backend status..." -ForegroundColor Yellow
$backendRunning = netstat -ano | findstr ":8000"

if (-not $backendRunning) {
    Write-Host ""
    Write-Host "ERROR: Backend is not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start backend first:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor White
    Write-Host "  uvicorn app.main:app --reload --port 8000" -ForegroundColor White
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "Backend is running (Port 8000)" -ForegroundColor Green
Write-Host ""

# Prepare user data
Write-Host "[2/3] Preparing user data..." -ForegroundColor Yellow

$userData = @{
    email = "admin@neuropredict.ai"
    username = "admin"
    password = "admin123"
    first_name = "Admin"
    last_name = "User"
    role = "admin"
} | ConvertTo-Json

Write-Host "User data ready" -ForegroundColor Green
Write-Host ""

# Create admin user
Write-Host "[3/3] Creating Admin user..." -ForegroundColor Yellow
Write-Host ""

try {
    # Add TLS 1.2 support
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    
    # Disable certificate validation for localhost (development only!)
    if (-not ([System.Management.Automation.PSTypeName]'TrustAllCertsPolicy').Type) {
        add-type @"
            using System.Net;
            using System.Security.Cryptography.X509Certificates;
            public class TrustAllCertsPolicy : ICertificatePolicy {
                public bool CheckValidationResult(
                    ServicePoint svcPoint, X509Certificate certificate,
                    WebRequest webRequest, int certificateProblem) {
                    return true;
                }
            }
"@
    }
    [System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy

    # Make API request
    $uri = "https://localhost:8000/api/v1/auth/register"
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $userData -ContentType "application/json" -ErrorAction Stop
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SUCCESS! Admin user created" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "User Information:" -ForegroundColor White
    Write-Host "  Email:    admin@neuropredict.ai" -ForegroundColor Cyan
    Write-Host "  Password: admin123" -ForegroundColor Cyan
    Write-Host "  Role:     admin" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Go to dashboard: http://localhost:5173" -ForegroundColor White
    Write-Host "  2. Login with the credentials above" -ForegroundColor White
    Write-Host "  3. Enjoy all features!" -ForegroundColor White
    Write-Host ""
    Write-Host "User ID: $($response.id)" -ForegroundColor Gray
    Write-Host ""
}
catch {
    $errorMessage = $_.Exception.Message
    $errorDetails = $_.ErrorDetails.Message
    
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ERROR Creating User" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    
    # Check for specific errors
    if ($errorDetails -like "*already exists*" -or $errorDetails -like "*duplicate*") {
        Write-Host "INFO: Admin user already exists!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "The user was created before." -ForegroundColor White
        Write-Host "You can login directly with these credentials:" -ForegroundColor White
        Write-Host ""
        Write-Host "  Email:    admin@neuropredict.ai" -ForegroundColor Cyan
        Write-Host "  Password: admin123" -ForegroundColor Cyan
        Write-Host ""
    }
    elseif ($errorMessage -like "*Unable to connect*" -or $errorMessage -like "*No connection*") {
        Write-Host "ERROR: Cannot connect to Backend!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Possible solutions:" -ForegroundColor Yellow
        Write-Host "  1. Make sure Backend is running" -ForegroundColor White
        Write-Host "  2. Check port 8000: netstat -ano | findstr :8000" -ForegroundColor White
        Write-Host "  3. Restart Backend" -ForegroundColor White
        Write-Host ""
    }
    else {
        Write-Host "Error details:" -ForegroundColor Yellow
        Write-Host $errorMessage -ForegroundColor Red
        if ($errorDetails) {
            Write-Host ""
            Write-Host "Backend response:" -ForegroundColor Yellow
            Write-Host $errorDetails -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "Alternative methods:" -ForegroundColor Yellow
        Write-Host "  1. Use Swagger UI: https://localhost:8000/docs" -ForegroundColor White
        Write-Host "  2. Use Browser Console (guide in CREATE_ADMIN_SIMPLE.md)" -ForegroundColor White
        Write-Host ""
    }
}

Write-Host "========================================" -ForegroundColor Gray
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

