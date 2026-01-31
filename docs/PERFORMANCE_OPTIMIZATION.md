# راهنمای بهینه‌سازی عملکرد - NeuroPredict-AI

## 📋 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [Database Optimization](#database-optimization)
3. [Caching Strategy](#caching-strategy)
4. [Image Processing Optimization](#image-processing-optimization)
5. [Model Inference Optimization](#model-inference-optimization)
6. [API Response Optimization](#api-response-optimization)
7. [Connection Pooling](#connection-pooling)
8. [Monitoring & Metrics](#monitoring--metrics)

---

## مقدمه

این راهنما بهینه‌سازی‌های عملکردی پیاده‌سازی شده در NeuroPredict-AI را شرح می‌دهد.

### Performance Targets

- ✅ **API Response Time**: < 200ms (95th percentile)
- ✅ **Prediction Latency**: < 3s
- ✅ **Database Query Time**: < 100ms (average)
- ✅ **Image Processing**: < 5s for 100MB
- ✅ **Cache Hit Rate**: > 80%

---

## Database Optimization

### Indexes

Indexes برای بهبود performance queries ایجاد شده‌اند:

```python
# Patients indexes
idx_patients_email
idx_patients_date_of_birth
idx_patients_created_at

# Medical records indexes
idx_medical_records_patient_id
idx_medical_records_visit_date
idx_medical_records_patient_visit (composite)

# Predictions indexes
idx_predictions_patient_id
idx_predictions_created_at
idx_predictions_status
idx_predictions_patient_status (composite)
```

### ایجاد Indexes

```bash
# Via API (requires admin role)
POST /api/v1/optimization/database/indexes

# Via Alembic migration
alembic upgrade add_performance_indexes
```

### Query Optimization

#### Eager Loading

استفاده از eager loading برای جلوگیری از N+1 queries:

```python
from app.services.optimization.query_optimizer import QueryOptimizer

# Get patient with records (optimized)
patient = await QueryOptimizer.get_patient_with_records_optimized(
    session, patient_id, use_cache=True
)
```

#### Pagination

استفاده از pagination برای queries بزرگ:

```python
# Get paginated predictions
result = await QueryOptimizer.get_predictions_paginated(
    session,
    patient_id=123,
    page=1,
    page_size=20,
    use_cache=True
)
```

#### Bulk Operations

استفاده از bulk operations برای multiple records:

```python
# Get multiple patients efficiently
patients = await QueryOptimizer.bulk_get_patients(
    session, [1, 2, 3, 4, 5], use_cache=True
)
```

### Database Analysis

```bash
# Analyze table statistics
GET /api/v1/optimization/database/analyze/{table_name}

# Get slow queries
GET /api/v1/optimization/database/slow-queries?limit=10

# Optimize query
POST /api/v1/optimization/database/optimize-query
{
  "query": "SELECT * FROM patients WHERE ..."
}
```

---

## Caching Strategy

### Cache Service

Cache service با Redis برای بهبود performance:

```python
from app.core.cache import cache_service

# Get from cache
value = await cache_service.get("patient", "123")

# Set in cache
await cache_service.set("patient", "123", patient_data, ttl=300)

# Get or set (cache-aside pattern)
value = await cache_service.get_or_set(
    "patient", "123",
    lambda: fetch_patient_from_db(123),
    ttl=300
)
```

### Cache Keys

**Naming Convention:**
- `patient:{patient_id}` - Patient data
- `patient:full:{patient_id}` - Patient with records
- `prediction:{prediction_id}` - Prediction result
- `predictions:{patient_id}:{page}:{page_size}` - Paginated predictions

### Cache TTL

- **Patient Data**: 300 seconds (5 minutes)
- **Predictions**: 600 seconds (10 minutes)
- **Paginated Results**: 60 seconds (1 minute)
- **System Metrics**: 30 seconds

### Cache Statistics

```bash
# Get cache statistics
GET /api/v1/optimization/cache/stats

# Clear cache
POST /api/v1/optimization/cache/clear?prefix=patient
```

---

## Image Processing Optimization

### Async Processing

استفاده از async processing برای image operations:

```python
from app.services.optimization.image_optimizer import ImageOptimizer

optimizer = ImageOptimizer(max_workers=4)

# Preprocess image asynchronously
processed = await optimizer.preprocess_image_async(
    image,
    normalize=True,
    resize=(256, 256)
)
```

### Batch Processing

پردازش batch برای multiple images:

```python
# Process multiple images in parallel
processed_images = await optimizer.batch_preprocess(
    images,
    normalize=True,
    resize=(256, 256)
)
```

### Image Size Optimization

بهینه‌سازی اندازه تصویر:

```python
# Optimize image size
optimized = optimizer.optimize_image_size(
    image,
    max_dimension=512,
    quality=90
)
```

---

## Model Inference Optimization

### Model Loading

بهینه‌سازی loading مدل:

```python
from app.services.optimization.model_optimizer import ModelOptimizer

optimizer = ModelOptimizer()

# Load model with optimizations
model = optimizer.load_model_optimized(
    "models/alzheimer_model.pth",
    MultiModalNeuralNetwork,
    use_cache=True
)
```

### Batch Inference

استفاده از batch inference:

```python
# Batch prediction
predictions = optimizer.predict_batch(
    model,
    inputs,
    batch_size=32
)
```

### Optimizations Applied

- ✅ Model caching
- ✅ Half precision (FP16) for GPU
- ✅ JIT compilation
- ✅ CUDA optimizations
- ✅ Batch processing

---

## API Response Optimization

### Response Compression

استفاده از compression برای responses بزرگ:

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Pagination

استفاده از pagination برای lists:

```python
# Paginated response
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

### Field Selection

اجازه انتخاب فیلدهای مورد نیاز:

```python
# Select specific fields
GET /api/v1/patients/123?fields=id,name,email
```

---

## Connection Pooling

### Database Connection Pool

```python
# Pool settings
pool_size=20          # Maintain 20 connections
max_overflow=10       # Allow 10 additional connections
pool_timeout=30       # Wait 30s for connection
pool_recycle=3600     # Recycle after 1 hour
pool_pre_ping=True    # Verify connections
```

### Redis Connection

Redis connection با connection pooling:

```python
redis_client = await redis.from_url(
    f"redis://{host}:{port}/{db}",
    max_connections=50
)
```

---

## Monitoring & Metrics

### Performance Metrics

Metrics برای monitoring performance:

- `http_request_duration_seconds` - API response time
- `prediction_duration_seconds` - Prediction latency
- `database_query_duration_seconds` - Query time
- `cache_hits_total` - Cache hit rate
- `cache_misses_total` - Cache miss rate

### Slow Query Monitoring

```bash
# Get slow queries
GET /api/v1/optimization/database/slow-queries
```

### Cache Monitoring

```bash
# Get cache statistics
GET /api/v1/optimization/cache/stats
```

---

## Best Practices

### 1. Use Caching

همیشه از cache برای داده‌های frequently accessed استفاده کنید:

```python
# Good
patient = await cache_service.get_or_set(
    "patient", str(patient_id),
    lambda: fetch_patient(patient_id),
    ttl=300
)
```

### 2. Optimize Queries

از indexes و eager loading استفاده کنید:

```python
# Good - uses eager loading
patient = await QueryOptimizer.get_patient_with_records_optimized(...)

# Bad - N+1 queries
patient = await session.get(Patient, patient_id)
records = await session.execute(select(MedicalRecord).where(...))
```

### 3. Batch Operations

برای multiple operations از batch استفاده کنید:

```python
# Good - batch operation
patients = await QueryOptimizer.bulk_get_patients(session, ids)

# Bad - multiple queries
for id in ids:
    patient = await session.get(Patient, id)
```

### 4. Async Processing

از async برای I/O operations استفاده کنید:

```python
# Good - async
processed = await optimizer.preprocess_image_async(image)

# Bad - blocking
processed = preprocess_image(image)  # Blocks event loop
```

### 5. Connection Pooling

از connection pooling استفاده کنید:

```python
# Configured in db/session.py
pool_size=20
max_overflow=10
```

---

## Performance Testing

### Load Testing

```bash
# Using Locust
locust -f tests/performance/load_test.py
```

### Benchmarking

```bash
# Using pytest-benchmark
pytest tests/performance/ -m performance --benchmark-only
```

---

## Troubleshooting

### مشکل: Slow Database Queries

**راه‌حل:**
1. بررسی indexes
2. استفاده از EXPLAIN ANALYZE
3. بهینه‌سازی query
4. استفاده از eager loading

### مشکل: High Memory Usage

**راه‌حل:**
1. محدود کردن batch size
2. استفاده از streaming برای large datasets
3. Clear model cache
4. Monitor memory usage

### مشکل: Cache Miss Rate High

**راه‌حل:**
1. افزایش TTL
2. بررسی cache keys
3. Pre-warming cache
4. بررسی cache size

---

## منابع بیشتر

- [SQLAlchemy Performance](https://docs.sqlalchemy.org/en/14/faq/performance.html)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [PyTorch Optimization](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)

---

## پشتیبانی

برای سوالات و مشکلات:
- Performance Team: performance@neuropredict-ai.com
- Technical Support: support@neuropredict-ai.com

