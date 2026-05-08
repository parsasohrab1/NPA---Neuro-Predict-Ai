# اسپرینت ۳–۴ — مانیتورینگ، بکاپ، DR و سخت‌سازی زیرساخت

این سند خروجی‌های اسپرینت ۳ و ۴ را خلاصه می‌کند: **قابلیت مشاهده‌پذیری (Observability)**، **پشتیبان‌گیری و بازیابی**، **آمادگی بحران (DR)** و **سخت‌سازی Docker / Nginx / Runtime**.

---

## ۱. مانیتورینگ (Monitoring)

### ۱.۱ رفع مسیر متریک Prometheus

- اندپوینت `/api/v1/monitoring/metrics/prometheus` قبلاً فقط یک **placeholder** برمی‌گرداند؛ Prometheus در `monitoring/prometheus.yml` هم به مسیر اشتباه و حتی jobهای غیرمتریک (پورت خام Postgres/Redis) اشاره می‌کرد.
- اکنون:
  - همان خروجی `prometheus_client` که در `GET /metrics` ریشه‌ی اپ است، از مسیر API هم در دسترس است (`get_metrics_response()`).
  - `monitoring/prometheus.yml` فقط `backend:8000` را با `metrics_path: /metrics` scrape می‌کند.
  - `monitoring/prometheus-advanced.yml` برای job بک‌اند به `/metrics` اصلاح شد.

### ۱.۲ پروفایل‌های Docker Compose (سبک‌سازی dev)

در `docker-compose.yml`:

- سرویس‌های **Prometheus + Grafana** زیر پروفایل `observability` قرار گرفتند.
- سرویس‌های **ELK** زیر پروفایل `elk` قرار گرفتند.

اجرای پیش‌فرض (فقط هسته):

```bash
docker compose up -d
```

با مانیتورینگ سبک:

```bash
docker compose --profile observability up -d
```

با لاگ متمرکز (سنگین):

```bash
docker compose --profile elk up -d
```

رمز Grafana از متغیر محیطی (با پیش‌فرض ناامن فقط برای dev):

```bash
export GRAFANA_ADMIN_PASSWORD='...'
docker compose --profile observability up -d
```

### ۱.۳ استک مانیتورینگ جدا (`monitoring/docker-compose.monitoring.yml`)

- فایل‌های گم‌شده‌ی **Loki** و **Promtail** اضافه شدند (`monitoring/loki/config.yml`, `monitoring/promtail/config.yml`).
- نسخه‌ی **Loki / Promtail** به خط `2.9.8` پین شد تا بازیابی DR قابل پیش‌بینی باشد.
- گزارش تحلیل Loki در کانفیگ غیرفعال شد (`analytics.reporting_enabled: false`).

اجرای پیشنهادی (بعد از بالا آوردن شبکه‌ی `neuropredict-network`):

```bash
docker network create neuropredict-network  # اگر وجود ندارد
docker compose -f monitoring/docker-compose.monitoring.yml up -d
```

---

## ۲. بکاپ (Backup)

### ۲.۱ اسکریپت زمان‌بندی‌شده

- `scripts/backup_postgres_scheduled.sh` (Linux/macOS/Git Bash)
- `scripts/backup_postgres_scheduled.ps1` (Windows)

هر دو:

1. `python backend/scripts/backup_database.py backup`
2. سپس `cleanup` با `KEEP_DAYS` (پیش‌فرض **۱۴** روز)

مسیر خروجی پیش‌فرض: `backups/db/` (نسبت به ریشه‌ی مخزن).

### ۲.۲ Git و داده‌ی حساس

- پوشه‌ی `backups/` به `.gitignore` اضافه شد تا **هرگز** дамپ حاوی PHI به مخزن push نشود.

### ۲.۳ Cron (Linux)

مثال روزانه ساعت 02:15:

```cron
15 2 * * * cd /opt/neuropredict && KEEP_DAYS=30 ./scripts/backup_postgres_scheduled.sh >> /var/log/neuropredict-backup.log 2>&1
```

### ۲.۴ Windows Task Scheduler

