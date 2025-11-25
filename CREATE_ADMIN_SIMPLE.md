# ساخت Admin User - راهنمای ساده فارسی

## 🎯 مشکل: با اطلاعات پیش‌فرض login نمی‌کند

این یعنی admin user هنوز ساخته نشده است. باید اول آن را بسازیم.

---

## ✅ راه‌حل 1: استفاده از Swagger UI (ساده‌ترین روش)

### مرحله 1: باز کردن Swagger
در browser، تب جدیدی باز کنید و به این آدرس بروید:
```
https://localhost:8000/docs
```

### مرحله 2: قبول کردن هشدار SSL
شما یک صفحه قرمز با پیغام امنیتی خواهید دید:
- روی **"Advanced"** یا **"پیشرفته"** کلیک کنید
- روی **"Proceed to localhost (unsafe)"** یا **"ادامه به localhost"** کلیک کنید

این عادی است چون backend از self-signed certificate استفاده می‌کند.

### مرحله 3: پیدا کردن Register Endpoint
در صفحه Swagger (که سبز رنگ است):
1. به پایین اسکرول کنید
2. بخش **"auth"** را پیدا کنید
3. روی **POST /api/v1/auth/register** کلیک کنید
4. باز می‌شود

### مرحله 4: امتحان کردن
1. روی دکمه **"Try it out"** کلیک کنید (سمت راست بالا)
2. یک فرم JSON نمایش داده می‌شود

### مرحله 5: وارد کردن اطلاعات
محتوای فرم را پاک کنید و **این JSON را کپی و paste کنید**:

```json
{
  "email": "admin@neuropredict.ai",
  "username": "admin",
  "password": "admin123",
  "first_name": "Admin",
  "last_name": "User",
  "role": "admin"
}
```

### مرحله 6: اجرا کردن
1. روی دکمه **"Execute"** کلیک کنید (پایین فرم)
2. صبر کنید تا پاسخ بیاید
3. اگر موفق بود، یک پاسخ سبز با اطلاعات user می‌بینید!

### مرحله 7: Login کردن
1. برگردید به صفحه login: `http://localhost:5173`
2. با این اطلاعات login کنید:
   - Email: `admin@neuropredict.ai`
   - Password: `admin123`
3. روی **"Sign in"** کلیک کنید
4. **موفق شدید!** 🎉

---

## ✅ راه‌حل 2: استفاده از Browser Console

اگر Swagger کار نکرد، از این روش استفاده کنید:

### مرحله 1: باز کردن Dashboard
به `http://localhost:5173` بروید

### مرحله 2: باز کردن Console
کلید **F12** را بزنید یا راست‌کلیک → **"Inspect"** → تب **"Console"**

### مرحله 3: اجرای کد
**این کد کامل را کپی کنید** و در console paste کنید، سپس **Enter** بزنید:

```javascript
// ساخت admin user
fetch('https://localhost:8000/api/v1/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'admin@neuropredict.ai',
    username: 'admin',
    password: 'admin123',
    first_name: 'Admin',
    last_name: 'User',
    role: 'admin'
  })
})
.then(response => {
  if (response.ok) {
    return response.json();
  } else {
    return response.json().then(err => {
      throw new Error(JSON.stringify(err, null, 2));
    });
  }
})
.then(data => {
  console.log('✅ کاربر با موفقیت ساخته شد!');
  console.log('📋 اطلاعات:', data);
  console.log('');
  console.log('🔐 حالا می‌توانید با این اطلاعات login کنید:');
  console.log('Email: admin@neuropredict.ai');
  console.log('Password: admin123');
  console.log('');
  alert('✅ کاربر admin ساخته شد!\n\nحالا می‌توانید login کنید:\nEmail: admin@neuropredict.ai\nPassword: admin123');
})
.catch(error => {
  console.error('❌ خطا در ساخت کاربر:', error.message);
  
  if (error.message.includes('already exists') || error.message.includes('duplicate')) {
    console.log('');
    console.log('💡 کاربر از قبل وجود دارد!');
    console.log('مستقیماً امتحان کنید login کنید.');
    alert('ℹ️ کاربر admin از قبل وجود دارد!\n\nمستقیماً login کنید.');
  } else {
    console.log('');
    console.log('🔍 راه‌حل‌های احتمالی:');
    console.log('1. مطمئن شوید backend روی port 8000 در حال اجرا است');
    console.log('2. از روش Swagger UI استفاده کنید (راحت‌تر است)');
  }
});
```

### مرحله 4: منتظر بمانید
بعد از چند ثانیه، یک پیام (alert) نمایش داده می‌شود که می‌گوید کاربر ساخته شد!

### مرحله 5: Login کنید
صفحه را refresh کنید و با اطلاعات پیش‌فرض login کنید.

---

## 🔍 اگر هنوز کار نکرد...

### بررسی 1: آیا Backend اجرا است؟

در PowerShell این دستور را اجرا کنید:
```powershell
netstat -ano | findstr ":8000"
```

باید خروجی شبیه این ببینید:
```
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       6412
```

اگر چیزی نمایش داده نشد، backend اجرا نیست! آن را اجرا کنید:
```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

### بررسی 2: دسترسی به Backend

در browser به این آدرس بروید:
```
https://localhost:8000/docs
```

اگر صفحه Swagger سبز رنگ را دیدید، یعنی backend کار می‌کند! ✅

اگر خطا دیدید یا صفحه باز نشد، backend مشکل دارد.

---

## 📝 اطلاعات پیش‌فرض (برای مراجعه آینده)

```
📧 Email:    admin@neuropredict.ai
👤 Username: admin
🔑 Password: admin123
👑 Role:     admin
```

---

## 🎉 بعد از ساخت موفق User

1. به صفحه login بروید: `http://localhost:5173`
2. اطلاعات بالا را وارد کنید
3. روی "Sign in" کلیک کنید
4. به dashboard اصلی وارد می‌شوید!

حالا می‌توانید از تمام قابلیت‌ها استفاده کنید:
- ✅ Disease Tracking
- ✅ 3D Analysis
- ✅ Data Monitoring
- ✅ Reports
- ✅ و همه چیز دیگر!

---

## 💡 نکته مهم

اگر در آینده دوباره این مشکل پیش آمد:
- Backend احتمالاً restart شده و database خالی شده
- همین مراحل را دوباره تکرار کنید تا admin user را بسازید

---

## ⚠️ برای Production

این اطلاعات فقط برای توسعه (development) است!

در محیط واقعی (production):
- ✅ Password قوی استفاده کنید
- ✅ Email واقعی استفاده کنید
- ✅ SECRET_KEY قوی در .env تنظیم کنید

---

**حالا یکی از دو روش بالا را امتحان کنید!** 🚀

توصیه می‌کنم **روش 1 (Swagger UI)** را امتحان کنید چون ساده‌تر و بصری‌تر است.

