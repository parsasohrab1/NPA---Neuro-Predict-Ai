# راهنمای تبدیل Diagrams-as-Code به Patent Drawings رسمی
# Guide: Converting Diagrams-as-Code to Patent-Quality Drawings

## 📋 فهرست مطالب

1. [مرور فرآیند تبدیل](#مرور-فرآیند-تبدیل)
2. [روش 1: Mermaid → SVG → Illustrator](#روش-1-mermaid--svg--illustrator)
3. [روش 2: Mermaid → PNG → Vectorization](#روش-2-mermaid--png--vectorization)
4. [روش 3: ترسیم از صفر در Illustrator](#روش-3-ترسیم-از-صفر-در-illustrator)
5. [چک‌لیست نهایی](#چکلیست-نهایی)

---

## 🎯 مرور فرآیند تبدیل

### مسیر تبدیل

```
Mermaid Diagram (Text) 
    ↓
SVG/PNG Export (High Resolution)
    ↓
Import to Illustrator/Inkscape
    ↓
Vector Conversion & Enhancement
    ↓
Numbering & Labeling
    ↓
Final Patent-Quality Drawing (TIFF/PDF)
```

---

## 🔧 روش 1: Mermaid → SVG → Illustrator

### مرحله 1: Export از Mermaid

**ابزارها:**
- Mermaid Live Editor (https://mermaid.live)
- Mermaid CLI
- VS Code Extension

**مرحله 1.1: استفاده از Mermaid Live Editor**

1. باز کردن https://mermaid.live
2. کپی کردن کد Mermaid از فایل‌های ما
3. Paste در editor
4. Download as SVG (High Resolution)

**مرحله 1.2: استفاده از Mermaid CLI**

```bash
# نصب Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# تبدیل به SVG
mmdc -i Figure_2_Neural_Network.mmd -o Figure_2_Neural_Network.svg -b white

# تبدیل به PNG با رزولوشن بالا
mmdc -i Figure_2_Neural_Network.mmd -o Figure_2_Neural_Network.png -w 2400 -H 1800 -b white
```

### مرحله 2: Import به Adobe Illustrator

1. **باز کردن Illustrator**
   - Create New Document
   - Size: 21.6 cm × 27.9 cm (8.5" × 11")
   - Color Mode: CMYK (یا RGB برای Digital)

2. **Import SVG**
   - File → Open → Select SVG file
   - یا File → Place → Select SVG

3. **تبدیل به Vector**
   - اگر SVG نیست، Object → Image Trace → Make
   - تنظیمات: High Fidelity Photo

### مرحله 3: Enhancement در Illustrator

**3.1 اصلاح خطوط:**
- Select All
- Stroke Weight: 0.5 pt (برای خطوط اصلی)
- Color: Black (#000000)

**3.2 اضافه کردن Reference Numerals:**
- استفاده از Type Tool
- Font: Arial Bold
- Size: 8 pt (حداقل 1.32 mm)
- Placement: خارج از شکل با خطوط leader

**3.3 اضافه کردن Labels:**
- Labels واضح برای تمام components
- Font: Arial Regular
- Size: 10 pt

**3.4 تنظیم Layout:**
- Align elements
- Consistent spacing
- Professional appearance

### مرحله 4: Export نهایی

**Export به TIFF:**
```
File → Export → Export As → TIFF
Resolution: 600 DPI
Color Mode: CMYK
Compression: None
```

**Export به PDF:**
```
File → Save As → PDF
Preset: High Quality Print
Resolution: 600 DPI
```

---

## 🔧 روش 2: Mermaid → PNG → Vectorization

### مرحله 1: Export به PNG با رزولوشن بالا

```bash
# با Mermaid CLI
mmdc -i input.mmd -o output.png -w 3600 -H 2700 -s 2

# یا با Mermaid Live Editor
# Download as PNG (Maximum Quality)
```

### مرحله 2: Vectorization

**با Adobe Illustrator:**
1. Place PNG image
2. Object → Image Trace → Make
3. Settings: High Fidelity Photo
4. Expand: Object → Expand

**با Inkscape (رایگان):**
1. Import PNG
2. Path → Trace Bitmap
3. Settings: Multiple scans, Colors
4. Apply

**با Online Tools:**
- Vectorizer.io
- Autotracer
- Vector Magic

### مرحله 3: Enhancement

همانند روش 1

---

## 🔧 روش 3: ترسیم از صفر در Illustrator

### مزایا:
- کیفیت بالاترین
- کنترل کامل
- مناسب برای Patent Drawings

### مراحل:

**1. Setup Document:**
```
File → New
Width: 8.5 inches (21.6 cm)
Height: 11 inches (27.9 cm)
Units: Inches
Color Mode: CMYK
```

**2. ترسیم Components:**
- استفاده از Rectangle Tool برای boxes
- استفاده از Line Tool برای connections
- استفاده از Ellipse Tool برای circles

**3. اضافه کردن Text:**
- Type Tool برای labels
- Reference Numerals با Type Tool

**4. Styling:**
- Consistent colors
- Professional appearance
- Patent standards compliance

---

## 🛠️ ابزارهای مورد نیاز

### نرم‌افزارهای اصلی

1. **Adobe Illustrator** ($$$)
   - بهترین کیفیت
   - Professional standard
   - Export به TIFF/PDF

2. **Inkscape** (رایگان)
   - جایگزین مناسب Illustrator
   - Vector graphics
   - Export به SVG/PDF

3. **CorelDRAW** ($$)
   - جایگزین Illustrator
   - Professional quality

### ابزارهای کمکی

1. **Mermaid CLI**
   - برای export اولیه

2. **Vectorization Tools**
   - برای تبدیل raster به vector

3. **Image Editors**
   - GIMP (post-processing)
   - Photoshop (retouching)

---

## 📋 چک‌لیست نهایی

### قبل از Export

- [ ] تمام Reference Numerals اضافه شده
- [ ] خطوط با ضخامت مناسب
- [ ] Labels واضح و خوانا
- [ ] Layout حرفه‌ای
- [ ] رنگ‌ها مناسب (سیاه و سفید ترجیح دارد)

### Export

- [ ] رزولوشن: 300+ DPI (600 DPI بهتر)
- [ ] فرمت: TIFF یا PDF
- [ ] اندازه: 21.6 × 27.9 cm
- [ ] Margins رعایت شده
- [ ] حجم فایل: < 25 MB

### پس از Export

- [ ] بررسی کیفیت در 50% scale
- [ ] بررسی خوانایی اعداد
- [ ] بررسی Consistency با سایر نقشه‌ها
- [ ] بررسی با Patent Attorney (در صورت امکان)

---

## 🔗 منابع

- [USPTO Drawing Standards](https://www.uspto.gov/patents/apply/filing-online/patent-drawings)
- [Mermaid Documentation](https://mermaid.js.org/)
- [Adobe Illustrator Help](https://helpx.adobe.com/illustrator/)
- [Inkscape Tutorials](https://inkscape.org/learn/tutorials/)

---

**آخرین بروزرسانی**: دسامبر 2024  
**وضعیت**: Complete Guide  
**نسخه**: 1.0

