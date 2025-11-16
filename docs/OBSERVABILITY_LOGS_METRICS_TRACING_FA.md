## قابلیت مشاهده‌پذیری: لاگینگ، متریک‌ها، تریسینگ

### اهداف
- تشخیص سریع مشکلات، تحلیل ریشه‌ای (RCA)، مانیتورینگ SLO/SLI، و ممیزی رویدادهای حساس.


### لاگینگ (Logging)
- الگو:
  - ساختاریافته (JSON) با فیلدهای ثابت: timestamp، level، service، env، request_id، user_id (در صورت مجاز)، path، method، status_code، latency_ms، error_code، message.
  - سطوح: DEBUG (توسعه)، INFO (جریان طبیعی)، WARN (مرزی/غیرمعمول)، ERROR (شکست)، CRITICAL (اختلال گسترده).
- سیاست‌ها:
  - عدم ثبت دادهٔ شخصی/حساس در لاگ؛ ماسک‌کردن ایمیل/تلفن/شناسه.
  - نگهداشت مبتنی بر سطح: ERROR/WARN طولانی‌تر از DEBUG/INFO.
  - همبستگی درخواست‌ها: تزریق Request ID در میدلور و افزودن به تمام لاگ‌ها.
- مسیرها/ماژول‌ها:
  - Backend FastAPI: لاگ درخواست/پاسخ (p95/p99)، خطاهای هندل‌نشده، رخدادهای امنیتی و CRUD حساس.
  - Workerها (در فازهای بعد): آغاز/پایان Job، اندازه صف، خطاهای پردازش.
- انتقال و ذخیره:
  - ارسال به Logstash/Elastic یا هر سامانهٔ جمع‌آوری مشابه (در پوشه monitoring موجود است).
  - چرخش لاگ (rotation) و محدودیت اندازه فایل در محیط‌های ساده.


### متریک‌ها (Metrics)
- دسته‌بندی:
  - Latency: histogram برای مسیرهای کلیدی (patients, imaging, predictions, reports).
  - Throughput: درخواست‌ها بر ثانیه/دقیقه به تفکیک endpoint.
  - Error Rate: شمارش 4xx/5xx بحرانی.
  - Resource: CPU, Memory, DB connections, Redis latency, Queue depth.
  - App-specific: تعداد پیش‌بینی موفق/ناموفق، زمان پردازش تصویر، cache hit/miss.
- ابزار:
  - Prometheus برای scrap و Grafana برای داشبورد (پوشه monitoring/grafana موجود است).
  - اکسپوز endpoint متریک‌ها (فاز بعد) یا اکسپوتر جانبی.
- داشبوردهای پیشنهادی:
  - API Overview: p50/p95/p99، Error Rate، RPS، Uptime.
  - DB/Cache: زمان کوئری، hit/miss، اتصالات.
  - Predictions Pipeline: زمان اجرا، موفق/ناموفق، صف.
- هشدارها (Alerting):
  - p95 Latency > هدف به مدت 5 دقیقه.
  - Error Rate > 2% به مدت 5 دقیقه.
  - Uptime < SLO روزانه.
  - Saturation منابع > 80% پایدار.


### تریسینگ (Tracing)
- دامنه:
  - Trace توزیع‌شده برای درخواست‌های API، فراخوانی‌های DB/Redis، آپلود فایل، اجرای مدل.
  - Propagation: Inject/Extract Request ID و Trace Context در میدلورها و سرویس‌ها.
- ابزار:
  - OpenTelemetry SDK + Collector (فاز بعد)؛ سازگاری با Jaeger/Tempo.
  - نمونه‌برداری (Sampling) پویا: ۱–۵٪ در حالت عادی؛ افزایش در رخدادها.
- بهترین‌عمل:
  - نام‌گذاری spanها: api.<route>، db.query، cache.get/set، model.run، file.upload.
  - افزودن attributes مهم: user_role، patient_id (در صورت مجاز)، status_code، byte_size.


### خط‌مشی نگهداشت و حریم خصوصی
- نگهداشت متفاوت برای سطوح/انواع لاگ (مثلاً ERROR/WARN: ۹۰ روز؛ INFO: ۳۰ روز).
- حذف/ناشناس‌سازی داده‌های شخصی در لاگ‌ها و متریک‌ها.
- دسترسی محدود به مخازن لاگ/متریک/تریس (اصل کمترین دسترسی).


### گام‌های اجرایی پیشنهادی (MVP → بعد)
- MVP:
  - فعال‌سازی لاگ ساختاریافته با Request ID در FastAPI.
  - شمارنده‌های ساده برای Error Rate و ثبت latency در لاگ‌ها.
  - داشبورد پایه در Grafana: Latency/Errors/RPS.
- فاز 2:
  - اکسپوز متریک‌های Prometheus و داشبوردهای غنی.
  - Alerting عملیاتی با آستانه‌های SLO.
  - تریسینگ OpenTelemetry برای مسیرهای کلیدی.
- فاز 3:
  - پوشش تریسینگ کامل سرویس‌ها و صف‌ها، نمونه‌برداری پویا.
  - بهینه‌سازی شاخص‌ها برای RCA سریع و ظرفیت‌سنجی.


