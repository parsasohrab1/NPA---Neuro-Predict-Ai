# 📦 فایل جامع راه‌اندازی داشبورد NeuroPredict-AI

## 🎯 فایل‌های جامع ایجاد شده

دو فایل جامع ایجاد شده که تمام قابلیت‌های لازم را دارند:

### 1. `راه‌اندازی_داشبورد_جامع.bat` (پیشنهادی برای Windows)

**ویژگی‌ها:**
- ✅ بررسی خودکار مسیر پروژه
- ✅ بررسی پیش‌نیازها (Python, Node.js, npm)
- ✅ بررسی پورت‌ها
- ✅ بررسی dependencies
- ✅ راه‌اندازی Backend و Frontend
- ✅ باز کردن خودکار مرورگر
- ✅ پیام‌های واضح و فارسی
- ✅ مدیریت خطا

**نحوه استفاده:**
```
دوبار کلیک روی: راه‌اندازی_داشبورد_جامع.bat
```

### 2. `راه‌اندازی_داشبورد_جامع.ps1` (نسخه PowerShell)

**ویژگی‌ها:**
- ✅ تمام قابلیت‌های نسخه Batch
- ✅ بررسی دقیق‌تر dependencies
- ✅ نصب خودکار dependencies (اختیاری)
- ✅ مدیریت بهتر processها
- ✅ گزینه‌های بیشتر

**نحوه استفاده:**
```powershell
.\راه‌اندازی_داشبورد_جامع.ps1
```

**گزینه‌ها:**
```powershell
# بدون بررسی‌ها
.\راه‌اندازی_داشبورد_جامع.ps1 -SkipChecks

# بدون باز کردن مرورگر
.\راه‌اندازی_داشبورد_جامع.ps1 -NoBrowser

# تغییر پورت‌ها
.\راه‌اندازی_داشبورد_جامع.ps1 -BackendPort 8001 -FrontendPort 5174

# فقط Backend یا فقط Frontend
.\راه‌اندازی_داشبورد_جامع.ps1 -SkipFrontend
.\راه‌اندازی_داشبورد_جامع.ps1 -SkipBackend
```

---

## 📋 قابلیت‌های فایل جامع

### بررسی‌های خودکار:
1. ✅ بررسی وجود Python
2. ✅ بررسی وجود Node.js و npm
3. ✅ بررسی وجود پوشه‌های backend و admin-dashboard
4. ✅ بررسی پورت‌های 8000 و 5173
5. ✅ بررسی dependencies (Python packages و node_modules)
6. ✅ جستجوی خودکار مسیر (اگر در دایرکتوری صحیح نباشید)

### راه‌اندازی:
1. ✅ راه‌اندازی Backend (FastAPI)
2. ✅ راه‌اندازی Frontend (Vite)
3. ✅ باز کردن خودکار مرورگر
4. ✅ نمایش لینک‌های دسترسی

### مدیریت خطا:
1. ✅ پیام‌های واضح برای هر خطا
2. ✅ راهنمایی برای حل مشکلات
3. ✅ بررسی وضعیت سرویس‌ها

---

## 🚀 استفاده سریع

### روش 1: دوبار کلیک (ساده‌ترین)
```
دوبار کلیک روی: راه‌اندازی_داشبورد_جامع.bat
```

### روش 2: از Command Prompt
```cmd
cd /d "C:\Users\asus\Documents\companies\ithub\AI\products\clones\NPA"
راه‌اندازی_داشبورد_جامع.bat
```

### روش 3: از PowerShell
```powershell
cd "C:\Users\asus\Documents\companies\ithub\AI\products\clones\NPA"
.\راه‌اندازی_داشبورد_جامع.ps1
```

---

## 🌐 دسترسی به داشبورد

بعد از راه‌اندازی موفق:

- **Admin Dashboard:** http://localhost:5173
- **Disease Tracking:** http://localhost:5173/disease-tracking
- **System Overview:** http://localhost:5173/
- **API Documentation:** http://localhost:8000/api/docs
- **Health Check:** http://localhost:8000/health

---

## 🛑 توقف سرویس‌ها

### روش 1: بستن پنجره‌ها
- پنجره‌های Command Prompt/PowerShell را ببندید

### روش 2: از Task Manager
- Task Manager را باز کنید (Ctrl+Shift+Esc)
- Processهای python و node را پیدا کنید
- End Task کنید

### روش 3: از Command Prompt
```cmd
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

---

## ⚠️ عیب‌یابی

### مشکل: "Python یافت نشد"
**راه‌حل:**
1. Python را از python.org دانلود و نصب کنید
2. در زمان نصب، "Add Python to PATH" را انتخاب کنید
3. Terminal را ببندید و دوباره باز کنید

### مشکل: "Node.js یافت نشد"
**راه‌حل:**
1. Node.js را از nodejs.org دانلود و نصب کنید
2. Terminal را ببندید و دوباره باز کنید

### مشکل: "پورت در حال استفاده است"
**راه‌حل:**
1. سرویس‌های قبلی را متوقف کنید
2. یا از PowerShell با گزینه تغییر پورت استفاده کنید:
   ```powershell
   .\راه‌اندازی_داشبورد_جامع.ps1 -BackendPort 8001 -FrontendPort 5174
   ```

### مشکل: "node_modules یافت نشد"
**راه‌حل:**
```cmd
cd admin-dashboard
npm install
```

### مشکل: "Python packages نصب نشده‌اند"
**راه‌حل:**
```cmd
cd backend
pip install -r requirements.txt
```

---

## 📝 نکات مهم

1. **اولین اجرا:** ممکن است چند دقیقه طول بکشد (نصب dependencies)
2. **پورت‌ها:** مطمئن شوید پورت‌های 8000 و 5173 آزاد هستند
3. **Firewall:** ممکن است Windows Firewall اجازه دسترسی بدهد
4. **Dependencies:** تمام dependencies باید قبلاً نصب شده باشند (برای offline mode)

---

## ✅ Checklist قبل از اجرا

- [ ] Python نصب شده است (`python --version`)
- [ ] Node.js نصب شده است (`node --version`)
- [ ] npm نصب شده است (`npm --version`)
- [ ] پورت‌های 8000 و 5173 آزاد هستند
- [ ] Dependencies نصب شده‌اند
- [ ] در دایرکتوری صحیح هستید (شامل backend و admin-dashboard)

---

**تاریخ آخرین به‌روزرسانی:** 2024-01-01

