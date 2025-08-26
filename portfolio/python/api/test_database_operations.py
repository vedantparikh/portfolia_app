#!/usr/bin/env python3
"""
Test script to verify basic database operations.
"""

import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_context, init_db
from database.models import User, Portfolio, Asset, Transaction, PortfolioAsset
from database.models.asset import AssetType
from database.models.transaction import TransactionType, TransactionStatus
from database.utils import (
    get_user_by_email,
    get_user_portfolios,
    get_portfolio_assets,
    calculate_portfolio_value,
    get_database_stats,
    validate_database_integrity,
)


def test_basic_operations():
    """Test basic database operations."""
    print("🧪 Testing basic database operations...")

    try:
        with get_db_context() as db:
            # Test 1: Create a test user
            print("  📝 Creating test user...")
            test_user = User(
                email="test@example.com",
                username="testuser",
                password_hash="hashed_password_123",
                is_active=True,
                is_verified=True,
            )
            db.add(test_user)
            db.flush()  # Flush to get the ID
            print(f"    ✅ User created with ID: {test_user.id}")

            # Test 2: Create a test portfolio
            print("  📊 Creating test portfolio...")
            test_portfolio = Portfolio(
                user_id=test_user.id,
                name="Test Portfolio",
                description="A test portfolio for testing",
                currency="USD",
                is_active=True,
                is_public=False,
            )
            db.add(test_portfolio)
            db.flush()
            print(f"    ✅ Portfolio created with ID: {test_portfolio.id}")

            # Test 3: Create a test asset
            print("  💰 Creating test asset...")
            test_asset = Asset(
                symbol="AAPL",
                name="Apple Inc.",
                asset_type=AssetType.STOCK,
                exchange="NASDAQ",
                country="US",
                currency="USD",
                sector="Technology",
                is_active=True,
            )
            db.add(test_asset)
            db.flush()
            print(f"    ✅ Asset created with ID: {test_asset.id}")

            # Test 4: Add asset to portfolio
            print("  🔗 Adding asset to portfolio...")
            portfolio_asset = PortfolioAsset(
                portfolio_id=test_portfolio.id,
                asset_id=test_asset.id,
                quantity=100.0,
                cost_basis=150.0,
                cost_basis_total=15000.0,
                current_value=16000.0,
                unrealized_pnl=1000.0,
                unrealized_pnl_percent=6.67,
            )
            db.add(portfolio_asset)
            db.flush()
            print(f"    ✅ Portfolio asset created with ID: {portfolio_asset.id}")

            # Test 5: Create a test transaction
            print("  📈 Creating test transaction...")
            test_transaction = Transaction(
                portfolio_id=test_portfolio.id,
                asset_id=test_asset.id,
                transaction_type=TransactionType.BUY,
                quantity=100.0,
                price=150.0,
                total_amount=15000.0,
                transaction_date=datetime.now(),
                status=TransactionStatus.COMPLETED,
                fees=0.0,
            )
            db.add(test_transaction)
            db.flush()
            print(f"    ✅ Transaction created with ID: {test_transaction.id}")

            # Test 6: Query operations
            print("  🔍 Testing query operations...")

            # Query user by email
            user = get_user_by_email(db, "test@example.com")
            print(f"    ✅ User query: {user.username}")

            # Query user portfolios
            portfolios = get_user_portfolios(db, test_user.id)
            print(f"    ✅ Portfolios query: {len(portfolios)} portfolio(s)")

            # Query portfolio assets
            assets = get_portfolio_assets(db, test_portfolio.id)
            print(f"    ✅ Portfolio assets query: {len(assets)} asset(s)")

            # Calculate portfolio value
            portfolio_value = calculate_portfolio_value(db, test_portfolio.id)
            print(
                f"    ✅ Portfolio value calculation: ${portfolio_value['total_current_value']:,.2f}"
            )

            # Test 7: Database statistics
            print("  📊 Testing database statistics...")
            stats = get_database_stats(db)
            print(f"    ✅ Database stats: {stats}")

            # Test 8: Database integrity
            print("  🔒 Testing database integrity...")
            integrity = validate_database_integrity(db)
            print(f"    ✅ Database integrity: {integrity['valid']}")

            print("\n🎉 All database operations tests passed!")
            return True

    except Exception as e:
        print(f"❌ Database operation test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def cleanup_test_data():
    """Clean up test data."""
    print("\n🧹 Cleaning up test data...")

    try:
        with get_db_context() as db:
            # Delete in reverse order to handle foreign key constraints
            db.query(Transaction).filter(Transaction.portfolio_id == 1).delete()
            db.query(PortfolioAsset).filter(PortfolioAsset.portfolio_id == 1).delete()
            db.query(Asset).filter(Asset.symbol == "AAPL").delete()
            db.query(Portfolio).filter(Portfolio.id == 1).delete()
            db.query(User).filter(User.email == "test@example.com").delete()

            print("    ✅ Test data cleaned up successfully")

    except Exception as e:
        print(f"    ⚠️  Cleanup warning: {e}")


def main():
    """Main test function."""
    print("🚀 Starting Database Operations Test")
    print("=" * 50)

    # Test basic operations
    success = test_basic_operations()

    if success:
        # Clean up test data
        cleanup_test_data()
        print("\n✅ Database operations test completed successfully!")
    else:
        print("\n❌ Database operations test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
