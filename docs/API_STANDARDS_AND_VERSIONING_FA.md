## استانداردهای API و قرارداد نسخه‌بندی

این راهنما با معماری فعلی پروژه هم‌راستاست (FastAPI + REST، پیشوند `settings.API_V1_PREFIX` مثل `/api/v1`). هدف: API پایدار، خوانا، قابل نسخه‌بندی و قابل ممیزی.


### اصول REST
- منابع با اسم جمع و حروف کوچک: `/patients`, `/predictions`, `/imaging`, `/reports`, `/longitudinal`, `/products`
- عملیات:
  - GET `/resources/` (لیست)، GET `/resources/{id}` (جزئیات)
  - POST `/resources/` (ایجاد)، PUT `/resources/{id}` (به‌روزرسانی کامل/جزئی)
  - DELETE `/resources/{id}` (حذف)
- شناسه‌ها عددی/رشته‌ای یکتا؛ روابط تو در تو: `/patients/{id}/medical-records`
- Content-Type: `application/json; charset=utf-8`
- احراز هویت: `Authorization: Bearer <token>`


### وضعیت‌های HTTP (نمونه)
- 200 OK (موفق)، 201 Created (ایجاد)، 204 No Content (حذف/بدون بدنه)
- 400 Bad Request (اعتبارسنجی نامعتبر)، 401 Unauthorized (توکن نامعتبر/نبود)
- 403 Forbidden (عدم دسترسی RBAC)، 404 Not Found (منبع موجود نیست)
- 409 Conflict (قیود یکتایی/تداخل)، 429 Too Many Requests (Rate Limit)
- 500 Internal Server Error (خطای غیرمنتظره)


### طرح خطا (Error Schema)
```json
{
  "detail": "پیام خطا قابل خواندن",
  "code": "OPTIONAL_ERROR_CODE",
  "trace_id": "OPTIONAL_REQUEST_ID"
}
```
- تمام خطاها شامل `detail`؛ در صورت امکان `code` و `trace_id` برای رهگیری.


### صفحه‌بندی، فیلتر، مرتب‌سازی
- پارامترها:
  - `skip` (>=0), `limit` (۱–۱۰۰۰)، `search` (اختیاری)، فیلترهای دامنه مانند `is_active=true`
  - مرتب‌سازی (در صورت نیاز فاز بعد): `sort=field`, `order=asc|desc`
- پاسخ لیستی: آرایه اشیاء؛ در صورت نیاز متادیتا (فاز بعد): `{ items: [...], total, skip, limit }`


### قرارداد ورودی/خروجی
- ورودی‌ها با Pydantic Schemas (Create/Update) اعتبارسنجی می‌شوند.
- خروجی‌ها با Schemas پاسخ (Response) و `from_attributes = True` برای ORM.
- عددهای احتمال/نمره در بازه‌های معتبر (مثلاً [0,1]).


### کش و سربرگ‌ها
- نتایج خواندنی پرتکرار با TTL کوتاه کش می‌شوند.
- سربرگ‌های Rate Limiting (در صورت فعال بودن):
  - `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After` (در 429)


### امنیت
- JWT Bearer، RBAC در لایه API با decorator `require_role("role")`
- هدرهای امنیتی HTTP، CORS محدود، محدودسازی نرخ درخواست
- عدم ارسال داده‌های حساس در خطا/لاگ


### نسخه‌بندی (Versioning)
- استراتژی: نسخه در مسیر URL (URI Versioning):
  - `/api/v1/...` فعال
  - نسخه‌های آینده: `/api/v2/...` با سازگاری شکسته
- پشتیبانی/کنارگذاری (Deprecation):
  - معرفی v2 → حفظ v1 به‌صورت هم‌زمان برای یک بازه (مثلاً 6–12 ماه)
  - علامت‌گذاری مسیرهای منسوخ با سربرگ:
    - `Deprecation: true`
    - `Sunset: <RFC 1123 date>` (تاریخ پایان)
    - لینک راهنما: `Link: <https://.../migration-guide>; rel="deprecation"`
- تغییرات سازگار به عقب (Backward-compatible):
  - افزودن فیلدهای اختیاری یا مسیرهای جدید در همان نسخه
  - عدم حذف/تغییر معنای فیلدهای موجود


### قرارداد نام‌گذاری و مسیرها
- حروف کوچک و `-` برای چندکلمه‌ای‌ها در مسیرها؛ فیلدها با snake_case یا camelCase (ثبات مهم است)
- آیتم‌ها در جمع: `/medical-records`, `/audit-logs`
- روابط منطقی: `/patients/{id}/medical-records`


### Idempotency
- PUT برای به‌روزرسانی منابع idempotent در سطح API
- برای عملیات غیر idempotent حساس (فاز بعد): کلید `Idempotency-Key` در سربرگ


### مستندسازی
- OpenAPI (FastAPI docs): `/api/docs` در حالت DEBUG
- نگهداری نمونه درخواست/پاسخ در `docs/API_EXAMPLES.md` (در صورت نیاز)


### GraphQL / gRPC (آینده)
- GraphQL: برای رابط‌های غنی/کلاینت‌های پیچیده (گزینه آتی، نه MVP)
- gRPC: برای ارتباط سرویس به سرویس با کارایی بالا (در صورت انشقاق میکروسرویسی)


### مثال‌های مسیر (هم‌راستا با پروژه)
- Patients:
  - GET `/api/v1/patients?skip=0&limit=50&search=...`
  - POST `/api/v1/patients` (role: nurse+)
  - GET `/api/v1/patients/{patient_id}`
  - PUT `/api/v1/patients/{patient_id}` (role: nurse+)
  - DELETE `/api/v1/patients/{patient_id}` (role: admin)
- Predictions:
  - POST `/api/v1/predictions` (role: doctor+)
  - GET `/api/v1/predictions/{id}`
- Products:
  - POST `/api/v1/products` (role: admin)
  - GET `/api/v1/products?is_active=true`


