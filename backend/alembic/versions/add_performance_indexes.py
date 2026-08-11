"""Add performance indexes

Revision ID: add_performance_indexes
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = None  # Update with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    # Patients table indexes
    op.create_index('idx_patients_email', 'patients', ['email'], unique=False)
    op.create_index('idx_patients_date_of_birth', 'patients', ['date_of_birth'], unique=False)
    op.create_index('idx_patients_created_at', 'patients', ['created_at'], unique=False)
    
    # Medical records indexes
    op.create_index('idx_medical_records_patient_id', 'medical_records', ['patient_id'], unique=False)
    op.create_index('idx_medical_records_visit_date', 'medical_records', ['visit_date'], unique=False)
    op.create_index('idx_medical_records_patient_visit', 'medical_records', ['patient_id', 'visit_date'], unique=False)
    
    # Predictions indexes
    # Note: no 'idx_predictions_status' / 'idx_predictions_patient_status' here —
    # the Prediction model has never had a 'status' column, so those two
    # index statements referenced a nonexistent column and would fail on
    # any real database. Left out rather than fixed-forward with a guessed
    # column, since it's unclear what the intended column was.
    op.create_index('idx_predictions_patient_id', 'predictions', ['patient_id'], unique=False)
    op.create_index('idx_predictions_created_at', 'predictions', ['created_at'], unique=False)
    
    # Imaging studies indexes
    # Note: no 'idx_imaging_studies_patient_id' — ImagingStudy links to a
    # patient via medical_record_id, not a direct patient_id column; that
    # index statement referenced a column the model has never had.
    op.create_index('idx_imaging_studies_study_date', 'imaging_studies', ['study_date'], unique=False)
    op.create_index('idx_imaging_studies_modality', 'imaging_studies', ['modality'], unique=False)
    
    # Audit logs indexes
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('idx_audit_logs_timestamp', 'audit_logs', ['timestamp'], unique=False)
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'], unique=False)


def downgrade():
    # Drop indexes in reverse order
    op.drop_index('idx_audit_logs_action', table_name='audit_logs')
    op.drop_index('idx_audit_logs_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_logs_user_id', table_name='audit_logs')
    
    op.drop_index('idx_imaging_studies_modality', table_name='imaging_studies')
    op.drop_index('idx_imaging_studies_study_date', table_name='imaging_studies')
    
    op.drop_index('idx_predictions_created_at', table_name='predictions')
    op.drop_index('idx_predictions_patient_id', table_name='predictions')
    
    op.drop_index('idx_medical_records_patient_visit', table_name='medical_records')
    op.drop_index('idx_medical_records_visit_date', table_name='medical_records')
    op.drop_index('idx_medical_records_patient_id', table_name='medical_records')
    
    op.drop_index('idx_patients_created_at', table_name='patients')
    op.drop_index('idx_patients_date_of_birth', table_name='patients')
    op.drop_index('idx_patients_email', table_name='patients')

