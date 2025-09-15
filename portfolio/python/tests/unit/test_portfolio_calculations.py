"""
Tests for Portfolio Calculation Service
Tests for CAGR, XIRR, TWR, MWR, Volatility, and Drawdown calculations.
Includes logic, integration, utility, edge case, asset, and benchmark tests.
"""
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from decimal import Decimal
from unittest.mock import ANY
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

# Adjust these imports if your directory structure is different
from app.core.database.models import Asset
from app.core.database.models import Portfolio
from app.core.database.models import PortfolioAsset
from app.core.database.models import Transaction
from app.core.database.models import TransactionType
from app.core.services.portfolio_calculation_service import PeriodType
from app.core.services.portfolio_calculation_service import PortfolioCalculationService

# Use pytest-asyncio for all async tests
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()

@pytest.fixture
def calculation_service(mock_db):
    """Portfolio calculation service instance with a mocked DB."""
    with patch("app.core.services.portfolio_calculation_service.MarketDataService") as MockMarketDataService:
        MockMarketDataService.return_value = Mock(name="MockMarketDataServiceInstance")
        service = PortfolioCalculationService(mock_db)
        return service

@pytest.fixture
def test_scenario_data():
    """
    Provides a complete, fixed scenario for all tests.
    """
    base_date = datetime(2023, 1, 1, tzinfo=timezone.utc)

    # --- Assets ---
    # *** FIX: Create mocks correctly by setting attributes, not passing kwargs ***
    mock_asset_1 = Mock(spec=Asset)
    mock_asset_1.id = 1
    mock_asset_1.symbol = 'TECH'
    mock_asset_1.name = 'Tech Stock'

    mock_asset_2 = Mock(spec=Asset)
    mock_asset_2.id = 2
    mock_asset_2.symbol = 'OTHER'
    mock_asset_2.name = 'Other Stock'

    # --- Transactions ---
    txn1 = Mock(spec=Transaction,
                transaction_date=base_date,
                transaction_type=TransactionType.BUY,
                total_amount=Decimal("5000.00"),
                quantity=Decimal(50),
                asset_id=1)
    txn2 = Mock(spec=Transaction,
                transaction_date=base_date + timedelta(days=180),
                transaction_type=TransactionType.BUY,
                total_amount=Decimal("3000.00"),
                quantity=Decimal(50),
                asset_id=2)
    txn3 = Mock(spec=Transaction,
                transaction_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
                transaction_type=TransactionType.SELL,
                total_amount=Decimal("1000.00"),
                quantity=Decimal(10),
                asset_id=1)

    all_transactions = [txn1, txn2, txn3]
    asset_1_txns = [txn1, txn3]

    # --- Portfolio and Asset Mocks ---
    mock_portfolio = Mock(spec=Portfolio)
    mock_portfolio.id = 1
    mock_portfolio.name = "Test Portfolio"
    mock_portfolio.user_id = 1

    mock_current_pa1 = Mock(spec=PortfolioAsset, current_value=Decimal("8000.00"))
    mock_current_pa2 = Mock(spec=PortfolioAsset, current_value=Decimal("2000.00"))
    mock_current_assets = [mock_current_pa1, mock_current_pa2]
    mock_current_value = 10000.00

    # --- Known Values for Calculations ---
    test_end_date = datetime(2024, 9, 15, tzinfo=timezone.utc)
    ytd_start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

    mock_ytd_initial_value = 9000.0
    mock_asset_1_ytd_initial_value = 6000.0
    mock_inception_initial_value = 5000.0

    # --- Mock Price Data ---
    date_rng = pd.date_range(start=ytd_start_date, end=test_end_date, freq='D')
    values = [100.0, 102.0, 95.0, 98.0, 110.0, 90.0]
    returns = pd.Series(values).pct_change().fillna(0).tolist()
    values_len = len(values)
    full_values = values + [90.0] * (len(date_rng) - values_len)
    full_returns = returns + [0.0] * (len(date_rng) - values_len)

    mock_daily_df = pd.DataFrame({
        "Date": date_rng.date,
        "PortfolioValue": full_values,
        "DailyReturn": full_returns
    })

    # Mock price history for "TECH" as raw DataFrame with COLUMNS
    tech_price_start = datetime(2022, 12, 30, tzinfo=timezone.utc)
    tech_price_dates = pd.date_range(start=tech_price_start, end=test_end_date, freq='D').date

    mock_tech_price_df = pd.DataFrame({"Date": tech_price_dates})
    price_map = { ytd_start_date.date(): 120.0 }
    mock_tech_price_df['Close'] = mock_tech_price_df['Date'].map(price_map)
    mock_tech_price_df['Close'] = mock_tech_price_df['Close'].ffill().bfill()

    return {
        "portfolio": mock_portfolio,
        "assets": {1: mock_asset_1, 2: mock_asset_2},
        "all_transactions": all_transactions,
        "asset_1_txns": asset_1_txns,
        "current_assets": mock_current_assets,
        "current_value": mock_current_value,
        "asset_1_current_value": float(mock_current_pa1.current_value),
        "ytd_start_date": ytd_start_date,
        "end_date": test_end_date,
        "mock_ytd_initial_value": mock_ytd_initial_value,
        "mock_inception_initial_value": mock_inception_initial_value,
        "mock_daily_df": mock_daily_df,
        "mock_tech_price_df": mock_tech_price_df,
        "mock_asset_1_ytd_initial_value": mock_asset_1_ytd_initial_value,
    }


