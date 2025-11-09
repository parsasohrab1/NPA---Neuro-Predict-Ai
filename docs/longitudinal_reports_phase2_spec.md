## فاز ۲ گزارش‌های طولی – مشخصات تکمیلی

### 🎯 اهداف
- زمان‌بندی تولید گزارش‌های طولی (روزانه / هفتگی / ماهانه / بازه سفارشی).
- گزارش‌های مقایسه‌ای (Cohort) برای چند بیمار / گروه معیار.
- افزودن Heatmap و لایه‌های تصویری به خروجی گزارش.
- کارتابل مدیریت گزارش‌ها در داشبورد ادمین (قابل زمان‌بندی، فیلتر، دانلود چندفرمت).

---

### 1. زمان‌بندی (Scheduling)
#### الزامات
- تعریف Job بر اساس:
  - نوع گزارش (Summary، Cohort، Imaging Heatmap).
  - بازه زمانی گزارش (Rolling window یا fixed).
  - فرکانس: روزانه، هفتگی، ماهانه، خصوصی‌سازی با Cron-like expression.
  - مخاطب / مقصد: فقط ذخیره در سیستم یا ارسال ایمیلی (فاز آینده).
- نگهداری وضعیت Job (فعال، غیرفعال، آخرین اجرا، خطای آخر).
- ذخیره خروجی‌های هر اجرا در جدول `longitudinal_reports`.

#### پیشنهاد فنی
- استفاده از **FastAPI + APScheduler** (حالت lightweight) یا ادغام با Celery اگر در فازهای بعدی نیاز به کار صفی شود.
- ماژول `report_scheduler_service` برای:
  - ثبت و مدیریت job ها.
  - ثبت Execution log در جدول جداگانه `longitudinal_report_runs` (job_id، report_id، status، started_at، finished_at، error).
- Endpoint جدید:
  - `POST /api/v1/reports/schedules` ایجاد Job.
  - `GET /api/v1/reports/schedules` لیست job ها.
  - `PATCH /api/v1/reports/schedules/{id}` به‌روزرسانی/غیرفعال‌سازی.
  - `DELETE /api/v1/reports/schedules/{id}` حذف Job.

---

### 2. گزارش‌های مقایسه‌ای (Cohort Reporting)
#### الزامات
- تعریف Cohort بر اساس:
  - فیلترهای بیمار: سن، جنسیت، diagnosis، risk level، label های سفارشی.
  - انتخاب اپیزود خاص یا همه اپیزودهای فعال.
  - انتخاب متریک‌های مقایسه: MMSE، Amyloid، Risk score، progression score.
- مقایسه دو حالت:
  1. **Patient vs Cohort Average** برای یک بیمار.
  2. **Cohort vs Cohort** (مثلاً درمان A در برابر درمان B).
- خروجی شامل:
  - جدول مقایسه‌ای (Average، Median، Std، Trend slope).
  - نمودارهای side-by-side یا overlaid line chart.
  - تحلیل متنی خلاصه (مثلاً: “Patient MMSE 10% پایین‌تر از cohort”).

#### پیشنهاد فنی
- افزودن سرویس `reporting_cohort_service` که:
  - ورودی cohort filter و patient filter.
  - از کوئری‌های aggregate (SQLAlchemy) با GROUP BY استفاده کند.
  - داده‌ی آماده برای heatmap و نمودارها برگرداند.
- Schema جدید:
  - `CohortDefinition` با فیلدهای `age_range`, `gender`, `diagnosis`, `tags`, `custom_sql_filter`.

---

### 3. Heatmap و لایه‌های تصویری
#### الزامات
- تولید Heatmap از اختلاف میانگین متریک‌ها در سطح cohort (Matrix: metric x time bucket).
- برای MRI:
  - امکان الصاق Heatmap تصویری (difference overlay) به گزارش.
  - اشاره به مسیر فایل heatmap در گزارش (base64 یا PNG).

#### پیشنهاد فنی
- استفاده از `seaborn` یا `matplotlib` برای تولید heatmap تصویری در backend.
- ذخیره فایل (PNG) در `settings.REPORTS_DIR` و لینک‌دهی در summary JSON (`heatmap_image_path`).
- افزودن گزینه UI برای نمایش تصویر Heatmap در داشبورد.

---

### 4. ساختار داده و جداول
- `longitudinal_report_schedules`:
  - `id`, `episode_id`, `name`, `report_type`, `schedule_cron`, `cohort_filter`, `comparison_filter`, `status`, `created_by`.
- `longitudinal_report_runs`:
  - `id`, `schedule_id`, `report_id`, `status`, `error`, `started_at`, `finished_at`.
- به‌روزرسانی جدول `longitudinal_reports` برای نگهداری متادیتای cohort (`comparison_context`).

---

### 5. تغییرات API و Schema
- `LongitudinalReportCreate` به‌روزرسانی برای پشتیبانی از:
  - `report_type` (summary, cohort_patient_vs_average, cohort_vs_cohort).
  - `cohort_filters` (شیء شامل age_range, gender, diagnosis, tags).
  - `comparison_cohort_filters`.
- پاسخ API شامل:
  - `heatmap_path`, `charts_payload`, `comparison_summary`.
- Endpoint تکمیلی:
  - `GET /api/v1/longitudinal/reports/{id}/heatmap` برای دریافت PNG آماده نمایش.

---

### 6. UI داشبورد ادمین
- صفحه Reports → تب “Scheduled Reports” با امکان ساخت، فعال/غیرفعال‌سازی، اجرای دستی و مشاهده لاگ اجرا.
- فرم ساخت Schedule با فیلتر cohort/comparison و ساختار cron آماده.
- لیست job ها + آخرین اجرا + دکمه Run now + مشاهده Execution log.
- در Longitudinal Tracking:
  - نمایش Heatmap به‌صورت Modal تعاملی و دکمه دانلود.
  - دانلودهای جدید (Excel/PDF) و نمایش خلاصه مقایسه.

---

### 7. تست و QA
- تست‌های unit/integration برای:
  - ساخت و اجرای گزارش‌های cohort.
  - زمان‌بندی (mock زمان).
  - تولید heatmap و ذخیره فایل.
- تست UI: اطمینان از نمایش heatmap و مدیریت job در داشبورد.
- QA سناریوها:
  - بدون داده → پیام مناسب.
  - خطای تولید گزارش → ثبت در run log.
  - مقایسه cohort بدون patient → خطا کنترل‌شده.

---

### 8. مراحل اجرای فاز
1. پیاده‌سازی مدل‌ها و migration.
2. سرویس‌های backend (cohort report + heatmap + scheduler).
3. API و تست.
4. توسعه UI (Scheduled Reports + نمایش heatmap).
5. مستندسازی و راهنمای بهره‌برداری.

---

**آخرین به‌روزرسانی:** نوامبر 2025  
**مسئول:** تیم محصول NeuroPredict-AI

