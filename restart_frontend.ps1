# PowerShell script to restart the frontend development server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Frontend Restart Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find the frontend dev server process (usually on port 5173)
Write-Host "[1/3] Finding frontend processes on port 5173..." -ForegroundColor Yellow
$frontendPorts = netstat -ano | findstr ":5173"

if ($frontendPorts) {
    Write-Host "Found frontend server running:" -ForegroundColor Green
    Write-Host $frontendPorts
    
    # Extract PIDs
    $pids = $frontendPorts | ForEach-Object {
        if ($_ -match '\s+(\d+)\s*$') {
            $matches[1]
        }
    } | Select-Object -Unique
    
    Write-Host ""
    Write-Host "[2/3] Stopping frontend processes..." -ForegroundColor Yellow
    
    foreach ($pid in $pids) {
        try {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "  Stopping process $pid ($($process.ProcessName))..." -ForegroundColor White
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Write-Host "  ✓ Stopped" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "  ✗ Could not stop process $pid" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "Waiting 3 seconds for processes to terminate..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
} else {
    Write-Host "No frontend server found running on port 5173" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/3] Starting frontend server..." -ForegroundColor Yellow
Write-Host "Running: npm run dev" -ForegroundColor Cyan
Write-Host ""

# Change to admin-dashboard directory and start the server
Set-Location -Path "admin-dashboard"

# Start the dev server in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Frontend server is starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "The development server will open in a new window." -ForegroundColor White
Write-Host "Wait for the message: 'Local: http://localhost:5173/'" -ForegroundColor White
Write-Host ""
Write-Host "Once it's running, open your browser to:" -ForegroundColor Cyan
Write-Host "  http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

