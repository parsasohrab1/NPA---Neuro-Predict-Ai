# Quick Backend Restart Script
Write-Host "`n========================================" -ForegroundColor Yellow
Write-Host "  Restarting Backend Server" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Yellow

# Kill existing Python/uvicorn processes
Write-Host "Stopping existing backend processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.Path -like "*NPA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Change to backend directory
Set-Location -Path "backend"

# Start the backend
Write-Host "`nStarting backend server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs: http://localhost:8000/docs`n" -ForegroundColor Cyan

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

