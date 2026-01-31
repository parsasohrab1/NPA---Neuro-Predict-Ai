"""Add composite index on predictions (patient_id, created_at)

Revision ID: add_predictions_patient_created_idx
Revises: add_performance_indexes
Create Date: 2025-01-31

"""
from alembic import op


revision = "add_predictions_patient_created_idx"
down_revision = "add_performance_indexes"  # Set to your latest revision if different
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "idx_predictions_patient_created_at",
        "predictions",
        ["patient_id", "created_at"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "idx_predictions_patient_created_at",
        table_name="predictions",
    )
