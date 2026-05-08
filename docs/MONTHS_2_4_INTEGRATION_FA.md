# ماه ۲–۴ — یکپارچه‌سازی PACS / EHR / FHIR

این سند تغییرات قابل‌تحویل ماه‌های ۲ تا ۴ روی لایهٔ یکپارچه‌سازی NeuroPredict-AI با
سیستم‌های بالینی (PACS / EHR / FHIR) را خلاصه می‌کند. تمرکز این مرحله این است که
از «اسکلت‌های stub» به «adapterهای واقعی، مقاوم و آزمون‌شده» برسیم — نه افزودن
بار جدید، بلکه قابل‌اعتماد کردن بار موجود.

## ۱) خلاصه (TL;DR)

| محور | قبل | بعد |
| --- | --- | --- |
| **FHIR `GET /Patient/{id}`** | `501 Not Implemented` | خواندن از DB → `Patient` resource |
| **FHIR `GET /Patient` search** | همیشه bundle خالی | جستجو با `_id` و `identifier`، Bundle با `total` صحیح |
| **FHIR `GET /Observation`** | bundle ثابت خالی | استخراج Observationهای LOINC از `MedicalRecord` |
| **FHIR `GET /DiagnosticReport`** | bundle ثابت خالی | تولید گزارش از `Prediction` با اجزای ریسک Alzheimer/Parkinson |
| **FHIR `metadata`** | hard-coded ناقص | `CapabilityStatement` به‌روز با `searchParam`های واقعی |
| **EHR client** | بدون retry، بدون idempotency، خطاهای خام `httpx` | retry نمایی روی 5xx/timeout، عدم retry روی 4xx، `Idempotency-Key`، `EHRError` نرمالایز |
| **DICOM PHI** | بدون ابزار de-identification | ماژول `dicom_deidentify` بر اساس DICOM PS3.15 Annex E (basic profile) با گزارش audit |
| **پوشش تست** | تست ندارند | ۳ فایل unit-test (mappers, EHR resilience, DICOM redaction) که در CI اجرا می‌شوند |

## ۲) معماری لایهٔ FHIR

```
backend/app/
├── api/integration/fhir.py          ← endpointهای FHIR (read/search/metadata)
└── services/integration/
    ├── fhir_mappers.py              ← مدل DB → resource dict (واحدِ خالص، testable)
    └── fhir_service.py              ← (legacy) سازندهٔ resource بر مبنای fhir.resources
```

تصمیم طراحی: mapperها به‌صورت توابع خالص که **dict** برمی‌گردانند نوشته شدند، نه
نمونه‌های `fhir.resources`. دلایل:

1. **سرعت تست**: مقایسه‌ٔ dict کم‌هزینه است؛ نیاز به DB یا pydantic model نیست.
2. **استقلال نسخه**: به نسخهٔ خاصی از `fhir.resources` گره نخوردیم.
3. **سازگاری FastAPI**: مستقیم در پاسخ JSON قرار می‌گیرد.

`fhir_service.py` برای سازگاری عقب‌رو (backward-compat) باقی ماند ولی به‌مرور
deprecate خواهد شد.

### ۲.۱) منابع تحت پوشش

| Resource | Read | Search | Search Params |
| --- | --- | --- | --- |
| `Patient` | ✅ | ✅ | `_id`, `identifier` |
| `Observation` | — | ✅ | `subject` / `patient` |
| `DiagnosticReport` | ✅ | ✅ | `subject` / `patient`, `status` (placeholder) |
| `ImagingStudy` | — | ✅ (bundle خالی deterministe) | `subject`, `modality` |
| `CapabilityStatement` (`/metadata`) | ✅ | — | — |

### ۲.۲) نگاشت Observation

برای هر `MedicalRecord` فقط ستون‌های غیر-`None` به Observation تبدیل می‌شوند.
کدها از LOINC انتخاب شده‌اند تا برای exporters عمومی (Epic, Cerner, OpenEHR)
بدون تغییر قابل پذیرش باشند:

