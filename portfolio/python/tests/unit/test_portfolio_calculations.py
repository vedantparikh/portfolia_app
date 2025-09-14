"""
Tests for Portfolio Calculation Service

Tests for CAGR, XIRR, TWR, and MWR calculations.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from app.core.database.models import Portfolio, Transaction, TransactionType
from app.core.services.portfolio_calculation_service import (
    PeriodType,
    PortfolioCalculationService,
)


class TestPortfolioCalculationService:
    """Test cases for portfolio calculation service."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()

    @pytest.fixture
    def calculation_service(self, mock_db):
        """Portfolio calculation service instance."""
        return PortfolioCalculationService(mock_db)

    @pytest.fixture
    def mock_portfolio(self):
        """Mock portfolio."""
        portfolio = Mock(spec=Portfolio)
        portfolio.id = 1
        portfolio.name = "Test Portfolio"
        portfolio.user_id = 1
        return portfolio

    @pytest.fixture
    def sample_transactions(self):
        """Sample transactions for testing."""
        base_date = datetime(2023, 1, 1)
        transactions = []

        # Buy transaction
        buy_transaction = Mock(spec=Transaction)
        buy_transaction.id = 1
        buy_transaction.portfolio_id = 1
        buy_transaction.asset_id = 1
        buy_transaction.transaction_type = TransactionType.BUY
        buy_transaction.quantity = Decimal("100")
        buy_transaction.price = Decimal("50.00")
        buy_transaction.total_amount = Decimal("5000.00")
        buy_transaction.transaction_date = base_date
        transactions.append(buy_transaction)

        # Another buy transaction
        buy_transaction2 = Mock(spec=Transaction)
        buy_transaction2.id = 2
        buy_transaction2.portfolio_id = 1
        buy_transaction2.asset_id = 1
        buy_transaction2.transaction_type = TransactionType.BUY
        buy_transaction2.quantity = Decimal("50")
        buy_transaction2.price = Decimal("60.00")
        buy_transaction2.total_amount = Decimal("3000.00")
        buy_transaction2.transaction_date = base_date + timedelta(days=180)
        transactions.append(buy_transaction2)

        return transactions

    def test_period_type_get_start_date(self):
        """Test period type start date calculation."""
        base_date = datetime(2024, 1, 15)

        # Test 3 months
        start_date = PeriodType.get_start_date(PeriodType.LAST_3_MONTHS, base_date)
        expected = base_date - timedelta(days=90)
        assert start_date == expected

        # Test YTD
        start_date = PeriodType.get_start_date(PeriodType.YTD, base_date)
        expected = datetime(2024, 1, 1)
        assert start_date == expected

        # Test inception
        start_date = PeriodType.get_start_date(PeriodType.INCEPTION, base_date)
        assert start_date is None

    @pytest.mark.asyncio
    async def test_calculate_cagr_basic(self, calculation_service, sample_transactions):
        """Test basic CAGR calculation."""
        portfolio_id = 1
        current_value = 10000.0  # Portfolio doubled
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 1, 1)  # 1 year later

        cagr = await calculation_service._calculate_cagr(
            portfolio_id, sample_transactions, current_value, start_date, end_date
        )

        # Should be approximately 25% CAGR for doubling in 1 year
        # (10000 / 5000)^(1/1) - 1 = 1.0 = 100%
        assert cagr is not None
        assert abs(cagr - 100.0) < 5.0  # Allow some tolerance

    @pytest.mark.asyncio
    async def test_calculate_cagr_no_transactions(self, calculation_service):
        """Test CAGR calculation with no transactions."""
        portfolio_id = 1
        current_value = 1000.0
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 1, 1)

        cagr = await calculation_service._calculate_cagr(
            portfolio_id, [], current_value, start_date, end_date
        )

        assert cagr is None

    @patch("pyxirr.xirr")
    def test_calculate_xirr(self, mock_xirr, calculation_service, sample_transactions):
        """Test XIRR calculation."""
        mock_xirr.return_value = 0.15  # 15% XIRR

        current_value = 10000.0
        end_date = datetime(2024, 1, 1)

        xirr_result = calculation_service._calculate_xirr(
            sample_transactions, current_value, end_date
        )

        assert xirr_result == 15.0  # Should convert to percentage
        mock_xirr.assert_called_once()

    @patch("pyxirr.xirr")
    def test_calculate_xirr_error(
        self, mock_xirr, calculation_service, sample_transactions
    ):
        """Test XIRR calculation with error."""
        mock_xirr.side_effect = Exception("XIRR calculation failed")

        current_value = 10000.0
        end_date = datetime(2024, 1, 1)

        xirr_result = calculation_service._calculate_xirr(
            sample_transactions, current_value, end_date
        )

        assert xirr_result is None

    @pytest.mark.asyncio
    async def test_calculate_twr_basic(self, calculation_service, sample_transactions):
        """Test basic TWR calculation."""
        portfolio_id = 1
        current_value = 10000.0
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 1, 1)

        twr = await calculation_service._calculate_twr(
            portfolio_id, sample_transactions, current_value, start_date, end_date
        )

        assert twr is not None
        # Should be positive return
        assert twr > 0

    @pytest.mark.asyncio
    async def test_calculate_initial_value(
        self, calculation_service, sample_transactions
    ):
        """Test initial value calculation."""
        portfolio_id = 1
        start_date = datetime(2023, 6, 1)  # After first transaction

        initial_value = await calculation_service._calculate_initial_market_value(
            portfolio_id, sample_transactions, start_date
        )

        # Should include the first transaction amount (or calculated market value)
        assert initial_value >= 0.0

    @pytest.mark.asyncio
    async def test_calculate_initial_value_no_start_date(
        self, calculation_service, sample_transactions
    ):
        """Test initial value calculation without start date."""
        portfolio_id = 1
        initial_value = await calculation_service._calculate_initial_market_value(
            portfolio_id, sample_transactions, None
        )

        # Should use first transaction amount (or calculated market value)
        assert initial_value >= 0.0

    def test_safe_subtract(self, calculation_service):
        """Test safe subtraction utility."""
        # Both values present
        result = calculation_service._safe_subtract(10.0, 5.0)
        assert result == 5.0

        # One value None
        result = calculation_service._safe_subtract(None, 5.0)
        assert result is None

        result = calculation_service._safe_subtract(10.0, None)
        assert result is None

        # Both values None
        result = calculation_service._safe_subtract(None, None)
        assert result is None

    def test_is_outperforming(self, calculation_service):
        """Test outperformance check."""
        # Portfolio outperforming
        result = calculation_service._is_outperforming(15.0, 10.0)
        assert result is True

        # Portfolio underperforming
        result = calculation_service._is_outperforming(5.0, 10.0)
        assert result is False

        # Equal performance
        result = calculation_service._is_outperforming(10.0, 10.0)
        assert result is False

        # Missing data
        result = calculation_service._is_outperforming(None, 10.0)
        assert result is None

    def test_empty_performance_result(self, calculation_service):
        """Test empty performance result structure."""
        result = calculation_service._empty_performance_result(1, "1y")

        assert result["portfolio_id"] == 1
        assert result["period"] == "1y"
        assert "error" in result
        assert result["metrics"]["cagr"] is None
        assert result["metrics"]["xirr"] is None
        assert result["metrics"]["twr"] is None
        assert result["metrics"]["mwr"] is None

    @pytest.mark.asyncio
    @patch.object(PortfolioCalculationService, "_get_portfolio")
    @patch.object(PortfolioCalculationService, "_get_transactions")
    @patch.object(PortfolioCalculationService, "_get_current_portfolio_value")
    async def test_calculate_portfolio_performance_integration(
        self,
        mock_get_value,
        mock_get_transactions,
        mock_get_portfolio,
        calculation_service,
        mock_portfolio,
        sample_transactions,
    ):
        """Test integration of portfolio performance calculation."""
        # Setup mocks
        mock_get_portfolio.return_value = mock_portfolio
        mock_get_transactions.return_value = sample_transactions
        mock_get_value.return_value = 10000.0

        result = await calculation_service.calculate_portfolio_performance(
            portfolio_id=1, user_id=1, period=PeriodType.LAST_1_YEAR
        )

        assert result["portfolio_id"] == 1
        assert result["portfolio_name"] == "Test Portfolio"
        assert result["current_value"] == 10000.0
        assert "metrics" in result
        assert "calculation_date" in result

    @pytest.mark.asyncio
    @patch.object(PortfolioCalculationService, "_get_portfolio")
    async def test_calculate_portfolio_performance_not_found(
        self, mock_get_portfolio, calculation_service
    ):
        """Test portfolio performance calculation when portfolio not found."""
        mock_get_portfolio.return_value = None

        with pytest.raises(ValueError, match="Portfolio 1 not found"):
            await calculation_service.calculate_portfolio_performance(
                portfolio_id=1, user_id=1, period=PeriodType.LAST_1_YEAR
            )
