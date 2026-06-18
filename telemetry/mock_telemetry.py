import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from alert.status_rules import get_status

TEST_DATA_DIR = PROJECT_ROOT / "test-data"
RUNS_DIR = TEST_DATA_DIR / "runs"
LATEST_TELEMETRY_FILE = TEST_DATA_DIR / "latest_telemetry.json"
HISTORY_TELEMETRY_FILE = TEST_DATA_DIR / "telemetry_history.json"
RUN_ID = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
RUN_HISTORY_FILE = RUNS_DIR / f"run_{RUN_ID}.json"

MAX_SPEED = 45.0
BATTERY_CAPACITY_WH = 480.0
BATTERY_FULL_VOLTAGE = 54.0
BATTERY_EMPTY_VOLTAGE = 42.0
AMBIENT_TEMP = 30.0
AUX_CURRENT = 0.35
TEMP_SHUTDOWN_THRESHOLD = 75.0
TEMP_RESTART_THRESHOLD = 62.0
RESTART_DELAY_SECONDS = 10

route_profile = [
    {"name": "start_exit", "duration": 4, "throttle": 0.95, "brake": 0.0},
    {"name": "short_straight", "duration": 5, "throttle": 0.78, "brake": 0.0},
    {"name": "lift_before_corner", "duration": 2, "throttle": 0.12, "brake": 0.0},
    {"name": "corner_brake", "duration": 3, "throttle": 0.0, "brake": 0.62},
    {"name": "corner_roll", "duration": 3, "throttle": 0.18, "brake": 0.0},
    {"name": "corner_exit", "duration": 4, "throttle": 0.86, "brake": 0.0},
    {"name": "efficient_section", "duration": 7, "throttle": 0.34, "brake": 0.0},
    {"name": "medium_straight", "duration": 5, "throttle": 0.68, "brake": 0.0},
    {"name": "hard_brake", "duration": 3, "throttle": 0.0, "brake": 0.72},
    {"name": "slow_corner", "duration": 4, "throttle": 0.20, "brake": 0.0},
    {"name": "back_straight", "duration": 6, "throttle": 0.82, "brake": 0.0},
    {"name": "coast_to_line", "duration": 4, "throttle": 0.0, "brake": 0.0},
]

speed = 0.0
throttle = 0.0
brake = 0.0
battery_wh = BATTERY_CAPACITY_WH
motor_temp = AMBIENT_TEMP
controller_temp = AMBIENT_TEMP
profile_index = 0
profile_time_left = route_profile[0]["duration"]
motor_enabled = True
cooldown_seconds = 0
telemetry_history = []


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def get_route_input(index, time_left):
    if time_left <= 0:
        index = (index + 1) % len(route_profile)
        time_left = route_profile[index]["duration"]

    segment = route_profile[index]
    return index, time_left - 1, segment


def smooth_input(current_value, target_value, response):
    return current_value + (target_value - current_value) * response


def update_speed(current_speed, throttle_value, brake_value, battery_percent):
    if battery_percent <= 0.0:
        return clamp(current_speed - 1.6, 0.0, MAX_SPEED)

    low_speed_boost = 1.0 + max(0.0, 24.0 - current_speed) / 24.0 * 0.35
    motor_force = throttle_value * 5.6 * low_speed_boost
    brake_force = brake_value * 9.2
    rolling_drag = 0.12 + current_speed * 0.012
    aerodynamic_drag = (current_speed / MAX_SPEED) ** 2 * 2.2
    acceleration = motor_force - brake_force - rolling_drag - aerodynamic_drag
    natural_variation = random.uniform(-0.08, 0.08)
    return clamp(current_speed + acceleration + natural_variation, 0.0, MAX_SPEED)


def calculate_current(current_speed, previous_speed, throttle_value, brake_value, battery_percent):
    if battery_percent <= 0.0:
        return 0.0

    speed_load = (current_speed / MAX_SPEED) ** 2 * 13.0
    acceleration_load = max(current_speed - previous_speed, 0.0) * 4.0
    throttle_load = throttle_value * 7.5
    brake_reduction = 1.0 - brake_value * 0.75
    motor_current = (speed_load + acceleration_load + throttle_load) * brake_reduction
    current = AUX_CURRENT + motor_current
    return clamp(current + random.uniform(-0.25, 0.25), 0.0, 25.0)


def calculate_aux_current(battery_percent):
    if battery_percent <= 0.0:
        return 0.0
    return clamp(AUX_CURRENT + random.uniform(-0.04, 0.04), 0.0, 1.0)


def update_temperature(temp, current, speed_value, heat_factor, cool_factor):
    airflow_cooling = speed_value * 0.0008
    high_load_heat = max(current - 12.0, 0.0) * heat_factor * 0.8
    heat = current * heat_factor + high_load_heat
    cooling = max(temp - AMBIENT_TEMP, 0.0) * (cool_factor + airflow_cooling)
    return clamp(temp + heat - cooling, AMBIENT_TEMP, 105.0)


def sensor_noise(value, noise):
    return value + random.uniform(-noise, noise)


def quantize(value, step):
    return round(value / step) * step


def read_speed_sensor(real_speed):
    noisy_speed = sensor_noise(real_speed, 0.25)
    return clamp(quantize(noisy_speed, 0.1), 0.0, MAX_SPEED)


