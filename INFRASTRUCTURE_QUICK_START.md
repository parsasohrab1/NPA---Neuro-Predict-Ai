# 🚀 راه‌اندازی سریع زیرساخت NeuroPredict AI

## Quick Start Guide - Infrastructure Setup

---

## 📋 نمای کلی / Overview

این پروژه شامل راه‌اندازی کامل زیرساخت امنیتی، مانیتورینگ و Kubernetes برای NeuroPredict AI است.

This project includes complete infrastructure setup for security, monitoring, and Kubernetes deployment of NeuroPredict AI.

---

## 🎯 چه چیزی پیاده‌سازی شده است؟

### ✅ 1. Security Audit Framework
- راهنمای جامع ممیزی امنیتی (70+ security checks)
- چک‌لیست OWASP, NIST, HIPAA compliance
- ابزارها و تکنیک‌های تست

**📄 فایل**: `docs/SECURITY_AUDIT_GUIDE.md`

### ✅ 2. Penetration Testing
- اسکریپت اسکن خودکار امنیتی
- تست authentication و authorization
- سناریوهای حمله مختلف

**📄 فایل‌ها**: 
- `docs/PENETRATION_TESTING_GUIDE.md`
- `pentest/scripts/automated_security_scan.sh`
- `pentest/scripts/test_authentication.py`

### ✅ 3. Prometheus + Grafana
- پیکربندی کامل monitoring stack
- 25+ alert rules
- Grafana dashboards
- Alertmanager configuration

**📄 فایل‌ها**:
- `monitoring/prometheus-advanced.yml`
- `monitoring/docker-compose.monitoring.yml`
- `monitoring/alerts/*.yml`

### ✅ 4. Kubernetes Cluster
- 10+ Kubernetes manifests
- Auto-scaling (HPA)
- Network policies
- Ingress با TLS
- اسکریپت استقرار خودکار

**📄 فایل‌ها**:
- `infra/k8s/*.yaml`
- `infra/k8s/deploy.sh`

---

## 🚀 راه‌اندازی در 5 دقیقه

### گام 1️⃣: Security Audit

```bash
# مطالعه راهنما
cat docs/SECURITY_AUDIT_GUIDE.md

# برای تیم‌های خارجی:
# این سند شامل تمام اطلاعات مورد نیاز برای ممیزی امنیتی است
```

### گام 2️⃣: Penetration Testing

```bash
# اجرای اسکن خودکار
cd pentest/scripts

# در Linux/Mac:
chmod +x automated_security_scan.sh
./automated_security_scan.sh

# تست Authentication
pip install requests
python test_authentication.py --url https://api-staging.neuropredict.local
```

### گام 3️⃣: Monitoring Stack

```bash
# استقرار Prometheus + Grafana
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# بررسی وضعیت
docker-compose -f docker-compose.monitoring.yml ps

# دسترسی به Grafana
# URL: http://localhost:3002
# Username: admin
# Password: admin (تغییر دهید در production)

# دسترسی به Prometheus
# URL: http://localhost:9090
```

### گام 4️⃣: Kubernetes Deployment

```bash
# پیش‌نیازها
# - kubectl نصب باشد
# - دسترسی به Kubernetes cluster
# - Docker images ساخته شده باشند

cd infra/k8s

# ایجاد secrets
cat > .env.production << 'EOF'
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/neuropredict_db
SECRET_KEY=YOUR_SECRET_KEY_HERE
# ... بقیه secrets
EOF

# استقرار
./deploy.sh deploy

# بررسی وضعیت
kubectl get all -n neuropredict
```

---

## 📊 دسترسی به سرویس‌ها

### بعد از استقرار موفق:

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | https://neuropredict.ai | - |
| Backend API | https://api.neuropredict.ai | - |
| Admin Dashboard | https://admin.neuropredict.ai | admin user |
| Grafana | https://grafana.neuropredict.ai | admin / admin |
| Prometheus | https://prometheus.neuropredict.ai | - |

### دسترسی محلی (Port Forwarding):

```bash
# Backend API
kubectl port-forward svc/backend 8000:8000 -n neuropredict

# Grafana
kubectl port-forward svc/grafana 3000:3000 -n neuropredict-monitoring

# Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n neuropredict-monitoring
```

---

## 📚 مستندات کامل

### 1. Security
- **Security Audit Guide**: `docs/SECURITY_AUDIT_GUIDE.md`
- **Penetration Testing Guide**: `docs/PENETRATION_TESTING_GUIDE.md`

### 2. Infrastructure
- **Kubernetes Deployment**: `docs/KUBERNETES_DEPLOYMENT_GUIDE.md`
- **Complete Setup Summary**: `docs/INFRASTRUCTURE_SETUP_COMPLETE.md`

### 3. Scripts
- **Security Scan**: `pentest/scripts/automated_security_scan.sh`
- **Auth Testing**: `pentest/scripts/test_authentication.py`
- **K8s Deployment**: `infra/k8s/deploy.sh`

---

## 🔧 دستورات مفید

### Monitoring

```bash
# مشاهده metrics
curl http://localhost:9090/api/v1/query?query=up

# بررسی alerts
curl http://localhost:9090/api/v1/alerts

# Grafana API
curl -u admin:admin http://localhost:3002/api/dashboards/home
```

