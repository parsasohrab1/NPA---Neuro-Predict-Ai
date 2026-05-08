# اسپرینت ۱–۲ — تست‌ها، امنیت پایه و گیت‌های CI

این سند تحویل‌شدنی‌های اسپرینت ۱ و ۲ پروژه‌ی NeuroPredict-AI رو خلاصه می‌کنه.
هدف: گذاشتن یک «سقف کیفی» قابل اتکا روی هر PR قبل از این‌که به merge برسه؛
نه چیز بیشتر، نه چیز کمتر.

---

## ۱. خلاصه‌ی یک‌نگاه

| محور | قبل از این اسپرینت | بعد از این اسپرینت |
| ---- | ----------------- | ----------------- |
| فایل `ci.yml` | شامل **دو** workflow هم‌نام، نامعتبر | یک workflow معتبر و واحد |
| `tests.yml` و `security-scan.yml` | با مسیر اشتباه `./NPA---Neuro-Predict-Ai/backend` | اولی حذف شد، دومی اصلاح شد |
| اسکن اسرار (gitleaks) | با `\|\| true` (هیچ‌وقت fail نمی‌کرد) | گیت سختگیر، مرتبط به `gitleaks-action@v2` |
| اسکن SAST | bandit با `\|\| true` | `bandit -lll` (HIGH = صفر) — fail می‌کنه |
| اسکن وابستگی پایتون | نداشتیم | `pip-audit --strict` در CI |
| اسکن وابستگی Node | `\|\| true` | `npm audit --omit=dev --audit-level=high` — fail می‌کنه |
| Lint بک‌اند | نداشتیم | `ruff check app` |
| Type-check فرانت‌ها | فقط در `build` | step مستقل `typecheck` |
| تست‌های فرانت | **هیچ‌چیز** | Vitest + Testing Library + smoke tests |
| تست اسموک بک‌اند | نداشتیم | `tests/test_smoke.py` (همیشه باید سبز باشه) |
| Coverage gate | `--cov-fail-under=80` در `pytest.ini` (در عمل اعمال نمی‌شد) | حداقل ۴۰٪ روی unit در CI، با برنامه‌ی افزایش تدریجی |
| CodeQL | نداشتیم | روی Python و JS/TS، هر push + هفتگی |
| Dependabot | نداشتیم | روی pip / npm / GitHub Actions / Docker |
| Pre-commit hooks | نداشتیم | gitleaks + ruff + bandit + پاک‌سازی فایل |
| `SECURITY.md` | نداشتیم | اضافه شد |
| `CODEOWNERS` | نداشتیم | اضافه شد |
| قالب PR / Issue | نداشتیم | اضافه شد |

---

## ۲. اسپرینت ۱ — تست‌ها و امنیت پایه

### ۲.۱ زیرساخت تست بک‌اند

- `backend/tests/test_smoke.py` اضافه شد. این تست‌ها **بدون نیاز به دیتابیس / Redis / مدل** اجرا می‌شن و هدفشون فقط اینه که گراف import سالم باشه و کانفیگ امنیتی پایه (مثل `SECRET_KEY` ≥ 32 و `DEBUG=False` در محیط‌های غیر-dev) رعایت بشه.
- `backend/pyproject.toml` اضافه شد:
  - تنظیمات `ruff` (مجموعه‌ی محافظه‌کار: `E9`, `F`, `B`, `I`)
  - تنظیمات `bandit` (هم‌راستا با CI: HIGH-only)
- در CI، اسموک تست‌ها قبل از سوئیت اصلی اجرا می‌شن تا اگه چیزی در مسیر import شکسته باشه، شکست خیلی زود و خوانا گزارش بشه.

### ۲.۲ زیرساخت تست فرانت‌اندها

روی هر دوی `frontend/` و `admin-dashboard/`:

