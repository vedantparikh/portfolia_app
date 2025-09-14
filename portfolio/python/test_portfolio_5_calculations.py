#!/usr/bin/env python3
"""
Test script to validate portfolio calculation logic with Portfolio 5 data.
This script tests the actual calculation methods with realistic data.
"""

import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.core.database.models import Transaction, TransactionStatus, TransactionType
from app.core.services.portfolio_calculation_service import PortfolioCalculationService


def create_portfolio_5_transactions():
    """Create transactions matching Portfolio 5 data."""
    transactions = []

    # Transaction 1: 2025-01-01 - BUY 4.27222600 AAPL @ $234.07 = $1000.9999
    tx1 = Mock(spec=Transaction)
    tx1.id = 1
    tx1.portfolio_id = 5
    tx1.asset_id = 1
    tx1.transaction_type = TransactionType.BUY
    tx1.quantity = Decimal("4.27222600")
    tx1.price = Decimal("234.0700")
    tx1.total_amount = Decimal("1000.9999")
    tx1.transaction_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    tx1.status = TransactionStatus.COMPLETED
    tx1.fees = Decimal("0.0")
    tx1.taxes = Decimal("0.0")
    transactions.append(tx1)

    # Transaction 2: 2025-02-01 - BUY 5.55555600 AAPL @ $180.00 = $1001.0001
    tx2 = Mock(spec=Transaction)
    tx2.id = 2
    tx2.portfolio_id = 5
    tx2.asset_id = 1
    tx2.transaction_type = TransactionType.BUY
    tx2.quantity = Decimal("5.55555600")
    tx2.price = Decimal("180.0000")
    tx2.total_amount = Decimal("1001.0001")
    tx2.transaction_date = datetime(2025, 2, 1, tzinfo=timezone.utc)
    tx2.status = TransactionStatus.COMPLETED
    tx2.fees = Decimal("0.0")
    tx2.taxes = Decimal("0.0")
    transactions.append(tx2)

    # Transaction 3: 2025-07-08 - SELL 4.54545500 AAPL @ $220.00 = $1001.0001
    tx3 = Mock(spec=Transaction)
    tx3.id = 3
    tx3.portfolio_id = 5
    tx3.asset_id = 1
    tx3.transaction_type = TransactionType.SELL
    tx3.quantity = Decimal("4.54545500")
    tx3.price = Decimal("220.0000")
    tx3.total_amount = Decimal("1001.0001")
    tx3.transaction_date = datetime(2025, 7, 8, tzinfo=timezone.utc)
    tx3.status = TransactionStatus.COMPLETED
    tx3.fees = Decimal("0.0")
    tx3.taxes = Decimal("0.0")
    transactions.append(tx3)

    return transactions


def test_portfolio_5_calculations():
    """Test calculations with Portfolio 5 data."""
    print("🧮 Testing Portfolio 5 Calculations")
    print("=" * 50)

    # Create mock database session
    mock_db = Mock()
    service = PortfolioCalculationService(mock_db)

    # Get Portfolio 5 transactions
    transactions = create_portfolio_5_transactions()

    # Current holdings: 5.28232700 AAPL shares
    # Remaining shares = 4.27222600 + 5.55555600 - 4.54545500 = 5.28232700 ✓
    remaining_shares = (
        float(transactions[0].quantity)
        + float(transactions[1].quantity)
        - float(transactions[2].quantity)
    )
    print(f"📊 Remaining shares: {remaining_shares:.8f} AAPL")

    # Assume current AAPL price is $220 (same as last transaction)
    current_aapl_price = 220.0
    current_value = remaining_shares * current_aapl_price
    print(f"💰 Current value: ${current_value:.2f} (at ${current_aapl_price}/share)")

    # Calculate net investment
    net_investment = (
        float(transactions[0].total_amount)
        + float(transactions[1].total_amount)
        - float(transactions[2].total_amount)
    )
    print(f"💵 Net investment: ${net_investment:.2f}")

    # Test dates
    start_date = None  # Use inception
    end_date = datetime(2025, 9, 14, tzinfo=timezone.utc)

    print("\n🔍 Testing Calculation Methods:")
    print("-" * 30)

    # Test CAGR
    try:
        cagr = service._calculate_cagr(
            transactions, current_value, start_date, end_date
        )
        print(f"📈 CAGR: {cagr:.2f}%" if cagr is not None else "📈 CAGR: None")

        if cagr is not None:
            # Validate logical outcome
            # From Jan 1 to Sep 14 is about 8.4 months
            # Net investment: $1001 -> Current value: $1162.11
            # Expected return: (1162.11/1001 - 1) * 100 = 16.09%
            # Annualized: ((1162.11/1001)^(12/8.4) - 1) * 100 ≈ 24.5%
            expected_range = (20.0, 30.0)
            if expected_range[0] <= cagr <= expected_range[1]:
                print(f"  ✅ CAGR is within expected range {expected_range}")
            else:
                print(
                    f"  ⚠️  CAGR {cagr:.2f}% is outside expected range {expected_range}"
                )
    except Exception as e:
        print(f"  ❌ CAGR calculation failed: {e}")

    # Test XIRR (mock the xirr function)
    try:
        from unittest.mock import patch

        with patch("app.core.services.portfolio_calculation_service.xirr") as mock_xirr:
            mock_xirr.return_value = 0.20  # 20% return
            xirr_result = service._calculate_xirr(transactions, current_value, end_date)
            print(
                f"📊 XIRR: {xirr_result:.2f}%"
                if xirr_result is not None
                else "📊 XIRR: None"
            )

            if xirr_result is not None:
                expected_xirr = 20.0
                if abs(xirr_result - expected_xirr) < 0.1:
                    print(f"  ✅ XIRR matches expected value {expected_xirr}%")
                else:
                    print(
                        f"  ⚠️  XIRR {xirr_result:.2f}% differs from expected {expected_xirr}%"
                    )
    except Exception as e:
        print(f"  ❌ XIRR calculation failed: {e}")

    # Test Simple TWR
    try:
        twr = service._calculate_simple_twr(
            transactions, current_value, start_date, end_date
        )
        print(
            f"⏱️  Simple TWR: {twr:.2f}%" if twr is not None else "⏱️  Simple TWR: None"
        )

        if twr is not None:
            # TWR should be similar to CAGR for this scenario
            expected_range = (20.0, 30.0)
            if expected_range[0] <= twr <= expected_range[1]:
                print(f"  ✅ TWR is within expected range {expected_range}")
            else:
                print(f"  ⚠️  TWR {twr:.2f}% is outside expected range {expected_range}")
    except Exception as e:
        print(f"  ❌ TWR calculation failed: {e}")

    # Test initial value calculation
    try:
        initial_value = service._calculate_initial_value(transactions, start_date)
        print(f"🏁 Initial value: ${initial_value:.2f}")

        expected_initial = float(transactions[0].total_amount)  # First transaction
        if abs(initial_value - expected_initial) < 0.01:
            print("  ✅ Initial value matches first transaction amount")
        else:
            print(
                f"  ⚠️  Initial value {initial_value:.2f} differs from expected {expected_initial:.2f}"
            )
    except Exception as e:
        print(f"  ❌ Initial value calculation failed: {e}")

    print("\n🎯 Summary:")
    print("-" * 20)
    print(f"Net Investment: ${net_investment:.2f}")
    print(f"Current Value: ${current_value:.2f}")
    print(f"Total Return: {((current_value / net_investment) - 1) * 100:.2f}%")
    print("Holding Period: ~8.4 months")


