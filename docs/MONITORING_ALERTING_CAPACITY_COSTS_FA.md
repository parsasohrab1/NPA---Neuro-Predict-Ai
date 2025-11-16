## مانیتورینگ، هشدارها، ظرفیت‌سنجی و هزینه‌ها

### اهداف
- دید شفاف روی سلامت، کارایی و هزینه‌ها؛ واکنش سریع به رخدادها؛ برنامه‌ریزی ظرفیت و بهینه‌سازی هزینه.


### مانیتورینگ (Metrics & Dashboards)
- شاخص‌های اپلیکیشن:
  - Latency (p50/p95/p99) به تفکیک endpointهای کلیدی: patients, imaging, predictions, reports
  - Error Rate (۴xx بحرانی/۵xx)، RPS، Queue depth (فاز صف)
  - Cache hit/miss، زمان کوئری DB، اتصالات DB/Redis
- شاخص‌های زیرساخت:
  - CPU/Memory/IO، Disk usage/IOPS، Network throughput/latency
  - Health/Readiness/Liveness پروب‌ها
- ابزارها:
  - Prometheus + Grafana برای متریک/داشبورد
  - Logstash/Elastic (یا معادل) برای لاگ‌محور
  - OpenTelemetry (Phase 2) برای تریسینگ
- داشبوردهای پیشنهادی:
  - API Overview: latency, errors, RPS, saturation
  - DB/Cache: query time, connections, hit/miss
  - Imaging/Predictions: پردازش‌ها، زمان اجرا، خطاها
  - Infra: Node/Container resources, disk/net


### هشدارها (Alerting)
- قواعد عملی (SLO-driven):
  - p95 Latency > هدف برای 5 دقیقه
  - Error Rate > 2% برای 5 دقیقه یا جهش ناگهانی
  - Uptime < 99.5% (MVP) در بازه روزانه
  - DB connections نزدیک سقف، Redis latency بالا
  - Disk usage > 80%، Queue depth بالا (فاز صف)
- سطوح هشدار:
  - Warning (اولیه) → Critical (تشدید) با مسیر Escalation
  - اعلان به کانال تیم + تلفن/پیام اضطراری برای Critical
- سرکوب/بی‌صدا (Silence) و نگهداشت نمایه رخدادها برای RCA


### ظرفیت‌سنجی (Capacity Planning)
- خط مبنا:
  - پروفایل ترافیک فعلی: RPS، حجم آپلود، تعداد پیش‌بینی‌ها در پیک
  - منابع مصرفی: CPU/Memory/DB/Redis بر حسب بار
- مدل‌سازی:
  - Headroom هدف: 30–50% برای پیک‌های غیرمنتظره
  - HPA بر اساس Latency/CPU؛ سقف replica و thresholdهای مقیاس
  - DB: حداکثر اتصالات، Pool sizing، Read/Write Split (فازهای بعد)
  - Storage: رشد تصاویر/گزارش‌ها، سیاست آرشیو/Retention
- تست بار دوره‌ای:
  - سناریوها: CRUD سنگین، آپلود تصویر، پیش‌بینی متوالی، ترکیبی
  - اهداف: بررسی آستانه SLO/حاشیه امنیت و نقاط گلوگاه


### هزینه‌ها (Cost Management)
- ردیابی هزینه:
  - برچسب‌گذاری منابع (env/service/owner)، گزارش دوره‌ای هزینه‌ها
  - تفکیک هزینه Compute/DB/Storage/Network/Logs
- بهینه‌سازی:
  - خاموشی محیط‌های غیرفعال (Dev/Stage off-hours)
  - اندازه‌گذاری صحیح instanceها و محدودسازی منابع کانتینر
  - کاهش لاگ INFO در Prod (نگهداشت معقول)، TTL برای متریک/لاگ
  - کش موثر، ایندکس‌گذاری DB، حذف N+1، فشرده‌سازی آرشیو
- بودجه و هشدار هزینه:
  - سقف بودجه ماهانه/محیط و هشدار در 70/90/100%


### فرآیند RCA و بهبود مستمر
- هنگام رخداد: جمع‌آوری لاگ‌ها/تریس/متریک مرتبط با trace_id
- تحلیل: تعیین علت ریشه‌ای (کد/DB/شبکه/وابستگی خارجی)
- اقدام اصلاحی: تغییرات پایدار (کد/پیکربندی/ایندکس/سیاست)
- بازبینی: به‌روزرسانی داشبورد/هشدار/مستندات و اشتراک‌گذاری آموزشی


### چک‌لیست سریع
- [ ] داشبوردهای API/DB/Infra آماده و مرور هفتگی
- [ ] آستانه‌های هشدار SLO و مسیر Escalation تعریف‌شده
- [ ] تست بار فصلی و به‌روزرسانی ظرفیت/HPA
- [ ] برچسب‌گذاری منابع و هشدار بودجه هزینه
- [ ] سیاست نگهداشت لاگ/متریک/بکاپ مطابق مقررات و هزینه

