"""Add missing database constraints and validations

Revision ID: 20250104000002
Revises: 20250104000001
Create Date: 2025-01-04 00:00:02.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '20250104000002'
down_revision = '20250104000001'
branch_labels = None
depends_on = None


def upgrade():
    # Add check constraints for data validation
    op.create_check_constraint(
        'ck_portfolio_assets_quantity_positive',
        'portfolio_assets',
        'quantity > 0'
    )
    
    op.create_check_constraint(
        'ck_portfolio_assets_cost_basis_positive',
        'portfolio_assets',
        'cost_basis > 0'
    )
    
    op.create_check_constraint(
        'ck_portfolio_assets_cost_basis_total_positive',
        'portfolio_assets',
        'cost_basis_total > 0'
    )
    
    # Transaction constraints
    op.create_check_constraint(
        'ck_transactions_quantity_positive',
        'transactions',
        'quantity > 0'
    )
    
    op.create_check_constraint(
        'ck_transactions_price_positive',
        'transactions',
        'price > 0'
    )
    
    op.create_check_constraint(
        'ck_transactions_total_amount_positive',
        'transactions',
        'total_amount > 0'
    )
    
    # Portfolio allocation constraints
    op.create_check_constraint(
        'ck_portfolio_allocations_target_percentage',
        'portfolio_allocations',
        'target_percentage >= 0 AND target_percentage <= 100'
    )
    
    op.create_check_constraint(
        'ck_portfolio_allocations_min_percentage',
        'portfolio_allocations',
        'min_percentage IS NULL OR (min_percentage >= 0 AND min_percentage <= 100)'
    )
    
    op.create_check_constraint(
        'ck_portfolio_allocations_max_percentage',
        'portfolio_allocations',
        'max_percentage IS NULL OR (max_percentage >= 0 AND max_percentage <= 100)'
    )
    
    # Asset price constraints
    op.create_check_constraint(
        'ck_asset_prices_close_positive',
        'asset_prices',
        'close_price > 0'
    )
    
    op.create_check_constraint(
        'ck_asset_prices_volume_non_negative',
        'asset_prices',
        'volume IS NULL OR volume >= 0'
    )
    
    # Performance metrics constraints
    op.create_check_constraint(
        'ck_performance_history_total_value_positive',
        'portfolio_performance_history',
        'total_value > 0'
    )
    
    op.create_check_constraint(
        'ck_risk_metrics_risk_score_range',
        'portfolio_risk_metrics',
        'risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)'
    )


def downgrade():
    # Drop check constraints
    op.drop_constraint('ck_portfolio_assets_quantity_positive', 'portfolio_assets')
    op.drop_constraint('ck_portfolio_assets_cost_basis_positive', 'portfolio_assets')
    op.drop_constraint('ck_portfolio_assets_cost_basis_total_positive', 'portfolio_assets')
    
    op.drop_constraint('ck_transactions_quantity_positive', 'transactions')
    op.drop_constraint('ck_transactions_price_positive', 'transactions')
    op.drop_constraint('ck_transactions_total_amount_positive', 'transactions')
    
    op.drop_constraint('ck_portfolio_allocations_target_percentage', 'portfolio_allocations')
    op.drop_constraint('ck_portfolio_allocations_min_percentage', 'portfolio_allocations')
    op.drop_constraint('ck_portfolio_allocations_max_percentage', 'portfolio_allocations')
    
    op.drop_constraint('ck_asset_prices_close_positive', 'asset_prices')
    op.drop_constraint('ck_asset_prices_volume_non_negative', 'asset_prices')
    
    op.drop_constraint('ck_performance_history_total_value_positive', 'portfolio_performance_history')
    op.drop_constraint('ck_risk_metrics_risk_score_range', 'portfolio_risk_metrics')
