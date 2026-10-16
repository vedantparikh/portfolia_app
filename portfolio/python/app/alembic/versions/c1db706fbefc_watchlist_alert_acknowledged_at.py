"""Watchlist alert acknowledged_at

Revision ID: c1db706fbefc
Revises: e97c82868ff5
Create Date: 2026-10-16

"""

import sqlalchemy as sa

from alembic import op

revision = "c1db706fbefc"
down_revision = "e97c82868ff5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "watchlist_alerts",
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("watchlist_alerts", "acknowledged_at")
