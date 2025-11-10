# 📊 مشخصات تب «Reports» در داشبورد NeuroPredict-AI

این سند نیازمندی‌های عملکردی و طرح UX تب گزارش‌ها را برای مرحله‌ی توسعه مشخص می‌کند.

---

## 🎯 اهداف کسب‌وکار
- ارائه‌ی گزارش‌های استاندارد برای پزشکان، پژوهشگران و مدیران.
- نمایش شاخص‌های کلیدی با نمودارهای تعاملی.
- امکان فیلتر، مقایسه، و خروجی گرفتن از گزارش‌ها (PDF/Excel/تصویر).
- ایجاد نقطه‌ی ورود برای توسعه تب‌های Longitudinal Tracking و Population Analytics.

---

## 👤 کاربران هدف
- **پزشک متخصص (Clinical)**: دسترسی به گزارش‌های بیمار-محور، روندهای کلینیکی، توصیه‌ها.
- **پژوهشگر**: گزارش‌های آماری، امکان مقایسه گروهی، خروجی داده برای تحلیل.
- **مدیر سیستم/بیمارستان**: خلاصه مدیریتی، عملکرد مدل‌ها، شاخص‌های عملیات.

---

## 🧩 ماژول‌های تب Reports
1. **Clinical Report**  
   - فیلتر: Patient، Date range، Disease type  
   - محتوا: خلاصه بیمار، آخرین پیش‌بینی‌ها، نمودار روند امتیاز ریسک، توصیه‌های درمانی، وضعیت پیگیری  
   - خروجی: PDF (قالب کلینیکی با لوگو/امضا)

2. **Research Report**  
   - فیلتر: Date range، Disease type، Risk level، Demographic filters، Episode/Study tag  
   - محتوا: آمار توصیفی، نمودار توزیع ریسک، جدول aggregate (mean/median)، heatmap چندلایه (MRI + Biomarker)  
   - خروجی: CSV/Excel، تصویر نمودارها، JSON خلاصه heatmap برای اشتراک‌گذاری سریع

3. **Management Dashboard**  
   - فیلتر: Date range، Facility، Model version  
   - محتوا: KPI نهایی (تعداد پیش‌بینی، زمان پاسخ، دقت مدل)، نمودار performance، لیست هشدارها/کارهای باز  
   - خروجی: PDF خلاصه مدیریتی

4. **Alert & Schedule Insights (Phase 2)**  
   - کارت وضعیت هشدارهای ترکیبی (Progression + Biomarker drift)  
   - لیست زمان‌بندی‌های فعال با وضعیت آخرین اجرا و CTA برای Run Now  
   - پیوند مستقیم به خروجی Heatmap آخرین ران  

5. **Custom Builder (نسخه بعدی)**  
   - Drag & drop ویجت‌ها، ذخیره قالب، اشتراک‌گذاری → در نسخه اولیه فقط ساختار اولیه و placeholder.

---

## 🧭 فلو UX متنی

### 1. Reports Landing
```
┌───────────────────────────────────────────┐
│ Header: Reports                           │
├───────────────────────────────────────────┤
│ Tabs: Clinical | Research | Management    │
│ Filters Panel (collapsible)               │
│ Generate button + Export dropdown         │
├───────────────────────────────────────────┤
│ Report Content Area (cards, charts)       │
│ • Clinical: patient info + charts         │
│ • Research: aggregation tables + charts   │
│ • Management: KPI cards + trend charts    │
├───────────────────────────────────────────┤
│ Activity Trail / Recent exports           │
└───────────────────────────────────────────┘
```

### 2. Filter Drawer استاندارد
- Patient selector (autocomplete)
- Date range picker
- Disease type (Alzheimer / Parkinson / Both)
- Risk level (Low / Medium / High)
- Additional filters per نوع گزارش

