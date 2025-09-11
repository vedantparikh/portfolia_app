"""
Portfolio Analytics Service
Comprehensive service for portfolio analysis, risk management, and performance tracking.
"""

import logging
import math
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import numpy as np
import pandas as pd
from sqlalchemy import and_
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.database.models import Portfolio
from app.core.database.models import PortfolioAsset
from app.core.database.models.portfolio_analytics import AssetPerformanceMetrics
from app.core.database.models.portfolio_analytics import PortfolioAllocation
from app.core.database.models.portfolio_analytics import PortfolioBenchmark
from app.core.database.models.portfolio_analytics import PortfolioPerformanceHistory
from app.core.database.models.portfolio_analytics import PortfolioRiskMetrics
from app.core.database.models.portfolio_analytics import RiskLevel
from app.core.schemas.portfolio_analytics import AllocationAnalysisResponse
from app.core.schemas.portfolio_analytics import AllocationDrift
from app.core.schemas.portfolio_analytics import AllocationItem
from app.core.schemas.portfolio_analytics import AssetMetricsResponse
from app.core.schemas.portfolio_analytics import PerformanceSnapshotResponse
from app.core.schemas.portfolio_analytics import PortfolioAllocationAnalysis
from app.core.schemas.portfolio_analytics import PortfolioAllocationCreate
from app.core.schemas.portfolio_analytics import PortfolioAnalyticsSummary
from app.core.schemas.portfolio_analytics import PortfolioRebalancingRecommendation
from app.core.schemas.portfolio_analytics import RebalancingAction
from app.core.schemas.portfolio_analytics import RiskCalculationResponse
from app.core.services.market_data_service import market_data_service

logger = logging.getLogger(__name__)