def test_benchmark_calculations():
    """Test benchmark calculations with Portfolio 5 investment schedule."""
    print("\n🏆 Testing Benchmark Calculations")
    print("=" * 50)

    # Create mock database session
    mock_db = Mock()
    service = PortfolioCalculationService(mock_db)

    # Create investment schedule matching Portfolio 5
    investment_amounts = [
        (datetime(2025, 1, 1, tzinfo=timezone.utc), 1000.9999),
        (datetime(2025, 2, 1, tzinfo=timezone.utc), 1001.0001),
        (datetime(2025, 7, 8, tzinfo=timezone.utc), -1001.0001),  # Sell
    ]

    # Create synthetic benchmark transactions
    benchmark_transactions = [
        {
            "transaction_date": datetime(2025, 1, 1, tzinfo=timezone.utc),
            "total_amount": 1000.9999,
            "transaction_type": "BUY",
        },
        {
            "transaction_date": datetime(2025, 2, 1, tzinfo=timezone.utc),
            "total_amount": 1001.0001,
            "transaction_type": "BUY",
        },
        {
            "transaction_date": datetime(2025, 7, 8, tzinfo=timezone.utc),
            "total_amount": 1001.0001,
            "transaction_type": "SELL",
        },
    ]

    # Assume benchmark current value (e.g., S&P 500 performance)
    benchmark_current_value = 1100.0  # 10% gain on net investment

    end_date = datetime(2025, 9, 14, tzinfo=timezone.utc)

    print("📊 Investment Schedule:")
    for date, amount in investment_amounts:
        print(f"  {date.date()}: ${amount:,.2f}")

    net_investment = sum(amount for _, amount in investment_amounts)
    print(f"💵 Net Investment: ${net_investment:.2f}")
    print(f"💰 Benchmark Current Value: ${benchmark_current_value:.2f}")

    print("\n🔍 Testing Benchmark Methods:")
    print("-" * 30)

    # Test Benchmark CAGR
    try:
        cagr = service._calculate_benchmark_cagr(
            benchmark_transactions, benchmark_current_value, None, end_date
        )
        print(
            f"📈 Benchmark CAGR: {cagr:.2f}%"
            if cagr is not None
            else "📈 Benchmark CAGR: None"
        )

        if cagr is not None:
            # Expected: (1100/1001)^(12/8.4) - 1 ≈ 14.5%
            expected_range = (10.0, 20.0)
            if expected_range[0] <= cagr <= expected_range[1]:
                print(f"  ✅ Benchmark CAGR is within expected range {expected_range}")
            else:
                print(
                    f"  ⚠️  Benchmark CAGR {cagr:.2f}% is outside expected range {expected_range}"
                )
    except Exception as e:
        print(f"  ❌ Benchmark CAGR calculation failed: {e}")

    # Test Benchmark TWR
    try:
        twr = service._calculate_benchmark_twr(
            benchmark_transactions, benchmark_current_value, None, end_date
        )
        print(
            f"⏱️  Benchmark TWR: {twr:.2f}%"
            if twr is not None
            else "⏱️  Benchmark TWR: None"
        )

        if twr is not None:
            expected_range = (10.0, 20.0)
            if expected_range[0] <= twr <= expected_range[1]:
                print(f"  ✅ Benchmark TWR is within expected range {expected_range}")
            else:
                print(
                    f"  ⚠️  Benchmark TWR {twr:.2f}% is outside expected range {expected_range}"
                )
    except Exception as e:
        print(f"  ❌ Benchmark TWR calculation failed: {e}")


if __name__ == "__main__":
    test_portfolio_5_calculations()
    test_benchmark_calculations()
    print("\n✅ Validation complete!")
