# 🧭 Longitudinal Tracking – Data Model & API Design

این سند نیازمندی‌ها و طراحی فاز اول پیاده‌سازی ماژول ردیابی طولی بیماران را مشخص می‌کند.

---

## 🎯 اهداف
- ثبت نقاط زمانی متعدد برای بیماران (Clinical + Imaging + Prediction).
- تحلیل روند شناختی، بیومارکر و MRI.
- محاسبه سرعت پیشرفت بیماری و تولید هشدار.
- فراهم‌کردن داده موردنیاز برای تایم‌لاین و نمودارهای روند در UI.

---

## 🗄️ طراحی داده

### 1. جدول `longitudinal_episodes`
- `id` (PK)
- `patient_id` → ForeignKey `patients.id`
- `title` (مثلاً “Early Diagnosis Program 2024”)
- `start_date`, `end_date` (nullable)
- `status` (active, completed, archived)
- `created_at`, `updated_at`

> هر بیمار می‌تواند چند اپیزود ردیابی داشته باشد (مطابق پروژه یا مطالعه بالینی).

### 2. جدول `longitudinal_visits`
- `id` (PK)
- `episode_id` → ForeignKey `longitudinal_episodes.id`
- `medical_record_id` (nullable) → ارتباط با `medical_records`
- `imaging_study_id` (nullable) → ارتباط با `imaging_studies`
- `prediction_id` (nullable) → ارتباط با `predictions`
- `visit_date` (datetime)
- `visit_type` (baseline, followup, therapy, imaging, lab)
- `notes` (Text)
- `progression_score` (optional float 0-1 برای شاخص پیشرفت)
- `created_at`, `updated_at`

### 3. جدول `longitudinal_metrics`
- `id` (PK)
- `visit_id` → ForeignKey `longitudinal_visits.id`
- `metric_type` (enum: `cognitive`, `biomarker`, `imaging`, `functional`)
- `metric_key` (مثلاً `mmse`, `moca`, `hippocampal_volume`)
- `metric_value` (float / json)
- `unit` (اختیاری)
- `z_score` (برای نرمال‌سازی)
- `created_at`

> این جدول اجازه می‌دهد داده‌های موجود `medical_records` یا استخراج‌های جدید را نسخه‌برداری کنیم تا نمودار روند سریعاً قابل محاسبه باشد.

### 4. جدول `longitudinal_alerts` (فاز ۲)
- `id`, `episode_id`, `visit_id`
- `alert_type` (progression_speed, sudden_change, imaging_drift, **combined_heatmap**)
- `severity` (low/medium/high)
- `trigger_payload` (JSON شامل متریک‌های مشارکت‌کننده)
- `message`, `created_at`, `acknowledged_at`, `resolved_by`

### 5. جدول `longitudinal_reports` (فاز گزارش‌های طولی)
- `id`, `episode_id`
- `report_type` (summary، cohort و ...)
- `format` (`xlsx`, `pdf`)
- `start_date`, `end_date`
- `file_path`, `pdf_path`
- `summary` (JSON از آمار متریک‌ها و بازه زمانی)
- `status` (completed, failed)
- `created_at`, `created_by`

---

## 🧠 سرویس‌ها و Aggregation

### Service: `LongitudinalTrackingService`
- `create_episode(patient_id, payload)`
- `add_visit(episode_id, payload)` → همگام‌سازی با `medical_records` / `imaging_studies`
- `record_metrics(visit_id, metrics[])`
- `get_episode_summary(patient_id, episode_id)` → شامل روند امتیازها، سرعت پیشرفت، نقاط کلیدی.
- `compare_imaging(visit_a, visit_b)` → خروجی برای UI (تولید thumbnail، heatmap، diff overlays)
- `create_report(episode_id, start_date, end_date, format)` → تولید summary JSON + فایل Excel/PDF
- `list_reports(episode_id)` و `get_report(report_id)` → دانلود فایل و نمایش metadata
- `generate_combined_alert(episode_id, visit_id)` → ایجاد هشدار ترکیبی در صورت عبور آستانه‌های چند متریک
- `get_heatmap_layers(report_id)` → بازگرداندن لایه‌های heatmap برای UI (MRI، Biomarker، AI drift)

### Service: `LongitudinalReportScheduler`
- `create_schedule(episode_id, payload)` → شامل cron، نوع گزارش، قالب
- `toggle_schedule(schedule_id, enabled)` → فعال/غیرفعال‌سازی
- `run_now(schedule_id)` → اجرای دستی و بازگرداندن شناسه run
- `list_runs(schedule_id, limit)` → تاریخچه اجرا با وضعیت و پیام خطا

