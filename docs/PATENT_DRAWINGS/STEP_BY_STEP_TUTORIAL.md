# آموزش گام به گام: ترسیم Patent Drawing
# Step-by-Step Tutorial: Creating Patent Drawings

## 🎯 هدف این آموزش

این آموزش شما را گام به گام برای تبدیل دیاگرام Mermaid به Patent Drawing رسمی راهنمایی می‌کند.

---

## 📋 پیش‌نیازها

- ✅ دیاگرام‌های Mermaid تولید شده
- ✅ Adobe Illustrator یا Inkscape نصب شده
- ✅ Reference Numerals list آماده

---

## 🚀 شروع - گام 1: آماده‌سازی

### 1.1 تولید SVG از Mermaid

```powershell
# اجرای اسکریپت
.\scripts\generate_patent_diagrams.ps1

# یا دستی
cd docs\PATENT_DRAWINGS
mmdc -i Figure_1_System_Architecture.mmd -o exports\svg\Figure_1.svg -w 2400 -H 1800
```

### 1.2 بررسی فایل تولید شده

- فایل SVG در `docs/PATENT_DRAWINGS/exports/svg/` قرار دارد
- فایل را در مرورگر باز کنید و بررسی کنید

---

## 🎨 گام 2: Setup در Illustrator

### 2.1 ایجاد Document جدید

```
File → New
Width: 8.5 inches
Height: 11 inches
Units: Inches
Color Mode: CMYK
Orientation: Portrait
```

### 2.2 تنظیم Guides برای Margins

```
View → Rulers → Show Rulers

ایجاد Guides:
- Top: 1 inch (از بالای صفحه)
- Bottom: 0.5 inches (از پایین صفحه)
- Left: 0.5 inches (از چپ صفحه)
- Right: 0.5 inches (از راست صفحه)
```

برای ایجاد Guide:
1. از Ruler کلیک و drag کنید
2. یا Object → Guides → Make

### 2.3 ایجاد Layers

```
Window → Layers

ایجاد Layers به ترتیب:
1. Guides (lock این layer)
2. Background
3. Main Drawing
4. Reference Numerals
5. Labels
6. Title Block
```

---

## 📥 گام 3: Import SVG

### 3.1 Import فایل

```
File → Place
انتخاب: Figure_1.svg
Place در صفحه
```

### 3.2 Scale کردن

```
1. Select imported graphic
2. Object → Transform → Scale
3. Scale uniformly: 80-90%
4. مطمئن شوید داخل drawing area است
```

### 3.3 Move به Layer مناسب

```
1. Select graphic
2. Drag به layer "Main Drawing"
```

---

## ✏️ گام 4: Enhancement و اصلاح

### 4.1 اصلاح خطوط

```
1. Select All (Ctrl+A)
2. Window → Stroke
3. Weight: 0.5 pt
4. Color: Black (C:0, M:0, Y:0, K:100)
```

### 4.2 حذف عناصر غیرضروری

- حذف background colors
- حذف gradients
- ساده‌سازی shapes

### 4.3 Organize Components

- Group related elements
- Align elements
- Consistent spacing

---

## 🔢 گام 5: شماره‌گذاری Reference Numerals

### 5.1 اضافه کردن اولین عدد

```
1. Switch به layer "Reference Numerals"
2. Type Tool (T)
3. Font: Arial Bold
4. Size: 10 pt
5. Color: Black
6. Type: "100"
7. Place خارج از component
```

### 5.2 اضافه کردن Leader Line

```
1. Line Tool (/)
2. Stroke: 0.2 pt
3. Draw line از عدد به component
4. Color: Black
```

### 5.3 ادامه شماره‌گذاری

برای تمام components:
- 110, 120, 130, ...
- 200, 210, 220, ...
- به ترتیب از چپ به راست، بالا به پایین

### 5.4 لیست Reference Numerals

از `FIGURES_SPECIFICATIONS.md` استفاده کنید:

```
100: Frontend Web Application
110: Admin Dashboard
200: API Gateway
210: Authentication Service
220: Data Processing Engine
230: AI Model Service
240: Data Fusion Service (PATENT-PENDING)
300: PostgreSQL Database
...
```

---

## 🏷️ گام 6: اضافه کردن Labels

### 6.1 Labels برای Components

```
1. Switch به layer "Labels"
2. Type Tool (T)
3. Font: Arial Regular
4. Size: 9 pt
5. Type نام component
6. Place نزدیک به component
```

### 6.2 Title Block

در پایین صفحه:

```
1. Type Tool (T)
2. Font: Arial Bold
3. Size: 14 pt
4. Type: "FIG. 1"
5. زیر آن: "System Architecture"
```

---

## 🎯 گام 7: Final Touches

### 7.1 بررسی Layout

- [ ] تمام elements داخل drawing area
- [ ] فاصله‌ها consistent
- [ ] تراز (alignment) درست

### 7.2 بررسی Readability

- [ ] اعداد قابل خواندن
- [ ] Labels واضح
- [ ] خطوط واضح

### 7.3 بررسی Standards

- [ ] Margins رعایت شده
- [ ] Reference Numerals ≥ 1.32 mm
- [ ] خطوط 0.3-0.5 mm

---

## 💾 گام 8: Export نهایی

### 8.1 Export به TIFF

```
File → Export → Export As
Format: TIFF
Filename: Figure_1_System_Architecture.tiff
Location: docs/PATENT_DRAWINGS/exports/tiff/

Settings:
- Resolution: 600 PPI
- Color Mode: Grayscale
- Compression: None
- Anti-aliasing: Art Optimized
```

### 8.2 Export به PDF

```
File → Save As
Format: PDF
Filename: Figure_1_System_Architecture.pdf

Settings:
- Preset: High Quality Print
- Standard: PDF/X-1a:2001
- Resolution: 600 DPI
```

---

## ✅ گام 9: بررسی نهایی

### 9.1 بررسی کیفیت

1. فایل TIFF را باز کنید
2. Zoom to 50%
3. بررسی کنید که:
   - اعداد قابل خواندن هستند
   - خطوط واضح هستند
   - کیفیت خوب است

### 9.2 چک‌لیست

```
[ ] اندازه: 21.6 × 27.9 cm
[ ] Margins: رعایت شده
[ ] Resolution: 600 DPI
[ ] Format: TIFF
[ ] Color: Grayscale
[ ] Reference Numerals: تمام اضافه شده
[ ] Labels: واضح و خوانا
[ ] Quality: قابل خواندن در 50%
```

---

## 🔄 تکرار برای سایر Figures

برای هر Figure:

1. ✅ تولید SVG
2. ✅ Import به Illustrator
3. ✅ Enhancement
4. ✅ شماره‌گذاری
5. ✅ Export

**تخمین زمان**: 6-8 ساعت per figure

---

## 🆘 رفع مشکلات رایج

### مشکل: اعداد خیلی کوچک

**راه حل**: 
- Size را به 12 pt افزایش دهید
- مطمئن شوید حداقل 1.32 mm است

### مشکل: خطوط خیلی نازک

**راه حل**:
- Stroke weight را به 0.5 pt افزایش دهید
- از 0.3 mm کمتر نباشد

### مشکل: Layout شلوغ

**راه حل**:
- فاصله‌ها را افزایش دهید
- عناصر را group کنید
- از چند صفحه استفاده کنید (اگر لازم است)

### مشکل: کیفیت پایین در Export

**راه حل**:
- Resolution را به 600 DPI افزایش دهید
- Compression را None کنید
- از Vector format استفاده کنید

---

## 📚 منابع بیشتر

- [Complete Conversion Guide](COMPLETE_CONVERSION_GUIDE.md)
- [Figures Specifications](FIGURES_SPECIFICATIONS.md)
- [USPTO Drawing Standards](https://www.uspto.gov/web/offices/pac/mpep/s608.html)

---

**آخرین بروزرسانی**: دسامبر 2024  
**وضعیت**: Step-by-Step Tutorial  
**نسخه**: 1.0

