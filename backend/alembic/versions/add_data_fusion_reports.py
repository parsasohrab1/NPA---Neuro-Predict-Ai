"""Add data fusion reports table

Revision ID: add_data_fusion_001
Revises: 
Create Date: 2024-11-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_data_fusion_001'
down_revision = None  # Update this to the latest migration if needed
branch_labels = None
depends_on = None


def upgrade():
    """Create data_fusion_reports table"""
    op.create_table(
        'data_fusion_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('medical_record_id', sa.Integer(), nullable=True),
        sa.Column('report_version', sa.String(length=20), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        
        # Modality Scores
        sa.Column('cognitive_modality_score', sa.Float(), nullable=False),
        sa.Column('biomarker_modality_score', sa.Float(), nullable=False),
        sa.Column('imaging_modality_score', sa.Float(), nullable=False),
        
        # Confidence Weights
        sa.Column('cognitive_confidence', sa.Float(), nullable=False),
        sa.Column('biomarker_confidence', sa.Float(), nullable=False),
        sa.Column('imaging_confidence', sa.Float(), nullable=False),
        
        # Integrated Fusion
        sa.Column('integrated_fusion_score', sa.Float(), nullable=False),
        sa.Column('fusion_confidence', sa.String(length=20), nullable=False),
        
        # Cross-Modal Correlations
        sa.Column('cognitive_biomarker_correlation', sa.Float(), nullable=False),
        sa.Column('cognitive_imaging_correlation', sa.Float(), nullable=False),
        sa.Column('biomarker_imaging_correlation', sa.Float(), nullable=False),
        sa.Column('cross_modal_consistency_score', sa.Float(), nullable=False),
        sa.Column('has_conflicting_findings', sa.Integer(), nullable=True),
        
        # Alzheimer's Disease Fusion
        sa.Column('alzheimer_fusion_score', sa.Float(), nullable=False),
        sa.Column('alzheimer_confidence', sa.Float(), nullable=False),
        sa.Column('ad_amyloid_tau_concordance', sa.Float(), nullable=False),
        sa.Column('ad_cognitive_biomarker_alignment', sa.Float(), nullable=False),
        sa.Column('ad_hippocampal_correlation', sa.Float(), nullable=False),
        
        # Parkinson's Disease Fusion
        sa.Column('parkinson_fusion_score', sa.Float(), nullable=False),
        sa.Column('parkinson_confidence', sa.Float(), nullable=False),
        sa.Column('pd_dopamine_cognitive_concordance', sa.Float(), nullable=False),
        sa.Column('pd_motor_cognitive_alignment', sa.Float(), nullable=False),
        sa.Column('pd_imaging_biomarker_correlation', sa.Float(), nullable=False),
        
        # Interpretation
        sa.Column('overall_interpretation', sa.String(length=50), nullable=False),
        sa.Column('primary_concern', sa.String(length=100), nullable=True),
        sa.Column('interpretation_confidence', sa.Float(), nullable=False),
        sa.Column('cognitive_evidence', sa.Text(), nullable=True),
        sa.Column('biomarker_evidence', sa.Text(), nullable=True),
        sa.Column('imaging_evidence', sa.Text(), nullable=True),
        
        # Report Sections
        sa.Column('executive_summary', sa.Text(), nullable=False),
        sa.Column('detailed_findings', sa.Text(), nullable=False),
        sa.Column('risk_assessment', sa.Text(), nullable=False),
        sa.Column('recommendations', sa.Text(), nullable=False),
        sa.Column('follow_up_plan', sa.Text(), nullable=True),
        
        # Advanced Analytics
        sa.Column('progression_rate', sa.Float(), nullable=True),
        sa.Column('trajectory_prediction', sa.String(length=50), nullable=True),
        sa.Column('has_outlier_findings', sa.Integer(), nullable=True),
        sa.Column('outlier_description', sa.Text(), nullable=True),
        
        # Data Quality
        sa.Column('data_completeness_score', sa.Float(), nullable=False),
        sa.Column('data_quality_notes', sa.Text(), nullable=True),
        
        # Metadata
        sa.Column('fusion_metadata', sa.JSON(), nullable=True),
        sa.Column('algorithm_version', sa.String(length=20), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['medical_record_id'], ['medical_records.id'], ),
    )
    
    # Create indexes
    op.create_index(op.f('ix_data_fusion_reports_id'), 'data_fusion_reports', ['id'], unique=False)
    op.create_index(op.f('ix_data_fusion_reports_patient_id'), 'data_fusion_reports', ['patient_id'], unique=False)
    op.create_index(op.f('ix_data_fusion_reports_medical_record_id'), 'data_fusion_reports', ['medical_record_id'], unique=False)
    op.create_index(op.f('ix_data_fusion_reports_generated_at'), 'data_fusion_reports', ['generated_at'], unique=False)
    op.create_index(op.f('ix_data_fusion_reports_fusion_score'), 'data_fusion_reports', ['integrated_fusion_score'], unique=False)
    op.create_index(op.f('ix_data_fusion_reports_interpretation'), 'data_fusion_reports', ['overall_interpretation'], unique=False)
    op.create_index(op.f('ix_data_fusion_reports_confidence'), 'data_fusion_reports', ['fusion_confidence'], unique=False)


def downgrade():
    """Drop data_fusion_reports table"""
    op.drop_index(op.f('ix_data_fusion_reports_confidence'), table_name='data_fusion_reports')
    op.drop_index(op.f('ix_data_fusion_reports_interpretation'), table_name='data_fusion_reports')
    op.drop_index(op.f('ix_data_fusion_reports_fusion_score'), table_name='data_fusion_reports')
    op.drop_index(op.f('ix_data_fusion_reports_generated_at'), table_name='data_fusion_reports')
    op.drop_index(op.f('ix_data_fusion_reports_medical_record_id'), table_name='data_fusion_reports')
    op.drop_index(op.f('ix_data_fusion_reports_patient_id'), table_name='data_fusion_reports')
    op.drop_index(op.f('ix_data_fusion_reports_id'), table_name='data_fusion_reports')
    op.drop_table('data_fusion_reports')

