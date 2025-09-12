"""
Market Data Service - yfinance only
Handles fetching real-time market data from yfinance without database storage.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd  # type: ignore
import yfinance as yf  # type: ignore

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for managing market data operations using yfinance only."""

    def __init__(self) -> None:
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price of a ticker from yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Try multiple price fields in order of preference
            price = (
                    info.get("currentPrice")
                    or info.get("regularMarketPrice")
                    or info.get("previousClose")
                    or info.get("open")
            )

            if price is not None:
                return float(price)

            # If info doesn't have price, try getting it from history
            hist = ticker.history(period="1d")
            if not hist.empty:
                return float(hist["Close"].iloc[-1])

            return None

        except Exception as e:
            logger.error("Error getting current price for %s: %s", symbol, e)
            return None

    async def get_multiple_current_prices(
            self, symbols: List[str]
    ) -> Dict[str, Optional[float]]:
        """Get current prices for multiple symbols efficiently."""
        try:
            # Use yfinance Tickers for bulk fetching
            tickers = yf.Tickers(" ".join(symbols))
            results = {}

            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.info

                    price = (
                            info.get("currentPrice")
                            or info.get("regularMarketPrice")
                            or info.get("previousClose")
                            or info.get("open")
                    )

                    if price is not None:
                        results[symbol] = float(price)
                    else:
                        # Fallback to history
                        hist = ticker.history(period="1d")
                        if not hist.empty:
                            results[symbol] = float(hist["Close"].iloc[-1])
                        else:
                            results[symbol] = None

                except Exception as e:
                    logger.error("Error getting price for %s: %s", symbol, e)
                    results[symbol] = None

            return results

        except Exception as e:
            logger.error("Error getting multiple prices: %s", e)
            # Fallback to individual requests
            results = {}
            for symbol in symbols:
                results[symbol] = await self.get_current_price(symbol)
            return results

    async def fetch_ticker_data(
            self,
            symbol: str,
            period: str = "max",
            interval: str = "1d",
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch ticker data from yfinance with retry logic.

        Args:
            symbol: Stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with market data or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                logger.info("Fetching data for %s (attempt %d)", symbol, attempt + 1)

                ticker = yf.Ticker(symbol)

                if start_date and end_date:
                    data = ticker.history(
                        start=start_date, end=end_date, interval=interval
                    )
                else:
                    data = ticker.history(period=period, interval=interval)

                if not isinstance(data, pd.DataFrame) or data.empty:
                    logger.warning("No data returned for %s", symbol)
                    return pd.DataFrame()

                logger.info("Successfully fetched %d records for %s", len(data), symbol)

                # Reset index to make Date a column
                data = data.reset_index()

                # Ensure we have the expected columns
                expected_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
                if not all(col in data.columns for col in expected_columns):
                    logger.warning("Missing expected columns in data for %s", symbol)
                    return pd.DataFrame()

                # Sort by date descending (most recent first)
                data = data.sort_values(by="Date", ascending=False)

                return data

            except Exception as e:
                logger.error("Attempt %d failed for %s: %s", attempt + 1, symbol, e)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("All attempts failed for %s", symbol)
                    return pd.DataFrame()

    async def get_ticker_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive ticker information from yfinance.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with ticker information or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or info.get("symbol") is None:
                logger.warning("No info available for %s", symbol)
                return None

            # Extract and normalize the information
            ticker_data = self._extract_ticker_information(ticker_info=info)

            logger.info(
                "Retrieved ticker info for %s: %s",
                symbol,
                ticker_data.get("longName", symbol),
            )
            return ticker_data

        except Exception as e:
            logger.error("Error getting ticker info for %s: %s", symbol, e)
            return None

    async def get_stock_latest_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Get the latest stock data for multiple symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            List of dictionaries with stock data
        """
        try:
            if not symbols:
                return []
            tickers = yf.Tickers(symbols)
            results = []
            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.info

                    if not info or info.get("symbol") is None:
                        logger.warning("No data available for %s", symbol)
                        continue

                    stock_data = self._extract_ticker_information(ticker_info=info)
                    results.append(stock_data)

                except Exception as e:
                    logger.error("Error processing %s: %s", symbol, e)
                    continue

            logger.info(
                "Retrieved data for %d out of %d symbols", len(results), len(symbols)
            )
            return results

        except Exception as e:
            logger.error("Error getting stock data for symbols %s: %s", symbols, e)
            return []

    async def search_symbols(
            self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:  # noqa: ARG002
        """
        Search for stock symbols using yfinance.
        Note: This is a basic implementation. For production, consider using
        a dedicated symbol search API.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching symbols with basic info
        """
        try:
            # This is a simple implementation - in production you might want
            # to use a more sophisticated search API

            # Try to get info for the query as a direct symbol
            ticker_info = await self.get_ticker_info(query.upper())

            if ticker_info:
                return [
                    {
                        "symbol": ticker_info["symbol"],
                        "name": ticker_info.get("longName")
                                or ticker_info.get("shortName"),
                        "exchange": ticker_info.get("exchange"),
                        "currency": ticker_info.get("currency"),
                        "type": ticker_info.get("quoteType"),
                    }
                ]
            else:
                return []

        except Exception as e:
            logger.error("Error searching symbols for query '%s': %s", query, e)
            return []

    def get_supported_periods(self) -> List[str]:
        """Get list of supported period values."""
        return ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

    def get_supported_intervals(self) -> List[str]:
        """Get list of supported interval values."""
        return [
            "1m",
            "2m",
            "5m",
            "15m",
            "30m",
            "60m",
            "90m",
            "1h",
            "1d",
            "5d",
            "1wk",
            "1mo",
            "3mo",
        ]

    async def get_market_status(self) -> Dict[str, Any]:
        """
        Get current market status.
        Note: This is a basic implementation using market hours.
        """
        try:
            # Get current time in Eastern Time (US market timezone)
            import pytz  # type: ignore

            et = pytz.timezone("US/Eastern")
            now_et = datetime.now(et)

            # Basic market hours check (9:30 AM - 4:00 PM ET, Monday-Friday)
            is_weekday = now_et.weekday() < 5  # Monday = 0, Friday = 4
            market_open_time = now_et.replace(
                hour=9, minute=30, second=0, microsecond=0
            )
            market_close_time = now_et.replace(
                hour=16, minute=0, second=0, microsecond=0
            )

            is_market_hours = market_open_time <= now_et <= market_close_time
            is_open = is_weekday and is_market_hours

            return {
                "is_open": is_open,
                "current_time_et": now_et.isoformat(),
                "next_open": None,  # Would need more complex logic
                "next_close": None,  # Would need more complex logic
                "timezone": "US/Eastern",
            }

        except Exception as e:
            logger.error("Error getting market status: %s", e)
            return {"is_open": None, "error": str(e)}

    def _extract_ticker_information(self, ticker_info: Dict[str, Any]) -> Dict[str, Any]:
        # Extract and normalize the information
        ticker_data = {
            "symbol": ticker_info.get("symbol").upper(),
            "long_name": ticker_info.get("longName"),
            "short_name": ticker_info.get("shortName"),
            "sector": ticker_info.get("sector"),
            "industry": ticker_info.get("industry"),
            "exchange": ticker_info.get("exchangeDisp", ticker_info.get("exchange")),
            "currency": ticker_info.get("currency"),
            "country": ticker_info.get("country"),
            "quote_type": ticker_info.get("quoteType"),
            "market_cap": ticker_info.get("marketCap"),
            "current_price": ticker_info.get("currentPrice", ticker_info.get("regularMarketPrice")),
            "price_change_percentage_24h": ticker_info.get('regularMarketChangePercent', 0),
            "previous_close": ticker_info.get("previousClose"),
            "open": ticker_info.get("open"),
            "day_low": ticker_info.get("dayLow"),
            "low_52w": ticker_info.get('fiftyTwoWeekLow'),
            "high_52w": ticker_info.get('fiftyTwoWeekHigh'),
            "day_high": ticker_info.get("dayHigh"),
            "volume": ticker_info.get("volume"),
            "average_volume": ticker_info.get("averageVolume"),
            "volume_24h": ticker_info.get("regularMarketVolume"),
            "beta": ticker_info.get("beta"),
            "trailing_PE": ticker_info.get("trailingPE"),
            "forward_PE": ticker_info.get("forwardPE"),
            "dividend_yield": ticker_info.get("dividendYield"),
            "payout_ratio": ticker_info.get("payoutRatio"),
            "book_value": ticker_info.get("bookValue"),
            "price_to_book": ticker_info.get("priceToBook"),
            "earnings_growth": ticker_info.get("earningsGrowth"),
            "revenue_growth": ticker_info.get("revenueGrowth"),
            "return_on_assets": ticker_info.get("returnOnAssets"),
            "return_on_equity": ticker_info.get("returnOnEquity"),
            "free_cashflow": ticker_info.get("freeCashflow"),
            "operating_cashflow": ticker_info.get("operatingCashflow"),
            "total_debt": ticker_info.get("totalDebt"),
            "total_cash": ticker_info.get("totalCash"),
            "long_business_summary": ticker_info.get("longBusinessSummary"),
            "website": ticker_info.get("website"),
            "full_time_employees": ticker_info.get("fullTimeEmployees"),
        }
        return ticker_data

    async def get_symbols_info(self, symbols: List[str]) -> Dict[str, Any]:

        tickers = yf.Tickers(symbols)
        result = {}
        for ticker in tickers.tickers.values():
            try:
                info = ticker.info
                if info.get('regularMarketPrice') is None:
                    logger.warning("Error getting info for symbol: %s", info.get('symbol'))
                    continue
                result[info.get('symbol')] = self._extract_ticker_information(ticker_info=info)
            except Exception as e:
                logger.error("Error processing ticker info: %s. Error: %s", ticker.ticker, e)
        return result


# Global instance
market_data_service = MarketDataService()
