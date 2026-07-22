# Kubernetes Deployment - NeuroPredict-AI

> **Canonical manifests live in [`infra/k8s/`](../infra/k8s/).**  
> This root `k8s/` directory is **legacy / deprecated**. Prefer `infra/k8s` for
> all new work, CD dry-runs, and production planning.
>
> Frontend and admin-dashboard Deployments/Services are defined under
> `infra/k8s/frontend-deployment.yaml` and
> `infra/k8s/admin-dashboard-deployment.yaml`.

## Legacy tree (this folder)

```
k8s/   ← DEPRECATED
├── namespace.yaml
├── configmap.yaml
├── secrets.yaml.example
├── deployment-backend.yaml
├── deployment-database.yaml
├── ingress.yaml
└── pdb.yaml
```

## Canonical tree

```
infra/k8s/
├── namespace.yaml
├── configmaps.yaml
├── secrets-template.yaml
├── postgres-statefulset.yaml
├── redis-deployment.yaml
├── backend-deployment.yaml
├── frontend-deployment.yaml      # clinical UI
├── admin-dashboard-deployment.yaml
├── ingress.yaml
├── network-policies.yaml
├── persistentvolumes.yaml
└── deploy.sh
```

## استقرار (canonical)

```bash
cd infra/k8s
kubectl apply -f namespace.yaml
# create secrets from secrets-template.yaml / sealed-secrets / external secrets
kubectl apply -f configmaps.yaml
kubectl apply -f postgres-statefulset.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f admin-dashboard-deployment.yaml
kubectl apply -f ingress.yaml
```

Client dry-run (used by gated CD):

```bash
kubectl apply --dry-run=client -f infra/k8s/
```

## Migration note

Do not add new manifests here. If something only exists under `k8s/`, port it
to `infra/k8s/` and update CD workflows.

## منابع بیشتر

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Production Deployment Guide](../docs/PRODUCTION_DEPLOYMENT.md)
- [Product maturity assessment](../docs/PRODUCT_MATURITY_ASSESSMENT_FA.md)
