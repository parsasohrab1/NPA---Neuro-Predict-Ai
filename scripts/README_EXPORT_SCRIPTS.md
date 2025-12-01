# راهنمای اسکریپت‌های خروجی Mermaid به Illustrator
# Guide: Mermaid to Illustrator Export Scripts

## 📋 فهرست اسکریپت‌ها

این پوشه شامل سه اسکریپت برای خروجی گرفتن از Mermaid به فرمت‌های قابل استفاده در Illustrator است:

1. **PowerShell Script** (`export_mermaid_to_illustrator.ps1`) - برای Windows
2. **Bash Script** (`export_mermaid_to_illustrator.sh`) - برای Linux/Mac
3. **Node.js Script** (`mermaid_to_illustrator.js`) - برای همه پلتفرم‌ها

---

## 🚀 استفاده سریع

### PowerShell (Windows)

```powershell
# Export تمام figures به SVG
.\scripts\export_mermaid_to_illustrator.ps1 -All -OutputFormat svg

# Export یک figure خاص
.\scripts\export_mermaid_to_illustrator.ps1 -FigureName "Figure_1_System_Architecture" -OutputFormat svg

# Export به تمام فرمت‌ها
.\scripts\export_mermaid_to_illustrator.ps1 -All -OutputFormat all

# Export با تنظیمات سفارشی
.\scripts\export_mermaid_to_illustrator.ps1 -All -OutputFormat png -DPI 600
```

### Bash (Linux/Mac)

```bash
# قابل اجرا کردن اسکریپت
chmod +x scripts/export_mermaid_to_illustrator.sh

# Export تمام figures به SVG
./scripts/export_mermaid_to_illustrator.sh --all --format svg

# Export یک figure خاص
./scripts/export_mermaid_to_illustrator.sh --figure Figure_1_System_Architecture --format svg

# Export به تمام فرمت‌ها
./scripts/export_mermaid_to_illustrator.sh --all --format all
```

### Node.js (همه پلتفرم‌ها)

```bash
# Export تمام figures به SVG
node scripts/mermaid_to_illustrator.js --all --format svg

# Export یک figure خاص
node scripts/mermaid_to_illustrator.js --figure Figure_1_System_Architecture --format svg

# Export به تمام فرمت‌ها
node scripts/mermaid_to_illustrator.js --all --format all
```

---

## 📐 فرمت‌های خروجی

### SVG (توصیه می‌شود برای Illustrator)

- **بهترین کیفیت**: Vector format
- **قابل ویرایش**: در Illustrator
- **اندازه**: 2400 × 1800 px (scalable)
- **استفاده**: مستقیماً در Illustrator باز کنید

```powershell
.\scripts\export_mermaid_to_illustrator.ps1 -All -OutputFormat svg
```

### PNG (High Resolution)

- **رزولوشن**: 600 DPI (پیش‌فرض)
- **اندازه**: 5100 × 6600 px (8.5" × 11" @ 600 DPI)
- **استفاده**: برای vectorization یا استفاده مستقیم

```powershell
.\scripts\export_mermaid_to_illustrator.ps1 -All -OutputFormat png -DPI 600
```

### PDF

- **رزولوشن**: 600 DPI
- **فرمت**: PDF/A compliant
- **نیازمند**: ImageMagick (برای تبدیل)

```powershell
.\scripts\export_mermaid_to_illustrator.ps1 -All -OutputFormat pdf
```

---

## ⚙️ پارامترها و گزینه‌ها

### PowerShell Script

| پارامتر | توضیح | پیش‌فرض |
|---------|-------|---------|
| `-FigureName` | نام figure خاص | - |
| `-All` | Export تمام figures | false |
| `-OutputFormat` | فرمت خروجی: svg, png, pdf, all | svg |
| `-DPI` | رزولوشن برای PNG/PDF | 600 |
| `-Width` | عرض SVG | 2400 |
| `-Height` | ارتفاع SVG | 1800 |

### Bash Script

| گزینه | توضیح | پیش‌فرض |
|-------|-------|---------|
| `-f, --figure` | نام figure خاص | - |
| `-a, --all` | Export تمام figures | false |
| `--format` | فرمت خروجی | svg |
| `--dpi` | رزولوشن | 600 |
| `--width` | عرض SVG | 2400 |
| `--height` | ارتفاع SVG | 1800 |

### Node.js Script

