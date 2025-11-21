# مراحل اجرای Live Dashboard - NeuroPredict-AI

## ⚠️ مشکل فعلی

Docker Desktop engine هنوز کاملاً آماده نیست. این پیام نشان می‌دهد که Docker در حال راه‌اندازی است.

## ✅ راه‌حل گام‌به‌گام

### مرحله 1: Docker Desktop را کاملاً Start کنید

1. **Docker Desktop** را باز کنید (از Start Menu)
2. **منتظر بمانید** تا:
   - آیکون Docker در system tray (کنار ساعت) **سبز** شود
   - پیام "Docker Desktop is running" نمایش داده شود
   - معمولاً 1-2 دقیقه طول می‌کشد

### مرحله 2: بررسی وضعیت Docker

در PowerShell اجرا کنید:

```powershell
docker info
```

**اگر موفق بود** (بدون خطا)، به مرحله بعد بروید.

**اگر خطا داد**، Docker Desktop را Restart کنید و دوباره امتحان کنید.

### مرحله 3: پیدا کردن docker-compose.yml

بررسی کنید که `docker-compose.yml` کجا است:

```powershell
# بررسی در directory فعلی
Test-Path docker-compose.yml

# بررسی در NPA---Neuro-Predict-Ai
Test-Path NPA---Neuro-Predict-Ai\docker-compose.yml
```

### مرحله 4: اجرای Dashboard

**اگر `docker-compose.yml` در directory فعلی است:**

```powershell
docker-compose up -d
```

**اگر `docker-compose.yml` در `NPA---Neuro-Predict-Ai` است:**

```powershell
cd NPA---Neuro-Predict-Ai
docker-compose up -d
```

### مرحله 5: بررسی وضعیت Containers

```powershell
docker-compose ps
```

باید همه containers با status "Up" نمایش داده شوند.

### مرحله 6: مشاهده Logs (اختیاری)

```powershell
docker-compose logs -f
```

برای خروج از logs: `Ctrl+C`

## 🌐 دسترسی به Dashboard ها

بعد از موفقیت‌آمیز بودن start:

- **Admin Dashboard (Real-time)**: http://localhost:3001
- **Main Application**: http://localhost:3000  
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

## 🔍 Troubleshooting

### مشکل: "Docker Desktop is not running"

**راه‌حل:**
1. Docker Desktop را باز کنید
2. منتظر بمانید تا کاملاً load شود
3. دوباره `docker info` را اجرا کنید

### مشکل: "Port already in use"

**راه‌حل:**
```powershell
# پیدا کردن process که از port استفاده می‌کند
netstat -ano | findstr :3000

# Kill کردن process (PID را جایگزین کنید)
taskkill /PID <PID> /F
```

### مشکل: Container fails to start

**راه‌حل:**
```powershell
# مشاهده logs
docker-compose logs [service-name]

# Rebuild containers
docker-compose up -d --build
```

## 📝 دستورات مفید

```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart a service
docker-compose restart [service-name]

# Remove everything
docker-compose down -v
```

## ⏱️ زمان‌بندی

- Docker Desktop start: 1-2 دقیقه
- Containers build (اولین بار): 5-10 دقیقه
- Containers start: 30-60 ثانیه

## ✅ Checklist

قبل از اجرا:
- [ ] Docker Desktop نصب و در حال اجرا است
- [ ] `docker info` بدون خطا اجرا می‌شود
- [ ] `docker-compose.yml` پیدا شده است
- [ ] Ports 3000, 3001, 8000, 5432, 6379 آزاد هستند

بعد از اجرا:
- [ ] همه containers با status "Up" هستند
- [ ] Health check موفق است: http://localhost:8000/health
- [ ] Admin Dashboard در دسترس است: http://localhost:3001

---

**نکته مهم**: همیشه قبل از اجرای `docker-compose up -d`، مطمئن شوید که:
1. Docker Desktop کاملاً راه‌اندازی شده است
2. `docker info` بدون خطا اجرا می‌شود
3. آیکون Docker در system tray سبز است

