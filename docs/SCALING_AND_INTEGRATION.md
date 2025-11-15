# آماده‌سازی برای مقیاس و یکپارچه‌سازی

این سند راهنمای پیاده‌سازی ویژگی‌های مقیاس‌پذیری و یکپارچه‌سازی برای سیستم NeuroPredict-AI است.

## 1. امنیت (Security Enhancements)

### 1.1 Multi-Factor Authentication (MFA)
- **TOTP (Time-based One-Time Password)**: پشتیبانی از Google Authenticator و سایر اپلیکیشن‌های TOTP
- **Backup Codes**: کدهای پشتیبان برای دسترسی در صورت از دست دادن دستگاه
- **QR Code Generation**: تولید خودکار QR code برای تنظیم MFA

**API Endpoints:**
- `POST /api/v1/security/mfa/setup` - تنظیم MFA
- `POST /api/v1/security/mfa/verify` - تأیید کد MFA
- `POST /api/v1/security/mfa/enable` - فعال‌سازی MFA
- `POST /api/v1/security/mfa/disable` - غیرفعال‌سازی MFA
- `GET /api/v1/security/mfa/status` - وضعیت MFA

### 1.2 سیاست‌های رمز عبور (Password Policies)
- حداقل طول رمز عبور
- نیاز به حروف بزرگ، کوچک، اعداد و کاراکترهای خاص
- جلوگیری از استفاده مجدد رمزهای قبلی
- انقضای رمز عبور
- هشدار قبل از انقضا

**مدل:** `PasswordPolicy` در `backend/app/models/security.py`

### 1.3 IP Whitelist
- مدیریت لیست IPهای مجاز برای هر کاربر
- پشتیبانی از CIDR notation برای محدوده IP
- انقضای خودکار IP whitelist entries

**API Endpoints:**
- `POST /api/v1/security/ip-whitelist` - افزودن IP به whitelist
- `GET /api/v1/security/ip-whitelist` - لیست IPهای whitelist شده
- `DELETE /api/v1/security/ip-whitelist/{id}` - حذف IP از whitelist

### 1.4 مدیریت سشن (Session Management)
- ردیابی تمام سشن‌های فعال کاربر
- امکان لغو سشن‌های خاص یا همه سشن‌ها
- ذخیره اطلاعات IP و User Agent برای هر سشن
- انقضای خودکار سشن‌ها

**API Endpoints:**
- `GET /api/v1/security/sessions` - لیست سشن‌های فعال
- `POST /api/v1/security/sessions/{id}/revoke` - لغو سشن خاص
- `POST /api/v1/security/sessions/revoke-all` - لغو همه سشن‌ها

### 1.5 لاگ‌های امنیتی (Security Logs)
- ثبت تمام رویدادهای امنیتی
- دسته‌بندی بر اساس severity (info, warning, error, critical)
- ردیابی IP address و User Agent
- جستجو و فیلتر لاگ‌ها

**API Endpoints:**
- `GET /api/v1/security/logs` - دریافت لاگ‌های امنیتی

## 2. مانیتورینگ و Observability

### 2.1 Prometheus & Grafana
- **Prometheus**: جمع‌آوری متریک‌ها از backend
- **Grafana**: نمایش و تجسم متریک‌ها
- Health checks پیشرفته با جزئیات سیستم

**سرویس‌ها:**
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3002` (admin/admin)

**API Endpoints:**
- `GET /api/v1/monitoring/health` - Health check جامع
- `GET /api/v1/monitoring/health/live` - Liveness probe
- `GET /api/v1/monitoring/health/ready` - Readiness probe
- `GET /api/v1/monitoring/metrics` - متریک‌های سیستم
- `GET /api/v1/monitoring/metrics/prometheus` - فرمت Prometheus

### 2.2 ELK Stack (Elasticsearch, Logstash, Kibana)
- **Elasticsearch**: ذخیره و جستجوی لاگ‌ها
- **Logstash**: پردازش و فیلتر لاگ‌ها
- **Kibana**: تجسم و تحلیل لاگ‌ها

**سرویس‌ها:**
- Elasticsearch: `http://localhost:9200`
- Kibana: `http://localhost:5601`
- Logstash: `http://localhost:5044` (HTTP input)

### 2.3 Sentry Integration
- ردیابی خطاها و exceptions
- Performance monitoring
- Release tracking

**پیکربندی:** در `backend/app/core/config.py` تنظیم `SENTRY_DSN`

## 3. یکپارچه‌سازی (Integration)

### 3.1 PACS Integration
- دریافت مطالعات تصویربرداری از سیستم PACS
- همگام‌سازی خودکار داده‌های DICOM

**API Endpoints:**
- `POST /api/v1/integration/pacs/fetch` - دریافت study از PACS
- `POST /api/v1/integration/pacs/sync` - همگام‌سازی study از PACS

### 3.2 EHR Integration
- دریافت اطلاعات بیمار از سیستم EHR
- همگام‌سازی داده‌های بالینی

**API Endpoints:**
- `POST /api/v1/integration/ehr/fetch` - دریافت اطلاعات بیمار از EHR
- `POST /api/v1/integration/ehr/sync` - همگام‌سازی بیمار از EHR

### 3.3 HL7/FHIR Integration
- ارسال و دریافت پیام‌های HL7
- ارسال و دریافت منابع FHIR
- جستجوی منابع FHIR

**API Endpoints:**
- `POST /api/v1/integration/hl7/send` - ارسال پیام HL7
- `POST /api/v1/integration/fhir/send` - ارسال منبع FHIR
- `GET /api/v1/integration/fhir/{resource_type}/{id}` - دریافت منبع FHIR
- `GET /api/v1/integration/fhir/{resource_type}` - جستجوی منابع FHIR

