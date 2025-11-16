## CI/CD و استراتژی‌های دپلوی (Blue-Green/Canary)

### اهداف
- تحویل سریع و ایمن با کمترین وقفه، قابلیت بازگشت سریع، و کنترل ریسک تغییرات.


### CI (Continuous Integration)
- Trigger: Pull Request و push به main
- مراحل:
  - Lint/Format: Backend (flake/ruff اختیاری)، Frontend (eslint/prettier)
  - Tests: واحد و یکپارچه؛ گزارش پوشش
  - Security: SAST (bandit, npm audit, secrets scan) و وابستگی‌ها
  - Build: تصاویر Docker نسخه‌بندی‌شده (`app:version-gitsha`)
  - Artefacts: انتشار image به Registry خصوصی/مدیریت‌شده
- بهترین‌عمل‌ها:
  - Parallelization، caching (pip/npm/docker layers)
  - Fail-fast روی High/Critical
  - Policy برای حجم لاگ و نگهداشت گزارش‌ها


### CD (Continuous Delivery/Deployment)
- محیط‌ها:
  - Stage: استقرار خودکار پس از قبولی CI + DAST/Smoke Tests
  - Prod: تایید دستی، rollout کنترل‌شده، پایش نزدیک
- پیکربندی:
  - Env Vars از Secret Store، image tags از CI
  - Health/Readiness/Liveness probes
  - Rollback با یک کلیک/اسکریپت


### استراتژی‌های دپلوی
- Rolling Update (پایه):
  - جایگزینی تدریجی پادها/سرویس‌ها با نسخه جدید
  - مزایا: ساده، بدون منابع دوبرابر
  - معایب: در صورت بروز ایراد در میانه rollout، تاثیر روی بخشی از ترافیک

- Blue-Green:
  - دو محیط موازی (Blue=فعلی، Green=جدید)، سوییچ ترافیک ناگهانی
  - مزایا: قطع سرویس حداقلی، rollback بسیار سریع
  - معایب: نیاز به منابع تقریباً دوبرابر، مدیریت داده/مهاجرت پیچیده‌تر
  - توصیه: برای تغییرات بزرگ/ریسکی یا نسخه‌های مدل جدید

- Canary:
  - درصد کمی از ترافیک به نسخه جدید (مثلاً 5% → 25% → 50% → 100%)
  - مزایا: پایش تدریجی اثر تغییر، کنترل دقیق ریسک
  - معایب: پیاده‌سازی پیچیده‌تر (Route/Service Mesh/Ingress هوشمند)
  - توصیه: برای انتشارهای مکرر، وقتی متریک‌ها و هشدارها خوب تنظیم شده‌اند


### پایش و معیارهای موفقیت در دپلوی
- SLI/SLOهای کلیدی: Latency (p95/p99)، Error Rate، Uptime، RPS
- بُرش‌های رصد: endpointهای حساس (auth/patients/predictions/imaging/upload)
- Error Budget: توقف rollout در صورت عبور از آستانه‌های خطا
- مسیرهای گزارش: کانال تیم/داشبورد Prod برای وضعیت rollout


### Rollback
- محرک‌ها: خطاهای 5xx/4xx بحرانی، Latency غیرعادی، خرابی سلامت
- روش‌ها:
  - Rolling: بازگشت به image قبل
  - Blue-Green: سوییچ فوری به محیط Blue
  - Canary: بازگرداندن درصد ترافیک به نسخه پایدار
- Runbook: چک‌لیست rollback + اعلان به ذی‌نفعان + RCA بعد از تثبیت


### مدیریت Schema/Migrations در دپلوی
- الگو Expand/Contract:
  - مرحله 1 (Expand): افزودن ستون/ایندکس سازگار به عقب
  - Backfill داده در پس‌زمینه
  - مرحله 2 (Contract): اعمال قیود نهایی/حذف قدیمی پس از اطمینان
- نکته: Blue-Green/Canary با تغییرات Schema باید سازگار به عقب باشد تا سوییچ/درصدگذاری ایمن بماند


### امنیت CI/CD
- Secrets در Secret Store، PoLP برای runnerها و Registry
- امضای تصاویر Docker (SLSA در فاز بعد)، اسکن وابستگی‌ها و image
- ممیزی Deploymentها، لاگ رخدادهای CD، تایید دستی Prod


### نمونه گردش کار (روی GitHub Actions – پیشنهادی)
- CI (on PR/main):
  - jobs: backend-lint-test, frontend-lint-test, sast, build-and-push-image
- CD Stage (on push main):
  - jobs: deploy-stage → run smoke + zap-light
- CD Prod (manual):
  - jobs: deploy-prod (strategy: blue-green/canary via Ingress/Service Mesh)


### چک‌لیست سریع
- [ ] CI کامل با lint/test/build + SAST و اسکن image
- [ ] Registry امن، برچسب‌گذاری نسخه‌ها، Rollback سریع
- [ ] Stage خودکار + DAST/Smoke، Prod با تایید دستی
- [ ] انتخاب استراتژی دپلوی (Blue-Green/Canary) بر اساس ریسک/منابع
- [ ] پایش SLOها حین rollout، توقف خودکار در عبور از آستانه
- [ ] مدیریت مهاجرت‌های Schema با Expand/Contract

