# Kubernetes Deployment - NeuroPredict-AI

## ساختار فایل‌ها

```
k8s/
├── namespace.yaml              # Namespace definition
├── configmap.yaml              # Application configuration
├── secrets.yaml.example        # Secrets template
├── deployment-backend.yaml    # Backend deployment
├── deployment-database.yaml   # Database StatefulSet
├── ingress.yaml                # Ingress configuration
└── pdb.yaml                    # Pod Disruption Budget
```

## استقرار

### 1. ایجاد Namespace

```bash
kubectl apply -f namespace.yaml
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

### 3. استقرار سرویس‌ها

```bash
# ConfigMap
kubectl apply -f configmap.yaml

# Database
kubectl apply -f deployment-database.yaml

# Backend
kubectl apply -f deployment-backend.yaml

# Ingress
kubectl apply -f ingress.yaml

# Pod Disruption Budget
kubectl apply -f pdb.yaml
```

### 4. بررسی وضعیت

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

## Scaling

### Manual Scaling

```bash
kubectl scale deployment neuropredict-backend --replicas=5 -n neuropredict-ai
```

### Auto Scaling

HPA به صورت خودکار بر اساس CPU و Memory scaling می‌کند:

```bash
# مشاهده HPA
kubectl get hpa -n neuropredict-ai

# مشاهده metrics
kubectl top pods -n neuropredict-ai
```

## Monitoring

### دسترسی به Metrics

```bash
# Port forward برای Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Port forward برای Grafana
kubectl port-forward -n monitoring svc/grafana 3001:3000
```

## Troubleshooting

### بررسی Logs

```bash
# Pod logs
kubectl logs <pod-name> -n neuropredict-ai

# Previous logs (if pod crashed)
kubectl logs <pod-name> -n neuropredict-ai --previous
```

### بررسی Events

```bash
kubectl get events -n neuropredict-ai --sort-by='.lastTimestamp'
```

### Debug Pod

```bash
# Exec into pod
kubectl exec -it <pod-name> -n neuropredict-ai -- /bin/bash
```

## Backup & Restore

برای backup و restore، از scripts در `backend/scripts/` استفاده کنید:

```bash
# Backup
python scripts/backup_database.py backup

# Restore
python scripts/backup_database.py restore --backup-file <file>
```

## Security

### Network Policies

برای محدود کردن ترافیک شبکه:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: neuropredict-network-policy
  namespace: neuropredict-ai
spec:
  podSelector:
    matchLabels:
      app: neuropredict-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: neuropredict-ai
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: neuropredict-ai
```

## منابع بیشتر

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Production Deployment Guide](../docs/PRODUCTION_DEPLOYMENT.md)

