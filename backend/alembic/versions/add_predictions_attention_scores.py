"""Add attention_scores column to predictions (explainability per modality)

Revision ID: add_predictions_attention_scores
Revises: add_predictions_patient_created_idx
Create Date: 2025-01-31

"""
from alembic import op
import sqlalchemy as sa


revision = "add_predictions_attention_scores"
down_revision = "add_predictions_patient_created_idx"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "predictions",
        sa.Column("attention_scores", sa.JSON(), nullable=True),
    )


def downgrade():
    op.drop_column("predictions", "attention_scores")
