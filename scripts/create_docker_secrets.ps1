# Script to create Docker secrets for production (PowerShell)
# Usage: .\scripts\create_docker_secrets.ps1

Write-Host "🔐 Creating Docker secrets for NeuroPredict-AI Production" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Yellow

# Check if Docker Swarm is initialized
$swarmInfo = docker info 2>&1 | Select-String "Swarm: active"
if (-not $swarmInfo) {
    Write-Host "⚠ Docker Swarm is not active. Initializing..." -ForegroundColor Yellow
    docker swarm init
}

# Function to generate secret key
function Generate-SecretKey {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    [Convert]::ToBase64String($bytes)
}

# Function to create secret
function Create-Secret {
    param(
        [string]$SecretName,
        [string]$Prompt,
        [bool]$IsPassword
    )
    
    if (docker secret ls 2>&1 | Select-String -Pattern $SecretName) {
        Write-Host "Secret $SecretName already exists. Skipping..." -ForegroundColor Yellow
        return
    }
    
    if ($IsPassword) {
        $secureValue = Read-Host -Prompt "$Prompt" -AsSecureString
        $secretValue = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)
        )
        
        $secureConfirm = Read-Host -Prompt "Confirm $Prompt" -AsSecureString
        $confirmValue = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureConfirm)
        )
        
        if ($secretValue -ne $confirmValue) {
            Write-Host "✗ Passwords do not match!" -ForegroundColor Red
            exit 1
        }
    } else {
        $secretValue = Read-Host -Prompt $Prompt
    }
    
    if ([string]::IsNullOrEmpty($secretValue)) {
        Write-Host "✗ Value cannot be empty!" -ForegroundColor Red
        exit 1
    }
    
    $secretValue | docker secret create $SecretName -
    Write-Host "✓ Secret $SecretName created" -ForegroundColor Green
}

Write-Host "`nCreating secrets...`n" -ForegroundColor Yellow

# 1. Secret Key for JWT
if (docker secret ls 2>&1 | Select-String -Pattern "neuropredict_secret_key") {
    Write-Host "Secret neuropredict_secret_key already exists." -ForegroundColor Yellow
    $generateNew = Read-Host "Generate new secret key? (y/n)"
    if ($generateNew -eq "y" -or $generateNew -eq "Y") {
        docker secret rm neuropredict_secret_key 2>$null
        $secretKey = Generate-SecretKey
        $secretKey | docker secret create neuropredict_secret_key -
        Write-Host "✓ Secret neuropredict_secret_key created (auto-generated)" -ForegroundColor Green
    }
} else {
    $secretKey = Generate-SecretKey
    $secretKey | docker secret create neuropredict_secret_key -
    Write-Host "✓ Secret neuropredict_secret_key created (auto-generated)" -ForegroundColor Green
}

# 2. Database Password
Create-Secret -SecretName "neuropredict_database_password" -Prompt "Database password" -IsPassword $true

# 3. Redis Password (optional)
$createRedis = Read-Host "Create Redis password secret? (y/n)"
if ($createRedis -eq "y" -or $createRedis -eq "Y") {
    Create-Secret -SecretName "neuropredict_redis_password" -Prompt "Redis password" -IsPassword $true
}

# 4. Grafana Admin Password
Create-Secret -SecretName "neuropredict_grafana_password" -Prompt "Grafana admin password" -IsPassword $true

Write-Host "`n✅ All secrets created successfully!`n" -ForegroundColor Green

Write-Host "Listing created secrets:"
docker secret ls | Select-String neuropredict

Write-Host "`n⚠ Important: Save these secrets in a secure password manager!" -ForegroundColor Yellow
Write-Host "⚠ Secrets cannot be retrieved once created.`n" -ForegroundColor Yellow

Write-Host "To use these secrets in production:"
Write-Host "  docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d"

