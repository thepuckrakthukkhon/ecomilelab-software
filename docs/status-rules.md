# EcoMileLab Status Rules

This document defines the prototype alert/status rules used by telemetry,
dashboard, and logger data.

The rules use these telemetry fields:

- `batteryPercent`
- `motorTemp`
- `controllerTemp`
- `status`

## Rule Order

Evaluate rules from top to bottom. The first matching rule becomes the status.

| Rule | Status | Severity | Condition |
| --- | --- | --- | --- |
| Motor is disabled and cooldown is complete | `RESTART_READY` | warning | `motor_enabled == false` and `cooldown_seconds >= 10` |
| Motor is disabled | `TEMP_SHUTDOWN` | danger | `motor_enabled == false` |
| Battery is critically low | `BATTERY_CRITICAL` | danger | `batteryPercent < 5` |
| Temperature is critically high | `TEMP_CRITICAL` | danger | `max(motorTemp, controllerTemp) >= 90` |
| Temperature is overheating | `OVERHEATING` | danger | `max(motorTemp, controllerTemp) >= 80` |
| Temperature is hot | `TEMP_HOT` | warning | `max(motorTemp, controllerTemp) >= 70` |
| Temperature is warm | `TEMP_WARM` | warning | `max(motorTemp, controllerTemp) >= 60` |
| Battery is low | `LOW_BATTERY` | warning | `batteryPercent < 20` |
| No alert condition | `NORMAL` | normal | all values are in normal range |

## Status Values

| Status | Meaning |
| --- | --- |
| `NORMAL` | System is operating normally. |
| `LOW_BATTERY` | Battery is low but not critical. |
| `BATTERY_CRITICAL` | Battery is critically low. |
| `TEMP_WARM` | Temperature is above normal. |
| `TEMP_HOT` | Temperature is high and should be watched closely. |
| `OVERHEATING` | Temperature is too high for normal operation. |
| `TEMP_CRITICAL` | Temperature is critically high. |
| `TEMP_SHUTDOWN` | Motor output is disabled for cooldown. |
| `RESTART_READY` | System has cooled enough to restart. |

## Module Usage

- `telemetry/mock_telemetry.py` calls `alert.status_rules.get_status(...)` and writes the result into the `status` field.
- `dashboard/app.js` consumes `status` and maps it to normal, warning, or danger styling.
- `logger/csv_logger.py` stores the `status` field in CSV so every record keeps its alert state.

Keep status names stable. If a status name changes, update dashboard styling,
sample scenarios, logger documentation, and this file in the same change.
