## داده و پایگاه داده

این سند وضعیت فعلی مدل داده، روابط، شاخص‌ها، مهاجرت‌ها، پشتیبان‌گیری/نگهداشت، و توصیه‌های عملکردی را خلاصه می‌کند. پایگاه داده پیشنهادی: PostgreSQL.


### موجودیت‌ها و روابط (Entities & Relations)
- User (`users`): نقش‌ها (`UserRole`)، وضعیت فعال/قفل، تاریخچه امنیتی.
- Patient (`patients`): مشخصات هویتی و جمعیت‌شناختی، دکتر مسئول.
- MedicalRecord (`medical_records`): نمرات شناختی، بیومارکرها، یادداشت‌ها، تاریخ ویزیت؛
  - رابطه: Many-to-One به Patient.
- ImagingStudy (`imaging_studies`): متادیتا تصویر (MRI/DICOM)، لینک به رکورد پزشکی؛
  - رابطه: Many-to-One به MedicalRecord.
- Prediction (`predictions`): نوع بیماری، نمرات ریسک/اطمینان، ویژگی‌ها/اهمیت‌ها (JSON)، گزارش؛
  - رابطه: Many-to-One به Patient و User (ایجادکننده).
- Longitudinal (Episode/Visit/Metric/Report/Alert …): ردیابی روند و هشدارها.
- AuditLog (`audit_logs`): ممیزی عملیات حساس.
- Product (`products`): مشخصات محصول، نسخه، `specs`/`metadata` (JSON)، وضعیت فعال.


### کلیدها و قیود (Keys & Constraints)
- کلیدهای اصلی: `id` عددی افزایشی.
- یکتایی‌های مهم: `users.email`, `users.username`, `patients.patient_id`.
- تمام روابط خارجی `ON DELETE` پیش‌فرض (حذف زنجیره‌ای فقط در برخی روابط مانند `medical_records.imaging_studies`).
- بازه‌های معنادار: نمرات ریسک/اعتماد در [0,1]، تاریخ تولد < امروز، تاریخ ویزیت معتبر.


### شاخص‌ها (Indexing)
- پیش‌فرض‌ها در کد: `index=True` روی کلیدها و تاریخ‌های پرتکرار (مثل `visit_date`).
- پیشنهادی تکمیلی (PostgreSQL):
  - `patients (patient_id, last_name, first_name)` برای جستجو.
  - `medical_records (patient_id, visit_date DESC)` برای آخرین رکورد.
  - `predictions (patient_id, created_at DESC)` برای گزارش‌های اخیر.
  - فیلدهای فیلتر پرتکرار: `products (is_active, name)`.
  - در صورت نیاز: ایندکس‌های جزئی/ترکیبی و GIN برای JSONB (در صورت مهاجرت).


### ضد N+1 و الگوهای کوئری
- استفاده از eager loading (`selectinload`) برای روابط متداول (نمونه: بارگذاری دکتر بیمار/سوابق/پیش‌بینی‌ها).
- صفحه‌بندی (`skip`, `limit`) و فیلتر/جستجو در سطح دیتابیس.
- کش نتایج خواندنی پرتکرار با TTL کوتاه (Redis) و بی‌اعتبارسازی هدفمند.


### نوع‌ها و JSON
- استفاده از `JSON` برای `input_features`/`feature_importance`/`specs`/`metadata` در حد نیاز.
- برای کوئری‌های پیچیده روی JSON، پیشنهاد مهاجرت به `JSONB` و ایندکس GIN.


### مهاجرت‌ها (Migrations)
- ابزار پیشنهادی: Alembic.
- قوانین:
  - مهاجرت افزایشی و برگشت‌پذیر (Downgrade) در محیط‌های غیرتولیدی؛ نسخه‌بندی شفاف.
  - تغییرات شکستن‌دار (Breaking) همراه با Migration Guide و پنجره قطع سرویس.
  - عدم حذف ستون بدون مسیر انتقال و زمان کنارگذاری (Deprecation Window).


### داده نمونه و اسکریپت‌ها
- مسیرهای موجود:
  - `backend/data/` و `NPA---Neuro-Predict-Ai/data/` برای داده‌های نمونه/تصاویر.
  - اسکریپت‌ها در `backend/scripts/` (تولید/آماده‌سازی/ارزیابی).


### پشتیبان‌گیری و بازیابی (Backup/Restore)
- پایگاه داده:
  - بکاپ زمان‌بندی‌شده (روزانه/ساعتی طبق سیاست)، رمزگذاری‌شده، تست دوره‌ای بازیابی (DR Drill).
  - نگهداشت نسخه‌ها بر اساس سیاست انطباق (مثلاً ۳۰/۹۰ روز).
- فایل‌ها (تصاویر/گزارش‌ها):
  - ذخیره‌سازی ایمن و پشتیبان رمزگذاری‌شده؛ مهاجرت به شیء-استور در تولید.


### نگهداشت و حریم خصوصی (Retention & Privacy)
- حداقل‌گرایی داده؛ نگهداشت مبتنی بر نیاز بالینی/قانونی.
- ناشناس‌سازی/پسودونیم‌سازی برای تحلیل/پژوهش؛ تفکیک محیط‌ها.
- مسیرهای DSR (درخواست‌های GDPR): استخراج/حذف با ممیزی و تأیید هویت قوی.


### کارایی و ظرفیت (Performance & Capacity)
- اهداف تاخیر CRUD: p95 ≤ 600ms؛ شاخص‌گذاری و eager loading.
- آپلود تصویر: اعتبارسنجی اولیه ≤ 2s برای ≤100MB؛ مسیر آسنکرون در فازهای بعد.
- پیش‌بینی: ≤ 2s (همگام MVP)؛ صف و Polling/Webhook در رشد بار.
- ظرفیت اولیه: 100 همزمان؛ قابلیت افزایش replica برای API.


### رشد و مقیاس (Scale & Growth)
- Read/Write Split و Replicaهای خواندنی در PostgreSQL (فازهای بعد).
- پارتیشن‌بندی جداول حجیم (مانند `imaging_studies`, `predictions`) بر اساس زمان/بیمار.
- صف پیام (RabbitMQ/Kafka) برای پردازش‌های سنگین (تصویر/مدل/گزارش).


### متغیرهای پیکربندی (نمونه)
- اتصال DB: `DATABASE_URL` (فرمت PostgreSQL)، حداکثر اتصال‌ها، Pool size/timeout.
- Redis: میزبان/پورت/DB برای کش و Rate Limiting.
- مسیرهای ذخیره فایل: `UPLOAD_DIR`, `DICOM_DIR`, `MRI_DIR`, `REPORTS_DIR`.


### بررسی‌های دوره‌ای
- سلامت ایندکس‌ها و پلن‌های کوئری (EXPLAIN/ANALYZE).
- رشد اندازه جداول/ایندکس‌ها و نیاز به آرشیو/پارتیشن.
- نرخ Hit کش و تنظیم TTL.
- ممیزی دسترسی‌ها و تمامیت داده (Consistent FK/unique، بدون یتیمی).


### ارجاع به کد
- مدل‌ها: `backend/app/models/*` (User, Patient, MedicalRecord, ImagingStudy, Prediction, Longitudinal*, AuditLog, Product)
- اسکیماها: `backend/app/schemas/*`
- API و الگوهای کش/صفحه‌بندی: `backend/app/api/*`
- تنظیمات/امنیت/کش: `backend/app/core/*`


