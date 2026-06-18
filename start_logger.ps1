$python = "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Python was not found at $python"
    exit 1
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Start-Process -FilePath $python -ArgumentList "logger\csv_logger.py" -WorkingDirectory $projectRoot -WindowStyle Hidden

Write-Host "Telemetry logger started."
Write-Host "Logs are saved in test-data/logs."
