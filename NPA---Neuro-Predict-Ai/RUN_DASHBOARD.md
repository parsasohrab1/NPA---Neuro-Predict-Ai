# اجرای Live Dashboard - دستورات صحیح

## 📍 موقعیت فعلی

شما در حال حاضر در directory صحیح هستید:
```
C:\Users\asus\Documents\companies\ithub\AI\products\clones\NPA\NPA---Neuro-Predict-Ai
```

`docker-compose.yml` در همین directory است.

## ✅ دستورات صحیح

### 1. بررسی Docker Desktop

```powershell
docker info
```

اگر خطا نداد، Docker آماده است.

### 2. Start Dashboard

از همین directory (که الان هستید):

```powershell
docker-compose up -d
```

### 3. بررسی وضعیت

```powershell
docker-compose ps
```

### 4. مشاهده Logs

```powershell
docker-compose logs -f
```

## 🌐 دسترسی به Dashboard ها

بعد از موفقیت‌آمیز بودن:

- **Admin Dashboard**: http://localhost:3001
- **Main App**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **Health**: http://localhost:8000/health

## ⚠️ اگر خطای "cd" می‌گیرید

**نیازی به `cd` نیست!** شما از قبل در directory صحیح هستید.

فقط این دستور را اجرا کنید:

```powershell
docker-compose up -d
```

## 🔍 بررسی مسیر

اگر می‌خواهید مطمئن شوید:

```powershell
# نمایش مسیر فعلی
Get-Location

# بررسی وجود docker-compose.yml
Test-Path docker-compose.yml
```

اگر `True` نمایش داد، همه چیز درست است!

## 📝 دستورات کامل

```powershell
# 1. بررسی Docker
docker info

# 2. Start services (از همین directory)
docker-compose up -d

# 3. بررسی وضعیت
docker-compose ps

# 4. Logs
docker-compose logs -f

# 5. Stop
docker-compose down
```

---

**نکته**: نیازی به `cd` نیست. از همین directory که هستید، `docker-compose up -d` را اجرا کنید.

