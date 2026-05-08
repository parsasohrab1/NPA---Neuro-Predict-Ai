# Scheduled PostgreSQL backup + retention (PowerShell)
# Run from repo root: .\scripts\backup_postgres_scheduled.ps1
# Env: POSTGRES_*, KEEP_DAYS, BACKUP_DIR

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$KeepDays = if ($env:KEEP_DAYS) { [int]$env:KEEP_DAYS } else { 14 }
$OutDir = if ($env:BACKUP_DIR) { $env:BACKUP_DIR } else { Join-Path $Root "backups\db" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

if (-not $env:POSTGRES_DB) { $env:POSTGRES_DB = "neuropredict_db" }
if (-not $env:POSTGRES_USER) { $env:POSTGRES_USER = "postgres" }
if (-not $env:POSTGRES_PASSWORD) { $env:POSTGRES_PASSWORD = "postgres" }
if (-not $env:POSTGRES_HOST) { $env:POSTGRES_HOST = "localhost" }
if (-not $env:POSTGRES_PORT) { $env:POSTGRES_PORT = "5432" }

Push-Location (Join-Path $Root "backend")
try {
    python scripts/backup_database.py backup --output-dir $OutDir
    python scripts/backup_database.py cleanup --output-dir $OutDir --keep-days $KeepDays
}
finally {
    Pop-Location
}

Write-Host "Backup + retention complete. Output: $OutDir"
