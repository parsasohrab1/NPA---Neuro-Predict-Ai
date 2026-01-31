# پیشنهادات بهینه‌سازی محصول NeuroPredict-AI

این سند پیشنهادات فنی برای بهینه‌سازی عملکرد، امنیت، تجربه کاربری و مقیاس‌پذیری محصول NeuroPredict-AI را ارائه می‌دهد.

---

## ۱. بک‌اند (Backend)

### ۱.۱ فعال‌سازی Cache Middleware
- **وضعیت:** `CacheMiddleware` پیاده‌سازی شده اما در `main.py` استفاده **نشده** است.
- **اقدام:** افزودن `CacheMiddleware` به pipeline در `main.py` برای cache کردن پاسخ‌های GET مربوط به `/patients/`, `/predictions/`, `/analytics/`.
- **نتیجه:** کاهش بار دیتابیس و بهبود زمان پاسخ برای لیست بیماران و پیش‌بینی‌ها.

### ۱.۲ Cache برای endpoint پیش‌بینی (خواندن)
- **وضعیت:** endpoint `GET /predictions/{id}` و لیست پیش‌بینی‌ها بدون cache هستند.
- **اقدام:** استفاده از `cache_service.get/set` با کلید مبتنی بر `prediction_id` یا پارامترهای query و TTL مناسب (مثلاً ۶۰–۳۰۰ ثانیه).
- **نکته:** endpoint `POST /predictions/` (ایجاد پیش‌بینی) نباید cache شود؛ پس از ایجاد، cache مرتبط با بیمار را invalidate کنید.

### ۱.۳ غیرهمگام کردن inference مدل (AI)
- **وضعیت:** متد `predict()` در `ai_model_service.py` به صورت `async` تعریف شده اما محاسبات PyTorch **همگام** روی CPU/GPU اجرا می‌شوند و event loop را block می‌کنند.
- **اقدام:** اجرای inference داخل `asyncio.to_thread()` یا `run_in_executor()` تا thread pool آن را اجرا کند و event loop آزاد بماند.
- **نتیجه:** امکان پردازش همزمان درخواست‌های دیگر و رعایت بهتر SLA (< 3s).

### ۱.۴ بهینه‌سازی Query در API پیش‌بینی
- **وضعیت:** در `create_prediction` دو query جدا برای Patient و MedicalRecord اجرا می‌شود.
- **اقدام:** یک query با `selectinload` یا `joinedload` برای بارگذاری Patient به‌همراه آخرین MedicalRecord (یا مرتب‌سازی و limit 1) تا N+1 و round-tripهای اضافه حذف شوند.

### ۱.۵ ایندکس دیتابیس برای جدول predictions
- **وضعیت:** روی `predictions.patient_id` و `predictions.created_at` ایندکس صریح تعریف نشده (فقط FK ممکن است ایندکس ایجاد کند).
- **اقدام:** اضافه کردن ایندکس مرکب برای فیلترهای رایج، مثلاً `(patient_id, created_at DESC)` برای لیست پیش‌بینی‌های هر بیمار.
- **مزیت:** کوئری‌های لیست و گزارش‌ها سریع‌تر می‌شوند.

### ۱.۶ محدودیت همزمانی برای پیش‌بینی
- **وضعیت:** در config مقدار `MAX_CONCURRENT_PREDICTIONS` وجود دارد اما در کد استفاده نشده.
- **اقدام:** استفاده از یک Semaphore با این مقدار در سرویس مدل تا در اوج بار، از overload مدل و افزایش زمان پاسخ جلوگیری شود.

### ۱.۷ اتصال Redis در Startup
- **وضعیت:** در `lifespan` فقط `init_db` و `realtime_service` و در shutdown فقط `cache_service.disconnect()` صریحاً دیده می‌شود؛ اتصال Redis در startup صریح نیست.
- **اقدام:** فراخوانی `await cache_service.connect()` در startup (قبل از yield) تا در production cache واقعاً فعال باشد.

---

## ۲. فرانت‌اند (Frontend)

### ۲.۱ Lazy Loading و Code Splitting
- **وضعیت:** تمام صفحات در `App.tsx` به صورت مستقیم import شده‌اند و در باندل اولیه قرار می‌گیرند.
- **اقدام:** استفاده از `React.lazy()` و `Suspense` برای صفحاتی مثل Reports، Longitudinal، PopulationAnalysis، ModelManagement، Settings.
- **نتیجه:** کاهش اندازه باندل اولیه و بهبود FCP و TTI.

### ۲.۲ Debounce برای جستجوی بیماران
- **وضعیت:** در `PatientsPage` با هر تغییر `search` بلافاصله `useQuery` با کلید جدید اجرا می‌شود و درخواست API زده می‌شود.
- **اقدام:** استفاده از debounce (مثلاً ۳۰۰ms) روی مقدار جستجو قبل از قرار دادن در `queryKey` یا استفاده از یک state میانی با debounce.
- **نتیجه:** کاهش تعداد درخواست‌ها و بار سرور.

### ۲.۳ استفاده یکدست از React Query
- **وضعیت:** در `api.ts` مقدار `USE_MOCK_DATA = true` به صورت ثابت است و سوییچ به API واقعی فقط با تغییر کد ممکن است.
- **اقدام:** خواندن این مقدار از متغیر محیط (مثلاً `import.meta.env.VITE_USE_MOCK_DATA`) تا در buildهای مختلف بتوان بدون تغییر کد از mock یا API واقعی استفاده کرد.