**پیکربندی:**
```python
HL7_FHIR_ENDPOINT = "http://fhir-server:8080"
PACS_SERVER_URL = "http://pacs-server:8042"
EHR_API_URL = "http://ehr-server:8080"
```

## 4. Backup & Disaster Recovery

### 4.1 استراتژی پشتیبان‌گیری
- پشتیبان‌گیری خودکار از دیتابیس PostgreSQL
- فرمت custom برای فشرده‌سازی بهتر
- ذخیره metadata برای هر backup

**API Endpoints:**
- `POST /api/v1/backup/create` - ایجاد backup
- `POST /api/v1/backup/restore` - بازیابی از backup
- `GET /api/v1/backup/list` - لیست backup‌ها
- `POST /api/v1/backup/verify` - بررسی صحت backup
- `POST /api/v1/backup/cleanup` - پاک‌سازی backup‌های قدیمی

### 4.2 نگهداشت داده
- پاک‌سازی خودکار backup‌های قدیمی
- نگهداری backup‌ها برای مدت زمان مشخص (پیش‌فرض: 30 روز)

## 5. بهینه‌سازی عملکرد (Performance)

### 5.1 Redis Caching
- کش کردن نتایج queryهای پرتکرار
- فشرده‌سازی داده‌ها با gzip
- TTL خودکار برای cache entries

**استفاده:**
```python
from ..services.performance_service import PerformanceService

# Cache query result
result = await PerformanceService.optimize_query(db, query, params)

# Invalidate cache
await PerformanceService.invalidate_cache_pattern("query:*")
```

### 5.2 بهینه‌سازی Query
- استفاده از indexes مناسب
- Query optimization با caching
- Batch processing برای عملیات‌های حجیم

### 5.3 فشرده‌سازی
- فشرده‌سازی داده‌ها در cache
- فشرده‌سازی response برای APIهای حجیم

### 5.4 CDN Configuration
برای production، توصیه می‌شود از CDN برای:
- Static assets (images, CSS, JS)
- Medical images (DICOM files)
- Reports و documents

**پیکربندی پیشنهادی:**
- CloudFront (AWS)
- Cloudflare
- Azure CDN

## 6. راه‌اندازی

### 6.1 نصب Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 6.2 راه‌اندازی با Docker Compose
```bash
docker-compose up -d
```

این دستور تمام سرویس‌ها را راه‌اندازی می‌کند:
- Backend API
- Frontend
- Admin Dashboard
- PostgreSQL
- Redis
- Prometheus
- Grafana
- Elasticsearch
- Logstash
- Kibana

### 6.3 Migration Database
```bash
cd backend
alembic upgrade head
```

### 6.4 ایجاد Password Policy پیش‌فرض
```python
from app.models.security import PasswordPolicy
from app.db.session import get_db

async def create_default_password_policy():
    db = next(get_db())
    policy = PasswordPolicy(
        name="default",
        description="Default password policy",
        min_length=8,
        require_uppercase=True,
        require_lowercase=True,
        require_digits=True,
        require_special_chars=True,
        prevent_reuse_count=5,
        expiration_days=90,
        warning_days=7,
        max_failed_attempts=5,
        lockout_duration_minutes=30,
        is_active=True,
        is_default=True
    )
    db.add(policy)
    db.commit()
```

## 7. پیکربندی

### 7.1 Environment Variables
```bash
# Security - REQUIRED
# Generate a secure SECRET_KEY using:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
# Must be at least 32 characters long
SECRET_KEY=your-secure-random-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Integration
HL7_FHIR_ENDPOINT=http://fhir-server:8080
PACS_SERVER_URL=http://pacs-server:8042
EHR_API_URL=http://ehr-server:8080

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### 7.2 Prometheus Configuration
فایل `monitoring/prometheus.yml` را برای تنظیم scrape targets ویرایش کنید.

### 7.3 Grafana Dashboards
Dashboardهای پیش‌ساخته در `monitoring/grafana/dashboards/` قرار دارند.

## 8. Best Practices

1. **امنیت:**
   - همیشه MFA را برای کاربران admin فعال کنید
   - IP whitelist را برای دسترسی‌های حساس تنظیم کنید
   - لاگ‌های امنیتی را به صورت منظم بررسی کنید

2. **مانیتورینگ:**
   - Health checks را به صورت منظم بررسی کنید
   - Alert rules را در Prometheus تنظیم کنید
   - Dashboardهای Grafana را برای مشاهده روندها استفاده کنید

3. **Backup:**
   - Backupهای منظم (روزانه) ایجاد کنید
   - Backupها را در مکان‌های مختلف ذخیره کنید
   - به صورت منظم restore test انجام دهید

4. **Performance:**
   - Cache را برای queryهای پرتکرار استفاده کنید
   - Queryها را بهینه کنید
   - از CDN برای static assets استفاده کنید

## 9. Troubleshooting

### مشکل در اتصال Redis
- بررسی کنید که Redis در حال اجرا است: `docker ps | grep redis`
- بررسی لاگ‌ها: `docker logs neuropredict-redis`

### مشکل در Prometheus
- بررسی configuration: `monitoring/prometheus.yml`
- بررسی لاگ‌ها: `docker logs neuropredict-prometheus`

### مشکل در Elasticsearch
- بررسی memory: Elasticsearch نیاز به حداقل 512MB RAM دارد
- بررسی لاگ‌ها: `docker logs neuropredict-elasticsearch`

## 10. منابع بیشتر

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [ELK Stack Documentation](https://www.elastic.co/guide/)
- [HL7 FHIR Documentation](https://www.hl7.org/fhir/)

