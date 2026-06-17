# EcoMileLab Software Spec v0.1

## Goal

EcoMileLab software receives vehicle telemetry, displays real-time status, and records test-run data for later efficiency analysis.

## Main Modules

- Telemetry Receiver: receives vehicle data.
- Dashboard: displays live vehicle state.
- Data Logger: stores telemetry as CSV.
- Alert System: classifies system status.

## Minimum Data Fields

| Field | Unit | Description |
| --- | --- | --- |
| timestamp | ISO time | Time the telemetry sample is created |
| speed | km/h | Vehicle speed |
| batteryVoltage | V | Battery pack voltage |
| batteryPercent | % | Estimated battery state of charge |
| current | A | Current draw |
| power | W | Electrical power, calculated from voltage and current |
| motorTemp | deg C | Motor temperature |
| controllerTemp | deg C | Motor controller temperature |
| status | text | NORMAL, LOW_BATTERY, OVERHEATING, or critical status |

## Temporary Data Format

Prototype telemetry uses JSON.

```json
{
  "timestamp": "2026-06-17T22:30:00",
  "speed": 32.5,
  "batteryVoltage": 48.2,
  "batteryPercent": 76,
  "current": 12.1,
  "power": 583.2,
  "motorTemp": 41,
  "controllerTemp": 38,
  "status": "NORMAL"
}
```

## Dashboard Requirements

The first dashboard should show:

- speed
- battery percent
- battery voltage
- current
- power
- motor temperature
- controller temperature
- status

## Logger Requirements

- Save one row per telemetry sample.
- Start with one sample per second.
- Store logs as CSV.
- One test run should create one file.

## Open Questions

- Will real telemetry use UART, CAN, Wi-Fi, BLE, or another protocol?
- What update rate is required: 1 Hz, 10 Hz, or faster?
- Which microcontroller will send the data?
- Will GPS be required?
- Should the dashboard run on a laptop, tablet, or in-vehicle display?
