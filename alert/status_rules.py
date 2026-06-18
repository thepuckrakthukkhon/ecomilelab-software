STATUS_SEVERITY = {
    "NORMAL": "normal",
    "LOW_BATTERY": "warning",
    "TEMP_WARM": "warning",
    "TEMP_HOT": "warning",
    "BATTERY_CRITICAL": "danger",
    "OVERHEATING": "danger",
    "TEMP_CRITICAL": "danger",
    "TEMP_SHUTDOWN": "danger",
    "RESTART_READY": "warning",
}

LOW_BATTERY_PERCENT = 20.0
CRITICAL_BATTERY_PERCENT = 5.0
TEMP_WARM_C = 60.0
TEMP_HOT_C = 70.0
OVERHEATING_C = 80.0
TEMP_CRITICAL_C = 90.0
RESTART_READY_SECONDS = 10


def get_status(
    battery_percent,
    motor_temp,
    controller_temp,
    motor_enabled=True,
    cooldown_seconds=0,
):
    hottest_temp = max(motor_temp, controller_temp)

    if not motor_enabled and cooldown_seconds >= RESTART_READY_SECONDS:
        return "RESTART_READY"
    if not motor_enabled:
        return "TEMP_SHUTDOWN"
    if battery_percent < CRITICAL_BATTERY_PERCENT:
        return "BATTERY_CRITICAL"
    if hottest_temp >= TEMP_CRITICAL_C:
        return "TEMP_CRITICAL"
    if hottest_temp >= OVERHEATING_C:
        return "OVERHEATING"
    if hottest_temp >= TEMP_HOT_C:
        return "TEMP_HOT"
    if hottest_temp >= TEMP_WARM_C:
        return "TEMP_WARM"
    if battery_percent < LOW_BATTERY_PERCENT:
        return "LOW_BATTERY"
    return "NORMAL"


def get_status_severity(status):
    return STATUS_SEVERITY.get(status, "danger")