class TestPortfolioCalculationServiceLogic:
    """Tests the main calculation logic by mocking the complex internal helpers."""

    @pytest.mark.asyncio
    @patch.object(PortfolioCalculationService, '_calculate_initial_market_value', new_callable=AsyncMock)
    @patch.object(PortfolioCalculationService, '_calculate_daily_portfolio_values', new_callable=AsyncMock)
    async def test_ytd_calculations(self, mock_get_daily_vals, mock_get_init_val, calculation_service, test_scenario_data):
        data = test_scenario_data

        mock_get_init_val.return_value = data["mock_ytd_initial_value"]
        mock_get_daily_vals.return_value = data["mock_daily_df"]

        cagr = await calculation_service._calculate_cagr(
            1, data["all_transactions"], data["current_value"], data["ytd_start_date"], data["end_date"]
        )
        twr = await calculation_service._calculate_twr(
             1, data["all_transactions"], data["current_value"], data["ytd_start_date"], data["end_date"]
        )

        with patch("pyxirr.xirr", Mock(return_value=0.1234)) as mock_pyxirr:
            xirr = await calculation_service._calculate_period_xirr(
                1, data["all_transactions"], data["current_value"], data["ytd_start_date"], data["end_date"]
            )
            period_txn = data["all_transactions"][2]
            expected_dates = [data["ytd_start_date"], period_txn.transaction_date, data["end_date"]]
            expected_amounts = [-9000.0, float(period_txn.total_amount), data["current_value"]]
            mock_pyxirr.assert_called_with(expected_dates, expected_amounts)

        volatility = await calculation_service._calculate_volatility(1, data["ytd_start_date"], data["end_date"])
        max_drawdown = await calculation_service._calculate_max_drawdown(1, data["ytd_start_date"], data["end_date"])

        assert cagr == pytest.approx(11.11, abs=0.01)
        assert twr == pytest.approx(-10.0, abs=0.01)
        assert xirr == 12.34

        mock_daily_returns = data["mock_daily_df"]["DailyReturn"]
        expected_vol = mock_daily_returns.std() * np.sqrt(252) * 100
        assert volatility == pytest.approx(expected_vol, abs=0.01)

        assert max_drawdown == pytest.approx(18.18, abs=0.01)

    @pytest.mark.asyncio
    @patch.object(PortfolioCalculationService, '_calculate_initial_market_value', new_callable=AsyncMock)
    @patch.object(PortfolioCalculationService, '_calculate_daily_portfolio_values', new_callable=AsyncMock)
    async def test_inception_calculations(self, mock_get_daily_vals, mock_get_init_val, calculation_service, test_scenario_data):
        data = test_scenario_data

        mock_get_init_val.return_value = data["mock_inception_initial_value"]
        mock_get_daily_vals.return_value = data["mock_daily_df"]

        years = (data["end_date"] - data["all_transactions"][0].transaction_date).days / 365.25
        cagr = await calculation_service._calculate_cagr(
            1, data["all_transactions"], data["current_value"], None, data["end_date"]
        )

        with patch("pyxirr.xirr", Mock(return_value=0.0987)) as mock_pyxirr:
            xirr = await calculation_service._calculate_period_xirr(
                1, data["all_transactions"], data["current_value"], None, data["end_date"]
            )
            expected_dates = [txn.transaction_date for txn in data["all_transactions"]] + [data["end_date"]]
            expected_amounts = [-5000.0, -3000.0, 1000.0, 10000.0]
            mock_pyxirr.assert_called_with(expected_dates, expected_amounts)

        expected_cagr = ((data["current_value"] / data["mock_inception_initial_value"]) ** (1 / years)) - 1
        assert cagr == pytest.approx(expected_cagr * 100, abs=0.01)
        assert xirr == 9.87

    @pytest.mark.asyncio
    @patch.object(PortfolioCalculationService, '_calculate_initial_market_value', new_callable=AsyncMock, return_value=0.0)
    async def test_ytd_starting_from_zero(self, mock_get_init_val, calculation_service, test_scenario_data):
        data = test_scenario_data

        cagr = await calculation_service._calculate_cagr(
            1, [], data["current_value"], data["ytd_start_date"], data["end_date"]
        )

        with patch.object(PortfolioCalculationService, '_calculate_daily_portfolio_values', new_callable=AsyncMock, return_value=pd.DataFrame()):
             twr = await calculation_service._calculate_twr(
                 1, [], data["current_value"], data["ytd_start_date"], data["end_date"]
             )

        assert cagr is None
        assert twr is None

        with patch("pyxirr.xirr", Mock(return_value=0.15)) as mock_pyxirr:
            buy_txn = Mock(spec=Transaction,
                           transaction_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
                           transaction_type=TransactionType.BUY,
                           total_amount=Decimal("1000.00"))

            xirr = await calculation_service._calculate_period_xirr(
                1, [buy_txn], data["current_value"], data["ytd_start_date"], data["end_date"]
            )
            expected_dates = [buy_txn.transaction_date, data["end_date"]]
            expected_amounts = [-1000.0, 10000.0]
            mock_pyxirr.assert_called_with(expected_dates, expected_amounts)
            assert xirr == 15.0


