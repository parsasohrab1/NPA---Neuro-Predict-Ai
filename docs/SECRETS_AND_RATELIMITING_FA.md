## مدیریت کلیدها/اسرار و محدودیت‌های ریت‌لیمیتینگ

### مدیریت کلیدها و اسرار (Secrets Management)
- اصول:
  - نگهداری کلیدها/توکن‌ها خارج از کد منبع؛ استفاده از Environment Variables یا Secret Store.
  - اصل کمترین دسترسی (PoLP): دسترسی فقط برای سرویس‌های نیازمند.
  - چرخش دوره‌ای کلیدها (Key Rotation) و ابطال فوری در رخدادها.
  - ثبت دسترسی/استفاده از کلیدها (ممکن در Secret Store/CI/CD).
- نگهداری:
  - توسعه: فایل‌های محلی امن (env.) خارج از کنترل نسخه، با نمونه `.env.example` بدون مقادیر حساس.
  - تولید: Secret Store (Vault/KMS/Cloud Secrets) یا مدیریت امن در Orchestrator.
  - جداسازی محیط‌ها: DEV/TEST/STAGE/PROD با کلیدهای مستقل.
- استفاده در برنامه (هم‌راستا با پروژه):
  - خواندن از `settings`/env در `backend/app/core/config.py`.
  - جلوگیری از چاپ/لاگ اسرار؛ ماسک‌کردن در لاگ‌ها.
  - عدم کش اسرار در حافظه طولانی‌مدت (در صورت نیاز، TTL کوتاه).
- چرخش کلید:
  - پشتیبانی از چند کلید فعال برای گذار امن (Active/Next).
  - مستندسازی روند چرخش (Runbook) و زمان‌بندی.
- ممیزی و انطباق:
  - ثبت تغییرات/گردش کلید، کنترل دسترسی مبتنی بر نقش برای مدیریت اسرار.
  - ذخیره نسخه‌ها و ابطال دسترسی‌های قدیمی.


### محدودیت‌های ریت‌لیمیتینگ (Rate Limiting)
- اهداف:
  - محافظت در برابر سوءاستفاده/Brute Force و کنترل مصرف منابع.
  - تضمین SLOهای کارایی و تجربه کاربری پایدار.
- الگو و زیرساخت:
  - پیاده‌سازی مبتنی بر Redis (موجود در `main.py` با `RateLimitMiddleware`).
  - کلیدگذاری بر اساس IP/کاربر/مسیر (ترکیبی برای مسیرهای حساس).
  - الگوریتم: Token Bucket/Leaky Bucket یا Fixed Window با Sliding Window (پیشنهادی).
- سیاست‌ها (نمونه پیشنهادی):
  - عمومی خواندنی (GETهای لیستی): 120 req/min/IP
  - مسیرهای حساس (Login/OTP): 5–10 req/min/IP/کاربر
  - ایجاد/ویرایش منابع بالینی: 60 req/min/کاربر
  - آپلود تصویر: 10 req/min/IP با حد همزمانی محدود
  - API داخلی/Integrations: سهمیهٔ جدا و IP Whitelist به همراه امضای درخواست
- سربرگ‌ها:
  - در پاسخ‌ها (در صورت فعال‌سازی): `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After` (در 429)
- خطا:
  - وضعیت 429 Too Many Requests با پیام خوانا و `Retry-After`
- استثناها/لیست سفید:
  - مسیرهای Health/Docs (اختیاری)، IP/Serviceهای داخلی (با احتیاط)
- Observability:
  - متریک‌های hit/limit/blocked، توزیع بر حسب مسیر/کاربر/IP
  - هشدار هنگام جهش Blocked Requests یا نزدیک‌شدن به سقف ظرفیت
- امنیت:
  - جلوگیری از Bypass: اعمال محدودیت قبل از اجرای سنگین/پایگاه داده.
  - همگام‌سازی ساعت/TTL، مقاومت در برابر حملات توزیع‌شده (ترکیب با WAF/Cloud).


### پیکربندی نمونه (پیشنهادی)
- Env Vars:
  - `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`
  - `RATE_LIMIT_DEFAULT=120/min`
  - `RATE_LIMIT_LOGIN=10/min`
  - `RATE_LIMIT_UPLOAD=10/min`
- سطح مسیر (Policy Table):
  - `/auth/*`: `RATE_LIMIT_LOGIN`
  - `/patients/*`, `/predictions/*`: `RATE_LIMIT_DEFAULT`
  - `/imaging/upload`: `RATE_LIMIT_UPLOAD` + کنترل اندازه/همزمانی


### Runbook و نگهداری
- Failover Redis: در خرابی Redis، رفتار محافظه‌کارانه (گزینه: fail-open محدود یا fail-closed روی مسیرهای حساس).
- پاکسازی کلیدها: TTL مناسب و Namespace جدا برای rate-limit.
- تست بار و تأیید آستانه‌ها قبل از استقرار.


