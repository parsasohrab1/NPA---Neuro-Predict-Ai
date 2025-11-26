# راهنمای استقرار Kubernetes

## راهنمای جامع استقرار NeuroPredict AI بر روی Kubernetes

### نسخه: 1.0.0
### تاریخ: November 2025

---

## فهرست مطالب

- [مقدمه](#مقدمه)
- [پیش‌نیازها](#پیش‌نیازها)
- [معماری](#معماری)
- [راه‌اندازی اولیه](#راه‌اندازی-اولیه)
- [استقرار](#استقرار)
- [مانیتورینگ](#مانیتورینگ)
- [امنیت](#امنیت)
- [عیب‌یابی](#عیب‌یابی)

---

## مقدمه

این سند راهنمای کاملی برای استقرار پلتفرم NeuroPredict AI بر روی Kubernetes ارائه می‌دهد.

### مزایای استقرار بر روی Kubernetes

- **مقیاس‌پذیری خودکار**: Auto-scaling بر اساس بار سیستم
- **بالا بودن دسترسی (High Availability)**: توزیع بار و redundancy
- **مدیریت منابع**: بهینه‌سازی استفاده از CPU و Memory
- **Rolling Updates**: به‌روزرسانی بدون قطعی سرویس
- **Self-healing**: بازیابی خودکار در صورت خرابی

---

## پیش‌نیازها

### ابزارهای مورد نیاز

```bash
# 1. kubectl - Kubernetes CLI
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# 2. helm - Package Manager
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 3. docker - برای ساخت images
# نصب Docker از: https://docs.docker.com/get-docker/

# 4. kubectx & kubens (اختیاری اما توصیه می‌شود)
sudo git clone https://github.com/ahmetb/kubectx /opt/kubectx
sudo ln -s /opt/kubectx/kubectx /usr/local/bin/kubectx
sudo ln -s /opt/kubectx/kubens /usr/local/bin/kubens
```

### Kubernetes Cluster

شما به یک Kubernetes cluster نیاز دارید. گزینه‌های مختلف:

#### گزینه 1: Managed Kubernetes (توصیه می‌شود برای Production)

```bash
# AWS EKS
eksctl create cluster \
  --name neuropredict-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.xlarge \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 10 \
  --managed

# Google GKE
gcloud container clusters create neuropredict-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10

# Azure AKS
az aks create \
  --resource-group neuropredict-rg \
  --name neuropredict-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10
```

#### گزینه 2: Local Development

```bash
# Minikube
minikube start --cpus 4 --memory 8192 --disk-size 50g

# Kind (Kubernetes in Docker)
kind create cluster --name neuropredict

# k3s (سبک‌وزن)
curl -sfL https://get.k3s.io | sh -
```

### تأیید اتصال به Cluster

```bash
# بررسی اتصال
kubectl cluster-info

# مشاهده nodes
kubectl get nodes

# بررسی context فعلی
kubectl config current-context
```

---

## معماری

### نمای کلی معماری

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │ Ingress │ (NGINX + TLS)
                    │Controller│
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐      ┌───▼────┐     ┌────▼────┐
   │Frontend │      │Backend │     │  Admin  │
   │ (React) │      │(FastAPI)│    │Dashboard│
   └─────────┘      └───┬────┘     └─────────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
       ┌────▼───┐  ┌───▼────┐ ┌───▼────┐
       │Postgres│  │ Redis  │ │  ML    │
       │   DB   │  │ Cache  │ │ Models │
       └────────┘  └────────┘ └────────┘
```

### Components

| Component | Replicas | Resources | Storage |
|-----------|----------|-----------|---------|
| Backend | 3-10 (HPA) | 500m-2 CPU, 1-4Gi RAM | - |
| Frontend | 2 | 100m-500m CPU, 256-512Mi RAM | - |
| Admin | 2 | 100m-500m CPU, 256-512Mi RAM | - |
| PostgreSQL | 1 | 500m-2 CPU, 1-4Gi RAM | 50Gi |
| Redis | 1 | 100m-500m CPU, 256Mi-1Gi RAM | 10Gi |
| Prometheus | 1 | 500m-1 CPU, 512Mi-1Gi RAM | 30d retention |
| Grafana | 1 | 250m-500m CPU, 256-512Mi RAM | - |

---

## راه‌اندازی اولیه

### 1. ساخت Docker Images

```bash
# Backend
cd backend
docker build -t neuropredict/backend:latest .
docker push neuropredict/backend:latest

# Frontend
cd ../frontend
docker build -t neuropredict/frontend:latest .
docker push neuropredict/frontend:latest

# Admin Dashboard
cd ../admin-dashboard
docker build -t neuropredict/admin-dashboard:latest .
docker push neuropredict/admin-dashboard:latest
```

### 2. ایجاد Secrets

```bash
# ایجاد فایل .env.production
cat > .env.production << 'EOF'
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/neuropredict_db
DATABASE_URL_SYNC=postgresql://user:password@postgres:5432/neuropredict_db
POSTGRES_USER=neuropredict_user
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE
SECRET_KEY=YOUR_SECRET_KEY_MIN_32_CHARS
JWT_SECRET_KEY=YOUR_JWT_SECRET_KEY
REDIS_PASSWORD=REDIS_PASSWORD_HERE
SMTP_PASSWORD=SMTP_PASSWORD_HERE
GRAFANA_ADMIN_PASSWORD=GRAFANA_PASSWORD_HERE
EOF

# ایجاد secret در Kubernetes
kubectl create secret generic neuropredict-secrets \
  --from-env-file=.env.production \
  --namespace=neuropredict

# حذف فایل محلی برای امنیت
rm .env.production
```

### 3. پیکربندی Storage

```bash
# برای cloud providers، storage class به صورت خودکار ایجاد می‌شود
# برای on-premise، باید NFS یا storage solution دیگری راه‌اندازی کنید

# مثال: نصب NFS provisioner
helm repo add nfs-subdir-external-provisioner \
  https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
  
helm install nfs-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
  --set nfs.server=YOUR_NFS_SERVER \
  --set nfs.path=/exported/path
```

---

## استقرار

### روش 1: استفاده از اسکریپت خودکار (توصیه می‌شود)

```bash
cd infra/k8s

# استقرار کامل
./deploy.sh deploy

# Dry run (بدون اعمال تغییرات)
DRY_RUN=true ./deploy.sh deploy

# استقرار در محیط مشخص
ENVIRONMENT=staging NAMESPACE=neuropredict-staging ./deploy.sh deploy
```

### روش 2: استقرار دستی مرحله به مرحله

#### مرحله 1: ایجاد Namespaces

```bash
kubectl apply -f namespace.yaml
```

#### مرحله 2: ایجاد ConfigMaps و Secrets

```bash
kubectl apply -f configmaps.yaml

# Secrets (از قسمت قبل)
kubectl create secret generic neuropredict-secrets \
  --from-env-file=.env.production \
  --namespace=neuropredict
```

#### مرحله 3: استقرار Storage

```bash
kubectl apply -f persistentvolumes.yaml

# بررسی PVCs
kubectl get pvc -n neuropredict
```

#### مرحله 4: استقرار Database

```bash
kubectl apply -f postgres-statefulset.yaml

# انتظار برای آماده شدن
kubectl wait --for=condition=ready pod -l app=postgres \
  -n neuropredict --timeout=300s

# بررسی logs
kubectl logs -f statefulset/postgres -n neuropredict
```

#### مرحله 5: استقرار Redis

```bash
kubectl apply -f redis-deployment.yaml

# بررسی وضعیت
kubectl get pods -l app=redis -n neuropredict
```

#### مرحله 6: اجرای Migration

```bash
# ایجاد Job برای migration
kubectl create job db-migration --from=cronjob/db-migration-cron \
  -n neuropredict || \
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
  namespace: neuropredict
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: neuropredict/backend:latest
        command: ["alembic", "upgrade", "head"]
        envFrom:
          - configMapRef:
              name: neuropredict-backend-config
          - secretRef:
              name: neuropredict-secrets
      restartPolicy: OnFailure
EOF

# مشاهده logs
kubectl logs job/db-migration -n neuropredict
```

#### مرحله 7: استقرار Backend

```bash
kubectl apply -f backend-deployment.yaml

# انتظار برای آماده شدن
kubectl wait --for=condition=available \
  deployment/neuropredict-backend \
  -n neuropredict --timeout=300s

# بررسی وضعیت
kubectl get deployment neuropredict-backend -n neuropredict
kubectl get pods -l tier=backend -n neuropredict
```

#### مرحله 8: استقرار Frontend

```bash
kubectl apply -f frontend-deployment.yaml

# بررسی وضعیت
kubectl get deployments -n neuropredict
```

#### مرحله 9: پیکربندی Network Policies

```bash
kubectl apply -f network-policies.yaml

# مشاهده network policies
kubectl get networkpolicies -n neuropredict
```

#### مرحله 10: استقرار Ingress

```bash
# نصب NGINX Ingress Controller (اگر نصب نشده)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --create-namespace \
  --namespace ingress-nginx

# نصب cert-manager برای TLS
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# اعمال Ingress
kubectl apply -f ingress.yaml

# دریافت IP یا Hostname
kubectl get ingress -n neuropredict
```

---

## مانیتورینگ

### نصب Prometheus + Grafana

```bash
# استفاده از Prometheus Operator
helm repo add prometheus-community \
  https://prometheus-community.github.io/helm-charts
helm repo update

# نصب kube-prometheus-stack
helm install prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace neuropredict-monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi \
  --set grafana.adminPassword='STRONG_PASSWORD'

# Port forwarding برای دسترسی محلی
kubectl port-forward -n neuropredict-monitoring \
  svc/prometheus-stack-grafana 3000:80
```

### دسترسی به Dashboards

```bash
# Grafana
kubectl port-forward -n neuropredict-monitoring \
  svc/prometheus-stack-grafana 3000:80
# باز کردن: http://localhost:3000
# username: admin
# password: STRONG_PASSWORD

# Prometheus
kubectl port-forward -n neuropredict-monitoring \
  svc/prometheus-stack-kube-prom-prometheus 9090:9090
# باز کردن: http://localhost:9090
```

---

## امنیت

### 1. RBAC Configuration

```yaml
# ایجاد Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: neuropredict-backend
  namespace: neuropredict

---
# ایجاد Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: neuropredict-backend-role
  namespace: neuropredict
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list"]

---
# RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: neuropredict-backend-binding
  namespace: neuropredict
subjects:
  - kind: ServiceAccount
    name: neuropredict-backend
roleRef:
  kind: Role
  name: neuropredict-backend-role
  apiGroup: rbac.authorization.k8s.io
```

### 2. Pod Security Standards

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: neuropredict
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 3. Network Policies

همه network policies در فایل `network-policies.yaml` تعریف شده‌اند.

### 4. Secrets Management

برای Production، استفاده از Sealed Secrets یا External Secrets Operator توصیه می‌شود:

```bash
# نصب Sealed Secrets
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# استفاده
kubeseal --format yaml < secrets-template.yaml > sealed-secrets.yaml
kubectl apply -f sealed-secrets.yaml
```

---

## عیب‌یابی

### دستورات مفید

```bash
# مشاهده وضعیت کلی
kubectl get all -n neuropredict

# بررسی logs
kubectl logs -f deployment/neuropredict-backend -n neuropredict
kubectl logs -f pod/POD_NAME -n neuropredict --previous

# دسترسی به shell در pod
kubectl exec -it deployment/neuropredict-backend -n neuropredict -- /bin/bash

# توضیح مشکلات pod
kubectl describe pod POD_NAME -n neuropredict

# مشاهده events
kubectl get events -n neuropredict --sort-by='.lastTimestamp'

# بررسی resource usage
kubectl top pods -n neuropredict
kubectl top nodes
```

### مشکلات رایج

#### 1. Pod در حالت Pending

```bash
# بررسی دلیل
kubectl describe pod POD_NAME -n neuropredict

# احتمالاً:
# - منابع کافی نیست: افزایش nodes یا کاهش resource requests
# - PVC mount نمی‌شود: بررسی storage class و provisioner
```

#### 2. Pod در حالت CrashLoopBackOff

```bash
# مشاهده logs
kubectl logs POD_NAME -n neuropredict --previous

# احتمالاً:
# - اتصال به database برقرار نمی‌شود
# - secrets به درستی تنظیم نشده
# - environment variables مقداردهی نشده
```

#### 3. Service دسترسی ندارد

```bash
# بررسی service
kubectl get svc -n neuropredict
kubectl describe svc SERVICE_NAME -n neuropredict

# بررسی endpoints
kubectl get endpoints SERVICE_NAME -n neuropredict

# test connectivity
kubectl run test-pod --image=busybox -it --rm -- \
  wget -O- http://SERVICE_NAME.neuropredict.svc.cluster.local:PORT
```

#### 4. مشکلات Database

```bash
# اتصال مستقیم به database
kubectl exec -it statefulset/postgres -n neuropredict -- psql -U postgres

# backup database
kubectl exec statefulset/postgres -n neuropredict -- \
  pg_dump -U postgres neuropredict_db > backup.sql

# restore database
kubectl exec -i statefulset/postgres -n neuropredict -- \
  psql -U postgres neuropredict_db < backup.sql
```

---

## به‌روزرسانی

### Rolling Update

```bash
# به‌روزرسانی image
kubectl set image deployment/neuropredict-backend \
  backend=neuropredict/backend:v2.0.0 \
  -n neuropredict

# مشاهده وضعیت rollout
kubectl rollout status deployment/neuropredict-backend -n neuropredict

# rollback در صورت مشکل
kubectl rollout undo deployment/neuropredict-backend -n neuropredict
```

### Blue-Green Deployment

```bash
# ایجاد deployment جدید (green)
kubectl apply -f backend-deployment-v2.yaml

# تغییر service به version جدید
kubectl patch service backend -n neuropredict \
  -p '{"spec":{"selector":{"version":"v2"}}}'

# در صورت مشکل، برگشت به version قبلی
kubectl patch service backend -n neuropredict \
  -p '{"spec":{"selector":{"version":"v1"}}}'
```

---

## Scaling

### Manual Scaling

```bash
# افزایش replicas
kubectl scale deployment/neuropredict-backend --replicas=5 -n neuropredict

# کاهش replicas
kubectl scale deployment/neuropredict-backend --replicas=2 -n neuropredict
```

### Auto Scaling (HPA)

HPA در فایل `backend-deployment.yaml` تعریف شده است.

```bash
# مشاهده وضعیت HPA
kubectl get hpa -n neuropredict

# توضیحات HPA
kubectl describe hpa neuropredict-backend-hpa -n neuropredict

# تست auto scaling با load
kubectl run -it --rm load-generator --image=busybox -n neuropredict -- \
  /bin/sh -c "while true; do wget -q -O- http://backend:8000/health; done"
```

---

## Backup & Restore

### Database Backup

```bash
# Automated backup with CronJob
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: neuropredict
spec:
  schedule: "0 2 * * *"  # هر روز ساعت 2 صبح
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -U postgres neuropredict_db | \
              gzip > /backups/backup-\$(date +%Y%m%d-%H%M%S).sql.gz
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: neuropredict-secrets
                  key: POSTGRES_PASSWORD
            volumeMounts:
            - name: backups
              mountPath: /backups
          restartPolicy: OnFailure
          volumes:
          - name: backups
            persistentVolumeClaim:
              claimName: postgres-backups-pvc
EOF
```

---

## منابع اضافی

### Documentation
- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Prometheus Operator](https://prometheus-operator.dev/)
- [Helm Charts](https://helm.sh/docs/)

### Tools
- [K9s - Kubernetes CLI](https://k9scli.io/)
- [Lens - Kubernetes IDE](https://k8slens.dev/)
- [Kubectx/Kubens](https://github.com/ahmetb/kubectx)

---

## پشتیبانی

برای سوالات و مشکلات:
- Email: devops@neuropredict.ai
- Slack: #kubernetes-support
- Documentation: https://docs.neuropredict.ai

---

**Document Version**: 1.0.0  
**Last Updated**: November 2025  
**Classification**: Internal Use Only

