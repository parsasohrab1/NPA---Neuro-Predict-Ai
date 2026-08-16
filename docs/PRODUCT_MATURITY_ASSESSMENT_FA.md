# ارزیابی بلوغ محصول NeuroPredict-AI

**تاریخ:** ۲۲ ژوئیه ۲۰۲۶  
**شاخه مرجع:** `main`  
**روش:** مقایسه مستندات با کد اجرایی (نه ادعاهای گزارش‌های داخلی)  
**سطح بلوغ کلی:** **نمونه‌نمای پیشرفته / MVP دمو** — آماده دمو و توسعه؛ **نامناسب برای استفاده بالینی واقعی**

---

## ۱) حکم خلاصه

NeuroPredict-AI از نظر **سطح سطح (surface area)** غنی است: FastAPI، React، داشبورد ادمین، اسکیماهای FHIR/HL7، مانیتورینگ، CI، و مستندات بسیار زیاد. اما در مسیرهای حیاتی محصول پزشکی، هنوز **شِلِ MVP** است:

| حوزه | سطح بلوغ | توضیح یک‌خطی |
|------|----------|---------------|
| دامنه API و مدل داده | MVP | CRUD بیمار/پیش‌بینی واقعی؛ سطح پوشش خوب |
| موتور AI بالینی | Prototype | بدون وزن مدل واقعی؛ fallback به random/heuristic |
| یکپارچگی بیمارستانی | Prototype | سازنده پیام/منبع؛ ارسال/دریافت واقعی ناقص |
| فرانت کلینیکال | Low–Medium | mock پیش‌فرض؛ گارد احراز هویت ضعیف |
| داشبورد ادمین | Medium | صفحات بالینی عمیق‌تر؛ Users/Audit/Settings نمونه |
| امنیت عملیاتی | Early MVP | JWT/RBAC هست؛ MFA در login اعمال نشده |
| انطباق (FDA/IRB/HIPAA) | Very Low | چک‌لیست‌ها ۰٪؛ مستندات اغلب بیش‌ادعا |
| Ops / CD | Low–Medium | CI قابل قبول؛ CD و k8s ناقص/دوگانه |
| کیفیت تست | Early MVP | تست‌ها زیاد اما اغلب mock/skip؛ E2E در CI نیست |

**نتیجه:** محصول برای **دمو، جذب سرمایه، و توسعه مشترک** مناسب است. برای **مراقبت بیمار، PHI واقعی، یا ادعای SaMD** هنوز فاصله معنادار دارد.

---

## ۲) شکاف صداقت مستند ↔ کد

این بزرگ‌ترین ریسک بلوغ سازمانی است: گزارش‌های داخلی (`STATUS.md`، `خلاصه_بررسی_به_روزرسانی.md`، `docs/COMPLIANCE_DOCUMENTATION.md`، `INTEGRATION_SUMMARY.md`) اغلب «کامل» یا «آماده» نشان می‌دهند، در حالی که:

| ادعا | واقعیت کد |
|------|-----------|
| مدل production با AUC بالا در registry | فقط `models/registry.json`؛ فایل `.pth` وجود ندارد |
| پیش‌بینی AI کامل | `ai_model_service.py`: در نبود وزن → random initialization |
| FHIR/PACS پیاده‌سازی‌شده | ساختار/stub؛ جستجوی خالی، بدون DIMSE واقعی |
| MFA پیاده‌سازی‌شده | API وجود دارد؛ **login توکن بدون چک MFA** صادر می‌کند |
| HIPAA/رمزنگاری در سکون کامل | فیلدهای PHI بیمار plaintext؛ رمزنگاری عمدتاً برای MFA secret |
| FDA 510(k) / IRB در مسیر | چک‌لیست FDA و tracker IRB هر دو **۰٪** |
| Vite 7 / E2E کامل | هنوز Vite 5؛ E2E در CI اجرا نمی‌شود |
| `VITE_USE_MOCK_DATA` کنترل‌شده | پیش‌فرض روشن وقتی env خالی است |

