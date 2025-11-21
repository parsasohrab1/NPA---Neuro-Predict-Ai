# راهنمای اجرای Live Dashboard - NeuroPredict-AI

## ⚠️ پیش‌نیاز: Docker Desktop

قبل از شروع، مطمئن شوید که **Docker Desktop** در حال اجرا است:

1. Docker Desktop را باز کنید
2. منتظر بمانید تا status به "Running" تغییر کند
3. سپس دستورات زیر را اجرا کنید

## 🚀 اجرای سریع

### روش 1: استفاده از Script (توصیه می‌شود)

#### Windows (PowerShell):
```powershell
cd NPA---Neuro-Predict-Ai
.\scripts\start_dashboard.ps1
```

#### Linux/Mac:
```bash
cd NPA---Neuro-Predict-Ai
chmod +x scripts/start_dashboard.sh
./scripts/start_dashboard.sh
```

### روش 2: دستی

```bash
# Navigate to project
cd NPA---Neuro-Predict-Ai

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🌐 دسترسی به Dashboard ها

بعد از اجرای سرویس‌ها، به آدرس‌های زیر دسترسی دارید:

### 1. Main Application (Frontend)
- **URL**: http://localhost:3000
- **Description**: Frontend application برای کاربران عادی

### 2. Admin Dashboard (Real-time) ⭐
- **URL**: http://localhost:3001
- **Description**: Admin dashboard با **real-time monitoring**
- **Features**:
  - ✅ AI/ML Health Monitoring (Model Drift, Performance, Confidence)
  - ✅ Clinical & Longitudinal Monitoring
  - ✅ System Health Monitoring (CPU, Memory, Disk, Network)
  - ✅ Security Monitoring (Audit Logs, Authentication)
  - ✅ Real-time WebSocket updates

### 3. API Documentation
- **URL**: http://localhost:8000/api/docs
- **Description**: Swagger UI برای API documentation

### 4. Health Check
- **URL**: http://localhost:8000/health
- **Description**: Health check endpoint

### 5. Metrics (Prometheus) - اگر production compose استفاده شود
- **URL**: http://localhost:9090
- **Description**: Prometheus metrics

## 📊 Admin Dashboard Features

### Real-time Monitoring Tabs:

1. **AI/ML Health**
   - Model Drift Score
   - Performance Metrics
   - Confidence Scores
   - Feature Importance

2. **Clinical Monitoring**
   - Longitudinal Tracking
   - Smart Alerting
   - Prediction Queue

3. **System Health**
   - Latency Metrics
   - Throughput
   - Service Health
   - Error Rates

4. **Security Monitoring**
   - Audit Log Stream
   - Authentication Monitoring
   - Admin Activity

## 🔍 بررسی وضعیت

### Check Container Status:
```bash
docker-compose ps
```

### View Logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f admin-dashboard
```

### Health Check:
```bash
# API Health
curl http://localhost:8000/health

# Or in browser
# http://localhost:8000/health
```

## 🛑 توقف سرویس‌ها

```bash
# Stop services (keep data)
docker-compose down

# Stop and remove volumes (delete data)
docker-compose down -v
```

## 🔧 Troubleshooting

### مشکل 1: Docker Desktop Not Running

**خطا:**
```
error during connect: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**راه‌حل:**
1. Docker Desktop را باز کنید
2. منتظر بمانید تا status "Running" شود
3. دوباره script را اجرا کنید

### مشکل 2: Port Already in Use

**خطا:**
```
Error: bind: address already in use
```

**راه‌حل:**
```powershell
# Windows - Find process using port
netstat -ano | findstr :3000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

### مشکل 3: Container Fails to Start

**راه‌حل:**
```bash
# Check logs
docker-compose logs [service-name]

# Rebuild containers
docker-compose up -d --build

# Remove and recreate
docker-compose down
docker-compose up -d
```

### مشکل 4: Database Connection Error

**راه‌حل:**
```bash
# Wait for database to be ready
docker-compose logs postgres

# Check database is healthy
docker-compose ps postgres
```

## 📝 Environment Variables

اگر نیاز به تغییر تنظیمات دارید، فایل `.env` ایجاد کنید:

```bash
# .env
SECRET_KEY=your-secret-key-here-min-32-chars
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/neuropredict_db
REDIS_HOST=redis
ENVIRONMENT=development
DEBUG=True
```

## 🎯 Quick Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Rebuild and start
docker-compose up -d --build

# Remove everything
docker-compose down -v
```

## 📚 مستندات بیشتر

- [Installation Guide](docs/INSTALLATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Real-time Dashboard](docs/REALTIME_DASHBOARD_IMPLEMENTATION.md)

## ✅ Checklist

قبل از اجرا:
- [ ] Docker Desktop نصب و در حال اجرا است
- [ ] Ports 3000, 3001, 8000, 5432, 6379 آزاد هستند
- [ ] فایل `docker-compose.yml` موجود است
- [ ] Environment variables تنظیم شده‌اند (اختیاری)

بعد از اجرا:
- [ ] همه containers در حال اجرا هستند (`docker-compose ps`)
- [ ] Health check موفق است (`http://localhost:8000/health`)
- [ ] Frontend در دسترس است (`http://localhost:3000`)
- [ ] Admin Dashboard در دسترس است (`http://localhost:3001`)

---

**نکته**: اگر Docker Desktop در حال اجرا نیست، ابتدا آن را start کنید و سپس دوباره script را اجرا کنید.

