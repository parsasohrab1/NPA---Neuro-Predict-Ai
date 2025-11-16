## راهنمای توسعه‌دهنده

این راهنما مراحل راه‌اندازی، معماری کد، استانداردها، تست، و نکات توسعه را پوشش می‌دهد.


### راه‌اندازی سریع (Backend)
1) پیش‌نیاز: Python 3.11+, PostgreSQL, Redis
2) ساخت محیط و نصب:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
3) تنظیم `.env` (نمونه در `backend/app/core/config.py` توصیف شده) شامل `SECRET_KEY`, `DATABASE_URL`, `REDIS_*`
4) اجرا:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
5) مستندات: در حالت DEBUG → `/api/docs`


### راه‌اندازی سریع (Frontend)
1) Node 18+
2) نصب و اجرا:
   ```bash
   cd frontend
   npm ci
   npm run dev
   ```
3) تنظیم `VITE_API_BASE_URL` در `.env` فرانت‌اند (در صورت نیاز)


### معماری کد Backend
- `app/api`: Routers (کنترلرها، RBAC با `require_role`)
- `app/schemas`: Pydantic DTOها (Create/Update/Response)
- `app/services`: منطق دامنه (AI/Reports/Longitudinal/Integration/Monitoring)
- `app/models`: ORM (SQLAlchemy), روابط و ایندکس‌ها
- `app/core`: Config/Security/Cache/Middleware
- `app/db`: Session و Base
- `app/main.py`: راه‌اندازی، میدلورها، ثبت Routerها


### استانداردها
- کدنویسی: خوانا، بدون `any`، نام‌گذاری معنادار، early-return
- امنیت: عدم لاگ اسرار/PII/PHI؛ JWT+RBAC؛ Rate Limiting
- کارایی: جلوگیری از N+1 (selectinload)، ایندکس‌ها، کش نتایج پرتکرار
- لاگ/متریک: لاگ ساختاریافته، متریک‌ها و هشدارها
- ADR: تصمیمات معماری در `docs/ADR/`


### تست
- Backend:
  ```bash
  cd backend
  pytest -q
  ```
  - فیکچرهای آماده در `backend/tests/conftest.py`
  - پوشش هدف اولیه ≥ 60%
- Frontend: Vitest/Jest + RTL (در صورت افزودن)
- E2E: Playwright/Cypress (Stage)


### توسعه فیچر جدید (چک‌لیست)
- [ ] اسکیماهای Pydantic (Create/Update/Response) و مدل/ایندکس
- [ ] Router + RBAC + کش (در صورت نیاز)
- [ ] سرویس دامنه + تست واحد/یکپارچه
- [ ] لاگ/متریک و هندل خطا با `trace_id`
- [ ] به‌روزرسانی Docs/API Reference/ADR (در صورت تغییر معماری)


### خطایابی
- استفاده از `X-Request-ID` برای رهگیری انتهابه‌انتها
- لاگ سطح DEBUG فقط در Dev
- بررسی `redis` برای کش/ریت‌لیمیت و صحت اتصال DB


### استقرار و عملیات
- CI: lint/test/build + SAST
- Stage: Smoke + DAST سبک → Prod با تایید دستی
- دپلوی: Rolling/Blue-Green/Canary (بر اساس `docs/CICD_AND_DEPLOY_STRATEGIES_FA.md`)


### منابع
- API Reference: `docs/API_REFERENCE_FA.md`
- استانداردها و نسخه‌بندی: `docs/API_STANDARDS_AND_VERSIONING_FA.md`
- قرارداد/خطا: `docs/API_CONTRACTS_AND_ERROR_HANDLING_FA.md`
- امنیت و حریم خصوصی: `docs/SECURITY_PRIVACY_COMPLIANCE_FA.md`
- ADR Index: `docs/ADR/index-fa.md`


