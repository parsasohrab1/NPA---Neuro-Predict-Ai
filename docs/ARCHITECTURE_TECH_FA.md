## معماری و تکنولوژی

### نمای کلی
- **Backend (FastAPI, Python)**: سرویس اصلی API برای مدیریت بیماران، سوابق، تصویربرداری، پیش‌بینی، گزارش‌ها، طولی، امنیت و یکپارچگی.
- **Frontend (Vite + React + TypeScript + Tailwind)**: کلاینت اصلی برای کاربران کلینیکی.
- **Admin Dashboard (React + TS + Tailwind)**: پنل مدیریتی برای نقش‌های ادمین/مدیریتی.
- **Database (SQLAlchemy/Async + PostgreSQL)**: ذخیره‌سازی ساختاریافته؛ با ایندکس‌ها و الگوهای ضد N+1.
- **Cache (Redis)**: کش نتایج خواندنی پرتکرار، Rate Limiting، و آماده‌سازی فلوهای آسنکرون در فاز بعد.
- **Storage**: فایل‌های تصویری (MRI/DICOM) و گزارش‌ها؛ قابل مهاجرت به شیء-استور.
- **Observability**: لاگینگ ساختاریافته، متریک‌ها (Prom/Grafana)، و تریسینگ (فاز بعد).
- **Security**: JWT، RBAC، هدرهای امنیتی، CORS، لاگ ممیزی.


### لایه‌ها و ماژول‌ها (Backend)
- `app/api`: اندپوینت‌ها (patients, predictions, imaging, reports, longitudinal, security, integration, backup, products).
- `app/models`: مدل‌های ORM (User, Patient, MedicalRecord, ImagingStudy, Prediction, Longitudinal*, Audit, Product).
- `app/schemas`: Pydantic Schemas برای اعتبارسنجی ورودی/خروجی.
- `app/services`: منطق دامنه (AI model, reporting, monitoring, integration, longitudinal, image processing).
- `app/core`: تنظیمات، امنیت، کش و سیاست‌های پایه.
- `app/db`: Session و Base و چرخهٔ عمر پایگاه داده.
- `app/main.py`: راه‌اندازی برنامه، میدلورها، CORS، Rate Limit، ثبت Routerها.


### جریان‌های کلیدی
- **CRUD بالینی**: درخواست UI → API FastAPI → ORM (با selectinload) → پاسخ کش‌شونده (TTL).
- **آپلود تصویر**: کلاینت → API → اعتبارسنجی فرمت/حجم → ذخیره فایل/متادیتا → لینک به رکورد.
- **پیش‌بینی**: API (doctor+) → آماده‌سازی داده از آخرین رکورد → اجرای مدل پایه → ذخیره Prediction → گزارش.
- **گزارش‌دهی**: رندر گزارش ساختاریافته (PDF) از داده‌های بیمار/پیش‌بینی → ذخیره/دانلود.
- **طولی**: Episode/Visit → متریک‌های کلیدی → نمودار روند → (فاز بعد) هشدار.


### تکنولوژی‌ها
- Backend: Python 3.x, FastAPI, SQLAlchemy Async, Pydantic, Uvicorn, Redis (async), JWT (python-jose), Passlib.
- Frontend: React 18+, TypeScript, Vite, TailwindCSS, React Router.
- Admin Dashboard: React + TS + Tailwind (جداگانه).
- DB: PostgreSQL (پیشنهادی)، Alembic (قابل اضافه‌شدن برای مهاجرت‌ها).
- ML: PyTorch/NumPy (در سرویس مدل)، Torch nn ماژول چندوجهی (نمونه).
- Monitoring: Prometheus/Grafana (پوشه monitoring)، Logstash/Elastic (نمونه کانفیگ).
- Containerization: Docker و docker-compose برای توسعه/استقرار پایه.


### الگوهای طراحی و بهترین‌عمل‌ها
- Async I/O برای مسیرهای I/O-محور؛ جلوگیری از N+1 با eager loading.
- کش نتایج خواندنی پرتکرار با TTL کوتاه و کلیدهای مشتق از پارامترها/کاربر.
- جداسازی concerns: API (کنترلر)، Schemas (قرارداد)، Services (منطق)، Models (داده).
- مدیریت خطا و پاسخ استاندارد؛ لاگ خطاهای هندل‌نشده در یک نقطه.
- نقش‌ها و کنترل دسترسی در لایه API با decorator `require_role`.


### مقیاس‌پذیری و استقرار
- مقیاس افقی API (stateless) با چند replica؛ HPA بر اساس CPU/Latency.
- جداسازی مسیرهای سنگین (آپلود/پیش‌بینی) و استفاده از صف/کارگر در فازهای بعد.
- ذخیره فایل‌ها روی دیسک محلی در توسعه؛ مهاجرت به شیء-استور (S3/MinIO) در تولید.
- پیکربندی از طریق Env Vars؛ Secrets در Secret Store.
- CI/CD: lint/test/build؛ Blue/Green یا Rolling در فازهای بعد.


### امنیت و انطباق (خلاصه)
- JWT، RBAC، Rate Limiting، هدرهای امنیتی، CORS محدود.
- لاگ ممیزی عملیات حساس و نگهداشت مناسب.
- رمزنگاری داده‌های حساس در انتقال و سکون؛ سیاست نگهداشت/حذف.
- اصول Privacy by Design؛ فرایند DSR/DPIA (به اسناد مرتبط مراجعه شود).


### نقشه راه فنی (High-level)
- فاز 1 (MVP): هسته بالینی، آپلود تصویر، پیش‌بینی پایه، گزارش ساده، امنیت پایه، مانیتورینگ سلامت.
- فاز 2: طولی پیشرفته، داشبورد مدیریتی، یکپارچگی یک‌طرفه HIS/PACS، متریک‌های Prometheus و Alerting.
- فاز 3: هشدارهای طولی، Explainability بیشتر، زمان‌بندی گزارش‌ها، MFA/IP Whitelist، تریسینگ.
- فاز 4: یکپارچگی دوطرفه، مدیریت نسخه مدل و Drift، استقرار بدون وقفه، بهینه‌سازی هزینه.


