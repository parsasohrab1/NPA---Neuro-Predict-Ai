## معماری کلان و دیاگرام‌ها (Context/Container)

### گزینه‌های معماری کلان
- **مونولیت ماژولار (پیشنهاد برای MVP)**
  - مزایا: توسعه سریع‌تر، دیپلوی ساده، تراکنش‌های درون‌فرایندی، ساده‌تر برای تیم کوچک.
  - معایب: رشد اندازه دیپلوی، نیاز به انشقاق در مقیاس بالا.
  - مناسب برای: هسته کلینیکی، آپلود تصویر، پیش‌بینی پایه، گزارش‌دهی ساده.

- **میکروسرویس‌ها (فازهای بعد)**
  - مزایا: استقلال استقرار و مقیاس هر دامنه (imaging/predictions/reports)، مرزبندی واضح، تاب‌آوری بهتر.
  - معایب: پیچیدگی شبکه/تراکنش توزیع‌شده، نیاز به Observability قوی، DevOps سنگین‌تر.
  - مناسب برای: زمانی که بار ترافیکی/محاسباتی رشد کند یا تیم‌ها تخصصی شوند.

- **سرورلس (انتخاب گزینشی)**
  - مزایا: مقیاس خودکار، پرداخت به ازای مصرف، مناسب برای کارهای نامنظم.
  - معایب: سردشدن، محدودیت زمان اجرا، Debug/Observability سخت‌تر.
  - مناسب برای: پردازش‌های Batch/Report یا Jobهای آسنکرون خاص در فازهای بعد.


### پیشنهاد مسیر
- فاز 1–2: مونولیت ماژولار FastAPI + Jobهای داخلی ساده (یا صف سبک).
- فاز 3+: جداسازی سرویس‌های سنگین (Imaging/Predictions/Reporting) به سرویس‌های مستقل.
- فاز 4+: اضافه‌کردن صف/اتوبوس پیام، کالکتور تریس، و استقرار بدون وقفه.


### دیاگرام کانتکست (C4: Context)

```mermaid
flowchart LR
  subgraph ExternalSystems [سیستم‌های بیرونی]
    HIS[(HIS)]
    PACS[(PACS)]
  end

  subgraph Users [کاربران]
    Admin[ادمین سامانه]
    Doctor[پزشک/نورولوژیست]
    Nurse[پرستار/کارشناس]
    Viewer[مشاهده‌گر/مدیر]
  end

  subgraph System [NeuroPredict-AI]
    FE[Frontend (React/TS)]
    ADM[Admin Dashboard (React/TS)]
    API[Backend API (FastAPI)]
    DB[(PostgreSQL)]
    Cache[(Redis)]
    Storage[(Images/Reports)]
  end

  Users --> FE
  Users --> ADM
  FE -->|REST/JSON| API
  ADM -->|REST/JSON| API
  API <-->|Sync/Async| HIS
  API <-->|Imaging Links| PACS
  API --> DB
  API --> Cache
  API --> Storage
```


### دیاگرام کانتینر (C4: Container)

```mermaid
flowchart TB
  subgraph Client
    Web[Frontend (Vite/React/TS)]
    AdminUI[Admin Dashboard (React/TS)]
  end

  subgraph Backend[FastAPI Monolith]
    APIGW[API Routers: auth/patients/imaging/predictions/reports/longitudinal/products]
    Services[Domain Services: AI/Reporting/Monitoring/Integration/ImageProc/Longitudinal]
    Core[Core: config/security/cache]
    ORM[DB Layer: SQLAlchemy Async]
  end

  subgraph Data
    PG[(PostgreSQL)]
    REDIS[(Redis)]
    FS[(File Storage: Images/Reports)]
  end

  Web -->|HTTP/JSON| APIGW
  AdminUI -->|HTTP/JSON| APIGW
  APIGW --> Services
  APIGW --> Core
  Services --> ORM
  Core --> REDIS
  ORM --> PG
  Services --> FS
```


### مرزبندی دامنه‌ها (نمونه مونولیت ماژولار)
- API لایه ارائه (Routers) ←→ Schemas (قرارداد) ←→ Services (منطق دامنه) ←→ Models/ORM (داده)
- دامنه‌ها: Patients, Imaging, Predictions, Reports, Longitudinal, Security, Integration, Products


### مسیر انشقاق به میکروسرویس‌ها (نمونه)
- Imaging Service: آپلود/اعتبارسنجی/پردازش تصویر، استوریج و صف پردازش.
- Prediction Service: اجرای مدل، صف Job، مقیاس‌پذیری مستقل (GPU در فاز بعد).
- Reporting Service: تولید PDF و گزارش‌های طولی زمان‌بندی‌شده.
- API Gateway/BFF: تجمیع پاسخ‌ها برای UIها، سیاست‌های امنیتی مشترک.


### ملاحظات عملیاتی
- Observability: لاگ ساختاریافته، متریک‌ها، تریسینگ (OpenTelemetry در فاز بعد).
- امنیت: JWT، RBAC، هدرهای امنیتی، CORS محدود، Rate Limiting.
- دیتابیس: ایندکس‌گذاری، جلوگیری از N+1، پشتیبان‌گیری/بازیابی.
- عملکرد: کش، Eager loading، Async I/O، صف برای کارهای طولانی.


