# Docker Production Configuration Guide

این راهنما نحوه استفاده از Docker برای production را توضیح می‌دهد.

## فایل‌های Configuration

### Development
- `docker-compose.yml` - برای development استفاده می‌شود

### Production
- `docker-compose.prod.yml` - تنظیمات production که با `docker-compose.yml` ترکیب می‌شود

## نصب و راه‌اندازی Production

### 1. ایجاد Docker Secrets

قبل از راه‌اندازی، باید secrets را ایجاد کنید:

```bash
# Secret key برای JWT
echo "your-super-secret-key-min-32-characters-long" | docker secret create neuropredict_secret_key -

# Database password
echo "your-secure-database-password" | docker secret create neuropredict_database_password -

# Redis password (اختیاری)
echo "your-redis-password" | docker secret create neuropredict_redis_password -

# Grafana admin password
echo "your-grafana-admin-password" | docker secret create neuropredict_grafana_password -
```

**نکته امنیتی:** هرگز secrets را در git commit نکنید!

### 2. بررسی Secrets

```bash
docker secret ls
```

باید موارد زیر را ببینید:
- `neuropredict_secret_key`
- `neuropredict_database_password`
- `neuropredict_redis_password`
- `neuropredict_grafana_password`

### 3. راه‌اندازی Production Stack

```bash
# راه‌اندازی با production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# مشاهده لاگ‌ها
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# بررسی وضعیت
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

## تفاوت‌های Production vs Development

### 1. Resource Limits

**Development:**
- Backend: 2 CPU, 2GB RAM
- Frontend: 1 CPU, 1GB RAM
- PostgreSQL: 2 CPU, 2GB RAM
- Redis: 1 CPU, 512MB RAM

**Production:**
- Backend: 4 CPU, 4GB RAM (with 4 workers)
- Frontend: 1.5 CPU, 1.5GB RAM
- PostgreSQL: 4 CPU, 4GB RAM (optimized config)
- Redis: 2 CPU, 1GB RAM (with persistence)

### 2. Secrets Management

**Development:**
- استفاده از environment variables مستقیم
- Passwords در `docker-compose.yml`

**Production:**
- استفاده از Docker Secrets
- Secrets در فایل‌های جداگانه
- دسترسی محدود به secrets

### 3. Health Checks

**Production:**
- Intervals طولانی‌تر (30s vs 10s)
- Start period بیشتر برای initialization
- Retries کمتر (3 vs 5)

### 4. Restart Policy

**Production:**
- `on-failure` با delay 5s
- Max attempts: 3
- Window: 120s

## Resource Limits توضیح

### Limits
حداکثر منابعی که container می‌تواند استفاده کند

### Reservations
حداقل منابعی که به container اختصاص داده می‌شود

### مثال برای Backend Production:
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # حداکثر 4 CPU
      memory: 4G       # حداکثر 4GB RAM
    reservations:
      cpus: '1.0'      # حداقل 1 CPU
      memory: 1G       # حداقل 1GB RAM
```

## Health Checks

همه services دارای health check هستند:

### Backend
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 60s  # 60s برای اولین بار
```

### Frontend
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000"]
  interval: 30s
  timeout: 5s
  retries: 3
```

**نکته:** curl باید در Dockerfile نصب شده باشد (✓ انجام شده)

## PostgreSQL Production Configuration

تنظیمات بهینه برای production:
- `max_connections`: 200
- `shared_buffers`: 1GB
- `effective_cache_size`: 3GB
- `maintenance_work_mem`: 256MB
- WAL configuration برای performance بهتر

## Redis Production Configuration

- `maxmemory`: 768MB
- `maxmemory-policy`: allkeys-lru
- `appendonly`: yes (persistence)
- `appendfsync`: everysec

## Monitoring در Production

### Prometheus
- Resource limits: 1 CPU, 1GB RAM
- Metrics collection از تمام services

### Grafana
- Resource limits: 1 CPU, 512MB RAM
- Admin password از secret استفاده می‌کند

## Troubleshooting

### مشکل: Secrets پیدا نمی‌شوند
```bash
# بررسی secrets
docker secret ls

# ایجاد secrets مجدد
docker secret create neuropredict_secret_key < secret_key.txt
```

### مشکل: Resource limits
```bash
# بررسی استفاده از منابع
docker stats

# تنظیم limits در docker-compose.prod.yml
```

### مشکل: Health check failures
```bash
# بررسی health check
docker inspect <container_name> | grep -A 10 Health

# بررسی logs
docker logs <container_name>
```

## Best Practices

1. **Secrets:**
   - هرگز در git commit نکنید
   - از Docker secrets استفاده کنید
   - Rotate secrets به صورت منظم

2. **Resource Limits:**
   - بر اساس workload تنظیم کنید
   - Monitor استفاده از منابع
   - Adjust limits بر اساس نیاز

3. **Health Checks:**
   - مناسب برای هر service تنظیم کنید
   - Start period برای services با initialization طولانی

4. **Backups:**
   - PostgreSQL: daily backups
   - Redis: RDB + AOF
   - Volumes: regular backups

## CI/CD Integration

```yaml
# Example GitHub Actions
- name: Create Docker secrets
  run: |
    echo "${{ secrets.SECRET_KEY }}" | docker secret create neuropredict_secret_key -
    echo "${{ secrets.DB_PASSWORD }}" | docker secret create neuropredict_database_password -

- name: Deploy production stack
  run: |
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## امنیت

1. **Secrets Management:**
   - استفاده از Docker secrets
   - محدود کردن دسترسی
   - Rotation منظم

2. **Network Security:**
   - استفاده از internal networks
   - محدود کردن exposed ports

3. **Image Security:**
   - استفاده از official images
   - Regular updates
   - Scan برای vulnerabilities

## مراجع

- [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/)
- [Docker Compose Override](https://docs.docker.com/compose/extends/)
- [Resource Limits](https://docs.docker.com/compose/compose-file/deploy/#resources)

