"""Baseline schema

Revision ID: e97c82868ff5
Revises:
Create Date: 2025-10-28 23:20:26.996808

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "e97c82868ff5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "market_indices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
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
    op.create_index(
        "idx_market_indices_active", "market_indices", ["is_active"], unique=False
    )
    op.create_index(
        "idx_market_indices_category", "market_indices", ["category"], unique=False
    )
    op.create_index(
        "idx_market_indices_country", "market_indices", ["country"], unique=False
    )
    op.create_index(
        "idx_market_indices_symbol", "market_indices", ["symbol"], unique=False
    )
    op.create_index(
        op.f("ix_market_indices_id"), "market_indices", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_market_indices_symbol"), "market_indices", ["symbol"], unique=True
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
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
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_users_active", "users", ["is_active"], unique=False)
    op.create_index("idx_users_email", "users", ["email"], unique=False)
    op.create_index("idx_users_username", "users", ["username"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_table(
        "analysis_configurations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("indicators", sa.JSON(), nullable=False),
        sa.Column("chart_settings", sa.JSON(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("usage_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_analysis_configurations_id"),
        "analysis_configurations",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analysis_configurations_user_id"),
        "analysis_configurations",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "asset_type",
            sa.Enum(
                "EQUITY",
                "ETF",
                "BOND",
                "INDEX",
                "CASH",
                "MUTUALFUND",
                "COMMODITY",
                "CRYPTOCURRENCY",
                "REAL_ESTATE",
                "OTHER",
                "FUTURE",
                "OPTION",
                "WARRANT",
                name="assettype",
            ),
            nullable=False,
        ),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("exchange", sa.String(length=100), nullable=True),
        sa.Column("isin", sa.String(length=12), nullable=True),
        sa.Column("cusip", sa.String(length=9), nullable=True),
        sa.Column("sector", sa.String(length=100), nullable=True),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_assets_active", "assets", ["is_active"], unique=False)
    op.create_index("idx_assets_country", "assets", ["country"], unique=False)
    op.create_index("idx_assets_currency", "assets", ["currency"], unique=False)
    op.create_index("idx_assets_exchange", "assets", ["exchange"], unique=False)
    op.create_index("idx_assets_sector", "assets", ["sector"], unique=False)
    op.create_index("idx_assets_symbol", "assets", ["symbol"], unique=False)
    op.create_index("idx_assets_type", "assets", ["asset_type"], unique=False)
    op.create_index("idx_assets_user_id", "assets", ["user_id"], unique=False)
    op.create_index(
        "idx_assets_user_symbol", "assets", ["user_id", "symbol"], unique=True
    )
    op.create_index(op.f("ix_assets_id"), "assets", ["id"], unique=False)
    op.create_index(op.f("ix_assets_symbol"), "assets", ["symbol"], unique=False)
    op.create_table(
        "portfolios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_portfolios_active", "portfolios", ["is_active"], unique=False)
    op.create_index("idx_portfolios_currency", "portfolios", ["currency"], unique=False)
    op.create_index("idx_portfolios_public", "portfolios", ["is_public"], unique=False)
    op.create_index("idx_portfolios_user_id", "portfolios", ["user_id"], unique=False)
    op.create_index(op.f("ix_portfolios_id"), "portfolios", ["id"], unique=False)
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("date_of_birth", sa.DateTime(timezone=True), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("timezone", sa.String(length=50), nullable=False),
        sa.Column("currency_preference", sa.String(length=3), nullable=False),
        sa.Column("language_preference", sa.String(length=10), nullable=False),
        sa.Column("notification_preferences", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        "idx_user_profiles_country", "user_profiles", ["country"], unique=False
    )
    op.create_index(
        "idx_user_profiles_currency",
        "user_profiles",
        ["currency_preference"],
        unique=False,
    )
    op.create_index(
        "idx_user_profiles_user_id", "user_profiles", ["user_id"], unique=False
    )
    op.create_index(op.f("ix_user_profiles_id"), "user_profiles", ["id"], unique=False)
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("refresh_token", sa.String(length=500), nullable=False),
        sa.Column("device_info", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_used",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_user_sessions_active", "user_sessions", ["is_active"], unique=False
    )
    op.create_index(
        "idx_user_sessions_expires_at", "user_sessions", ["expires_at"], unique=False
    )
    op.create_index(
        "idx_user_sessions_session_id", "user_sessions", ["session_id"], unique=False
    )
    op.create_index(
        "idx_user_sessions_user_id", "user_sessions", ["user_id"], unique=False
    )
    op.create_index(op.f("ix_user_sessions_id"), "user_sessions", ["id"], unique=False)
    op.create_index(
        op.f("ix_user_sessions_session_id"),
        "user_sessions",
        ["session_id"],
        unique=True,
    )
    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_watchlist_user_name"),
    )
    op.create_index(
        "idx_watchlists_default", "watchlists", ["is_default"], unique=False
    )
    op.create_index("idx_watchlists_name", "watchlists", ["name"], unique=False)
    op.create_index("idx_watchlists_public", "watchlists", ["is_public"], unique=False)
    op.create_index("idx_watchlists_user_id", "watchlists", ["user_id"], unique=False)
    op.create_index(op.f("ix_watchlists_id"), "watchlists", ["id"], unique=False)
    op.create_table(
        "portfolio_allocations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("portfolio_id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column(
            "target_percentage", sa.Numeric(precision=10, scale=4), nullable=False
        ),
        sa.Column("min_percentage", sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column("max_percentage", sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column(
            "rebalance_threshold", sa.Numeric(precision=10, scale=4), nullable=True
        ),
        sa.Column("last_rebalance_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rebalance_frequency", sa.String(length=20), nullable=True),
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
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "portfolio_id", "asset_id", name="uq_portfolio_asset_allocation"
        ),
    )
    op.create_index(
        "idx_portfolio_allocations_active",
        "portfolio_allocations",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        "idx_portfolio_allocations_asset_id",
        "portfolio_allocations",
        ["asset_id"],
        unique=False,
    )
    op.create_index(
        "idx_portfolio_allocations_portfolio_id",
        "portfolio_allocations",
        ["portfolio_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_portfolio_allocations_id"),
        "portfolio_allocations",
        ["id"],
        unique=False,
    )
    op.create_table(
        "portfolio_assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("portfolio_id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("cost_basis", sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column(
            "cost_basis_total", sa.Numeric(precision=20, scale=4), nullable=False
        ),
        sa.Column("current_value", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("unrealized_pnl", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column(
            "unrealized_pnl_percent", sa.Numeric(precision=10, scale=4), nullable=True
        ),
        sa.Column("realized_pnl", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column(
            "realized_pnl_percent", sa.Numeric(precision=10, scale=4), nullable=True
        ),
        sa.Column("today_pnl", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column(
            "today_pnl_percent", sa.Numeric(precision=10, scale=4), nullable=True
        ),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_portfolio_assets_asset_id", "portfolio_assets", ["asset_id"], unique=False
    )
    op.create_index(
        "idx_portfolio_assets_portfolio_asset",
        "portfolio_assets",
        ["portfolio_id", "asset_id"],
        unique=True,
    )
    op.create_index(
        "idx_portfolio_assets_portfolio_id",
        "portfolio_assets",
        ["portfolio_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_portfolio_assets_id"), "portfolio_assets", ["id"], unique=False
    )
    op.create_table(
        "portfolio_benchmarks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("portfolio_id", sa.Integer(), nullable=False),
        sa.Column("benchmark_asset_id", sa.Integer(), nullable=False),
        sa.Column("benchmark_name", sa.String(length=255), nullable=False),
        sa.Column("benchmark_type", sa.String(length=50), nullable=False),
        sa.Column("tracking_error", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column(
            "information_ratio", sa.Numeric(precision=10, scale=6), nullable=True
        ),
        sa.Column("beta", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("alpha", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("excess_return", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column(
            "excess_return_percent", sa.Numeric(precision=10, scale=4), nullable=True
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
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
            ["benchmark_asset_id"], ["assets.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_portfolio_benchmarks_active",
        "portfolio_benchmarks",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        "idx_portfolio_benchmarks_asset_id",
        "portfolio_benchmarks",
        ["benchmark_asset_id"],
        unique=False,
    )
    op.create_index(
        "idx_portfolio_benchmarks_portfolio_id",
        "portfolio_benchmarks",
        ["portfolio_id"],
        unique=False,
    )
    op.create_index(
        "idx_portfolio_benchmarks_primary",
        "portfolio_benchmarks",
        ["is_primary"],
        unique=False,
    )
    op.create_index(
        op.f("ix_portfolio_benchmarks_id"), "portfolio_benchmarks", ["id"], unique=False
    )
    op.create_table(
        "portfolio_performance_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("portfolio_id", sa.Integer(), nullable=False),
        sa.Column("snapshot_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_value", sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column(
            "total_cost_basis", sa.Numeric(precision=20, scale=4), nullable=False
        ),
        sa.Column(
            "total_unrealized_pnl", sa.Numeric(precision=20, scale=4), nullable=False
        ),
        sa.Column(
            "total_unrealized_pnl_percent",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
        ),
        sa.Column("daily_return", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column(
            "cumulative_return", sa.Numeric(precision=10, scale=6), nullable=True
        ),
        sa.Column(
            "annualized_return", sa.Numeric(precision=10, scale=6), nullable=True
        ),
        sa.Column("volatility", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("sharpe_ratio", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("max_drawdown", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("var_95", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("var_99", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("beta", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("alpha", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("benchmark_return", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("tracking_error", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column(
            "information_ratio", sa.Numeric(precision=10, scale=6), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "portfolio_id", "snapshot_date", name="uq_portfolio_performance_date"
        ),
    )
    op.create_index(
        "idx_portfolio_performance_date",
        "portfolio_performance_history",
        ["snapshot_date"],
        unique=False,
    )
    op.create_index(
        "idx_portfolio_performance_portfolio_date",
        "portfolio_performance_history",
        ["portfolio_id", "snapshot_date"],
        unique=False,
    )
    op.create_index(
        "idx_portfolio_performance_portfolio_id",
        "portfolio_performance_history",
        ["portfolio_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_portfolio_performance_history_id"),
        "portfolio_performance_history",
        ["id"],
        unique=False,
    )
    op.create_table(
        "rebalancing_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("portfolio_id", sa.Integer(), nullable=False),
        sa.Column("event_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("trigger_reason", sa.Text(), nullable=True),
        sa.Column(
            "pre_rebalance_value", sa.Numeric(precision=20, scale=4), nullable=False
        ),
        sa.Column("pre_rebalance_allocations", sa.Text(), nullable=True),
        sa.Column("rebalancing_actions", sa.Text(), nullable=True),
        sa.Column(
            "post_rebalance_value", sa.Numeric(precision=20, scale=4), nullable=True
        ),
        sa.Column("post_rebalance_allocations", sa.Text(), nullable=True),
        sa.Column("rebalancing_cost", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("tax_impact", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("execution_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_rebalancing_events_date",
        "rebalancing_events",
        ["event_date"],
        unique=False,
    )
    op.create_index(
        "idx_rebalancing_events_portfolio_id",
        "rebalancing_events",
        ["portfolio_id"],
        unique=False,
    )
    op.create_index(
        "idx_rebalancing_events_status", "rebalancing_events", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_rebalancing_events_id"), "rebalancing_events", ["id"], unique=False
    )
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("portfolio_id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column(
            "transaction_type",
            sa.Enum(
                "BUY",
                "SELL",
                "DIVIDEND",
                "SPLIT",
                "MERGER",
                "SPIN_OFF",
                "RIGHTS_ISSUE",
                "STOCK_OPTION_EXERCISE",
                "TRANSFER_IN",
                "TRANSFER_OUT",
                "FEE",
                "OTHER",
                name="transactiontype",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING", "COMPLETED", "CANCELLED", "FAILED", name="transactionstatus"
            ),
            nullable=False,
        ),
        sa.Column("quantity", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("price", sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("transaction_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("settlement_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("reference_number", sa.String(length=100), nullable=True),
        sa.Column("fees", sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column("taxes", sa.Numeric(precision=20, scale=4), nullable=False),
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
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_transactions_asset_date",
        "transactions",
        ["asset_id", "transaction_date"],
        unique=False,
    )
    op.create_index(
        "idx_transactions_asset_id", "transactions", ["asset_id"], unique=False
    )
    op.create_index(
        "idx_transactions_date", "transactions", ["transaction_date"], unique=False
    )
    op.create_index(
        "idx_transactions_portfolio_date",
        "transactions",
        ["portfolio_id", "transaction_date"],
        unique=False,
    )
    op.create_index(
        "idx_transactions_portfolio_id", "transactions", ["portfolio_id"], unique=False
    )
    op.create_index("idx_transactions_status", "transactions", ["status"], unique=False)
    op.create_index(
        "idx_transactions_type", "transactions", ["transaction_type"], unique=False
    )
    op.create_index(op.f("ix_transactions_id"), "transactions", ["id"], unique=False)
    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("added_price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column(
            "added_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("current_price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column(
            "price_change_since_added", sa.Numeric(precision=10, scale=2), nullable=True
        ),
        sa.Column(
            "price_change_percent_since_added",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("personal_rating", sa.Integer(), nullable=True),
        sa.Column("investment_thesis", sa.Text(), nullable=True),
        sa.Column("alert_price_high", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("alert_price_low", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column(
            "alert_price_change_percent",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
        ),
        sa.Column("alerts_enabled", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["watchlist_id"], ["watchlists.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("watchlist_id", "symbol", name="uq_watchlist_item_symbol"),
    )
    op.create_index(
        "idx_watchlist_items_added_date",
        "watchlist_items",
        ["added_date"],
        unique=False,
    )
    op.create_index(
        "idx_watchlist_items_alerts_enabled",
        "watchlist_items",
        ["alerts_enabled"],
        unique=False,
    )
    op.create_index(
        "idx_watchlist_items_sort_order",
        "watchlist_items",
        ["sort_order"],
        unique=False,
    )
    op.create_index(
        "idx_watchlist_items_symbol", "watchlist_items", ["symbol"], unique=False
    )
    op.create_index(
        "idx_watchlist_items_watchlist_id",
        "watchlist_items",
        ["watchlist_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_watchlist_items_id"), "watchlist_items", ["id"], unique=False
    )
    op.create_table(
        "manual_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column(
            "entry_method",
            sa.Enum(
                "MANUAL", "PDF_IMPORT", "API_IMPORT", "CSV_IMPORT", name="entrymethod"
            ),
            nullable=False,
        ),
        sa.Column("validation_status", sa.String(length=50), nullable=False),
        sa.Column("validation_notes", sa.Text(), nullable=True),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("import_batch_id", sa.String(length=100), nullable=True),
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
            ["transaction_id"], ["transactions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
    )
    op.create_index(
        "idx_manual_entries_batch", "manual_entries", ["import_batch_id"], unique=False
    )
    op.create_index(
        "idx_manual_entries_method", "manual_entries", ["entry_method"], unique=False
    )
    op.create_index(
        "idx_manual_entries_transaction_id",
        "manual_entries",
        ["transaction_id"],
        unique=False,
    )
    op.create_index(
        "idx_manual_entries_user_id", "manual_entries", ["user_id"], unique=False
    )
    op.create_index(
        "idx_manual_entries_validation",
        "manual_entries",
        ["validation_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_manual_entries_id"), "manual_entries", ["id"], unique=False
    )
    op.create_table(
        "watchlist_alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_item_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("threshold_value", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("condition", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_triggered", sa.Boolean(), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("triggered_value", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("notify_email", sa.Boolean(), nullable=False),
        sa.Column("notify_push", sa.Boolean(), nullable=False),
        sa.Column("notify_sms", sa.Boolean(), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["watchlist_item_id"], ["watchlist_items.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_watchlist_alerts_active", "watchlist_alerts", ["is_active"], unique=False
    )
    op.create_index(
        "idx_watchlist_alerts_item_id",
        "watchlist_alerts",
        ["watchlist_item_id"],
        unique=False,
    )
    op.create_index(
        "idx_watchlist_alerts_triggered",
        "watchlist_alerts",
        ["is_triggered"],
        unique=False,
    )
    op.create_index(
        "idx_watchlist_alerts_type", "watchlist_alerts", ["alert_type"], unique=False
    )
    op.create_index(
        "idx_watchlist_alerts_user_id", "watchlist_alerts", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_watchlist_alerts_id"), "watchlist_alerts", ["id"], unique=False
    )
    op.create_table(
        "watchlist_performance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_item_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("volume", sa.Integer(), nullable=True),
        sa.Column("market_cap", sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column(
            "price_change_since_added", sa.Numeric(precision=10, scale=2), nullable=True
        ),
        sa.Column(
            "price_change_percent_since_added",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
        ),
        sa.Column("days_since_added", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["watchlist_item_id"], ["watchlist_items.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_watchlist_performance_date",
        "watchlist_performance",
        ["date"],
        unique=False,
    )
    op.create_index(
        "idx_watchlist_performance_item_id",
        "watchlist_performance",
        ["watchlist_item_id"],
        unique=False,
    )
    op.create_index(
        "idx_watchlist_performance_price",
        "watchlist_performance",
        ["price"],
        unique=False,
    )
    op.create_index(
        op.f("ix_watchlist_performance_id"),
        "watchlist_performance",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_watchlist_performance_id"), table_name="watchlist_performance"
    )
    op.drop_index("idx_watchlist_performance_price", table_name="watchlist_performance")
    op.drop_index(
        "idx_watchlist_performance_item_id", table_name="watchlist_performance"
    )
    op.drop_index("idx_watchlist_performance_date", table_name="watchlist_performance")
    op.drop_table("watchlist_performance")
    op.drop_index(op.f("ix_watchlist_alerts_id"), table_name="watchlist_alerts")
    op.drop_index("idx_watchlist_alerts_user_id", table_name="watchlist_alerts")
    op.drop_index("idx_watchlist_alerts_type", table_name="watchlist_alerts")
    op.drop_index("idx_watchlist_alerts_triggered", table_name="watchlist_alerts")
    op.drop_index("idx_watchlist_alerts_item_id", table_name="watchlist_alerts")
    op.drop_index("idx_watchlist_alerts_active", table_name="watchlist_alerts")
    op.drop_table("watchlist_alerts")
    op.drop_index(op.f("ix_manual_entries_id"), table_name="manual_entries")
    op.drop_index("idx_manual_entries_validation", table_name="manual_entries")
    op.drop_index("idx_manual_entries_user_id", table_name="manual_entries")
    op.drop_index("idx_manual_entries_transaction_id", table_name="manual_entries")
    op.drop_index("idx_manual_entries_method", table_name="manual_entries")
    op.drop_index("idx_manual_entries_batch", table_name="manual_entries")
    op.drop_table("manual_entries")
    op.drop_index(op.f("ix_watchlist_items_id"), table_name="watchlist_items")
    op.drop_index("idx_watchlist_items_watchlist_id", table_name="watchlist_items")
    op.drop_index("idx_watchlist_items_symbol", table_name="watchlist_items")
    op.drop_index("idx_watchlist_items_sort_order", table_name="watchlist_items")
    op.drop_index("idx_watchlist_items_alerts_enabled", table_name="watchlist_items")
    op.drop_index("idx_watchlist_items_added_date", table_name="watchlist_items")
    op.drop_table("watchlist_items")
    op.drop_index(op.f("ix_transactions_id"), table_name="transactions")
    op.drop_index("idx_transactions_type", table_name="transactions")
    op.drop_index("idx_transactions_status", table_name="transactions")
    op.drop_index("idx_transactions_portfolio_id", table_name="transactions")
    op.drop_index("idx_transactions_portfolio_date", table_name="transactions")
    op.drop_index("idx_transactions_date", table_name="transactions")
    op.drop_index("idx_transactions_asset_id", table_name="transactions")
    op.drop_index("idx_transactions_asset_date", table_name="transactions")
    op.drop_table("transactions")
    op.drop_index(op.f("ix_rebalancing_events_id"), table_name="rebalancing_events")
    op.drop_index("idx_rebalancing_events_status", table_name="rebalancing_events")
    op.drop_index(
        "idx_rebalancing_events_portfolio_id", table_name="rebalancing_events"
    )
    op.drop_index("idx_rebalancing_events_date", table_name="rebalancing_events")
    op.drop_table("rebalancing_events")
    op.drop_index(
        op.f("ix_portfolio_performance_history_id"),
        table_name="portfolio_performance_history",
    )
    op.drop_index(
        "idx_portfolio_performance_portfolio_id",
        table_name="portfolio_performance_history",
    )
    op.drop_index(
        "idx_portfolio_performance_portfolio_date",
        table_name="portfolio_performance_history",
    )
    op.drop_index(
        "idx_portfolio_performance_date", table_name="portfolio_performance_history"
    )
    op.drop_table("portfolio_performance_history")
    op.drop_index(op.f("ix_portfolio_benchmarks_id"), table_name="portfolio_benchmarks")
    op.drop_index("idx_portfolio_benchmarks_primary", table_name="portfolio_benchmarks")
    op.drop_index(
        "idx_portfolio_benchmarks_portfolio_id", table_name="portfolio_benchmarks"
    )
    op.drop_index(
        "idx_portfolio_benchmarks_asset_id", table_name="portfolio_benchmarks"
    )
    op.drop_index("idx_portfolio_benchmarks_active", table_name="portfolio_benchmarks")
    op.drop_table("portfolio_benchmarks")
    op.drop_index(op.f("ix_portfolio_assets_id"), table_name="portfolio_assets")
    op.drop_index("idx_portfolio_assets_portfolio_id", table_name="portfolio_assets")
    op.drop_index("idx_portfolio_assets_portfolio_asset", table_name="portfolio_assets")
    op.drop_index("idx_portfolio_assets_asset_id", table_name="portfolio_assets")
    op.drop_table("portfolio_assets")
    op.drop_index(
        op.f("ix_portfolio_allocations_id"), table_name="portfolio_allocations"
    )
    op.drop_index(
        "idx_portfolio_allocations_portfolio_id", table_name="portfolio_allocations"
    )
    op.drop_index(
        "idx_portfolio_allocations_asset_id", table_name="portfolio_allocations"
    )
    op.drop_index(
        "idx_portfolio_allocations_active", table_name="portfolio_allocations"
    )
    op.drop_table("portfolio_allocations")
    op.drop_index(op.f("ix_watchlists_id"), table_name="watchlists")
    op.drop_index("idx_watchlists_user_id", table_name="watchlists")
    op.drop_index("idx_watchlists_public", table_name="watchlists")
    op.drop_index("idx_watchlists_name", table_name="watchlists")
    op.drop_index("idx_watchlists_default", table_name="watchlists")
    op.drop_table("watchlists")
    op.drop_index(op.f("ix_user_sessions_session_id"), table_name="user_sessions")
    op.drop_index(op.f("ix_user_sessions_id"), table_name="user_sessions")
    op.drop_index("idx_user_sessions_user_id", table_name="user_sessions")
    op.drop_index("idx_user_sessions_session_id", table_name="user_sessions")
    op.drop_index("idx_user_sessions_expires_at", table_name="user_sessions")
    op.drop_index("idx_user_sessions_active", table_name="user_sessions")
    op.drop_table("user_sessions")
    op.drop_index(op.f("ix_user_profiles_id"), table_name="user_profiles")
    op.drop_index("idx_user_profiles_user_id", table_name="user_profiles")
    op.drop_index("idx_user_profiles_currency", table_name="user_profiles")
    op.drop_index("idx_user_profiles_country", table_name="user_profiles")
    op.drop_table("user_profiles")
    op.drop_index(op.f("ix_portfolios_id"), table_name="portfolios")
    op.drop_index("idx_portfolios_user_id", table_name="portfolios")
    op.drop_index("idx_portfolios_public", table_name="portfolios")
    op.drop_index("idx_portfolios_currency", table_name="portfolios")
    op.drop_index("idx_portfolios_active", table_name="portfolios")
    op.drop_table("portfolios")
    op.drop_index(op.f("ix_assets_symbol"), table_name="assets")
    op.drop_index(op.f("ix_assets_id"), table_name="assets")
    op.drop_index("idx_assets_user_symbol", table_name="assets")
    op.drop_index("idx_assets_user_id", table_name="assets")
    op.drop_index("idx_assets_type", table_name="assets")
    op.drop_index("idx_assets_symbol", table_name="assets")
    op.drop_index("idx_assets_sector", table_name="assets")
    op.drop_index("idx_assets_exchange", table_name="assets")
    op.drop_index("idx_assets_currency", table_name="assets")
    op.drop_index("idx_assets_country", table_name="assets")
    op.drop_index("idx_assets_active", table_name="assets")
    op.drop_table("assets")
    op.drop_index(
        op.f("ix_analysis_configurations_user_id"), table_name="analysis_configurations"
    )
    op.drop_index(
        op.f("ix_analysis_configurations_id"), table_name="analysis_configurations"
    )
    op.drop_table("analysis_configurations")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index("idx_users_username", table_name="users")
    op.drop_index("idx_users_email", table_name="users")
    op.drop_index("idx_users_active", table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_market_indices_symbol"), table_name="market_indices")
    op.drop_index(op.f("ix_market_indices_id"), table_name="market_indices")
    op.drop_index("idx_market_indices_symbol", table_name="market_indices")
    op.drop_index("idx_market_indices_country", table_name="market_indices")
    op.drop_index("idx_market_indices_category", table_name="market_indices")
    op.drop_index("idx_market_indices_active", table_name="market_indices")
    op.drop_table("market_indices")
    sa.Enum(name="assettype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="entrymethod").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="transactionstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="transactiontype").drop(op.get_bind(), checkfirst=True)
