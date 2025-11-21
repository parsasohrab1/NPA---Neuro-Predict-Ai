# 🔧 NeuroPredict-AI Troubleshooting Guide

راهنمای جامع عیب‌یابی برای مشکلات رایج در NeuroPredict-AI

## فهرست مطالب

1. [مشکلات نصب و راه‌اندازی](#مشکلات-نصب-و-راه‌اندازی)
2. [مشکلات Docker](#مشکلات-docker)
3. [مشکلات پایگاه داده](#مشکلات-پایگاه-داده)
4. [مشکلات Backend API](#مشکلات-backend-api)
5. [مشکلات Frontend](#مشکلات-frontend)
6. [مشکلات احراز هویت](#مشکلات-احراز-هویت)
7. [مشکلات پیش‌بینی AI](#مشکلات-پیش‌بینی-ai)
8. [مشکلات آپلود فایل](#مشکلات-آپلود-فایل)
9. [مشکلات عملکرد](#مشکلات-عملکرد)
10. [مشکلات شبکه و اتصال](#مشکلات-شبکه-و-اتصال)
11. [مشکلات Production](#مشکلات-production)
12. [لاگ‌ها و دیباگ](#لاگ‌ها-و-دیباگ)

---

## مشکلات نصب و راه‌اندازی

### مشکل: Docker نصب نیست

**علائم:**
```
docker: command not found
```

**راه‌حل:**
```bash
# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# macOS
brew install docker

# Windows
# دانلود Docker Desktop از docker.com
```

### مشکل: Docker Compose پیدا نمی‌شود

**علائم:**
```
docker-compose: command not found
```

**راه‌حل:**
```bash
# نصب Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# یا استفاده از docker compose (v2)
docker compose version
```

### مشکل: Port در حال استفاده است

**علائم:**
```
Error: bind: address already in use
Port 8000 is already allocated
```

**راه‌حل:**
```bash
# بررسی پورت‌های استفاده شده
# Linux/Mac
lsof -i :8000
netstat -ano | findstr :8000  # Windows

# تغییر پورت در docker-compose.yml
ports:
  - "8001:8000"  # به جای 8000:8000

# یا متوقف کردن سرویس استفاده کننده
sudo kill -9 <PID>
```

### مشکل: فایل .env وجود ندارد

**علائم:**
```
FileNotFoundError: .env file not found
```

**راه‌حل:**
```bash
# کپی از فایل نمونه
cp backend/.env.example backend/.env

# ویرایش فایل .env
nano backend/.env  # یا ویرایشگر دلخواه

# تولید SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## مشکلات Docker

### مشکل: Container شروع نمی‌شود

**علائم:**
```
Container exited with code 1
```

**راه‌حل:**
```bash
# بررسی لاگ‌ها
docker-compose logs backend
docker-compose logs frontend

# بررسی وضعیت
docker-compose ps

# راه‌اندازی مجدد
docker-compose restart backend

# راه‌اندازی از ابتدا
docker-compose down
docker-compose up -d
```

### مشکل: Health check failed

**علائم:**
```
Health check failed: curl: (7) Failed to connect
```

**راه‌حل:**
```bash
# بررسی نصب curl در container
docker exec -it neuropredict-backend curl --version

# اگر curl نصب نیست، Dockerfile را بررسی کنید
# باید شامل: RUN apt-get install -y curl (یا apk add curl)

# بررسی دسترسی به health endpoint
docker exec -it neuropredict-backend curl http://localhost:8000/health
```

### مشکل: Volume mount کار نمی‌کند

**علائم:**
```
Permission denied
Files not syncing
```

**راه‌حل:**
```bash
# بررسی مجوزهای فایل
ls -la backend/

# تنظیم مجوزها
chmod -R 755 backend/
chown -R $USER:$USER backend/

# در Windows، بررسی تنظیمات Docker Desktop
# Settings → Resources → File Sharing
```

### مشکل: Out of memory

**علائم:**
```
Container killed: OOM (Out of Memory)
```

**راه‌حل:**
```bash
# بررسی استفاده از حافظه
docker stats

# افزایش resource limits در docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G  # افزایش از 2G
```

---

## مشکلات پایگاه داده

### مشکل: اتصال به پایگاه داده برقرار نمی‌شود

**علائم:**
```
Connection refused
Could not connect to database
```

**راه‌حل:**
```bash
# بررسی وضعیت PostgreSQL
docker-compose ps postgres

# بررسی لاگ‌های PostgreSQL
docker-compose logs postgres

# تست اتصال
docker exec -it neuropredict-db psql -U postgres -c "SELECT 1;"

# بررسی DATABASE_URL در .env
# باید به صورت: postgresql+asyncpg://postgres:postgres@postgres:5432/neuropredict_db
```

### مشکل: Migration اجرا نمی‌شود

**علائم:**
```
Alembic migration failed
Table already exists
```

**راه‌حل:**
```bash
# اجرای migration دستی
docker-compose exec backend alembic upgrade head

# بررسی وضعیت migration
docker-compose exec backend alembic current

# بازگشت به migration قبلی
docker-compose exec backend alembic downgrade -1

# بازنشانی کامل (⚠️ داده‌ها پاک می‌شوند)
docker-compose down -v
docker-compose up -d
```

### مشکل: Query timeout

**علائم:**
```
Query timeout exceeded
Database connection pool exhausted
```

**راه‌حل:**
```bash
# بررسی تعداد اتصالات
docker exec -it neuropredict-db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# افزایش pool size در config.py
pool_size=20  # به جای 10
max_overflow=30  # به جای 20

# بررسی query‌های کند
docker exec -it neuropredict-db psql -U postgres -c "SELECT pid, now() - query_start as duration, query FROM pg_stat_activity WHERE state = 'active';"
```

---

## مشکلات Backend API

### مشکل: API پاسخ نمی‌دهد

**علائم:**
```
Connection refused
502 Bad Gateway
```

**راه‌حل:**
```bash
# بررسی وضعیت backend
docker-compose ps backend

# بررسی لاگ‌ها
docker-compose logs -f backend

# تست health endpoint
curl http://localhost:8000/health

# بررسی پورت
netstat -tulpn | grep 8000
```

### مشکل: 500 Internal Server Error

**علائم:**
```
500 Internal Server Error
Internal server error occurred
```

**راه‌حل:**
```bash
# بررسی لاگ‌های کامل
docker-compose logs backend | tail -100

# بررسی traceback در لاگ
# معمولاً شامل خطا و stack trace است

# بررسی environment variables
docker-compose exec backend env | grep -E "DATABASE|SECRET|REDIS"

# بررسی dependencies
docker-compose exec backend pip list
```

### مشکل: Rate limiting فعال است

**علائم:**
```
429 Too Many Requests
Rate limit exceeded
```

**راه‌حل:**
```bash
# بررسی تنظیمات rate limiting
# در config.py:
RATE_LIMIT_ENABLED = True
RATE_LIMIT_DEFAULT_PER_MINUTE = 120

# غیرفعال کردن موقت (development)
RATE_LIMIT_ENABLED = False

# بررسی Redis connection
docker-compose exec backend python -c "import redis; r = redis.from_url('redis://redis:6379/0'); print(r.ping())"
```

### مشکل: CORS error

**علائم:**
```
CORS policy: No 'Access-Control-Allow-Origin' header
```

**راه‌حل:**
```bash
# بررسی CORS_ORIGINS در .env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# در config.py:
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:3001"]

# راه‌اندازی مجدد backend
docker-compose restart backend
```

---

## مشکلات Frontend

### مشکل: صفحه سفید نمایش داده می‌شود

**علائم:**
```
Blank page
No content displayed
```

**راه‌حل:**
```bash
# بررسی console در browser (F12)
# معمولاً خطای JavaScript وجود دارد

# بررسی لاگ‌های frontend
docker-compose logs frontend

# بررسی build
cd frontend
npm run build

# بررسی API connection
# در browser console:
fetch('http://localhost:8000/health').then(r => r.json()).then(console.log)
```

### مشکل: Hot reload کار نمی‌کند

**علائم:**
```
Changes not reflected
Page not updating
```

**راه‌حل:**
```bash
# بررسی volume mount
docker-compose ps frontend

# بررسی Vite config
# در vite.config.ts باید watch فعال باشد

# راه‌اندازی مجدد
docker-compose restart frontend

# یا اجرای دستی
cd frontend
npm run dev
```

### مشکل: Build failed

**علائم:**
```
Build error
npm ERR!
```

**راه‌حل:**
```bash
# پاک کردن node_modules
cd frontend
rm -rf node_modules package-lock.json

# نصب مجدد
npm install

# بررسی version compatibility
node --version  # باید >= 18
npm --version   # باید >= 9

# بررسی خطاهای خاص در output
```

---

## مشکلات احراز هویت

### مشکل: Login موفق نمی‌شود

**علائم:**
```
Invalid credentials
401 Unauthorized
```

**راه‌حل:**
```bash
# بررسی کاربر در database
docker-compose exec backend python -c "
from app.db.session import AsyncSessionLocal
from app.models.user import User
import asyncio

async def check():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == 'admin@example.com'))
        user = result.scalar_one_or_none()
        print(f'User found: {user is not None}')
        if user:
            print(f'Active: {user.is_active}')

asyncio.run(check())
"

# ایجاد کاربر جدید
docker-compose exec backend python scripts/create_admin.py

# بررسی SECRET_KEY
# باید در .env تنظیم شده باشد
```

### مشکل: Token منقضی می‌شود

**علائم:**
```
Token expired
401 Unauthorized after some time
```

**راه‌حل:**
```bash
# بررسی تنظیمات token expiration
# در config.py:
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # افزایش اگر نیاز است
REFRESH_TOKEN_EXPIRE_DAYS = 7

# استفاده از refresh token
# در frontend باید refresh token logic پیاده‌سازی شود
```

### مشکل: Session timeout

**علائم:**
```
Session expired
Please login again
```

**راه‌حل:**
```bash
# بررسی session management
# در backend/app/services/security_service.py

# افزایش session timeout
SESSION_TIMEOUT_MINUTES = 60  # به جای 30
```

---

## مشکلات پیش‌بینی AI

### مشکل: Prediction timeout

**علائم:**
```
Prediction taking too long
Request timeout
```

**راه‌حل:**
```bash
# بررسی لاگ‌های AI service
docker-compose logs backend | grep -i "prediction\|model"

# بررسی resource limits
docker stats neuropredict-backend

# افزایش timeout در API
# در predictions.py:
timeout = 300  # 5 minutes

# بررسی model loading
docker-compose exec backend python -c "
from app.services.ai_service import AIService
import asyncio
asyncio.run(AIService.load_models())
"
```

### مشکل: Model load failed

**علائم:**
```
Model not found
Model loading error
```

**راه‌حل:**
```bash
# بررسی وجود model files
ls -la models/

# بررسی path در config
MODEL_DIR = "models"

# بررسی PyTorch/TensorFlow installation
docker-compose exec backend python -c "import torch; print(torch.__version__)"
docker-compose exec backend python -c "import tensorflow as tf; print(tf.__version__)"
```

### مشکل: Prediction accuracy پایین است

**علائم:**
```
Low confidence scores
Incorrect predictions
```

**راه‌حل:**
```bash
# این مشکل معمولاً مربوط به model training است
# بررسی:
# 1. Model weights به‌روز هستند؟
# 2. Training data کافی است؟
# 3. Input data quality مناسب است؟

# بررسی feature importance
# در prediction results باید feature_importance موجود باشد
```

---

## مشکلات آپلود فایل

### مشکل: فایل آپلود نمی‌شود

**علائم:**
```
Upload failed
File too large
```

**راه‌حل:**
```bash
# بررسی file size limit
# در config.py:
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# بررسی disk space
df -h

# بررسی permissions
ls -la uploads/

# بررسی فرمت فایل
# DICOM files باید .dcm extension داشته باشند
```

### مشکل: DICOM file invalid

**علائم:**
```
Invalid DICOM file
Cannot read DICOM
```

**راه‌حل:**
```bash
# بررسی DICOM file با pydicom
docker-compose exec backend python -c "
from pydicom import dcmread
try:
    ds = dcmread('uploads/dicom/test.dcm')
    print('Valid DICOM file')
except Exception as e:
    print(f'Error: {e}')
"

# بررسی DICOM metadata
# باید شامل: Modality, StudyDate, PatientID باشد
```

### مشکل: File corruption

**علائم:**
```
File corrupted
Cannot process file
```

**راه‌حل:**
```bash
# بررسی checksum
md5sum uploads/dicom/file.dcm

# بررسی disk errors
dmesg | grep -i error

# بررسی file permissions
chmod 644 uploads/dicom/*
```

---

## مشکلات عملکرد

### مشکل: Slow response times

**علائم:**
```
API responses slow
High latency
```

**راه‌حل:**
```bash
# بررسی database queries
docker exec -it neuropredict-db psql -U postgres -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# بررسی indexes
docker exec -it neuropredict-db psql -U postgres -c "\d+ patients"

# بررسی Redis cache
docker-compose exec redis redis-cli INFO stats

# بررسی connection pool
# در session.py باید pool_size مناسب باشد
```

### مشکل: High memory usage

**علائم:**
```
Out of memory
High RAM usage
```

**راه‌حل:**
```bash
# بررسی memory usage
docker stats

# بررسی memory leaks
# در Python باید memory profiling انجام شود

# افزایش memory limits
# در docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
```

### مشکل: High CPU usage

**علائم:**
```
CPU at 100%
Slow performance
```

**راه‌حل:**
```bash
# بررسی CPU usage
docker stats
top

# بررسی processes
docker-compose exec backend ps aux

# بررسی background tasks
# ممکن است scheduled tasks زیادی در حال اجرا باشند
```

---

## مشکلات شبکه و اتصال

### مشکل: Services نمی‌توانند با هم ارتباط برقرار کنند

**علائم:**
```
Connection refused between services
Network unreachable
```

**راه‌حل:**
```bash
# بررسی Docker network
docker network ls
docker network inspect neuropredict-network

# بررسی service names
# در docker-compose.yml باید service names صحیح باشند
# backend → postgres (نه localhost)

# تست connectivity
docker-compose exec backend ping postgres
docker-compose exec backend ping redis
```

### مشکل: External API calls fail

**علائم:**
```
Cannot reach external API
Network timeout
```

**راه‌حل:**
```bash
# بررسی firewall
sudo ufw status

# بررسی proxy settings
# در Docker باید proxy تنظیم شود اگر نیاز است

# بررسی DNS
docker-compose exec backend nslookup api.example.com
```

---

## مشکلات Production

### مشکل: Secrets not found

**علائم:**
```
Secret not found
Docker secret error
```

**راه‌حل:**
```bash
# بررسی Docker Swarm
docker info | grep Swarm

# ایجاد secrets
./scripts/create_docker_secrets.sh

# بررسی secrets
docker secret ls

# استفاده از secrets
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### مشکل: SSL/HTTPS issues

**علائم:**
```
SSL certificate error
HTTPS not working
```

**راه‌حل:**
```bash
# بررسی certificate
openssl x509 -in cert.pem -text -noout

# بررسی nginx/load balancer config
# باید SSL properly configured باشد

# استفاده از Let's Encrypt
certbot --nginx -d yourdomain.com
```

### مشکل: Backup failed

**علائم:**
```
Backup error
Cannot create backup
```

**راه‌حل:**
```bash
# بررسی backup service
docker-compose logs backend | grep backup

# بررسی disk space
df -h backups/

# اجرای manual backup
docker-compose exec backend python -c "
from app.services.backup_service import BackupService
import asyncio
result = asyncio.run(BackupService.create_database_backup())
print(result)
"
```

---

## لاگ‌ها و دیباگ

### مشاهده لاگ‌های Real-time

```bash
# همه services
docker-compose logs -f

# یک service خاص
docker-compose logs -f backend

# آخرین 100 خط
docker-compose logs --tail=100 backend

# با timestamp
docker-compose logs -f --timestamps backend
```

### بررسی لاگ‌های Application

```bash
# لاگ‌های Python
docker-compose exec backend tail -f logs/app.log

# لاگ‌های JSON (structured logging)
docker-compose logs backend | jq .

# فیلتر کردن errors
docker-compose logs backend | grep -i error
```

### Debug Mode

```bash
# فعال کردن debug در .env
DEBUG=True
LOG_LEVEL=DEBUG

# راه‌اندازی مجدد
docker-compose restart backend

# بررسی debug logs
docker-compose logs backend | grep DEBUG
```

### Performance Profiling

```bash
# استفاده از cProfile
docker-compose exec backend python -m cProfile -o profile.stats app/main.py

# بررسی profile
python -m pstats profile.stats
```

---

## دریافت کمک بیشتر

### منابع مفید

1. **مستندات:**
   - [User Guide](USER_GUIDE.md)
   - [API Documentation](API.md)
   - [Installation Guide](INSTALLATION.md)

2. **لاگ‌ها:**
   - همیشه لاگ‌ها را بررسی کنید
   - Stack traces را ذخیره کنید

3. **Community:**
   - GitHub Issues
   - Support Email: support@neuropredict-ai.com

### گزارش مشکل

هنگام گزارش مشکل، لطفاً شامل کنید:
- نسخه سیستم
- مراحل بازتولید مشکل
- لاگ‌های مربوطه
- Screenshots (در صورت امکان)
- Environment details

---

*آخرین به‌روزرسانی: دسامبر 2024*