---

## ۳) نواقص اولویت‌بندی‌شده

### P0 — مسدودکننده استفاده بالینی / PHI

1. **وزن مدل و fail-closed**  
   بدون `.pth` معتبر، inference را رد کنید (نه random). checksum و version pin اجباری.

2. **ویژگی تصویر واقعی**  
   `np.random.randn(32)` در پردازش تصویر و `np.zeros` در training imaging channel را جایگزین کنید؛ در غیر این صورت «multimodal» نادرست است.

3. **خاموش کردن mock پیش‌فرض فرانت**  
   `VITE_USE_MOCK_DATA` پیش‌فرض `false`؛ در خطای API به داده ساختگی برنگردید.

4. **گارد احراز هویت روی مسیرهای بالینی**  
   فرانت و ادمین: redirect اجباری؛ مسیر `/login` ادمین را ثبت کنید؛ sample-data/clear-all را در غیر-DEBUG ببندید.

5. **اعمال MFA روی login** + رمزنگاری backup codes + revocation توکن.

6. **PHI و حریم خصوصی واقعی**  
   رمزنگاری در سکون برای فیلدهای حساس، erasure کامل (نه stub)، و BAA/فرآیند سازمانی — نه فقط چک‌لیست تیک‌خورده.

### P1 — گردش‌کار CDSS واقعی

7. **IFU / disclaimer «تشخیص نیست»** روی صفحه نتیجه پیش‌بینی.  
8. **تأیید/Override پزشک** با ثبت audit تصمیم.  
9. **رضایت/consent** در محصول (نه فقط در docs IRB).  
10. **اتصال Users / Roles / Audit / Settings** ادمین به API واقعی (حذف mockهای محلی).  
11. **تکمیل CRUD بیمار و export** (دکمه‌های بدون handler / `alert` را حذف یا وصل کنید).

### P2 — یکپارچگی بیمارستانی

12. **PACS واقعی** (C-FIND/C-MOVE/C-STORE) یا برچسب صریح Experimental.  
13. **HL7 send با ACK** (نه log-only `return True`).  
14. **کلاینت FHIR remote** + ImagingStudy واقعی.  
15. تست یکپارچگی با WireMock/شبیه‌ساز — نه assert روی `[200,404,500]`.

### P3 — انطباق نظارتی (حقیقت‌محور)

16. اجرای فازهای `IRB_IMPLEMENTATION_TRACKER` قبل از داده بیمار واقعی.  
17. پر کردن `FDA_510K_CHECKLIST` با شواهد (نه معماری).  
18. QMS سبک (ISO 13485 / design controls) و label/IFU قفل‌شده به نسخه نرم‌افزار.  
19. بازنگری/اصلاح گزارش‌هایی که وضعیت را بیش‌ازحد مثبت نشان می‌دهند.

### P4 — Ops و کیفیت مهندسی

20. جایگزینی placeholderهای CD (`cd-prod.yml` / `deploy-production.yml`).  
21. یکپارچه‌سازی درخت‌های `k8s/` و `infra/k8s/` + Deployments فرانت/ادمین.  
22. Backup از `DATABASE_URL` واقعی + offsite واقعی + تمرین restore.  
23. Rate limit مشترک Redis برای همه workerها؛ سخت‌گیری CSP.  
24. Playwright در CI؛ پوشش روی `ai_model_service` / security / integrations.  
25. بستن advisory Vite 5؛ کانال امنیتی واقعی به‌جای `security@example.com`.

---

## ۴) امتیاز بلوغ پیشنهادی (۰–۵)

