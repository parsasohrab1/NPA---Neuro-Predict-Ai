# فهرست بسته شواهد FDA / IRB (Evidence Pack Index)

**تاریخ:** ژوئیه ۲۰۲۶  
**شاخه:** `cursor/maturity-p0-p4-implementation-892d`  
**هدف:** تمایز صریح بین آنچه **در repo وجود دارد** و آنچه برای مسیر نظارتی **غایب** است.

> این سند جایگزین ارسال FDA/IRB نیست. فقط نقشه صداقت evidence است.

---

## خلاصه

| حوزه | وضعیت evidence در repo | درصد اجرایی واقعی |
|------|------------------------|-------------------|
| FDA 510(k) | عمدتاً چک‌لیست و پیش‌نویس متنی | **0%** submission |
| IRB | Tracker و راهنما؛ بدون پروتکل/رضایت ثبت‌شده | **0%** execution |
| HIPAA / BAA | سیاست‌های متنی؛ رمزنگاری PHI در سکون تأیید نشده | Designed / partial |
| QMS / ISO 13485 | سند برنامه‌ای | Not started |

---

## FDA 510(k) — EXISTS در repo

| Artifact | Path | Note |
|----------|------|------|
| Device description draft | `docs/FDA_510K_Device_Description.md` | پیش‌نویس متنی؛ formal submission نیست |
| 510(k) checklist (0%) | `docs/FDA_510K_CHECKLIST.md` | برنامه‌ریزی؛ همه بخش‌ها ⬜ |
| Quick start / guides | `docs/FDA_510K_*.md` | راهنما، نه evidence |
| Product maturity assessment | `docs/PRODUCT_MATURITY_ASSESSMENT_FA.md` | ارزیابی داخلی محصول |

## FDA 510(k) — MISSING

| Artifact | Expected location | Status |
|----------|-------------------|--------|
| FDA Form 3514 | `forms/FDA_3514_510k_Form.pdf` | **MISSING** (`forms/` absent) |
| FDA Form 3674 | `forms/FDA_3674_Statement.pdf` | **MISSING** |
| FDA Form 3601 | `forms/FDA_3601_Fee_Cover_Sheet.pdf` | **MISSING** |
| Cover letter (signed) | — | **MISSING** |
| Executive summary (locked) | — | **MISSING** |
| Predicate device analysis pack | — | **MISSING** |
| Clinical validation study report | — | **MISSING** |
| Software bill of materials / SBOM signed | — | **MISSING** |
| Labeling / IFU locked to version | — | **MISSING** |
| Design history file (DHF) | — | **MISSING** |

---

## IRB — EXISTS در repo

| Artifact | Path | Note |
|----------|------|------|
| Implementation tracker (0%) | `docs/IRB_IMPLEMENTATION_TRACKER.md` | همه فازها شروع‌نشده |
| Process / quick guides | `docs/IRB_*.md` | راهنما |

## IRB — MISSING

| Artifact | Status |
|----------|--------|
| Named PI / study team roster | **MISSING** |
| CITI / GCP / HIPAA training certificates | **MISSING** |
| Protocol version on file | **MISSING** |
| Informed consent form (IRB-stamped) | **MISSING** |
| IRB submission receipt / approval letter | **MISSING** |
| Site delegation log | **MISSING** |
| `forms/` directory with IRB PDFs | **MISSING** |

---

## HIPAA / امنیت — EXISTS vs MISSING

| Claim historically marked "✅ complete" | Reality in code/repo |
|----------------------------------------|----------------------|
| Encryption at rest (AES-256) for PHI | **Partial / not verified** — patient PHI fields largely plaintext; crypto used mainly for secrets (e.g. MFA) |
| Business Associate Agreements (BAA) | **Missing as signed artifacts** — no BAA PDFs in repo; policy text only |
| Encryption in transit (TLS) | **Designed** — depends on deployment ingress/certs; not proven by evidence pack |
| Audit logging | **Partial** — code paths exist; retention/review evidence incomplete |
| Access control (RBAC) | **Partial** — JWT/RBAC present; MFA not fully enforced on login historically |

See softened language in `docs/COMPLIANCE_DOCUMENTATION.md`.

---

## نحوه به‌روزرسانی این فهرست

1. فقط وقتی artifact واقعی commit یا به vault لینک شد، ردیف را از MISSING به EXISTS ببرید.
2. درصدهای `FDA_510K_CHECKLIST.md` / `IRB_IMPLEMENTATION_TRACKER.md` را **بدون** شاهد بالا نبرید.
3. هر ✅ جدید باید به مسیر فایل یا ticket ممیزی ارجاع دهد.
