## محیط‌ها (Dev/Stage/Prod) و IaC (Terraform/…)

### استاندارد محیط‌ها
- Dev (توسعه):
  - هدف: سرعت توسعه و آزمایش محلی.
  - ابزار: `docker-compose` (API/DB/Redis/Prom/Grafana)، داده مصنوعی، لاگ سطح DEBUG.
  - امنیت: اسرار محلی امن (env file خارج از Git)، TLS اختیاری، CORS بازتر (کنترل‌شده).
- Stage (پیش‌تولید/QA):
  - هدف: اعتبارسنجی End-to-End قبل از تولید.
  - پیکربندی نزدیک به Prod، داده شبه‌واقعی، لاگ INFO، مانیتورینگ فعال، DAST کامل شبانه.
  - امنیت: TLS فعال، CSP Report-Only، Rate Limit مشابه Prod، اسرار از Secret Store.
- Prod (تولید):
  - هدف: پایداری/مقیاس/امنیت.
  - TLS اجباری، CSP سخت‌گیرانه، هدرهای امنیتی کامل، Rate Limit چندسطحی.
  - مانیتورینگ/HPA/بکاپ/DR Drill، اسرار در Secret Store و Rotation دوره‌ای.


### پیکربندی و اسرار
- تفکیک Env Vars برای هر محیط؛ `.env.example` بدون مقادیر حساس.
- Secret Store (Vault/KMS/Cloud Secrets) در Stage/Prod.
- نسخه‌بندی پیکربندی‌ها بدون افشای اسرار (GitOps-friendly).


### استقرار و شبکه
- Orchestration: Kubernetes (پیشنهادی) یا PaaS/VM با Systemd.
- Health/Readiness/Liveness برای سرویس‌ها.
- شبکه: لایه لبه (TLS termination/WAF)، فایروال/NSG، ساب‌نت‌های خصوصی برای DB/Redis.


### IaC (Infrastructure as Code)
- Terraform:
  - منابع: شبکه (VPC/Subnets/Security Groups)، پایگاه‌داده مدیریت‌شده، Redis، شیء-استور، Load Balancer، DNS، مانیتورینگ.
  - State: ریموت (S3/GCS + Locking با DynamoDB/Cloud-native).
  - ماژولار: ماژول‌های تکرارپذیر برای محیط‌ها؛ متغیرها/ورودی‌ها از Workspace/TFVars.
  - سیاست‌ها: برچسب‌گذاری (tags) برای هزینه/مالک، حداقل مجوزهای سرویس.
- Ansible (گزینشی):
  - پیکربندی OS/Agents/Collectors و استقرار غیرکانتینری.


### CI/CD پیوسته با محیط‌ها
- CI: lint/test/build + SAST در PR/main.
- CD:
  - Stage: استقرار خودکار پس از قبولی CI، اجرای DAST/Smoke Tests.
  - Prod: تایید دستی، rollout تدریجی (Rolling/Blue-Green)، مانیتورینگ نزدیک.
- Artefacts: Docker images با برچسب `app:version-gitsha`، امضای تصویر (در فاز بعد).


### مشاهده‌پذیری و امنیت
- متریک‌ها: Latency/Errors/RPS/Resources؛ داشبوردهای مستقل برای هر محیط.
- لاگ‌ها: سطح مناسب محیط، نگهداشت متفاوت (Dev کوتاه، Prod طولانی‌تر).
- امنیت: RBAC سرتاسری، هدرهای امنیتی، CSP، ریت‌لیمیت، ممیزی عملیات حساس.


### سیاست‌های داده و بکاپ
- Dev: داده مصنوعی، بدون PHI/PII واقعی.
- Stage: شبه‌واقعی/ناشناس‌سازی‌شده؛ بکاپ سبک.
- Prod: RPO/RTO مشخص، بکاپ رمزگذاری‌شده، DR Drill دوره‌ای.


### الگوی نام‌گذاری و DNS
- دامنه‌ها:
  - Dev: `dev.example.com`
  - Stage: `stage.example.com`
  - Prod: `app.example.com` (یا `api.example.com`/`admin.example.com`)
- برچسب‌گذاری منابع: `env=dev|stage|prod`, `service=api|frontend|admin`, `owner=team`


### مسیر پیشنهادی پیاده‌سازی
- گام 1: Compose توسعه + Env Vars تفکیک‌شده + Secret handling پایه.
- گام 2: Terraform ماژولار برای شبکه/DB/Redis/Storage، State ریموت، Stage پایدار.
- گام 3: CD به Stage + DAST/Smoke؛ Prod با تایید دستی و مانیتورینگ.
- گام 4: HPA/Alerting، CSP سخت‌گیرانه، IaC کامل (Monitoring/DNS/WAF)، OTel.


### چک‌لیست سریع
- [ ] تفکیک کامل پیکربندی محیط‌ها + Secret Store در Stage/Prod
- [ ] Terraform با State ریموت + ماژول‌های محیطی + برچسب‌گذاری
- [ ] CI/CD: Stage خودکار، Prod با تایید، Rollout تدریجی
- [ ] TLS، CSP، Rate Limit، هدرهای امنیتی در Stage/Prod
- [ ] مانیتورینگ/هشدارها، نگهداشت لاگ/متریک بر اساس محیط
- [ ] RPO/RTO و DR Drill متناسب با محیط‌ها

