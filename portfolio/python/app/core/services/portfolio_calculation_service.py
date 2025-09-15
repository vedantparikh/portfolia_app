"""
Portfolio Calculation Service

Comprehensive service for calculating portfolio performance metrics including:
- CAGR (Compound Annual Growth Rate)
- XIRR (Extended Internal Rate of Return)
- TWR (Time-Weighted Return)
- MWR (Money-Weighted Return)

Supports period-based calculations and benchmark comparisons.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import pyxirr  # type: ignore
from sqlalchemy.orm import Session

from app.core.database.models import (
    Asset,
    Portfolio,
    PortfolioAsset,
    Transaction,
    TransactionType,
)
from app.core.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)


class PeriodType:
    """Standard period types for calculations."""

    LAST_3_MONTHS = "3m"
    LAST_6_MONTHS = "6m"
    LAST_1_YEAR = "1y"
    LAST_2_YEARS = "2y"
    LAST_3_YEARS = "3y"
    LAST_5_YEARS = "5y"
    YTD = "ytd"
    INCEPTION = "inception"

    @classmethod
    def get_start_date(
        cls, period: str, base_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """Get start date for a given period."""
        if base_date is None:
            base_date = datetime.now(timezone.utc)

        if period == cls.LAST_3_MONTHS:
            return base_date - timedelta(days=90)
        elif period == cls.LAST_6_MONTHS:
            return base_date - timedelta(days=180)
        elif period == cls.LAST_1_YEAR:
            return base_date - timedelta(days=365)
        elif period == cls.LAST_2_YEARS:
            return base_date - timedelta(days=730)
        elif period == cls.LAST_3_YEARS:
            return base_date - timedelta(days=1095)
        elif period == cls.LAST_5_YEARS:
            return base_date - timedelta(days=1825)
        elif period == cls.YTD:
            return datetime(base_date.year, 1, 1)
        elif period == cls.INCEPTION:
            return None  # No start date filter
        else:
            raise ValueError(f"Unknown period type: {period}")


class PortfolioCalculationService:
    """Service for comprehensive portfolio performance calculations."""

    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService()

    async def calculate_portfolio_performance(
        self,
        portfolio_id: int,
        user_id: int,
        period: str = PeriodType.INCEPTION,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive portfolio performance metrics.

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID for ownership verification
            period: Period for calculation
            end_date: End date for calculation (defaults to now)

        Returns:
            Dictionary containing all performance metrics
        """
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        start_date = PeriodType.get_start_date(period, end_date)

        # Get portfolio and verify ownership
        portfolio = self._get_portfolio(portfolio_id, user_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found or not accessible")

        # Get transactions for the period
        transactions = self._get_transactions(portfolio_id, start_date, end_date)
        if not transactions:
            return self._empty_performance_result(portfolio_id, period)

        # Get current portfolio value
        current_value = self._get_current_portfolio_value(portfolio_id)

        # Calculate different return metrics
        cagr = await self._calculate_cagr(
            portfolio_id, transactions, current_value, start_date, end_date
        )
        xirr_value = self._calculate_xirr(transactions, current_value, end_date)
        twr = await self._calculate_twr(
            portfolio_id, transactions, current_value, start_date, end_date
        )
        mwr = self._calculate_mwr(transactions, current_value, start_date, end_date)

        # Calculate additional metrics
        volatility = await self._calculate_volatility(
            portfolio_id, start_date, end_date
        )
        sharpe_ratio = self._calculate_sharpe_ratio(twr, volatility)
        max_drawdown = await self._calculate_max_drawdown(
            portfolio_id, start_date, end_date
        )

        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "current_value": current_value,
            "metrics": {
                "cagr": cagr,
                "xirr": xirr_value,
                "twr": twr,
                "mwr": mwr,
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
            },
            "calculation_date": datetime.now(timezone.utc).isoformat(),
        }

    async def calculate_asset_performance(
        self,
        portfolio_id: int,
        asset_id: int,
        user_id: int,
        period: str = PeriodType.INCEPTION,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Calculate performance metrics for a specific asset within a portfolio.

        Args:
            portfolio_id: Portfolio ID
            asset_id: Asset ID
            user_id: User ID for ownership verification
            period: Period for calculation
            end_date: End date for calculation

        Returns:
            Dictionary containing asset performance metrics
        """
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        start_date = PeriodType.get_start_date(period, end_date)

        # Verify portfolio ownership
        portfolio = self._get_portfolio(portfolio_id, user_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found or not accessible")

        # Get asset transactions for the period
        asset_transactions = self._get_asset_transactions(
            portfolio_id, asset_id, start_date, end_date
        )

        if not asset_transactions:
            return self._empty_asset_performance_result(portfolio_id, asset_id, period)

        # Get current asset value in portfolio
        current_asset_value = self._get_current_asset_value(portfolio_id, asset_id)

        # Calculate metrics for the asset
        cagr = await self._calculate_asset_cagr(
            portfolio_id, asset_transactions, current_asset_value, start_date, end_date
        )
        xirr_value = self._calculate_asset_xirr(
            asset_transactions, current_asset_value, end_date
        )
        twr = await self._calculate_asset_twr(
            portfolio_id, asset_transactions, current_asset_value, start_date, end_date
        )
        mwr = self._calculate_asset_mwr(
            asset_transactions, current_asset_value, start_date, end_date
        )

        # Get asset information
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()

        return {
            "portfolio_id": portfolio_id,
            "asset_id": asset_id,
            "asset_symbol": asset.symbol if asset else "UNKNOWN",
            "asset_name": asset.name if asset else "Unknown Asset",
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "current_value": current_asset_value,
            "metrics": {
                "cagr": cagr,
                "xirr": xirr_value,
                "twr": twr,
                "mwr": mwr,
            },
            "calculation_date": datetime.now(timezone.utc).isoformat(),
        }

    async def calculate_benchmark_performance(
        self,
        benchmark_symbol: str,
        investment_amounts: List[Tuple[datetime, float]],
        period: str = PeriodType.INCEPTION,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Calculate hypothetical performance if money was invested in benchmark.

        Args:
            benchmark_symbol: Benchmark symbol (e.g., '^GSPC' for S&P 500)
            investment_amounts: List of (date, amount) tuples representing investments
            period: Period for calculation
            end_date: End date for calculation

        Returns:
            Dictionary containing benchmark performance metrics
        """
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        start_date = PeriodType.get_start_date(period, end_date)

        # Filter investment amounts for the period
        if start_date:
            investment_amounts = [
                (date, amount)
                for date, amount in investment_amounts
                if date >= start_date and date <= end_date
            ]

        if not investment_amounts:
            return self._empty_benchmark_performance_result(benchmark_symbol, period)

        # Get benchmark price history
        try:
            price_data = await self.market_data_service.fetch_ticker_data(
                symbol=benchmark_symbol, period="max", interval="1d"
            )

            if price_data.empty:
                raise ValueError(
                    f"No price data available for benchmark {benchmark_symbol}"
                )

            # Calculate hypothetical portfolio value
            current_value = self._calculate_hypothetical_benchmark_value(
                investment_amounts, price_data, end_date
            )

            # Create synthetic transactions for benchmark calculations
            benchmark_transactions = self._create_benchmark_transactions(
                investment_amounts, price_data
            )

            # Calculate metrics
            cagr = self._calculate_benchmark_cagr(
                benchmark_transactions, current_value, start_date, end_date
            )
            xirr_value = self._calculate_benchmark_xirr(
                benchmark_transactions, current_value, end_date
            )
            twr = self._calculate_benchmark_twr(
                benchmark_transactions, current_value, start_date, end_date
            )
            mwr = self._calculate_benchmark_mwr(
                benchmark_transactions, current_value, start_date, end_date
            )

            return {
                "benchmark_symbol": benchmark_symbol,
                "period": period,
                "start_date": start_date,
                "end_date": end_date,
                "current_value": current_value,
                "total_invested": sum(amount for _, amount in investment_amounts),
                "metrics": {
                    "cagr": cagr,
                    "xirr": xirr_value,
                    "twr": twr,
                    "mwr": mwr,
                },
                "calculation_date": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error("Error calculating benchmark performance: %s", e)
            return self._empty_benchmark_performance_result(benchmark_symbol, period)

    async def compare_portfolio_to_benchmark(
        self,
        portfolio_id: int,
        user_id: int,
        benchmark_symbol: str,
        period: str = PeriodType.INCEPTION,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Compare portfolio performance to benchmark using same investment schedule.

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID for ownership verification
            benchmark_symbol: Benchmark symbol
            period: Period for comparison
            end_date: End date for comparison

        Returns:
            Dictionary containing comparison metrics
        """
        # Get portfolio performance
        portfolio_performance = await self.calculate_portfolio_performance(
            portfolio_id, user_id, period, end_date
        )

        # Get portfolio transactions to replicate investment schedule
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        start_date = PeriodType.get_start_date(period, end_date)
        transactions = self._get_transactions(portfolio_id, start_date, end_date)

        # Create investment schedule for benchmark
        investment_amounts = []
        for transaction in transactions:
            if transaction.transaction_type == TransactionType.BUY:
                investment_amounts.append(
                    (transaction.transaction_date, float(transaction.total_amount))
                )
            elif transaction.transaction_type == TransactionType.SELL:
                investment_amounts.append(
                    (transaction.transaction_date, -float(transaction.total_amount))
                )

        # Get benchmark performance
        benchmark_performance = await self.calculate_benchmark_performance(
            benchmark_symbol, investment_amounts, period, end_date
        )

        # Calculate comparison metrics
        portfolio_metrics = portfolio_performance.get("metrics", {})
        benchmark_metrics = benchmark_performance.get("metrics", {})

        comparison = {
            "portfolio_performance": portfolio_performance,
            "benchmark_performance": benchmark_performance,
            "comparison": {
                "cagr_difference": self._safe_subtract(
                    portfolio_metrics.get("cagr"), benchmark_metrics.get("cagr")
                ),
                "xirr_difference": self._safe_subtract(
                    portfolio_metrics.get("xirr"), benchmark_metrics.get("xirr")
                ),
                "twr_difference": self._safe_subtract(
                    portfolio_metrics.get("twr"), benchmark_metrics.get("twr")
                ),
                "mwr_difference": self._safe_subtract(
                    portfolio_metrics.get("mwr"), benchmark_metrics.get("mwr")
                ),
                "outperforming": self._is_outperforming(
                    portfolio_metrics.get("twr"), benchmark_metrics.get("twr")
                ),
            },
        }

        return comparison

    # Helper methods for calculations

    async def _calculate_daily_portfolio_values(
        self,
        portfolio_id: int,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> pd.DataFrame:
        """
        Calculate daily portfolio values using historical price data from yfinance.

        This method reconstructs the portfolio value for each day by:
        1. Getting all transactions up to each date
        2. Calculating holdings for each date
        3. Getting historical prices for all assets
        4. Computing daily portfolio values

        Returns:
            DataFrame with columns: Date, PortfolioValue, DailyReturn
        """
        try:
            # Get all transactions for the portfolio
            all_transactions = self._get_transactions(portfolio_id, None, end_date)

            if not all_transactions:
                return pd.DataFrame()

            # Determine the actual start date
            if start_date is None:
                start_date = min(t.transaction_date for t in all_transactions).date()
            else:
                start_date = start_date.date()

            end_date = end_date.date()

            # Get all unique assets in the portfolio
            asset_ids = list(set(t.asset_id for t in all_transactions))
            assets = {}

            for asset_id in asset_ids:
                asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
                if asset:
                    assets[asset_id] = asset

            # Get historical price data for all assets
            asset_prices = {}
            for asset_id, asset in assets.items():
                try:
                    price_data = await self.market_data_service.fetch_ticker_data(
                        symbol=asset.symbol, period="max", interval="1d"
                    )

                    if not price_data.empty:
                        # Convert to proper format and index by date
                        price_data["Date"] = pd.to_datetime(price_data["Date"]).dt.date
                        price_data = price_data.set_index("Date")
                        asset_prices[asset_id] = price_data

                except Exception as e:
                    logger.warning(
                        "Could not fetch price data for asset %s: %s", asset.symbol, e
                    )
                    continue

            if not asset_prices:
                logger.error("No price data available for any assets")
                return pd.DataFrame()

            # Create date range
            date_range = pd.date_range(start=start_date, end=end_date, freq="D")
            portfolio_values = []

            for current_date in date_range:
                current_date = current_date.date()

                # Skip weekends (markets are closed)
                if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    continue

                # Calculate holdings as of this date
                holdings = self._calculate_holdings_as_of_date(
                    all_transactions, current_date
                )

                if not holdings:
                    continue

                # Calculate portfolio value for this date
                portfolio_value = 0.0

                for asset_id, quantity in holdings.items():
                    if asset_id in asset_prices and quantity > 0:
                        # Get the price for this date (or closest available)
                        price = self._get_price_for_date(
                            asset_prices[asset_id], current_date
                        )

                        if price is not None:
                            portfolio_value += quantity * price

                if portfolio_value > 0:
                    portfolio_values.append(
                        {"Date": current_date, "PortfolioValue": portfolio_value}
                    )

            if not portfolio_values:
                return pd.DataFrame()

            # Create DataFrame and calculate daily returns
            df = pd.DataFrame(portfolio_values)
            df = df.sort_values("Date")

            # Calculate daily returns
            df["DailyReturn"] = df["PortfolioValue"].pct_change()

            # Remove the first row (NaN return)
            df = df.dropna()

            return df

        except Exception as e:
            logger.error("Error calculating daily portfolio values: %s", e)
            return pd.DataFrame()

    def _calculate_holdings_as_of_date(
        self,
        transactions: List[Transaction],
        as_of_date: datetime.date,
    ) -> Dict[int, float]:
        """
        Calculate asset holdings as of a specific date.

        Args:
            transactions: All transactions for the portfolio
            as_of_date: Date to calculate holdings for

        Returns:
            Dictionary mapping asset_id to quantity held
        """
        holdings = {}

        # Filter transactions up to the specified date
        relevant_transactions = [
            t for t in transactions if t.transaction_date.date() <= as_of_date
        ]

        # Sort by date to process in chronological order
        relevant_transactions.sort(key=lambda t: t.transaction_date)

        for transaction in relevant_transactions:
            asset_id = transaction.asset_id
            quantity = float(transaction.quantity)

            if asset_id not in holdings:
                holdings[asset_id] = 0.0

            if transaction.transaction_type == TransactionType.BUY:
                holdings[asset_id] += quantity
            elif transaction.transaction_type == TransactionType.SELL:
                holdings[asset_id] -= quantity

                # Remove asset if quantity becomes zero or negative
                if holdings[asset_id] <= 0:
                    holdings.pop(asset_id, None)

        return holdings

    def _get_price_for_date(
        self,
        price_data: pd.DataFrame,
        target_date: datetime.date,
    ) -> Optional[float]:
        """
        Get the closing price for a specific date, using the closest available date if exact date not found.

        Args:
            price_data: DataFrame with price data indexed by date
            target_date: Target date to get price for

        Returns:
            Closing price or None if not available
        """
        try:
            # Try exact date first
            if target_date in price_data.index:
                return float(price_data.loc[target_date, "Close"])

            # Find the closest date before target_date
            available_dates = price_data.index
            valid_dates = [d for d in available_dates if d <= target_date]

            if valid_dates:
                closest_date = max(valid_dates)
                return float(price_data.loc[closest_date, "Close"])

            return None

        except Exception as e:
            logger.warning("Error getting price for date %s: %s", target_date, e)
            return None

    async def _calculate_cagr(
        self,
        portfolio_id: int,
        transactions: List[Transaction],
        current_value: float,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """Calculate Compound Annual Growth Rate using actual market values."""
        try:
            # Get initial market value (not cost basis) at period start
            initial_value = await self._calculate_initial_market_value(
                portfolio_id, transactions, start_date
            )

            if initial_value <= 0 or current_value <= 0:
                return None

            # Calculate period in years
            if start_date:
                years = (end_date - start_date).days / 365.25
            else:
                # Use first transaction date
                first_transaction = min(transactions, key=lambda t: t.transaction_date)
                years = (end_date - first_transaction.transaction_date).days / 365.25

            if years <= 0:
                return None

            # CAGR = (Ending Value / Beginning Value)^(1/number of years) - 1
            cagr = (current_value / initial_value) ** (1 / years) - 1
            return float(cagr * 100)  # Return as percentage

        except Exception as e:
            logger.error("Error calculating CAGR: %s", e)
            return None

    def _calculate_xirr(
        self,
        transactions: List[Transaction],
        current_value: float,
        end_date: datetime,
    ) -> Optional[float]:
        """Calculate Extended Internal Rate of Return using pyxirr."""
        try:
            # Prepare cash flows for XIRR calculation
            dates = []
            amounts = []

            # Add all transactions as cash flows
            for transaction in transactions:
                dates.append(transaction.transaction_date)
                if transaction.transaction_type == TransactionType.BUY:
                    amounts.append(
                        -float(transaction.total_amount)
                    )  # Negative for outflows
                elif transaction.transaction_type == TransactionType.SELL:
                    amounts.append(
                        float(transaction.total_amount)
                    )  # Positive for inflows

            # Add current value as final inflow
            dates.append(end_date)
            amounts.append(current_value)

            if len(dates) < 2:
                return None

            # Calculate XIRR
            xirr_result = pyxirr.xirr(dates, amounts)

            if xirr_result is None:
                return None

            return float(xirr_result * 100)  # Return as percentage

        except Exception as e:
            logger.error("Error calculating XIRR: %s", e)
            return None

    async def _calculate_twr(
        self,
        portfolio_id: int,
        transactions: List[Transaction],
        current_value: float,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """
        Calculate Time-Weighted Return using daily portfolio values.

        TWR eliminates the impact of cash flows by calculating returns
        between transaction dates and geometrically linking them.
        """
        try:
            # Get daily portfolio values
            daily_values = await self._calculate_daily_portfolio_values(
                portfolio_id, start_date, end_date
            )

            if daily_values.empty or len(daily_values) < 2:
                logger.warning(
                    "Insufficient data for TWR calculation, using simple method"
                )
                return await self._calculate_simple_twr(
                    portfolio_id, transactions, current_value, start_date, end_date
                )

            # Get transaction dates for cash flow adjustments
            transaction_dates = set()
            for transaction in transactions:
                if start_date is None or transaction.transaction_date >= start_date:
                    if transaction.transaction_date <= end_date:
                        transaction_dates.add(transaction.transaction_date.date())

            # Calculate TWR by geometrically linking daily returns
            # but adjusting for cash flows on transaction dates
            daily_returns = daily_values["DailyReturn"].dropna()

            if len(daily_returns) == 0:
                return None

            # For precise TWR, we should adjust for cash flows
            # For now, use the geometric mean of daily returns
            # This is a good approximation when cash flows are small relative to portfolio size

            # Calculate cumulative return
            cumulative_return = (1 + daily_returns).prod() - 1

            # Annualize if period is more than one year
            days = len(daily_returns)
            if days > 252:  # More than one trading year
                years = days / 252
                twr = ((1 + cumulative_return) ** (1 / years)) - 1
            else:
                twr = cumulative_return

            return float(twr * 100)  # Return as percentage

        except Exception as e:
            logger.error("Error calculating TWR: %s", e)
            return await self._calculate_simple_twr(
                portfolio_id, transactions, current_value, start_date, end_date
            )

    async def _calculate_simple_twr(
        self,
        portfolio_id: int,
        transactions: List[Transaction],
        current_value: float,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """Fallback simple TWR calculation using actual market values when daily data is not available."""
        try:
            # Use actual market value at period start, not cost basis
            initial_value = await self._calculate_initial_market_value(
                portfolio_id, transactions, start_date
            )
            if initial_value <= 0:
                return None

            # Simple TWR calculation using market values
            total_return = (current_value / initial_value) - 1

            # Annualize if period is more than one year
            if start_date:
                years = (end_date - start_date).days / 365.25
            else:
                first_transaction = min(transactions, key=lambda t: t.transaction_date)
                years = (end_date - first_transaction.transaction_date).days / 365.25

            if years > 1:
                twr = ((1 + total_return) ** (1 / years)) - 1
            else:
                twr = total_return

            return float(twr * 100)  # Return as percentage

        except Exception as e:
            logger.error("Error calculating simple TWR: %s", e)
            return None

    def _calculate_mwr(
        self,
        transactions: List[Transaction],
        current_value: float,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """Calculate Money-Weighted Return (same as XIRR for this implementation)."""
        # MWR is essentially the same as XIRR for most practical purposes
        return self._calculate_xirr(transactions, current_value, end_date)

    async def _calculate_volatility(
        self,
        portfolio_id: int,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """
        Calculate portfolio volatility using daily returns from historical data.

        Returns annualized volatility as a percentage.
        """
        try:
            # Get daily portfolio values
            daily_values = await self._calculate_daily_portfolio_values(
                portfolio_id, start_date, end_date
            )

            if daily_values.empty or len(daily_values) < 2:
                logger.warning("Insufficient data for volatility calculation")
                return None

            # Calculate daily returns (already calculated in daily_values)
            daily_returns = daily_values["DailyReturn"].dropna()

            if len(daily_returns) < 2:
                return None

            # Calculate standard deviation of daily returns
            daily_volatility = daily_returns.std()

            # Annualize volatility (assuming 252 trading days per year)
            annualized_volatility = daily_volatility * np.sqrt(252)

            # Convert to percentage
            return float(annualized_volatility * 100)

        except Exception as e:
            logger.error("Error calculating volatility: %s", e)
            return None

    def _calculate_sharpe_ratio(
        self,
        annual_return: Optional[float],
        volatility: Optional[float],
        risk_free_rate: float = 2.0,
    ) -> Optional[float]:
        """Calculate Sharpe ratio."""
        try:
            if annual_return is None or volatility is None or volatility == 0:
                return None

            # Sharpe Ratio = (Portfolio Return - Risk-free Rate) / Portfolio Volatility
            sharpe = (annual_return - risk_free_rate) / volatility
            return float(sharpe)

        except Exception as e:
            logger.error("Error calculating Sharpe ratio: %s", e)
            return None

    async def _calculate_max_drawdown(
        self,
        portfolio_id: int,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """
        Calculate maximum drawdown using daily portfolio values.

        Maximum drawdown is the largest peak-to-trough decline in portfolio value.
        Returns the drawdown as a percentage.
        """
        try:
            # Get daily portfolio values
            daily_values = await self._calculate_daily_portfolio_values(
                portfolio_id, start_date, end_date
            )

            if daily_values.empty or len(daily_values) < 2:
                logger.warning("Insufficient data for max drawdown calculation")
                return None

            portfolio_values = daily_values["PortfolioValue"]

            # Calculate running maximum (peak values)
            running_max = portfolio_values.expanding().max()

            # Calculate drawdown at each point
            drawdowns = (portfolio_values - running_max) / running_max

            # Find maximum drawdown (most negative value)
            max_drawdown = drawdowns.min()

            # Convert to positive percentage
            return float(abs(max_drawdown) * 100)

        except Exception as e:
            logger.error("Error calculating max drawdown: %s", e)
            return None

    # Asset-specific calculation methods (similar to portfolio methods but for single assets)

    async def _calculate_asset_cagr(
        self,
        portfolio_id: int,
        transactions: List[Transaction],
        current_value: float,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """Calculate CAGR for a specific asset."""
        # For individual assets, we'll use cost basis as fallback since we don't have
        # individual asset daily values. This is a limitation that would require
        # asset-specific daily value tracking to fix properly.
        try:
            initial_value = self._calculate_cost_basis_at_date(transactions, start_date)

            if initial_value <= 0 or current_value <= 0:
                return None

            # Calculate period in years
            if start_date:
                years = (end_date - start_date).days / 365.25
            else:
                # Use first transaction date
                first_transaction = min(transactions, key=lambda t: t.transaction_date)
                years = (end_date - first_transaction.transaction_date).days / 365.25

            if years <= 0:
                return None

            # CAGR = (Ending Value / Beginning Value)^(1/number of years) - 1
            cagr = (current_value / initial_value) ** (1 / years) - 1
            return float(cagr * 100)  # Return as percentage

        except Exception as e:
            logger.error("Error calculating asset CAGR: %s", e)
            return None

    def _calculate_asset_xirr(
        self,
        transactions: List[Transaction],
        current_value: float,
        end_date: datetime,
    ) -> Optional[float]:
        """Calculate XIRR for a specific asset."""
        return self._calculate_xirr(transactions, current_value, end_date)

    async def _calculate_asset_twr(
        self,
        portfolio_id: int,
        transactions: List[Transaction],
        current_value: float,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """Calculate TWR for a specific asset."""
        # For individual assets, we use cost basis since we don't track daily asset values
        # This is a limitation - proper asset TWR would require daily asset value tracking
        try:
            initial_value = self._calculate_cost_basis_at_date(transactions, start_date)
            if initial_value <= 0:
                return None

            # Simple TWR calculation using cost basis (limitation)
            total_return = (current_value / initial_value) - 1

            # Annualize if period is more than one year
            if start_date:
                years = (end_date - start_date).days / 365.25
            else:
                first_transaction = min(transactions, key=lambda t: t.transaction_date)
                years = (end_date - first_transaction.transaction_date).days / 365.25

            if years > 1:
                twr = ((1 + total_return) ** (1 / years)) - 1
            else:
                twr = total_return

            return float(twr * 100)  # Return as percentage

        except Exception as e:
            logger.error("Error calculating asset TWR: %s", e)
            return None

    def _calculate_asset_mwr(
        self,
        transactions: List[Transaction],
        current_value: float,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """Calculate MWR for a specific asset."""
        return self._calculate_mwr(transactions, current_value, start_date, end_date)

    # Benchmark calculation methods

    def _calculate_hypothetical_benchmark_value(
        self,
        investment_amounts: List[Tuple[datetime, float]],
        price_data: pd.DataFrame,
        end_date: datetime,
    ) -> float:
        """Calculate current value of hypothetical benchmark investment."""
        try:
            total_shares = 0.0

            for invest_date, amount in investment_amounts:
                # Find closest price to investment date
                price_row = self._find_closest_price(price_data, invest_date)
                if price_row is not None:
                    price = float(price_row["Close"])
                    if amount > 0:  # Buy
                        shares = amount / price
                        total_shares += shares
                    else:  # Sell
                        shares = abs(amount) / price
                        total_shares -= shares

            # Get current price
            latest_price_row = price_data.iloc[0]  # Data is sorted descending
            current_price = float(latest_price_row["Close"])

            return total_shares * current_price

        except Exception as e:
            logger.error("Error calculating hypothetical benchmark value: %s", e)
            return 0.0

    def _create_benchmark_transactions(
        self,
        investment_amounts: List[Tuple[datetime, float]],
        price_data: pd.DataFrame,
    ) -> List[Dict[str, Any]]:
        """Create synthetic transactions for benchmark calculations."""
        transactions = []

        for invest_date, amount in investment_amounts:
            price_row = self._find_closest_price(price_data, invest_date)
            if price_row is not None:
                price = float(price_row["Close"])
                transactions.append(
                    {
                        "transaction_date": invest_date,
                        "total_amount": amount,
                        "price": price,
                        "transaction_type": "BUY" if amount > 0 else "SELL",
                    }
                )

        return transactions

    def _calculate_benchmark_cagr(
        self,
        transactions: List[Dict[str, Any]],
        current_value: float,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """Calculate CAGR for benchmark."""
        try:
            # Calculate net investment (BUY + SELL)
            # Note: BUY amounts are positive (+1000), SELL amounts are already negative (-800)
            # So we simply sum them: +1000 + (-800) = +200 (correct net investment)
            net_investment = sum(t["total_amount"] for t in transactions)

            if net_investment <= 0 or current_value <= 0:
                return None

            if start_date:
                years = (end_date - start_date).days / 365.25
            else:
                first_transaction = min(
                    transactions, key=lambda t: t["transaction_date"]
                )
                years = (end_date - first_transaction["transaction_date"]).days / 365.25

            if years <= 0:
                return None

            cagr = (current_value / net_investment) ** (1 / years) - 1
            return float(cagr * 100)

        except Exception as e:
            logger.error("Error calculating benchmark CAGR: %s", e)
            return None

    def _calculate_benchmark_xirr(
        self,
        transactions: List[Dict[str, Any]],
        current_value: float,
        end_date: datetime,
    ) -> Optional[float]:
        """Calculate XIRR for benchmark."""
        try:
            dates = [t["transaction_date"] for t in transactions]
            # Fix: Simply invert all amounts since they're already correctly signed
            # BUY (+1000) becomes -1000 (outflow)
            # SELL (-800) becomes +800 (inflow)
            amounts = [-t["total_amount"] for t in transactions]

            dates.append(end_date)
            amounts.append(current_value)

            if len(dates) < 2:
                return None

            xirr_result = pyxirr.xirr(dates, amounts)
            return float(xirr_result * 100) if xirr_result is not None else None

        except Exception as e:
            logger.error("Error calculating benchmark XIRR: %s", e)
            return None

    def _calculate_benchmark_twr(
        self,
        transactions: List[Dict[str, Any]],
        current_value: float,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """Calculate TWR for benchmark."""
        try:
            # Calculate net investment (BUY + SELL)
            # Note: BUY amounts are positive (+1000), SELL amounts are already negative (-800)
            # So we simply sum them: +1000 + (-800) = +200 (correct net investment)
            net_investment = sum(t["total_amount"] for t in transactions)

            if net_investment <= 0:
                return None

            total_return = (current_value / net_investment) - 1

            if start_date:
                years = (end_date - start_date).days / 365.25
            else:
                first_transaction = min(
                    transactions, key=lambda t: t["transaction_date"]
                )
                years = (end_date - first_transaction["transaction_date"]).days / 365.25

            if years > 1:
                twr = ((1 + total_return) ** (1 / years)) - 1
            else:
                twr = total_return

            return float(twr * 100)

        except Exception as e:
            logger.error("Error calculating benchmark TWR: %s", e)
            return None

    def _calculate_benchmark_mwr(
        self,
        transactions: List[Dict[str, Any]],
        current_value: float,
        _start_date: Optional[datetime],
        end_date: datetime,
    ) -> Optional[float]:
        """Calculate MWR for benchmark."""
        return self._calculate_benchmark_xirr(transactions, current_value, end_date)

    # Utility methods

    def _get_portfolio(self, portfolio_id: int, user_id: int) -> Optional[Portfolio]:
        """Get portfolio and verify ownership."""
        return (
            self.db.query(Portfolio)
            .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
            .first()
        )

    def _get_transactions(
        self,
        portfolio_id: int,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> List[Transaction]:
        """Get transactions for a portfolio within a date range."""
        query = self.db.query(Transaction).filter(
            Transaction.portfolio_id == portfolio_id,
            Transaction.transaction_date <= end_date,
        )

        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)

        return query.order_by(Transaction.transaction_date).all()

    def _get_asset_transactions(
        self,
        portfolio_id: int,
        asset_id: int,
        start_date: Optional[datetime],
        end_date: datetime,
    ) -> List[Transaction]:
        """Get transactions for a specific asset within a portfolio."""
        query = self.db.query(Transaction).filter(
            Transaction.portfolio_id == portfolio_id,
            Transaction.asset_id == asset_id,
            Transaction.transaction_date <= end_date,
        )

        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)

        return query.order_by(Transaction.transaction_date).all()

    def _get_current_portfolio_value(self, portfolio_id: int) -> float:
        """Get current total value of portfolio."""
        try:
            assets = (
                self.db.query(PortfolioAsset)
                .filter(PortfolioAsset.portfolio_id == portfolio_id)
                .all()
            )

            total_value = 0.0
            for asset in assets:
                if asset.current_value is not None and asset.current_value > 0:
                    total_value += float(asset.current_value)
                elif asset.cost_basis_total is not None:
                    # Fallback to cost basis if current value is not available
                    total_value += float(asset.cost_basis_total)
                else:
                    logger.warning(
                        f"No value available for asset {asset.asset_id} in portfolio {portfolio_id}"
                    )

            return total_value

        except Exception as e:
            logger.error("Error getting current portfolio value: %s", e)
            return 0.0

    def _get_current_asset_value(self, portfolio_id: int, asset_id: int) -> float:
        """Get current value of a specific asset in portfolio."""
        try:
            asset = (
                self.db.query(PortfolioAsset)
                .filter(
                    PortfolioAsset.portfolio_id == portfolio_id,
                    PortfolioAsset.asset_id == asset_id,
                )
                .first()
            )

            if asset:
                if asset.current_value is not None and asset.current_value > 0:
                    return float(asset.current_value)
                elif asset.cost_basis_total is not None:
                    # Fallback to cost basis if current value is not available
                    return float(asset.cost_basis_total)
                else:
                    logger.warning(
                        f"No value available for asset {asset_id} in portfolio {portfolio_id}"
                    )

            return 0.0

        except Exception as e:
            logger.error("Error getting current asset value: %s", e)
            return 0.0

    async def _calculate_initial_market_value(
        self,
        portfolio_id: int,
        transactions: List[Transaction],
        start_date: Optional[datetime],
    ) -> float:
        """Calculate actual market value of portfolio at period start date."""
        try:
            if start_date is None:
                # For inception period, use cost basis of first transaction
                if transactions:
                    first_transaction = min(
                        transactions, key=lambda t: t.transaction_date
                    )
                    return float(first_transaction.total_amount)
                return 0.0

            # Get daily portfolio values to find market value at start date
            daily_values = await self._calculate_daily_portfolio_values(
                portfolio_id, None, start_date
            )

            if daily_values.empty:
                # Fallback to cost basis calculation if no daily data available
                return self._calculate_cost_basis_at_date(transactions, start_date)

            # Find the portfolio value closest to start_date
            start_date_only = start_date.date()
            daily_values["Date"] = pd.to_datetime(daily_values["Date"]).dt.date

            # Get the last available value before or on start_date
            valid_dates = daily_values[daily_values["Date"] <= start_date_only]

            if not valid_dates.empty:
                return float(valid_dates.iloc[-1]["PortfolioValue"])
            else:
                # If no data before start_date, use cost basis
                return self._calculate_cost_basis_at_date(transactions, start_date)

        except Exception as e:
            logger.error("Error calculating initial market value: %s", e)
            # Fallback to cost basis calculation
            return self._calculate_cost_basis_at_date(transactions, start_date)

    def _calculate_cost_basis_at_date(
        self,
        transactions: List[Transaction],
        start_date: Optional[datetime],
    ) -> float:
        """Calculate cost basis (net investment) up to a specific date - fallback method."""
        try:
            if start_date:
                # Get transactions before start date to calculate cost basis
                initial_transactions = [
                    t for t in transactions if t.transaction_date < start_date
                ]
            else:
                # Use the first transaction as starting point
                if transactions:
                    first_transaction = min(
                        transactions, key=lambda t: t.transaction_date
                    )
                    return float(first_transaction.total_amount)
                return 0.0

            # Calculate net investment up to start date
            net_investment = 0.0
            for transaction in initial_transactions:
                if transaction.transaction_type == TransactionType.BUY:
                    net_investment += float(transaction.total_amount)
                elif transaction.transaction_type == TransactionType.SELL:
                    net_investment -= float(transaction.total_amount)

            return max(net_investment, 0.0)

        except Exception as e:
            logger.error("Error calculating cost basis at date: %s", e)
            return 0.0

    def _find_closest_price(
        self, price_data: pd.DataFrame, target_date: datetime
    ) -> Optional[pd.Series]:
        """Find the closest price data to a target date."""
        try:
            price_data["Date"] = pd.to_datetime(price_data["Date"])

            # Find the closest date
            closest_idx = (price_data["Date"] - target_date).abs().idxmin()
            return price_data.loc[closest_idx]

        except Exception as e:
            logger.error("Error finding closest price: %s", e)
            return None

    def _safe_subtract(self, a: Optional[float], b: Optional[float]) -> Optional[float]:
        """Safely subtract two optional float values."""
        if a is not None and b is not None:
            return a - b
        return None

    def _is_outperforming(
        self, portfolio_return: Optional[float], benchmark_return: Optional[float]
    ) -> Optional[bool]:
        """Check if portfolio is outperforming benchmark."""
        if portfolio_return is not None and benchmark_return is not None:
            return portfolio_return > benchmark_return
        return None

    def _empty_performance_result(
        self, portfolio_id: int, period: str
    ) -> Dict[str, Any]:
        """Return empty performance result."""
        return {
            "portfolio_id": portfolio_id,
            "period": period,
            "error": "No transactions found for the specified period",
            "metrics": {
                "cagr": None,
                "xirr": None,
                "twr": None,
                "mwr": None,
                "volatility": None,
                "sharpe_ratio": None,
                "max_drawdown": None,
            },
        }

    def _empty_asset_performance_result(
        self, portfolio_id: int, asset_id: int, period: str
    ) -> Dict[str, Any]:
        """Return empty asset performance result."""
        return {
            "portfolio_id": portfolio_id,
            "asset_id": asset_id,
            "period": period,
            "error": "No transactions found for the specified asset and period",
            "metrics": {
                "cagr": None,
                "xirr": None,
                "twr": None,
                "mwr": None,
            },
        }

    def _empty_benchmark_performance_result(
        self, benchmark_symbol: str, period: str
    ) -> Dict[str, Any]:
        """Return empty benchmark performance result."""
        return {
            "benchmark_symbol": benchmark_symbol,
            "period": period,
            "error": "No investment data or price data available",
            "metrics": {
                "cagr": None,
                "xirr": None,
                "twr": None,
                "mwr": None,
            },
        }
