# راهنمای یکپارچه‌سازی - NeuroPredict-AI

## 📋 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [HL7 FHIR Integration](#hl7-fhir-integration)
3. [PACS Integration](#pacs-integration)
4. [EHR/HIS Integration](#ehrhis-integration)
5. [Medical Devices Integration](#medical-devices-integration)
6. [Configuration](#configuration)
7. [Testing](#testing)

---

## مقدمه

NeuroPredict-AI از استانداردهای باز برای یکپارچه‌سازی با سیستم‌های پزشکی استفاده می‌کند:

- **HL7 FHIR R4**: برای تبادل داده‌های بالینی
- **DICOM**: برای تصاویر پزشکی و PACS
- **REST API**: برای EHR/HIS integration
- **HL7 v2**: برای دستگاه‌های پزشکی (در حال توسعه)

---

## HL7 FHIR Integration

### Overview

FHIR (Fast Healthcare Interoperability Resources) استاندارد HL7 برای تبادل اطلاعات سلامت است.

### Supported Resources

- **Patient**: اطلاعات بیمار
- **Observation**: مشاهدات بالینی (نتایج آزمایش، علائم حیاتی)
- **DiagnosticReport**: گزارش‌های تشخیصی
- **ImagingStudy**: مطالعات تصویربرداری

### API Endpoints

#### Patient Resources

```bash
# دریافت Patient
GET /api/v1/fhir/Patient/{patient_id}

# ایجاد Patient
POST /api/v1/fhir/Patient
{
  "name": "John Doe",
  "birth_date": "1980-01-01",
  "gender": "male",
  "identifiers": []
}
```

#### Observation Resources

```bash
# جستجوی Observations
GET /api/v1/fhir/Observation?patient={patient_id}&code={code}

# ایجاد Observation
POST /api/v1/fhir/Observation
{
  "patient_id": "patient-123",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "33747-0",
      "display": "MMSE Score"
    }],
    "text": "MMSE Score"
  },
  "value": 28,
  "effective_datetime": "2024-01-15T10:00:00Z",
  "status": "final"
}
```

#### DiagnosticReport Resources

```bash
# جستجوی DiagnosticReports
GET /api/v1/fhir/DiagnosticReport?patient={patient_id}

# ایجاد DiagnosticReport
POST /api/v1/fhir/DiagnosticReport
{
  "patient_id": "patient-123",
  "status": "final",
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
      "code": "LAB",
      "display": "Laboratory"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "33747-0",
      "display": "Alzheimer's Risk Assessment"
    }]
  },
  "effective_datetime": "2024-01-15T10:00:00Z",
  "conclusion": "High risk of Alzheimer's disease",
  "results": []
}
```

#### Capability Statement

```bash
# دریافت CapabilityStatement
GET /api/v1/fhir/metadata
```

### FHIR Service Usage

```python
from app.services.integration.fhir_service import FHIRService

fhir_service = FHIRService(base_url="http://localhost:8000/fhir")

# ایجاد Patient Resource
patient = fhir_service.create_patient_resource(
    patient_id="patient-123",
    name="John Doe",
    birth_date="1980-01-01",
    gender="male"
)

# ایجاد Observation Resource
observation = fhir_service.create_observation_resource(
    observation_id="obs-123",
    patient_id="patient-123",
    code={"text": "MMSE Score"},
    value=28,
    effective_datetime="2024-01-15T10:00:00Z"
)
```

---

## PACS Integration

### Overview

PACS (Picture Archiving and Communication System) برای مدیریت تصاویر DICOM استفاده می‌شود.

### DICOM Operations

#### Query Studies

```bash
# جستجوی مطالعات
GET /api/v1/pacs/studies?patient_id={patient_id}&study_date={date}
```

#### Retrieve Study

```bash
# دریافت مطالعه
GET /api/v1/pacs/studies/{study_instance_uid}
```

#### Upload DICOM

```bash
# آپلود فایل DICOM
POST /api/v1/pacs/upload
Content-Type: multipart/form-data

file: <dicom_file>
patient_id: <patient_id>
study_description: <description>
```

#### Validate DICOM

```bash
# اعتبارسنجی فایل DICOM
POST /api/v1/pacs/validate
Content-Type: multipart/form-data

file: <dicom_file>
```

#### Modality Worklist

```bash
# دریافت Modality Worklist
GET /api/v1/pacs/worklist?patient_id={patient_id}&scheduled_date={date}
```

### PACS Service Usage

```python
from app.services.integration.pacs_service import PACSService

pacs_service = PACSService(pacs_server_url="http://pacs.example.com")

# جستجوی مطالعات
studies = pacs_service.query_patient_studies(
    patient_id="patient-123",
    study_date="20240115"
)

# دریافت مطالعه
datasets = pacs_service.retrieve_study("1.2.840.113619.2.55.3.123456")

# استخراج metadata
metadata = pacs_service.parse_dicom_metadata("/path/to/dicom/file.dcm")

# اعتبارسنجی
validation = pacs_service.validate_dicom_file("/path/to/dicom/file.dcm")
```

---

## EHR/HIS Integration

### Overview

EHR/HIS integration برای دریافت و ارسال داده‌های بالینی استفاده می‌شود.

### API Endpoints

#### Get Patient Data

```bash
# دریافت اطلاعات بیمار
GET /api/v1/ehr/patients/{patient_id}
```

#### Get Lab Results

```bash
# دریافت نتایج آزمایش
GET /api/v1/ehr/patients/{patient_id}/lab-results?start_date={date}&end_date={date}
```

#### Get Medications

```bash
# دریافت داروها
GET /api/v1/ehr/patients/{patient_id}/medications
```

#### Get Vital Signs

```bash
# دریافت علائم حیاتی
GET /api/v1/ehr/patients/{patient_id}/vital-signs?start_date={date}&end_date={date}
```

#### Sync Patient Data

```bash
# همگام‌سازی کامل اطلاعات بیمار
POST /api/v1/ehr/patients/{patient_id}/sync
```

#### Send Prediction to EHR

```bash
# ارسال نتیجه پیش‌بینی به EHR
POST /api/v1/ehr/patients/{patient_id}/predictions
{
  "disease_type": "alzheimer",
  "risk_level": "high",
  "risk_score": 0.85,
  "confidence": 0.92,
  "recommendations": [
    "Follow-up MRI in 6 months",
    "Cognitive assessment recommended"
  ]
}
```

### EHR Service Usage

```python
from app.services.integration.ehr_service import EHRService

ehr_service = EHRService(
    ehr_api_url="http://ehr.example.com/api",
    api_key="your-api-key"
)

# دریافت اطلاعات بیمار
patient_data = await ehr_service.get_patient_data("patient-123")

# دریافت نتایج آزمایش
lab_results = await ehr_service.get_patient_lab_results(
    patient_id="patient-123",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# همگام‌سازی کامل
sync_result = await ehr_service.sync_patient_data("patient-123")

# ارسال نتیجه پیش‌بینی
success = await ehr_service.send_prediction_result(
    patient_id="patient-123",
    prediction_result={
        "disease_type": "alzheimer",
        "risk_level": "high",
        "risk_score": 0.85
    }
)
```

---

## Medical Devices Integration

### Overview

یکپارچه‌سازی با دستگاه‌های پزشکی برای دریافت داده‌های real-time.

### Supported Protocols

- **DICOM Modality Worklist**: برای دریافت لیست کارهای برنامه‌ریزی شده
- **HL7 v2**: برای دستگاه‌های آزمایشگاهی (در حال توسعه)
- **REST API**: برای دستگاه‌های مدرن

### Implementation Status

- ✅ DICOM Modality Worklist
- ⏳ HL7 v2 (در حال توسعه)
- ⏳ Real-time Data Streaming (در حال توسعه)

---

## Configuration

### Environment Variables

```bash
# PACS Configuration
PACS_SERVER_URL=http://pacs.example.com
PACS_AE_TITLE=NEUROPREDICT

# EHR Configuration
EHR_API_URL=http://ehr.example.com/api
EHR_API_KEY=your-api-key

# FHIR Configuration
HL7_FHIR_ENDPOINT=http://fhir.example.com/fhir
HL7_FHIR_BASE_URL=http://localhost:8000/fhir
```

### Settings in config.py

```python
# Integration Settings
PACS_SERVER_URL: Optional[str] = None
PACS_AE_TITLE: str = "NEUROPREDICT"
EHR_API_URL: Optional[str] = None
EHR_API_KEY: Optional[str] = None
HL7_FHIR_ENDPOINT: Optional[str] = None
HL7_FHIR_BASE_URL: str = "http://localhost:8000/fhir"
```

---

## Testing

### FHIR Testing

```python
# Test FHIR Patient creation
def test_create_patient_resource():
    fhir_service = FHIRService()
    patient = fhir_service.create_patient_resource(
        patient_id="test-123",
        name="Test Patient",
        birth_date="1980-01-01",
        gender="male"
    )
    assert patient.resource_type == "Patient"
    assert patient.id == "test-123"
```

### PACS Testing

```python
# Test DICOM validation
def test_validate_dicom():
    pacs_service = PACSService()
    validation = pacs_service.validate_dicom_file("test.dcm")
    assert validation["valid"] == True
```

### EHR Testing

```python
# Test EHR sync
async def test_ehr_sync():
    ehr_service = EHRService(ehr_api_url="http://test-ehr.com")
    result = await ehr_service.sync_patient_data("patient-123")
    assert result["success"] == True
```

---

## Best Practices

### 1. Error Handling

همیشه خطاها را handle کنید:

```python
try:
    patient_data = await ehr_service.get_patient_data(patient_id)
except Exception as e:
    logger.error(f"Error fetching patient data: {e}")
    # Fallback logic
```

### 2. Timeout Configuration

برای درخواست‌های خارجی timeout تنظیم کنید:

```python
ehr_service = EHRService(
    ehr_api_url="http://ehr.example.com",
    timeout=30.0
)
```

### 3. Authentication

از API keys و tokens برای احراز هویت استفاده کنید:

```python
headers = {
    "Authorization": f"Bearer {api_key}"
}
```

### 4. Data Validation

همیشه داده‌های دریافتی را validate کنید:

```python
validation = pacs_service.validate_dicom_file(file_path)
if not validation["valid"]:
    raise ValueError("Invalid DICOM file")
```

---

## Troubleshooting

### مشکل: PACS Connection Failed

**راه‌حل:**
- بررسی کنید که PACS_SERVER_URL درست تنظیم شده است
- بررسی کنید که network connectivity وجود دارد
- بررسی کنید که DICOM ports باز هستند

### مشکل: EHR API Authentication Failed

**راه‌حل:**
- بررسی کنید که EHR_API_KEY درست است
- بررسی کنید که token منقضی نشده است
- بررسی کنید که permissions درست هستند

### مشکل: FHIR Resource Validation Failed

**راه‌حل:**
- بررسی کنید که تمام فیلدهای required وجود دارند
- بررسی کنید که format داده‌ها درست است
- از FHIR validator استفاده کنید

---

## منابع بیشتر

- [HL7 FHIR Documentation](https://www.hl7.org/fhir/)
- [DICOM Standard](https://www.dicomstandard.org/)
- [FHIR Python Library](https://github.com/nazrulworld/fhir.resources)
- [pydicom Documentation](https://pydicom.github.io/)

---

## پشتیبانی

برای سوالات و مشکلات:
- Integration Team: integration@neuropredict-ai.com
- Technical Support: support@neuropredict-ai.com

