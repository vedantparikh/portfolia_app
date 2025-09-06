"""Add missing database fields for enhanced functionality

Revision ID: 20250104000003
Revises: 20250104000002
Create Date: 2025-01-04 00:00:03.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '20250104000003'
down_revision = '20250104000002'
branch_labels = None
depends_on = None


def upgrade():
    # Add market cap and other financial metrics to assets
    op.add_column('assets', sa.Column('market_cap', sa.Numeric(20, 2), nullable=True))
    op.add_column('assets', sa.Column('pe_ratio', sa.Numeric(10, 4), nullable=True))
    op.add_column('assets', sa.Column('pb_ratio', sa.Numeric(10, 4), nullable=True))
    op.add_column('assets', sa.Column('dividend_yield', sa.Numeric(10, 4), nullable=True))
    op.add_column('assets', sa.Column('eps', sa.Numeric(10, 4), nullable=True))
    op.add_column('assets', sa.Column('book_value', sa.Numeric(10, 4), nullable=True))
    op.add_column('assets', sa.Column('shares_outstanding', sa.Numeric(20, 0), nullable=True))
    
    # Add portfolio settings
    op.add_column('portfolios', sa.Column('target_return', sa.Numeric(10, 4), nullable=True))
    op.add_column('portfolios', sa.Column('max_volatility', sa.Numeric(10, 4), nullable=True))
    op.add_column('portfolios', sa.Column('rebalance_frequency', sa.String(20), nullable=True))
    op.add_column('portfolios', sa.Column('last_rebalance', sa.DateTime(timezone=True), nullable=True))
    op.add_column('portfolios', sa.Column('benchmark_id', sa.Integer(), nullable=True))
    
    # Add foreign key for benchmark
    op.create_foreign_key('fk_portfolios_benchmark', 'portfolios', 'assets', ['benchmark_id'], ['id'])
    
    # Add indexes for new fields
    op.create_index('idx_assets_market_cap', 'assets', ['market_cap'])
    op.create_index('idx_assets_pe_ratio', 'assets', ['pe_ratio'])
    op.create_index('idx_assets_dividend_yield', 'assets', ['dividend_yield'])
    op.create_index('idx_portfolios_benchmark', 'portfolios', ['benchmark_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_assets_market_cap', 'assets')
    op.drop_index('idx_assets_pe_ratio', 'assets')
    op.drop_index('idx_assets_dividend_yield', 'assets')
    op.drop_index('idx_portfolios_benchmark', 'portfolios')
    
    # Drop foreign key
    op.drop_constraint('fk_portfolios_benchmark', 'portfolios', type_='foreignkey')
    
    # Drop columns
    op.drop_column('portfolios', 'benchmark_id')
    op.drop_column('portfolios', 'last_rebalance')
    op.drop_column('portfolios', 'rebalance_frequency')
    op.drop_column('portfolios', 'max_volatility')
    op.drop_column('portfolios', 'target_return')
    
    op.drop_column('assets', 'shares_outstanding')
    op.drop_column('assets', 'book_value')
    op.drop_column('assets', 'eps')
    op.drop_column('assets', 'dividend_yield')
    op.drop_column('assets', 'pb_ratio')
    op.drop_column('assets', 'pe_ratio')
    op.drop_column('assets', 'market_cap')
