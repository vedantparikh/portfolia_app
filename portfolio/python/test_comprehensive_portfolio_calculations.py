"""
Comprehensive Unit Tests for Portfolio Calculation Service

This test suite covers all scenarios and edge cases for the portfolio calculation service,
including the logical fixes for CAGR, TWR, XIRR, and benchmark calculations.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pandas as pd
import pytest


# Mock the database models and services
class MockTransaction:
    def __init__(
        self, transaction_date, transaction_type, total_amount, quantity, asset_id
    ) -> None:
        self.transaction_date = transaction_date
        self.transaction_type = transaction_type
        self.total_amount = total_amount
        self.quantity = quantity
        self.asset_id = asset_id


class MockTransactionType:
    BUY = "BUY"
    SELL = "SELL"


class MockPortfolio:
    def __init__(self, id, name, user_id) -> None:
        self.id = id
        self.name = name
        self.user_id = user_id


class MockAsset:
    def __init__(self, id, symbol, name) -> None:
        self.id = id
        self.symbol = symbol
        self.name = name


class MockPortfolioAsset:
    def __init__(self, portfolio_id, asset_id, current_value, cost_basis_total) -> None:
        self.portfolio_id = portfolio_id
        self.asset_id = asset_id
        self.current_value = current_value
        self.cost_basis_total = cost_basis_total


# Mock the imports
import sys
from unittest.mock import MagicMock

# Create mock modules
mock_models = MagicMock()
mock_models.Transaction = MockTransaction
mock_models.TransactionType = MockTransactionType
mock_models.Portfolio = MockPortfolio
mock_models.Asset = MockAsset
mock_models.PortfolioAsset = MockPortfolioAsset

mock_market_service = MagicMock()

sys.modules["app.core.database.models"] = mock_models
sys.modules["app.core.services.market_data_service"] = mock_market_service

# Now import the service
from app.core.services.portfolio_calculation_service import (
    PeriodType,
    PortfolioCalculationService,
)


class TestPortfolioCalculationService:
    """Comprehensive test suite for portfolio calculation service."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.service = PortfolioCalculationService(self.mock_db)

        # Mock the market data service
        self.service.market_data_service = AsyncMock()

        # Common test dates
        self.base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        self.start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        self.end_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

    def create_mock_transactions(
        self, transactions_data: List[Dict[str, Any]]
    ) -> List[MockTransaction]:
        """Create mock transactions from test data."""
        transactions = []
        for data in transactions_data:
            transaction = MockTransaction(
                transaction_date=data["date"],
                transaction_type=data["type"],
                total_amount=data["amount"],
                quantity=data.get(
                    "quantity", data["amount"] / 100
                ),  # Assume $100 per share
                asset_id=data.get("asset_id", 1),
            )
            transactions.append(transaction)
        return transactions

    def create_mock_price_data(
        self, dates: List[datetime], prices: List[float]
    ) -> pd.DataFrame:
        """Create mock price data."""
        return pd.DataFrame(
            {
                "Date": dates,
                "Close": prices,
                "Open": prices,
                "High": [p * 1.05 for p in prices],
                "Low": [p * 0.95 for p in prices],
                "Volume": [1000000] * len(prices),
            }
        )

    # Test 1: Portfolio CAGR Calculation - Fixed Logic
    @pytest.mark.asyncio
    async def test_portfolio_cagr_with_market_values(self) -> None:
        """Test CAGR calculation using actual market values instead of cost basis."""

        # Scenario: Invested $10,000 five years ago, grew to $50,000 by start of last year, now $60,000
        transactions_data = [
            {
                "date": datetime(2019, 1, 1, tzinfo=timezone.utc),
                "type": "BUY",
                "amount": 10000.0,
            },
        ]
        transactions = self.create_mock_transactions(transactions_data)

        # Mock daily portfolio values - showing growth to $50,000 by start of period
        daily_values = pd.DataFrame(
            {
                "Date": [datetime(2023, 1, 1).date()],
                "PortfolioValue": [50000.0],
                "DailyReturn": [0.0],
            }
        )

        # Mock the daily portfolio values calculation
        with patch.object(
            self.service, "_calculate_daily_portfolio_values", return_value=daily_values
        ):
            cagr = await self.service._calculate_cagr(
                portfolio_id=1,
                transactions=transactions,
                current_value=60000.0,
                start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            )

        # Expected: (60000 / 50000) ^ 1 - 1 = 20%
        assert cagr is not None
        assert abs(cagr - 20.0) < 0.01, f"Expected ~20%, got {cagr}%"

    @pytest.mark.asyncio
    async def test_portfolio_cagr_inception_period(self) -> None:
        """Test CAGR calculation for inception period (should use cost basis)."""

        transactions_data = [
            {
                "date": datetime(2023, 1, 1, tzinfo=timezone.utc),
                "type": "BUY",
                "amount": 10000.0,
            },
        ]
        transactions = self.create_mock_transactions(transactions_data)

        cagr = await self.service._calculate_cagr(
            portfolio_id=1,
            transactions=transactions,
            current_value=12000.0,
            start_date=None,  # Inception
            end_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )

        # Expected: (12000 / 10000) ^ (1/1) - 1 = 20%
        assert cagr is not None
        assert abs(cagr - 20.0) < 0.01, f"Expected ~20%, got {cagr}%"

    # Test 2: Benchmark CAGR/TWR - Fixed Net Investment Logic
    def test_benchmark_cagr_correct_net_investment(self) -> None:
        """Test benchmark CAGR with corrected net investment calculation."""

        # Scenario: BUY $1000, SELL $800, current value $300
        benchmark_transactions = [
            {
                "transaction_date": datetime(2023, 1, 1, tzinfo=timezone.utc),
                "total_amount": 1000.0,  # Positive for BUY
                "transaction_type": "BUY",
            },
            {
                "transaction_date": datetime(2023, 6, 1, tzinfo=timezone.utc),
                "total_amount": -800.0,  # Negative for SELL
                "transaction_type": "SELL",
            },
        ]

        cagr = self.service._calculate_benchmark_cagr(
            transactions=benchmark_transactions,
            current_value=300.0,
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )

        # Net investment should be: 1000 + (-800) = 200
        # CAGR should be: (300 / 200) ^ 1 - 1 = 50%
        assert cagr is not None
        assert abs(cagr - 50.0) < 0.01, f"Expected ~50%, got {cagr}%"

    def test_benchmark_twr_correct_net_investment(self) -> None:
        """Test benchmark TWR with corrected net investment calculation."""

        benchmark_transactions = [
            {
                "transaction_date": datetime(2023, 1, 1, tzinfo=timezone.utc),
                "total_amount": 1000.0,
                "transaction_type": "BUY",
            },
            {
                "transaction_date": datetime(2023, 6, 1, tzinfo=timezone.utc),
                "total_amount": -800.0,
                "transaction_type": "SELL",
            },
        ]

        twr = self.service._calculate_benchmark_twr(
            transactions=benchmark_transactions,
            current_value=300.0,
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )

        # Same calculation as CAGR for this simple case
        assert twr is not None
        assert abs(twr - 50.0) < 0.01, f"Expected ~50%, got {twr}%"

    # Test 3: Benchmark XIRR - Fixed Cash Flow Signs
    def test_benchmark_xirr_correct_cash_flows(self) -> None:
        """Test benchmark XIRR with corrected cash flow signs."""

        benchmark_transactions = [
            {
                "transaction_date": datetime(2023, 1, 1, tzinfo=timezone.utc),
                "total_amount": 1000.0,  # BUY: positive amount
                "transaction_type": "BUY",
            },
            {
                "transaction_date": datetime(2023, 6, 1, tzinfo=timezone.utc),
                "total_amount": -800.0,  # SELL: negative amount
                "transaction_type": "SELL",
            },
        ]

        # Mock pyxirr to verify correct cash flows are passed
        with patch("pyxirr.xirr") as mock_xirr:
            mock_xirr.return_value = 0.15  # 15% return

            xirr = self.service._calculate_benchmark_xirr(
                transactions=benchmark_transactions,
                current_value=300.0,
                end_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            )

            # Verify pyxirr was called with correct cash flows
            mock_xirr.assert_called_once()
            call_args = mock_xirr.call_args[0]
            amounts = call_args[1]

            # Expected cash flows: [-1000, +800, +300]
            # BUY 1000 -> -1000 (outflow)
            # SELL -800 -> +800 (inflow)
            # Final value -> +300 (inflow)
            expected_amounts = [-1000.0, 800.0, 300.0]
            assert (
                amounts == expected_amounts
            ), f"Expected {expected_amounts}, got {amounts}"
            assert xirr == 15.0

    # Test 4: Edge Cases
    @pytest.mark.asyncio
    async def test_cagr_zero_initial_value(self) -> None:
        """Test CAGR calculation when initial value is zero."""

        transactions = self.create_mock_transactions([])

        cagr = await self.service._calculate_cagr(
            portfolio_id=1,
            transactions=transactions,
            current_value=1000.0,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        assert cagr is None

    @pytest.mark.asyncio
    async def test_cagr_zero_current_value(self) -> None:
        """Test CAGR calculation when current value is zero."""

        transactions_data = [{"date": self.start_date, "type": "BUY", "amount": 1000.0}]
        transactions = self.create_mock_transactions(transactions_data)

        cagr = await self.service._calculate_cagr(
            portfolio_id=1,
            transactions=transactions,
            current_value=0.0,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        assert cagr is None

    @pytest.mark.asyncio
    async def test_cagr_negative_time_period(self) -> None:
        """Test CAGR calculation with negative time period."""

        transactions_data = [
            {
                "date": self.end_date,
                "type": "BUY",
                "amount": 1000.0,
            }  # Transaction after end date
        ]
        transactions = self.create_mock_transactions(transactions_data)

        cagr = await self.service._calculate_cagr(
            portfolio_id=1,
            transactions=transactions,
            current_value=1200.0,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        assert cagr is None

    def test_benchmark_calculations_empty_transactions(self) -> None:
        """Test benchmark calculations with empty transactions."""

        cagr = self.service._calculate_benchmark_cagr(
            transactions=[],
            current_value=1000.0,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        twr = self.service._calculate_benchmark_twr(
            transactions=[],
            current_value=1000.0,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        xirr = self.service._calculate_benchmark_xirr(
            transactions=[], current_value=1000.0, end_date=self.end_date
        )

        assert cagr is None
        assert twr is None
        assert xirr is None

    def test_benchmark_negative_net_investment(self) -> None:
        """Test benchmark calculations when net investment is negative (more sells than buys)."""

        benchmark_transactions = [
            {
                "transaction_date": datetime(2023, 1, 1, tzinfo=timezone.utc),
                "total_amount": 500.0,
                "transaction_type": "BUY",
            },
            {
                "transaction_date": datetime(2023, 6, 1, tzinfo=timezone.utc),
                "total_amount": -1000.0,  # Sell more than bought
                "transaction_type": "SELL",
            },
        ]

        cagr = self.service._calculate_benchmark_cagr(
            transactions=benchmark_transactions,
            current_value=100.0,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        twr = self.service._calculate_benchmark_twr(
            transactions=benchmark_transactions,
            current_value=100.0,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        # Net investment = 500 + (-1000) = -500 (negative)
        # Should return None for negative net investment
        assert cagr is None
        assert twr is None

    # Test 5: Portfolio XIRR (Should remain correct)
    def test_portfolio_xirr_correct_cash_flows(self) -> None:
        """Test that portfolio XIRR calculation remains correct."""

        transactions_data = [
            {
                "date": datetime(2023, 1, 1, tzinfo=timezone.utc),
                "type": "BUY",
                "amount": 1000.0,
            },
            {
                "date": datetime(2023, 6, 1, tzinfo=timezone.utc),
                "type": "SELL",
                "amount": 800.0,
            },
        ]
        transactions = self.create_mock_transactions(transactions_data)

        with patch("pyxirr.xirr") as mock_xirr:
            mock_xirr.return_value = 0.12  # 12% return

            xirr = self.service._calculate_xirr(
                transactions=transactions, current_value=300.0, end_date=self.end_date
            )

            # Verify correct cash flows for portfolio XIRR
            mock_xirr.assert_called_once()
            call_args = mock_xirr.call_args[0]
            amounts = call_args[1]

            # Expected: BUY -> -1000 (outflow), SELL -> +800 (inflow), Final -> +300 (inflow)
            expected_amounts = [-1000.0, 800.0, 300.0]
            assert amounts == expected_amounts
            assert xirr == 12.0

    # Test 6: Complex Multi-Transaction Scenarios
    def test_complex_benchmark_scenario(self) -> None:
        """Test complex scenario with multiple buys and sells."""

        benchmark_transactions = [
            {
                "transaction_date": datetime(2023, 1, 1, tzinfo=timezone.utc),
                "total_amount": 1000.0,
                "transaction_type": "BUY",
            },
            {
                "transaction_date": datetime(2023, 3, 1, tzinfo=timezone.utc),
                "total_amount": 500.0,
                "transaction_type": "BUY",
            },
            {
                "transaction_date": datetime(2023, 6, 1, tzinfo=timezone.utc),
                "total_amount": -300.0,
                "transaction_type": "SELL",
            },
            {
                "transaction_date": datetime(2023, 9, 1, tzinfo=timezone.utc),
                "total_amount": 200.0,
                "transaction_type": "BUY",
            },
            {
                "transaction_date": datetime(2023, 11, 1, tzinfo=timezone.utc),
                "total_amount": -400.0,
                "transaction_type": "SELL",
            },
        ]

        # Net investment = 1000 + 500 + (-300) + 200 + (-400) = 1000
        current_value = 1200.0

        cagr = self.service._calculate_benchmark_cagr(
            transactions=benchmark_transactions,
            current_value=current_value,
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )

        # Expected: (1200 / 1000) ^ 1 - 1 = 20%
        assert cagr is not None
        assert abs(cagr - 20.0) < 0.01, f"Expected ~20%, got {cagr}%"

    # Test 7: Asset-specific calculations
    @pytest.mark.asyncio
    async def test_asset_calculations_use_cost_basis(self) -> None:
        """Test that asset calculations properly use cost basis (documented limitation)."""

        transactions_data = [
            {
                "date": datetime(2023, 1, 1, tzinfo=timezone.utc),
                "type": "BUY",
                "amount": 1000.0,
                "asset_id": 1,
            },
            {
                "date": datetime(2023, 6, 1, tzinfo=timezone.utc),
                "type": "SELL",
                "amount": 300.0,
                "asset_id": 1,
            },
        ]
        transactions = self.create_mock_transactions(transactions_data)

        # Asset CAGR should use cost basis since we don't track daily asset values
        cagr = await self.service._calculate_asset_cagr(
            portfolio_id=1,
            transactions=transactions,
            current_value=900.0,
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )

        # Cost basis at start = 1000 (first transaction)
        # Expected: (900 / 1000) ^ 1 - 1 = -10%
        assert cagr is not None
        assert abs(cagr - (-10.0)) < 0.01, f"Expected ~-10%, got {cagr}%"

    # Test 8: Period Type Calculations
    def test_period_type_start_dates(self) -> None:
        """Test that period types calculate correct start dates."""

        base_date = datetime(2024, 6, 15, tzinfo=timezone.utc)

        # Test various periods
        assert PeriodType.get_start_date(
            PeriodType.LAST_3_MONTHS, base_date
        ) == base_date - timedelta(days=90)
        assert PeriodType.get_start_date(
            PeriodType.LAST_1_YEAR, base_date
        ) == base_date - timedelta(days=365)
        assert PeriodType.get_start_date(PeriodType.YTD, base_date) == datetime(
            2024, 1, 1
        )
        assert PeriodType.get_start_date(PeriodType.INCEPTION, base_date) is None

        # Test invalid period
        with pytest.raises(ValueError):
            PeriodType.get_start_date("invalid_period", base_date)

    # Test 9: Daily Portfolio Values Calculation
    @pytest.mark.asyncio
    async def test_daily_portfolio_values_calculation(self) -> None:
        """Test the daily portfolio values calculation logic."""

        # Mock transactions
        transactions_data = [
            {
                "date": datetime(2023, 1, 1, tzinfo=timezone.utc),
                "type": "BUY",
                "amount": 1000.0,
                "quantity": 10,
                "asset_id": 1,
            },
            {
                "date": datetime(2023, 6, 1, tzinfo=timezone.utc),
                "type": "SELL",
                "amount": 500.0,
                "quantity": 5,
                "asset_id": 1,
            },
        ]

        # Mock price data
        price_dates = [
            datetime(2023, 1, 1),
            datetime(2023, 3, 1),
            datetime(2023, 6, 1),
            datetime(2023, 12, 31),
        ]
        prices = [100.0, 110.0, 100.0, 120.0]
        price_data = self.create_mock_price_data(price_dates, prices)

        # Mock database queries
        self.mock_db.query.return_value.filter.return_value.all.return_value = (
            self.create_mock_transactions(transactions_data)
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            MockAsset(1, "AAPL", "Apple Inc.")
        )

        # Mock market data service
        self.service.market_data_service.fetch_ticker_data.return_value = price_data

        daily_values = await self.service._calculate_daily_portfolio_values(
            portfolio_id=1,
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2023, 12, 31, tzinfo=timezone.utc),
        )

        assert not daily_values.empty
        assert "PortfolioValue" in daily_values.columns
        assert "DailyReturn" in daily_values.columns

    # Test 10: Error Handling
    @pytest.mark.asyncio
    async def test_error_handling_in_calculations(self) -> None:
        """Test error handling in various calculation methods."""

        # Test with invalid data that should trigger exceptions
        transactions = [Mock(transaction_date="invalid_date")]

        # These should return None instead of raising exceptions
        cagr = await self.service._calculate_cagr(
            1, transactions, 1000.0, self.start_date, self.end_date
        )
        assert cagr is None

        xirr = self.service._calculate_xirr(transactions, 1000.0, self.end_date)
        assert xirr is None


def run_tests() -> bool:
    """Run all tests."""
    import subprocess
    import sys

    # Run pytest with verbose output
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "test_comprehensive_portfolio_calculations.py",
            "-v",
            "--tb=short",
        ],
        capture_output=True,
        text=True,
    )

    print("Test Results:")
    print("=" * 50)
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)

    return result.returncode == 0


if __name__ == "__main__":
    # Run the tests
    success = run_tests()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