- اضافه شدن Vitest + jsdom + `@testing-library/react` + `@testing-library/jest-dom` + `@testing-library/user-event` + `@vitest/coverage-v8`.
- `vitest.config.ts` مستقل (نه merge با `vite.config.ts`) برای پرهیز از side-effectهای dev-server (proxy/WebSocket).
- `src/test/setup.ts` با `cleanup` خودکار بعد از هر تست.
- اولین smoke test (`src/__tests__/smoke.test.tsx`) که فقط toolchain رو اعتبارسنجی می‌کنه.
- اسکریپت‌های `test`، `test:coverage`، `typecheck` در `package.json`.
- در `admin-dashboard` که PostCSS/Tailwind داشت ولی `autoprefixer` و `postcss` در devDeps نبود، اون‌ها هم اضافه شدن (یک باگ صامت قبلی).

### ۲.۳ امنیت پایه

- `SECURITY.md` در ریشه با policy گزارش آسیب‌پذیری.
- `.pre-commit-config.yaml`:
  - `gitleaks` (اسرار)
  - `ruff` (با `--fix`)
  - `bandit -lll` روی `backend/app`
  - hookهای استاندارد: trailing whitespace, EOF newline, large files, merge conflict, private key detection.
- `.gitleaks.toml` با allowlist محدود برای فیکسچرهای تست و کلیدهای سینتتیک CI.
- `.github/dependabot.yml` با گروه‌های minor/patch:
  - `pip` در `backend/`
  - `npm` در `frontend/` و `admin-dashboard/`
  - `github-actions` در `/`
  - `docker` در هر سه context
- `.github/workflows/codeql.yml` برای SAST روی Python و JS/TS.

---

## ۳. اسپرینت ۲ — گیت‌های CI

### ۳.۱ بازنویسی `ci.yml`

`/.github/workflows/ci.yml` به یک workflow معتبر و واحد تبدیل شد با این job‌ها:

1. **`backend`** (Postgres + Redis services)
   - `ruff check app`
   - `bandit -lll` (HIGH = صفر)
   - `pip-audit --strict` روی `requirements.txt`
   - `pytest tests/test_smoke.py --no-cov` (smoke gate)
   - `pytest tests/ --ignore=tests/e2e --ignore=tests/integration --ignore=tests/performance --cov-fail-under=40`
   - آپلود `coverage.xml` به‌عنوان artifact.
2. **`frontend`** با matrix (`frontend`, `admin-dashboard`):
   - `npm ci`
   - `npm run lint --if-present`
   - `npm run typecheck --if-present`
   - `npm test --if-present -- --run`
   - `npm run build`
   - `npm audit --omit=dev --audit-level=high`  *(گیت سخت — نسبت به PR قبلی که با `\|\| true` بود)*
3. **`secrets-scan`**: `gitleaks-action@v2` با `fetch-depth: 0` و `GITHUB_TOKEN` (دیگه silent نیست).
4. **`docker-build`**: ساخت ایمیج‌های `backend`/`frontend`/`admin-dashboard` بدون push (اعتبارسنجی Dockerfile).

### ۳.۲ هم‌سویی workflow‌های دیگه

- `tests.yml` (شکسته، duplicate) **حذف شد**.
- `security-scan.yml`:
  - مسیرهای اشتباه `./NPA---Neuro-Predict-Ai/backend` به `backend/` اصلاح شد.
  - گزارش‌های Bandit / Safety / Semgrep / **pip-audit** به‌صورت artifact آپلود می‌شن.
  - زمان‌بندی هفتگی (Cron دوشنبه) حفظ شد.
- `codeql.yml` اضافه شد (Python + JS/TS، هفتگی + هر PR).

### ۳.۳ Concurrency و دیگر تنظیمات

- `concurrency.group: ci-${{ github.ref }}` با `cancel-in-progress: true`؛ هر push روی همون branch، runهای قبلی رو لغو می‌کنه (صرفه‌جویی در GitHub Actions minutes).
- `permissions: contents: read` به‌عنوان پیش‌فرض حداقلی (least privilege).
- timeout روی هر job (کف ۵، سقف ۲۵ دقیقه).

### ۳.۴ Branch protection پیشنهادی (در GitHub UI تنظیم بشه)

روی branchهای `main` و `develop` این status check‌ها رو required کنید:

