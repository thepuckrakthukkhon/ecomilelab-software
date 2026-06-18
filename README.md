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

## 3. Main Modules

### 3.1 Telemetry

หน้าที่:

- รับข้อมูลจากรถหรือ mock data
- ตรวจว่า data format ถูกต้อง
- ส่งข้อมูลต่อให้ dashboard และ logger

ข้อมูลที่ต้องรับ:

- timestamp
- speed
- batteryVoltage
- batteryPercent
- current
- power
- motorTemp
- controllerTemp
- status

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

### 3.3 Logger

หน้าที่:

- บันทึก telemetry ระหว่างการทดสอบ
- เก็บข้อมูลเป็นไฟล์สำหรับวิเคราะห์ย้อนหลัง
- เตรียมข้อมูลให้ทีมใช้ดู performance หลังจบรอบทดสอบ

### 3.4 Alert System

หน้าที่:

- ประเมินสถานะรถจากข้อมูล telemetry
- ส่งสถานะให้ dashboard แสดงผล
- ช่วยให้ทีมเห็นความผิดปกติได้เร็วขึ้น

สถานะเริ่มต้น:

- NORMAL
- LOW_BATTERY
- OVERHEATING
- BATTERY_CRITICAL
- OVERHEATING_CRITICAL

## 4. Data Format

Prototype ใช้ JSON เป็น format หลักในช่วงแรก เพื่อให้อ่านง่าย ทดสอบง่าย และเชื่อมต่อกับ dashboard/logger ได้เร็ว

ข้อมูล telemetry หนึ่งชุดควรแทนสถานะของรถ ณ เวลานั้น และต้องมี field ตามที่กำหนดในหัวข้อ Data Fields

Detailed data format documentation is in
[`docs/telemetry-data-format.md`](docs/telemetry-data-format.md).
Status rules are documented in [`docs/status-rules.md`](docs/status-rules.md).

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

- สร้างข้อมูลใหม่เป็นช่วงเวลา
- speed เปลี่ยนขึ้นลงได้
- batteryPercent ลดลงได้
- current เปลี่ยนตามสภาพการวิ่ง
- power คำนวณจาก voltage และ current
- temperature เปลี่ยนตาม current
- status เปลี่ยนตาม condition

เป้าหมายของ mock telemetry คือให้ทีม software พัฒนา dashboard, logger และ alert system ได้โดยไม่ต้องรอรถจริง

## 7. Repository Structure

```text
ecomilelab-software/
├─ telemetry/
├─ dashboard/
├─ logger/
├─ docs/
└─ test-data/
```

## 8. Definition of Done v0.1

ถือว่า Software v0.1 เสร็จเมื่อ:

- mock telemetry สร้างข้อมูลได้
- dashboard แสดงค่าจาก telemetry ได้
- logger บันทึกข้อมูลได้
- มี test-data สำหรับทดสอบระบบ
- มี documentation อธิบาย data format
- ทุกอย่างรันได้จากคำอธิบายใน README

## 9. Running the CSV Logger

Start mock telemetry first so `test-data/telemetry_history.json` is updated:

```powershell
python telemetry/mock_telemetry.py
```

In another terminal, start the logger:

```powershell
python logger/csv_logger.py
```

The logger appends telemetry records from `test-data/telemetry_history.json` to
`test-data/logs/telemetry_<run-time>.csv`. If you start the logger after mock
telemetry has already been running, it backfills the records already in history
and then keeps adding new records.
Each row includes:

- timestamp
- speed
- batteryVoltage
- batteryPercent
- current
- power
- motorTemp
- controllerTemp
- status

For a short local check, stop after a fixed number of records:

```powershell
python logger/csv_logger.py --max-records 5
```

## 10. Sample Telemetry Scenarios

Reusable scenario data lives in `test-data/scenarios/`.

- `normal_run.json`
- `low_battery.json`
- `overheating.json`

Use a scenario with the logger:

```powershell
python logger/csv_logger.py --source test-data/scenarios/low_battery.json --max-records 3
```
