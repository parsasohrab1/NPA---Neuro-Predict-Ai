## کیفیت و تست

### اهداف
- اطمینان از صحت عملکرد، جلوگیری از رگرسیون، افزایش اعتماد به استقرارهای مکرر، و کاهش MTTR.


### هرم تست (Test Pyramid)
- Unit Tests (زیاد): منطق خالص، سرویس‌ها، اسکیماها، کم‌هزینه و سریع.
- Integration Tests (متوسط): API + DB/Redis واقعی (یا in-memory)، گردش‌های کلیدی.
- E2E/UI Tests (کم): سناریوهای کاربر از طریق مرورگر (Playwright/Cypress)، مسیرهای حیاتی.


### ابزارها و چارچوب‌ها
- Backend: pytest + pytest-asyncio، httpx/fastapi TestClient، factory/faker، coverage.
- Frontend: Vitest/Jest + React Testing Library، Playwright/Cypress برای E2E.
- Static Analysis: ruff/flake8/bandit (Py)، eslint/prettier (TS)، secrets scan (gitleaks).


### دامنه تست‌ها (Backend)
- واحد:
  - سرویس‌ها: ai_model_service, reporting_service, integration_service, longitudinal_service
  - اعتبارسنجی Schemas (Pydantic) و تبدیل‌ها
  - منطق امنیتی کمکی (بدون اسرار واقعی)
- یکپارچه:
  - API: patients, predictions, imaging, reports, longitudinal, products
  - RBAC: require_role و سناریوهای دسترسی
  - کش: get/set/invalidate الگوهای پرکاربرد
  - DB: CRUD با داده نمونه و ایندکس‌های مهم
- قراردادی (گزینشی):
  - قراردادهای Integrations (mocks/stubs) برای HIS/PACS/webhook


### دامنه تست‌ها (Frontend)
- واحد: کامپوننت‌ها، هوک‌ها و منطق نمایشی
- یکپارچه: صفحات کلیدی، روتینگ، فرم‌ها و اعتبارسنجی‌ها
- E2E: مسیرهای حیاتی (ورود، ثبت بیمار، آپلود تصویر، ایجاد پیش‌بینی، دانلود گزارش)


### داده تست و فیکسچرها
- داده مصنوعی/ناشناس‌سازی‌شده؛ عدم استفاده از PHI/PII واقعی
- فیکسچرهای pytest برای DB/Redis/کاربر تست و seed داده
- استراتژی Seed قابل تکرار برای پایگاه داده تست


### پوشش و معیارها
- پوشش هدف اولیه: ≥ 60% (Backend/Frontend)، افزایش تدریجی به 75%+
- معیارهای CI: عبور همه تست‌ها، عبور SAST/DAST پایه، عدم افت شدید پوشش


### تست‌های کارایی و بار (گزینشی)
- سناریوهای سبک برای p95 latency مسیرهای patients/predictions/imaging
- ابزارها: k6/locust (گزینشی)، Threshold بر اساس SLO


### CI و اجرای خودکار
- روی Pull Request: unit + integration سریع، lint، SAST، (E2E سبک اختیاری)
- روی main/Stage: suite کامل + DAST سبک، گزارش پوشش، artefact‌ها
- گزارش‌ها: ذخیره نتایج/کاورج و لاگ‌ها به‌صورت قابل دانلود


### استراتژی جلوگیری از رگرسیون
- افزودن تست همزمان با رفع باگ/افزودن فیچر
- Snapshot تست برای API/UI (با احتیاط)، و تست قرارداد برای Integrations
- Feature flags برای انتشار تدریجی و تست A/B (در صورت نیاز)


### کنترل کیفیت (QA) و بازبینی
- Code Review اجباری، چک‌لیست امنیت/کارایی/قابلیت نگهداری
- QA روی Stage با داده شبه‌واقعی، سناریوهای دستی Documented برای مسیرهای حساس
- پایش Production بعد از استقرار (Canary/Blue-Green) و رول‌بک سریع


### چک‌لیست سریع
- [ ] تست واحد/یکپارچه برای مسیرهای کلیدی Backend
- [ ] تست واحد UI و حداقل چند سناریو E2E
- [ ] lint + SAST در CI، DAST سبک در Stage
- [ ] پوشش حداقل 60% و مسیر ارتقا
- [ ] داده تست مصنوعی و فیکسچرهای قابل تکرار
- [ ] تست بار سبک برای مسیرهای حیاتی با Thresholdهای SLO