- `backend`
- `frontend (frontend)` و `frontend (admin-dashboard)`
- `secrets-scan`
- `docker-build`
- `Analyze (python)` و `Analyze (javascript-typescript)` (CodeQL)

و این تنظیمات:

- Require pull request before merging
- Require approvals: حداقل ۱
- Dismiss stale approvals on new commits
- Require linear history
- Require signed commits (اختیاری ولی توصیه‌شده برای تیم پزشکی)

---

## ۴. لیست فایل‌های اضافه/تغییر یافته

```text
.github/CODEOWNERS                              (new)
.github/dependabot.yml                          (new)
.github/ISSUE_TEMPLATE/bug_report.md            (new)
.github/ISSUE_TEMPLATE/feature_request.md       (new)
.github/pull_request_template.md                (new)
.github/workflows/ci.yml                        (rewritten)
.github/workflows/codeql.yml                    (new)
.github/workflows/security-scan.yml             (fixed)
.github/workflows/tests.yml                     (deleted, broken duplicate)
.gitleaks.toml                                  (new)
.pre-commit-config.yaml                         (new)
SECURITY.md                                     (new)
backend/pyproject.toml                          (new)
backend/tests/test_smoke.py                     (new)
frontend/package.json                           (test deps + scripts)
frontend/package-lock.json                      (regenerated)
frontend/vitest.config.ts                       (new)
frontend/src/test/setup.ts                      (new)
frontend/src/__tests__/smoke.test.tsx           (new)
admin-dashboard/package.json                    (test deps + postcss/autoprefixer + scripts)
admin-dashboard/package-lock.json               (regenerated)
admin-dashboard/vitest.config.ts                (new)
admin-dashboard/src/test/setup.ts               (new)
admin-dashboard/src/__tests__/smoke.test.tsx    (new)
docs/SPRINT_1_2_PLAN_FA.md                      (this file)
```

---

## ۵. کارهای فالواپ پیشنهادی (اسپرینت ۳ به بعد)

این اسپرینت عمداً «سقف کف» گذاشته. مرحله‌ی بعد:

1. **بالا بردن coverage gate**: از ۴۰٪ به ۶۰٪ → ۷۵٪ در سه اسپرینت بعدی.
2. **افزودن تست‌های واقعی فرانت** برای: LoginPage، PredictionResultPage، ExplainabilityWidget.
3. **افزودن تست‌های واقعی auth/predictions** در بک‌اند با fixtureهای موجود `conftest.py`.
4. **فعال کردن `pre-commit ci`** (یا `lefthook`) تا قبل از push اجرا بشه.
5. **افزودن DAST سبک** (ZAP baseline) به‌عنوان job اختیاری روی PR (الان فقط در یکی از فایل‌های قدیمی بود).
6. **Trivy روی ایمیج‌های Docker** بعد از build، با شکست روی CRITICAL.
7. **افزودن SBOM** (CycloneDX یا Syft) و آپلود به‌عنوان artifact هر release.
8. **سختگیر کردن ruff** (افزودن `S` (bandit-style)، `UP`، `RUF`) و باندل با pre-commit.
9. **به‌روزرسانی Vite به ۵.۴+** (یا ۷.x) برای رفع آسیب‌پذیری moderate ثبت‌شده در `SECURITY_VULNERABILITIES_REPORT.md`.

---

## ۶. اجرای محلی

```bash
# Backend (پیش‌نیاز: Python 3.11)
cd backend
pip install -r requirements.txt
pip install ruff bandit pip-audit
ruff check app
bandit -r app -lll
pip-audit -r requirements.txt --strict
pytest tests/test_smoke.py -q --no-cov

# Frontend
cd frontend
npm ci
npm run lint
npm run typecheck
npm test -- --run
npm run build

# Admin dashboard
cd admin-dashboard
npm ci
npm run typecheck
npm test -- --run
npm run build

# Pre-commit (یک‌بار)
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

**نسخه‌ی سند:** ۱.۰  
**وضعیت:** Sprint 1–2 آماده‌ی merge / فعال‌سازی Branch Protection
