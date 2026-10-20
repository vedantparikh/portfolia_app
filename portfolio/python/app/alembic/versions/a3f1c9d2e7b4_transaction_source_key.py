"""Transaction source_key for duplicate-safe imports

Revision ID: a3f1c9d2e7b4
Revises: c1db706fbefc
Create Date: 2026-10-20

"""

import sqlalchemy as sa

from alembic import op

revision = "a3f1c9d2e7b4"
down_revision = "c1db706fbefc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "transactions", sa.Column("source_key", sa.String(length=64), nullable=True)
    )
    op.create_index(
        "uq_transactions_portfolio_source_key",
        "transactions",
        ["portfolio_id", "source_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_transactions_portfolio_source_key", table_name="transactions")
    op.drop_column("transactions", "source_key")
