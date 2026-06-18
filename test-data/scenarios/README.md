# Telemetry Sample Scenarios

These JSON files provide predictable telemetry data for testing dashboard,
logger, and alert behavior before real vehicle hardware is available.

## Files

| File | Purpose |
| --- | --- |
| `normal_run.json` | Normal driving data with safe battery and temperature values. |
| `low_battery.json` | Low battery and battery critical states. |
| `overheating.json` | Warm, hot, and overheating temperature states. |

Each file is an array of telemetry objects using the same field names as
`telemetry/mock_telemetry.py`.

## Required Fields

Each record includes:

- `timestamp`
- `runId`
- `speed`
- `batteryVoltage`
- `batteryPercent`
- `current`
- `power`
- `motorTemp`
- `controllerTemp`
- `status`

## Use With Logger

Run the logger against one scenario file:

```powershell
python logger/csv_logger.py --source test-data/scenarios/low_battery.json --max-records 3
```

The logger will write the scenario records to a CSV file under
`test-data/logs/`.

## Use With Dashboard

To preview one scenario record in the dashboard, copy one object from a scenario
file into `test-data/latest_telemetry.json`, then open the dashboard.