| محور | امتیاز | یادداشت |
|------|--------|---------|
| قابلیت دمو و داستان محصول | **۴** | معماری و UI غنی |
| صحت فنی هسته AI | **۱٫۵** | بدون وزن واقعی |
| یکپارچگی HIS/PACS | **۱٫۵** | شِل API |
| امنیت و هویت | **۲٫۵** | پایه خوب، حفره‌های بحرانی |
| انطباق پزشکی | **۱** | docs ≫ evidence |
| آمادگی تولید | **۲** | CI خوب؛ CD ضعیف |
| کیفیت نرم‌افزار (تست/DoD) | **۲** | حجم تست ≠ اطمینان |
| **میانگین وزنی محصول پزشکی** | **≈ ۲ / ۵** | MVP دمو، نه SaMD |

---

## ۵) نقشه راه بلوغ (فنی، نه تقویمی)

```
مرحله A — Honest MVP
  fail-closed مدل · خاموش mock · auth gate · disclaimer IFU

مرحله B — Clinical Pilot Ready
  وزن آموزش‌دیده + اعتبارسنجی · MFA اجباری · PHI encryption
  override پزشک · audit تصمیم · حذف sample-data در prod

مرحله C — Hospital Integration
  PACS/HL7/FHIR end-to-end · تست قرارداد · DR تمرین‌شده

مرحله D — Regulatory Path
  IRB اجرا · داده واقعی · clinical validation · 510(k) evidence pack
  QMS + labeling قفل‌شده به نسخه

مرحله E — Multi-site Production
  CD واقعی · k8s یکپارچه · SLA/observability · drift monitoring
```

هر مرحله باید با **معیار خروج قابل اندازه‌گیری** بسته شود (مثلاً: «inference بدون وزن → HTTP 503»، «mock data در prod غیرممکن»، «IRB phase 1–3 کامل»).

---

## ۶) KPI بلوغ (پیشنهاد اندازه‌گیری)

| KPI | وضعیت فعلی تقریبی | هدف مرحله B |
|-----|-------------------|-------------|
| درصد inference با وزن checksum‌شده | ~0% | 100% |
| mock data در محیط غیر-dev | پیش‌فرض روشن | ممنوع |
| MFA enforced برای نقش‌های بالینی | API only | 100% login path |
| مسیرهای PHI بدون auth | باز در فرانت | 0 |
| پوشش تست مسیرهای حیاتی (AI/auth/integration) | پایین/mock | ≥70% واقعی |
| پیشرفت IRB tracker | 0% | ≥ فازهای رضایت و پروتکل |
| پیشرفت FDA checklist با evidence | 0% | بخش Device + Labeling شروع‌شده |
| CD deploy واقعی (نه echo) | خیر | stage خودکار |

---

## ۷) توصیه مدیریتی

1. **زبان محصول را صادق کنید:** «CDSS کمکی در حال توسعه / فقط برای تحقیق و دمو» تا زمان تکمیل مراحل A–B.  
2. **جلوی تورم مستندات را بگیرید:** هر ✅ باید به تست خودکار یا artifact قابل ممیزی وصل باشد.  
3. **اولویت را از feature جدید به بستن مسیرهای حیاتی منتقل کنید** (مدل، mock، auth، IFU).  
4. **یک Owner بلوغ** تعیین کنید که گزارش‌های وضعیت را فقط بر اساس evidence به‌روز کند.

---

## ۸) شواهد کلیدی (مسیر فایل)

- `models/` — فقط `registry.json` (بدون وزن)
- `backend/app/services/ai_model_service.py` — random initialization
- `backend/app/api/models.py` — Mock model data
- `frontend/src/services/api.ts` — mock پیش‌فرض
- `docs/FDA_510K_CHECKLIST.md` — 0%
- `docs/IRB_IMPLEMENTATION_TRACKER.md` — 0%
- `STATUS.md` — صراحتاً: NOT ready for production clinical use

---

**تهیه‌کننده:** ارزیابی خودکار کد و مستندات (Cloud Agent)  
**محدودیت:** این سند ممیزی رسمی امنیتی/بالینی نیست؛ مبنایی برای اولویت‌بندی محصول است.
