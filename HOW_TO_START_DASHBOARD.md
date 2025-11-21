# راهنمای سریع اجرای Dashboard

## ⚠️ مشکل: Docker Desktop در حال اجرا نیست

خطای شما نشان می‌دهد که Docker Desktop engine در حال اجرا نیست.

## ✅ راه‌حل

### مرحله 1: Docker Desktop را Start کنید

1. **Docker Desktop** را از Start Menu باز کنید
2. منتظر بمانید تا status به **"Running"** تغییر کند (معمولاً 30-60 ثانیه)
3. در system tray (کنار ساعت) آیکون Docker باید سبز باشد

### مرحله 2: بررسی کنید که Docker در حال اجرا است

در PowerShell اجرا کنید:

```powershell
docker info
```

اگر پیام خطا نداد، Docker آماده است.

### مرحله 3: Dashboard را Start کنید

از دایرکتوری فعلی (`NPA`) اجرا کنید:

```powershell
# اگر docker-compose.yml در همین directory است
docker-compose up -d

# یا اگر در NPA---Neuro-Predict-Ai است
cd NPA---Neuro-Predict-Ai
docker-compose up -d
```

## 📍 مسیر صحیح

بر اساس ساختار پروژه شما:

```
C:\Users\asus\Documents\companies\ithub\AI\products\clones\NPA\
├── docker-compose.yml          ← اینجا
├── NPA---Neuro-Predict-Ai\
│   └── docker-compose.yml      ← یا اینجا
```

**اگر `docker-compose.yml` در root directory (`NPA`) است:**

```powershell
# از همین directory
docker-compose up -d
```

**اگر `docker-compose.yml` در `NPA---Neuro-Predict-Ai` است:**

```powershell
cd NPA---Neuro-Predict-Ai
docker-compose up -d
```

## 🚀 دستورات سریع

```powershell
# 1. بررسی Docker
docker info

# 2. Start services
docker-compose up -d

# 3. بررسی وضعیت
docker-compose ps

# 4. مشاهده Logs
docker-compose logs -f

# 5. توقف
docker-compose down
```

## 🌐 بعد از Start

- **Admin Dashboard**: http://localhost:3001
- **Main App**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **Health**: http://localhost:8000/health

## ❓ اگر هنوز مشکل دارید

1. Docker Desktop را Restart کنید
2. منتظر بمانید تا کاملاً load شود
3. دوباره `docker info` را اجرا کنید
4. سپس `docker-compose up -d` را اجرا کنید

---

**نکته**: همیشه قبل از اجرای `docker-compose`، مطمئن شوید که Docker Desktop در حال اجرا است.

