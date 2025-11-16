## تست امنیتی (SAST/DAST) و سیاست‌های امنیت محتوا (CSP)

### اهداف
- پیشگیری از آسیب‌پذیری‌ها پیش از استقرار (Shift-Left)، کشف مسائل زمان اجرا، و کاهش ریسک XSS/Clickjacking با CSP.


### SAST (Static Application Security Testing)
- دامنه:
  - Backend (Python): بررسی وابستگی‌ها (pip/audit)، تحلیل کد (bandit), secrets scan (trufflehog/gitleaks).
  - Frontend (JS/TS): بررسی وابستگی‌ها (npm/yarn audit)، lint امنیتی و تحلیل باندل.
- ادغام CI:
  - اجرا در Pull Request و در main؛ شکست Build روی آسیب‌پذیری‌های High/Critical.
  - تولید گزارش (SARIF/HTML) و آرشیو در CI.
- قوانین عملی:
  - خط‌مشی نسخه‌ به‌روز وابستگی‌ها (Dependabot/Renovate).
  - Exceptions قابل‌ردیابی برای False Positive با محدودیت زمانی.


### DAST (Dynamic Application Security Testing)
- دامنه:
  - اسکن زمان اجرا روی محیط تست/Stage: OWASP ZAP/DAST ابزارهای مشابه.
  - سناریوها: احراز هویت، مسیرهای حساس (auth/patients/predictions/imaging/upload).
- ادغام CI/CD:
  - اجرای زاپ سروریس با پالیسی سبک در PR (زودبازخورد) و سنگین‌تر در Stage شبانه.
  - تولید گزارش و اخطار در Thresholdهای High/Critical.
- نکات عملی:
  - محافظت از داده واقعی (استفاده از داده‌های مصنوعی در Stage).
  - زمان‌بندی اسکن کامل خارج از ساعات اوج.


### CSP (Content Security Policy)
- هدف: کاهش XSS/Clickjacking و بارگیری منابع غیرمجاز.
- سطح اولیه (پیشنهادی برای MVP – گزارش‌گرانه):
  - Report-Only: `Content-Security-Policy-Report-Only`
  - سیاست پیشنهادی:
    - `default-src 'self';`
    - `script-src 'self' 'unsafe-inline' 'unsafe-eval'` (حذف تدریجی این دو در فاز بعد)
    - `style-src 'self' 'unsafe-inline'` (برای Tailwind/Inline; حذف تدریجی)
    - `img-src 'self' data: blob:`
    - `font-src 'self' data:`
    - `connect-src 'self' https://api.example.com` (تنظیم بر اساس دامنه‌ها)
    - `frame-ancestors 'none'` (یا دامنه‌های مجاز)
    - `object-src 'none'`
    - `base-uri 'self'`
    - `report-uri https://csp-collector.example.com/report`
- فاز سخت‌گیرانه:
  - حذف `unsafe-inline`/`unsafe-eval` با انتقال Inlineها به فایل‌ها/nonce/hash.
  - محدودسازی `connect-src`/`img-src`/`frame-ancestors` به دامنه‌های دقیق.
  - فعال‌سازی `Content-Security-Policy` (نه فقط Report-Only).


### هدرهای مکمل امنیتی
- `X-Frame-Options: DENY` (یا با CSP `frame-ancestors`)
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (پس از اطمینان TLS دائمی)
- `Permissions-Policy` برای محدودسازی قابلیت‌های مرورگر


### فرآیند پیشنهادی
- مرحله 1 (MVP):
  - SAST پایه در CI (bandit, npm audit, secrets scan)، DAST سبک در PRهای اصلی.
  - فعال‌سازی `CSP-Report-Only` با دامنه‌های فعلی + هدرهای امنیتی پایه.
  - پایش گزارش‌های CSP و کاهش تدریجی منابع غیرضروری/Inline.
- مرحله 2:
  - DAST کامل شبانه در Stage + Thresholdهای اخطار.
  - سخت‌کردن CSP (حذف `unsafe-inline/eval`)، محدودسازی دقیق `connect-src`.
  - افزودن `Permissions-Policy` و گزارش‌های منظم امنیتی.
- مرحله 3:
  - ادغام OIDC/MFA سیاست‌ها، اسکن وابستگی خودکار، تست نفوذ دوره‌ای شخص ثالث.


### Observability و ممیزی
- گزارش‌های SAST/DAST در CI/CD آرشیو شوند؛ روند رسیدگی ثبت شود.
- شمارش و روند آسیب‌پذیری‌ها (باز/بسته)، زمان متوسط رفع (MTTR).
- مانیتورینگ گزارش‌های CSP (نرخ رویدادها، مسیرها/Origin‌های خطا).


### چک‌لیست سریع
- [ ] SAST: bandit, npm audit, secrets scan در CI
- [ ] DAST: ZAP سبک در PR و کامل در Stage
- [ ] CSP: Report-Only در MVP، سخت‌گیرانه در فاز 2
- [ ] هدرهای امنیتی پایه (HSTS, XFO, XCTO, Referrer, Permissions)
- [ ] آرشیو و ردیابی گزارش‌ها، MTTR آسیب‌پذیری‌ها

