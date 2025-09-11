"""remove_market_data_tables

Revision ID: f1b2d5154794
Revises: a0afe386843f
Create Date: 2025-09-11 01:56:15.679853

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f1b2d5154794"
down_revision = "a0afe386843f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop market data tables - we're switching to yfinance-only approach

    # Drop tables in correct order (respecting foreign key constraints)
    op.drop_table("data_update_log")
    op.drop_table("market_data")
    op.drop_table("asset_prices")
    op.drop_table("ticker_info")


def downgrade() -> None:
    # Recreate the tables if we need to rollback
    # Note: This is a destructive operation, data will be lost

    # Recreate ticker_info table
    op.create_table(
        "ticker_info",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("company_name", sa.String(length=500), nullable=True),
        sa.Column("sector", sa.String(length=100), nullable=True),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("exchange", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("currency", sa.String(length=20), nullable=True),
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
        sa.UniqueConstraint("symbol"),
    )
    op.create_index("ix_ticker_info_id", "ticker_info", ["id"])
    op.create_index("ix_ticker_info_symbol", "ticker_info", ["symbol"])

    # Recreate asset_prices table
    op.create_table(
        "asset_prices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open_price", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("high_price", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("low_price", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("close_price", sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column("volume", sa.Numeric(precision=20, scale=0), nullable=True),
        sa.Column("adjusted_close", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("dividend_amount", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("split_ratio", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_asset_prices_asset_id", "asset_prices", ["asset_id"])
    op.create_index("idx_asset_prices_date", "asset_prices", ["date"])
    op.create_index(
        "idx_asset_prices_asset_date", "asset_prices", ["asset_id", "date"], unique=True
    )
    op.create_index("ix_asset_prices_id", "asset_prices", ["id"])

    # Recreate market_data table
    op.create_table(
        "market_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("open_price", sa.Float(), nullable=False),
        sa.Column("high_price", sa.Float(), nullable=False),
        sa.Column("low_price", sa.Float(), nullable=False),
        sa.Column("close_price", sa.Float(), nullable=False),
        sa.Column("volume", sa.BigInteger(), nullable=False),
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
        sa.ForeignKeyConstraint(["ticker_id"], ["ticker_info.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_ticker_date_unique", "market_data", ["ticker_id", "date"], unique=True
    )
    op.create_index("idx_date_ticker", "market_data", ["date", "ticker_id"])
    op.create_index("ix_market_data_id", "market_data", ["id"])
    op.create_index("ix_market_data_ticker_id", "market_data", ["ticker_id"])
    op.create_index("ix_market_data_date", "market_data", ["date"])

    # Recreate data_update_log table
    op.create_table(
        "data_update_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker_symbol", sa.String(length=20), nullable=False),
        sa.Column("operation", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("records_processed", sa.Integer(), default=0),
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
    op.create_index("ix_data_update_log_id", "data_update_log", ["id"])
    op.create_index(
        "ix_data_update_log_ticker_symbol", "data_update_log", ["ticker_symbol"]
    )
