## نقش‌ها و سطوح دسترسی (RBAC)

این ماتریس با نقش‌های موجود در سیستم هم‌راستاست (`admin`, `doctor`, `radiologist`, `researcher`, `nurse`, `viewer`) و با منطق فعلی بک‌اند (تابع `require_role` و سلسله‌مراتب نقش‌ها) سازگار است.

### سلسله‌مراتب نقش‌ها
- admin > doctor/radiologist/researcher > nurse > viewer

### اصول کلی
- عملیات حساس نوشتاری (Create/Update/Delete) برای داده‌های بالینی: حداقل `nurse` یا بالاتر.
- تولید پیش‌بینی‌های بالینی: `doctor` یا بالاتر.
- مدیریت کاربران و تنظیمات سیستمی: فقط `admin`.
- مشاهده داده‌ها: حداقل `viewer` (با محدودیت‌های حریم خصوصی).

### دسترسی API های اصلی (نمونه‌های کلیدی)
- Auth:
  - Login/Refresh: عمومی (بدون نقش)؛ پس از احراز هویت نقش اعمال می‌شود.
- Patients (`/patients`):
  - Create/Update: `nurse`+
  - Delete: `admin`
  - Get/List: `viewer`+
- Medical Records (زیرمجموعه بیمار):
  - Create/Update: `nurse`+
  - Get/List: `viewer`+
- Imaging (`/imaging`):
  - Upload: `nurse`+
  - Get/List: `viewer`+
  - تحلیل پیشرفته (در فازهای بعد): `radiologist`/`doctor`+
- Predictions (`/predictions`):
  - Create (اجرای مدل): `doctor`+
  - Get/List: `viewer`+
  - Review/Approve (در صورت نیاز): `doctor`+
- Reports (`/reports`):
  - Generate/Download: `viewer`+ (دانلود ممکن است برای برخی نقش‌ها محدود شود)
  - Scheduled (فازهای بعد): `doctor`/`admin`+
- Longitudinal (`/longitudinal`):
  - Create/Update Episodes/Visits: `nurse`+
  - Alerts config (فازهای بعد): `doctor`/`admin`+
- Products (`/products`):
  - Create/Update/Delete: `admin`
  - Get/List: `viewer`+
- Security/Monitoring/Integration/Backup:
  - Reading dashboards: `admin`
  - Mutating config/actions: فقط `admin`

### دسترسی UI (ادمین داشبورد و کلاینت)
- Viewer:
  - مشاهده لیست بیماران، جزئیات پایه، گزارش‌ها و نتایج پیش‌بینی (بدون ویرایش).
- Nurse:
  - همهٔ دسترسی‌های Viewer +
  - ایجاد/ویرایش بیمار، ثبت سوابق، آپلود تصویر.
- Doctor / Radiologist / Researcher:
  - همهٔ دسترسی‌های Nurse +
  - اجرای پیش‌بینی، مرور و تفسیر نتایج، گزارش‌گیری.
  - Radiologist: ماژول‌های تصویربرداری پیشرفته (در فازهای بعد).
  - Researcher: دسترسی خواندنی گسترده‌تر به داده‌های ناشناس‌سازی‌شده (مطابق سیاست).
- Admin:
  - مدیریت کاربران/نقش‌ها، تنظیمات امنیتی، گزارش‌های سیستمی، محصولات/مدل‌ها.

### سیاست‌های امنیتی تکمیلی
- احراز هویت اجباری برای همهٔ مسیرها (به‌جز Login/Health).
- اعمال Rate-Limiting و سرآیندهای امنیتی HTTP.
- ممیزی رویدادها: ورود/خروج، CRUDهای حساس، اجرای پیش‌بینی.
- (فازهای بعد) MFA برای نقش‌های حساس و لیست سفید IP.


