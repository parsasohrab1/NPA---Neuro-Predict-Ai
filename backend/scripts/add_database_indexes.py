#!/usr/bin/env python
"""
Script to add database indexes for performance optimization
Run this script after initial database setup to improve query performance
"""
import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add parent directory to path
sys.path.insert(0, '.')

from app.core.config import settings


async def add_indexes():
    """Add indexes to frequently queried columns"""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False
    )
    
    indexes = [
        # Predictions table indexes
        "CREATE INDEX IF NOT EXISTS idx_predictions_patient_id ON predictions(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_predictions_created_by ON predictions(created_by);",
        "CREATE INDEX IF NOT EXISTS idx_predictions_reviewed_by ON predictions(reviewed_by);",
        "CREATE INDEX IF NOT EXISTS idx_predictions_patient_created ON predictions(patient_id, created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_predictions_risk_levels ON predictions(alzheimer_risk_level, parkinson_risk_level);",
        
        # Medical records table indexes
        "CREATE INDEX IF NOT EXISTS idx_medical_records_patient_id ON medical_records(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_medical_records_visit_date ON medical_records(visit_date DESC);",
        "CREATE INDEX IF NOT EXISTS idx_medical_records_patient_visit ON medical_records(patient_id, visit_date DESC);",
        
        # Imaging studies table indexes
        "CREATE INDEX IF NOT EXISTS idx_imaging_studies_medical_record_id ON imaging_studies(medical_record_id);",
        "CREATE INDEX IF NOT EXISTS idx_imaging_studies_study_date ON imaging_studies(study_date DESC);",
        
        # Patients table indexes (additional)
        "CREATE INDEX IF NOT EXISTS idx_patients_assigned_doctor ON patients(assigned_doctor_id);",
        "CREATE INDEX IF NOT EXISTS idx_patients_created_at ON patients(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_patients_gender ON patients(gender);",
        # Composite search-friendly index suggested by docs
        "CREATE INDEX IF NOT EXISTS idx_patients_pid_name ON patients(patient_id, last_name, first_name);",
        
        # Audit logs table indexes
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);",
        
        # Composite indexes for common query patterns
        "CREATE INDEX IF NOT EXISTS idx_predictions_patient_risk ON predictions(patient_id, alzheimer_risk_level, parkinson_risk_level);",
        "CREATE INDEX IF NOT EXISTS idx_medical_records_patient_visit_type ON medical_records(patient_id, visit_type, visit_date DESC);",

        # Products table indexes (filtering/sorting)
        "CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);",
        "CREATE INDEX IF NOT EXISTS idx_products_active_name ON products(is_active, name);",
    ]
    
    async with engine.begin() as conn:
        print("Adding database indexes for performance optimization...")
        for idx_sql in indexes:
            try:
                await conn.execute(text(idx_sql))
                # Extract index name from SQL
                idx_name = idx_sql.split("idx_")[1].split(" ")[0] if "idx_" in idx_sql else "unknown"
                print(f"✅ Created index: {idx_name}")
            except Exception as e:
                # Extract index name from SQL
                idx_name = idx_sql.split("idx_")[1].split(" ")[0] if "idx_" in idx_sql else "unknown"
                print(f"⚠️  Index {idx_name} may already exist or error: {e}")
        
        print("\n✅ Database indexes added successfully!")
        print("Query performance should be significantly improved.")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_indexes())

