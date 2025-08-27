"""Update volume column to BIGINT

Revision ID: update_volume_bigint
Revises: f8faaa20f885
Create Date: 2025-08-27 20:45:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6g7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    """Change volume column from INTEGER to BIGINT."""
    # Change the volume column type from INTEGER to BIGINT
    op.alter_column(
        "market_data",
        "volume",
        existing_type=sa.INTEGER(),
        type_=sa.BIGINT(),
        existing_nullable=False,
    )


def downgrade():
    """Change volume column back from BIGINT to INTEGER."""
    # Change the volume column type back from BIGINT to INTEGER
    op.alter_column(
        "market_data",
        "volume",
        existing_type=sa.BIGINT(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
