"""Add erased_at column to patients for PHI erasure tracking

Revision ID: add_patients_erased_at
Revises: add_data_fusion_reports
Create Date: 2026-07-22

"""
from alembic import op
import sqlalchemy as sa


revision = "add_patients_erased_at"
down_revision = "add_data_fusion_001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "patients",
        sa.Column("erased_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_column("patients", "erased_at")
