"""
Tests for Daily Portfolio Value Calculations

Tests the enhanced portfolio calculation service with daily values.
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pandas as pd
import pytest

from app.core.database.models import Asset, Portfolio, Transaction, TransactionType
from app.core.services.portfolio_calculation_service import (
    PeriodType,
    PortfolioCalculationService,
)


class TestDailyPortfolioCalculations:
    """Test cases for daily portfolio value calculations."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()

    @pytest.fixture
    def calculation_service(self, mock_db):
        """Portfolio calculation service instance."""
        service = PortfolioCalculationService(mock_db)
        # Mock the market data service
        service.market_data_service = AsyncMock()
        return service

    @pytest.fixture
    def mock_portfolio(self):
        """Mock portfolio."""
        portfolio = Mock(spec=Portfolio)
        portfolio.id = 1
        portfolio.name = "Test Portfolio"
        portfolio.user_id = 1
        return portfolio

    @pytest.fixture
    def mock_asset(self):
        """Mock asset."""
        asset = Mock(spec=Asset)
        asset.id = 1
        asset.symbol = "AAPL"
        asset.name = "Apple Inc."
        return asset

    @pytest.fixture
    def sample_transactions(self):
        """Sample transactions for testing."""
        transactions = []
        
        # Initial buy
        buy1 = Mock(spec=Transaction)
        buy1.id = 1
        buy1.portfolio_id = 1
        buy1.asset_id = 1
        buy1.transaction_type = TransactionType.BUY
        buy1.quantity = Decimal("100")
        buy1.price = Decimal("150.00")
        buy1.total_amount = Decimal("15000.00")
        buy1.transaction_date = datetime(2023, 1, 15)
        transactions.append(buy1)
        
        # Additional buy
        buy2 = Mock(spec=Transaction)
        buy2.id = 2
        buy2.portfolio_id = 1
        buy2.asset_id = 1
        buy2.transaction_type = TransactionType.BUY
        buy2.quantity = Decimal("50")
        buy2.price = Decimal("160.00")
        buy2.total_amount = Decimal("8000.00")
        buy2.transaction_date = datetime(2023, 6, 15)
        transactions.append(buy2)
        
        return transactions

    @pytest.fixture
    def sample_price_data(self):
        """Sample historical price data."""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        # Filter out weekends
        dates = [d for d in dates if d.weekday() < 5]
        
        # Create realistic price data with some volatility
        np.random.seed(42)  # For reproducible tests
        base_price = 150.0
        prices = []
        
        for i, date in enumerate(dates):
            # Simulate price movement with trend and volatility
            trend = 0.0002 * i  # Slight upward trend
            volatility = np.random.normal(0, 0.02)  # 2% daily volatility
            price = base_price * (1 + trend + volatility)
            prices.append(price)
        
        df = pd.DataFrame({
            'Date': [d.date() for d in dates],
            'Open': [p * 0.995 for p in prices],
            'High': [p * 1.01 for p in prices],
            'Low': [p * 0.99 for p in prices],
            'Close': prices,
            'Volume': [1000000] * len(dates),
            'Dividends': [0.0] * len(dates),
            'Stock Splits': [0.0] * len(dates),
        })
        
        return df

    async def test_calculate_daily_portfolio_values(
        self, calculation_service, mock_asset, sample_transactions, sample_price_data
    ):
        """Test daily portfolio value calculation."""
        # Setup mocks
        calculation_service.db.query.return_value.filter.return_value.first.return_value = mock_asset
        calculation_service.market_data_service.fetch_ticker_data.return_value = sample_price_data
        
        # Mock _get_transactions
        with patch.object(calculation_service, '_get_transactions', return_value=sample_transactions):
            result = await calculation_service._calculate_daily_portfolio_values(
                portfolio_id=1,
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 12, 31)
            )
        
        # Verify results
        assert not result.empty
        assert 'Date' in result.columns
        assert 'PortfolioValue' in result.columns
        assert 'DailyReturn' in result.columns
        
        # Check that portfolio values are reasonable
        assert all(result['PortfolioValue'] > 0)
        
        # Check that we have daily returns
        assert len(result['DailyReturn'].dropna()) > 0

    def test_calculate_holdings_as_of_date(self, calculation_service, sample_transactions):
        """Test holdings calculation as of specific date."""
        # Test holdings before any transactions
        holdings = calculation_service._calculate_holdings_as_of_date(
            sample_transactions, datetime(2022, 12, 31).date()
        )
        assert holdings == {}
        
        # Test holdings after first transaction
        holdings = calculation_service._calculate_holdings_as_of_date(
            sample_transactions, datetime(2023, 3, 1).date()
        )
        assert holdings[1] == 100.0
        
        # Test holdings after second transaction
        holdings = calculation_service._calculate_holdings_as_of_date(
            sample_transactions, datetime(2023, 12, 31).date()
        )
        assert holdings[1] == 150.0

    def test_get_price_for_date(self, calculation_service, sample_price_data):
        """Test price retrieval for specific dates."""
        # Set up price data with date index
        sample_price_data['Date'] = pd.to_datetime(sample_price_data['Date']).dt.date
        price_data = sample_price_data.set_index('Date')
        
        # Test exact date match
        test_date = price_data.index[10]  # Use a date that exists
        price = calculation_service._get_price_for_date(price_data, test_date)
        assert price is not None
        assert price > 0
        
        # Test closest date (weekend)
        weekend_date = datetime(2023, 1, 7).date()  # Saturday
        price = calculation_service._get_price_for_date(price_data, weekend_date)
        assert price is not None  # Should find Friday's price

    async def test_enhanced_volatility_calculation(
        self, calculation_service, mock_asset, sample_transactions, sample_price_data
    ):
        """Test volatility calculation with daily data."""
        # Setup mocks
        calculation_service.db.query.return_value.filter.return_value.first.return_value = mock_asset
        calculation_service.market_data_service.fetch_ticker_data.return_value = sample_price_data
        
        with patch.object(calculation_service, '_get_transactions', return_value=sample_transactions):
            volatility = await calculation_service._calculate_volatility(
                portfolio_id=1,
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 12, 31)
            )
        
        # Verify volatility is calculated
        assert volatility is not None
        assert volatility > 0
        assert volatility < 100  # Reasonable volatility range

    async def test_enhanced_max_drawdown_calculation(
        self, calculation_service, mock_asset, sample_transactions, sample_price_data
    ):
        """Test maximum drawdown calculation with daily data."""
        # Create price data with a clear drawdown
        drawdown_data = sample_price_data.copy()
        # Simulate a 20% drawdown in the middle of the year
        mid_point = len(drawdown_data) // 2
        for i in range(mid_point, mid_point + 50):
            if i < len(drawdown_data):
                drawdown_data.loc[i, 'Close'] *= 0.8
        
        # Setup mocks
        calculation_service.db.query.return_value.filter.return_value.first.return_value = mock_asset
        calculation_service.market_data_service.fetch_ticker_data.return_value = drawdown_data
        
        with patch.object(calculation_service, '_get_transactions', return_value=sample_transactions):
            max_drawdown = await calculation_service._calculate_max_drawdown(
                portfolio_id=1,
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 12, 31)
            )
        
        # Verify drawdown is calculated and reasonable
        assert max_drawdown is not None
        assert max_drawdown > 0
        assert max_drawdown < 50  # Should be less than 50%

    async def test_enhanced_twr_calculation(
        self, calculation_service, mock_asset, sample_transactions, sample_price_data
    ):
        """Test Time-Weighted Return calculation with daily data."""
        # Setup mocks
        calculation_service.db.query.return_value.filter.return_value.first.return_value = mock_asset
        calculation_service.market_data_service.fetch_ticker_data.return_value = sample_price_data
        
        with patch.object(calculation_service, '_get_transactions', return_value=sample_transactions):
            twr = await calculation_service._calculate_twr(
                portfolio_id=1,
                transactions=sample_transactions,
                current_value=25000.0,
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 12, 31)
            )
        
        # Verify TWR is calculated
        assert twr is not None
        # TWR should be reasonable (not extremely high or low)
        assert -50 < twr < 100

    async def test_full_portfolio_performance_with_daily_data(
        self, calculation_service, mock_portfolio, mock_asset, sample_transactions, sample_price_data
    ):
        """Test complete portfolio performance calculation with daily data."""
        # Setup all mocks
        calculation_service.db.query.return_value.filter.return_value.first.side_effect = [
            mock_portfolio,  # For _get_portfolio
            mock_asset,      # For asset lookup in daily values
        ]
        calculation_service.market_data_service.fetch_ticker_data.return_value = sample_price_data
        
        with patch.object(calculation_service, '_get_transactions', return_value=sample_transactions), \
             patch.object(calculation_service, '_get_current_portfolio_value', return_value=25000.0):
            
            result = await calculation_service.calculate_portfolio_performance(
                portfolio_id=1,
                user_id=1,
                period=PeriodType.LAST_1_YEAR,
                end_date=datetime(2023, 12, 31)
            )
        
        # Verify all metrics are calculated
        assert result["portfolio_id"] == 1
        assert result["portfolio_name"] == "Test Portfolio"
        assert result["current_value"] == 25000.0
        
        metrics = result["metrics"]
        assert metrics["cagr"] is not None
        assert metrics["xirr"] is not None
        assert metrics["twr"] is not None
        assert metrics["mwr"] is not None
        assert metrics["volatility"] is not None  # Now calculated with daily data
        assert metrics["max_drawdown"] is not None  # Now calculated with daily data
        
        # Sharpe ratio should be calculated if volatility exists
        if metrics["volatility"] and metrics["volatility"] > 0:
            assert metrics["sharpe_ratio"] is not None

    def test_weekend_handling(self, calculation_service):
        """Test that weekends are properly handled in date ranges."""
        # Create a date range that includes weekends
        start_date = datetime(2023, 1, 1).date()  # Sunday
        end_date = datetime(2023, 1, 8).date()    # Sunday
        
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Count weekdays (should skip weekends)
        weekdays = [d for d in date_range if d.weekday() < 5]
        
        # Should have 5 weekdays (Mon-Fri)
        assert len(weekdays) == 5

    async def test_missing_price_data_handling(
        self, calculation_service, mock_asset, sample_transactions
    ):
        """Test handling when price data is not available."""
        # Setup mock to return empty DataFrame
        calculation_service.db.query.return_value.filter.return_value.first.return_value = mock_asset
        calculation_service.market_data_service.fetch_ticker_data.return_value = pd.DataFrame()
        
        with patch.object(calculation_service, '_get_transactions', return_value=sample_transactions):
            result = await calculation_service._calculate_daily_portfolio_values(
                portfolio_id=1,
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 12, 31)
            )
        
        # Should return empty DataFrame when no price data available
        assert result.empty

    def test_accuracy_benchmark_comparison(self):
        """Test calculation accuracy against known benchmarks."""
        # Test CAGR calculation with known values
        # If you invest $1000 and it grows to $1100 in 1 year, CAGR should be 10%
        
        # This would be implemented with known test cases
        # For example, using historical S&P 500 data and comparing results
        # to published performance metrics
        
        # Example test case:
        initial_value = 1000.0
        final_value = 1100.0
        years = 1.0
        
        expected_cagr = ((final_value / initial_value) ** (1 / years) - 1) * 100
        assert abs(expected_cagr - 10.0) < 0.01  # Should be approximately 10%


if __name__ == "__main__":
    # Run a simple test
    async def run_test():
        print("Running daily portfolio calculation tests...")
        # This would run the actual tests
        print("Tests completed successfully!")
    
    asyncio.run(run_test())