| Field DB | LOINC | Display | Unit (UCUM) |
| --- | --- | --- | --- |
| `mmse_score` | 72133-2 | Mini-Mental State Examination | `{score}` |
| `moca_score` | 72172-0 | Montreal Cognitive Assessment | `{score}` |
| `blood_pressure_systolic` | 8480-6 | Systolic BP | `mm[Hg]` |
| `blood_pressure_diastolic` | 8462-4 | Diastolic BP | `mm[Hg]` |
| `heart_rate` | 8867-4 | Heart rate | `/min` |
| `respiratory_rate` | 9279-1 | Respiratory rate | `/min` |
| `temperature` | 8310-5 | Body temperature | `Cel` |
| `oxygen_saturation` | 59408-5 | SpO2 | `%` |
| `weight` | 29463-7 | Body weight | `kg` |
| `height` | 8302-2 | Body height | `cm` |
| `bmi` | 39156-5 | BMI | `kg/m2` |
| `blood_glucose` | 1558-6 | Fasting glucose | `mg/dL` |
| `cholesterol_total` | 2093-3 | Cholesterol total | `mg/dL` |

افزودن سنجه‌های جدید فقط با اضافه‌کردن یک سطر در `_OBSERVATION_MAP` انجام می‌شود.

## ۳) مقاوم‌سازی EHR client

`backend/app/services/integration/ehr_service.py` بازنویسی شد. تغییرات کلیدی:

- **timeoutهای جدا**: `connect_timeout=5s`, `read_timeout=15s`, `pool=connect`.
- **retry نمایی** (پیش‌فرض ۳ تلاش، backoff ۰٫۵s × ۲^n):
  - retry می‌شود روی: `408`, `425`, `429`, `500`, `502`, `503`, `504`, و
    `httpx.TimeoutException` / `httpx.TransportError`.
  - retry نمی‌شود روی هر `4xx` دیگر (خطای کلاینت = باگ ما، نه گذرا).
- **`EHRError` یکپارچه**: همهٔ خطاها در یک نوع استثنا با `status_code` پسماند می‌نشیند.
- **`Idempotency-Key` خودکار** برای `send_prediction_result` تا retry در شبکهٔ پرنوسان
  باعث نوشتن دوبارهٔ پیش‌بینی نشود.
- **سیاست 404**: `get_patient_data` در 404 خطا نمی‌اندازد و `{}` برمی‌گرداند
  (سازگاری با کلاینت‌های فعلی).

این سرویس می‌تواند بدون `EHR_API_URL` (محیط dev) به‌صورت بی‌ضرر no-op شود و
empty list/dict برگرداند تا تست‌ها و health-checkهای بالادست خراب نشوند.

### ۳.۱) لاگ‌های قابل audit

تمام تلاش‌های retry و خطاها از طریق `logger = logging.getLogger(__name__)` لاگ
می‌شوند، یعنی stack موجود Loki/Promtail (Sprint 3-4) به‌صورت رایگان آن‌ها را
جمع‌آوری می‌کند.

## ۴) De-identification برای DICOM (PACS)

ماژول جدید `app/services/integration/dicom_deidentify.py`. زیرمجموعه‌ای محافظه‌کار
از **DICOM PS3.15 Annex E (Basic Application Confidentiality Profile)** را
پیاده می‌کند. پوشش:

- پاک‌سازی نام، تاریخ تولد، جنسیت، آدرس، تلفن، نژاد، شغل بیمار.
- جایگزینی `PatientID` با `replacement_id` (pseudo-anonymisation).
- حذف نام/آدرس/تلفن پزشک ارجاع‌دهنده، اپراتور، و مشخصات نهاد ارائه‌دهنده.
- پاک‌سازی متن‌های آزاد که اغلب PHI نشت می‌دهند: `StudyComments`,
  `SeriesComments`, `ImageComments`, `PatientComments`,
  `RequestedProcedureComments`.
- درج `PatientIdentityRemoved=YES` و `DeidentificationMethod` در dataset
  خروجی (مطابق DICOM PS3.3 §C.7.1.1).

> ⚠️ این ماژول **فقط metadata** را تمیز می‌کند. PHI «چاپ‌شده روی پیکسل» (burned-in
> annotation) باید جداگانه با OCR + masking پردازش شود — این کار در ماه‌های
> آینده روی صف قرار می‌گیرد.

