## احراز هویت/مجوز (OIDC/OAuth2/JWT) و مدیریت سشن

این سند معماری فعلی و مسیر توسعه برای AuthN/AuthZ را توضیح می‌دهد: توکن‌های JWT، رفرش، RBAC، و یکپارچگی OIDC/OAuth2 در فازهای بعد.


### وضعیت فعلی (MVP)
- احراز هویت: JWT Access Token (امضا با کلید محرمانه)، مسیر ورود در `auth/login`.
- اعتبارسنجی: `get_current_user` → استخراج `sub` از JWT → بازیابی کاربر از DB.
- مجوز: `require_role("role")` بر اساس سلسله‌مراتب نقش‌ها (`admin > doctor/radiologist/researcher > nurse > viewer`).
- نشست: Stateless (بدون نگهداری سمت سرور)، با مدت انقضا برای Access Token (مثلاً 15–30 دقیقه).
- رفرش: JWT Refresh Token با عمر طولانی‌تر (چند روز/هفته) و Endpoint نوسازی.


### قرارداد توکن‌ها
- Access Token:
  - Claims: `sub` (user_id)، `exp`، `type="access"`، نقش کاربر (اختیاری)
  - عمر: کوتاه (۱۵–۳۰ دقیقه)، استفاده در `Authorization: Bearer ...`
- Refresh Token:
  - Claims: `sub`، `exp` طولانی‌تر، `type="refresh"`
  - نگهداری امن سمت کلاینت (HttpOnly cookie پیشنهاد می‌شود)
  - استفاده فقط برای دریافت Access جدید؛ عدم استفاده برای دسترسی به API‌های محافظت‌شده


### مدیریت نشست و ابطال
- Stateless پیش‌فرض: ابطال توکن‌ها با چرخش کلید (Key Rotation) یا لیست سیاه (Blacklist) در Redis/DB.
- لیست سیاه (اختیاری):
  - ذخیره شناسه/فینگرپرینت Refresh Token در Redis با TTL تا انقضا
  - ابطال در رخدادهای امنیتی (گم‌شدن دستگاه/نقض امنیتی/تغییر رمز)
- Logout:
  - ابطال Refresh Token (حذف از لیست مجاز/قرار در Blacklist)
  - سمت کلاینت: پاک‌سازی توکن/کوکی


### RBAC و اعمال مجوز
- در سطح API: دکوریتور `require_role("...")` برای محافظت از CRUD و مسیرهای حساس (Predictions/Products/...)
- سیاست‌ها:
  - ایجاد/ویرایش بیمار: `nurse`+
  - اجرای پیش‌بینی: `doctor`+
  - مدیریت کاربران/تنظیمات/محصولات: `admin`
- ثبت ممیزی در عملیات حساس (ایجاد/حذف/پیش‌بینی/تغییر نقش)


### OIDC/OAuth2 (فازهای بعد)
- انگیزه: SSO سازمانی، فدراسیون هویت، مدیریت متمرکز سیاست‌ها و MFA
- گزینه‌ها: Keycloak، Auth0، Azure AD، Okta، یا راهکار داخلی OIDC
- فلو پیشنهادی (Authorization Code + PKCE):
  1) کلاینت → IdP (ورود)
  2) IdP → کالبک اپ با Authorization Code
  3) بک‌اند کد را با Access/ID Token از IdP عوض می‌کند
  4) نگاشت هویت/نقش از IdP به `UserRole` داخلی
  5) صدور JWT داخلی کوتاه‌عمر برای APIهای بک‌اند (BFF الگو)
- ملاحظات:
  - چرخش کلید عمومی IdP (JWKS) و کش/ریفریش کلیدها
  - Token Introspection/Revocation در صورت نیاز
  - MFA/Step-up Auth برای عملیات حساس


### امنیت کلاینت و ذخیره‌سازی توکن
- وب:
  - Access Token در حافظه (JS) کوتاه‌عمر؛ Refresh در HttpOnly/Secure/SameSite Cookie
  - محافظت از XSS/CSRF (Cookie + SameSite + Anti-CSRF token در صورت نیاز)
- موبایل/دسکتاپ:
  - Secure Storage سیستم‌عامل؛ جداسازی محیط‌ها


### سخت‌سازی و بهترین‌عمل
- انقضای کوتاه Access، محدودسازی عمر Refresh، Rotation دوره‌ای
- IP/Device Binding (اختیاری) برای Refresh Token
- محدودسازی نرخ برای مسیرهای auth (login/refresh)
- هشدار در جهش خطای ورود/شکست‌های متوالی
- PoLP برای دسترسی‌های مدیریتی، MFA برای نقش‌های حساس (Phase 3)


### خطایابی و ممیزی
- لاگ ساختاریافته: تلاش‌های ورود (موفق/ناموفق)، refresh، logout، ابطال
- بدون لاگ داده‌های حساس (پسورد/توکن کامل)
- متریک‌ها: نرخ موفق/ناموفق، زمان پاسخ، توزیع نقش‌ها در فراخوانی‌ها


### مسیر مهاجرت به OIDC
- گام 1: افزوده‌شدن پشتیبانی اختیاری OIDC در کنار JWT داخلی (Dual Mode)
- گام 2: Role Mapping و هم‌ترازسازی سیاست‌ها
- گام 3: فعال‌سازی MFA/Step-up برای عملیات حساس
- گام 4: برش تدریجی ورود داخلی به نفع SSO (در صورت الزام سازمانی)


### ارجاعات کدی
- Config/Token: `backend/app/core/security.py`, `backend/app/core/config.py`
- RBAC: `require_role` در `backend/app/core/security.py`
- مدل کاربر/نقش‌ها: `backend/app/models/user.py`


