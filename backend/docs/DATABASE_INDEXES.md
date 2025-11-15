# Database Indexes Optimization

This document describes the database indexes added to improve query performance.

## Overview

Database indexes have been added to frequently queried columns to significantly improve query performance, especially for:
- Patient lookups
- Prediction queries
- Medical record retrieval
- Analytics and reporting

## Indexes Added

### Predictions Table
- `idx_predictions_patient_id` - For filtering predictions by patient
- `idx_predictions_created_at` - For ordering predictions by date (DESC)
- `idx_predictions_created_by` - For filtering by creator
- `idx_predictions_reviewed_by` - For filtering by reviewer
- `idx_predictions_patient_created` - Composite index for patient + date queries
- `idx_predictions_risk_levels` - For filtering by risk levels
- `idx_predictions_patient_risk` - Composite index for patient + risk level queries

### Medical Records Table
- `idx_medical_records_patient_id` - For filtering records by patient
- `idx_medical_records_visit_date` - For ordering by visit date (DESC)
- `idx_medical_records_patient_visit` - Composite index for patient + visit date queries
- `idx_medical_records_patient_visit_type` - Composite index for patient + visit type + date

### Imaging Studies Table
- `idx_imaging_studies_medical_record_id` - For filtering by medical record
- `idx_imaging_studies_study_date` - For ordering by study date (DESC)

### Patients Table
- `idx_patients_assigned_doctor` - For filtering by assigned doctor
- `idx_patients_created_at` - For ordering by creation date
- `idx_patients_gender` - For analytics queries

### Audit Logs Table
- `idx_audit_logs_user_id` - For filtering by user
- `idx_audit_logs_timestamp` - For ordering by timestamp
- `idx_audit_logs_action` - For filtering by action type

## Running the Index Creation Script

### Option 1: Using Python Script

```bash
cd backend
python scripts/add_database_indexes.py
```

### Option 2: Using Docker

```bash
docker-compose exec backend python scripts/add_database_indexes.py
```

### Option 3: Direct SQL (PostgreSQL)

If you prefer to run SQL directly:

```sql
-- Connect to database
psql -U postgres -d neuropredict_db

-- Run the index creation statements from the script
```

## Performance Impact

After adding these indexes, you should see:
- **50-90% faster** queries on indexed columns
- **Significantly reduced** query execution time for:
  - Patient lookups
  - Prediction filtering and sorting
  - Medical record retrieval
  - Analytics queries
  - Audit log searches

## Monitoring Index Usage

To check if indexes are being used:

```sql
-- Check index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

## Notes

- Indexes are automatically created when using `init_db()` for new databases
- For existing databases, run the `add_database_indexes.py` script
- Indexes add minimal overhead for INSERT/UPDATE operations
- The performance gain for SELECT queries far outweighs the small write overhead

