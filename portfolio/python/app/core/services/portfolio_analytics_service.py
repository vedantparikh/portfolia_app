"""
Portfolio Analytics Service
Comprehensive service for portfolio analysis, risk management, and performance tracking.
"""

import math
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.core.database.models import AssetPrice, Portfolio, PortfolioAsset
from app.core.database.models.portfolio_analytics import (
    AssetPerformanceMetrics,
    PortfolioAllocation,
    PortfolioBenchmark,
    PortfolioPerformanceHistory,
    PortfolioRiskMetrics,
    RiskLevel,
)
from app.core.schemas.portfolio_analytics import (
    PortfolioAllocationAnalysis,
    PortfolioAllocationCreate,
    PortfolioAnalyticsSummary,
    PortfolioRebalancingRecommendation,
)


class PortfolioAnalyticsService:
    """Service for comprehensive portfolio analytics and risk management."""

    def __init__(self, db: Session):
        self.db = db

    # Portfolio Performance History
    def create_performance_snapshot(
        self, portfolio_id: int, snapshot_date: Optional[datetime] = None
    ) -> PortfolioPerformanceHistory:
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

        # Calculate basic metrics
        total_cost_basis = sum(float(asset.cost_basis_total) for asset in portfolio_assets)
        total_current_value = sum(
            float(asset.current_value or asset.cost_basis_total) for asset in portfolio_assets
        )
        total_unrealized_pnl = total_current_value - total_cost_basis
        total_unrealized_pnl_percent = (
            (total_unrealized_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0
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

        return snapshot

    def _calculate_portfolio_performance_metrics(
        self, portfolio_id: int, snapshot_date: datetime
    ) -> Dict[str, Any]:
        """Calculate portfolio performance metrics."""
        # Get historical performance data
        end_date = snapshot_date
        start_date = end_date - timedelta(days=365)  # 1 year lookback

        # Get daily returns for the portfolio
        daily_returns = self._get_portfolio_daily_returns(portfolio_id, start_date, end_date)

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

    def _get_portfolio_daily_returns(
        self, portfolio_id: int, start_date: datetime, end_date: datetime
    ) -> pd.Series:
        """Get daily portfolio returns."""
        # Get portfolio assets
        portfolio_assets = (
            self.db.query(PortfolioAsset)
            .filter(PortfolioAsset.portfolio_id == portfolio_id)
            .all()
        )

        if not portfolio_assets:
            return pd.Series()

        # Get price data for all assets
        asset_ids = [asset.asset_id for asset in portfolio_assets]
        prices = (
            self.db.query(AssetPrice)
            .filter(
                and_(
                    AssetPrice.asset_id.in_(asset_ids),
                    AssetPrice.date >= start_date,
                    AssetPrice.date <= end_date,
                )
            )
            .order_by(AssetPrice.asset_id, AssetPrice.date)
            .all()
        )

        # Create price DataFrame
        price_data = {}
        for price in prices:
            if price.asset_id not in price_data:
                price_data[price.asset_id] = {}
            price_data[price.asset_id][price.date] = float(price.close_price)

        # Calculate portfolio value over time
        portfolio_values = {}
        for date in pd.date_range(start_date, end_date, freq="D"):
            total_value = 0
            for asset in portfolio_assets:
                # Get latest price for this asset on or before this date
                asset_prices = price_data.get(asset.asset_id, {})
                latest_price = None
                for price_date, price in sorted(asset_prices.items()):
                    if price_date <= date:
                        latest_price = price
                    else:
                        break

                if latest_price:
                    total_value += float(asset.quantity) * latest_price

            if total_value > 0:
                portfolio_values[date] = total_value

        return pd.Series(portfolio_values)

    # Asset Performance Metrics
    def calculate_asset_metrics(
        self, asset_id: int, calculation_date: Optional[datetime] = None
    ) -> AssetPerformanceMetrics:
        """Calculate comprehensive metrics for an asset."""
        if calculation_date is None:
            calculation_date = datetime.utcnow()

        # Get asset price data
        end_date = calculation_date
        start_date = end_date - timedelta(days=365)  # 1 year lookback

        prices = (
            self.db.query(AssetPrice)
            .filter(
                and_(
                    AssetPrice.asset_id == asset_id,
                    AssetPrice.date >= start_date,
                    AssetPrice.date <= end_date,
                )
            )
            .order_by(AssetPrice.date)
            .all()
        )

        if len(prices) < 30:
            raise ValueError("Insufficient price data for calculations")

        # Create price DataFrame
        price_data = pd.DataFrame(
            [
                {
                    "date": price.date,
                    "open": float(price.open_price or price.close_price),
                    "high": float(price.high_price or price.close_price),
                    "low": float(price.low_price or price.close_price),
                    "close": float(price.close_price),
                    "volume": float(price.volume or 0),
                }
                for price in prices
            ]
        )
        price_data.set_index("date", inplace=True)

        # Calculate technical indicators
        metrics = self._calculate_technical_indicators(price_data)

        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(price_data)

        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(price_data)

        # Get current price
        current_price = float(prices[-1].close_price)
        price_change = current_price - float(prices[-2].close_price) if len(prices) > 1 else 0
        price_change_percent = (price_change / float(prices[-2].close_price)) * 100 if len(prices) > 1 else 0

        # Create metrics record
        asset_metrics = AssetPerformanceMetrics(
            asset_id=asset_id,
            calculation_date=calculation_date,
            current_price=Decimal(str(current_price)),
            price_change=Decimal(str(price_change)),
            price_change_percent=Decimal(str(price_change_percent)),
            **metrics,
            **risk_metrics,
            **performance_metrics,
        )

        self.db.add(asset_metrics)
        self.db.commit()
        self.db.refresh(asset_metrics)

        return asset_metrics

    def _calculate_technical_indicators(self, price_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators for an asset."""
        metrics = {}

        # Moving averages
        metrics["sma_20"] = Decimal(str(price_data["close"].rolling(20).mean().iloc[-1]))
        metrics["sma_50"] = Decimal(str(price_data["close"].rolling(50).mean().iloc[-1]))
        metrics["sma_200"] = Decimal(str(price_data["close"].rolling(200).mean().iloc[-1]))

        # Exponential moving averages
        metrics["ema_12"] = Decimal(str(price_data["close"].ewm(span=12).mean().iloc[-1]))
        metrics["ema_26"] = Decimal(str(price_data["close"].ewm(span=26).mean().iloc[-1]))

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
        metrics["volatility_20d"] = Decimal(str(returns.rolling(20).std().iloc[-1] * math.sqrt(252)))
        metrics["volatility_60d"] = Decimal(str(returns.rolling(60).std().iloc[-1] * math.sqrt(252)))
        metrics["volatility_252d"] = Decimal(str(returns.std() * math.sqrt(252)))

        # Beta calculation (simplified - would need market data)
        # For now, set to 1.0 as placeholder
        metrics["beta"] = Decimal("1.0")

        # Sharpe ratio (simplified)
        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * math.sqrt(252)
        sharpe_ratio = (annual_return - 0.02) / annual_volatility if annual_volatility > 0 else 0
        metrics["sharpe_ratio"] = Decimal(str(sharpe_ratio))

        return metrics

    def _calculate_performance_metrics(self, price_data: pd.DataFrame) -> Dict[str, Any]:
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

    def analyze_portfolio_allocation(self, portfolio_id: int) -> PortfolioAllocationAnalysis:
        """Analyze portfolio allocation and detect drift."""
        # Get current allocations
        portfolio_assets = (
            self.db.query(PortfolioAsset)
            .filter(PortfolioAsset.portfolio_id == portfolio_id)
            .all()
        )

        # Get target allocations
        target_allocations = (
            self.db.query(PortfolioAllocation)
            .filter(
                and_(
                    PortfolioAllocation.portfolio_id == portfolio_id,
                    PortfolioAllocation.is_active == True,
                )
            )
            .all()
        )

        # Calculate current portfolio value
        total_value = sum(
            float(asset.current_value or asset.cost_basis_total) for asset in portfolio_assets
        )

        # Calculate current allocations
        current_allocations = []
        for asset in portfolio_assets:
            asset_value = float(asset.current_value or asset.cost_basis_total)
            allocation_percent = (asset_value / total_value * 100) if total_value > 0 else 0
            current_allocations.append(
                {
                    "asset_id": asset.asset_id,
                    "symbol": asset.asset.symbol,
                    "allocation_percent": float(allocation_percent),
                    "value": asset_value,
                }
            )

        # Calculate target allocations
        target_allocations_dict = {
            alloc.asset_id: alloc.target_percentage for alloc in target_allocations
        }

        # Calculate drift
        total_drift = 0
        max_drift = 0
        assets_requiring_rebalance = []
        rebalancing_actions = []

        for current in current_allocations:
            asset_id = current["asset_id"]
            current_percent = current["allocation_percent"]
            target_percent = target_allocations_dict.get(asset_id, 0)

            drift = abs(current_percent - target_percent)
            total_drift += drift
            max_drift = max(max_drift, drift)

            # Check if rebalancing is needed
            threshold = next(
                (
                    float(alloc.rebalance_threshold)
                    for alloc in target_allocations
                    if alloc.asset_id == asset_id and alloc.rebalance_threshold
                ),
                5.0,  # Default 5% threshold
            )

            if drift > threshold:
                assets_requiring_rebalance.append(
                    {
                        "asset_id": asset_id,
                        "symbol": current["symbol"],
                        "current_percent": current_percent,
                        "target_percent": target_percent,
                        "drift": drift,
                        "threshold": threshold,
                    }
                )

                # Calculate rebalancing action
                value_difference = (target_percent - current_percent) / 100 * total_value
                rebalancing_actions.append(
                    {
                        "asset_id": asset_id,
                        "symbol": current["symbol"],
                        "action": "buy" if value_difference > 0 else "sell",
                        "value_change": abs(value_difference),
                        "percent_change": abs(drift),
                    }
                )

        return PortfolioAllocationAnalysis(
            portfolio_id=portfolio_id,
            analysis_date=datetime.utcnow(),
            current_allocations=current_allocations,
            target_allocations=[
                {
                    "asset_id": alloc.asset_id,
                    "symbol": alloc.asset.symbol,
                    "target_percent": float(alloc.target_percentage),
                }
                for alloc in target_allocations
            ],
            total_drift=Decimal(str(total_drift)),
            max_drift=Decimal(str(max_drift)),
            assets_requiring_rebalance=assets_requiring_rebalance,
            rebalancing_actions=rebalancing_actions,
        )

    # Risk Analysis
    def calculate_portfolio_risk_metrics(
        self, portfolio_id: int, calculation_date: Optional[datetime] = None
    ) -> PortfolioRiskMetrics:
        """Calculate comprehensive risk metrics for a portfolio."""
        if calculation_date is None:
            calculation_date = datetime.utcnow()

        # Get portfolio performance data
        end_date = calculation_date
        start_date = end_date - timedelta(days=365)

        daily_returns = self._get_portfolio_daily_returns(portfolio_id, start_date, end_date)

        if len(daily_returns) < 30:
            raise ValueError("Insufficient data for risk calculations")

        returns = daily_returns.pct_change().dropna()

        # Calculate risk metrics
        portfolio_volatility = returns.std() * math.sqrt(252)
        sharpe_ratio = (returns.mean() * 252 - 0.02) / portfolio_volatility if portfolio_volatility > 0 else 0

        # Drawdown analysis
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()

        # Value at Risk
        var_95_1d = returns.quantile(0.05)
        var_99_1d = returns.quantile(0.01)
        var_95_1m = var_95_1d * math.sqrt(30)
        var_99_1m = var_99_1d * math.sqrt(30)

        # Conditional Value at Risk
        cvar_95_1d = returns[returns <= var_95_1d].mean()
        cvar_99_1d = returns[returns <= var_99_1d].mean()

        # Risk level assessment
        risk_score = min(100, max(0, (portfolio_volatility * 100) / 2))  # Simplified risk score
        if risk_score < 20:
            risk_level = RiskLevel.VERY_LOW
        elif risk_score < 40:
            risk_level = RiskLevel.LOW
        elif risk_score < 60:
            risk_level = RiskLevel.MODERATE
        elif risk_score < 80:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH

        # Diversification metrics
        portfolio_assets = (
            self.db.query(PortfolioAsset)
            .filter(PortfolioAsset.portfolio_id == portfolio_id)
            .all()
        )

        # Calculate concentration risk (Herfindahl index)
        total_value = sum(
            float(asset.current_value or asset.cost_basis_total) for asset in portfolio_assets
        )
        weights = [
            float(asset.current_value or asset.cost_basis_total) / total_value
            for asset in portfolio_assets
        ]
        concentration_risk = sum(w**2 for w in weights)
        effective_number_of_assets = 1 / concentration_risk if concentration_risk > 0 else 0

        # Create risk metrics record
        risk_metrics = PortfolioRiskMetrics(
            portfolio_id=portfolio_id,
            calculation_date=calculation_date,
            portfolio_volatility=Decimal(str(portfolio_volatility)),
            sharpe_ratio=Decimal(str(sharpe_ratio)),
            max_drawdown=Decimal(str(max_drawdown)),
            var_95_1d=Decimal(str(var_95_1d)),
            var_99_1d=Decimal(str(var_99_1d)),
            var_95_1m=Decimal(str(var_95_1m)),
            var_99_1m=Decimal(str(var_99_1m)),
            cvar_95_1d=Decimal(str(cvar_95_1d)),
            cvar_99_1d=Decimal(str(cvar_99_1d)),
            risk_level=risk_level,
            risk_score=Decimal(str(risk_score)),
            concentration_risk=Decimal(str(concentration_risk)),
            effective_number_of_assets=Decimal(str(effective_number_of_assets)),
        )

        self.db.add(risk_metrics)
        self.db.commit()
        self.db.refresh(risk_metrics)

        return risk_metrics

    # Comprehensive Analytics
    def get_portfolio_analytics_summary(self, portfolio_id: int) -> PortfolioAnalyticsSummary:
        """Get comprehensive portfolio analytics summary."""
        # Get portfolio basic info
        portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise ValueError("Portfolio not found")

        # Get latest performance snapshot
        latest_snapshot = (
            self.db.query(PortfolioPerformanceHistory)
            .filter(PortfolioPerformanceHistory.portfolio_id == portfolio_id)
            .order_by(desc(PortfolioPerformanceHistory.snapshot_date))
            .first()
        )

        # Get latest risk metrics
        latest_risk = (
            self.db.query(PortfolioRiskMetrics)
            .filter(PortfolioRiskMetrics.portfolio_id == portfolio_id)
            .order_by(desc(PortfolioRiskMetrics.calculation_date))
            .first()
        )

        # Get primary benchmark
        primary_benchmark = (
            self.db.query(PortfolioBenchmark)
            .filter(
                and_(
                    PortfolioBenchmark.portfolio_id == portfolio_id,
                    PortfolioBenchmark.is_primary == True,
                    PortfolioBenchmark.is_active == True,
                )
            )
            .first()
        )

        # Build summary
        summary_data = {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "calculation_date": datetime.utcnow(),
        }

        if latest_snapshot:
            summary_data.update(
                {
                    "total_value": latest_snapshot.total_value,
                    "total_cost_basis": latest_snapshot.total_cost_basis,
                    "total_unrealized_pnl": latest_snapshot.total_unrealized_pnl,
                    "total_unrealized_pnl_percent": latest_snapshot.total_unrealized_pnl_percent,
                    "total_return": latest_snapshot.cumulative_return,
                    "annualized_return": latest_snapshot.annualized_return,
                    "volatility": latest_snapshot.volatility,
                    "sharpe_ratio": latest_snapshot.sharpe_ratio,
                    "max_drawdown": latest_snapshot.max_drawdown,
                    "var_95_1d": latest_snapshot.var_95,
                    "beta": latest_snapshot.beta,
                    "alpha": latest_snapshot.alpha,
                }
            )

        if latest_risk:
            summary_data.update(
                {
                    "risk_level": latest_risk.risk_level,
                    "risk_score": latest_risk.risk_score,
                    "concentration_risk": latest_risk.concentration_risk,
                    "effective_number_of_assets": latest_risk.effective_number_of_assets,
                }
            )

        if primary_benchmark:
            summary_data.update(
                {
                    "benchmark_name": primary_benchmark.benchmark_name,
                    "excess_return": primary_benchmark.excess_return,
                    "tracking_error": primary_benchmark.tracking_error,
                    "information_ratio": primary_benchmark.information_ratio,
                }
            )

        return PortfolioAnalyticsSummary(**summary_data)

    # Rebalancing Recommendations
    def get_rebalancing_recommendation(self, portfolio_id: int) -> PortfolioRebalancingRecommendation:
        """Get rebalancing recommendations for a portfolio."""
        # Analyze current allocation
        allocation_analysis = self.analyze_portfolio_allocation(portfolio_id)

        # Determine if rebalancing is needed
        if allocation_analysis.total_drift < 5:  # Less than 5% total drift
            trigger_reason = "No rebalancing needed - within acceptable drift limits"
            priority = "low"
            urgency_score = 0
        elif allocation_analysis.max_drift < 10:  # Max single asset drift < 10%
            trigger_reason = "Moderate drift detected - consider rebalancing"
            priority = "medium"
            urgency_score = 50
        else:
            trigger_reason = "Significant drift detected - rebalancing recommended"
            priority = "high"
            urgency_score = 80

        # Calculate estimated costs and tax impact
        estimated_cost = sum(
            action["value_change"] * 0.001 for action in allocation_analysis.rebalancing_actions
        ) if allocation_analysis.rebalancing_actions else 0  # 0.1% transaction cost
        tax_impact = sum(
            action["value_change"] * 0.15 for action in allocation_analysis.rebalancing_actions
            if action["action"] == "sell"
        ) if allocation_analysis.rebalancing_actions else 0  # 15% capital gains tax on sales

        # Determine recommended timing
        if urgency_score > 70:
            recommended_timing = "immediate"
        elif urgency_score > 40:
            recommended_timing = "within_1_week"
        else:
            recommended_timing = "next_rebalancing_cycle"

        return PortfolioRebalancingRecommendation(
            portfolio_id=portfolio_id,
            recommendation_date=datetime.utcnow(),
            trigger_reason=trigger_reason,
            current_drift=allocation_analysis.total_drift,
            rebalancing_actions=allocation_analysis.rebalancing_actions,
            estimated_cost=Decimal(str(estimated_cost)),
            tax_impact=Decimal(str(tax_impact)),
            expected_allocations=allocation_analysis.target_allocations,
            priority=priority,
            recommended_timing=recommended_timing,
            urgency_score=Decimal(str(urgency_score)),
        )
