# راهنمای یکپارچه‌سازی HL7 v2 - NeuroPredict-AI

## 📋 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [HL7 v2 Message Types](#hl7-v2-message-types)
3. [API Endpoints](#api-endpoints)
4. [Message Examples](#message-examples)
5. [Device Streaming](#device-streaming)
6. [Configuration](#configuration)

---

## مقدمه

HL7 v2 یک استاندارد قدیمی‌تر از FHIR است که هنوز در بسیاری از سیستم‌های پزشکی و دستگاه‌ها استفاده می‌شود. NeuroPredict-AI از HL7 v2 برای یکپارچه‌سازی با دستگاه‌های پزشکی استفاده می‌کند.

### Supported Message Types

- **ADT^A01**: Admit Patient
- **ORU^R01**: Observation Result
- **Lab Results**: Laboratory test results
- **Vital Signs**: Real-time vital signs data

---

## HL7 v2 Message Types

### ADT^A01 - Admit Patient

Message برای پذیرش بیمار:

```
MSH|^~\&|NEUROPREDICT|HOSPITAL|LAB|LAB|20240115100000||ADT^A01^ADT_A01|MSG001|P|2.5
EVN|A01|20240115100000|||DOCTOR^ADMITTING
PID|1||PATIENT123||DOE^JOHN^MIDDLE||19800101|M|||
PV1|1|I|ICU^ICU^01|||DOCTOR^ADMITTING|||SUR||||1|||DOCTOR^ADMITTING||20240115100000|||
```

### ORU^R01 - Observation Result

Message برای نتایج مشاهده:

```
MSH|^~\&|NEUROPREDICT|HOSPITAL|LAB|LAB|20240115100000||ORU^R01^ORU_R01|MSG002|P|2.5
PID|1||PATIENT123|||||||
OBR|1|OBS001||8480-6^Systolic BP||||20240115100000||||||||||F||||||
OBX|1|NM|8480-6^Systolic BP||120|mmHg||||F|||20240115100000
```

---

## API Endpoints

### Create Admit Message

```bash
POST /api/v1/hl7v2/admit
Content-Type: application/json

{
  "patient_id": "PATIENT123",
  "patient_name": "DOE^JOHN^MIDDLE",
  "birth_date": "19800101",
  "gender": "M",
  "admission_date": "20240115100000",
  "admitting_doctor": "DOCTOR^ADMITTING"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "MSH|^~\\&|...",
  "message_type": "ADT^A01"
}
```

### Create Observation Message

```bash
POST /api/v1/hl7v2/observation
Content-Type: application/json

{
  "patient_id": "PATIENT123",
  "observation_id": "OBS001",
  "observation_code": "8480-6",
  "observation_value": "120",
  "observation_units": "mmHg",
  "observation_date": "20240115100000",
  "status": "F"
}
```

### Create Lab Result Message

```bash
POST /api/v1/hl7v2/lab-result
Content-Type: application/json

{
  "patient_id": "PATIENT123",
  "test_code": "33747-0",
  "test_name": "MMSE Score",
  "result_value": "28",
  "units": "score",
  "reference_range": "24-30",
  "result_status": "F"
}
```

### Create Vital Signs Message

```bash
POST /api/v1/hl7v2/vital-signs
Content-Type: application/json

{
  "patient_id": "PATIENT123",
  "vital_signs": {
    "blood_pressure": {
      "systolic": 120,
      "diastolic": 80
    },
    "heart_rate": 72,
    "temperature": 98.6,
    "respiratory_rate": 16,
    "oxygen_saturation": 98
  }
}
```

### Parse Message

```bash
POST /api/v1/hl7v2/parse
Content-Type: application/json

{
  "message": "MSH|^~\\&|NEUROPREDICT|HOSPITAL|LAB|LAB|20240115100000||ORU^R01^ORU_R01|MSG002|P|2.5\rPID|1||PATIENT123|||||||\rOBR|1|OBS001||8480-6^Systolic BP||||20240115100000|||||||||||F||||||\rOBX|1|NM|8480-6^Systolic BP||120|mmHg||||F|||20240115100000\r"
}
```

**Response:**
```json
{
  "status": "success",
  "valid": true,
  "errors": [],
  "segments": [...],
  "patient_info": {
    "patient_id": "PATIENT123",
    "name": "...",
    "birth_date": "...",
    "gender": "..."
  },
  "observations": [...]
}
```

### Validate Message

```bash
POST /api/v1/hl7v2/validate
Content-Type: application/json

{
  "message": "MSH|^~\\&|..."
}
```

### Send Message

```bash
POST /api/v1/hl7v2/send
Content-Type: application/json

{
  "message": "MSH|^~\\&|...",
  "destination": "http://hl7-server.example.com"
}
```

---

## Message Examples

### Example 1: Admit Patient

```python
from app.services.integration.hl7v2_service import HL7v2Service

hl7v2_service = HL7v2Service()

message = hl7v2_service.create_admit_message(
    patient_id="PATIENT123",
    patient_name="DOE^JOHN^MIDDLE",
    birth_date="19800101",
    gender="M",
    admission_date="20240115100000",
    admitting_doctor="DOCTOR^ADMITTING"
)

print(message.to_string())
```

### Example 2: Lab Result

```python
message = hl7v2_service.create_lab_result_message(
    patient_id="PATIENT123",
    test_code="33747-0",
    test_name="MMSE Score",
    result_value="28",
    units="score",
    reference_range="24-30",
    result_status="F"
)
```

### Example 3: Vital Signs

```python
message = hl7v2_service.create_vital_signs_message(
    patient_id="PATIENT123",
    vital_signs={
        "blood_pressure": {"systolic": 120, "diastolic": 80},
        "heart_rate": 72,
        "temperature": 98.6,
        "respiratory_rate": 16,
        "oxygen_saturation": 98
    }
)
```

---

## Device Streaming

### Start Stream

```bash
POST /api/v1/devices/stream/start
Content-Type: application/json

{
  "device_id": "DEVICE001",
  "device_type": "vital_signs_monitor",
  "device_url": "http://device.example.com",
  "interval": 1.0
}
```

### Stop Stream

```bash
POST /api/v1/devices/stream/stop/DEVICE001
```

### Get Stream Status

```bash
GET /api/v1/devices/stream/status/DEVICE001
```

### List Active Streams

```bash
GET /api/v1/devices/stream/list
```

### WebSocket Streaming

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/devices/stream/DEVICE001');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Device data:', data);
};
```

---

## Configuration

### Environment Variables

```bash
# HL7 v2 Configuration
HL7_SERVER_URL=http://hl7-server.example.com
HL7_AE_TITLE=NEUROPREDICT
```

### Settings in config.py

```python
HL7_SERVER_URL: Optional[str] = None
HL7_AE_TITLE: str = "NEUROPREDICT"
```

---

## Supported Device Types

- `vital_signs_monitor`: Vital signs monitoring devices
- `lab_analyzer`: Laboratory analyzers
- `imaging_device`: Medical imaging devices
- `respiratory_device`: Respiratory devices
- `cardiac_monitor`: Cardiac monitoring devices

---

## Best Practices

### 1. Message Validation

همیشه messages را قبل از ارسال validate کنید:

```python
is_valid, errors = message.validate()
if not is_valid:
    # Handle errors
    pass
```

### 2. Error Handling

خطاها را handle کنید:

```python
try:
    message = hl7v2_service.create_observation_message(...)
except Exception as e:
    logger.error(f"Error creating message: {e}")
```

### 3. Message Formatting

از separators درست استفاده کنید:

```python
# Field separator: |
# Component separator: ^
# Repetition separator: ~
# Escape character: \
# Subcomponent separator: &
```

### 4. Timestamp Format

از فرمت درست timestamp استفاده کنید:

```python
# Format: YYYYMMDDHHMMSS
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
```

---

## Troubleshooting

### مشکل: Invalid Message Format

**راه‌حل:**
- بررسی کنید که separators درست هستند
- بررسی کنید که تمام فیلدهای required وجود دارند
- از validate endpoint استفاده کنید

### مشکل: Device Connection Failed

**راه‌حل:**
- بررسی کنید که device_url درست است
- بررسی کنید که network connectivity وجود دارد
- بررسی کنید که device در دسترس است

### مشکل: WebSocket Disconnection

**راه‌حل:**
- بررسی کنید که device stream فعال است
- بررسی کنید که network connection پایدار است
- از reconnection logic استفاده کنید

---

## منابع بیشتر

- [HL7 v2 Documentation](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=185)
- [HL7 v2 Message Structure](https://www.hl7.org/fhir/v2/)
- [MLLP Protocol](https://www.hl7.org/documentcenter/public_temp_2E58C1F9-1C23-BA17-0CDE7B2B0B5B6C7E/wg/inm/mllp_transport_specification.PDF)

---

## پشتیبانی

برای سوالات و مشکلات:
- Integration Team: integration@neuropredict-ai.com
- Technical Support: support@neuropredict-ai.com

