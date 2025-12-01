# Quick Start: تبدیل سریع به Patent Drawings
# Quick Start Guide: Rapid Patent Drawing Conversion

## ⚡ شروع سریع در 5 مرحله

### مرحله 1: تولید SVG (2 دقیقه)

```powershell
.\scripts\generate_patent_diagrams.ps1
```

فایل‌های SVG در `docs/PATENT_DRAWINGS/exports/svg/` ایجاد می‌شوند.

---

### مرحله 2: باز کردن در Illustrator/Inkscape (1 دقیقه)

#### Illustrator:
```
File → New → 8.5" × 11"
File → Place → Select SVG
```

#### Inkscape:
```
File → Document Properties → 216mm × 279mm
File → Open → Select SVG
```

---

### مرحله 3: تنظیمات اولیه (5 دقیقه)

```
1. Select All (Ctrl+A)
2. Stroke Weight: 0.5 pt
3. Color: Black
4. Organize Layers
```

---

### مرحله 4: شماره‌گذاری (30-60 دقیقه)

```
1. Type Tool
2. Font: Arial Bold, 10 pt
3. اضافه کردن اعداد: 100, 110, 120, ...
4. Leader Lines از عدد به component
```

**Reference Numerals List**: از `FIGURES_SPECIFICATIONS.md` استفاده کنید.

---

### مرحله 5: Export (2 دقیقه)

#### Illustrator:
```
File → Export → Export As → TIFF
Resolution: 600 DPI
Color Mode: Grayscale
Compression: None
```

#### Inkscape:
```
File → Export PNG → 5100 × 6600 px (600 DPI)
سپس در GIMP: Convert to Grayscale → Save as TIFF
```

---

## 📋 چک‌لیست سریع

- [ ] اندازه: 8.5" × 11"
- [ ] Margins: رعایت شده
- [ ] Reference Numerals: اضافه شده
- [ ] خطوط: 0.5 pt
- [ ] Export: 600 DPI TIFF

---

## 🔗 راهنماهای کامل

- [Step-by-Step Tutorial](STEP_BY_STEP_TUTORIAL.md) - آموزش کامل
- [Complete Conversion Guide](COMPLETE_CONVERSION_GUIDE.md) - راهنمای جامع
- [Figures Specifications](FIGURES_SPECIFICATIONS.md) - Reference Numerals

---

**زمان کل**: ~1-2 ساعت per figure

