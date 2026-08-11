"""merge data_fusion, clinical_explanation, and vital_signs heads

Revision ID: a0b5b1c54f4b
Revises: add_data_fusion_001, add_predictions_clinical_explanation, add_vital_signs_001
Create Date: 2026-08-11 15:15:01.534826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0b5b1c54f4b'
down_revision = ('add_data_fusion_001', 'add_predictions_clinical_explanation', 'add_vital_signs_001')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