def read_voltage_sensor(open_circuit_voltage, current_value):
    voltage_sag = current_value * 0.035
    noisy_voltage = sensor_noise(open_circuit_voltage - voltage_sag, 0.04)
    return clamp(quantize(noisy_voltage, 0.01), BATTERY_EMPTY_VOLTAGE - 1.0, BATTERY_FULL_VOLTAGE)


def read_current_sensor(real_current):
    noisy_current = sensor_noise(real_current, 0.08)
    return clamp(quantize(noisy_current, 0.01), 0.0, 30.0)


def read_temp_sensor(real_temp):
    noisy_temp = sensor_noise(real_temp, 0.15)
    return clamp(quantize(noisy_temp, 0.1), AMBIENT_TEMP - 1.0, 110.0)


TEST_DATA_DIR.mkdir(exist_ok=True)
RUNS_DIR.mkdir(exist_ok=True)

while True:
    hottest_temp = max(motor_temp, controller_temp)

    if motor_enabled and hottest_temp >= TEMP_SHUTDOWN_THRESHOLD:
        motor_enabled = False
        cooldown_seconds = 0

    if not motor_enabled and hottest_temp <= TEMP_RESTART_THRESHOLD:
        cooldown_seconds += 1
    elif not motor_enabled:
        cooldown_seconds = 0

    if not motor_enabled and cooldown_seconds >= RESTART_DELAY_SECONDS:
        motor_enabled = True
        cooldown_seconds = 0
        profile_index = 0
        profile_time_left = route_profile[0]["duration"]

    battery_percent = (battery_wh / BATTERY_CAPACITY_WH) * 100.0
    profile_index, profile_time_left, route_segment = get_route_input(
        profile_index, profile_time_left
    )

    target_throttle = route_segment["throttle"]
    target_brake = route_segment["brake"]

    if battery_percent <= 0.0 or not motor_enabled:
        target_throttle = 0.0
        target_brake = 0.0

    throttle = clamp(smooth_input(throttle, target_throttle, 0.55), 0.0, 1.0)
    brake = clamp(smooth_input(brake, target_brake, 0.65), 0.0, 1.0)

    previous_speed = speed
    speed = update_speed(speed, throttle, brake, battery_percent)

    battery_percent = (battery_wh / BATTERY_CAPACITY_WH) * 100.0
    battery_voltage = BATTERY_EMPTY_VOLTAGE + (battery_percent / 100.0) * (
        BATTERY_FULL_VOLTAGE - BATTERY_EMPTY_VOLTAGE
    )

    if motor_enabled:
        current = calculate_current(speed, previous_speed, throttle, brake, battery_percent)
    else:
        current = calculate_aux_current(battery_percent)

    power = battery_voltage * current
    battery_wh = clamp(battery_wh - power / 3600.0, 0.0, BATTERY_CAPACITY_WH)
    battery_percent = (battery_wh / BATTERY_CAPACITY_WH) * 100.0

    motor_temp = update_temperature(motor_temp, current, speed, 0.075, 0.004)
    controller_temp = update_temperature(controller_temp, current, speed, 0.06, 0.005)

    if not motor_enabled:
        motor_temp = clamp(
            motor_temp - max(0.35, (motor_temp - AMBIENT_TEMP) * 0.025),
            AMBIENT_TEMP,
            105.0,
        )
        controller_temp = clamp(
            controller_temp - max(0.30, (controller_temp - AMBIENT_TEMP) * 0.022),
            AMBIENT_TEMP,
            105.0,
        )

    measured_current = read_current_sensor(current)
    measured_voltage = read_voltage_sensor(battery_voltage, measured_current)
    measured_speed = read_speed_sensor(speed)
    measured_motor_temp = read_temp_sensor(motor_temp)
    measured_controller_temp = read_temp_sensor(controller_temp)
    measured_power = measured_voltage * measured_current
    measured_battery_percent = clamp(
        quantize(sensor_noise(battery_percent, 0.04), 0.01),
        0.0,
        100.0,
    )

    status = get_status(
        measured_battery_percent,
        measured_motor_temp,
        measured_controller_temp,
        motor_enabled,
        cooldown_seconds,
    )

    telemetry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "runId": RUN_ID,
        "speed": round(measured_speed, 2),
        "batteryVoltage": round(measured_voltage, 2),
        "batteryPercent": round(measured_battery_percent, 2),
        "current": round(measured_current, 2),
        "power": round(measured_power, 2),
        "motorTemp": round(measured_motor_temp, 2),
        "controllerTemp": round(measured_controller_temp, 2),
        "status": status,
    }

    telemetry_history.append(telemetry)

    with open(LATEST_TELEMETRY_FILE, "w", encoding="utf-8") as file:
        json.dump(telemetry, file, indent=2, ensure_ascii=False)

    with open(HISTORY_TELEMETRY_FILE, "w", encoding="utf-8") as file:
        json.dump(telemetry_history, file, indent=2, ensure_ascii=False)

    with open(RUN_HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(telemetry_history, file, indent=2, ensure_ascii=False)

    print(
        f"{telemetry['timestamp']} speed={telemetry['speed']}km/h "
        f"battery={telemetry['batteryPercent']}% current={telemetry['current']}A "
        f"power={telemetry['power']}W motor={telemetry['motorTemp']}C "
        f"status={telemetry['status']}",
        flush=True,
    )

    time.sleep(1)
