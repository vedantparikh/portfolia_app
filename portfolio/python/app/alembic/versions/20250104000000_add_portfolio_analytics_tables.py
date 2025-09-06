"""Add portfolio analytics tables

Revision ID: 20250104000000
Revises: 22eb674867a8
Create Date: 2025-01-04 00:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = '20250104000000'
down_revision = '22eb674867a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    performance_metric_type = postgresql.ENUM(
        'TOTAL_RETURN', 'ANNUALIZED_RETURN', 'VOLATILITY', 'SHARPE_RATIO', 
        'SORTINO_RATIO', 'MAX_DRAWDOWN', 'BETA', 'ALPHA', 'INFORMATION_RATIO', 
        'TREYNOR_RATIO', 'CALMAR_RATIO', 'VALUE_AT_RISK', 'CONDITIONAL_VALUE_AT_RISK', 
        'TRACKING_ERROR', 'CORRELATION',
        name='performancemetrictype'
    )
    performance_metric_type.create(op.get_bind())

    risk_level = postgresql.ENUM(
        'VERY_LOW', 'LOW', 'MODERATE', 'HIGH', 'VERY_HIGH',
        name='risklevel'
    )
    risk_level.create(op.get_bind())

    # Create portfolio_performance_history table
    op.create_table('portfolio_performance_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('snapshot_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_value', sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column('total_cost_basis', sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column('total_unrealized_pnl', sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column('total_unrealized_pnl_percent', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('daily_return', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('cumulative_return', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('annualized_return', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('volatility', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('sharpe_ratio', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('max_drawdown', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('var_95', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('var_99', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('beta', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('alpha', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('benchmark_return', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('tracking_error', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('information_ratio', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_portfolio_performance_portfolio_id', 'portfolio_performance_history', ['portfolio_id'])
    op.create_index('idx_portfolio_performance_date', 'portfolio_performance_history', ['snapshot_date'])
    op.create_index('idx_portfolio_performance_portfolio_date', 'portfolio_performance_history', ['portfolio_id', 'snapshot_date'])
    op.create_unique_constraint('uq_portfolio_performance_date', 'portfolio_performance_history', ['portfolio_id', 'snapshot_date'])

    # Create asset_performance_metrics table
    op.create_table('asset_performance_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('calculation_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_price', sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column('price_change', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('price_change_percent', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('sma_20', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('sma_50', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('sma_200', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('ema_12', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('ema_26', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('rsi', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('macd', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('macd_signal', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('macd_histogram', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('stochastic_k', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('stochastic_d', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('bollinger_upper', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('bollinger_middle', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('bollinger_lower', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('atr', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('volume_sma', sa.Numeric(precision=20, scale=0), nullable=True),
        sa.Column('volume_ratio', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('obv', sa.Numeric(precision=20, scale=0), nullable=True),
        sa.Column('volatility_20d', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('volatility_60d', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('volatility_252d', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('beta', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('sharpe_ratio', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('total_return_1m', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('total_return_3m', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('total_return_6m', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('total_return_1y', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('total_return_3y', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('total_return_5y', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_asset_performance_asset_id', 'asset_performance_metrics', ['asset_id'])
    op.create_index('idx_asset_performance_date', 'asset_performance_metrics', ['calculation_date'])
    op.create_index('idx_asset_performance_asset_date', 'asset_performance_metrics', ['asset_id', 'calculation_date'])
    op.create_unique_constraint('uq_asset_performance_date', 'asset_performance_metrics', ['asset_id', 'calculation_date'])

    # Create portfolio_allocations table
    op.create_table('portfolio_allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('target_percentage', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('min_percentage', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('max_percentage', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('rebalance_threshold', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('last_rebalance_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rebalance_frequency', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_portfolio_allocations_portfolio_id', 'portfolio_allocations', ['portfolio_id'])
    op.create_index('idx_portfolio_allocations_asset_id', 'portfolio_allocations', ['asset_id'])
    op.create_index('idx_portfolio_allocations_active', 'portfolio_allocations', ['is_active'])
    op.create_unique_constraint('uq_portfolio_asset_allocation', 'portfolio_allocations', ['portfolio_id', 'asset_id'])

    # Create rebalancing_events table
    op.create_table('rebalancing_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('event_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('trigger_reason', sa.Text(), nullable=True),
        sa.Column('pre_rebalance_value', sa.Numeric(precision=20, scale=4), nullable=False),
        sa.Column('pre_rebalance_allocations', sa.Text(), nullable=True),
        sa.Column('rebalancing_actions', sa.Text(), nullable=True),
        sa.Column('post_rebalance_value', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('post_rebalance_allocations', sa.Text(), nullable=True),
        sa.Column('rebalancing_cost', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('tax_impact', sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('execution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_rebalancing_events_portfolio_id', 'rebalancing_events', ['portfolio_id'])
    op.create_index('idx_rebalancing_events_date', 'rebalancing_events', ['event_date'])
    op.create_index('idx_rebalancing_events_status', 'rebalancing_events', ['status'])

    # Create portfolio_risk_metrics table
    op.create_table('portfolio_risk_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('calculation_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('portfolio_volatility', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('portfolio_beta', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('portfolio_alpha', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('sharpe_ratio', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('sortino_ratio', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('treynor_ratio', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('calmar_ratio', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('max_drawdown', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('max_drawdown_duration', sa.Integer(), nullable=True),
        sa.Column('current_drawdown', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('var_95_1d', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('var_99_1d', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('var_95_1m', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('var_99_1m', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('cvar_95_1d', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('cvar_99_1d', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('risk_level', postgresql.ENUM('VERY_LOW', 'LOW', 'MODERATE', 'HIGH', 'VERY_HIGH', name='risklevel'), nullable=True),
        sa.Column('risk_score', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('concentration_risk', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('effective_number_of_assets', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('diversification_ratio', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('average_correlation', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('max_correlation', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_portfolio_risk_portfolio_id', 'portfolio_risk_metrics', ['portfolio_id'])
    op.create_index('idx_portfolio_risk_date', 'portfolio_risk_metrics', ['calculation_date'])
    op.create_index('idx_portfolio_risk_portfolio_date', 'portfolio_risk_metrics', ['portfolio_id', 'calculation_date'])
    op.create_unique_constraint('uq_portfolio_risk_date', 'portfolio_risk_metrics', ['portfolio_id', 'calculation_date'])

    # Create asset_correlations table
    op.create_table('asset_correlations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset1_id', sa.Integer(), nullable=False),
        sa.Column('asset2_id', sa.Integer(), nullable=False),
        sa.Column('calculation_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('correlation_1m', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('correlation_3m', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('correlation_6m', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('correlation_1y', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('correlation_3y', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('rolling_correlation_20d', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('rolling_correlation_60d', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('p_value', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('is_significant', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['asset1_id'], ['assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['asset2_id'], ['assets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_asset_correlation_asset1', 'asset_correlations', ['asset1_id'])
    op.create_index('idx_asset_correlation_asset2', 'asset_correlations', ['asset2_id'])
    op.create_index('idx_asset_correlation_date', 'asset_correlations', ['calculation_date'])
    op.create_unique_constraint('uq_asset_correlation', 'asset_correlations', ['asset1_id', 'asset2_id', 'calculation_date'])

    # Create portfolio_benchmarks table
    op.create_table('portfolio_benchmarks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('benchmark_asset_id', sa.Integer(), nullable=False),
        sa.Column('benchmark_name', sa.String(length=255), nullable=False),
        sa.Column('benchmark_type', sa.String(length=50), nullable=False),
        sa.Column('tracking_error', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('information_ratio', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('beta', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('alpha', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('excess_return', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('excess_return_percent', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['benchmark_asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_portfolio_benchmarks_portfolio_id', 'portfolio_benchmarks', ['portfolio_id'])
    op.create_index('idx_portfolio_benchmarks_asset_id', 'portfolio_benchmarks', ['benchmark_asset_id'])
    op.create_index('idx_portfolio_benchmarks_active', 'portfolio_benchmarks', ['is_active'])
    op.create_index('idx_portfolio_benchmarks_primary', 'portfolio_benchmarks', ['is_primary'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('portfolio_benchmarks')
    op.drop_table('asset_correlations')
    op.drop_table('portfolio_risk_metrics')
    op.drop_table('rebalancing_events')
    op.drop_table('portfolio_allocations')
    op.drop_table('asset_performance_metrics')
    op.drop_table('portfolio_performance_history')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS risklevel')
    op.execute('DROP TYPE IF EXISTS performancemetrictype')
