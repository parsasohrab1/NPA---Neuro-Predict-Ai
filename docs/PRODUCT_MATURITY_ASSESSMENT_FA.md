# ارزیابی بلوغ محصول NeuroPredict-AI

**تاریخ:** ۲۲ ژوئیه ۲۰۲۶  
**شاخه مرجع:** `cursor/maturity-p0-p4-implementation-892d`  
**روش:** مقایسه مستندات با کد اجرایی (نه ادعای گزارش‌های داخلی)  
**سطح بلوغ کلی:** **Honest MVP در حال تثبیت** — هنوز **نامناسب برای استفاده بالینی واقعی / SaMD**

---

## ۰) وضعیت پیاده‌سازی نقشه راه (این شاخه)

| مرحله | وضعیت | شواهد در کد |
|------|--------|-------------|
| **A — Honest MVP** | ✅ عمدتاً انجام شد | fail-closed مدل + `models/ensemble_model.pth` baseline غیر clinically-validated؛ imaging deterministic؛ mock فرانت پیش‌فرض off؛ ProtectedRoute؛ MFA روی login؛ PHI erase API |
| **B — Clinical Pilot** | 🟡 جزئی | IFU disclaimer + clinician override؛ Users/Audit/Settings ادمین به API؛ CRUD/export؛ consent محصول هنوز ناقص |
| **C — Integration** | 🟡 scaffolding صادق | PACS/HL7/FHIR دیگر success جعلی نمی‌دهند؛ MLLP/httpx وقتی env ست باشد؛ contract tests |
| **D — Regulatory** | ⚪ صداقت evidence | FDA/IRB همچنان **۰٪ اجرا**؛ `docs/EVIDENCE_PACK_INDEX_FA.md` فهرست EXISTS vs MISSING |
| **E — Multi-site Production** | ⚪ آماده‌سازی | CD gated (بدون fake deploy)؛ `infra/k8s` canonical + admin deploy؛ Playwright در CI |

---

## ۱) حکم خلاصه

NeuroPredict-AI سطح API/UI غنی دارد. این شاخه **شکاف صداقت مستند↔کد** را می‌بندد؛ اعتبارسنجی بالینی و evidence نظارتی هنوز غایب است.

| حوزه | قبل | بعد از این شاخه |
|------|-----|------------------|
| موتور AI | random fallback | fail-closed؛ baseline weights غیرvalidated |
| فرانت | mock پیش‌فرض ON | mock فقط با `VITE_USE_MOCK_DATA=true` + auth guard |
| MFA login | توکن بدون MFA | challenge + `/auth/login/mfa` |
| یکپارچگی | 200 خالی سبز | 503/501 `not_configured`/`not_implemented` |
| FDA/IRB | ادعاهای مبهم | صراحت ۰٪ + evidence index |
| Ops | CD echo | workflow_dispatch gated validators |

**نتیجه:** برای دمو/توسعه صادق‌تر است. برای مراقبت بیمار واقعی هنوز Clinical Pilot کامل + IRB/داده واقعی لازم است.

---

## ۲) شکاف صداقت مستند ↔ کد

قبلاً بزرگ‌ترین ریسک سازمانی بود. **این شاخه بسیاری از ادعاهای نادرست را با رفتار کد هم‌تراز کرد**؛ موارد باقی‌مانده:

| ادعا / موضوع | وضعیت پس از این شاخه |
|--------------|----------------------|
| وزن مدل / registry AUC | baseline `.pth` چک‌این شد با برچسب **unvalidated**؛ fail-closed اگر وزن نباشد |
| random inference | حذف‌شده مگر `DEBUG`+`ALLOW_MOCK_PREDICTIONS` |
| FHIR/PACS «کامل» | scaffolding صادق؛ 503/501 وقتی unconfigured |
| MFA روی login | ✅ challenge + `/auth/login/mfa` |
| HIPAA encryption کامل | همچنان **partial** — erase واقعی؛ encryption-at-rest تأیید نشده |
| FDA / IRB | صراحتاً **۰٪** + evidence index (جعل پیشرفت نشده) |
| mock فرانت پیش‌فرض | ✅ فقط با env صریح `true` |
| CD deploy جعلی | ✅ gated validators؛ بدون echo success |

گزارش‌های قدیمی (`خلاصه_بررسی_به_روزرسانی.md` و مشابه) ممکن است هنوز بیش‌ازحد مثبت باشند — منبع حقیقت: این سند + `STATUS.md` + evidence index.

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
