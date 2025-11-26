# ⚠️ Backend Restart Required - Manual Instructions

## مشکل فعلی | Current Problem

شما همچنان خطای **"0 patients, 0 records, 0 predictions created. WARNING: 2 errors occurred"** را می‌بینید.

**علت:** Backend هنوز کد قدیمی را اجرا می‌کند که به دنبال CSV files است.

**راه حل:** Backend باید با کد جدید restart شود.

---

## ✅ مراحل حل مشکل | Solution Steps

### مرحله 1: Kill کردن Backend قدیمی

یک terminal **PowerShell** باز کنید و این دستور را اجرا کنید:

```powershell
Get-Process | Where-Object {$_.ProcessName -like '*python*'} | Stop-Process -Force
```

این کار تمام Python processes را متوقف می‌کند.

---

### مرحله 2: Start کردن Backend جدید

**در همان terminal**، این دستورات را اجرا کنید:

```powershell
cd C:\Users\asus\Documents\companies\ithub\AI\products\clones\NPA
powershell -ExecutionPolicy Bypass -File start_backend.ps1
```

**صبر کنید** تا این پیام را ببینید:

```
✓ Environment variables configured
...
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

✅ **Backend آماده است!**

---

### مرحله 3: ساخت Medical Records & Predictions

**یک terminal دیگر** باز کنید و این دستورات را اجرا کنید:

```powershell
cd C:\Users\asus\Documents\companies\ithub\AI\products\clones\NPA
python create_medical_records_100k.py
```

این کار:
- **20-30 دقیقه** طول می‌کشد (برای 100,500 بیمار)
- Medical records و predictions برای تمام بیماران می‌سازد
- Progress نشان می‌دهد

---

### مرحله 4: تست Disease Tracking Dashboard

1. Browser را باز کنید
2. به این آدرس بروید:
   ```
   http://localhost:5173/disease-tracking
   ```
3. دکمه **"Load All Data"** را بزنید
4. باید **100,500 بیمار** با تمام medical records و predictions ببینید!

---

## 🔍 چک کردن Backend

برای اینکه مطمئن شوید backend در حال اجرا است:

```powershell
# روش 1: Check با curl
Invoke-WebRequest -Uri "http://localhost:8001/api/v1/disease-tracking/health"

# روش 2: Check با Python
python -c "import requests; r = requests.get('http://localhost:8001/api/v1/disease-tracking/health'); print('Backend OK' if r.status_code == 200 else 'Backend Error')"
```

اگر **200 OK** دیدید، backend آماده است!

---

## 🐛 Troubleshooting

### اگر Backend start نمی‌شود:

```powershell
# Kill تمام Python processes
Get-Process | Where-Object {$_.ProcessName -like '*python*'} | Stop-Process -Force

# Check کنید که process باقی نمانده
Get-Process | Where-Object {$_.ProcessName -like '*python*'}

# Restart کنید
cd C:\Users\asus\Documents\companies\ithub\AI\products\clones\NPA
.\start_backend.ps1
```

### اگر Port 8001 استفاده می‌شود:

```powershell
# پیدا کردن process که port 8001 را استفاده می‌کند
netstat -ano | findstr :8001

# Kill کردن آن process (PID را از output بالا بگیرید)
Stop-Process -Id <PID> -Force
```

### اگر همچنان خطا می‌دهد:

1. بررسی کنید که `backend/app/api/disease_tracking.py` کد جدید دارد:
   ```powershell
   Select-String -Path "backend/app/api/disease_tracking.py" -Pattern "Fetch ALL patients from database"
   ```
   
   اگر چیزی پیدا نشد، به من بگویید تا فایل را دوباره اصلاح کنم.

2. Git pull کنید (اگر تغییرات commit نشده):
   ```powershell
   git pull origin main
   ```

---

## 📊 انتظارات

بعد از اجرای موفق `create_medical_records_100k.py`، باید این نتیجه را ببینید:

```
✅ SUCCESS!

📊 Results:
   Message: Loaded 100500 patients successfully!
   Patients processed: 100,500
   Records created: 100,500
   Predictions created: 100,500
   Skipped: 0
   Errors: 0

   ⏱️  Duration: ~1200-1800 seconds (20-30 minutes)
```

---

## 🎯 Quick Reference

| دستور | توضیح |
|------|-------|
| `Get-Process \| Where-Object {$_.ProcessName -like '*python*'} \| Stop-Process -Force` | Kill all Python |
| `.\start_backend.ps1` | Start Backend |
| `python create_medical_records_100k.py` | Create Medical Records |
| `Invoke-WebRequest -Uri "http://localhost:8001/api/v1/disease-tracking/health"` | Check Backend |

---

## ❓ سوالات متداول

**Q: چرا باید backend restart شود؟**  
A: Python فایل‌ها را فقط یک بار (هنگام start) load می‌کند. برای اینکه تغییرات کد دیده شوند، باید restart شود.

**Q: چرا 20-30 دقیقه طول می‌کشد؟**  
A: برای 100,500 بیمار، باید:
- Medical record بسازیم (cognitive scores, biomarkers, MRI data)
- Risk scores محاسبه کنیم (Alzheimer's & Parkinson's)
- Predictions بسازیم
- همه را در database ذخیره کنیم

**Q: می‌توانم progress را ببینم?**  
A: بله! در terminal backend، log messages نشان داده می‌شوند. هر 500 بیمار، یک batch commit می‌شود.

---

## 🎉 بعد از اتمام

بعد از اینکه همه مراحل کامل شد:
- ✅ 100,500 بیمار در database
- ✅ 100,500 medical records
- ✅ 100,500 predictions  
- ✅ Disease Tracking Dashboard کاملاً کار می‌کند
- ✅ Data Fusion Reports برای هر بیمار قابل تولید است

**آماده برای استفاده در production!** 🚀

---

**تاریخ ایجاد:** Wednesday Nov 26, 2025  
**برای کمک بیشتر:** این فایل را به من نشان دهید و بگویید کجا گیر کردید.

