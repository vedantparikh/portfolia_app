"""Optimize portfolio and asset database indexes

Revision ID: 20250104000001
Revises: 20250104000000
Create Date: 2025-01-04 00:00:01.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '20250104000001'
down_revision = '20250104000000'
branch_labels = None
depends_on = None


def upgrade():
    # Add composite indexes for common query patterns
    op.create_index('idx_portfolios_user_active', 'portfolios', ['user_id', 'is_active'])
    op.create_index('idx_portfolios_user_public', 'portfolios', ['user_id', 'is_public'])
    op.create_index('idx_portfolios_updated_at', 'portfolios', ['updated_at'])
    
    # Portfolio assets optimization
    op.create_index('idx_portfolio_assets_value', 'portfolio_assets', ['current_value'])
    op.create_index('idx_portfolio_assets_pnl', 'portfolio_assets', ['unrealized_pnl'])
    op.create_index('idx_portfolio_assets_last_updated', 'portfolio_assets', ['last_updated'])
    
    # Asset price optimization
    op.create_index('idx_asset_prices_symbol_date', 'asset_prices', ['asset_id', 'date'])
    op.create_index('idx_asset_prices_date_range', 'asset_prices', ['date', 'asset_id'])
    
    # Transaction optimization
    op.create_index('idx_transactions_portfolio_type', 'transactions', ['portfolio_id', 'transaction_type'])
    op.create_index('idx_transactions_asset_type', 'transactions', ['asset_id', 'transaction_type'])
    op.create_index('idx_transactions_date_range', 'transactions', ['transaction_date', 'portfolio_id'])
    
    # Analytics tables optimization
    op.create_index('idx_performance_portfolio_date', 'portfolio_performance_history', ['portfolio_id', 'snapshot_date'])
    op.create_index('idx_risk_portfolio_date', 'portfolio_risk_metrics', ['portfolio_id', 'calculation_date'])
    op.create_index('idx_asset_metrics_asset_date', 'asset_performance_metrics', ['asset_id', 'calculation_date'])
    
    # Add partial indexes for active records
    op.create_index('idx_assets_active_symbol', 'assets', ['symbol'], postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_portfolios_active_user', 'portfolios', ['user_id'], postgresql_where=sa.text('is_active = true'))


def downgrade():
    # Drop the indexes
    op.drop_index('idx_portfolios_user_active', 'portfolios')
    op.drop_index('idx_portfolios_user_public', 'portfolios')
    op.drop_index('idx_portfolios_updated_at', 'portfolios')
    
    op.drop_index('idx_portfolio_assets_value', 'portfolio_assets')
    op.drop_index('idx_portfolio_assets_pnl', 'portfolio_assets')
    op.drop_index('idx_portfolio_assets_last_updated', 'portfolio_assets')
    
    op.drop_index('idx_asset_prices_symbol_date', 'asset_prices')
    op.drop_index('idx_asset_prices_date_range', 'asset_prices')
    
    op.drop_index('idx_transactions_portfolio_type', 'transactions')
    op.drop_index('idx_transactions_asset_type', 'transactions')
    op.drop_index('idx_transactions_date_range', 'transactions')
    
    op.drop_index('idx_performance_portfolio_date', 'portfolio_performance_history')
    op.drop_index('idx_risk_portfolio_date', 'portfolio_risk_metrics')
    op.drop_index('idx_asset_metrics_asset_date', 'asset_performance_metrics')
    
    op.drop_index('idx_assets_active_symbol', 'assets')
    op.drop_index('idx_portfolios_active_user', 'portfolios')
