$python = "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Python was not found at $python"
    exit 1
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -like "*telemetry\mock_telemetry.py*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Start-Process -FilePath $python -ArgumentList "telemetry\mock_telemetry.py" -WorkingDirectory $projectRoot -WindowStyle Hidden

$serverRunning = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (-not $serverRunning) {
    Start-Process -FilePath $python -ArgumentList "-m", "http.server", "8000" -WorkingDirectory $projectRoot -WindowStyle Hidden
}

Start-Sleep -Seconds 1
Start-Process "http://localhost:8000/dashboard/"

Write-Host "Dashboard started: http://localhost:8000/dashboard/"
Write-Host "Each run is saved in test-data/runs."
