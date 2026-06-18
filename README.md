# Mocktelemetry for Learning

Mocktelemetry for Learning is a small learning project for understanding how a
vehicle telemetry software stack works before real hardware is ready.

The project simulates telemetry data, displays it in a dashboard, saves it to
CSV logs, defines status/alert rules, and provides reusable test scenarios.
It is intentionally beginner-friendly so each module can be studied, changed,
run, and tested one step at a time.

## Learning Goals

Use this project to practice:

- Python data generation and file I/O
- JSON telemetry data formats
- CSV logging
- JavaScript dashboard updates with `fetch`
- Basic alert/status rules
- Test data scenarios and edge cases
- Git branches, pull requests, and issue-based workflow
- Writing clear software documentation

## Current Scope

This project is focused on mock telemetry only. It does not connect to real
ESP32, Arduino, sensors, motor controllers, or BMS hardware yet.

Current modules:

- `telemetry/` - generates mock vehicle telemetry
- `dashboard/` - displays the latest telemetry values
- `logger/` - saves telemetry history to CSV
- `alert/` - defines status and severity rules
- `test-data/scenarios/` - reusable sample telemetry scenarios
- `docs/` - data format and status rule documentation

## Repository Structure

```text
mocktelemetry-for-learning/
├─ alert/
├─ dashboard/
├─ docs/
├─ logger/
├─ telemetry/
└─ test-data/
```

## Telemetry Fields

Each telemetry record uses these main fields:

| Field | Meaning |
| --- | --- |
| `timestamp` | Time when the telemetry record was generated. |
| `speed` | Vehicle speed in km/h. |
| `batteryVoltage` | Battery voltage in V. |
| `batteryPercent` | Battery percentage from 0 to 100. |
| `current` | Electrical current in A. |
| `power` | Electrical power in W. |
| `motorTemp` | Motor temperature in deg C. |
| `controllerTemp` | Controller temperature in deg C. |
| `status` | Alert/status value such as `NORMAL` or `LOW_BATTERY`. |

Detailed documentation:

- [Telemetry data format](docs/telemetry-data-format.md)
- [Status rules](docs/status-rules.md)

## Run Mock Telemetry

Run the mock telemetry generator:

```powershell
python telemetry/mock_telemetry.py
```

It writes:

- `test-data/latest_telemetry.json`
- `test-data/telemetry_history.json`
- `test-data/runs/run_<time>.json`

## Run Dashboard

Start the dashboard helper:

```powershell
.\start_dashboard.ps1
```

Then open:

```text
http://localhost:8000/dashboard/
```

The dashboard reads `test-data/latest_telemetry.json`.

## Run CSV Logger

Start mock telemetry first, then run:

```powershell
python logger/csv_logger.py
```

The logger reads `test-data/telemetry_history.json` and writes CSV files under:

```text
test-data/logs/
```

For a short check:

```powershell
python logger/csv_logger.py --max-records 5
```

## Use Sample Scenarios

Reusable scenario data lives in `test-data/scenarios/`:

- `normal_run.json`
- `low_battery.json`
- `overheating.json`

Run the logger with a scenario:

```powershell
python logger/csv_logger.py --source test-data/scenarios/low_battery.json --max-records 3
```

## Suggested Learning Exercises

Start small. Change one thing, run it, and observe the result.

1. Change `LOW_BATTERY_PERCENT` in `alert/status_rules.py`.
2. Add a new telemetry field such as `throttle`.
3. Display the new field in `dashboard/index.html` and `dashboard/app.js`.
4. Add the new field to `logger/csv_logger.py`.
5. Update `docs/telemetry-data-format.md`.
6. Create a new scenario file in `test-data/scenarios/`.
7. Commit the change on the related module branch and merge it into `main`.

## Definition of Done for This Learning Stage

Mock telemetry learning stage is complete when:

- mock telemetry generates changing JSON data
- dashboard displays the latest telemetry values
- logger saves multiple CSV records
- sample scenarios cover normal, low battery, and overheating cases
- status rules are documented and shared by the telemetry generator
- data format docs explain fields, units, status values, and module usage

This stage is complete. The next learning step is connecting mock software
concepts to real telemetry input such as ESP32 serial data.