### 3. خروجی‌های پیشنهادی
- دکمه‌ی `Generate report` → Fetch داده → Render content
- Dropdown `Export` → گزینه‌های PDF، Excel، تصویر نمودار
- Modal تأیید قبل از دانلود برای لاگ و انتخاب مسیر ذخیره

---

## 🛠️ نیازمندی‌های Backend
- Endpoint ها:
  - `GET /api/v1/reports/clinical?patient_id=&from=&to=&disease_type=`
  - `GET /api/v1/reports/research?from=&to=&risk_level=&age_group=...`
  - `GET /api/v1/reports/management?model_version=&facility=&from=&to=`
  - `POST /api/v1/reports/export` (نوع گزارش + پارامترها + فرمت خروجی)
- Endpoint های فاز ۲:
  - `POST /api/v1/longitudinal/reports/schedules` برای ایجاد/ویرایش زمان‌بندی
  - `POST /api/v1/longitudinal/reports/{schedule_id}/run` برای اجرای دستی
  - `GET /api/v1/longitudinal/reports/{report_id}/heatmap/summary` جهت داده‌های خلاصه
- ماژول سرویس: `app/services/reporting_service.py`
  - لایه استخراج داده از جداول موجود (patients, medical_records, predictions, imaging_studies)
  - Aggregation با SQLAlchemy / pandas
  - تولید داده ساخت‌یافته برای charts
- Migration احتمالی:
  - جدول `report_exports` برای ذخیره متادیتای دانلودها
  - نمای (view) برای کوئری‌های پیچیده (اختیاری)
  - جدول `report_schedules` و `report_schedule_runs` برای نگه‌داری وضعیت اجراها

---

## 🎨 نیازمندی‌های Frontend
- ساختار مسیر: `/admin/reports` با زیرتب‌ها
- State: Zustand یا React Query برای حفظ فیلترها و cache گزارش
- کامپوننت‌ها:
  - `ReportsPage` (wrapper + tabs)
  - `ClinicalReportPanel`, `ResearchReportPanel`, `ManagementReportPanel`
  - `ReportFiltersDrawer`
  - `ReportExportMenu`
  - `ReportScheduleBoard` (نمایش وضعیت scheduleها و تاریخچه اجرا)
  - `CombinedAlertBanner` برای هشدارهای cross-module
- Chart library: `Recharts` (درحال حاضر نصب است)؛ برای heatmap ممکن است `Nivo` اضافه شود.
- PDF export: بررسی `react-pdf` در frontend یا سرویس backend (برای هماهنگی با branding به احتمال زیاد backend مناسب‌تر است).

---

## ✅ معیارهای موفقیت
- تولید گزارش در کمتر از 3 ثانیه (با داده‌ی نمونه)
- امکان اعمال فیلترهای اصلی و مشاهده‌ی بازتاب در محتوا
- خروجی PDF/Excel بدون خطا برای حداقل گزارش کلینیکی و پژوهشی
- اجرای موفقیت‌آمیز حداقل یک زمان‌بندی گزارش در 24 ساعت گذشته
- کمتر از 3 هشدار false-positive در هفته برای هشدار ترکیبی
- تمام اقدامات (Generate/Export) در audit log ثبت شود

---

## 🔄 گام‌های بعدی
1. تایید مستند نیازمندی توسط تیم محصول/پزشکی.
2. طراحی بصری (Figma) بر اساس ساختار فوق.
3. تعریف API contract (schema request/response) و اضافه‌کردن تست‌های واحد سرویس گزارش.
4. پیاده‌سازی incremental: ابتدا تب Clinical، سپس Research و Management.
5. ادغام با Role-based access → Clinical و Management فقط برای Admin/Doctor قابل مشاهده، Research برای Researcher/Admin.
6. فاز ۲: تکمیل بورد زمان‌بندی و هشدار، افزودن تست‌های end-to-end برای heatmap چندلایه.

---

**آخرین بروزرسانی**: نوامبر 2025  
**مسئول**: تیم محصول NeuroPredict-AI


