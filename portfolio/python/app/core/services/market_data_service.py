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
    ) -> Optional[pd.DataFrame]:
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
                    return None

                logger.info("Successfully fetched %d records for %s", len(data), symbol)

                # Reset index to make Date a column
                data = data.reset_index()

                # Ensure we have the expected columns
                expected_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
                if not all(col in data.columns for col in expected_columns):
                    logger.warning("Missing expected columns in data for %s", symbol)
                    return None

                # Sort by date descending (most recent first)
                data = data.sort_values(by="Date", ascending=False)

                return data

            except Exception as e:
                logger.error("Attempt %d failed for %s: %s", attempt + 1, symbol, e)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("All attempts failed for %s", symbol)
                    return None

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
            ticker_data = {
                "symbol": info.get("symbol", symbol).upper(),
                "longName": info.get("longName"),
                "shortName": info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "exchange": info.get("exchange"),
                "exchangeDisp": info.get("exchangeDisp"),
                "currency": info.get("currency"),
                "country": info.get("country"),
                "quoteType": info.get("quoteType"),
                "marketCap": info.get("marketCap"),
                "currentPrice": info.get("currentPrice"),
                "regularMarketPrice": info.get("regularMarketPrice"),
                "previousClose": info.get("previousClose"),
                "open": info.get("open"),
                "dayLow": info.get("dayLow"),
                "dayHigh": info.get("dayHigh"),
                "volume": info.get("volume"),
                "averageVolume": info.get("averageVolume"),
                "beta": info.get("beta"),
                "trailingPE": info.get("trailingPE"),
                "forwardPE": info.get("forwardPE"),
                "dividendYield": info.get("dividendYield"),
                "payoutRatio": info.get("payoutRatio"),
                "bookValue": info.get("bookValue"),
                "priceToBook": info.get("priceToBook"),
                "earningsGrowth": info.get("earningsGrowth"),
                "revenueGrowth": info.get("revenueGrowth"),
                "returnOnAssets": info.get("returnOnAssets"),
                "returnOnEquity": info.get("returnOnEquity"),
                "freeCashflow": info.get("freeCashflow"),
                "operatingCashflow": info.get("operatingCashflow"),
                "totalDebt": info.get("totalDebt"),
                "totalCash": info.get("totalCash"),
                "longBusinessSummary": info.get("longBusinessSummary"),
                "website": info.get("website"),
                "fullTimeEmployees": info.get("fullTimeEmployees"),
            }

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

            # Use yfinance Tickers for bulk fetching
            tickers_str = " ".join(symbols)
            tickers = yf.Tickers(tickers_str)

            results = []

            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.info

                    if not info or info.get("symbol") is None:
                        logger.warning("No data available for %s", symbol)
                        continue

                    stock_data = {
                        "symbol": info.get("symbol", symbol).upper(),
                        "name": (
                            info.get("longName") or info.get("shortName") or symbol
                        ),
                        "latest_price": (
                            info.get("currentPrice")
                            or info.get("regularMarketPrice")
                            or info.get("previousClose")
                            or 0.0
                        ),
                        "latest_date": info.get("regularMarketTime"),
                        "market_cap": info.get("marketCap"),
                        "pe_ratio": info.get("trailingPE"),
                        "beta": info.get("beta"),
                        "currency": info.get("currency"),
                        "exchange": (info.get("exchangeDisp") or info.get("exchange")),
                        "dividend_yield": info.get("dividendYield", 0.0),
                        "day_change": None,  # Would need historical data to calculate
                        "day_change_percent": None,  # Would need historical data to calculate
                        "volume": info.get("volume"),
                        "avg_volume": info.get("averageVolume"),
                    }

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


# Global instance
market_data_service = MarketDataService()
