# EcoMileLab Software Specs v0.1

## 1. Goal

ระบบ Software ของ EcoMileLab มีหน้าที่รับข้อมูลจากรถ แสดงผลแบบ real-time และบันทึกข้อมูลการทดสอบ เพื่อนำไปวิเคราะห์ประสิทธิภาพ พลังงาน และความปลอดภัยของรถ

## 2. Scope

เวอร์ชันแรกของ software จะโฟกัสที่:

- Telemetry
- Dashboard
- Data Logging
- Basic Alert System
- Test Data / Mock Data

ยังไม่รวม:

- Mobile app
- Cloud system
- Login system
- Full motor control algorithm
- Hardware protocol ขั้นสุดท้าย

## 3. Main Modules

### 3.1 Telemetry

หน้าที่:

- รับข้อมูลจากรถหรือ mock data
- ตรวจว่า data format ถูกต้อง
- ส่งข้อมูลต่อให้ dashboard และ logger

ข้อมูลที่ต้องรับ:

- speed
- batteryVoltage
- batteryPercent
- current
- power
- motorTemp
- controllerTemp
- status
- timestamp

### 3.2 Dashboard

หน้าที่:

- แสดงข้อมูลรถแบบ real-time
- แสดงสถานะระบบ
- ใช้สีช่วยบอกความผิดปกติ

ค่าที่ต้องแสดง:

- Speed
- Battery %
- Battery Voltage
- Current
- Power
- Motor Temperature
- Controller Temperature
- Status

สีสถานะ:

- NORMAL = เขียว
- LOW_BATTERY = เหลือง
- OVERHEATING = ส้ม/แดง
- CRITICAL = แดง

### 3.3 Logger

หน้าที่:

- บันทึก telemetry ระหว่างการทดสอบ
- เก็บข้อมูลเป็นไฟล์สำหรับวิเคราะห์ย้อนหลัง

Format เริ่มต้น:

- CSV
- JSONL

กติกา:

- บันทึกอย่างน้อย 1 ครั้งต่อวินาที
- 1 test run = 1 log file
- ชื่อไฟล์ควรมีวันที่และเวลา

ตัวอย่างชื่อไฟล์:

```text
run_2026-06-17_2230.csv
```

### 3.4 Alert System

หน้าที่:

- ประเมินสถานะรถจากข้อมูล telemetry
- ส่งสถานะให้ dashboard แสดงผล

สถานะเริ่มต้น:

```text
NORMAL
LOW_BATTERY
OVERHEATING
BATTERY_CRITICAL
OVERHEATING_CRITICAL
```

เงื่อนไขเริ่มต้น:

```text
batteryPercent < 20       -> LOW_BATTERY
batteryPercent < 5        -> BATTERY_CRITICAL
motorTemp > 80            -> OVERHEATING
controllerTemp > 80       -> OVERHEATING
motorTemp > 85            -> OVERHEATING_CRITICAL
controllerTemp > 85       -> OVERHEATING_CRITICAL
```

## 4. Data Format

Prototype ใช้ JSON ก่อน

ตัวอย่าง:

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

## 5. Data Fields

| Field | Type | Unit | Description |
| --- | --- | --- | --- |
| timestamp | string | ISO time | เวลาที่ข้อมูลถูกสร้าง |
| speed | number | km/h | ความเร็วรถ |
| batteryVoltage | number | V | แรงดันแบตเตอรี่ |
| batteryPercent | number | % | เปอร์เซ็นต์แบตเตอรี่ |
| current | number | A | กระแสไฟฟ้า |
| power | number | W | กำลังไฟฟ้า |
| motorTemp | number | deg C | อุณหภูมิมอเตอร์ |
| controllerTemp | number | deg C | อุณหภูมิ controller |
| status | string | - | สถานะระบบ |

## 6. Mock Telemetry

ก่อน hardware พร้อม ให้ใช้ mock telemetry เพื่อจำลองข้อมูลรถ

Mock telemetry ต้องทำได้:

- สร้างข้อมูลใหม่ทุก 1 วินาที
- speed เปลี่ยนขึ้นลง
- batteryPercent ลดลงเรื่อย ๆ
- current เปลี่ยนตาม speed
- power คำนวณจาก voltage x current
- temperature เปลี่ยนตาม current
- status เปลี่ยนตาม condition

สูตรเริ่มต้น:

```text
speed = speed + random(-5, +5)
speed อยู่ระหว่าง 0 ถึง 45

batteryPercent = batteryPercent - random(0.1, 0.5)
batteryPercent อยู่ระหว่าง 0 ถึง 100

batteryVoltage = 42 + (batteryPercent / 100) * 12

current = 2 + (speed / 45) * 18 + random(-1, +1)
current อยู่ระหว่าง 0 ถึง 25

power = batteryVoltage * current
```

## 7. Repository Structure

```text
ecomilelab-software/
├─ telemetry/
├─ dashboard/
├─ logger/
├─ docs/
└─ test-data/
```

## 9. Definition of Done v0.1

ถือว่า Software v0.1 เสร็จเมื่อ:

- mock telemetry สร้างข้อมูลได้
- dashboard แสดงค่าจาก telemetry ได้
- logger บันทึกข้อมูลเป็น CSV ได้
- มี test-data อย่างน้อย 3 scenario
- มี documentation อธิบาย data format
- ทุกอย่างรันได้จาก README
