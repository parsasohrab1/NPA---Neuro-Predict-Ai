## API Reference (خلاصه فارسی)

پیشوند نسخه: `/api/v1` (قابل تنظیم با `settings.API_V1_PREFIX`). احراز هویت: `Authorization: Bearer <token>`.


### Auth
- POST `/auth/login` → دریافت Token
  - body: `{ "username": string, "password": string }`
  - 200: `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }`


### Patients
- GET `/patients?skip=0&limit=50&search=...` → فهرست بیماران
- POST `/patients` (role: nurse+) → ایجاد بیمار
  - body: `PatientCreate` (شناسه بیمار یکتا)
- GET `/patients/{patient_id}` → جزییات بیمار (cache 10m)
- PUT `/patients/{patient_id}` (role: nurse+) → بروزرسانی
- DELETE `/patients/{patient_id}` (role: admin) → حذف
- GET `/patients/{patient_id}/medical-records` → سوابق بیمار


### Predictions
- POST `/predictions` (role: doctor+) → اجرای پیش‌بینی
  - body: `PredictionRequest` (بیمار باید رکورد اخیر داشته باشد)
  - 201: `PredictionResponse` (risk/confidence در [0,1], report_path اختیاری)


### Imaging
- POST `/imaging/dicom` (role: doctor+) → آپلود DICOM
  - form: `patient_id`, `medical_record_id?`, `file(.dcm)`
  - محدودیت اندازه: `settings.MAX_UPLOAD_SIZE` (پیش‌فرض 100MB)
- GET `/imaging/studies/{study_id}/preview` → تصویر پیش‌نمایش PNG
- GET `/imaging/studies/{study_id}/slices` → متادیتای اسلایس‌ها
- GET `/imaging/studies/{study_id}/slice/{slice_index}` → اسلایس مشخص


### Reports
- GET/POST مسیرهای گزارش (مطابق `reports.py`) – تولید/دانلود PDF (در صورت پیاده‌سازی)


### Longitudinal
- مسیرهای طولی (Episode/Visit/...) مطابق `longitudinal.py` – ردیابی روند و متریک‌ها


### Products
- GET `/products?is_active=true` → فهرست محصولات
- POST `/products` (role: admin) → ایجاد
- GET `/products/{product_id}` → جزییات
- PUT `/products/{product_id}` (role: admin) → بروزرسانی
- DELETE `/products/{product_id}` (role: admin) → حذف


### خطاها و ریت‌لیمیت
- خطاها: JSON با `detail` و `trace_id` (در صورت موجود)
- ریت‌لیمیت: هدرهای `X-RateLimit-*`, `Retry-After` در 429
- سیاست مسیرمحور: login/upload سفت‌تر از CRUD عادی


### قراردادها و اسکیماها
- Schemas: `backend/app/schemas/*` (Pydantic)
- مدل‌ها: `backend/app/models/*`
- استانداردها/نسخه‌بندی: `docs/API_STANDARDS_AND_VERSIONING_FA.md`, `docs/API_CONTRACTS_AND_ERROR_HANDLING_FA.md`


