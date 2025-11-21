# راهنمای سریع اجرای Live Dashboard - NeuroPredict-AI

## پیش‌نیازها

1. ✅ Docker Desktop نصب و در حال اجرا باشد
2. ✅ Docker Compose در دسترس باشد
3. ✅ Ports 3000, 3001, 8000, 5432, 6379 آزاد باشند

## اجرای سریع

### Windows (PowerShell)

```powershell
# Navigate to project
cd NPA---Neuro-Predict-Ai

# Start services
.\scripts\start_dashboard.ps1

# Or manually
docker-compose up -d
```

### Linux/Mac

```bash
# Navigate to project
cd NPA---Neuro-Predict-Ai

# Make script executable
chmod +x scripts/start_dashboard.sh

# Start services
./scripts/start_dashboard.sh

# Or manually
docker-compose up -d
```

## دسترسی به Dashboard ها

### Main Application
- **URL**: http://localhost:3000
- **Description**: Frontend application برای کاربران

### Admin Dashboard (Real-time)
- **URL**: http://localhost:3001
- **Description**: Admin dashboard با real-time monitoring
- **Features**:
  - AI/ML Health Monitoring
  - Clinical & Longitudinal Monitoring
  - System Health Monitoring
  - Security Monitoring
  - Real-time WebSocket updates

### API Documentation
- **URL**: http://localhost:8000/api/docs
- **Description**: Swagger UI برای API documentation

### Health Check
- **URL**: http://localhost:8000/health
- **Description**: Health check endpoint

### Metrics (Prometheus)
- **URL**: http://localhost:9090
- **Description**: Prometheus metrics (اگر production compose استفاده شود)

## بررسی وضعیت سرویس‌ها

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f admin-dashboard
```

## توقف سرویس‌ها

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Troubleshooting

### مشکل: Docker is not running

**راه‌حل:**
1. Docker Desktop را start کنید
2. منتظر بمانید تا Docker کاملاً راه‌اندازی شود
3. دوباره script را اجرا کنید

### مشکل: Port already in use

**راه‌حل:**
1. بررسی کنید که چه process از port استفاده می‌کند:
   ```bash
   # Windows
   netstat -ano | findstr :3000
   
   # Linux/Mac
   lsof -i :3000
   ```
2. Process را terminate کنید یا port را در docker-compose.yml تغییر دهید

### مشکل: Container fails to start

**راه‌حل:**
1. Logs را بررسی کنید:
   ```bash
   docker-compose logs [service-name]
   ```
2. Environment variables را بررسی کنید
3. Dependencies را بررسی کنید

### مشکل: Database connection error

**راه‌حل:**
1. مطمئن شوید که postgres container در حال اجرا است
2. منتظر بمانید تا database کاملاً initialize شود
3. Connection string را بررسی کنید

## دسترسی به Admin Dashboard

### Login

1. به http://localhost:3001 بروید
2. با credentials زیر login کنید:
   - **Email**: admin@neuropredict-ai.com
   - **Password**: admin123 (یا password که در setup استفاده کردید)

### Features

- **Real-time Monitoring**: WebSocket برای live updates
- **AI/ML Health**: Model drift, performance, confidence scores
- **Clinical Monitoring**: Longitudinal tracking, alerts
- **System Health**: CPU, memory, disk, network
- **Security Monitoring**: Audit logs, authentication

## Development Mode

برای development با hot reload:

```bash
# Services already configured for hot reload
# Changes in code will automatically reload
```

## Production Mode

برای production:

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

## نکات مهم

1. **First Run**: اولین بار ممکن است چند دقیقه طول بکشد تا images download شوند
2. **Database**: Database به صورت خودکار initialize می‌شود
3. **Cache**: Redis برای caching استفاده می‌شود
4. **Monitoring**: Prometheus و Grafana در production compose موجود هستند

## پشتیبانی

برای مشکلات:
- Logs را بررسی کنید: `docker-compose logs -f`
- Health check کنید: `curl http://localhost:8000/health`
- Documentation: `docs/INSTALLATION.md`

