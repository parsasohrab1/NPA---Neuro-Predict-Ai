# راهنمای کامل: خروجی گرفتن از Mermaid به Illustrator
# Complete Guide: Exporting Mermaid to Illustrator

## 🎯 خلاصه

این راهنما تمام ابزارها و اسکریپت‌های لازم برای تبدیل دیاگرام‌های Mermaid به فرمت‌های قابل استفاده در Adobe Illustrator را ارائه می‌دهد.

---

## 📋 فهرست محتوا

1. [اسکریپت‌های موجود](#اسکریپتهای-موجود)
2. [استفاده سریع](#استفاده-سریع)
3. [فرمت‌های خروجی](#فرمتهای-خروجی)
4. [مراحل بعدی (Illustrator)](#مراحل-بعدی-illustrator)
5. [راهنماهای کامل](#راهنماهای-کامل)

---

## 🔧 اسکریپت‌های موجود

### 1. PowerShell Script (Windows) ⭐ توصیه می‌شود

**فایل**: `scripts/export_mermaid_to_illustrator.ps1`

**ویژگی‌ها:**
- ✅ پارامترهای پیشرفته
- ✅ Export به SVG, PNG, PDF
- ✅ تنظیمات DPI و اندازه
- ✅ Export دسته‌ای یا تک‌تک

**استفاده:**
```powershell
.\scripts\export_mermaid_to_illustrator.ps1 -All -OutputFormat svg
```

### 2. Bash Script (Linux/Mac)

**فایل**: `scripts/export_mermaid_to_illustrator.sh`

**ویژگی‌ها:**
- ✅ همانند PowerShell script
- ✅ قابل اجرا در Linux/Mac
- ✅ پارامترهای command-line

**استفاده:**
```bash
chmod +x scripts/export_mermaid_to_illustrator.sh
./scripts/export_mermaid_to_illustrator.sh --all --format svg
```

### 3. Node.js Script (همه پلتفرم‌ها)

**فایل**: `scripts/mermaid_to_illustrator.js`

**ویژگی‌ها:**
- ✅ Cross-platform
- ✅ قابل استفاده در CI/CD
- ✅ Module-based (قابل import)

**استفاده:**
```bash
node scripts/mermaid_to_illustrator.js --all --format svg
```

---

## 🚀 استفاده سریع

### مثال 1: Export تمام Figures به SVG

```powershell
# PowerShell
.\scripts\export_mermaid_to_illustrator.ps1 -All -OutputFormat svg
```

```bash
# Bash
./scripts/export_mermaid_to_illustrator.sh --all --format svg
```

```bash
# Node.js
node scripts/mermaid_to_illustrator.js --all --format svg
```

### مثال 2: Export یک Figure خاص

```powershell
.\scripts\export_mermaid_to_illustrator.ps1 `
    -FigureName "Figure_1_System_Architecture" `
    -OutputFormat svg
```

### مثال 3: Export به تمام فرمت‌ها

```powershell
.\scripts\export_mermaid_to_illustrator.ps1 -All -OutputFormat all
```

### مثال 4: Export با رزولوشن بالا

```powershell
.\scripts\export_mermaid_to_illustrator.ps1 `
    -All `
    -OutputFormat png `
    -DPI 1200
```

---

## 📐 فرمت‌های خروجی

### SVG (توصیه می‌شود برای Illustrator)

**ویژگی‌ها:**
- ✅ Vector format (بی‌نهایت scalable)
- ✅ قابل ویرایش در Illustrator
- ✅ کیفیت بالا
- ✅ حجم فایل کم

**استفاده:**
1. Illustrator → File → Open
2. انتخاب فایل SVG
3. SVG به صورت vector import می‌شود
4. قابل ویرایش و enhancement

**تنظیمات:**
- Width: 2400 px
- Height: 1800 px
- Scale: 2x
- Background: White

### PNG (High Resolution)

**ویژگی‌ها:**
- ✅ Raster format
- ✅ رزولوشن بالا (600 DPI)
- ✅ مناسب برای vectorization

**استفاده:**
1. Illustrator → File → Place
2. Object → Image Trace → Make
3. Settings: High Fidelity Photo

**تنظیمات:**
- Width: 5100 px (8.5" @ 600 DPI)
- Height: 6600 px (11" @ 600 DPI)
- Scale: 3x

### PDF

**ویژگی‌ها:**
- ✅ PDF/A compliant
- ✅ مناسب برای sharing
- ✅ نیازمند ImageMagick

**استفاده:**
- مستقیماً در Illustrator باز کنید
- یا برای sharing استفاده کنید

---

## 🎨 مراحل بعدی (Illustrator)

### مرحله 1: باز کردن SVG در Illustrator

```
1. Adobe Illustrator
2. File → Open
3. انتخاب: docs/PATENT_DRAWINGS/exports/svg/Figure_X.svg
4. SVG به صورت vector import می‌شود
```

### مرحله 2: ایجاد Document جدید (8.5" × 11")

```
1. File → New
2. Width: 8.5 inches
3. Height: 11 inches
4. Units: Inches
5. Color Mode: CMYK
6. Orientation: Portrait
```

### مرحله 3: Import SVG به Document جدید

```
1. File → Place
2. انتخاب فایل SVG
3. Place در صفحه
4. Scale به اندازه مناسب (حدود 80-90%)
5. قرار دادن داخل drawing area
```

### مرحله 4: Enhancement

```
1. اصلاح خطوط (Stroke Weight: 0.5 pt)
2. حذف عناصر غیرضروری
3. Organize layers
4. Alignment
```

### مرحله 5: شماره‌گذاری

```
1. Type Tool (T)
2. Font: Arial Bold, 10 pt
3. اضافه کردن Reference Numerals: 100, 110, 120, ...
4. Leader Lines
```

### مرحله 6: Export نهایی

```
1. File → Export → Export As → TIFF
2. Resolution: 600 DPI
3. Color Mode: Grayscale
4. Compression: None
```

---

## 📚 راهنماهای کامل

### برای تبدیل به Patent Drawings:

1. **📖 [Complete Conversion Guide](docs/PATENT_DRAWINGS/COMPLETE_CONVERSION_GUIDE.md)**
   - راهنمای جامع و کامل
   - تمام مراحل با جزئیات

2. **📖 [Step-by-Step Tutorial](docs/PATENT_DRAWINGS/STEP_BY_STEP_TUTORIAL.md)**
   - آموزش گام به گام
   - مثال‌های عملی

3. **📖 [Quick Start](docs/PATENT_DRAWINGS/QUICK_START.md)**
   - شروع سریع در 5 مرحله
   - برای کاربران با تجربه

4. **📖 [Export Scripts Guide](scripts/README_EXPORT_SCRIPTS.md)**
   - راهنمای کامل اسکریپت‌ها
   - تمام پارامترها و گزینه‌ها

---

## ⚙️ پیش‌نیازها

### الزامی:

- ✅ **Node.js** (v14+)
- ✅ **Mermaid CLI**: `npm install -g @mermaid-js/mermaid-cli`

### اختیاری (برای PDF):

- ⬜ **ImageMagick**: برای تبدیل PNG به PDF

---

## 📁 ساختار فایل‌ها

```
scripts/
├── export_mermaid_to_illustrator.ps1    ← PowerShell Script
├── export_mermaid_to_illustrator.sh     ← Bash Script
├── mermaid_to_illustrator.js            ← Node.js Script
└── README_EXPORT_SCRIPTS.md             ← راهنمای کامل

docs/PATENT_DRAWINGS/
├── exports/
│   ├── svg/                             ← SVG files (Illustrator-ready)
│   ├── png/                             ← PNG files (High Resolution)
│   └── pdf/                             ← PDF files
└── ...
```

---

## ✅ چک‌لیست استفاده

### قبل از Export:

- [ ] Node.js نصب شده
- [ ] Mermaid CLI نصب شده
- [ ] فایل‌های Mermaid موجود هستند

### بعد از Export:

- [ ] فایل‌های SVG در `exports/svg/` موجود هستند
- [ ] فایل‌ها قابل باز شدن در Illustrator هستند
- [ ] کیفیت مناسب است

### در Illustrator:

- [ ] Document 8.5" × 11" ایجاد شده
- [ ] SVG import شده
- [ ] Reference Numerals اضافه شده
- [ ] Export به TIFF انجام شده

---

## 🔗 لینک‌های مفید

- [Mermaid CLI Documentation](https://github.com/mermaid-js/mermaid-cli)
- [Adobe Illustrator Help](https://helpx.adobe.com/illustrator/)
- [USPTO Drawing Standards](https://www.uspto.gov/web/offices/pac/mpep/s608.html)

---

**آخرین بروزرسانی**: دسامبر 2024  
**وضعیت**: Complete  
**نسخه**: 1.0