Action: `powershell.exe -File C:\path\to\repo\scripts\backup_postgres_scheduled.ps1`  
متغیرها: `POSTGRES_HOST`, `KEEP_DAYS`, `BACKUP_DIR` در صورت نیاز.

---

## ۳. DR (Disaster Recovery) — چک‌لیست عملیاتی

| مرحله | اقدام |
| ----- | ----- |
| **RPO** | حداکثر از دست رفتن داده: مثلاً ۲۴ ساعت → بکاپ حداقل روزانه + WAL archiving در prod (خارج از این اسپرینت). |
| **RTO** | زمان بازیابی: اندازه‌گیری با یک drill فصلی. |
| **بکاپ خارج از سایت** | کپی رمزنگاری‌شده‌ی `backups/db/` به Object Storage (S3 / Azure Blob) با IAM محدود. |
| **اسرار** | Docker Swarm/Kubernetes secrets؛ هرگز در compose ثابت نکنید (prod از `docker-compose.prod.yml` + secrets خارجی). |
| **تست بازیابی** | هر فصل یک بار `restore` روی محیط staging با `--backup-file` و تأیید دستی `yes`. |
| **مانیتورینگ حین بحران** | وضعیت `/health`، متریک‌های Prometheus، لاگ Loki/ELK. |
| **مستندات ارتباطات** | لیست وابستگی‌ها: Postgres، Redis، مدل‌ها، uploads. |

---

## ۴. سخت‌سازی زیرساخت (Hardening)

### ۴.۱ Docker

- `security_opt: no-new-privileges:true` روی `postgres`, `redis`, `backend`, `admin-dashboard`, `prometheus`, `grafana`.
- `backend/Dockerfile`: اجرای فرآیند با کاربر غیر root (`USER app`) و `chown` روی `/app`.
- پروفایل‌ها برای کاهش سطح حمله‌ی سطحی در محیط توسعه (سرویس‌های سنگین به‌صورت پیش‌فرض بالا نمی‌آیند).

### ۴.۲ Nginx

- هدرهای `Referrer-Policy` و `Permissions-Policy` به بلاک‌های SSL اضافه شدند (هم‌تراز با سرور API).

### ۴.۳ CI — اعتبارسنجی Compose

- Workflow جدید: `.github/workflows/infra-validate.yml`  
  دستور `docker compose ... config -q` برای:
  - `docker-compose.yml`
  - `monitoring/docker-compose.monitoring.yml`

---

## ۵. فایل‌های تغییر یافته / جدید (خلاصه)

| مسیر | توضیح |
| ----- | ----- |
| `backend/app/api/monitoring.py` | متریک واقعی Prometheus در `/metrics/prometheus` |
| `monitoring/prometheus.yml` | scrape صحیح `/metrics` |
| `monitoring/prometheus-advanced.yml` | مسیر بک‌اند اصلاح شد |
| `monitoring/loki/config.yml` | جدید |
| `monitoring/promtail/config.yml` | جدید |
| `monitoring/docker-compose.monitoring.yml` | پین Loki/Promtail |
| `docker-compose.yml` | پروفایل‌ها، `no-new-privileges`, Grafana env |
| `backend/Dockerfile` | کاربر غیر root |
| `nginx/nginx.conf` | هدرهای امنیتی تکمیلی |
| `scripts/backup_postgres_scheduled.*` | بکاپ + retention |
| `.gitignore` | نادیده گرفتن `backups/` |
| `.github/workflows/infra-validate.yml` | گیت CI برای compose |
| این سند | `docs/SPRINT_3_4_PLAN_FA.md` |

---

## ۶. فالواپ پیشنهادی (اسپرینت ۵+)

- WAL archiving و Point-in-Time Recovery برای Postgres در production.
- Trivy scan روی ایمیج‌های Docker در CI (شکست روی CRITICAL).
- رمزنگاری بکاپ در rest (age / gpg) قبل از آپلود به object storage.
- Grafana/IAM: غیرفعال کردن anonymous، SSO سازمانی.
- جدا کردن شبکه‌ی داخلی Compose (شبکه‌ی جدا برای DB از frontend).

**نسخه سند:** 1.0  
**وضعیت:** آماده‌ی merge و اجرای branch protection روی `Infra validate` در کنار CI اصلی
