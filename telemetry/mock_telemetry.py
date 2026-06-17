import json
import random
import time
from datetime import datetime


speed = 0.0
battery_percent = 100.0
motor_temp = 30.0
controller_temp = 30.0


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def get_status(battery_percent, motor_temp, controller_temp):
    if battery_percent < 5.0:
        return "BATTERY_CRITICAL"
    if motor_temp > 85.0 or controller_temp > 85.0:
        return "OVERHEATING_CRITICAL"
    if battery_percent < 20.0:
        return "LOW_BATTERY"
    if motor_temp > 80.0 or controller_temp > 80.0:
        return "OVERHEATING"
    return "NORMAL"


while True:
    speed += random.uniform(-5.0, 5.0)
    speed = clamp(speed, 0.0, 45.0)

    battery_percent -= random.uniform(0.1, 0.5)
    battery_percent = clamp(battery_percent, 0.0, 100.0)

    battery_voltage = 42.0 + (battery_percent / 100.0) * 12.0

    current = 2.0 + (speed / 45.0) * 18.0 + random.uniform(-1.0, 1.0)
    current = clamp(current, 0.0, 25.0)

    power = battery_voltage * current

    motor_temp += current * 0.01 - 0.03
    controller_temp += current * 0.008 - 0.025

    motor_temp = clamp(motor_temp, 25.0, 100.0)
    controller_temp = clamp(controller_temp, 25.0, 100.0)

    status = get_status(battery_percent, motor_temp, controller_temp)

    telemetry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "speed": round(speed, 2),
        "batteryVoltage": round(battery_voltage, 2),
        "batteryPercent": round(battery_percent, 2),
        "current": round(current, 2),
        "power": round(power, 2),
        "motorTemp": round(motor_temp, 2),
        "controllerTemp": round(controller_temp, 2),
        "status": status,
    }

    print(json.dumps(telemetry, indent=2))
    time.sleep(1)