class TestPortfolioCalculationServiceIntegration:
    """This tests the main public method, mocking the DB and key helpers."""

    @pytest.mark.asyncio
    @patch.object(PortfolioCalculationService, "_get_portfolio")
    @patch.object(PortfolioCalculationService, "_get_transactions")
    @patch.object(PortfolioCalculationService, "_get_current_portfolio_value")
    @patch.object(PortfolioCalculationService, '_calculate_initial_market_value', new_callable=AsyncMock)
    @patch.object(PortfolioCalculationService, '_calculate_daily_portfolio_values', new_callable=AsyncMock)
    async def test_calculate_portfolio_performance_integration(
            self, mock_get_daily_vals, mock_get_init_val, mock_get_value, mock_get_transactions,
            mock_get_portfolio, calculation_service, test_scenario_data):
        data = test_scenario_data

        mock_get_portfolio.return_value = data["portfolio"]
        mock_get_transactions.return_value = data["all_transactions"]
        mock_get_value.return_value = data["current_value"]
        mock_get_init_val.return_value = data["mock_ytd_initial_value"]
        mock_get_daily_vals.return_value = data["mock_daily_df"]

        with patch("pyxirr.xirr", Mock(return_value=0.1234)):
            result = await calculation_service.calculate_portfolio_performance(
                portfolio_id=1, user_id=1, period=PeriodType.YTD, end_date=data["end_date"]
            )

        assert result["portfolio_name"] == "Test Portfolio"
        metrics = result["metrics"]
        assert metrics["cagr"] == pytest.approx(11.11, abs=0.01)
        assert metrics["twr"] == pytest.approx(-10.0, abs=0.01)
        assert metrics["xirr"] == 12.34
        assert metrics["mwr"] == 12.34
        assert metrics["max_drawdown"] == pytest.approx(18.18, abs=0.01)

        mock_daily_returns = data["mock_daily_df"]["DailyReturn"]
        expected_vol = mock_daily_returns.std() * np.sqrt(252) * 100
        assert metrics["volatility"] == pytest.approx(expected_vol, abs=0.01)


    @pytest.mark.asyncio
    @patch.object(PortfolioCalculationService, "_get_portfolio")
    async def test_calculate_portfolio_performance_not_found(self, mock_get_portfolio, calculation_service):
        mock_get_portfolio.return_value = None
        with pytest.raises(ValueError, match="Portfolio 1 not found"):
            await calculation_service.calculate_portfolio_performance(
                portfolio_id=1, user_id=1, period=PeriodType.LAST_1_YEAR
            )

    @pytest.mark.asyncio
    @patch.object(PortfolioCalculationService, "_get_portfolio")
    @patch.object(PortfolioCalculationService, "_get_transactions")
    async def test_performance_no_transactions(self, mock_get_transactions, mock_get_portfolio, calculation_service, test_scenario_data):
        mock_get_portfolio.return_value = test_scenario_data["portfolio"]
        mock_get_transactions.return_value = []

        result = await calculation_service.calculate_portfolio_performance(
            1, 1, period=PeriodType.YTD, end_date=test_scenario_data["end_date"]
        )

        assert "error" in result
        assert result["metrics"]["cagr"] is None
        assert result["metrics"]["xirr"] is None

    @pytest.mark.asyncio
    @patch.object(PortfolioCalculationService, "_get_portfolio")
    @patch.object(PortfolioCalculationService, "_get_transactions")
    @patch.object(PortfolioCalculationService, "_get_current_portfolio_value", return_value=0.0)
    @patch.object(PortfolioCalculationService, '_calculate_initial_market_value', new_callable=AsyncMock, return_value=9000.0)
    @patch.object(PortfolioCalculationService, '_calculate_daily_portfolio_values', new_callable=AsyncMock)
    async def test_performance_all_assets_sold(
        self, mock_daily_vals, mock_init_val, mock_get_current_val, mock_get_txns,
        mock_get_portfolio, calculation_service, test_scenario_data
    ):
        mock_daily_vals.return_value = test_scenario_data["mock_daily_df"]
        mock_get_portfolio.return_value = test_scenario_data["portfolio"]
        mock_get_txns.return_value = test_scenario_data["all_transactions"]

        result = await calculation_service.calculate_portfolio_performance(
            1, 1, period=PeriodType.YTD, end_date=test_scenario_data["end_date"]
        )

        assert result["metrics"]["cagr"] == -100.0
        assert result["metrics"]["xirr"] is not None


