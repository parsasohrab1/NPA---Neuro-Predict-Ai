# راهنمای کامل تبدیل به Patent Drawings رسمی
# Complete Guide: Converting to Patent-Quality Drawings

## 📋 فهرست مطالب

1. [مقدمه و الزامات](#مقدمه-و-الزامات)
2. [مراحل تبدیل - گام به گام](#مراحل-تبدیل---گام-به-گام)
3. [ابزارها و نرم‌افزارها](#ابزارها-و-نرمافزارها)
4. [راهنمای ترسیم در Illustrator](#راهنمای-ترسیم-در-illustrator)
5. [راهنمای ترسیم در Inkscape](#راهنمای-ترسیم-در-inkscape)
6. [شماره‌گذاری Reference Numerals](#شمارهگذاری-reference-numerals)
7. [چک‌لیست نهایی USPTO](#چکلیست-نهایی-uspto)
8. [مثال‌های عملی](#مثالهای-عملی)

---

## 🎯 مقدمه و الزامات

### چرا Patent Drawings مهم است؟

برای ثبت اختراع Utility Patent در حوزه AI و پزشکی، نقشه‌های فنی رسمی (Patent Drawings) یک **الزام قانونی** است. این نقشه‌ها باید:

- تمام اجزای ادعاهای اختراع را به وضوح نشان دهند
- کیفیت حرفه‌ای داشته باشند
- استانداردهای USPTO را رعایت کنند
- قابل خواندن در صورت کاهش 50% باشند

---

## 📐 استانداردهای USPTO

### الزامات اصلی:

| مورد | الزام |
|------|-------|
| **اندازه صفحه** | 21.6 cm × 27.9 cm (8.5" × 11") |
| **Margins** | Top: 2.5 cm (1"), Others: 1.3 cm (0.5") |
| **رزولوشن** | حداقل 300 DPI (ترجیح 600 DPI) |
| **فرمت** | TIFF (ترجیح) یا PDF |
| **رنگ** | سیاه و سفید (رنگی فقط در صورت ضرورت) |
| **Reference Numerals** | حداقل 1.32 mm (0.052 inches) |
| **خطوط** | 0.3-0.5 mm (ضخامت) |
| **فونت** | Arial, Times New Roman, یا Courier |

---

## 🔄 مراحل تبدیل - گام به گام

### مرحله 1: آماده‌سازی اولیه

#### 1.1 تولید Diagrams اولیه

```bash
# استفاده از اسکریپت ما
.\scripts\generate_patent_diagrams.ps1

# یا دستی با Mermaid CLI
mmdc -i Figure_1.mmd -o Figure_1.svg -w 2400 -H 1800
```

#### 1.2 انتخاب ابزار

- **Adobe Illustrator**: بهترین کیفیت ($$$)
- **Inkscape**: رایگان و قدرتمند (توصیه می‌شود)
- **CorelDRAW**: جایگزین مناسب ($$)

---

### مرحله 2: Import به نرم‌افزار

#### 2.1 Adobe Illustrator

1. **باز کردن Illustrator**
   - File → New Document
   - Width: **8.5 inches** (21.6 cm)
   - Height: **11 inches** (27.9 cm)
   - Units: Inches
   - Color Mode: **CMYK** (یا RGB برای Digital)

2. **Import SVG**
   - File → Open → Select SVG file
   - یا File → Place → Select SVG
   - Scale as needed

#### 2.2 Inkscape

1. **باز کردن Inkscape**
   - File → Document Properties
   - Custom Size: **216 mm × 279 mm**
   - Units: mm

2. **Import SVG**
   - File → Open → Select SVG file
   - یا File → Import → Select SVG

---

### مرحله 3: تبدیل به Vector (در صورت نیاز)

#### اگر فایل PNG است:

**Adobe Illustrator:**
1. Place PNG image
2. Select image
3. Object → Image Trace → Make
4. Settings: **High Fidelity Photo**
5. Object → Expand

**Inkscape:**
1. Import PNG
2. Path → Trace Bitmap
3. Settings: **Multiple scans**, **Colors**
4. Update preview
5. Apply

---

### مرحله 4: اصلاح و Enhancement

#### 4.1 اصلاح خطوط

**Adobe Illustrator:**
```
1. Select All (Ctrl+A)
2. Stroke Weight: 0.5 pt (برای خطوط اصلی)
3. Stroke Color: Black (#000000)
4. Remove fills (در صورت نیاز)
```

**Inkscape:**
```
1. Select All (Ctrl+A)
2. Stroke paint: Black
3. Stroke style: Width 0.5 mm
4. Fill: None (در صورت نیاز)
```

#### 4.2 حذف عناصر غیرضروری

- حذف لایه‌های background
- حذف عناصر تزئینی
- ساده‌سازی تا حد امکان

#### 4.3 تنظیم Layout

- قرار دادن عناصر در مرکز
- فاصله‌گذاری مناسب
- تراز کردن (Alignment)

---

### مرحله 5: شماره‌گذاری Reference Numerals

این مرحله **بسیار مهم** است!

#### 5.1 اضافه کردن اعداد

**Adobe Illustrator:**
```
1. Type Tool (T)
2. Font: Arial Bold
3. Size: 8-10 pt (حداقل 1.32 mm)
4. Color: Black (#000000)
5. Placement: خارج از شکل (با خطوط leader)
```

**Inkscape:**
```
1. Text Tool (T)
2. Font: Arial Bold
3. Font Size: 8-10 pt
4. Fill: Black
5. Placement: خارج از شکل
```

#### 5.2 سیستم شماره‌گذاری

| Range | استفاده |
|-------|---------|
| **100-199** | Client/Frontend Components |
| **200-299** | Backend Services |
| **300-399** | Data Layer |
| **400-499** | External Systems |
| **500-599** | Security Layer |
| **600-699** | Output/Results |
| **700-799** | Reports/Visualization |
| **800-899** | Review/Approval |
| **900-999** | Final/Storage |

#### 5.3 اضافه کردن Leader Lines

**Adobe Illustrator:**
```
1. Line Tool (/)
2. Stroke: 0.2 pt
3. Color: Black
4. Draw line از عدد به عنصر
```

**Inkscape:**
```
1. Bezier Tool (B)
2. Stroke: 0.2 mm
3. Draw line از عدد به عنصر
```

---

### مرحله 6: اضافه کردن Labels

#### 6.1 Labels برای Components

- استفاده از Type Tool
- Font: Arial Regular
- Size: 10-12 pt
- Placement: نزدیک به component

#### 6.2 Title Block

در پایین صفحه اضافه کنید:
- Figure Number (مثلاً "FIG. 1")
- Title (مثلاً "System Architecture")
- Page Number (در صورت چند صفحه‌ای)

---

### مرحله 7: تنظیم Margins

#### 7.1 Guide Lines

**Adobe Illustrator:**
```
View → Guides → Show Guides
View → Rulers → Show Rulers
Drag from rulers برای ایجاد guides:
- Top: 1 inch (2.5 cm)
- Bottom: 0.5 inches (1.3 cm)
- Left/Right: 0.5 inches (1.3 cm)
```

**Inkscape:**
```
View → Guides → Show Guides
Drag from rulers برای ایجاد guides با همان اندازه‌ها
```

#### 7.2 محدود کردن Drawing Area

- مطمئن شوید تمام عناصر داخل drawing area هستند
- Reference numerals می‌توانند کمی خارج باشند

---

### مرحله 8: Export نهایی

#### 8.1 Export به TIFF (ترجیح USPTO)

**Adobe Illustrator:**
```
File → Export → Export As
Format: TIFF
Resolution: 600 DPI
Color Mode: CMYK
Compression: None
Anti-aliasing: Art Optimized
```

**Inkscape:**
```
File → Export PNG Image
Export Area: Page
Width: 5100 px (8.5" × 600 DPI)
Height: 6600 px (11" × 600 DPI)
```

سپس در GIMP یا Photoshop:
1. Open PNG
2. Image → Mode → Grayscale (برای سیاه و سفید)
3. File → Export As → TIFF
4. Compression: None

#### 8.2 Export به PDF

**Adobe Illustrator:**
```
File → Save As → PDF
Preset: High Quality Print
Standard: PDF/X-1a:2001
Resolution: 600 DPI
```

**Inkscape:**
```
File → Save As → PDF
```

---

## 🎨 راهنمای ترسیم در Illustrator

### Setup Document

```
File → New
Artboards: 1
Width: 8.5 in
Height: 11 in
Units: Inches
Orientation: Portrait
Color Mode: CMYK
Raster Effects: 300 DPI
```

### تنظیمات مهم

#### Grid & Guides

```
View → Show Grid (برای تراز)
View → Snap to Grid (اختیاری)
Edit → Preferences → Guides & Grid:
- Gridline every: 0.5 in
- Subdivisions: 4
```

#### Layers Organization

```
Layer 1: Background (guides)
Layer 2: Main Drawing
Layer 3: Reference Numerals
Layer 4: Labels
Layer 5: Title Block
```

### Tips & Tricks

1. **Group کردن**: Related elements را group کنید
2. **Layers**: هر section را در layer جداگانه قرار دهید
3. **Symbols**: برای repeated elements استفاده کنید
4. **Align**: استفاده از Align panel برای تراز
5. **Pathfinder**: برای merge کردن shapes

---

## 🎨 راهنمای ترسیم در Inkscape

### Setup Document

```
File → Document Properties
Page Size: Custom
Width: 216 mm (8.5")
Height: 279 mm (11")
Units: mm
Orientation: Portrait
```

### تنظیمات مهم

#### Grid & Guides

```
View → Grid
Edit → Preferences → Grids:
- Spacing X: 12.7 mm (0.5")
- Spacing Y: 12.7 mm (0.5")
```

#### Layers

```
Layer → Layers (Ctrl+Shift+L)
اضافه کردن layers:
- Guides
- Main Drawing
- Reference Numerals
- Labels
- Title Block
```

### Tips & Tricks

1. **Snap**: استفاده از Snap to Grid
2. **Alignment**: استفاده از Align & Distribute panel
3. **Path Operations**: Union, Difference, Intersection
4. **Node Editing**: F2 برای ویرایش paths

---

## 🔢 شماره‌گذاری Reference Numerals

### قواعد USPTO

1. **اندازه**: حداقل 1.32 mm (0.052 inches)
2. **Style**: Bold
3. **رنگ**: مشکی (#000000)
4. **قرارگیری**: خارج از شکل (اگر امکان دارد)
5. **ترتیب**: از چپ به راست، بالا به پایین

### مثال شماره‌گذاری

```
Figure 1: System Architecture
- 100: Frontend Application
- 110: Admin Dashboard
- 200: API Gateway
- 210: Authentication Service
- 220: Data Processing Engine
- 230: AI Model Service
- 240: Data Fusion Service (PATENT-PENDING)
- 300: Database
- 310: Image Storage
```

### Leader Lines

- ضخامت: 0.2 pt
- رنگ: مشکی
- Style: Solid (نه dashed)
- طول: کوتاه (حدود 3-5 mm)

---

## ✅ چک‌لیست نهایی USPTO

### قبل از Export

- [ ] اندازه صفحه: 21.6 × 27.9 cm
- [ ] Margins رعایت شده (Top: 2.5 cm, Others: 1.3 cm)
- [ ] تمام Reference Numerals اضافه شده
- [ ] اندازه اعداد: حداقل 1.32 mm
- [ ] خطوط: 0.3-0.5 mm
- [ ] رنگ: سیاه و سفید (یا رنگی در صورت ضرورت)
- [ ] Labels واضح و خوانا
- [ ] Layout حرفه‌ای
- [ ] Title Block اضافه شده

### Export

- [ ] رزولوشن: 300+ DPI (600 DPI بهتر)
- [ ] فرمت: TIFF (ترجیح) یا PDF
- [ ] اندازه: 21.6 × 27.9 cm
- [ ] حجم فایل: < 25 MB
- [ ] کیفیت: بدون compression (یا lossless)

### بررسی نهایی

- [ ] کیفیت در 50% scale بررسی شده
- [ ] خوانایی اعداد تایید شده
- [ ] Consistency با سایر نقشه‌ها
- [ ] با Patent Attorney بررسی شده (در صورت امکان)

---

## 📝 مثال‌های عملی

### مثال 1: تبدیل Figure 1 (System Architecture)

#### مرحله 1: Export از Mermaid

```bash
mmdc -i docs/PATENT_DRAWINGS/Figure_1_System_Architecture.mmd \
     -o exports/Figure_1.svg \
     -w 2400 -H 1800 -s 2
```

#### مرحله 2: Import به Illustrator

1. New Document: 8.5" × 11"
2. File → Place → Figure_1.svg
3. Scale to fit drawing area

#### مرحله 3: Enhancement

1. Select All
2. Stroke Weight: 0.5 pt
3. Remove unnecessary elements
4. Organize layers

#### مرحله 4: Reference Numerals

```
100: Frontend (Arial Bold, 10 pt)
110: Admin Dashboard (Arial Bold, 10 pt)
200: API Gateway (Arial Bold, 10 pt)
...
```

#### مرحله 5: Export

1. File → Export → Export As → TIFF
2. Resolution: 600 DPI
3. Color Mode: Grayscale
4. Compression: None

---

### مثال 2: تبدیل Figure 2 (Neural Network)

این نقشه پیچیده‌تر است و نیاز به دقت بیشتری دارد:

1. **Layers مهم**: Input, Hidden, Output
2. **اتصالات**: باید واضح باشند
3. **Labels**: برای هر layer
4. **Reference Numerals**: برای هر component

---

## 🔗 منابع و لینک‌ها

### USPTO Resources

- [Patent Drawing Requirements](https://www.uspto.gov/patents/apply/filing-online/patent-drawings)
- [Drawing Standards (MPEP 608)](https://www.uspto.gov/web/offices/pac/mpep/s608.html)
- [Size and Margins](https://www.uspto.gov/web/offices/pac/mpep/s60802.html)

### Tools

- [Adobe Illustrator](https://www.adobe.com/products/illustrator.html)
- [Inkscape](https://inkscape.org/)
- [Mermaid Live Editor](https://mermaid.live)
- [Vectorizer.io](https://vectorizer.io/) (برای vectorization)

### Tutorials

- [Illustrator Basics](https://helpx.adobe.com/illustrator/tutorials.html)
- [Inkscape Tutorials](https://inkscape.org/learn/tutorials/)
- [Patent Drawing Tutorial](https://www.uspto.gov/patents/apply/filing-online/patent-drawings)

---

## ⚠️ نکات مهم

### DO's (انجام دهید)

✅ از Reference Numerals واضح و خوانا استفاده کنید  
✅ خطوط را با ضخامت مناسب ترسیم کنید  
✅ Layout را ساده و واضح نگه دارید  
✅ تمام عناصر را تراز کنید  
✅ Margins را رعایت کنید  

### DON'Ts (انجام ندهید)

❌ از رنگ‌های پیچیده استفاده نکنید (مگر ضروری)  
❌ Reference Numerals را خیلی کوچک نکنید  
❌ خطوط را خیلی نازک یا خیلی ضخیم نکنید  
❌ از فونت‌های decorative استفاده نکنید  
❌ Layout را شلوغ نکنید  

---

## 📊 Timeline تخمینی

| مرحله | زمان |
|-------|------|
| آماده‌سازی | 30 دقیقه |
| Import و تنظیم | 1 ساعت |
| Enhancement | 2-3 ساعت |
| شماره‌گذاری | 1-2 ساعت |
| Review و اصلاح | 1 ساعت |
| Export و بررسی | 30 دقیقه |
| **Total** | **6-8 ساعت per figure** |

---

**آخرین بروزرسانی**: دسامبر 2024  
**وضعیت**: Complete Guide Ready  
**نسخه**: 2.0

