# راهنمای استقرار Production - NeuroPredict-AI

## 📋 فهرست مطالب

1. [پیش‌نیازها](#پیش‌نیازها)
2. [آماده‌سازی](#آماده‌سازی)
3. [استقرار با Docker Compose](#استقرار-با-docker-compose)
4. [استقرار با Kubernetes](#استقرار-با-kubernetes)
5. [Monitoring & Alerting](#monitoring--alerting)
6. [Backup & Disaster Recovery](#backup--disaster-recovery)
7. [Security Hardening](#security-hardening)

---

## پیش‌نیازها

### سخت‌افزار

- **CPU**: حداقل 4 cores (8+ cores توصیه می‌شود)
- **RAM**: حداقل 16GB (32GB+ توصیه می‌شود)
- **Storage**: حداقل 200GB SSD
- **Network**: حداقل 100Mbps

### نرم‌افزار

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.24+ (برای K8s deployment)
- PostgreSQL Client Tools (برای backup)

---

## آماده‌سازی

### 1. Environment Variables

فایل `.env.production` ایجاد کنید:

```bash
# Database
POSTGRES_DB=neuropredict_db
POSTGRES_USER=neuropredict_user
POSTGRES_PASSWORD=<secure-password>
POSTGRES_HOST=postgres

# Security
SECRET_KEY=<generate-secure-key-32-chars-min>
ALGORITHM=HS256

# Redis
REDIS_PASSWORD=<secure-password>

# Application
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://neuropredict-ai.com,https://www.neuropredict-ai.com

# Monitoring
GRAFANA_PASSWORD=<secure-password>

# SMTP (for alerts)
SMTP_USERNAME=<smtp-user>
SMTP_PASSWORD=<smtp-password>
```

### 2. SSL Certificates

SSL certificates را در `nginx/ssl/` قرار دهید:

```bash
mkdir -p nginx/ssl
# Copy your SSL certificates
cp cert.pem nginx/ssl/
cp key.pem nginx/ssl/
```

---

## استقرار با Docker Compose

### 1. استقرار

```bash
# استفاده از docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d

# بررسی وضعیت
docker-compose -f docker-compose.prod.yml ps

# مشاهده لاگ‌ها
docker-compose -f docker-compose.prod.yml logs -f
```

### 2. بررسی سلامت سیستم

```bash
# Health check
curl https://api.neuropredict-ai.com/health

# Metrics
curl https://api.neuropredict-ai.com/metrics
```

### 3. دسترسی به Monitoring

- **Grafana**: https://your-domain:3001
- **Prometheus**: http://your-domain:9090
- **Alertmanager**: http://your-domain:9093

---

## استقرار با Kubernetes

### 1. ایجاد Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. ایجاد Secrets

```bash
# از فایل .env
kubectl create secret generic neuropredict-secrets \
  --from-env-file=.env.production \
  --namespace=neuropredict-ai

# یا دستی
kubectl create secret generic neuropredict-secrets \
  --from-literal=SECRET_KEY='your-key' \
  --from-literal=POSTGRES_PASSWORD='your-password' \
  --namespace=neuropredict-ai
```

### 3. ایجاد ConfigMap

```bash
kubectl apply -f k8s/configmap.yaml
```

### 4. استقرار سرویس‌ها

```bash
# Database
kubectl apply -f k8s/deployment-database.yaml

# Backend
kubectl apply -f k8s/deployment-backend.yaml

# Frontend (اگر موجود باشد)
# kubectl apply -f k8s/deployment-frontend.yaml

# Ingress
kubectl apply -f k8s/ingress.yaml

# Pod Disruption Budget
kubectl apply -f k8s/pdb.yaml
```

### 5. بررسی وضعیت

```bash
# Pods
kubectl get pods -n neuropredict-ai

# Services
kubectl get svc -n neuropredict-ai

# Ingress
kubectl get ingress -n neuropredict-ai

# HPA
kubectl get hpa -n neuropredict-ai
```

---

## Monitoring & Alerting

### Prometheus

Prometheus به صورت خودکار metrics را جمع‌آوری می‌کند:

- **HTTP Metrics**: Request rate, latency, error rates
- **AI/ML Metrics**: Prediction latency, confidence scores
- **System Metrics**: CPU, memory, disk, network
- **Database Metrics**: Connections, query performance

### Grafana Dashboards

Dashboards پیش‌فرض:
- System Overview
- API Performance
- AI/ML Health
- Database Performance
- Security Events

### Alerting

Alerts برای:
- System downtime
- High error rates
- High latency
- Model drift
- Security incidents

---

## Backup & Disaster Recovery

### Automated Backups

```bash
# Setup cron job برای daily backup
0 2 * * * /path/to/scripts/backup_scheduler.sh
```

### Manual Backup

```bash
python scripts/backup_database.py backup \
    --db-name neuropredict_db \
    --db-user postgres \
    --db-password <password> \
    --output-dir /backups
```

### Restore

```bash
python scripts/backup_database.py restore \
    --backup-file /backups/neuropredict_db_20240115_020000.sql \
    --db-name neuropredict_db \
    --db-user postgres \
    --db-password <password>
```

### Backup Strategy

- **Daily Backups**: هر شب ساعت 2 صبح
- **Weekly Backups**: هر یکشنبه
- **Monthly Backups**: اول هر ماه
- **Retention**: 30 روز daily, 12 ماه monthly

---

## Security Hardening

### 1. Security Scanning

```bash
# اجرای security scan
python scripts/security_scan.py

# بررسی گزارش‌ها
cat security_reports/security_scan_report.txt
```

### 2. Dependency Updates

```bash
# بررسی vulnerabilities
safety check

# به‌روزرسانی dependencies
pip list --outdated
pip install --upgrade <package>
```

### 3. Network Security

- استفاده از Firewall
- IP Whitelisting برای admin endpoints
- Rate Limiting
- DDoS Protection

### 4. Application Security

- HTTPS only
- Security headers
- Input validation
- SQL injection prevention
- XSS protection

---

## Compliance

### HIPAA Compliance

- ✅ Encryption at rest
- ✅ Encryption in transit
- ✅ Access controls
- ✅ Audit logging
- ✅ Data backup

### GDPR Compliance

- ✅ Data minimization
- ✅ Right to access
- ✅ Right to erasure
- ✅ Data portability
- ✅ Privacy by design

### FDA 21 CFR Part 11

- ✅ Electronic records validation
- ✅ Audit trail
- ✅ System validation
- ✅ Change control

---

## Troubleshooting

### مشکل: Pods در حال Crash

```bash
# بررسی logs
kubectl logs <pod-name> -n neuropredict-ai

# بررسی events
kubectl describe pod <pod-name> -n neuropredict-ai
```

### مشکل: Database Connection Failed

```bash
# بررسی database pod
kubectl get pods -n neuropredict-ai | grep postgres

# بررسی connection string
kubectl get secret neuropredict-secrets -n neuropredict-ai -o yaml
```

### مشکل: High Memory Usage

```bash
# بررسی resource usage
kubectl top pods -n neuropredict-ai

# Scale up اگر نیاز باشد
kubectl scale deployment neuropredict-backend --replicas=5 -n neuropredict-ai
```

---

## Maintenance

### Regular Tasks

1. **Weekly**: Review security alerts
2. **Monthly**: Update dependencies
3. **Quarterly**: Security audit
4. **Annually**: Disaster recovery testing

### Updates

```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

---

## منابع بیشتر

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Security Best Practices](docs/SECURITY_INFRASTRUCTURE_ROADMAP.md)

