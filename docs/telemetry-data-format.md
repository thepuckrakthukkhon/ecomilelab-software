# EcoMileLab Telemetry Data Format

This document defines the telemetry JSON format used by the EcoMileLab
software prototype. The same format is shared by the mock telemetry generator,
dashboard, logger, and alert/status logic.

## Data Flow

```text
telemetry/mock_telemetry.py
  -> test-data/latest_telemetry.json
  -> test-data/telemetry_history.json
  -> dashboard/app.js
  -> logger/csv_logger.py
```

`latest_telemetry.json` contains one latest telemetry object. It is useful for
the dashboard because the dashboard only needs the newest values.

`telemetry_history.json` contains an array of telemetry objects. It is useful
for the logger because the logger can backfill records that were created before
the logger started.

## Telemetry Object

Each telemetry object represents one vehicle state snapshot.

```json
{
  "timestamp": "2026-06-18T13:15:10",
  "runId": "2026-06-18_13-15-07",
  "speed": 19.9,
  "batteryVoltage": 53.07,
  "batteryPercent": 99.71,
  "current": 25.07,
  "power": 1330.46,
  "motorTemp": 39.8,
  "controllerTemp": 37.7,
  "status": "NORMAL"
}
```

## Required Fields

| Field | Type | Unit | Required | Meaning |
| --- | --- | --- | --- | --- |
| `timestamp` | string | ISO local time | Yes | Time when this telemetry snapshot was generated. |
| `speed` | number | km/h | Yes | Vehicle speed. |
| `batteryVoltage` | number | V | Yes | Battery pack voltage. |
| `batteryPercent` | number | % | Yes | Estimated battery percentage from 0 to 100. |
| `current` | number | A | Yes | Electrical current draw. |
| `power` | number | W | Yes | Electrical power, usually `batteryVoltage * current`. |
| `motorTemp` | number | deg C | Yes | Motor temperature. |
| `controllerTemp` | number | deg C | Yes | Motor controller temperature. |
| `status` | string | - | Yes | Current system status for dashboard and alerts. |
| `runId` | string | - | Optional | Identifier for one mock telemetry run/session. |

## Status Values

| Status | Meaning | Typical trigger |
| --- | --- | --- |
| `NORMAL` | System is operating normally. | Battery and temperatures are in safe ranges. |
| `LOW_BATTERY` | Battery is getting low. | `batteryPercent < 20`. |
| `BATTERY_CRITICAL` | Battery is critically low. | `batteryPercent < 5`. |
| `TEMP_WARM` | Temperature is above normal but not dangerous yet. | Hottest temperature is at least 60 deg C. |
| `TEMP_HOT` | Temperature is high and should be watched closely. | Hottest temperature is at least 70 deg C. |
| `OVERHEATING` | Temperature is too high for normal operation. | Hottest temperature is at least 80 deg C. |
| `TEMP_CRITICAL` | Temperature is critically high. | Hottest temperature is at least 90 deg C. |
| `TEMP_SHUTDOWN` | Motor output is disabled for cooldown. | Mock motor shutdown has triggered. |
| `RESTART_READY` | System has cooled enough to restart. | Cooldown delay has completed. |

The exact thresholds live in `alert/status_rules.py` and are documented in
[`docs/status-rules.md`](status-rules.md). If those thresholds change, update
this document and any dashboard/logger assumptions in the same pull request.

## Module Responsibilities

### Telemetry

- Creates telemetry objects with the required fields.
- Writes the latest object to `test-data/latest_telemetry.json`.
- Appends each object to `test-data/telemetry_history.json`.
- Keeps field names stable so other modules do not break.

### Dashboard

- Reads `test-data/latest_telemetry.json`.
- Displays the latest speed, battery, current, power, temperatures, and status.
- Uses `status` to choose normal, warning, or danger visual styling.

### Logger

- Reads `test-data/telemetry_history.json` by default.
- Writes telemetry records to CSV under `test-data/logs/`.
- Keeps the CSV header aligned with the required fields.
- Avoids duplicating records with the same `timestamp`.

### Alert / Status Logic

- Converts telemetry values into a simple `status` string.
- Should keep status names stable for the dashboard and logger.
- Should document any threshold changes here.

## CSV Logger Output

The logger writes CSV columns in this order:

```csv
timestamp,speed,batteryVoltage,batteryPercent,current,power,motorTemp,controllerTemp,status
```

Example row:

```csv
2026-06-18T13:15:10,19.9,53.07,99.71,25.07,1330.46,39.8,37.7,NORMAL
```

This means that at `2026-06-18T13:15:10`, the vehicle was moving at
`19.9 km/h`, using about `1330.46 W`, with `99.71%` battery remaining, and the
system status was `NORMAL`.
