# Mock Data Generator

โปรแกรมนี้ใช้สร้างข้อมูล telemetry จำลองจากรถไฟฟ้า เพื่อให้ทีม Dashboard, Data Logger และ Analysis ทดสอบระบบได้ก่อนมี ESP32 หรือ sensor จริง

## Requirements

- Node.js

## วิธีรัน

รันโหมดปกติ:

```bash
node mock-generator.js
```

เลือก mode:

```bash
node mock-generator.js normal
node mock-generator.js overheat
node mock-generator.js low_battery
node mock-generator.js sensor_error
```

ใส่ชื่อ session:

```bash
node mock-generator.js normal test_001
node mock-generator.js overheat race_2026_06_14
```

รันเพื่อทดสอบแค่ 5 packet:

```bash
node mock-generator.js normal test_001 --count 5
```

## Modes

| Mode | ความหมาย |
|---|---|
| `normal` | จำลองรถทำงานปกติ |
| `overheat` | จำลองอุณหภูมิสูง |
| `low_battery` | จำลองแบตเตอรี่ต่ำ |
| `sensor_error` | จำลอง sensor อ่านค่าผิดพลาด |

## JSON Format

```json
{
  "device_id": "esp32_01",
  "timestamp": 1700000000123,
  "session": "test_001",
  "data": {
    "current_A": 12.5,
    "temp_C": 45.2,
    "speed_rpm": 3200,
    "battery_V": 48.1
  },
  "status": "ok"
}
```

## Output

โปรแกรมจะ print JSON 1 packet ทุก 1 วินาทีใน terminal

## Embedded Dashboard

รัน dashboard ที่ฝังข้อมูลสดจาก mock generator:

```bash
node ../dashboard-server.js
```

จากนั้นเปิด:

```text
http://localhost:3000
```

API ที่ใช้กับ dashboard:

```text
GET /api/telemetry/latest
GET /api/telemetry/stream
```

## Status Rules

| Status | เงื่อนไข |
|---|---|
| `ok` | ข้อมูลปกติ |
| `warn` | อุณหภูมิเริ่มสูง หรือแบตต่ำ |
| `err` | อุณหภูมิสูงมาก หรือ sensor error |