### Metric Aggregation
- روند زمانی: گروه‌بندی بر اساس `metric_key`.
- سرعت پیشرفت: محاسبه slope در بازه زمانی (linear regression ساده یا اختلاف).
- نرمال‌سازی: استفاده از `metric_value` و `z_score`.

---

## 🌐 API طراحی پیشنهادی (نسخه اولیه)

| روش | مسیر | توضیح |
|-----|------|--------|
| `GET` | `/api/v1/longitudinal/{patient_id}/episodes` | لیست اپیزودها |
| `POST` | `/api/v1/longitudinal/{patient_id}/episodes` | ایجاد اپیزود جدید |
| `GET` | `/api/v1/longitudinal/episodes/{episode_id}` | خلاصه episode با visits و metrics |
| `POST` | `/api/v1/longitudinal/episodes/{episode_id}/visits` | افزودن visit |
| `POST` | `/api/v1/longitudinal/visits/{visit_id}/metrics` | ثبت مجموعه متریک |
| `GET` | `/api/v1/longitudinal/episodes/{episode_id}/timeline` | داده آماده برای تایم‌لاین |
| `GET` | `/api/v1/longitudinal/episodes/{episode_id}/trend?metric=mmse` | نمودار روند یک متریک |
| `GET` | `/api/v1/longitudinal/episodes/{episode_id}/comparison?visit_a=&visit_b=` | مقایسه دو visit (MRI diff) |
| `GET` | `/api/v1/longitudinal/episodes/{episode_id}/progression` | خلاصه سرعت پیشرفت متریک‌های کلیدی |
| `GET` | `/api/v1/longitudinal/episodes/{episode_id}/alerts` | هشدارهای فعال اپیزود |
| `POST` | `/api/v1/longitudinal/alerts/{alert_id}/acknowledge` | تأیید هشدار |
| `POST` | `/api/v1/longitudinal/episodes/{episode_id}/reports` | تولید گزارش دوره‌ای |
| `GET` | `/api/v1/longitudinal/episodes/{episode_id}/reports` | لیست گزارش‌های ذخیره‌شده |
| `GET` | `/api/v1/longitudinal/reports/{report_id}/download?variant=` | دانلود فایل Excel/PDF |
| `GET` | `/api/v1/longitudinal/reports/{report_id}/heatmap/summary` | دریافت متادیتای heatmap چندلایه |
| `POST` | `/api/v1/longitudinal/reports/schedules` | ایجاد/ویرایش زمان‌بندی گزارش |
| `GET` | `/api/v1/longitudinal/reports/schedules/{schedule_id}/runs` | تاریخچه اجراهای زمان‌بندی |

> Endpointها در فازهای بعدی با قابلیت فیلتر تاریخ، نوع متریک و هشدار تکمیل می‌شوند.

---

## 🔐 دسترسی و نقش‌ها
- **دکتر / متخصص**: CRUD اپیزود، مشاهده روند، ثبت visit/metric.
- **پژوهشگر**: حالت read-only (با داده ناشناس).
- **اپراتور**: فقط ثبت داده خام (بدون تحلیل).

---

## 🔄 مهاجرت و وابستگی‌ها
- ایجاد جداول جدید (مهاجرت Alembic).
- هماهنگی با `medical_records` و `imaging_studies` (nullable FK).
- اضافه‌کردن Enum جدید برای `visit_type` و `metric_type`.
- در صورت نیاز به تاریخچه اتوماتیک، hook برای sync از medical_records → longitudinal (در فاز بعد).

---

## 🛣️ گام‌های بعدی
1. ایجاد migrations و مدل‌های SQLAlchemy مطابق طرح.
2. پیاده‌سازی `LongitudinalTrackingService`.
3. ساخت API و تست unit/integration (timeline، trend، comparison، progression، alerts، reports).
4. آماده‌سازی داده نمونه برای UI و اعتبارسنجی heatmap/alerts/reports.
5. طراحی UI (تایم‌لاین، نمودار، مقایسه تصویری، کارت سرعت، هشدارها، مدیریت گزارش‌ها) → فاز فرانت‌اند.
6. فاز ۲.۱: پیاده‌سازی Scheduler service، هشدار ترکیبی، و افزودن تست‌های end-to-end برای تولید گزارش‌های زمان‌بندی شده.

---

**آخرین به‌روزرسانی:** نوامبر 2025  
**مسئول:** تیم محصول NeuroPredict-AI


