Get-CimInstance Win32_Process |
    Where-Object {
        $_.CommandLine -like "*telemetry\mock_telemetry.py*" -or
        $_.CommandLine -like "*http.server*8000*"
    } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Write-Host "Stopped mock telemetry and dashboard server."
