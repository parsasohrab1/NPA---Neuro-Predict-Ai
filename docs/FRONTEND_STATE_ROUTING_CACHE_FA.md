## مدیریت حالت، روتینگ، و کش سمت کلاینت

این راهنما با استک فعلی (React + TypeScript + Vite + Tailwind) هم‌راستاست و الگوی پیشنهادی برای مدیریت حالت UI، روتینگ، و کش داده‌های سروری را مشخص می‌کند.


### مدیریت حالت (State Management)
- اصول تفکیک:
  - Local UI State: درون کامپوننت‌ها (useState/useReducer)؛ مثال: باز/بسته بودن مودال، ورودی فرم.
  - App-wide State (context): فقط برای مشترک‌های واقعی مثل auth/user، theme/RTL، i18n.
  - Server State: داده‌هایی که منبع واحد حقیقت آنها سرور است (لیست‌ها/جزئیات). کش شوند و جدا از state محلی نگه‌داری شوند.
- پیشنهاد:
  - Contextهای سبک: `AuthContext`, `ThemeContext`, `I18nContext`.
  - پرهیز از Global Store سنگین مگر در سناریوهای پیچیده (Redux/Zustand فقط در صورت نیاز).


### روتینگ (Routing)
- ابزار: React Router
  - ساختار مسیرها: ماژولار، خوانا، پایدار؛ پشتیبانی از گاردهای نقش (RBAC) در سطح Route.
  - Lazy-loading صفحات سنگین (code-splitting).
  - Breadcrumb برای عمق‌های چندسطحی.
  - اسکرول به بالا در ناوبری و مدیریت تمرکز (Focus) برای A11y.
- پیشنهاد ساختار:
  - `/login`, `/patients`, `/patients/:id`, `/imaging`, `/predictions`, `/reports`, `/longitudinal`, `/admin/*`, `/products`
  - صفحه 404 و 403 اختصاصی.


### کش سمت کلاینت برای Server State
- ابزار پیشنهادی: TanStack Query (React Query) یا SWR (گزینش‌پذیر)
  - مزایا: کش هوشمند، invalidate/refresh ساده، مدیریت status (loading/error), retry/backoff, pagination, infinite queries.
  - الگوی کلیدگذاری: `['patients', { skip, limit, search }]`, `['patient', id]`, `['products', filters]`.
  - سیاست تازگی: `staleTime` براساس نوع داده (لیست‌های پرتکرار: 1–5 دقیقه؛ جزئیات: 5–10 دقیقه).
  - invalidate هدفمند پس از mutations (create/update/delete).
  - prefetch برای ناوبری روان بین لیست/جزئیات.
  - نگاشت خطاها به پیام‌های خوانا و رفتار retry مناسب.
- SWR جایگزین سبک: اگر Query پیچیده نیست، `useSWR` با `fetcher` مشترک و `mutate`.


### الگوهای فراخوانی API
- لایه سرویس:
  - توابع تایپ‌شده (TS) برای هر endpoint: `getPatients(params)`, `getPatient(id)`, `createPatient(dto)`…
  - مدیریت توکن/خطا در یک نقطه (interceptor/fetch wrapper).
  - تبدیل داده (normalize) و نگهداری انواع (types) کنار سرویس‌ها.
- ادغام با Query/Caching:
  - Query hooks: `usePatientsQuery(params)`, `usePatientQuery(id)`.
  - Mutation hooks: `useCreatePatientMutation()`, سپس `invalidateQueries(['patients'])`.


### RBAC در روتینگ و UI
- Route Guards: چک نقش‌ها قبل از رندر صفحه/مسیر (redirect به 403/404).
- UI-level Guards: پنهان‌سازی/غیرفعال‌سازی اکشن‌ها بر اساس نقش (مثلاً دکمه حذف فقط برای admin).


### پرفورمنس و UX
- code-splitting صفحات بزرگ، `Suspense`/Skeleton برای بارگذاری.
- virtualization برای لیست‌های طولانی (react-window/virtualized).
- Debounce در جستجو/فیلتر، prefetch در hover/focus لینک‌ها.
- حفظ اسکرول/فیلتر بین ناوبری لیست ↔ جزئیات (state in URL/query params).


### خطا و وضعیت
- الگوهای Loading/Empty/Error یکنواخت برای لیست‌ها و جزئیات.
- Toast/Alert برای موفقیت/خطاهای mutation و رخدادهای مهم.
- لاگ کلاینت (اختیاری) بدون PII؛ گزارش Web Vitals (اختیاری).


### چک‌لیست سریع
- [ ] Context فقط برای auth/theme/i18n؛ بقیه در state محلی یا server-state
- [ ] React Router با lazy-loading و گارد نقش‌ها؛ مسیرهای 403/404
- [ ] TanStack Query/SWR برای کش سروری با کلیدگذاری و staleTime مناسب
- [ ] invalidate هدفمند پس از mutation، prefetch لیست/جزئیات
- [ ] لایه سرویس تایپ‌شده + مدیریت توکن/خطا مرکزی
- [ ] الگوهای Loading/Empty/Error/Toast ثابت، Debounce جستجو، virtualization لیست

