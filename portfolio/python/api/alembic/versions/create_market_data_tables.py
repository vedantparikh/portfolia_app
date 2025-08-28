"""Create market data tables

Revision ID: create_market_data_tables
Revises: f8faaa20f885
Create Date: 2024-01-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "f8faaa20f885"
branch_labels = None
depends_on = None


def upgrade():
    # Create ticker_info table
    op.create_table(
        "ticker_info",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("company_name", sa.String(length=500), nullable=True),
        sa.Column("sector", sa.String(length=100), nullable=True),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("exchange", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create index on symbol
    op.create_index("ix_ticker_info_symbol", "ticker_info", ["symbol"], unique=True)
    op.create_index("ix_ticker_info_id", "ticker_info", ["id"], unique=False)

    # Create market_data table
    op.create_table(
        "market_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("open_price", sa.Float(), nullable=False),
        sa.Column("high_price", sa.Float(), nullable=False),
        sa.Column("low_price", sa.Float(), nullable=False),
        sa.Column("close_price", sa.Float(), nullable=False),
        sa.Column("volume", sa.Integer(), nullable=False),
        sa.Column("adjusted_close", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["ticker_id"],
            ["ticker_info.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes on market_data
    op.create_index("ix_market_data_id", "market_data", ["id"], unique=False)
    op.create_index(
        "ix_market_data_ticker_id", "market_data", ["ticker_id"], unique=False
    )
    op.create_index("ix_market_data_date", "market_data", ["date"], unique=False)
    op.create_index(
        "idx_ticker_date_unique", "market_data", ["ticker_id", "date"], unique=True
    )
    op.create_index(
        "idx_date_ticker", "market_data", ["date", "ticker_id"], unique=False
    )

    # Create data_update_log table
    op.create_table(
        "data_update_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker_symbol", sa.String(length=20), nullable=False),
        sa.Column("operation", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("records_processed", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes on data_update_log
    op.create_index("ix_data_update_log_id", "data_update_log", ["id"], unique=False)
    op.create_index(
        "ix_data_update_log_ticker_symbol",
        "data_update_log",
        ["ticker_symbol"],
        unique=False,
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_index("ix_data_update_log_ticker_symbol", table_name="data_update_log")
    op.drop_index("ix_data_update_log_id", table_name="data_update_log")
    op.drop_table("data_update_log")

    op.drop_index("idx_date_ticker", table_name="market_data")
    op.drop_index("idx_ticker_date_unique", table_name="market_data")
    op.drop_index("ix_market_data_date", table_name="market_data")
    op.drop_index("ix_market_data_ticker_id", table_name="market_data")
    op.drop_index("ix_market_data_id", table_name="market_data")
    op.drop_table("market_data")

    op.drop_index("ix_ticker_info_id", table_name="ticker_info")
    op.drop_index("ix_ticker_info_symbol", table_name="ticker_info")
    op.drop_table("ticker_info")
