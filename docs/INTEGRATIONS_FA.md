## یکپارچه‌سازی‌ها (Integrations)

این سند راهبرد و الگوهای یکپارچگی سامانه با سیستم‌های بیرونی را پوشش می‌دهد: HIS، PACS، SSO/IdP، Webhookها، و تبادل داده. مبتنی بر قابلیت‌های فعلی (`app/api/integration.py`, `app/services/integration_service.py`) و مسیر رشد فازبندی‌شده.


### اهداف
- تبادل دادهٔ مطمئن و قابل ممیزی با کمترین بار عملیاتی
- همگام‌سازی پایدار (نزدیک به بلادرنگ یا دسته‌ای) بسته به نیاز
- امنیت و حریم خصوصی مطابق RBAC و سیاست‌های سازمانی


### انواع یکپارچگی
- HIS/EMR:
  - همگام‌سازی بیمار/سوابق (Pull/Push)
  - فراخوانی نتایج پیش‌بینی و گزارش‌ها
  - استانداردهای محتمل: HL7 v2، FHIR (در فازهای بعد)
- PACS/RIS:
  - لینک/دریافت متادیتای تصویر، ارجاع به DICOM
  - دریافت URL امن یا WADO-RS برای نمایش/دانلود (در صورت پشتیبانی)
- SSO/IdP:
  - SAML/OIDC برای ورود واحد (در فاز بعد)
  - نقشه‌برداری نقش‌ها (Role Mapping) به `UserRole`
- Webhooks/Callbacks:
  - اعلان تکمیل پیش‌بینی/گزارش، هشدارهای طولی
  - امضای پیام (HMAC) و idempotency در دریافت‌کننده


### الگوهای همگام‌سازی
- Pull Batch (MVP):
  - کران‌جاب دوره‌ای برای دریافت بیماران جدید/به‌روزرسانی‌شده
  - فیلتر بر اساس timestamp/offset؛ نگهداری cursor
- Pull Near-Real-Time (Phase 2):
  - Subscription/Queue از HIS (در صورت پشتیبانی)
  - Backoff و DLQ برای شکست‌ها
- Push (Outbound):
  - ارسال نتیجه پیش‌بینی/گزارش به HIS با قرارداد مشخص و امضای درخواست


### نگاشت داده (Data Mapping)
- Patient:
  - patient_id داخلی ←→ شناسه HIS (MRN/ExternalID)
  - نام/نام خانوادگی/تاریخ تولد/جنسیت مطابق فیلدهای HIS
- Medical Record:
  - نمرات شناختی و بیومارکرها به ICD/LOINC (در صورت نیاز آتی)
- Imaging:
  - StudyInstanceUID/AccessionNumber/Modality، تاریخ و مسیر دسترسی
- Prediction/Report:
  - نوع بیماری، نمره ریسک/اعتماد، نسخه مدل، لینک گزارش PDF


### امنیت و انطباق
- احراز هویت API با توکن‌های سرویس (mTLS/Token) و IP Whitelist
- رمزنگاری در انتقال (TLS) و امضای درخواست‌ها (HMAC/JWT)
- ممیزی کامل درخواست/پاسخ (بدون لاگ دادهٔ حساس)، نگهداشت مطابق سیاست
- محدودسازی نرخ برای اتصال‌های بیرونی و Circuit Breaker


### مدیریت خطا و قابلیت اطمینان
- Retry با Backoff نمایی در خطاهای موقت
- DLQ/Outbox برای پیام‌های ناموفق (Phase 2 با پیام‌رسان)
- Idempotency-Key برای عملیات غیر idempotent
- زمان‌بندی مجدد خودکار و گزارش‌گیری نرخ موفق/ناموفق


### تست و اعتبارسنجی
- محیط‌های شبیه‌سازی شده (Sandbox/Stubs) برای HIS/PACS
- Contract Testing (نمونه‌ها/Schema) و تست‌های انتهابه‌انتها (E2E)
- Verify دادهٔ همگام‌شده (Sampling)، پایش عدم‌تطابق‌ها


### API الگو (نمونه‌های فرضی)
- HIS Pull:
  - GET `HIS /api/patients?updated_after=...&cursor=...`
  - پاسخ: `{ items: [...], next_cursor: "...", total: ... }`
- Push Prediction:
  - POST `HIS /api/predictions` با بدنه:
    ```json
    {
      "patient_external_id": "HIS-123",
      "disease_type": "alzheimer",
      "risk_score": 0.82,
      "confidence": 0.91,
      "model_version": "v1.0.0",
      "report_url": "https://.../reports/123.pdf",
      "timestamp": "2025-01-01T10:20:30Z"
    }
    ```
- PACS Metadata:
  - GET `PACS /studies/{StudyInstanceUID}` → متادیتا و لینک‌های دسترسی


### فازبندی اجرای یکپارچگی
- فاز 1 (MVP):
  - Pull Batch از HIS برای بیماران جدید/آپدیت‌ها (روزانه/ساعتی)
  - ثبت متادیتای PACS (لینک/UID) بدون دانلود مستقیم
  - وب‌هوک داخلی آزمایشی (log-only) برای Events کلیدی
- فاز 2:
  - Push نتایج پیش‌بینی/گزارش به HIS (با امضا و idempotency)
  - Queue برای پردازش آسنکرون و DLQ
  - PACS: WADO-RS/URL ایمن در صورت امکان
- فاز 3:
  - OIDC/SAML برای SSO و Role Mapping
  - Subscription near real-time از HIS (در صورت پشتیبانی)


### معیارهای پایش/کیفیت یکپارچگی
- موفق/ناموفق همگام‌سازی، زمان تا همگام‌سازی، نرخ Retry
- تاخیر Pull/Push، خطاهای قرارداد/اعتبارسنجی
- اثر بر کارایی (Latency/Throughput) و مصرف منابع


### ارجاع به کد
- API Integration: `backend/app/api/integration.py`
- Service: `backend/app/services/integration_service.py`
- امنیت/تنظیمات: `backend/app/core/*`