class PortfolioAnalyticsService:
    """Service for comprehensive portfolio analytics and risk management."""

    def __init__(self, db: Session):
        self.db = db

    # Portfolio Performance History
    async def create_performance_snapshot(
        self, portfolio_id: int, snapshot_date: Optional[datetime] = None
    ) -> PerformanceSnapshotResponse:
        """Create a performance snapshot for a portfolio."""
        if snapshot_date is None:
            snapshot_date = datetime.utcnow()

        # Get portfolio assets
        portfolio_assets = (
            self.db.query(PortfolioAsset)
            .filter(PortfolioAsset.portfolio_id == portfolio_id)
            .all()
        )

        if not portfolio_assets:
            raise ValueError("Portfolio has no assets")

        # Calculate basic metrics using real-time prices from yfinance
        total_cost_basis = sum(
            float(asset.cost_basis_total) for asset in portfolio_assets
        )
        total_current_value = 0

        # Get current prices for all assets
        for asset in portfolio_assets:
            if asset.asset and asset.asset.symbol:
                current_price = await market_data_service.get_current_price(
                    asset.asset.symbol
                )
                if current_price:
                    total_current_value += float(current_price) * float(asset.quantity)
                else:
                    # Fallback to cost basis if price unavailable
                    total_current_value += float(asset.cost_basis_total)
            else:
                total_current_value += float(asset.cost_basis_total)

        total_unrealized_pnl = total_current_value - total_cost_basis
        total_unrealized_pnl_percent = (
            (total_unrealized_pnl / total_cost_basis * 100)
            if total_cost_basis > 0
            else 0
        )

        # Calculate performance metrics
        performance_metrics = self._calculate_portfolio_performance_metrics(
            portfolio_id, snapshot_date
        )

        # Create snapshot
        snapshot = PortfolioPerformanceHistory(
            portfolio_id=portfolio_id,
            snapshot_date=snapshot_date,
            total_value=Decimal(str(total_current_value)),
            total_cost_basis=Decimal(str(total_cost_basis)),
            total_unrealized_pnl=Decimal(str(total_unrealized_pnl)),
            total_unrealized_pnl_percent=Decimal(str(total_unrealized_pnl_percent)),
            **performance_metrics,
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        # Return schema response with all available fields
        return PerformanceSnapshotResponse(
            id=snapshot.id,
            portfolio_id=snapshot.portfolio_id,
            snapshot_date=snapshot.snapshot_date,
            total_value=snapshot.total_value,
            total_cost_basis=snapshot.total_cost_basis,
            total_unrealized_pnl=snapshot.total_unrealized_pnl,
            total_unrealized_pnl_percent=snapshot.total_unrealized_pnl_percent,
            created_at=snapshot.created_at,
        )

    def _calculate_portfolio_performance_metrics(
        self, portfolio_id: int, snapshot_date: datetime
    ) -> Dict[str, Any]:
        """Calculate portfolio performance metrics."""
        # Get historical performance data
        end_date = snapshot_date
        start_date = end_date - timedelta(days=365)  # 1 year lookback

        # Get daily returns for the portfolio
        daily_returns = self._get_portfolio_daily_returns(
            portfolio_id, start_date, end_date
        )

        if len(daily_returns) < 30:  # Need at least 30 days of data
            return {}

        # Calculate metrics
        metrics = {}

        # Basic returns
        total_return = (daily_returns.iloc[-1] / daily_returns.iloc[0]) - 1
        metrics["cumulative_return"] = Decimal(str(total_return))

        # Annualized return
        days = len(daily_returns)
        annualized_return = (1 + total_return) ** (365 / days) - 1
        metrics["annualized_return"] = Decimal(str(annualized_return))

        # Volatility (annualized)
        daily_volatility = daily_returns.pct_change().std()
        annualized_volatility = daily_volatility * math.sqrt(252)
        metrics["volatility"] = Decimal(str(annualized_volatility))

        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
        metrics["sharpe_ratio"] = Decimal(str(sharpe_ratio))

        # Maximum drawdown
        cumulative_returns = (1 + daily_returns.pct_change()).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        metrics["max_drawdown"] = Decimal(str(max_drawdown))

        # Value at Risk (95% and 99%)
        returns = daily_returns.pct_change().dropna()
        var_95 = returns.quantile(0.05)
        var_99 = returns.quantile(0.01)
        metrics["var_95"] = Decimal(str(var_95))
        metrics["var_99"] = Decimal(str(var_99))

        return metrics

    async def _get_portfolio_daily_returns(
        self, portfolio_id: int, start_date: datetime, end_date: datetime
    ) -> pd.Series:
        """Get daily portfolio returns using yfinance data."""
        # Get portfolio assets
        portfolio_assets = (
            self.db.query(PortfolioAsset)
            .filter(PortfolioAsset.portfolio_id == portfolio_id)
            .all()
        )

        if not portfolio_assets:
            return pd.Series()

        # For now, return a simplified series based on current values
        # In a full implementation, you'd fetch historical data for each asset
        # and calculate portfolio values over time

        # Get current portfolio value as a baseline
        total_current_value = 0
        for asset in portfolio_assets:
            if asset.asset and asset.asset.symbol:
                current_price = await market_data_service.get_current_price(
                    asset.asset.symbol
                )
                if current_price:
                    total_current_value += float(current_price) * float(asset.quantity)
                else:
                    total_current_value += float(asset.cost_basis_total)
            else:
                total_current_value += float(asset.cost_basis_total)

        # Create a simple series with the current value
        # This is a placeholder - in production you'd want historical portfolio values
        date_range = pd.date_range(start_date, end_date, freq="D")
        values = [total_current_value] * len(date_range)

        return pd.Series(values, index=date_range)

    # Asset Performance Metrics
    async def calculate_asset_metrics(
        self, asset_id: int, calculation_date: Optional[datetime] = None
    ) -> AssetMetricsResponse:
        """Calculate comprehensive metrics for an asset using yfinance data."""
        if calculation_date is None:
            calculation_date = datetime.utcnow()

        # Get asset from database to get symbol
        from app.core.database.models import Asset

        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset or not asset.symbol:
            raise ValueError("Asset not found or missing symbol")

        # Get historical data from yfinance (1 year lookback)
        end_date_str = calculation_date.strftime("%Y-%m-%d")
        start_date_str = (calculation_date - timedelta(days=365)).strftime("%Y-%m-%d")

        price_data = await market_data_service.fetch_ticker_data(
            symbol=asset.symbol,
            start_date=start_date_str,
            end_date=end_date_str,
            interval="1d",
        )

        if price_data is None or len(price_data) < 30:
            raise ValueError("Insufficient price data for calculations")

        # Get current price and calculate basic metrics
        current_price = await market_data_service.get_current_price(asset.symbol)
        if not current_price:
            current_price = float(price_data["Close"].iloc[-1])

        # Calculate price change
        previous_close = (
            float(price_data["Close"].iloc[-2])
            if len(price_data) > 1
            else current_price
        )
        price_change = current_price - previous_close
        price_change_percent = (
            (price_change / previous_close) * 100 if previous_close > 0 else 0
        )

        # Calculate technical indicators using the price data
        metrics = self._calculate_technical_indicators_from_yfinance(price_data)

        # Calculate risk and performance metrics
        risk_metrics = self._calculate_risk_metrics_from_yfinance(price_data)
        performance_metrics = self._calculate_performance_metrics_from_yfinance(
            price_data
        )

        # Create and save metrics record
        asset_metrics = AssetPerformanceMetrics(
            asset_id=asset_id,
            calculation_date=calculation_date,
            current_price=Decimal(str(current_price)),
            price_change=Decimal(str(price_change)) if price_change else None,
            price_change_percent=(
                Decimal(str(price_change_percent)) if price_change_percent else None
            ),
            **metrics,
            **risk_metrics,
            **performance_metrics,
        )

        self.db.add(asset_metrics)
        self.db.commit()
        self.db.refresh(asset_metrics)

        # Return comprehensive schema response with all available fields matching database model
        return AssetMetricsResponse(
            id=asset_metrics.id,
            asset_id=asset_metrics.asset_id,
            calculation_date=asset_metrics.calculation_date,
            current_price=asset_metrics.current_price,
            price_change=asset_metrics.price_change,
            price_change_percent=asset_metrics.price_change_percent,
            # Technical indicators
            sma_20=asset_metrics.sma_20,
            sma_50=asset_metrics.sma_50,
            sma_200=asset_metrics.sma_200,
            ema_12=asset_metrics.ema_12,
            ema_26=asset_metrics.ema_26,
            # Momentum indicators
            rsi=asset_metrics.rsi,
            macd=asset_metrics.macd,
            macd_signal=asset_metrics.macd_signal,
            macd_histogram=asset_metrics.macd_histogram,
            stochastic_k=asset_metrics.stochastic_k,
            stochastic_d=asset_metrics.stochastic_d,
            # Volatility indicators
            bollinger_upper=asset_metrics.bollinger_upper,
            bollinger_middle=asset_metrics.bollinger_middle,
            bollinger_lower=asset_metrics.bollinger_lower,
            atr=asset_metrics.atr,
            # Volume indicators
            volume_sma=asset_metrics.volume_sma,
            volume_ratio=asset_metrics.volume_ratio,
            obv=asset_metrics.obv,
            # Risk metrics
            volatility_20d=asset_metrics.volatility_20d,
            volatility_60d=asset_metrics.volatility_60d,
            volatility_252d=asset_metrics.volatility_252d,
            beta=asset_metrics.beta,
            sharpe_ratio=asset_metrics.sharpe_ratio,
            # Performance metrics
            total_return_1m=asset_metrics.total_return_1m,
            total_return_3m=asset_metrics.total_return_3m,
            total_return_1y=asset_metrics.total_return_1y,
            created_at=asset_metrics.created_at,
        )

    def _calculate_technical_indicators_from_yfinance(
        self, price_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Calculate technical indicators from yfinance data."""
        metrics = {}

        try:
            # Moving averages
            if len(price_data) >= 20:
                metrics["sma_20"] = Decimal(
                    str(price_data["Close"].rolling(20).mean().iloc[-1])
                )
            if len(price_data) >= 50:
                metrics["sma_50"] = Decimal(
                    str(price_data["Close"].rolling(50).mean().iloc[-1])
                )
            if len(price_data) >= 200:
                metrics["sma_200"] = Decimal(
                    str(price_data["Close"].rolling(200).mean().iloc[-1])
                )

            # Exponential moving averages
            if len(price_data) >= 12:
                metrics["ema_12"] = Decimal(
                    str(price_data["Close"].ewm(span=12).mean().iloc[-1])
                )
            if len(price_data) >= 26:
                metrics["ema_26"] = Decimal(
                    str(price_data["Close"].ewm(span=26).mean().iloc[-1])
                )

            # RSI
            if len(price_data) >= 14:
                delta = price_data["Close"].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                metrics["rsi"] = Decimal(str(rsi.iloc[-1]))

            # Volume indicators
            if "Volume" in price_data.columns and len(price_data) >= 20:
                metrics["volume_sma"] = Decimal(
                    str(price_data["Volume"].rolling(20).mean().iloc[-1])
                )

        except Exception as e:
            # If calculation fails, set None values
            pass

        return metrics

    def _calculate_risk_metrics_from_yfinance(
        self, price_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Calculate risk metrics from yfinance data."""
        metrics = {}

        try:
            # Calculate returns
            returns = price_data["Close"].pct_change().dropna()

            # Volatility
            if len(returns) >= 20:
                metrics["volatility_20d"] = Decimal(
                    str(returns.rolling(20).std().iloc[-1] * np.sqrt(252))
                )
            if len(returns) >= 60:
                metrics["volatility_60d"] = Decimal(
                    str(returns.rolling(60).std().iloc[-1] * np.sqrt(252))
                )

            # Sharpe ratio (assuming risk-free rate of 2%)
            if len(returns) >= 252:
                excess_returns = returns - 0.02 / 252  # Daily risk-free rate
                metrics["sharpe_ratio"] = Decimal(
                    str(excess_returns.mean() / excess_returns.std() * np.sqrt(252))
                )

            # Max drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            metrics["max_drawdown"] = Decimal(str(drawdown.min()))

        except Exception as e:
            # If calculation fails, set None values
            pass

        return metrics

    def _calculate_performance_metrics_from_yfinance(
        self, price_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Calculate performance metrics from yfinance data."""
        metrics = {}

        try:
            # Calculate returns for different periods
            current_price = price_data["Close"].iloc[-1]

            # 1-day return
            if len(price_data) >= 2:
                metrics["total_return_1d"] = Decimal(
                    str((current_price / price_data["Close"].iloc[-2] - 1) * 100)
                )

            # 1-week return
            if len(price_data) >= 7:
                metrics["total_return_1w"] = Decimal(
                    str((current_price / price_data["Close"].iloc[-7] - 1) * 100)
                )

            # 1-month return
            if len(price_data) >= 30:
                metrics["total_return_1m"] = Decimal(
                    str((current_price / price_data["Close"].iloc[-30] - 1) * 100)
                )

            # 3-month return
            if len(price_data) >= 90:
                metrics["total_return_3m"] = Decimal(
                    str((current_price / price_data["Close"].iloc[-90] - 1) * 100)
                )

            # 1-year return
            if len(price_data) >= 252:
                metrics["total_return_1y"] = Decimal(
                    str((current_price / price_data["Close"].iloc[-252] - 1) * 100)
                )

        except Exception as e:
            # If calculation fails, set None values
            pass

        return metrics

    async def analyze_portfolio_allocation(
        self, portfolio_id: int
    ) -> AllocationAnalysisResponse:
        """Analyze portfolio allocation and detect drift from targets."""
        # Get portfolio assets with current values
        portfolio_assets = (
            self.db.query(PortfolioAsset)
            .filter(PortfolioAsset.portfolio_id == portfolio_id)
            .all()
        )

        if not portfolio_assets:
            raise ValueError("Portfolio has no assets")

        # Calculate current allocations using real-time prices
        current_allocations = []
        total_current_value = 0

        for asset in portfolio_assets:
            if asset.asset and asset.asset.symbol:
                current_price = await market_data_service.get_current_price(
                    asset.asset.symbol
                )
                if current_price:
                    current_value = float(current_price) * float(asset.quantity)
                else:
                    current_value = float(asset.cost_basis_total)
            else:
                current_value = float(asset.cost_basis_total)

            total_current_value += current_value

            current_allocations.append({"asset": asset, "current_value": current_value})

        # Calculate allocation percentages and create AllocationItem objects
        allocation_items = []
        allocation_drifts = []
        total_drift = Decimal("0")
        rebalancing_needed = False

        for allocation in current_allocations:
            asset = allocation["asset"]
            current_value = allocation["current_value"]
            current_percentage = (
                Decimal(str((current_value / total_current_value) * 100))
                if total_current_value > 0
                else Decimal("0")
            )

            # Get target allocation if exists
            target_allocation = (
                self.db.query(PortfolioAllocation)
                .filter(
                    PortfolioAllocation.portfolio_id == portfolio_id,
                    PortfolioAllocation.asset_id == asset.asset_id,
                    PortfolioAllocation.is_active == True,
                )
                .first()
            )

            target_percentage = (
                target_allocation.target_percentage if target_allocation else None
            )

            allocation_item = AllocationItem(
                asset_id=asset.asset_id,
                asset_symbol=asset.asset.symbol if asset.asset else "Unknown",
                asset_name=asset.asset.name if asset.asset else None,
                current_percentage=current_percentage,
                target_percentage=target_percentage,
                current_value=Decimal(str(current_value)),
                quantity=asset.quantity,
            )
            allocation_items.append(allocation_item)

            # Calculate drift if target exists
            if target_percentage:
                drift_percentage = current_percentage - target_percentage
                drift_amount = Decimal(str(total_current_value)) * (
                    drift_percentage / 100
                )
                requires_rebalancing = abs(drift_percentage) > Decimal(
                    "5"
                )  # 5% threshold

                if requires_rebalancing:
                    rebalancing_needed = True

                total_drift += abs(drift_percentage)

                allocation_drift = AllocationDrift(
                    asset_id=asset.asset_id,
                    asset_symbol=asset.asset.symbol if asset.asset else "Unknown",
                    current_percentage=current_percentage,
                    target_percentage=target_percentage,
                    drift_percentage=drift_percentage,
                    drift_amount=drift_amount,
                    requires_rebalancing=requires_rebalancing,
                    recommended_action=(
                        "buy"
                        if drift_percentage < 0
                        else "sell" if drift_percentage > 0 else "hold"
                    ),
                )
                allocation_drifts.append(allocation_drift)

        return AllocationAnalysisResponse(
            portfolio_id=portfolio_id,
            current_allocations=allocation_items,
            target_allocations=[
                item for item in allocation_items if item.target_percentage is not None
            ],
            allocation_drift=allocation_drifts,
            total_drift_percentage=total_drift,
            rebalancing_needed=rebalancing_needed,
            analysis_date=datetime.utcnow(),
        )

    async def calculate_portfolio_risk_metrics(
        self, portfolio_id: int, calculation_date: Optional[datetime] = None
    ) -> RiskCalculationResponse:
        """Calculate comprehensive risk metrics for a portfolio."""
        if calculation_date is None:
            calculation_date = datetime.utcnow()

        # Get portfolio assets
        portfolio_assets = (
            self.db.query(PortfolioAsset)
            .filter(PortfolioAsset.portfolio_id == portfolio_id)
            .all()
        )

        if not portfolio_assets:
            raise ValueError("Portfolio has no assets")

        # Calculate portfolio volatility and other risk metrics
        # This is a simplified implementation - in practice you'd want more sophisticated calculations
        portfolio_volatility = Decimal("15.0")  # Placeholder
        var_95 = Decimal("5.0")  # Placeholder
        var_99 = Decimal("8.0")  # Placeholder

        # Create risk metrics record
        risk_metrics = PortfolioRiskMetrics(
            portfolio_id=portfolio_id,
            calculation_date=calculation_date,
            risk_level=RiskLevel.MODERATE,
            portfolio_volatility=portfolio_volatility,
            var_95_1d=var_95,
            var_99_1d=var_99,
        )

        self.db.add(risk_metrics)
        self.db.commit()
        self.db.refresh(risk_metrics)

        return RiskCalculationResponse(
            portfolio_id=risk_metrics.portfolio_id,
            calculation_date=risk_metrics.calculation_date,
            risk_level=risk_metrics.risk_level,
            portfolio_volatility=risk_metrics.portfolio_volatility,
            var_95=risk_metrics.var_95_1d,
            var_99=risk_metrics.var_99_1d,
            expected_shortfall_95=None,
            expected_shortfall_99=None,
            max_drawdown=None,
            sharpe_ratio=None,
            sortino_ratio=None,
            beta=None,
            correlation_to_market=None,
        )

    def _calculate_technical_indicators(
        self, price_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Calculate technical indicators for an asset."""
        metrics = {}

        # Moving averages
        metrics["sma_20"] = Decimal(
            str(price_data["close"].rolling(20).mean().iloc[-1])
        )
        metrics["sma_50"] = Decimal(
            str(price_data["close"].rolling(50).mean().iloc[-1])
        )
        metrics["sma_200"] = Decimal(
            str(price_data["close"].rolling(200).mean().iloc[-1])
        )

        # Exponential moving averages
        metrics["ema_12"] = Decimal(
            str(price_data["close"].ewm(span=12).mean().iloc[-1])
        )
        metrics["ema_26"] = Decimal(
            str(price_data["close"].ewm(span=26).mean().iloc[-1])
        )

        # RSI
        delta = price_data["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        metrics["rsi"] = Decimal(str(rsi.iloc[-1]))

        # MACD
        ema_12 = price_data["close"].ewm(span=12).mean()
        ema_26 = price_data["close"].ewm(span=26).mean()
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9).mean()
        macd_histogram = macd - macd_signal

        metrics["macd"] = Decimal(str(macd.iloc[-1]))
        metrics["macd_signal"] = Decimal(str(macd_signal.iloc[-1]))
        metrics["macd_histogram"] = Decimal(str(macd_histogram.iloc[-1]))

        # Bollinger Bands
        sma_20 = price_data["close"].rolling(20).mean()
        std_20 = price_data["close"].rolling(20).std()
        metrics["bollinger_upper"] = Decimal(str((sma_20 + (std_20 * 2)).iloc[-1]))
        metrics["bollinger_middle"] = Decimal(str(sma_20.iloc[-1]))
        metrics["bollinger_lower"] = Decimal(str((sma_20 - (std_20 * 2)).iloc[-1]))

        # ATR
        high_low = price_data["high"] - price_data["low"]
        high_close = np.abs(price_data["high"] - price_data["close"].shift())
        low_close = np.abs(price_data["low"] - price_data["close"].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(14).mean()
        metrics["atr"] = Decimal(str(atr.iloc[-1]))

        return metrics

    def _calculate_risk_metrics(self, price_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate risk metrics for an asset."""
        metrics = {}

        # Volatility calculations
        returns = price_data["close"].pct_change().dropna()
        metrics["volatility_20d"] = Decimal(
            str(returns.rolling(20).std().iloc[-1] * math.sqrt(252))
        )
        metrics["volatility_60d"] = Decimal(
            str(returns.rolling(60).std().iloc[-1] * math.sqrt(252))
        )
        metrics["volatility_252d"] = Decimal(str(returns.std() * math.sqrt(252)))

        # Beta calculation (simplified - would need market data)
        # For now, set to 1.0 as placeholder
        metrics["beta"] = Decimal("1.0")

        # Sharpe ratio (simplified)
        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * math.sqrt(252)
        sharpe_ratio = (
            (annual_return - 0.02) / annual_volatility if annual_volatility > 0 else 0
        )
        metrics["sharpe_ratio"] = Decimal(str(sharpe_ratio))

        return metrics

    def _calculate_performance_metrics(
        self, price_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Calculate performance metrics for an asset."""
        metrics = {}

        current_price = price_data["close"].iloc[-1]

        # Calculate returns for different periods
        periods = {
            "1m": 30,
            "3m": 90,
            "6m": 180,
            "1y": 365,
            "3y": 1095,
            "5y": 1825,
        }

        for period_name, days in periods.items():
            if len(price_data) >= days:
                start_price = price_data["close"].iloc[-days]
                total_return = (current_price / start_price) - 1
                metrics[f"total_return_{period_name}"] = Decimal(str(total_return))
            else:
                metrics[f"total_return_{period_name}"] = None

        return metrics

    # Portfolio Allocation Management
    def set_portfolio_allocation(
        self, portfolio_id: int, allocations: List[PortfolioAllocationCreate]
    ) -> List[PortfolioAllocation]:
        """Set target allocations for a portfolio."""
        # Clear existing allocations
        self.db.query(PortfolioAllocation).filter(
            PortfolioAllocation.portfolio_id == portfolio_id
        ).delete()

        # Create new allocations
        new_allocations = []
        for allocation_data in allocations:
            allocation = PortfolioAllocation(
                portfolio_id=portfolio_id,
                asset_id=allocation_data.asset_id,
                target_percentage=allocation_data.target_percentage,
                min_percentage=allocation_data.min_percentage,
                max_percentage=allocation_data.max_percentage,
                rebalance_threshold=allocation_data.rebalance_threshold,
                rebalance_frequency=allocation_data.rebalance_frequency,
                is_active=allocation_data.is_active,
            )
            self.db.add(allocation)
            new_allocations.append(allocation)

        self.db.commit()
        for allocation in new_allocations:
            self.db.refresh(allocation)

        return new_allocations

    async def get_portfolio_analytics_summary(
        self, portfolio_id: int
    ) -> Dict[str, Any]:
        """Get comprehensive portfolio analytics summary."""
        try:
            # Get portfolio assets
            portfolio_assets = (
                self.db.query(PortfolioAsset)
                .filter(PortfolioAsset.portfolio_id == portfolio_id)
                .all()
            )

            if not portfolio_assets:
                raise ValueError("Portfolio has no assets")

            # Calculate basic metrics using real-time prices
            total_cost_basis = sum(
                float(asset.cost_basis_total) for asset in portfolio_assets
            )
            total_current_value = 0

            # Get current prices for all assets
            for asset in portfolio_assets:
                if asset.asset and asset.asset.symbol:
                    current_price = await market_data_service.get_current_price(
                        asset.asset.symbol
                    )
                    if current_price:
                        total_current_value += float(current_price) * float(
                            asset.quantity
                        )
                    else:
                        total_current_value += float(asset.cost_basis_total)
                else:
                    total_current_value += float(asset.cost_basis_total)

            total_unrealized_pnl = total_current_value - total_cost_basis
            total_unrealized_pnl_percent = (
                (total_unrealized_pnl / total_cost_basis * 100)
                if total_cost_basis > 0
                else 0
            )

            # Get latest performance snapshot
            latest_snapshot = (
                self.db.query(PortfolioPerformanceHistory)
                .filter(PortfolioPerformanceHistory.portfolio_id == portfolio_id)
                .order_by(PortfolioPerformanceHistory.snapshot_date.desc())
                .first()
            )

            # Get latest risk metrics
            latest_risk = (
                self.db.query(PortfolioRiskMetrics)
                .filter(PortfolioRiskMetrics.portfolio_id == portfolio_id)
                .order_by(PortfolioRiskMetrics.calculation_date.desc())
                .first()
            )

            # Get portfolio info
            portfolio = (
                self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            )

            return {
                "portfolio_id": portfolio_id,
                "portfolio_name": portfolio.name if portfolio else "Unknown",
                "calculation_date": datetime.utcnow(),
                "total_value": Decimal(str(total_current_value)),
                "total_cost_basis": Decimal(str(total_cost_basis)),
                "total_unrealized_pnl": Decimal(str(total_unrealized_pnl)),
                "total_unrealized_pnl_percent": Decimal(
                    str(total_unrealized_pnl_percent)
                ),
                # Performance metrics from latest snapshot
                "total_return": (
                    latest_snapshot.cumulative_return if latest_snapshot else None
                ),
                "annualized_return": (
                    latest_snapshot.annualized_return if latest_snapshot else None
                ),
                "volatility": latest_snapshot.volatility if latest_snapshot else None,
                "sharpe_ratio": (
                    latest_snapshot.sharpe_ratio if latest_snapshot else None
                ),
                "sortino_ratio": None,  # Would need to be calculated
                "max_drawdown": (
                    latest_snapshot.max_drawdown if latest_snapshot else None
                ),
                # Risk metrics from latest calculation
                "risk_level": latest_risk.risk_level if latest_risk else None,
                "portfolio_volatility": (
                    latest_risk.portfolio_volatility if latest_risk else None
                ),
                "var_95": latest_risk.var_95_1d if latest_risk else None,
                "var_99": latest_risk.var_99_1d if latest_risk else None,
                "beta": latest_risk.portfolio_beta if latest_risk else None,
                "alpha": latest_risk.portfolio_alpha if latest_risk else None,
                # Diversification metrics
                "concentration_risk": (
                    latest_risk.concentration_risk if latest_risk else None
                ),
                "effective_number_of_assets": (
                    latest_risk.effective_number_of_assets if latest_risk else None
                ),
                "diversification_ratio": (
                    latest_risk.diversification_ratio if latest_risk else None
                ),
                # Benchmark comparison
                "benchmark_name": None,  # Would need to get from benchmark table
                "benchmark_return": (
                    latest_snapshot.benchmark_return if latest_snapshot else None
                ),
                "tracking_error": (
                    latest_snapshot.tracking_error if latest_snapshot else None
                ),
                "information_ratio": (
                    latest_snapshot.information_ratio if latest_snapshot else None
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get portfolio analytics summary: {e}")
            raise

    async def get_rebalancing_recommendation(self, portfolio_id: int) -> Dict[str, Any]:
        """Get rebalancing recommendations for a portfolio."""
        try:
            # Get current allocation analysis
            allocation_analysis = await self.analyze_portfolio_allocation(portfolio_id)

            # Check if rebalancing is needed
            if not allocation_analysis.rebalancing_needed:
                return {
                    "portfolio_id": portfolio_id,
                    "recommendation_date": datetime.utcnow(),
                    "trigger_reason": "no_rebalancing_needed",
                    "current_drift": allocation_analysis.total_drift_percentage,
                    "rebalancing_actions": [],
                    "estimated_cost": Decimal("0"),
                    "tax_impact": None,
                    "expected_allocations": [
                        item.dict() for item in allocation_analysis.current_allocations
                    ],
                    "expected_risk_reduction": None,
                    "expected_return_impact": None,
                    "priority": "low",
                    "recommended_timing": "no_action_needed",
                    "urgency_score": Decimal("0"),
                }

            # Generate rebalancing actions based on drift analysis
            rebalancing_actions = []
            estimated_cost = Decimal("0")

            for drift in allocation_analysis.allocation_drift:
                if drift.requires_rebalancing:
                    # Calculate recommended action
                    if drift.drift_percentage < -5:  # Underweight by more than 5%
                        action_type = "buy"
                        quantity_change = (
                            abs(drift.drift_amount) / 100
                        )  # Simplified calculation
                    elif drift.drift_percentage > 5:  # Overweight by more than 5%
                        action_type = "sell"
                        quantity_change = (
                            abs(drift.drift_amount) / 100
                        )  # Simplified calculation
                    else:
                        action_type = "hold"
                        quantity_change = Decimal("0")

                    # Estimate transaction cost (0.1% of transaction value)
                    transaction_cost = abs(drift.drift_amount) * Decimal("0.001")
                    estimated_cost += transaction_cost

                    rebalancing_action = {
                        "asset_id": drift.asset_id,
                        "asset_symbol": drift.asset_symbol,
                        "action_type": action_type,
                        "current_quantity": Decimal(
                            "0"
                        ),  # Would need to get from portfolio assets
                        "target_quantity": Decimal("0"),  # Would need to calculate
                        "quantity_change": quantity_change,
                        "estimated_cost": transaction_cost,
                        "priority": (
                            "high" if abs(drift.drift_percentage) > 10 else "medium"
                        ),
                    }
                    rebalancing_actions.append(rebalancing_action)

            # Calculate expected allocations after rebalancing
            expected_allocations = []
            for item in allocation_analysis.current_allocations:
                expected_allocation = {
                    "asset_id": item.asset_id,
                    "asset_symbol": item.asset_symbol,
                    "asset_name": item.asset_name,
                    "current_percentage": item.current_percentage,
                    "target_percentage": item.target_percentage
                    or item.current_percentage,
                    "expected_percentage": item.target_percentage
                    or item.current_percentage,
                    "current_value": item.current_value,
                    "quantity": item.quantity,
                }
                expected_allocations.append(expected_allocation)

            # Determine priority and urgency
            max_drift = max(
                [
                    abs(drift.drift_percentage)
                    for drift in allocation_analysis.allocation_drift
                ]
            )
            if max_drift > 15:
                priority = "high"
                urgency_score = Decimal("90")
                recommended_timing = "immediate"
            elif max_drift > 10:
                priority = "medium"
                urgency_score = Decimal("60")
                recommended_timing = "within_week"
            else:
                priority = "low"
                urgency_score = Decimal("30")
                recommended_timing = "within_month"

            return {
                "portfolio_id": portfolio_id,
                "recommendation_date": datetime.utcnow(),
                "trigger_reason": f"allocation_drift_exceeds_threshold_{max_drift:.1f}%",
                "current_drift": allocation_analysis.total_drift_percentage,
                "rebalancing_actions": rebalancing_actions,
                "estimated_cost": estimated_cost,
                "tax_impact": estimated_cost
                * Decimal("0.2"),  # Simplified tax estimate
                "expected_allocations": expected_allocations,
                "expected_risk_reduction": Decimal("5.0"),  # Simplified estimate
                "expected_return_impact": Decimal("0.5"),  # Simplified estimate
                "priority": priority,
                "recommended_timing": recommended_timing,
                "urgency_score": urgency_score,
            }

        except Exception as e:
            logger.error(f"Failed to get rebalancing recommendation: {e}")
            raise