class TestAssetAndBenchmarkPerformance:
    """New test for asset and benchmark methods."""

    @pytest.mark.asyncio
    @patch.object(PortfolioCalculationService, "_get_portfolio")
    @patch.object(PortfolioCalculationService, "_get_asset_transactions")
    @patch.object(PortfolioCalculationService, "_get_current_asset_value")
    @patch("app.core.services.portfolio_calculation_service.MarketDataService.fetch_ticker_data", new_callable=AsyncMock)
    async def test_asset_performance_ytd(
        self, mock_fetch_data, mock_get_current_asset_val, mock_get_asset_txns,
        mock_get_portfolio, calculation_service, test_scenario_data
    ):
        """Tests the calculate_asset_performance method, validating the 'Market Value > Cost Basis' logic."""
        data = test_scenario_data
        asset_id = 1
        user_id = 1

        mock_get_portfolio.return_value = data["portfolio"]
        mock_get_asset_txns.return_value = data["asset_1_txns"]
        mock_get_current_asset_val.return_value = data["asset_1_current_value"]
        mock_fetch_data.return_value = data["mock_tech_price_df"]

        calculation_service.db.query.return_value.filter.return_value.first.return_value = data["assets"][1]

        with patch("pyxirr.xirr", Mock(return_value=0.25)) as mock_pyxirr:
            result = await calculation_service.calculate_asset_performance(
                data["portfolio"].id, asset_id, user_id, PeriodType.YTD, data["end_date"]
            )

        assert result["asset_id"] == 1
        assert result["current_value"] == 8000.0

        assert result["metrics"]["cagr"] == pytest.approx(33.33, abs=0.01)

        assert result["metrics"]["xirr"] == 25.0
        assert result["metrics"]["mwr"] == 25.0

        expected_dates = [data["ytd_start_date"], data["asset_1_txns"][1].transaction_date, data["end_date"]]
        expected_amounts = [-6000.0, 1000.0, 8000.0]
        mock_pyxirr.assert_called_with(expected_dates, expected_amounts)

    @pytest.mark.asyncio
    @patch("app.core.services.portfolio_calculation_service.MarketDataService.fetch_ticker_data", new_callable=AsyncMock)
    async def test_benchmark_performance(self, mock_fetch_data, calculation_service, test_scenario_data):
        """Tests the benchmark calculation logic."""
        investments = [
            (datetime(2024, 1, 1, tzinfo=timezone.utc), 1000.0),
            (datetime(2024, 3, 1, tzinfo=timezone.utc), 500.0)
        ]
        end_date = test_scenario_data["end_date"]

        benchmark_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        spy_dates = pd.date_range(start=benchmark_start, end=end_date, freq='D').date
        price_df = pd.DataFrame({"Date": spy_dates})

        price_map = {
            datetime(2024, 1, 1).date(): 100.0,
            datetime(2024, 3, 1).date(): 110.0,
            end_date.date(): 120.0
        }
        price_df['Close'] = price_df['Date'].map(price_map)
        price_df['Close'] = price_df['Close'].ffill()
        price_df['Close'] = price_df['Close'].bfill()

        mock_fetch_data.return_value = price_df

        with patch("pyxirr.xirr", Mock(return_value=0.15)):
            result = await calculation_service.calculate_benchmark_performance(
                benchmark_symbol="SPY",
                investment_amounts=investments,
                period=PeriodType.YTD,
                end_date=end_date
            )

        expected_value = (1000/100 + 500/110) * 120
        assert "error" not in result
        assert result["current_value"] == pytest.approx(expected_value)
        assert result["metrics"]["cagr"] > 0
        assert result["metrics"]["xirr"] == 15.0


