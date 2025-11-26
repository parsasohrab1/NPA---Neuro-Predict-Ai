# 🔍 Troubleshooting Guide: خطای 404 در Data Fusion Reports

## وضعیت فعلی
شما در حال تلاش برای دسترسی به `/data-fusion` هستید و خطای 404 می‌بینید.

---

## ✅ چک‌لیست تشخیص مشکل

لطفاً این موارد را **به ترتیب** چک کنید:

### 1️⃣ آیا Frontend اصلاً اجرا است؟

**تست:**
- به `http://localhost:5173` بروید
- آیا صفحه login باز می‌شود؟

**نتیجه:**
- ✅ **بله، login باز می‌شود** → Frontend در حال اجرا است، به مرحله 2 بروید
- ❌ **نه، صفحه باز نمی‌شود** → Frontend اجرا نیست:
  ```powershell
  cd frontend
  npm run dev
  ```

---

### 2️⃣ آیا می‌توانید login کنید؟

**تست:**
- وارد داشبورد شوید (Login)
- به صفحه اصلی Dashboard بروید

**نتیجه:**
- ✅ **بله، وارد شدم** → مشکل فقط در route `/data-fusion` است، به مرحله 3 بروید
- ❌ **نه، نمی‌توانم login کنم** → مشکل از Backend است:
  ```powershell
  powershell -ExecutionPolicy Bypass -File start_backend.ps1
  ```

---

### 3️⃣ آیا منوی "Data Fusion Reports" را می‌بینید؟

**تست:**
- در Sidebar سمت چپ نگاه کنید
- آیا گزینه "✨ Data Fusion Reports" با gradient بنفش وجود دارد؟

**نتیجه:**
- ✅ **بله، می‌بینم** → کد جدید compile شده، به مرحله 4 بروید
- ❌ **نه، نمی‌بینم** → Frontend با کد قدیمی است:
  ```powershell
  # Frontend را RESTART کنید:
  powershell -ExecutionPolicy Bypass -File restart_frontend.ps1
  ```

---

### 4️⃣ آیا روی منو کلیک کرده‌اید؟

**تست:**
- روی "✨ Data Fusion Reports" در sidebar کلیک کنید
- یا مستقیماً به `http://localhost:5173/data-fusion` بروید

**نتیجه:**
- ✅ **صفحه باز شد** → مشکل حل شد! 🎉
- ❌ **هنوز 404** → به مرحله 5 بروید

---

### 5️⃣ Developer Console چه می‌گوید؟

**تست:**
1. در مرورگر `F12` بزنید
2. به tab **Console** بروید
3. خطاهای قرمز را ببینید

**خطاهای محتمل:**

#### خطا: `Failed to fetch dynamically imported module`
**معنی:** Frontend با کد قدیمی cache شده

**راه حل:**
```
1. Ctrl+Shift+R (Hard Refresh)
2. یا Clear Browser Cache
3. یا Incognito Mode
```

#### خطا: `404 - Module not found: DataFusionReports`
**معنی:** فایل در build موجود نیست

**راه حل:**
```powershell
# Frontend را کاملاً rebuild کنید:
cd frontend
npm run build
npm run dev
```

#### خطا: `Unexpected token '<'` یا `SyntaxError`
**معنی:** Server HTML به جای JS برمی‌گرداند (مشکل routing)

**راه حل:**
- این مشکل Vite config است
- فایل `frontend/vite.config.ts` را چک کنید

---

### 6️⃣ Network Tab چه می‌گوید؟

**تست:**
1. در Developer Tools به tab **Network** بروید
2. صفحه را refresh کنید
3. آیا request به `/data-fusion` ارسال می‌شود؟

**نتایج محتمل:**

#### Status: `200 OK` اما محتوا خالی
**راه حل:** Cache مرورگر را پاک کنید

#### Status: `404 Not Found`
**راه حل:** Frontend routing مشکل دارد - rebuild کنید

#### Status: `ERR_CONNECTION_REFUSED`
**راه حل:** Frontend اصلاً اجرا نیست

---

## 🚀 راه حل قطعی (اگر هیچکدام کار نکرد)

این دستورات را **دقیقاً به ترتیب** اجرا کنید:

### مرحله 1: تمیز کردن محیط
```powershell
# Kill همه Node processes
Get-Process | Where-Object {$_.ProcessName -like '*node*'} | Stop-Process -Force

# پاک کردن cache
cd frontend
Remove-Item -Recurse -Force node_modules/.vite -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
```

### مرحله 2: دریافت آخرین کد
```powershell
cd ..
git pull origin main
git status  # چک کنید که clean است
```

### مرحله 3: Rebuild و اجرا
```powershell
cd frontend
npm install  # اختیاری اما توصیه می‌شود
npm run dev
```

### مرحله 4: صبر کنید
- منتظر بمانید تا پیام `ready in XXXms` ببینید
- معمولاً 30-60 ثانیه طول می‌کشد

### مرحله 5: تست
1. به `http://localhost:5173` بروید
2. Login کنید
3. در Sidebar دنبال "✨ Data Fusion Reports" بگردید
4. روی آن کلیک کنید
5. یا مستقیماً به `http://localhost:5173/data-fusion` بروید

---

## 📝 اگر هنوز کار نکرد

لطفاً این اطلاعات را برای من بفرستید:

### 1. خروجی Terminal
```powershell
cd frontend
npm run dev
# خروجی terminal را کپی کنید
```

### 2. Browser Console Errors
- `F12` → Console tab
- تمام خطاهای قرمز را کپی کنید

### 3. Network Requests
- `F12` → Network tab
- Request به `/data-fusion` را چک کنید
- Status code چیست؟

### 4. Git Status
```powershell
git status
git log --oneline -n 5
```

---

## 🎯 نکات مهم

1. ⚠️ **حتماً صبر کنید** تا Frontend compile شود (`ready` message)
2. ⚠️ **حتماً Cache را Clear کنید** (`Ctrl+Shift+R`)
3. ⚠️ **حتماً Backend روی port 8001 در حال اجرا باشد**
4. ⚠️ **حتماً به `/data-fusion` بروید نه `/data-fusion-reports`**

---

## ✅ موفقیت

وقتی صفحه باز شد، باید این‌ها را ببینید:

```
✨ Data Fusion Reports
PATENT-PENDING: Multi-Modal Medical Data Integration

[Purple gradient box with patent notice]

Generate or View Fusion Reports
[Input: Enter Patient ID] [Button: Generate Fusion Report]
```

اگر این‌ها را دیدید، تبریک! صفحه به درستی کار می‌کند! 🎉

---

## 🆘 کمک بیشتر

اگر هیچکدام از راه‌حل‌ها کار نکرد:

1. Screenshot از خطا بگیرید
2. خروجی Terminal را کپی کنید
3. Browser Console errors را کپی کنید
4. این اطلاعات را برای من بفرستید

من کمک خواهم کرد! 🤝

