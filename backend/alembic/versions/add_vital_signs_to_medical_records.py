"""Add vital signs to medical_records (علائم حیاتی و شرایط بالینی)

Revision ID: add_vital_signs_001
Revises: add_predictions_attention_scores
Create Date: 2025-02-01

"""
from alembic import op
import sqlalchemy as sa


revision = "add_vital_signs_001"
down_revision = "add_predictions_attention_scores"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "medical_records",
        sa.Column("blood_pressure_systolic", sa.Float(), nullable=True),
    )
    op.add_column(
        "medical_records",
        sa.Column("blood_pressure_diastolic", sa.Float(), nullable=True),
    )
    op.add_column(
        "medical_records",
        sa.Column("temperature", sa.Float(), nullable=True),
    )
    op.add_column(
        "medical_records",
        sa.Column("heart_rate", sa.Float(), nullable=True),
    )
    op.add_column(
        "medical_records",
        sa.Column("respiratory_rate", sa.Float(), nullable=True),
    )
    op.add_column(
        "medical_records",
        sa.Column("oxygen_saturation", sa.Float(), nullable=True),
    )
    op.add_column(
        "medical_records",
        sa.Column("weight", sa.Float(), nullable=True),
    )
    op.add_column(
        "medical_records",
        sa.Column("height", sa.Float(), nullable=True),
    )
    op.add_column(
        "medical_records",
        sa.Column("bmi", sa.Float(), nullable=True),
    )
    op.add_column(
        "medical_records",
        sa.Column("blood_glucose", sa.Float(), nullable=True),
    )
    op.add_column(
        "medical_records",
        sa.Column("cholesterol_total", sa.Float(), nullable=True),
    )


def downgrade():
    op.drop_column("medical_records", "cholesterol_total")
    op.drop_column("medical_records", "blood_glucose")
    op.drop_column("medical_records", "bmi")
    op.drop_column("medical_records", "height")
    op.drop_column("medical_records", "weight")
    op.drop_column("medical_records", "oxygen_saturation")
    op.drop_column("medical_records", "respiratory_rate")
    op.drop_column("medical_records", "heart_rate")
    op.drop_column("medical_records", "temperature")
    op.drop_column("medical_records", "blood_pressure_diastolic")
    op.drop_column("medical_records", "blood_pressure_systolic")
