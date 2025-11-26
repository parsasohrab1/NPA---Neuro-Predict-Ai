# System Requirements Specification (SRS) Update | به‌روزرسانی مشخصات سیستم

## Project: NeuroPredict-AI - 100,000 Patient Scale
## Version: 2.0.0
## Date: November 26, 2025

---

## 1. Executive Summary | خلاصه اجرایی

NeuroPredict-AI has been **scaled to handle 100,000 patients** with comprehensive medical data, enabling large-scale machine learning training and clinical decision support research.

**سیستم NeuroPredict-AI به ظرفیت 100,000 بیمار ارتقا یافته است.**

---

## 2. System Overview | نمای کلی سیستم

### 2.1 Data Scale | مقیاس داده

| Component | Quantity | Details |
|-----------|----------|---------|
| **Total Patients** | 100,000 | 50k Synthetic + 50k Real-Based |
| **Normal Controls** | 80,000 (80%) | Healthy individuals |
| **Alzheimer's Disease** | 10,000 (10%) | 3k Synthetic + 7k Real |
| **Parkinson's Disease** | 10,000 (10%) | 3k Synthetic + 7k Real |
| **Medical Records** | 100,000 | One per patient |
| **Biomarker Measurements** | 400,000+ | Multiple per patient |
| **MRI Features** | 500,000+ | Multiple metrics per patient |
| **Predictions** | 100,000+ | Risk assessments |

---

## 3. Functional Requirements | الزامات عملکردی

### FR-1: Patient Data Management

#### FR-1.1: Patient Storage
- **Requirement**: System SHALL store 100,000 patient records
- **Implementation**: SQLite/PostgreSQL database with optimized indexing
- **Performance**: Query response < 100ms for single patient
- **Performance**: Query response < 2s for 1000 patients with pagination

#### FR-1.2: Patient Search
- **Requirement**: System SHALL support fast search across 100k patients
- **Search Criteria**: ID, Name, Diagnosis, Age Range, Risk Level
- **Performance**: Full-text search < 500ms
- **Implementation**: Database indexes on key fields

#### FR-1.3: Patient Classification
- **Automatic Classification**: Based on biomarkers, cognitive scores, MRI
- **Categories**: Normal (80%), Alzheimer (10%), Parkinson (10%)
- **Risk Levels**: Low, Medium, High
- **Update Frequency**: Real-time on data change

---

### FR-2: Data Distribution

#### FR-2.1: Synthetic Data (50,000 patients)
- **Normal**: 44,000 (88%)
- **Alzheimer**: 3,000 (6%)
- **Parkinson**: 3,000 (6%)
- **Quality**: Statistically generated, clinically valid patterns
- **Storage**: CSV files in `data/large_dataset/synthetic/`

#### FR-2.2: Real-Based Data (50,000 patients)
- **Normal**: 36,000 (72%)
- **Alzheimer**: 7,000 (14%)
- **Parkinson**: 7,000 (14%)
- **Source Patterns**: OASIS, ADNI, PPMI-inspired
- **Storage**: CSV files in `data/large_dataset/real/`

---

### FR-3: Performance Requirements

#### FR-3.1: Database Performance
- **Single Record Retrieval**: < 50ms
- **Batch Retrieval (100 records)**: < 200ms
- **Batch Retrieval (1000 records)**: < 1s
- **Search Query**: < 500ms
- **Complex Aggregation**: < 2s

#### FR-3.2: API Performance
- **GET /patients**: < 200ms (with pagination)
- **GET /patients/{id}**: < 100ms
- **POST /patients**: < 300ms
- **Load All Data**: < 30 minutes (for 100k records)

#### FR-3.3: Dashboard Performance
- **Initial Load**: < 3s
- **Chart Rendering**: < 1s
- **Data Filtering**: < 500ms
- **Pagination**: < 200ms per page

---

### FR-4: Data Quality Requirements

#### FR-4.1: Completeness
- ✅ 100% patients have demographic data
- ✅ 100% patients have cognitive scores (MMSE, MoCA, Memory, Attention, Executive)
- ✅ 100% patients have biomarkers (Amyloid-beta, Tau, Dopamine, APOE ε4)
- ✅ 100% patients have MRI features (5 key metrics)
- ✅ 100% patients have diagnosis labels

#### FR-4.2: Validity
- ✅ All values within physiologically plausible ranges
- ✅ Correlations match medical knowledge
- ✅ Disease patterns consistent with literature
- ✅ Age distributions appropriate for diseases