| گزینه | توضیح | پیش‌فرض |
|-------|-------|---------|
| `-f, --figure` | نام figure خاص | - |
| `-a, --all` | Export تمام figures | false |
| `--format` | فرمت خروجی | svg |

---

## 📁 ساختار خروجی

```
docs/PATENT_DRAWINGS/exports/
├── svg/                    ← SVG files (Illustrator-ready)
│   ├── Figure_1_System_Architecture.svg
│   ├── Figure_2_Neural_Network_Architecture.svg
│   └── ...
├── png/                    ← PNG files (High Resolution)
│   ├── Figure_1_System_Architecture.png
│   └── ...
├── pdf/                    ← PDF files
│   ├── Figure_1_System_Architecture.pdf
│   └── ...
└── illustrator/            ← (برای فایل‌های آماده Illustrator)
```

---

## 🎨 مراحل بعدی (استفاده در Illustrator)

### 1. باز کردن SVG در Illustrator

```
1. Adobe Illustrator → File → Open
2. انتخاب فایل SVG از exports/svg/
3. SVG به عنوان vector import می‌شود
```

### 2. ایجاد Document جدید

```
1. File → New
2. Width: 8.5 inches
3. Height: 11 inches
4. Color Mode: CMYK
```

### 3. Import و Scale

```
1. File → Place → انتخاب SVG
2. Scale به اندازه مناسب
3. قرار دادن در drawing area (با margins)
```

### 4. Enhancement

- اضافه کردن Reference Numerals
- اصلاح خطوط
- اضافه کردن Labels
- بهبود Layout

### 5. Export نهایی

```
File → Export → Export As → TIFF
Resolution: 600 DPI
Color Mode: Grayscale
Compression: None
```

---

## 🔧 پیش‌نیازها

### نصب Mermaid CLI

```bash
npm install -g @mermaid-js/mermaid-cli
```

### نصب ImageMagick (برای PDF export)

**Windows:**
- دانلود از: https://imagemagick.org/script/download.php
- یا با Chocolatey: `choco install imagemagick`

**Linux:**
```bash
sudo apt-get install imagemagick  # Ubuntu/Debian
sudo yum install ImageMagick      # CentOS/RHEL
```

**Mac:**
```bash
brew install imagemagick
```

---

## 💡 مثال‌های استفاده

### مثال 1: Export یک Figure به SVG

```powershell
.\scripts\export_mermaid_to_illustrator.ps1 `
    -FigureName "Figure_1_System_Architecture" `
    -OutputFormat svg
```

### مثال 2: Export تمام Figures به تمام فرمت‌ها

```powershell
.\scripts\export_mermaid_to_illustrator.ps1 `
    -All `
    -OutputFormat all
```

### مثال 3: Export با رزولوشن بالاتر

```powershell
.\scripts\export_mermaid_to_illustrator.ps1 `
    -All `
    -OutputFormat png `
    -DPI 1200
```

---

## ✅ چک‌لیست

قبل از استفاده:

- [ ] Mermaid CLI نصب شده
- [ ] Node.js نصب شده
- [ ] فایل‌های Mermaid در `docs/PATENT_DRAWINGS/` موجود هستند
- [ ] ImageMagick نصب شده (برای PDF export)

بعد از Export:

- [ ] فایل‌های SVG در `exports/svg/` موجود هستند
- [ ] فایل‌ها قابل باز شدن در Illustrator هستند
- [ ] کیفیت مناسب است

---

## 🆘 رفع مشکلات

### مشکل: Mermaid CLI پیدا نمی‌شود

**راه حل:**
```bash
npm install -g @mermaid-js/mermaid-cli
```

### مشکل: SVG در Illustrator باز نمی‌شود

**راه حل:**
1. فایل SVG را در مرورگر باز کنید و بررسی کنید
2. از فایل PNG استفاده کنید
3. در Illustrator: File → Place (نه Open)

### مشکل: کیفیت PNG پایین است

**راه حل:**
- DPI را افزایش دهید: `-DPI 1200`
- Scale را افزایش دهید

---

## 📚 مستندات مرتبط

- [Complete Conversion Guide](../docs/PATENT_DRAWINGS/COMPLETE_CONVERSION_GUIDE.md)
- [Step-by-Step Tutorial](../docs/PATENT_DRAWINGS/STEP_BY_STEP_TUTORIAL.md)
- [Quick Start](../docs/PATENT_DRAWINGS/QUICK_START.md)

---

**آخرین بروزرسانی**: دسامبر 2024  
**نسخه**: 1.0

