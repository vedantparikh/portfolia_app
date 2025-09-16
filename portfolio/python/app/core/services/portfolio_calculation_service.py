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
            return datetime(base_date.year, 1, 1, tzinfo=timezone.utc)
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
        # Note: For accurate metrics, we often need all transactions up to end_date
        # to calculate initial values, even if the user only wants a specific period.
        # However, for XIRR, we only want transactions *within* the period + the initial state.
        # For simplicity in this structure, we get transactions relevant to the period.
        # Let's get ALL transactions and let calculators filter.
        all_transactions = self._get_transactions(portfolio_id, None, end_date)

        # Filter transactions that fall *within* the specified period for calculations
        if start_date:
            period_transactions = [
                t for t in all_transactions if t.transaction_date >= start_date
            ]
        else:
            period_transactions = all_transactions

        if not period_transactions:
            # Still check if there are any transactions at all
            if not all_transactions:
                return self._empty_performance_result(portfolio_id, period)
            # If no transactions in the period, it means we are holding assets
            # bought before the period. period_transactions should be empty.

        # Get current portfolio value
        current_value = self._get_current_portfolio_value(portfolio_id)

        # Calculate different return metrics
        cagr = await self._calculate_cagr(
            portfolio_id, all_transactions, current_value, start_date, end_date
        )

        # XIRR calculation should use transactions relevant to the period,
        # plus the market value at the start of the period as the initial outflow.
        xirr_value = await self._calculate_period_xirr(
            portfolio_id, all_transactions, current_value, start_date, end_date
        )

        twr = await self._calculate_twr(
            portfolio_id, all_transactions, current_value, start_date, end_date
        )

        # MWR is just XIRR.
        mwr = xirr_value

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

        # Get ALL asset transactions up to end_date
        all_asset_transactions = self._get_asset_transactions(
            portfolio_id, asset_id, None, end_date
        )

        if not all_asset_transactions:
            return self._empty_asset_performance_result(portfolio_id, asset_id, period)

        # Filter for transactions within the period (needed for period XIRR)
        if start_date:
            period_transactions = [
                t for t in all_asset_transactions if t.transaction_date >= start_date
            ]
        else:
            period_transactions = all_asset_transactions

        # Get current asset value in portfolio
        current_asset_value = self._get_current_asset_value(portfolio_id, asset_id)

        # Calculate metrics for the asset
        # Note: These calculations are corrected to use the asset's MARKET VALUE
        # at the start of the period, not its cost basis.
        cagr = await self._calculate_asset_cagr(
            all_asset_transactions, current_asset_value, start_date, end_date
        )

        # Proper XIRR calculation for an asset
        xirr_value = await self._calculate_asset_period_xirr(
            all_asset_transactions, current_asset_value, start_date, end_date
        )

        twr = await self._calculate_asset_twr(
            all_asset_transactions, current_asset_value, start_date, end_date
        )

        mwr = xirr_value  # MWR is XIRR

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
        # We need ALL investments up to end_date to calculate total shares
        all_investments = [
            (date, amount)
            for date, amount in investment_amounts
            if date <= end_date
        ]

        if not all_investments:
            return self._empty_benchmark_performance_result(benchmark_symbol, period)

        # Get investments relevant to the period (for period-specific XIRR)
        if start_date:
            period_investments = [
                (date, amount)
                for date, amount in all_investments
                if date >= start_date
            ]
        else:
            period_investments = all_investments

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
                all_investments, price_data, end_date
            )

            # Create synthetic transactions for benchmark calculations
            benchmark_transactions_all = self._create_benchmark_transactions(
                all_investments, price_data
            )

            # Calculate initial value at start_date
            if start_date:
                # Period calculation: Get market value at start_date
                initial_value = self._calculate_hypothetical_benchmark_value(
                    [t for t in all_investments if t[0] < start_date],
                    price_data,
                    start_date
                )
            else:
                # Inception calculation: Use first transaction amount, if it exists
                if benchmark_transactions_all:
                    initial_value = benchmark_transactions_all[0]['total_amount']
                else:
                    initial_value = 0.0  # No transactions, so initial value is 0

            # Calculate metrics
            cagr = self._calculate_benchmark_cagr(
                benchmark_transactions_all, current_value, start_date, end_date, initial_value
            )

            # Calculate period-specific XIRR
            xirr_value = self._calculate_benchmark_period_xirr(
                period_investments, initial_value, current_value, start_date, end_date
            )

            twr = self._calculate_benchmark_twr(
                benchmark_transactions_all, current_value, start_date, end_date, initial_value
            )

            mwr = xirr_value  # MWR is XIRR

            total_invested_period = sum(amount for _, amount in period_investments)

            return {
                "benchmark_symbol": benchmark_symbol,
                "period": period,
                "start_date": start_date,
                "end_date": end_date,
                "current_value": current_value,
                "initial_value_period": initial_value,
                "total_invested_period": total_invested_period,
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
            end_date = portfolio_performance.get("end_date", datetime.now(timezone.utc))

        # Get ALL transactions up to end date to build the full investment schedule
        transactions = self._get_transactions(portfolio_id, None, end_date)

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

        # Get benchmark performance for the same period
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
        Calculate daily portfolio values using historical price data.
        Returns:
            DataFrame with columns: Date, PortfolioValue, DailyReturn
        """
        try:
            # Get all transactions for the portfolio
            all_transactions = self._get_transactions(portfolio_id, None, end_date)
            if not all_transactions:
                return pd.DataFrame()

            # Determine the actual start date
            first_transaction_date = min(t.transaction_date for t in all_transactions)
            calc_start_date = first_transaction_date
            if start_date:
                # We need data from just before the period start to get the initial value
                calc_start_date = min(start_date - timedelta(days=7), first_transaction_date)

            calc_start_date_d = calc_start_date.date()
            end_date_d = end_date.date()

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
                        # *** FIX: ADDED .sort_index() TO PREVENT PANDAS asof ERROR ***
                        price_data = price_data.set_index("Date").sort_index()
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
            date_range = pd.date_range(start=calc_start_date_d, end=end_date_d, freq="D")
            portfolio_values = []
            for current_date in date_range:
                current_date = current_date.date()
                # Calculate holdings as of this date
                holdings = self._calculate_holdings_as_of_date(
                    all_transactions, current_date
                )

                if not holdings:
                    # If no holdings, portfolio value is 0 (unless we track cash)
                    if portfolio_values:  # Only add if we already started tracking
                        portfolio_values.append(
                            {"Date": current_date, "PortfolioValue": 0.0}
                        )
                    continue

                # Calculate portfolio value for this date
                portfolio_value = 0.0
                valid_price_found = False
                for asset_id, quantity in holdings.items():
                    if asset_id in asset_prices and quantity > 0:
                        # Get the price for this date (or closest available)
                        price = self._get_price_for_date(
                            asset_prices[asset_id], current_date
                        )
                        if price is not None:
                            portfolio_value += quantity * price
                            valid_price_found = True

                if portfolio_value > 0 or valid_price_found:
                    portfolio_values.append(
                        {"Date": current_date, "PortfolioValue": portfolio_value}
                    )

            if not portfolio_values:
                return pd.DataFrame()

            # Create DataFrame and calculate daily returns
            df = pd.DataFrame(portfolio_values).drop_duplicates(subset=["Date"])
            df = df.sort_values("Date").set_index("Date")

            # Calculate daily returns, handling cash flows
            # To calculate pure daily return, we need to account for cash flows on transaction days.
            # (Value_End - Value_Start - CashFlow) / (Value_Start + CashFlow_In)
            # This complex logic is simplified here by using pct_change,
            # which assumes no intra-day cash flows (close-to-close).
            # This is standard for most retail volatility/drawdown calcs.
            df["DailyReturn"] = df["PortfolioValue"].pct_change()

            # Re-index to ensure all calendar days are present, then ffill values for weekends/holidays
            df = df.reindex(pd.date_range(start=df.index.min(), end=df.index.max(), freq='D'))
            df['PortfolioValue'] = df['PortfolioValue'].ffill()

            # Recalculate returns based on filled data, then drop NaNs
            df["DailyReturn"] = df["PortfolioValue"].pct_change().fillna(0)

            # Now, filter the DF to ONLY the user-requested period
            if start_date:
                df = df[df.index >= start_date.date()]

            df = df.dropna(subset=["PortfolioValue"])
            return df.reset_index().rename(columns={"index": "Date"})
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
        # Filter transactions up to and including the specified date
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

        # Clean up assets with zero or negative quantity
        final_holdings = {
            asset_id: qty
            for asset_id, qty in holdings.items()
            if qty > 1e-9  # Use small threshold for float comparison
        }
        return final_holdings

    def _get_price_for_date(
            self,
            price_data: pd.DataFrame,
            target_date: datetime.date,
    ) -> Optional[float]:
        """
        Get the closing price for a specific date, using forward filling logic.
        (Uses last known price if target_date is a weekend/holiday)
        Args:
            price_data: DataFrame with price data indexed by date (must be sorted)
            target_date: Target date to get price for
        Returns:
            Closing price or None if not available
        """
        try:
            # price_data index is assumed to be sorted datetime.date objects
            if target_date in price_data.index:
                return float(price_data.loc[target_date, "Close"])

            # Use asof to get the latest price available on or before the target date
            # This efficiently handles weekends and holidays by finding the last trading day.
            closest_price_row = price_data.asof(target_date)

            if closest_price_row is not None:
                return float(closest_price_row["Close"])

            # If no data is available before or on target_date (e.g., before IPO)
            return None
        except Exception as e:
            logger.warning("Error getting price for date %s: %s", target_date, e)
            return None

    async def _calculate_cagr(
            self,
            portfolio_id: int,
            transactions: List[Transaction],  # Pass ALL transactions
            current_value: float,
            start_date: Optional[datetime],
            end_date: datetime,
    ) -> Optional[float]:
        """
        Calculate Compound Annual Growth Rate (CAGR) or Simple Return.
        - Returns simple cumulative return for periods <= 1 year (like YTD).
        - Returns annualized CAGR for periods > 1 year.
        """
        try:
            # Get initial market value at period start
            initial_value = await self._calculate_initial_market_value(
                portfolio_id, transactions, start_date
            )

            if initial_value <= 0 or current_value < 0:
                # If initial value was 0 and current is > 0, return is infinite (or 100%?);
                # If initial > 0 and current is 0, return is -100%.
                # For simplicity, if initial is 0, we can't calculate a rate of return.
                if initial_value <= 0:
                    return None  # Cannot calculate return from 0
                if current_value <= 0:
                    return -100.0

            # Calculate period in years
            if start_date:
                calc_start_date = start_date
                years = (end_date - calc_start_date).days / 365.25
            else:
                # Use first transaction date for INCEPTION
                if not transactions:
                    return None
                first_transaction = min(transactions, key=lambda t: t.transaction_date)
                calc_start_date = first_transaction.transaction_date
                years = (end_date - calc_start_date).days / 365.25

            # Calculate simple total return first
            total_return = (current_value / initial_value) - 1

            if years <= 0:
                # If no time passed or invalid period, just return the simple change
                return float(total_return * 100)

            # *** FIX: Only annualize if period is > 1 year ***
            if years > 1:
                # Actual CAGR formula for multi-year periods
                annualized_return = ((1 + total_return) ** (1 / years)) - 1
            else:
                # For periods <= 1 year (like YTD), return the simple total return
                annualized_return = total_return

            return float(annualized_return * 100)  # Return as percentage
        except Exception as e:
            logger.error("Error calculating CAGR: %s", e)
            return None

    async def _calculate_period_xirr(
            self,
            portfolio_id: int,
            all_transactions: List[Transaction],
            current_value: float,
            start_date: Optional[datetime],
            end_date: datetime
    ) -> Optional[float]:
        """Calculate XIRR for a specific period (not just inception)."""
        try:
            dates = []
            amounts = []

            if start_date:
                # 1. Get Market Value at start_date. This is the initial "outflow"
                initial_value = await self._calculate_initial_market_value(
                    portfolio_id, all_transactions, start_date
                )

                if initial_value > 0:
                    dates.append(start_date)
                    amounts.append(-initial_value)  # Outflow

                # 2. Add all cash flows *within* the period
                period_transactions = [
                    t for t in all_transactions if t.transaction_date >= start_date
                ]
            else:
                # This is INCEPTION period. Use all transactions.
                period_transactions = all_transactions

            # Add transactions as cash flows
            for transaction in period_transactions:
                dates.append(transaction.transaction_date)
                if transaction.transaction_type == TransactionType.BUY:
                    amounts.append(
                        -float(transaction.total_amount)
                    )  # Negative for outflows
                elif transaction.transaction_type == TransactionType.SELL:
                    amounts.append(
                        float(transaction.total_amount)
                    )  # Positive for inflows

            # 3. Add current value as final inflow
            if current_value > 0 or not amounts:
                # Add current value even if 0, if there are transactions.
                # If no transactions and no start date, we need at least 2 points.
                # But if we have an initial value, we need this final point.
                dates.append(end_date)
                amounts.append(current_value)

            if len(dates) < 2:
                return None  # Not enough data points for XIRR

            # Check if all amounts are same sign (unless only 2 points)
            if len(dates) > 2:
                pos = any(a > 0 for a in amounts)
                neg = any(a < 0 for a in amounts)
                if not (pos and neg):
                    logger.warning("XIRR calculation failed: requires both positive and negative cash flows.")
                    return None  # pyxirr requires at least one pos and one neg flow

            # Calculate XIRR
            xirr_result = pyxirr.xirr(dates, amounts)
            if xirr_result is None:
                return None

            return float(xirr_result * 100)  # Return as percentage
        except Exception as e:
            logger.error("Error calculating Period XIRR: %s", e)
            return None

    async def _calculate_twr(
            self,
            portfolio_id: int,
            transactions: List[Transaction],  # Pass ALL transactions
            current_value: float,
            start_date: Optional[datetime],
            end_date: datetime,
    ) -> Optional[float]:
        """
        Calculate Time-Weighted Return using daily portfolio values.
        """
        try:
            # Get daily portfolio values *for the specified period*
            daily_values_df = await self._calculate_daily_portfolio_values(
                portfolio_id, start_date, end_date
            )

            if daily_values_df.empty or len(daily_values_df) < 2:
                logger.warning(
                    "Insufficient daily data for TWR calculation, using simple method"
                )
                return await self._calculate_simple_twr(
                    portfolio_id, transactions, current_value, start_date, end_date
                )

            # The daily_values_df "DailyReturn" column already approximates TWR component returns.
            # We just need to link them geometrically.
            # We must convert daily returns (0.01) to factors (1.01)
            daily_return_factors = 1 + daily_values_df["DailyReturn"].dropna()

            if len(daily_return_factors) == 0:
                return 0.0  # No returns calculated

            # Calculate cumulative return
            cumulative_return_factor = daily_return_factors.prod()
            cumulative_return = cumulative_return_factor - 1

            # Now, check if we need to annualize
            period_start_date = daily_values_df["Date"].min()
            period_end_date = daily_values_df["Date"].max()
            if isinstance(period_start_date, pd.Timestamp):
                period_start_date = period_start_date.date()
            if isinstance(period_end_date, pd.Timestamp):
                period_end_date = period_end_date.date()

            days_in_period = (period_end_date - period_start_date).days
            years = days_in_period / 365.25

            # *** FIX: Only annualize if period is > 1 year ***
            if years > 1:
                # This is the annualized TWR (same logic as CAGR)
                twr = (cumulative_return_factor ** (1 / years)) - 1
            else:
                # For periods <= 1 year (like YTD), return the simple cumulative return
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
            transactions: List[Transaction],  # Pass ALL transactions
            current_value: float,
            start_date: Optional[datetime],
            end_date: datetime,
    ) -> Optional[float]:
        """
        Fallback simple TWR (using Market Values).
        - Returns simple cumulative return for periods <= 1 year (like YTD).
        - Returns annualized CAGR-like calculation for periods > 1 year.
        This is essentially identical to our corrected _calculate_cagr method.
        """
        try:
            # Use actual market value at period start, not cost basis
            initial_value = await self._calculate_initial_market_value(
                portfolio_id, transactions, start_date
            )

            if initial_value <= 0 or current_value < 0:
                if initial_value <= 0:
                    return None
                if current_value <= 0:
                    return -100.0

            # Calculate period in years
            if start_date:
                calc_start_date = start_date
                years = (end_date - calc_start_date).days / 365.25
            else:
                # Use first transaction date
                if not transactions:
                    return None
                first_transaction = min(transactions, key=lambda t: t.transaction_date)
                calc_start_date = first_transaction.transaction_date
                years = (end_date - calc_start_date).days / 365.25

            # Calculate simple total return first
            total_return = (current_value / initial_value) - 1

            if years <= 0:
                return float(total_return * 100)

            # *** FIX: Only annualize if period is > 1 year ***
            if years > 1:
                # Annualized return
                twr = ((1 + total_return) ** (1 / years)) - 1
            else:
                # For periods <= 1 year (like YTD), return the simple total return
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
        """
        Calculate Money-Weighted Return (same as XIRR for this implementation).
        NOTE: This is deprecated in favor of the new _calculate_period_xirr method,
        which correctly handles period calculations. The main function now calls that instead.
        This function calculates INCEPTION XIRR only.
        """
        # MWR is essentially the same as XIRR. This calculates inception XIRR.
        try:
            dates = []
            amounts = []
            for transaction in transactions:  # Assumes ALL transactions passed
                dates.append(transaction.transaction_date)
                if transaction.transaction_type == TransactionType.BUY:
                    amounts.append(-float(transaction.total_amount))
                elif transaction.transaction_type == TransactionType.SELL:
                    amounts.append(float(transaction.total_amount))

            dates.append(end_date)
            amounts.append(current_value)

            if len(dates) < 2:
                return None

            xirr_result = pyxirr.xirr(dates, amounts)
            return float(xirr_result * 100) if xirr_result is not None else None
        except Exception as e:
            logger.error("Error calculating inception MWR/XIRR: %s", e)
            return None

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
            # Get daily portfolio values *for the specified period*
            daily_values = await self._calculate_daily_portfolio_values(
                portfolio_id, start_date, end_date
            )

            if daily_values.empty or len(daily_values) < 2:
                logger.warning("Insufficient data for volatility calculation")
                return None

            # Calculate daily returns
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
            # Note: annual_return is already a percentage, risk_free_rate is a percentage.
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
            # Get daily portfolio values for the period
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

            # Handle cases where running_max is 0 (replace inf with 0 or NaN)
            drawdowns.replace([np.inf, -np.inf], np.nan, inplace=True)
            drawdowns.fillna(0, inplace=True)

            # Find maximum drawdown (most negative value)
            max_drawdown = drawdowns.min()

            # Convert to positive percentage
            return float(abs(max_drawdown) * 100)
        except Exception as e:
            logger.error("Error calculating max drawdown: %s", e)
            return None

    # Asset-specific calculation methods
    async def _calculate_asset_cagr(
            self,
            transactions: List[Transaction],  # Pass ALL asset transactions
            current_value: float,
            start_date: Optional[datetime],
            end_date: datetime,
    ) -> Optional[float]:
        """
        Calculate CAGR or Simple Return for a specific asset.
        *** CORRECTED: Uses Market Value at period start, not cost basis ***
        """
        try:
            # Use market value at period start, not cost basis.
            asset_id_for_calc = transactions[0].asset_id if transactions else 0
            initial_value = await self._calculate_initial_asset_market_value(
                asset_id_for_calc, transactions, start_date
            )

            if initial_value <= 0 or current_value < 0:
                if initial_value <= 0:
                    return None
                if current_value <= 0:
                    return -100.0

            # Calculate period in years
            if start_date:
                calc_start_date = start_date
                years = (end_date - calc_start_date).days / 365.25
            else:
                # Use first transaction date
                if not transactions:
                    return None
                first_transaction = min(transactions, key=lambda t: t.transaction_date)
                calc_start_date = first_transaction.transaction_date
                years = (end_date - calc_start_date).days / 365.25

            # Calculate simple total return first
            total_return = (current_value / initial_value) - 1

            if years <= 0:
                return float(total_return * 100)

            # *** FIX: Only annualize if period is > 1 year ***
            if years > 1:
                # Actual CAGR formula
                annualized_return = ((1 + total_return) ** (1 / years)) - 1
            else:
                # For periods <= 1 year (like YTD), return the simple total return
                annualized_return = total_return

            return float(annualized_return * 100)  # Return as percentage
        except Exception as e:
            logger.error("Error calculating asset CAGR: %s", e)
            return None

    async def _calculate_asset_period_xirr(
            self,
            all_transactions: List[Transaction],  # ALL transactions for this asset
            current_value: float,
            start_date: Optional[datetime],
            end_date: datetime
    ) -> Optional[float]:
        """
        Calculate period-specific XIRR for a single asset.
        *** CORRECTED: Uses Market Value at period start, not cost basis ***
        """
        try:
            dates = []
            amounts = []

            if start_date:
                # 1. Get Market Value at start_date. This is the initial "outflow"
                # This is the FIX: Must use Market Value at period start, not Cost Basis.
                asset_id_for_calc = all_transactions[0].asset_id if all_transactions else 0
                initial_value = await self._calculate_initial_asset_market_value(
                    asset_id_for_calc, all_transactions, start_date
                )

                if initial_value > 0:
                    dates.append(start_date)
                    amounts.append(-initial_value)  # Outflow

                # 2. Add all cash flows *within* the period
                period_transactions = [
                    t for t in all_transactions if t.transaction_date >= start_date
                ]
            else:
                # This is INCEPTION period. Use all transactions.
                period_transactions = all_transactions

            # Add transactions as cash flows
            for transaction in period_transactions:
                dates.append(transaction.transaction_date)
                if transaction.transaction_type == TransactionType.BUY:
                    amounts.append(-float(transaction.total_amount))
                elif transaction.transaction_type == TransactionType.SELL:
                    amounts.append(float(transaction.total_amount))

            # 3. Add current value as final inflow
            dates.append(end_date)
            amounts.append(current_value)

            if len(dates) < 2:
                return None

            pos = any(a > 0 for a in amounts)
            neg = any(a < 0 for a in amounts)
            if not (pos and neg):
                logger.warning("Asset XIRR calculation failed: requires both positive and negative cash flows.")
                return None

            xirr_result = pyxirr.xirr(dates, amounts)
            return float(xirr_result * 100) if xirr_result is not None else None
        except Exception as e:
            logger.error("Error calculating asset period XIRR: %s", e)
            return None

    async def _calculate_asset_twr(
            self,
            transactions: List[Transaction],  # ALL asset transactions
            current_value: float,
            start_date: Optional[datetime],
            end_date: datetime,
    ) -> Optional[float]:
        """
        Calculate TWR for a specific asset.
        *** CORRECTED: Uses Market Value at period start, not cost basis. ***
        This calculation is identical to the corrected asset CAGR.
        """
        try:
            # Use market value at period start, not cost basis.
            asset_id_for_calc = transactions[0].asset_id if transactions else 0
            initial_value = await self._calculate_initial_asset_market_value(
                asset_id_for_calc, transactions, start_date
            )

            if initial_value <= 0 or current_value < 0:
                if initial_value <= 0:
                    return None
                if current_value <= 0:
                    return -100.0

            # Calculate period in years
            if start_date:
                calc_start_date = start_date
                years = (end_date - calc_start_date).days / 365.25
            else:
                if not transactions:
                    return None
                first_transaction = min(transactions, key=lambda t: t.transaction_date)
                calc_start_date = first_transaction.transaction_date
                years = (end_date - calc_start_date).days / 365.25

            # Calculate simple total return first
            total_return = (current_value / initial_value) - 1

            if years <= 0:
                return float(total_return * 100)

            # *** FIX: Only annualize if period is > 1 year ***
            if years > 1:
                # Annualized return
                twr = ((1 + total_return) ** (1 / years)) - 1
            else:
                # For periods <= 1 year (like YTD), return the simple total return
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
        """
        Calculate MWR for a specific asset.
        This is deprecated; the main function calls _calculate_asset_period_xirr directly.
        This function calculates INCEPTION XIRR only.
        """
        # This will always return INCEPTION XIRR, ignoring start_date.
        return self._calculate_asset_period_xirr(transactions, current_value, None, end_date)

    # Benchmark calculation methods
    def _calculate_hypothetical_benchmark_value(
            self,
            investment_amounts: List[Tuple[datetime, float]],  # ALL investments up to as_of_date
            price_data: pd.DataFrame,
            as_of_date: datetime,
    ) -> float:
        """Calculate value of hypothetical benchmark investment at a specific date."""
        try:
            total_shares = 0.0

            # Ensure price data has a proper date index
            if not isinstance(price_data.index, pd.DatetimeIndex):
                # This check handles if price_data was passed without index set
                price_data_indexed = price_data.copy()
                price_data_indexed["Date_col"] = pd.to_datetime(price_data_indexed["Date"])
                price_data_indexed = price_data_indexed.set_index('Date_col').sort_index()
            else:
                price_data_indexed = price_data.sort_index().copy()

            # # Ensure index is date objects, not datetimes, to match _get_price_for_date
            # if not price_data_indexed.empty and not isinstance(price_data_indexed.index[0], datetime.date):
            #     price_data_indexed.index = price_data_indexed.index.date

            for invest_date, amount in investment_amounts:
                if invest_date > as_of_date:
                    continue  # Ignore investments after the target date

                # Find closest price to investment date
                price = self._get_price_for_date(price_data_indexed, invest_date.date())

                if price is not None and price > 0:
                    shares = amount / price  # Amount is already signed (+ for BUY, - for SELL)
                    total_shares += shares
                else:
                    logger.warning(f"No price found for benchmark on or before {invest_date.date()}")

            # Get latest price at as_of_date
            current_price = self._get_price_for_date(price_data_indexed, as_of_date.date())

            if current_price is None:
                logger.error(f"No benchmark price data found at end date {as_of_date.date()}")
                return 0.0  # Cannot calculate value

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
        try:
            transactions = []

            # *** FIX: Use .copy() to prevent mutating the input DataFrame ***
            price_data_local = price_data.copy()

            # Ensure price data has a proper date index
            if not isinstance(price_data_local.index, pd.DatetimeIndex):
                price_data_local['Date_col'] = pd.to_datetime(price_data_local['Date'])
                price_data_local = price_data_local.set_index('Date_col').sort_index()
            else:
                price_data_local = price_data_local.sort_index()

            # Ensure index is date objects
            # if not price_data_local.empty and not isinstance(price_data_local.index[0], datetime.date):
            #     price_data_local.index = price_data_local.index.date

            for invest_date, amount in investment_amounts:
                # Use the local, formatted copy
                price = self._get_price_for_date(price_data_local, invest_date.date())
                if price is not None:
                    transactions.append(
                        {
                            "transaction_date": invest_date,
                            "total_amount": amount,
                            "price": price,
                            "transaction_type": "BUY" if amount > 0 else "SELL",
                        }
                    )
            return transactions
        except Exception as e:
            # If this helper fails, it must return an empty list, not crash the parent
            logger.error("Error creating benchmark transactions: %s", e)
            return []

    def _calculate_benchmark_cagr(
            self,
            transactions: List[Dict[str, Any]],  # ALL transactions
            current_value: float,
            start_date: Optional[datetime],
            end_date: datetime,
            initial_value: float  # Market value at start_date
    ) -> Optional[float]:
        """
        Calculate CAGR or Simple Return for benchmark.
        """
        try:
            if initial_value <= 0 or current_value < 0:
                if initial_value <= 0:
                    return None
                if current_value <= 0:
                    return -100.0

            if start_date:
                calc_start_date = start_date
                years = (end_date - calc_start_date).days / 365.25
            else:
                if not transactions:
                    return None
                first_transaction = min(
                    transactions, key=lambda t: t["transaction_date"]
                )
                calc_start_date = first_transaction["transaction_date"]
                years = (end_date - calc_start_date).days / 365.25

            total_return = (current_value / initial_value) - 1

            if years <= 0:
                return float(total_return * 100)

            # *** FIX: Only annualize if period is > 1 year ***
            if years > 1:
                annualized_return = ((1 + total_return) ** (1 / years)) - 1
            else:
                annualized_return = total_return

            return float(annualized_return * 100)
        except Exception as e:
            logger.error("Error calculating benchmark CAGR: %s", e)
            return None

    def _calculate_benchmark_period_xirr(
            self,
            period_investments: List[Tuple[datetime, float]],  # Investments *within* period
            initial_value: float,  # Market value at start of period
            current_value: float,
            start_date: Optional[datetime],
            end_date: datetime,
    ) -> Optional[float]:
        """Calculate period-specific XIRR for benchmark."""
        try:
            dates = []
            amounts = []

            # 1. Add initial value at start_date (if it exists)
            if start_date and initial_value > 0:
                dates.append(start_date)
                amounts.append(-initial_value)  # Outflow

            # 2. Add all investments within the period
            for invest_date, amount in period_investments:
                dates.append(invest_date)
                # BUY is positive amount, needs to be negative flow. SELL is negative amount, needs to be positive flow.
                amounts.append(-amount)

            # 3. Add final value
            dates.append(end_date)
            amounts.append(current_value)  # Inflow

            if len(dates) < 2:
                return None

            pos = any(a > 0 for a in amounts)
            neg = any(a < 0 for a in amounts)
            if not (pos and neg):
                logger.warning("Benchmark XIRR calculation failed: requires both positive and negative cash flows.")
                return None

            xirr_result = pyxirr.xirr(dates, amounts)
            return float(xirr_result * 100) if xirr_result is not None else None
        except Exception as e:
            logger.error("Error calculating benchmark XIRR: %s", e)
            return None

    def _calculate_benchmark_twr(
            self,
            transactions: List[Dict[str, Any]],  # ALL transactions
            current_value: float,
            start_date: Optional[datetime],
            end_date: datetime,
            initial_value: float  # Market value at start_date
    ) -> Optional[float]:
        """
        Calculate TWR for benchmark (identical to CAGR calc since we use market values).
        """
        try:
            if initial_value <= 0 or current_value < 0:
                if initial_value <= 0:
                    return None
                if current_value <= 0:
                    return -100.0

            if start_date:
                calc_start_date = start_date
                years = (end_date - calc_start_date).days / 365.25
            else:
                if not transactions:
                    return None
                first_transaction = min(
                    transactions, key=lambda t: t["transaction_date"]
                )
                calc_start_date = first_transaction["transaction_date"]
                years = (end_date - calc_start_date).days / 365.25

            total_return = (current_value / initial_value) - 1

            if years <= 0:
                return float(total_return * 100)

            # *** FIX: Only annualize if period is > 1 year ***
            if years > 1:
                annualized_return = ((1 + total_return) ** (1 / years)) - 1
            else:
                annualized_return = total_return

            return float(annualized_return * 100)
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
        """
        Calculate MWR for benchmark.
        This is deprecated; the main function calls _calculate_benchmark_period_xirr.
        This function calculates INCEPTION XIRR only.
        """
        try:
            dates = [t["transaction_date"] for t in transactions]
            amounts = [-t["total_amount"] for t in transactions]  # Invert amount sign

            dates.append(end_date)
            amounts.append(current_value)

            if len(dates) < 2:
                return None

            xirr_result = pyxirr.xirr(dates, amounts)
            return float(xirr_result * 100) if xirr_result is not None else None
        except Exception as e:
            logger.error("Error calculating benchmark inception MWR: %s", e)
            return None

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
        """
        Get transactions for a portfolio.
        If start_date is provided, filter from that date.
        If start_date is None, get ALL transactions up to end_date.
        """
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
        """
        Get transactions for a specific asset.
        If start_date is None, get ALL transactions up to end_date.
        """
        query = self.db.query(Transaction).filter(
            Transaction.portfolio_id == portfolio_id,
            Transaction.asset_id == asset_id,
            Transaction.transaction_date <= end_date,
        )
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        return query.order_by(Transaction.transaction_date).all()

    def _get_current_portfolio_value(self, portfolio_id: int) -> float:
        """Get current total value of portfolio from PortfolioAsset table."""
        try:
            assets = (
                self.db.query(PortfolioAsset)
                .filter(PortfolioAsset.portfolio_id == portfolio_id)
                .all()
            )
            total_value = 0.0
            for asset in assets:
                if asset.current_value is not None:
                    total_value += float(asset.current_value)
                elif asset.quantity is not None and asset.quantity == 0:
                    pass  # Asset sold, value is 0
                elif asset.cost_basis_total is not None:
                    # Fallback to cost basis ONLY if value is missing but quantity exists
                    if asset.quantity is not None and asset.quantity > 0:
                        logger.warning(
                            f"No current_value for {asset.asset_id}, falling back to cost_basis"
                        )
                        total_value += float(asset.cost_basis_total)
                    # Otherwise, quantity is likely 0, so value is 0.
            return total_value
        except Exception as e:
            logger.error("Error getting current portfolio value: %s", e)
            return 0.0

    def _get_current_asset_value(self, portfolio_id: int, asset_id: int) -> float:
        """Get current value of a specific asset in portfolio from PortfolioAsset."""
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
                if asset.current_value is not None:
                    return float(asset.current_value)
                elif asset.quantity is not None and asset.quantity == 0:
                    return 0.0  # Sold
                elif asset.cost_basis_total is not None and asset.quantity > 0:
                    # Fallback to cost basis
                    logger.warning(
                        f"No current_value for {asset_id}, falling back to cost_basis"
                    )
                    return float(asset.cost_basis_total)
            return 0.0
        except Exception as e:
            logger.error("Error getting current asset value: %s", e)
            return 0.0

    async def _calculate_initial_market_value(
            self,
            portfolio_id: int,
            transactions: List[Transaction],  # ALL transactions up to end_date
            start_date: Optional[datetime],
    ) -> float:
        """Calculate actual market value of portfolio at period start date."""
        try:
            if start_date is None:
                # For INCEPTION period, the initial value is the cost of the first transaction.
                if transactions:
                    first_transaction = min(
                        transactions, key=lambda t: t.transaction_date
                    )
                    # We need to adjust start_date to be JUST before this,
                    # so that the transaction itself counts as a cash flow.
                    # For a simple TWR/CAGR calc, the initial value *is* the first investment.
                    return float(first_transaction.total_amount)
                return 0.0

            # Get daily portfolio values up to the start_date to find the value.
            # We fetch data up to the start_date, and look for the value on the last available day.
            daily_values = await self._calculate_daily_portfolio_values(
                portfolio_id, None, start_date
            )

            if daily_values.empty:
                # Fallback to cost basis calculation if no daily data available
                return self._calculate_cost_basis_at_date(transactions, start_date)

            # Find the portfolio value closest to start_date
            start_date_only = start_date.date()
            daily_values["Date"] = pd.to_datetime(daily_values["Date"]).dt.date

            # Get the last available value ON or BEFORE start_date
            valid_dates = daily_values[daily_values["Date"] <= start_date_only]

            if not valid_dates.empty:
                # Return the most recent value found
                return float(valid_dates.iloc[-1]["PortfolioValue"])
            else:
                # If no data before start_date (first transaction is after start_date?)
                # This logically means the portfolio value was 0.
                # But cost basis calc might be safer.
                return self._calculate_cost_basis_at_date(transactions, start_date)
        except Exception as e:
            logger.error("Error calculating initial market value: %s", e)
            # Fallback to cost basis calculation
            return self._calculate_cost_basis_at_date(transactions, start_date)

    def _calculate_cost_basis_at_date(
            self,
            transactions: List[Transaction],  # ALL transactions (for that asset or portfolio)
            as_of_date: Optional[datetime],
    ) -> float:
        """Calculate net cost basis (net investment) up to a specific date."""
        try:
            if as_of_date:
                # Get transactions strictly BEFORE start date to calculate opening cost basis
                initial_transactions = [
                    t for t in transactions if t.transaction_date < as_of_date
                ]
            else:
                # INCEPTION period. Initial cost basis is the first transaction.
                if transactions:
                    first_transaction = min(
                        transactions, key=lambda t: t.transaction_date
                    )
                    return float(first_transaction.total_amount)
                return 0.0

            if not initial_transactions:
                return 0.0  # No investments before this date.

            # Calculate net investment up to start date
            net_investment = 0.0
            holdings = {}  # Need to track holdings to handle sells correctly

            # This logic must replicate an average cost basis calculation
            # to properly reduce net_investment on a sale.
            # Simple Net Investment (easier, but less accurate for CAGR base)
            for transaction in initial_transactions:
                if transaction.transaction_type == TransactionType.BUY:
                    net_investment += float(transaction.total_amount)
                elif transaction.transaction_type == TransactionType.SELL:
                    # This sell removes capital. The amount removed should be proportional
                    # to the cost basis of the shares sold.
                    # A simple sum is (Total Buys - Total Sells)
                    net_investment -= float(transaction.total_amount)  # This is Net Cash Flow

            # A true cost basis calculation would track shares and avg price.
            # For this context, "Net Investment" (total buys - total sells) is what
            # is typically meant by "initial value" when market value isn't available.
            return max(net_investment, 0.0)  # Cost basis can't be negative
        except Exception as e:
            logger.error("Error calculating cost basis at date: %s", e)
            return 0.0

    async def _calculate_initial_asset_market_value(
            self,
            asset_id: int,
            all_transactions: List[Transaction],  # All transactions for this asset
            start_date: Optional[datetime],
    ) -> float:
        """
        Calculate actual market value of a single asset at period start date.
        This is the new helper function to fix the logical flaw.
        """
        try:
            if start_date is None:
                # For INCEPTION period, the initial value is the cost of the first transaction.
                if all_transactions:
                    first_transaction = min(
                        all_transactions, key=lambda t: t.transaction_date
                    )
                    return float(first_transaction.total_amount)
                return 0.0

            # 1. Calculate holdings of this asset just BEFORE the start_date
            # We only need transactions *before* the start date to get opening holdings
            transactions_before_start = [
                t for t in all_transactions if t.transaction_date < start_date
            ]
            if not transactions_before_start:
                return 0.0  # No holdings at the start of the period

            holdings_at_start = self._calculate_holdings_as_of_date(
                transactions_before_start, start_date.date() - timedelta(days=1)
            )

            quantity_at_start = holdings_at_start.get(asset_id, 0.0)
            if quantity_at_start <= 0:
                return 0.0  # Asset was held but sold before the period started

            # 2. Get asset symbol to fetch price data
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                logger.warning(f"Could not find asset {asset_id} to get symbol.")
                # Fallback to cost basis
                return self._calculate_cost_basis_at_date(all_transactions, start_date)

            # 3. Fetch price data
            price_data = await self.market_data_service.fetch_ticker_data(
                symbol=asset.symbol, period="max", interval="1d"
            )
            if price_data.empty:
                logger.warning(f"No price data for {asset.symbol}, falling back to cost basis")
                # Fallback to cost basis
                return self._calculate_cost_basis_at_date(all_transactions, start_date)

            # Convert to proper format and index by date (using robust method)
            price_data_indexed = price_data.copy()
            if "Date" not in price_data_indexed.columns:
                # Handle cases where Date might already be the index but not named
                price_data_indexed = price_data_indexed.reset_index()

            price_data_indexed["Date_col"] = pd.to_datetime(price_data_indexed["Date"])
            price_data_indexed = price_data_indexed.set_index('Date_col').sort_index()

            # if not price_data_indexed.empty and not isinstance(price_data_indexed.index[0], datetime.date):
            #     price_data_indexed.index = price_data_indexed.index.date

            # 4. Get the price on the start date (using the correctly indexed DF)
            price_at_start = self._get_price_for_date(price_data_indexed, start_date.date())

            if price_at_start is None:
                logger.warning(f"No price found for {asset.symbol} on {start_date.date()}, falling back to cost basis")
                # Fallback to cost basis if price data is incomplete
                return self._calculate_cost_basis_at_date(all_transactions, start_date)

            # 5. Return market value
            return float(quantity_at_start * price_at_start)

        except Exception as e:
            logger.error(f"Error calculating initial asset market value for {asset_id}: {e}")
            # Fallback to cost basis on any error
            return self._calculate_cost_basis_at_date(all_transactions, start_date)

    def _find_closest_price(
            self, price_data: pd.DataFrame, target_date: datetime
    ) -> Optional[pd.Series]:
        """Find the closest price data to a target date. (DEPRECATED by _get_price_for_date)"""
        try:
            # This logic is less robust than _get_price_for_date.
            # This should ideally be replaced by:
            # price = self._get_price_for_date(price_data_indexed_by_date, target_date.date())
            # return price (as a Series if needed, or just the float)
            # Temporary shim for existing logic (assuming price_data is NOT indexed by date)
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
            "error": "No transactions found for the specified period or portfolio",
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
