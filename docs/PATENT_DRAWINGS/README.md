# نقشه‌های فنی Patent - NeuroPredict-AI
# Patent-Quality Technical Drawings

## 📋 فهرست محتوا

این پوشه شامل تمام نقشه‌های فنی مورد نیاز برای ثبت اختراع NeuroPredict-AI است.

---

## 🎯 هدف

ایجاد نقشه‌های فنی با کیفیت بالا و استاندارد USPTO برای:
- ثبت اختراع Utility Patent
- مستندسازی سیستم
- ارائه در FDA 510(k) Submission

---

## 📁 ساختار فایل‌ها

```
PATENT_DRAWINGS/
├── README.md                                    ← این فایل
├── PATENT_DRAWINGS_GUIDE.md                    ← راهنمای کامل
├── FIGURES_SPECIFICATIONS.md                   ← مشخصات تمام نقشه‌ها
├── CONVERSION_GUIDE.md                         ← راهنمای تبدیل
│
├── Figure_1_System_Architecture.md             ← Figure 1: معماری سیستم
├── Figure_2_Neural_Network_Architecture.md     ← Figure 2: معماری شبکه عصبی
├── Figure_3_Data_Fusion_System.md              ← Figure 3: سیستم Data Fusion
├── Figure_4_Clinical_Workflow.md               ← Figure 4: جریان کار بالینی
│
└── exports/                                     ← خروجی‌های تولید شده
    ├── svg/                                    ← فایل‌های SVG
    ├── png/                                    ← فایل‌های PNG
    └── pdf/                                    ← فایل‌های PDF
```

---

## 📊 نقشه‌های مورد نیاز

### نقشه‌های اصلی (الزامی)

| Figure | عنوان | وضعیت | اولویت |
|--------|-------|-------|--------|
| **Figure 1** | System Architecture | ✅ آماده | بالا |
| **Figure 2** | Neural Network Architecture | ✅ آماده | بالا |
| **Figure 3** | Data Fusion System (Patent-Pending) | ✅ آماده | **بسیار بالا** |
| **Figure 4** | Clinical Workflow | ✅ آماده | بالا |
| **Figure 5** | Image Processing Pipeline | ⬜ در انتظار | متوسط |
| **Figure 6** | Detailed Data Fusion Algorithm | ⬜ در انتظار | **بسیار بالا** |

### نقشه‌های تکمیلی (توصیه می‌شود)

| Figure | عنوان | وضعیت |
|--------|-------|-------|
| **Figure 7** | Feature Extraction Process | ⬜ |
| **Figure 8** | Risk Stratification Algorithm | ⬜ |
| **Figure 9** | User Interface Layout | ⬜ |
| **Figure 10** | Database Schema | ⬜ |

---

## 🚀 شروع سریع

### مرحله 1: تولید دیاگرام‌های اولیه

**Windows:**
```powershell
.\scripts\generate_patent_diagrams.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/generate_patent_diagrams.sh
./scripts/generate_patent_diagrams.sh
```

این اسکریپت:
- دیاگرام‌های Mermaid را می‌خواند
- به SVG و PNG با رزولوشن بالا تبدیل می‌کند
- در `docs/PATENT_DRAWINGS/exports/` ذخیره می‌کند

### مرحله 2: تبدیل به Patent Drawings رسمی

1. **Import به Illustrator/Inkscape**
   - باز کردن SVG/PNG files
   - Create New Document: 21.6 cm × 27.9 cm

2. **اضافه کردن Reference Numerals**
   - استفاده از Type Tool
   - Font: Arial Bold, Size: 8-10 pt
   - اعداد: 100, 110, 120, ...

3. **Enhancement**
   - اصلاح خطوط (0.3-0.5 mm)
   - اضافه کردن Labels
   - بهبود Layout

4. **Export نهایی**
   - فرمت: TIFF یا PDF
   - رزولوشن: 600 DPI
   - اندازه: 21.6 × 27.9 cm

---

## 📐 استانداردهای USPTO

### الزامات اصلی:

- ✅ **اندازه صفحه**: 21.6 cm × 27.9 cm (8.5" × 11")
- ✅ **Margins**: Top 2.5 cm, Others 1.3 cm
- ✅ **رزولوشن**: حداقل 300 DPI (ترجیح 600 DPI)
- ✅ **فرمت**: TIFF (ترجیح) یا PDF
- ✅ **Reference Numerals**: حداقل 1.32 mm
- ✅ **خطوط**: 0.3-0.5 mm (ضخامت)
- ✅ **رنگ**: سیاه و سفید (رنگی فقط در صورت ضرورت)

---

## 🎨 نقشه‌های Patent-Pending

### ⚠️ نقشه‌های حیاتی برای اختراع:

1. **Figure 3**: Data Fusion System
   - **وضعیت**: ⚠️ **PATENT-PENDING CORE INNOVATION**
   - این نقشه باید به دقت و با Highlight ترسیم شود

2. **Figure 6**: Detailed Data Fusion Algorithm
   - جزئیات الگوریتم Fusion
   - فرمول‌های ریاضی
   - جریان محاسبات

---

## 📚 راهنماها

### راهنماهای موجود:

1. **`PATENT_DRAWINGS_GUIDE.md`**
   - راهنمای کامل تهیه Patent Drawings
   - استانداردهای USPTO
   - ابزارها و نرم‌افزارها

2. **`FIGURES_SPECIFICATIONS.md`**
   - مشخصات تمام نقشه‌ها
   - Reference Numerals کامل
   - توضیحات جزئیات

3. **`COMPLETE_CONVERSION_GUIDE.md`** ⭐ **جدید و کامل**
   - راهنمای جامع تبدیل به Patent Drawings رسمی
   - مراحل کامل گام به گام
   - راهنمای Illustrator و Inkscape
   - چک‌لیست کامل USPTO

4. **`STEP_BY_STEP_TUTORIAL.md`** ⭐ **جدید و عملی**
   - آموزش گام به گام عملی
   - مثال‌های واقعی
   - Tips & Tricks
   - رفع مشکلات رایج

5. **`QUICK_START.md`** ⭐ **شروع سریع**
   - Quick Start در 5 مرحله
   - چک‌لیست سریع

6. **`CONVERSION_GUIDE.md`**
   - راهنمای تبدیل Diagrams-as-Code (نسخه قدیمی)
   - برای مرجع استفاده کنید

---

## ✅ پیشرفت

```
نقشه‌های آماده: [████░░░░░░] 40%

✅ Figure 1: System Architecture
✅ Figure 2: Neural Network Architecture
✅ Figure 3: Data Fusion System
✅ Figure 4: Clinical Workflow
⬜ Figure 5: Image Processing Pipeline
⬜ Figure 6: Detailed Data Fusion Algorithm
⬜ Figure 7-10: Additional Figures
```

---

## 🔧 ابزارهای مورد نیاز

### برای تولید اولیه:
- ✅ Mermaid CLI (برای export)
- ✅ Node.js

### برای ترسیم رسمی:
- ⬜ Adobe Illustrator ($$$) - بهترین
- ⬜ Inkscape (رایگان) - جایگزین مناسب
- ⬜ CorelDRAW ($$) - جایگزین

---

## 📝 مراحل بعدی

### فوری (این هفته):

1. ✅ تولید دیاگرام‌های Mermaid (انجام شده)
2. ⬜ Export به SVG/PNG
3. ⬜ Review و اصلاح

### کوتاه‌مدت (این ماه):

1. ⬜ تبدیل به Patent Drawings رسمی
2. ⬜ اضافه کردن Reference Numerals
3. ⬜ Enhancement در Illustrator/Inkscape
4. ⬜ Review توسط Patent Attorney

### میان‌مدت (2-3 ماه):

1. ⬜ تکمیل تمام نقشه‌ها
2. ⬜ Final Review
3. ⬜ آماده‌سازی برای ثبت اختراع

---

## 📞 منابع

### USPTO Resources:
- [Patent Drawing Requirements](https://www.uspto.gov/patents/apply/filing-online/patent-drawings)
- [Drawing Standards](https://www.uspto.gov/web/offices/pac/mpep/s608.html)

### Tools:
- [Mermaid Live Editor](https://mermaid.live)
- [Adobe Illustrator](https://www.adobe.com/products/illustrator.html)
- [Inkscape](https://inkscape.org/)

---

**آخرین بروزرسانی**: دسامبر 2024  
**وضعیت**: در حال توسعه  
**نسخه**: 1.0