class TestPortfolioCalculationServiceUtilities:
    """Tests for the simple, synchronous helper functions."""

    def test_period_type_get_start_date(self):
        base_date = datetime(2024, 1, 15, tzinfo=timezone.utc)
        start_date = PeriodType.get_start_date(PeriodType.LAST_3_MONTHS, base_date)
        assert start_date == base_date - timedelta(days=90)
        start_date = PeriodType.get_start_date(PeriodType.YTD, base_date)
        assert start_date == datetime(2024, 1, 1, tzinfo=timezone.utc)
        start_date = PeriodType.get_start_date(PeriodType.INCEPTION, base_date)
        assert start_date is None

    def test_safe_subtract(self, calculation_service):
        assert calculation_service._safe_subtract(10.0, 5.0) == 5.0
        assert calculation_service._safe_subtract(None, 5.0) is None

    def test_is_outperforming(self, calculation_service):
        assert calculation_service._is_outperforming(15.0, 10.0) is True
        assert calculation_service._is_outperforming(5.0, 10.0) is False

    def test_empty_performance_result(self, calculation_service):
        result = calculation_service._empty_performance_result(1, "1y")
        assert result["portfolio_id"] == 1
        assert result["metrics"]["cagr"] is None        assert calculation_service._is_outperforming(15.0, 10.0) is True
        assert calculation_service._is_outperforming(5.0, 10.0) is False

    def test_empty_performance_result(self, calculation_service):
        result = calculation_service._empty_performance_result(1, "1y")
        assert result["portfolio_id"] == 1
        assert result["metrics"]["cagr"] is None