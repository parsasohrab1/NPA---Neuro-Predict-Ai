## انتخاب پشته‌های فناوری (Frontend, Backend, DB، کش، پیام‌رسان، جستجو)

این انتخاب‌ها با کد فعلی پروژه هم‌راستا هستند و مسیر رشد در فازهای بعد را پوشش می‌دهند.

### Frontend
- انتخاب: React + TypeScript + Vite + TailwindCSS
  - دلیل: سرعت توسعه، تایپ‌سیف بودن، باندل سریع، طراحی واکنش‌گرا سریع.
  - Router: React Router
  - i18n: آماده‌سازی پشتیبانی فارسی/RTL
  - جایگزین‌ها: Next.js (SSR/SEO) در صورت نیاز آتی.

### Backend
- انتخاب: Python FastAPI (Async) + Uvicorn
  - دلیل: کارایی مناسب، تایپینگ خوب، DX عالی، هم‌خوان با نیازهای ML.
  - ORM: SQLAlchemy Async
  - Schemas: Pydantic
  - Auth: JWT (python-jose) + Passlib
  - جایگزین‌ها: Node.js NestJS (در صورت نیاز تیم)، Go (برای سرویس‌های با کارایی بالا).

### Database
- انتخاب: PostgreSQL
  - دلیل: ACID، ایندکس‌های پیشرفته، JSONB، اکوسیستم قوی.
  - مهاجرت‌ها: Alembic (قابل اضافه‌شدن/فعال‌سازی)
  - الگوها: جلوگیری از N+1 (eager loading)، ایندکس‌گذاری ستون‌های جستجو.
  - جایگزین‌ها: MySQL/MariaDB، یا TimescaleDB برای طولی سنگین.

### Cache
- انتخاب: Redis
  - دلیل: کش پاسخ‌های پرتکرار، Rate Limiting، زیرساخت Async آماده.
  - الگوها: TTL کوتاه، کلید بر اساس پارامترها/کاربر، بی‌اعتبارسازی هدفمند.
  - جایگزین‌ها: Memcached (در سناریوهای بسیار ساده).

### Messaging (پیام‌رسان/صف) – فازهای بعد
- انتخاب پیشنهادی: RabbitMQ (وظایف قابل‌اعتماد) یا Kafka (جریان‌های حجیم)
  - دلیل: جداسازی پردازش‌های سنگین (آپلود/پیش‌بینی/گزارش)، مقیاس‌پذیری مستقل.
  - الگوها: Retry/Backoff، DLQ، Idempotency.
  - جایگزین‌ها: Redis Streams برای حجم کم، SQS/SNS (ابر).

### Search (جستجو) – در صورت نیاز
- انتخاب: OpenSearch/Elasticsearch
  - دلیل: جستجوی متن کامل در بیماران/گزارش‌ها، آنالیتیکس ساده.
  - جایگزین‌ها: PostgreSQL full-text برای مقیاس کوچک (MVP).

### Observability
- انتخاب: Prometheus + Grafana، Logstash/Elastic (نمونه موجود)، OpenTelemetry (فاز بعد)
  - دلیل: پایش SLO/SLI، داشبورد سریع، قابلیت تریس توزیع‌شده.

### Storage
- انتخاب: فایل‌سیستم محلی (توسعه) → شیء-استور (S3/MinIO) در تولید
  - دلیل: نگهداری تصاویر MRI/DICOM و فایل‌های گزارش.

### امنیت
- JWT + RBAC، هدرهای امنیتی، CORS محدود، Rate Limiting، لاگ ممیزی
  - رمزنگاری در انتقال و سکون، مدیریت Secrets در محیط اجرا.

### جمع‌بندی مسیر
- MVP: Monolith ماژولار FastAPI + PostgreSQL + Redis + React/Tailwind
- فاز 2: افزودن متریک‌ها/هشدار، یکپارچگی یک‌طرفه HIS/PACS، صف سبک
- فاز 3+: انشقاق سرویس‌های سنگین، جستجو پیشرفته، شیء-استور، CI/CD پیشرفته


