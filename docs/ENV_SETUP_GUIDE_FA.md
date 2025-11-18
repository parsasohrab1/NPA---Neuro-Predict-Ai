# راهنمای تنظیم متغیرهای محیطی (Environment Variables)

## مقدمه

این راهنما نحوه تنظیم متغیرهای محیطی برای پروژه NeuroPredict-AI را توضیح می‌دهد.

---

## 1. ایجاد فایل `.env`

### Backend

در دایرکتوری `backend/` فایل `.env` را ایجاد کنید:

```bash
cd backend
cp .env.example .env  # اگر .env.example وجود دارد
# یا
touch .env
```

### Frontend

در دایرکتوری `frontend/` فایل `.env` را ایجاد کنید:

```bash
cd frontend
touch .env
```

---

## 2. متغیرهای ضروری Backend

### 2.1 امنیت (Security) - **فوری**

```env
# SECRET_KEY - بسیار مهم!
# برای تولید کلید امن:
# python -c 'import secrets; print(secrets.token_urlsafe(32))'
SECRET_KEY=your-generated-secret-key-min-32-characters

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

⚠️ **هشدار:** هرگز SECRET_KEY پیش‌فرض را در production استفاده نکنید!

### 2.2 پایگاه داده (Database)

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/neuropredict_db
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/neuropredict_db
```

### 2.3 Redis

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 2.4 محیط اجرا (Environment)

```env
ENVIRONMENT=development  # یا production, staging, test
DEBUG=true  # در production باید false باشد
```

### 2.5 CORS

```env
# لیست URLهای frontend (JSON array)
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:8080"]
```

---

## 3. متغیرهای Frontend

### 3.1 API URL

```env
VITE_API_URL=http://localhost:8000
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 4. تولید SECRET_KEY امن

### روش 1: Python

```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

### روش 2: OpenSSL

```bash
openssl rand -hex 32
```

### روش 3: Online Generator

⚠️ **توصیه نمی‌شود** - فقط برای development

---

## 5. مثال فایل `.env` کامل (Development)

### Backend `.env`

```env
# Application
APP_NAME=NeuroPredict-AI
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/neuropredict_db
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/neuropredict_db

# Security - Generate your own!
SECRET_KEY=change-this-to-a-secure-random-string-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:8080"]

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# File Upload
MAX_UPLOAD_SIZE=104857600
UPLOAD_DIR=uploads
DICOM_DIR=uploads/dicom
MRI_DIR=uploads/mri
REPORTS_DIR=uploads/reports

# AI Models
ALZHEIMER_MODEL_PATH=models/alzheimer_model.pth
PARKINSON_MODEL_PATH=models/parkinson_model.pth
ENSEMBLE_MODEL_PATH=models/ensemble_model.pth
MODEL_REGISTRY_PATH=models/registry.json

# Model Config
MODEL_CONFIDENCE_THRESHOLD=0.75
BATCH_SIZE=32
USE_TRAINED_MODEL=true

# Training
TRAINING_DATA_DIR=data/data/csv
TRAIN_RATIO=0.7
VAL_RATIO=0.15
TEST_RATIO=0.15
TRAINING_EPOCHS=100
TRAINING_BATCH_SIZE=32
TRAINING_LEARNING_RATE=0.001
TRAINING_WEIGHT_DECAY=0.00001
TRAINING_PATIENCE=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/neuropredict.log

# Audit
ENABLE_AUDIT_LOG=true
AUDIT_LOG_FILE=logs/audit.log

# Performance
MAX_CONCURRENT_PREDICTIONS=10
PREDICTION_TIMEOUT=300

# Rate Limiting
RATE_LIMIT_DEFAULT_PER_MINUTE=120
RATE_LIMIT_USER_PER_HOUR=1000
RATE_LIMIT_LOGIN_PER_MINUTE=10
RATE_LIMIT_UPLOAD_PER_MINUTE=10

# Backup
BACKUP_DIR=backups
BACKUP_OFFSITE_DIR=backups_offsite
BACKUP_FULL_INTERVAL_HOURS=24
BACKUP_WAL_INTERVAL_MINUTES=15
BACKUP_RETENTION_DAYS=14
BACKUP_VERIFY_WEEKLY=true
BACKUP_VERIFY_INTERVAL_DAYS=7
```

### Frontend `.env`

```env
VITE_API_URL=http://localhost:8000
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 6. تنظیمات Production

### 6.1 امنیت Production

```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-secure-key>
```

### 6.2 CORS Production

```env
CORS_ORIGINS=["https://yourdomain.com","https://admin.yourdomain.com"]
```

### 6.3 Database Production

```env
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/dbname
```

### 6.4 استفاده از Secrets Management

برای production، از سیستم‌های مدیریت secrets استفاده کنید:
- **Docker Secrets**
- **Kubernetes Secrets**
- **AWS Secrets Manager**
- **HashiCorp Vault**

---

## 7. بررسی صحت تنظیمات

### 7.1 Backend

```bash
cd backend
python -c "from app.core.config import settings; print('Config loaded successfully')"
```

### 7.2 Frontend

```bash
cd frontend
npm run build  # باید بدون خطا اجرا شود
```

---

## 8. مشکلات رایج

### 8.1 خطای SECRET_KEY

```
ValueError: SECRET_KEY must be at least 32 characters long
```

**راه حل:** یک کلید 32 کاراکتری یا بیشتر تولید کنید.

### 8.2 خطای CORS

```
CORS policy: No 'Access-Control-Allow-Origin' header
```

**راه حل:** URL frontend را به `CORS_ORIGINS` اضافه کنید.

### 8.3 خطای Database Connection

```
Could not connect to database
```

**راه حل:** 
- بررسی کنید PostgreSQL در حال اجرا است
- بررسی کنید `DATABASE_URL` صحیح است
- بررسی کنید credentials صحیح است

---

## 9. چک‌لیست

- [ ] فایل `.env` در `backend/` ایجاد شده
- [ ] فایل `.env` در `frontend/` ایجاد شده
- [ ] `SECRET_KEY` تولید و تنظیم شده (حداقل 32 کاراکتر)
- [ ] `DATABASE_URL` صحیح است
- [ ] `REDIS_HOST` و `REDIS_PORT` صحیح است
- [ ] `CORS_ORIGINS` شامل URLهای frontend است
- [ ] `ENVIRONMENT` و `DEBUG` برای محیط مناسب تنظیم شده
- [ ] فایل `.env` در `.gitignore` است (نباید commit شود!)

---

## 10. منابع

- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/usage/settings/)
- [Environment Variables Best Practices](https://12factor.net/config)

---

**آخرین به‌روزرسانی:** 2024-12-XX