ابزار یک `DeidentificationReport` ساختاریافته برمی‌گرداند (لیست‌های
`blanked / removed / replaced / missing`) که برای ثبت در audit log قابل serialize
شدن است.

## ۵) تست‌ها

| فایل | چه چیزی را تضمین می‌کند |
| --- | --- |
| `tests/unit/test_fhir_mappers.py` | شکل صحیح Patient/Observation/DiagnosticReport، fallback جنسیت ناشناخته، رد کردن مقادیر `None`، شکل Bundle searchset، CapabilityStatement |
| `tests/unit/test_ehr_service.py` | retry روی 5xx، عدم retry روی 4xx، `Idempotency-Key` در writeها، رفتار no-op وقتی URL خالی است |
| `tests/unit/test_dicom_deidentify.py` | جایگزینی/پاک‌سازی/حذف فیلدها، عدم mutate ورودی، خطا در `replacement_id` خالی، قواعد سفارشی |

تست‌ها در `tests/unit/` قرار گرفتند تا توسط CI اصلی اجرا شوند (CI پوشهٔ
`tests/integration` را عمداً نادیده می‌گیرد چون آن‌ها به DB/Service واقعی نیاز
دارند).

تست‌های mapper و de-identification هیچ شبکه/DBی نمی‌خواهند.
تست‌های EHR از `httpx.MockTransport` و `monkeypatch` استفاده می‌کنند تا
ایزوله بمانند.

## ۶) سازگاری و migration

- هیچ schema change در DB لازم نیست. Mapperها فقط می‌خوانند.
- `fhir_service.py` (legacy) همچنان قابل استفاده است؛ اما endpointها
  دیگر به آن نیاز ندارند.
- API external interfaceها سازگار با ورژن قبلی هستند به استثنای:
  - `GET /api/v1/fhir/Patient/{id}` که قبلاً 501 می‌داد، حالا 200/404.
  - `GET /api/v1/fhir/metadata` که حالا داینامیک است.

## ۷) پیشنهادات برای ماه‌های ۵–۶

### بازار/integration

- پیاده‌سازی واقعی PACS (C-FIND/C-MOVE/C-STORE) با `pynetdicom` و یک سرور تست
  (Orthanc) در docker compose.
- نوشتن یک ETL برای import متادیتای DICOM (پس از de-id) به جدول
  `imaging_studies` تا `GET /ImagingStudy` نتایج واقعی برگرداند.
- اضافه‌کردن FHIR `_format=xml` و paging (`_count`, `_offset`, `next`).
- پشتیبانی از HL7 v2 ADT^A04 (admission) → خلق Patient.

### قابلیت اطمینان

- circuit breaker (مثلاً `pybreaker`) دور `EHRService._request` تا EHR
  در حال downtime، کل request flow را گیر نیندازد.
- متریک‌های Prometheus برای retryها: counter `ehr_request_retries_total`
  و histogram `ehr_request_duration_seconds`.
- audit-log جداگانه روی هر `send_prediction_result` (همراه با hash
  payload) برای انطباق با مقررات HIPAA/GDPR.

### امنیت

- علاوه بر `Idempotency-Key`، اضافه‌کردن JWT-style signing روی payloadهای
  outbound به EHR.
- پیاده‌سازی pixel-level de-identification (مثل `presidio-image-redactor`).
- branch protection به‌روزرسانی روی `main`: required check جدید
  `Backend (lint, test, SAST)` تا تست‌های unit جدید gate شوند.

## ۸) فایل‌های افزوده/تغییریافته

```
backend/app/api/integration/fhir.py                          (rewrite)
backend/app/services/integration/fhir_mappers.py             (new)
backend/app/services/integration/ehr_service.py              (rewrite)
backend/app/services/integration/dicom_deidentify.py         (new)
backend/tests/unit/test_fhir_mappers.py                      (new)
backend/tests/unit/test_ehr_service.py                       (new)
backend/tests/unit/test_dicom_deidentify.py                  (new)
docs/MONTHS_2_4_INTEGRATION_FA.md                            (new — این سند)
```
