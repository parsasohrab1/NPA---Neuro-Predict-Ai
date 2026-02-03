"""Add clinical_explanation column to predictions (clinical explainability)

Revision ID: add_predictions_clinical_explanation
Revises: add_predictions_attention_scores
Create Date: 2025-02-03

"""
from alembic import op
import sqlalchemy as sa


revision = "add_predictions_clinical_explanation"
down_revision = "add_predictions_attention_scores"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "predictions",
        sa.Column("clinical_explanation", sa.JSON(), nullable=True),
    )


def downgrade():
    op.drop_column("predictions", "clinical_explanation")