### ۲.۴ Pagination سمت سرور
- **وضعیت:** در `patientsApi.getAll` و مشابه‌ها، `skip` و `limit` استفاده می‌شوند اما در UI ممکن است همه داده‌ها یکجا گرفته شوند (مثلاً limit ثابت 100).
- **اقدام:** پیاده‌سازی pagination واقعی در لیست بیماران و پیش‌بینی‌ها (صفحه و اندازه صفحه) و استفاده از `getNextPageParam` در React Query در صورت پشتیبانی API از cursor/offset.
- **نتیجه:** کاهش مصرف حافظه و زمان پاسخ برای دیتاست‌های بزرگ.

### ۲.۵ بهینه‌سازی Vite Build
- **اقدام:** در `vite.config.ts` می‌توان از `build.rollupOptions.output.manualChunks` برای تفکیک vendorهای سنگین (مثلاً recharts، react-router) استفاده کرد تا کش مرورگر مؤثرتر شود.
- **نتیجه:** به‌روزرسانی‌های بعدی با تغییرات کم، نیاز به دانلود مجدد کل باندل نداشته باشند.

---

## ۳. امنیت و عملیات

### ۳.۱ غیرفعال بودن Docs در Production
- **وضعیت:** در production با `DEBUG=False`، `docs_url` و `redoc_url` روی `None` تنظیم شده که مناسب است.
- **پیشنهاد:** اطمینان از اینکه متغیر `DEBUG` و `ENVIRONMENT` در محیط production به درستی تنظیم شده‌اند (مثلاً از env و نه فایل ثابت).

### ۳.۲ Rate Limiting
- **وضعیت:** محدودیت نرخ (rate limit) برای APIها به صورت سراسری دیده نشد.
- **اقدام:** اضافه کردن middleware محدودیت نرخ (مثلاً بر اساس IP یا توکن) برای endpointهای حساس مثل `/predictions/` (POST) و `/auth/` تا از سوءاستفاده و DDoS خفیف جلوگیری شود.

### ۳.۳ Health Check دقیق‌تر
- **وضعیت:** endpoint `/health` فقط یک پاسخ ثابت برمی‌گرداند.
- **اقدام:** در صورت امکان بررسی اتصال به PostgreSQL و Redis در همین endpoint و برگرداندن وضعیت (مثلاً 503) در صورت قطع بودن؛ برای load balancer و مانیتورینگ مفید است.

---

## ۴. مدل و Explainability (مطابق SRS)

### ۴.۱ Attention Scores در خروجی API
- **وضعیت:** در SRS و اسکیما، `attention_scores` برای MRI، Biomarker و Cognitive تعریف شده؛ در پاسخ فعلی `ai_model_service.predict` و schema پاسخ این فیلد دیده نشد.
- **اقدام:** تکمیل معماری مدل با لایه attention (در صورت استفاده از مدل چندحالته) و برگرداندن `attention_scores` در پاسخ API و ذخیره در audit log.

### ۴.۲ Audit Log برای پیش‌بینی
- **وضعیت:** در SRS ذکر شده که attention scores در audit log ذخیره شوند.
- **اقدام:** اطمینان از اینکه برای هر `create_prediction` یک رکورد audit با جزئیات لازم (از جمله attention_scores در صورت وجود) ثبت می‌شود.

---

## ۵. اولویت‌بندی پیشنهادی

| اولویت | مورد | تلاش تقریبی | تاثیر | وضعیت |
|--------|------|-------------|--------|--------|
| بالا | فعال‌سازی Cache Middleware و اتصال Redis در startup | کم | بالا | ✅ انجام‌شده |
| بالا | اجرای inference مدل در thread pool (to_thread) | کم | بالا | ✅ انجام‌شده |
| بالا | Lazy loading صفحات در فرانت | کم | متوسط–بالا | ✅ انجام‌شده |
| متوسط | Debounce جستجو + Pagination سمت سرور | متوسط | متوسط | ✅ انجام‌شده |
| متوسط | ایندکس predictions و بهینه‌سازی query ایجاد پیش‌بینی | کم | متوسط | ✅ انجام‌شده |
| متوسط | Rate limiting و Health check با DB/Redis | متوسط | امنیت و پایداری | ✅ انجام‌شده |
| پایین | توجه به attention_scores و audit log مطابق SRS | بسته به مدل | انطباق با SRS | ✅ انجام‌شده |

*موارد بالا در چرخه بهینه‌سازی پیاده‌سازی شده‌اند.*

---

## ۶. جمع‌بندی

با اعمال موارد بالا:
- **عملکرد:** کاهش زمان پاسخ و افزایش توان عملیاتی با cache و عدم block شدن event loop در inference.
- **مقیاس‌پذیری:** کنترل همزمانی پیش‌بینی و pagination واقعی.
- **تجربه کاربری:** بارگذاری سریع‌تر اولیه و جستجوی روان‌تر.
- **امنیت و عملیات:** rate limiting و health check مناسب‌تر برای استقرار production.

در صورت نیاز می‌توان برای هر مورد، طرح تغییر دقیق (diff یا مراحل پیاده‌سازی) جداگانه تهیه کرد.