#### FR-4.3: Consistency
- ✅ Alzheimer patients have low amyloid-beta + high tau
- ✅ Parkinson patients have low dopamine
- ✅ Normal controls have normal range values
- ✅ Cognitive scores correlate with biomarkers

---

## 4. Non-Functional Requirements | الزامات غیر عملکردی

### NFR-1: Scalability | مقیاس‌پذیری
- **Current**: 100,000 patients
- **Target**: Up to 1,000,000 patients
- **Database**: Support for horizontal scaling
- **API**: Load balancing ready
- **Storage**: ~15GB for 100k patients (CSV)

### NFR-2: Performance | عملکرد
- **Response Time**: 95% of queries < 1s
- **Throughput**: 1000 requests/minute
- **Concurrent Users**: 100 simultaneous users
- **Data Loading**: Batch import of 10k records/minute

### NFR-3: Reliability | قابلیت اطمینان
- **Uptime**: 99.5%
- **Data Integrity**: 100% (ACID transactions)
- **Backup**: Daily automated backups
- **Recovery Time**: < 4 hours

### NFR-4: Security | امنیت
- **Data Privacy**: All synthetic/anonymized data
- **Access Control**: Role-based (Admin, Doctor, Nurse)
- **Audit Logging**: All data access logged
- **Encryption**: TLS for data in transit

---

## 5. Data Model | مدل داده

### 5.1 Patient Entity
```
Patient {
  id: Integer (Primary Key)
  patient_id: String (Unique, Indexed)
  first_name: String
  last_name: String
  date_of_birth: Date
  age: Integer (Calculated)
  gender: Enum(Male, Female, Other)
  education_years: Integer
  email: String
  phone: String
  created_at: DateTime
  updated_at: DateTime
}
```

### 5.2 Medical Record Entity
```
MedicalRecord {
  id: Integer (Primary Key)
  patient_id: Integer (Foreign Key, Indexed)
  visit_date: DateTime
  
  // Cognitive Scores
  mmse_score: Float (0-30)
  moca_score: Float (0-30)
  memory_score: Float (0-100)
  attention_score: Float (0-100)
  executive_function_score: Float (0-100)
  
  // Biomarkers
  amyloid_beta: Float (pg/mL)
  tau_protein: Float (pg/mL)
  dopamine_level: Float (ng/mL)
  apoe_e4_status: Boolean
  
  // MRI Features
  hippocampal_volume: Float (mm³)
  cortical_thickness: Float (mm)
  ventricular_volume: Float (mm³)
  white_matter_hyperintensities: Float
  brain_volume_total: Float (mm³)
  
  diagnosis: Enum(Normal, Alzheimer, Parkinson)
  label: Integer (0=Normal, 1=Alzheimer, 2=Parkinson)
}
```

### 5.3 Prediction Entity
```
Prediction {
  id: Integer (Primary Key)
  patient_id: Integer (Foreign Key, Indexed)
  disease_type: Enum(Alzheimer, Parkinson, Both)
  alzheimer_risk_score: Float (0-1)
  parkinson_risk_score: Float (0-1)
  alzheimer_risk_level: Enum(Low, Medium, High)
  parkinson_risk_level: Enum(Low, Medium, High)
  confidence: Float (0-1)
  created_at: DateTime
}
```

---

## 6. System Architecture | معماری سیستم

### 6.1 Technology Stack

**Backend**:
- Python 3.10+
- FastAPI 0.115+
- SQLAlchemy 2.0+ (ORM)
- SQLite (Development) / PostgreSQL (Production)
- Redis (Caching)

**Frontend**:
- React 18+
- TypeScript 5+
- TailwindCSS 3+
- Recharts (Visualization)
- React Query (Data fetching)

**ML/AI**:
- PyTorch 2.1+
- Scikit-learn 1.3+
- NumPy, Pandas

---

## 7. Database Optimization | بهینه‌سازی دیتابیس

### 7.1 Indexes
```sql
-- Primary Keys (auto-indexed)
CREATE INDEX idx_patients_id ON patients(id);
CREATE INDEX idx_medical_records_id ON medical_records(id);
CREATE INDEX idx_predictions_id ON predictions(id);

-- Foreign Keys
CREATE INDEX idx_medical_records_patient_id ON medical_records(patient_id);
CREATE INDEX idx_predictions_patient_id ON predictions(patient_id);

-- Search Fields
CREATE INDEX idx_patients_patient_id ON patients(patient_id);
CREATE INDEX idx_patients_created_at ON patients(created_at);
CREATE INDEX idx_medical_records_diagnosis ON medical_records(diagnosis);
CREATE INDEX idx_medical_records_visit_date ON medical_records(visit_date);

-- Composite Indexes for common queries
CREATE INDEX idx_patients_diagnosis_created ON medical_records(diagnosis, created_at);
```

