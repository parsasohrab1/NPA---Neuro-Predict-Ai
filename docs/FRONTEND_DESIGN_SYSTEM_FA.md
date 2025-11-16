## سیستم طراحی و کامپوننت‌ها (Frontend)

این راهنما با استک فعلی (React + TypeScript + Vite + Tailwind) هم‌راستاست و اصول طراحی، توکن‌ها، الگوها و مجموعه کامپوننت‌های پایه را مشخص می‌کند.


### اصول طراحی
- سادگی و وضوح بالینی؛ تمرکز بر خوانایی و حداقل بار شناختی.
- ثبات الگوها بین صفحات؛ سلسله‌مراتب بصری واضح (Typography/Spacing).
- دسترس‌پذیری: کنتراست کافی، فوکوس قابل‌مشاهده، قابل‌دسترسی با کیبورد، ARIA.
- RTL-first: فارسی پیش‌فرض، آمادگی i18n برای زبان‌های بعدی.
- بازخورد صریح: حالت‌های Loading/Empty/Error/Skeleton.


### توکن‌ها (Design Tokens)
- رنگ‌ها (نمونه):
  - primary: آبی بالینی، success: سبز، warning: کهربایی، danger: قرمز
  - surface: سفید/خاکستری روشن؛ متن: خاکستری تیره/مشکی
- تایپوگرافی:
  - عنوان‌ها h1–h4، متن پایه، زیرنویس؛ اندازه/وزن ثابت
- فضاگذاری:
  - مقیاس ثابت (4px یا 8px) برای margin/padding/gap
- سایه/شعاع:
  - سطوح کارت/دیالوگ با shadow/rounded استاندارد
- حالت‌ها:
  - states: hover/active/disabled/focus با تغییر واضح رنگ/سایه


### الگوهای تعاملی
- فرم‌ها:
  - لیبل واضح، placeholder توصیفی، helper/error text، اعتبارسنجی همزمان/پس ازblur
  - کنترل‌های تاریخ/انتخاب با دسترس‌پذیری کامل
- ناوبری:
  - سایدبار + نوار بالا؛ breadcrumb برای صفحات عمیق
- لیست و جدول:
  - جستجو/فیلتر/سورت، صفحه‌بندی، Empty/No-results با CTA مناسب
- دیالوگ/Drawer:
  - تایید عملیات خطرناک با توضیح روشن، دکمه‌ها: primary/secondary/destructive
- وضعیت‌ها:
  - Loading (spinner/skeleton)، Error (پیغام خوانا + راه‌حل)، Empty (راهنما/CTA)


### کامپوننت‌های پایه (مجموعه پیشنهادی)
- Layout:
  - `AppShell`, `Sidebar`, `Topbar`, `Breadcrumb`
- داده و نمایش:
  - `Card`, `Badge`, `Tag`, `Avatar`, `Stat`, `Progress`, `Alert`
  - `Table` (ستون‌های قابل سورت/فیلتر)، `DataList`, `EmptyState`
- فرم‌ها:
  - `Button` (primary/secondary/tertiary/destructive/link + sizes)
  - `Input`, `Textarea`, `Select`, `Checkbox`, `Radio`, `Switch`, `DatePicker`
  - `FormField` (label/helper/error)، `FormSection`
- بازخورد:
  - `Toast/Notification`, `Modal/Dialog`, `Drawer`, `Tooltip`, `Spinner`, `Skeleton`
- ناوبری:
  - `Tabs`, `Step`, `Pagination`, `Dropdown`, `Breadcrumb`


### الگوهای دامنه (Domain Patterns)
- بیمار/پرونده:
  - کارت خلاصه بیمار، فرم ثبت/ویرایش، تایم‌لاین ویزیت‌ها
- تصویربرداری:
  - کارت مطالعه، وضعیت آپلود/اعتبارسنجی، پیش‌نمایش متادیتا
- پیش‌بینی/گزارش:
  - کارت نتیجه با Risk/Confidence، جدول ویژگی‌ها، دکمه دانلود گزارش
- طولی:
  - نمودار روند (line/area)، کارت هشدار با شدت، فیلتر بازه زمانی
- مدیریت:
  - لیست کاربران/نقش‌ها، محصولات/نسخه‌ها، تنظیمات سیستم


### اصول پیاده‌سازی (React + Tailwind)
- TypeScript: نوع‌دهی صریح props، اجتناب از any.
- کامپوننت‌ها:
  - props مینیمال و معنادار؛ variant/size به‌صورت enums
  - ترکیب‌پذیری (children/render props) برای انعطاف
  - کلاس‌ها با Tailwind + الگوی `cn()` برای ترکیب شرطی
- وضعیت:
  - state محلی برای UI، context فقط برای مشترک‌های واقعی (theme/i18n/auth)
  - درخواست‌ها با hooks (SWR/React Query در صورت نیاز آینده)
- دسترس‌پذیری:
  - نقش‌ها/ARIA مناسب، فوکوس کنترل‌شده، trap در Modal/Drawer


### دسترس‌پذیری و i18n/RTL
- متن‌های جایگزین (alt) برای تصاویر/آیکون‌ها
- ترتیب تب منطقی، استفاده از `<label for>` و `id` یکتا
- پیام‌های خطا قابل‌خواندن و نزدیک کنترل مربوطه
- فایل‌های ترجمه (`i18n`) با کلیدهای پایدار؛ تاریخ/عدد RTL-friendly


### تم‌سازی (Theming)
- پایه Tailwind + CSS variables برای رنگ‌ها/spacing/typography
- پشتیبانی Dark Mode (فاز بعد) با کلاس `dark` و توکن‌های متناظر


### کیفیت و تست UI
- Unit/Integration با React Testing Library: رندر، تعامل، دسترس‌پذیری پایه
- E2E با Playwright/Cypress برای سناریوهای حیاتی (ورود، ثبت بیمار، پیش‌بینی، دانلود گزارش)
- لزوم Snapshot محدود برای اجزاء ثابت (Badge/Avatar) و پرهیز در اجزاء پویا


### چک‌لیست طراحی
- [ ] کنتراست رنگ‌ها و اندازه قلم‌ها استاندارد WCAG AA
- [ ] حالت‌های hover/active/focus/disabled پیاده و تست شده
- [ ] فرم‌ها: خطاها/validation واضح و قابل‌خواندن
- [ ] صفحات: Loading/Empty/Error مشخص
- [ ] RTL کامل و آمادگی i18n
- [ ] اجتناب از تکثیر سبک‌ها؛ استفاده از توکن‌ها و کلاس‌های مشترک