### Kubernetes

```bash
# وضعیت کلی
kubectl get all -n neuropredict

# Logs
kubectl logs -f deployment/neuropredict-backend -n neuropredict

# Shell access
kubectl exec -it deployment/neuropredict-backend -n neuropredict -- /bin/bash

# Scaling
kubectl scale deployment/neuropredict-backend --replicas=5 -n neuropredict

# Events
kubectl get events -n neuropredict --sort-by='.lastTimestamp'
```

### Security Testing

```bash
# ZAP Scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://api.neuropredict.local

# Trivy Container Scan
trivy image neuropredict/backend:latest

# Bandit Python Security
cd backend && bandit -r . -f json -o security_report.json
```

---

## 🔒 چک‌لیست امنیتی

قبل از Production:

- [ ] تمام secrets تغییر کرده‌اند
- [ ] TLS/SSL فعال است
- [ ] Firewall و Network Policies فعال است
- [ ] Backup استراتژی پیاده‌سازی شده
- [ ] Monitoring و Alerting فعال است
- [ ] Security Audit انجام شده
- [ ] Penetration Testing انجام شده
- [ ] Access logs فعال است
- [ ] HIPAA compliance بررسی شده
- [ ] Disaster Recovery plan آماده است

---

## 📈 Monitoring Dashboards

### Grafana Dashboards موجود:

1. **NeuroPredict Overview**
   - Request rate & Response time
   - CPU & Memory usage
   - Database connections
   - Error rates

### Prometheus Alerts:

- High Error Rate (>5%)
- High Response Time (>2s)
- API Endpoint Down
- High CPU/Memory Usage
- Database Issues
- SSL Certificate Expiring
- DDoS Detection

---

## 🐛 عیب‌یابی

### مشکلات رایج:

#### 1. Pod در حالت Pending
```bash
kubectl describe pod POD_NAME -n neuropredict
# بررسی کنید: resources, storage, node capacity
```

#### 2. Service دسترسی ندارد
```bash
kubectl get svc -n neuropredict
kubectl get endpoints -n neuropredict
```

#### 3. Database connection failed
```bash
kubectl logs statefulset/postgres -n neuropredict
kubectl exec -it statefulset/postgres -n neuropredict -- psql -U postgres
```

#### 4. Monitoring metrics missing
```bash
# بررسی Prometheus targets
curl http://localhost:9090/api/v1/targets

# بررسی service discovery
kubectl get servicemonitors -n neuropredict-monitoring
```

---

## 📞 پشتیبانی

### مشکل دارید؟

1. **مستندات را بررسی کنید**: 
   - `docs/KUBERNETES_DEPLOYMENT_GUIDE.md` - راهنمای کامل
   - `docs/INFRASTRUCTURE_SETUP_COMPLETE.md` - خلاصه کامل

2. **Logs را بررسی کنید**:
   ```bash
   kubectl logs -f deployment/neuropredict-backend -n neuropredict
   ```

3. **تماس با تیم**:
   - DevOps: devops@neuropredict.ai
   - Security: security@neuropredict.ai
   - On-Call: [تماس اضطراری]

---

## 🎯 مراحل بعدی

### پس از راه‌اندازی:

1. ✅ **Security Audit** را با تیم خارجی هماهنگ کنید
2. ✅ **Penetration Testing** در محیط Staging انجام دهید
3. ✅ **Load Testing** برای بررسی Auto-scaling
4. ✅ **Disaster Recovery** را تست کنید
5. ✅ **Documentation** را به تیم آموزش دهید

### بهبودهای آینده:

- [ ] CI/CD با GitOps (ArgoCD)
- [ ] Service Mesh (Istio/Linkerd)
- [ ] Multi-Region Deployment
- [ ] Advanced Monitoring (AI-powered)
- [ ] Cost Optimization

---

## 📊 آمار پروژه

```
✅ 4 سند جامع
✅ 10+ Kubernetes manifests  
✅ 25+ Alert rules
✅ 70+ Security checks
✅ 2 اسکریپت تست خودکار
✅ 1 Grafana dashboard
✅ Complete monitoring stack
✅ Production-ready deployment
```

---

## ⭐ ویژگی‌های کلیدی

- 🔒 **Security-First**: OWASP, NIST, HIPAA compliance
- 📊 **Observable**: Prometheus + Grafana + Loki + Jaeger
- ⚡ **Scalable**: Kubernetes با HPA (3-10 pods)
- 🛡️ **Resilient**: Health checks, auto-recovery, backups
- 🚀 **Production-Ready**: Complete documentation & automation
- 🌍 **Cloud-Native**: Kubernetes, containers, microservices

---

## 🎉 خلاصه

**همه چیز آماده است!** 🎊

شما اکنون دارای یک infrastructure کامل برای:
- ✅ Security Auditing
- ✅ Penetration Testing  
- ✅ Production Monitoring
- ✅ Kubernetes Deployment

**مستندات** جامع و به فارسی ✅  
**اسکریپت‌ها** آماده و قابل اجرا ✅  
**Best Practices** پیاده‌سازی شده ✅

---

**نسخه**: 1.0.0  
**تاریخ**: 26 نوامبر 2025  
**وضعیت**: ✅ آماده برای Production

**موفق باشید! 🚀**

