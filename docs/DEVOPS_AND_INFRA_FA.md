## DevOps و زیرساخت

### اهداف
- استقرار قابل اعتماد، مقیاس‌پذیر و امن با بازخورد سریع (CI/CD)، مشاهده‌پذیری کامل و هزینه قابل کنترل.


### محیط‌ها و پیکربندی
- محیط‌ها: DEV، TEST/QA، STAGE، PROD
- پیکربندی از طریق Env Vars؛ جداسازی کامل اسرار و تنظیمات هر محیط
- نمونه فایل‌ها: `.env.example` (بدون مقادیر حساس)


### کانتینری‌سازی و اجرا
- Docker برای backend/frontend/admin-dashboard
- docker-compose برای توسعه محلی (DB/Redis/Prom/Grafana)
- تولید: Orchestrator (Kubernetes/Swarm) یا PaaS (گزینشی)
- Health/Readiness/Liveness برای سرویس‌ها


### CI/CD
- CI: lint + test + build (Backend/Frontend) در Pull Request و main
- امنیت در CI: SAST (bandit/npm audit/secrets scan) و DAST سبک/Stage
- Artefact‌ها: تصاویر Docker نسخه‌بندی‌شده (tag: git SHA + semver)
- CD: 
  - STAGE: استقرار خودکار پس از قبولی CI
  - PROD: تایید دستی (manual approval) + rollout تدریجی
- استراتژی استقرار: Rolling/Blue-Green (فازهای بعد)


### مانیتورینگ و لاگینگ
- Observability: Prometheus (متریک)، Grafana (داشبورد)، Logstash/Elastic (لاگ)
- متریک‌ها: Latency (p50/p95/p99)، Error Rate، RPS، منابع (CPU/Mem/DB/Redis)
- هشداری‌ها: آستانه‌های SLO (Latency/Error/Uptime)، ظرفیت DB/Redis، Queue depth
- تریسینگ: OpenTelemetry + Collector (فاز بعد) به Jaeger/Tempo


### شبکه و امنیت
- TLS همه‌جا، هدرهای امنیتی، CORS محدود، WAF (اختیاری)
- Rate Limiting مبتنی بر Redis؛ سیاست‌های متفاوت برای مسیرهای حساس
- Firewall/NSG: محدودسازی درگاه‌ها و دسترسی فقط سرویس به سرویس
- SSO/OIDC (فاز بعد)، MFA برای نقش‌های حساس


### پایگاه‌داده و ذخیره‌سازی
- PostgreSQL با ایندکس‌گذاری مناسب، جلوگیری از N+1 (eager loading)
- Backup/Restore با RPO/RTO مشخص؛ DR Drill دوره‌ای
- فایل‌ها: گزارش‌ها/تصاویر روی فایل‌سیستم در DEV، شیء-استور در PROD (S3/MinIO)
- کش: Redis برای پاسخ‌های خواندنی پرتکرار و Rate Limit


### مقیاس‌پذیری و ظرفیت
- API stateless با replica و HPA بر اساس CPU/Latency
- جداسازی مسیرهای سنگین (آپلود/پیش‌بینی) و صف آسنکرون در فاز بعد
- Read/Write Split در DB و پارتیشن‌بندی جداول حجیم (فازهای بعد)


### IaC و مدیریت تنظیمات
- IaC: Terraform/Ansible (گزینشی) برای شبکه، DB، Redis، شیء-استور، مانیتورینگ
- Secret Management: Vault/KMS/Cloud Secrets؛ Rotation دوره‌ای
- Registry: Docker Registry خصوصی/مدیریت‌شده


### امنیت و انطباق
- RBAC سرتاسری (اپ/زیرساخت)، ممیزی عملیات حساس
- رمزنگاری در انتقال/سکون، DSR/DPIA طبق اسناد امنیتی
- اسکن وابستگی‌ها، Patch Management، حداقل‌گرایی سطح دسترسی


### هزینه و بهینه‌سازی
- منابع پویا (Auto-Scaling) و خاموشی محیط‌های غیرفعال خارج ساعات کاری
- لاگ‌های سطح DEBUG فقط در DEV
- استفاده از TTL/Retention برای متریک/لاگ/بکاپ‌ها


### Runbooks و عملیات
- رخداد: ارزیابی، ایزوله، رفع (break-glass)، ثبت RCA
- ظرفیت: بازبینی دوره‌ای آستانه‌ها و تنظیم replica/HPA
- تغییر: Change Management با ثبت تاثیر/بازگشت سریع (rollback)


### نقشه راه
- MVP: CI پایه، Docker، Compose محلی، Health/Logs، متریک‌های پایه
- فاز 2: CD به STAGE، هشدارها، داشبوردهای غنی، صف آسنکرون برای وظایف سنگین
- فاز 3: استقرار بدون وقفه، OTel، IaC کامل، SSO/MFA، Read/Write Split، شیء-استور


