## قراردادهای API و مدیریت خطا

این سند قراردادهای ورودی/خروجی، الگوی صفحه‌بندی/فیلتر، شناسه‌گذاری، و سیاست مدیریت خطا را مشخص می‌کند. با FastAPI و الگوهای فعلی هم‌راستاست.


### اصول قرارداد
- Content-Type: `application/json; charset=utf-8`
- احراز هویت: `Authorization: Bearer <access_token>`
- مسیرها: منابع جمع (`/patients`, `/predictions`, `/products`)، جزئیات (`/{id}`)، روابط تو-در-تو (`/patients/{id}/medical-records`)
- نسخه‌بندی: پیشوند URI (مثل `/api/v1/...`)


### ورودی‌ها (Requests)
- بدنه ایجاد/ویرایش با Schemas صریح (Pydantic) و اعتبارسنجی سمت سرور
- شناسه‌ها: عددی/رشته‌ای یکتا؛ فیلدهای تاریخ ISO8601
- Idempotency (گزینشی برای عملیات حساس):
  - سربرگ `Idempotency-Key: <uuid>` برای `POST`های غیرتکرارشونده
  - رفتار: تکرار با همان کلید → همان نتیجه/کد


### خروجی‌ها (Responses)
- جزئیات: شیء واحد مطابق Schema پاسخ (Response)
- لیست‌ها:
  - MVP: آرایه ساده اشیاء
  - فاز بعد (پیشنهادی): الگوی Envelope
    ```json
    {
      "items": [ ... ],
      "total": 123,
      "skip": 0,
      "limit": 50
    }
    ```
- تاریخ/زمان: ISO8601 (UTC)؛ اعداد احتمال در بازه‌های معتبر (مثلاً [0,1])


### صفحه‌بندی، فیلتر، مرتب‌سازی
- پارامترها:
  - `skip` (>=0), `limit` (1–1000), `search` (اختیاری)، فیلتر دامنه مانند `is_active=true`
  - (فاز بعد) مرتب‌سازی: `sort={field}`, `order=asc|desc`
- سربرگ‌های کمکی (اختیاری): `X-Total-Count`


### مدیریت خطا (Error Handling)
- وضعیت‌های استاندارد:
  - 400 (Bad Request) – اعتبارسنجی نامعتبر/پارامترهای ناقص
  - 401 (Unauthorized) – توکن نامعتبر/منقضی
  - 403 (Forbidden) – عدم مجوز RBAC
  - 404 (Not Found) – منبع موجود نیست
  - 409 (Conflict) – تعارض/قیود یکتا (مانند patient_id تکراری)
  - 422 (Unprocessable Entity) – خطاهای اسکیما/نوع
  - 429 (Too Many Requests) – عبور از Rate Limit
  - 500 (Internal Server Error) – خطای غیرمنتظره
- بدنه خطا (پیشنهادی):
  ```json
  {
    "detail": "پیام خطا قابل‌خواندن",
    "code": "OPTIONAL_ERROR_CODE",
    "trace_id": "OPTIONAL_REQUEST_ID"
  }
  ```
- خطاهای اعتبارسنجی (422): فهرست فیلدها و پیام‌ها
  ```json
  {
    "detail": [
      {"loc": ["body", "first_name"], "msg": "field required", "type": "value_error.missing"}
    ],
    "trace_id": "req-abc123"
  }
  ```
- همبستگی و رهگیری:
  - `trace_id` در پاسخ خطا/لاگ برای رهگیری انتهابه‌انتها
  - افزودن `X-Request-ID` در درخواست‌های کلاینت (اختیاری)


### خطاهای قابل‌Retry
- 408/429/5xx با backoff و jitter (کلاینت باید Retry کند)
- 4xx منطقی (400/403/404/409/422): عدم Retry، اصلاح ورودی/مجوز


### Rate Limiting
- 429 با هدرها:
  - `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`


### Deprecation/نسخه‌ها
- سربرگ‌ها برای مسیرهای منسوخ:
  - `Deprecation: true`
  - `Sunset: <RFC 1123 date>`
  - `Link: <https://.../migration-guide>; rel="deprecation"`


### نمونه‌ها (هم‌راستا با پروژه)
- ایجاد بیمار (201):
  ```json
  {
    "id": 101,
    "patient_id": "PT-001",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1980-01-15",
    "gender": "male",
    "created_at": "2025-01-01T10:20:30Z"
  }
  ```
- خطای تعارض (409):
  ```json
  {
    "detail": "Patient with ID PT-001 already exists",
    "code": "PATIENT_ID_CONFLICT",
    "trace_id": "req-xyz789"
  }
  ```


### بهترین‌عمل‌ها
- پیام‌های خطا کوتاه و قابل‌فهم برای کلینیک؛ عدم افشای جزئیات داخلی
- سازگاری نام فیلدها بین اسکیما/مدل/پاسخ
- نگاشت خطاهای DB/وابستگی به خطاهای دامنه با کدهای پایدار


### ارجاع
- استانداردهای پایه: `docs/API_STANDARDS_AND_VERSIONING_FA.md`
- نمونه‌های بیشتر: در صورت نیاز `docs/API_EXAMPLES.md`


