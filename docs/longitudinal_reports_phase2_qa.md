## QA Checklist – Longitudinal Reports Phase 2

### Backend API
- [ ] ایجاد گزارش Summary با بازه زمانی و بررسی خروجی Excel/PDF.
- [ ] ایجاد گزارش `cohort_patient_vs_average` و اطمینان از وجود Heatmap و داده مقایسه‌ای.
- [ ] دریافت Heatmap از مسیر `GET /api/v1/longitudinal/reports/{id}/heatmap`.
- [ ] مدیریت خطاها: نبود داده (کد 400)، شناسه نامعتبر (کد 404).
- [ ] ساخت، به‌روزرسانی وضعیت، حذف، و اجرای دستی Schedule ها.
- [ ] ثبت اجرای زمان‌بندی در `longitudinal_report_runs` و بررسی فیلدهای `started_at`, `finished_at`, `status`.

### فرانت‌اند Admin Dashboard
- [ ] تولید گزارش Summary و Cohort از طریق UI و دانلود Excel/PDF.
- [ ] مشاهده Heatmap در Modal و بستن آن بدون Memory leak (Object URL آزاد شود).
- [ ] تکمیل فرم فیلتر Cohort (جنسیت، سن، patient IDs) و اعتبارسنجی ورودی‌ها.
- [ ] ساخت Schedule جدید (نام، cron، نوع گزارش) و مشاهده در لیست.
- [ ] تغییر وضعیت Schedule (Pause/Resume)، حذف، و اجرای Run Now.
- [ ] نمایش لیست Runs با وضعیت‌ها و پیام خطا، اجرای دستی Run در حالت queued.
- [ ] رفرش خودکار جداول پس از عملیات (بدون نیاز به refresh دستی صفحه).

### سناریوهای مرزی
- [ ] انتخاب Episode بدون ویزیت → پیام مناسب هنگام تولید گزارش.
- [ ] ثبت Schedule برای Episode دیگر و فیلتر شدن در UI (نمایش فقط Scheduleهای اپیزود فعال).
- [ ] حذف فایل Heatmap در سرور → UI پیام «Heatmap not available».
- [ ] زمان‌بندی با Cron نامعتبر → پیام خطای مناسب در UI و API.
- [ ] تست عملکرد در صورت نبود Matplotlib/Seaborn (خطای کنترل‌شده).

### مستندات و پشتیبانی
- [ ] بروزرسانی README/Spec با توضیحات نحوه استفاده از Scheduling و Cohort Reports.
- [ ] ثبت مثال Cron (روزانه، هفتگی، ماهانه) و نکات مربوط به timezone سرور.