### 7.2 Query Optimization
- Use `selectinload` for eager loading relationships
- Implement pagination (limit/offset)
- Cache frequently accessed data (Redis)
- Use connection pooling

---

## 8. API Endpoints | نقاط پایانی API

### 8.1 Patient Management

#### GET /api/v1/patients
**Purpose**: Get list of patients with pagination
**Parameters**:
- `skip`: Integer (default: 0)
- `limit`: Integer (default: 100, max: 1000)
- `search`: String (optional)
- `diagnosis`: Enum (optional filter)
**Performance**: < 200ms
**Response**: Array of Patient objects

#### GET /api/v1/patients/{id}
**Purpose**: Get single patient details
**Performance**: < 100ms
**Response**: Patient object with relationships

#### POST /api/v1/patients/import/csv
**Purpose**: Batch import patients from CSV
**Performance**: ~10,000 records/minute
**Response**: Import statistics

### 8.2 Disease Tracking

#### POST /api/v1/disease-tracking/load-all-datasets
**Purpose**: Load all 100k patients into disease tracking
**Performance**: < 30 minutes for full load
**Response**: Statistics (patients, records, predictions created)

---

## 9. Dashboard Optimization | بهینه‌سازی داشبورد

### 9.1 Pagination
- Default page size: 50 patients
- Maximum page size: 500 patients
- Virtual scrolling for large lists

### 9.2 Data Loading
- Lazy loading for charts
- Progressive data fetching
- Skeleton loaders during fetch

### 9.3 Filtering
- Client-side filtering for < 1000 records
- Server-side filtering for > 1000 records
- Debounced search inputs

### 9.4 Caching
- React Query cache (5 minutes default)
- Redis cache for aggregated data
- Browser localStorage for user preferences

---

## 10. Testing Requirements | الزامات تست

### 10.1 Unit Tests
- ✅ 80%+ code coverage
- ✅ All API endpoints tested
- ✅ All database queries tested
- ✅ All utility functions tested

### 10.2 Integration Tests
- ✅ End-to-end user workflows
- ✅ API integration tests
- ✅ Database integration tests

### 10.3 Performance Tests
- ✅ Load test with 100k records
- ✅ Stress test with 1000 concurrent users
- ✅ Query performance benchmarks

### 10.4 Data Quality Tests
- ✅ Validate all 100k patients
- ✅ Check data consistency
- ✅ Verify distributions match specs

---

## 11. Deployment | استقرار

### 11.1 Development
- SQLite database
- Single server
- Hot reload enabled

### 11.2 Production
- PostgreSQL database (with replication)
- Load balancer
- Multiple application servers
- Redis cluster
- CDN for static assets

---

## 12. Monitoring | نظارت

### 12.1 Metrics
- Request count per endpoint
- Response times (p50, p95, p99)
- Error rates
- Database query times
- Cache hit rates

### 12.2 Alerts
- Response time > 2s
- Error rate > 5%
- Database connections > 80%
- Disk usage > 85%

---

## 13. Future Enhancements | بهبودهای آینده

### 13.1 Phase 2 (Target: Q1 2026)
- Scale to 500,000 patients
- Real-time prediction updates
- Advanced visualization (3D brain models)
- Multi-language support

### 13.2 Phase 3 (Target: Q2 2026)
- Scale to 1,000,000 patients
- Federated learning
- Mobile application
- Clinical trial integration

---

## 14. Acceptance Criteria | معیارهای پذیرش

✅ **100,000 patients** generated and stored
✅ **All patients** have complete medical data
✅ **Distribution** matches specifications (80% Normal, 10% AD, 10% PD)
✅ **API performance** meets requirements (< 1s for most queries)
✅ **Dashboard** loads and displays data correctly
✅ **Search and filter** work across full dataset
✅ **Documentation** updated and complete
✅ **Code committed** to GitHub

---

**Document Version**: 2.0.0  
**Last Updated**: November 26, 2025  
**Status**: ✅ Implemented  
**Next Review**: Q1 2026

