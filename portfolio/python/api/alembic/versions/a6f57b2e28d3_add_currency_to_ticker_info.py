"""add_currency_to_ticker_info

Revision ID: a6f57b2e28d3
Revises: b2c3d4e5f6g7
Create Date: 2025-08-29 19:19:40.998575

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a6f57b2e28d3"
down_revision: Union[str, None] = "b2c3d4e5f6g7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add currency column to ticker_info table
    op.add_column("ticker_info", sa.Column("currency", sa.String(20), nullable=True))


def downgrade() -> None:
    # Remove currency column from ticker_info table
    op.drop_column("ticker_info", "currency")
