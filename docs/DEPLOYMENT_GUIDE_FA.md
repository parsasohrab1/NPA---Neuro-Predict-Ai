## راهنمای دپلوی (Deployment Guide)

این راهنما مراحل دپلوی در محیط‌های Dev/Stage/Prod را با تمرکز بر امنیت و پایداری توضیح می‌دهد.


### پیش‌نیازها
- Docker و Registry امن، محیط اجرای هدف (VM/Kubernetes/PaaS)
- پایگاه‌داده PostgreSQL، Redis، فضای ذخیره فایل/شیء-استور
- Secret Store برای کلیدها/توکن‌ها (Vault/KMS/Cloud Secrets)


### تنظیمات محیط (Env Vars)
- Backend (`backend/app/core/config.py` می‌خواند):
  - `SECRET_KEY`, `DATABASE_URL`, `REDIS_HOST/PORT/DB`
  - مسیرها: `UPLOAD_DIR`, `DICOM_DIR`, `MRI_DIR`, `REPORTS_DIR`
  - ریت‌لیمیت: `RATE_LIMIT_*` (در صورت نیاز)
- Frontend: `VITE_API_BASE_URL`, `LANG/RTL`, متاها در `index.html`


### ساخت و انتشار تصاویر
- Backend:
  ```bash
  docker build -t registry/app-backend:1.0.0 .
  docker push registry/app-backend:1.0.0
  ```
- Frontend/Admin:
  ```bash
  docker build -t registry/app-frontend:1.0.0 .
  docker push registry/app-frontend:1.0.0
  ```


### دپلوی روی Stage
- پایگاه‌داده/Redis آماده و در دسترس
- اجرای Migration (در صورت فعال‌سازی Alembic)
- استقرار Backend/Frontend با image tag مشخص
- Health/Readiness/Liveness بررسی شود؛ Smoke Tests + DAST سبک


### دپلوی روی Prod
- تایید دستی و برنامه Rollback آماده
- استراتژی دپلوی: Rolling یا Blue-Green/Canary (ترجیح برای انتشارهای بزرگ)
- مانیتورینگ نزدیک: p95 latency/error rate/uptime و گزارش رخدادها


### Rollback
- Backend/Frontend: بازگشت به image برچسب قبل
- Migration‌ها: الگوی Expand/Contract؛ در صورت نیاز، rollback امن
- اطلاع‌رسانی و ثبت اقدامات


### امنیت و انطباق
- TLS همه‌جا، CSP، هدرهای امنیتی، RBAC، Rate Limiting
- اسرار فقط از Secret Store؛ لاگ بدون PII/PHI
- تست سلامت بکاپ‌ها و DR Drill مطابق برنامه


### چک‌لیست سریع
- [ ] Env Vars تنظیم و اسرار در Secret Store
- [ ] Images ساخته و در Registry امن منتشر شد
- [ ] DB/Redis/Storage آماده و Health OK
- [ ] Stage: Smoke/DAST OK → Prod با تایید دستی
- [ ] Rollback و مانیتورینگ فعال


