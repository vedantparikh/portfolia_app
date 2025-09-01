"""
Market Data Service
Handles fetching, storing, and serving daily market data with fallback to local data.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from app.core.database.connection import get_db_session
from app.core.database.models.market_data import MarketData, TickerInfo

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for managing market data operations."""

    def __init__(self) -> None:
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price of a ticker."""
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info.get('currentPrice', None) or ticker.info.get("regularMarketPrice", None)
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None

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

        Always fetches maximum available data for 1d interval to ensure comprehensive coverage.
        Note: yfinance default behavior returns only ~30 days, so we explicitly use period="max".

        Args:
            symbol: Stock symbol
            period: Data period (default: "max" for maximum available data - typically 40+ years)
            interval: Data interval (default: "1d" for daily data)

        Returns:
            DataFrame with market data or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching data for {symbol} (attempt {attempt + 1})")

                ticker = yf.Ticker(symbol)

                data = ticker.history(
                    period=period, interval=interval, start=start_date, end=end_date
                )

                if not isinstance(data, pd.DataFrame) or data.empty:
                    logger.warning(f"No data returned for {symbol}")
                    return None

                logger.info(
                    f"Successfully fetched {len(data)} records for {symbol} (max period)"
                )
                data = data.reset_index()
                data = data.sort_values(by="Date", ascending=False)

                return data

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {symbol}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"All attempts failed for {symbol}")
                    return None

    async def store_market_data(
        self, symbol: str, data: pd.DataFrame, session: Session, append: bool = False
    ) -> bool:
        """
        Store market data in the database.

        Args:
            symbol: Stock symbol
            data: DataFrame with market data
            session: Database session
            append: Whether to append data to existing records.
            If False, existing records will be updated and new records will be added to the database.
            If True, only new records will be added to the database.
            Schedular, should pass False. api, should pass True for better
            performance as its less likely to be required to be updated.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get or create ticker info
            ticker_info = await self._get_or_create_ticker(symbol, session)

            if append:
                # Get last recorded date for the ticker from the database
                last_recorded_date = session.execute(
                    select(MarketData)
                    .where(MarketData.ticker_id == ticker_info.id)
                    .order_by(desc(MarketData.date))
                    .limit(1)
                )
                last_recorded_date = last_recorded_date.scalar_one_or_none()
                if last_recorded_date:
                    data = data[data["Date"] > last_recorded_date.date]
            # Convert DataFrame to database records
            records = []
            for date, row in data.iterrows():
                record = MarketData(
                    ticker_id=ticker_info.id,
                    date=date.date(),
                    open_price=float(row["Open"]),
                    high_price=float(row["High"]),
                    low_price=float(row["Low"]),
                    close_price=float(row["Close"]),
                    volume=int(row["Volume"]),
                    adjusted_close=(
                        float(row["Adj Close"])
                        if "Adj Close" in row
                        else float(row["Close"])
                    ),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                records.append(record)

            # Bulk insert/update (upsert logic)
            await self._upsert_market_data(records, session)

            logger.info(f"Stored {len(records)} records for {symbol}")
            return True

        except Exception as e:
            logger.error(f"Failed to store data for {symbol}: {e}")
            return False

    async def _get_or_create_ticker(self, symbol: str, session: Session) -> TickerInfo:
        """Get existing ticker or create new one with comprehensive company information."""
        try:
            # Check if ticker exists
            result = session.execute(
                select(TickerInfo).where(TickerInfo.symbol == symbol)
            )
            ticker = result.scalar_one_or_none()

            if ticker:
                # Update existing ticker with fresh company info
                logger.info(f"Updating existing ticker info for {symbol}")
                company_info = await self._fetch_company_info(symbol)

                ticker.name = company_info["name"]
                ticker.company_name = company_info["company_name"]
                ticker.sector = company_info["sector"]
                ticker.industry = company_info["industry"]
                ticker.exchange = company_info["exchange"]
                ticker.currency = company_info["currency"]
                ticker.updated_at = datetime.now(timezone.utc)

                session.commit()
                session.refresh(ticker)
                return ticker

            # Create new ticker with comprehensive company information
            logger.info(f"Creating new ticker with company info for {symbol}")
            company_info = await self._fetch_company_info(symbol)

            ticker = TickerInfo(
                symbol=symbol,
                name=company_info["name"],
                company_name=company_info["company_name"],
                sector=company_info["sector"],
                industry=company_info["industry"],
                exchange=company_info["exchange"],
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(ticker)
            session.commit()
            session.refresh(ticker)

            logger.info(f"Created ticker {symbol}: {ticker.name} ({ticker.sector})")
            return ticker

        except Exception as e:
            logger.error(f"Error in _get_or_create_ticker for {symbol}: {e}")
            raise

    async def _upsert_market_data(
        self, records: List[MarketData], session: Session
    ) -> None:
        """Upsert market data records."""
        try:
            for record in records:
                # Check if record exists for this date and ticker
                existing = session.execute(
                    select(MarketData).where(
                        and_(
                            MarketData.ticker_id == record.ticker_id,
                            MarketData.date == record.date,
                        )
                    )
                )
                existing_record = existing.scalar_one_or_none()

                if existing_record:
                    # Update existing record
                    existing_record.open_price = record.open_price
                    existing_record.high_price = record.high_price
                    existing_record.low_price = record.low_price
                    existing_record.close_price = record.close_price
                    existing_record.volume = record.volume
                    existing_record.adjusted_close = record.adjusted_close
                    existing_record.updated_at = datetime.now(timezone.utc)
                else:
                    # Insert new record
                    session.add(record)

            session.commit()

        except Exception as e:
            logger.error(f"Error in _upsert_market_data: {e}")
            session.rollback()
            raise

    async def get_market_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Get market data from local database.

        Args:
            symbol: Stock symbol
            start_date: Start date for data range
            end_date: End date for data range

        Returns:
            DataFrame with market data or None if not found
        """
        try:
            async with get_db_session() as session:
                # Get ticker info
                result = session.execute(
                    select(TickerInfo).where(TickerInfo.symbol == symbol)
                )
                ticker = result.scalar_one_or_none()

                if not ticker:
                    logger.warning(f"Ticker {symbol} not found in database")
                    return None

                # Build query
                query = select(MarketData).where(MarketData.ticker_id == ticker.id)

                if start_date:
                    query = query.where(MarketData.date >= start_date.date())
                if end_date:
                    query = query.where(MarketData.date <= end_date.date())

                query = query.order_by(desc(MarketData.date))

                # Execute query
                result = session.execute(query)
                records = result.scalars().all()

                if not records:
                    logger.warning(f"No market data found for {symbol}")
                    return None

                # Convert to DataFrame
                data = []
                for record in records:
                    data.append(
                        {
                            "Date": record.date,
                            "Open": record.open_price,
                            "High": record.high_price,
                            "Low": record.low_price,
                            "Close": record.close_price,
                            "Volume": record.volume,
                            "Adj Close": record.adjusted_close,
                        }
                    )

                df = pd.DataFrame(data)

                logger.info(f"Retrieved {len(df)} records for {symbol} from database")
                return df

        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return None

    async def get_data_with_fallback(
        self, symbol: str, period: str = "max", interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Get market data with fallback logic.
        ALWAYS tries to fetch from yfinance first for fresh data, falls back to local data only if yfinance fails.

        Always fetches maximum available data for 1d interval to ensure comprehensive coverage.
        Note: yfinance default behavior returns only ~30 days, so we explicitly use period="max".

        Args:
            symbol: Stock symbol
            period: Data period (default: "max" for maximum available data - typically 40+ years)
            interval: Data interval (default: "1d" for daily data)

        Returns:
            DataFrame with market data or None if not available
        """
        # Priority: yfinance API > local database
        logger.info(
            f"Fetching fresh data from yfinance for {symbol} {period} {interval}"
        )
        fresh_data = await self.fetch_ticker_data(
            symbol=symbol, period=period, interval=interval
        )

        if fresh_data is not None:
            # Store the fresh data in database for future fallback
            try:
                async with get_db_session() as session:
                    await self.store_market_data(
                        symbol=symbol, data=fresh_data, session=session, append=True
                    )
                logger.info(
                    f"✅ Fresh data fetched and stored for {symbol} (max period: {len(fresh_data)} records)"
                )
                return fresh_data
            except Exception as e:
                logger.error(f"Failed to store fresh data for {symbol}: {e}")
                # Still return the data even if storage failed
                logger.info(
                    f"Returning fresh data for {symbol} (storage failed but data is valid)"
                )
                return fresh_data

        # Only fallback to local data if yfinance completely fails
        logger.warning(f"yfinance failed for {symbol}, falling back to local database")
        local_data = await self.get_market_data(symbol)

        if local_data is not None:
            logger.info(
                f"📊 Local data retrieved for {symbol} ({len(local_data)} records) - yfinance unavailable"
            )
            return local_data

        logger.error(
            f"❌ No data available for {symbol} (neither yfinance nor local database)"
        )
        return None

    async def update_all_tickers(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Update data for all specified tickers.

        Args:
            symbols: List of stock symbols to update

        Returns:
            Dictionary with update status for each symbol
        """
        results = {}

        for symbol in symbols:
            try:
                logger.info(f"Updating data for {symbol}")
                success = await self.update_single_ticker(symbol)
                results[symbol] = success
            except Exception as e:
                logger.error(f"Error updating {symbol}: {e}")
                results[symbol] = False

        return results

    async def update_single_ticker(self, symbol: str) -> bool:
        """Update data for a single ticker."""
        try:
            # Fetch fresh data (always max period, 1d interval for comprehensive coverage)
            data = await self.fetch_ticker_data(symbol, "max", "1d")

            if data is None:
                logger.warning(f"No fresh data available for {symbol}")
                return False

            # Store in database
            async with get_db_session() as session:
                success = await self.store_market_data(symbol, data, session)

            return success

        except Exception as e:
            logger.error(f"Error updating {symbol}: {e}")
            return False

    async def get_data_quality_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get information about data quality and freshness.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with data quality information
        """
        try:
            async with get_db_session() as session:
                # Get ticker info
                result = session.execute(
                    select(TickerInfo).where(TickerInfo.symbol == symbol)
                )
                ticker = result.scalar_one_or_none()

                if not ticker:
                    return {"error": "Ticker not found"}

                # Get latest data record
                result = session.execute(
                    select(MarketData)
                    .where(MarketData.ticker_id == ticker.id)
                    .order_by(desc(MarketData.date))
                    .limit(1)
                )
                latest_record = result.scalar_one_or_none()

                if not latest_record:
                    return {"error": "No data available"}

                # Calculate data age
                data_age = datetime.now(timezone.utc).date() - latest_record.date

                return {
                    "symbol": symbol,
                    "latest_date": latest_record.date.isoformat(),
                    "data_age_days": data_age.days,
                    "is_fresh": data_age.days <= 1,
                    "last_updated": latest_record.updated_at.isoformat(),
                }

        except Exception as e:
            logger.error(f"Error getting data quality info for {symbol}: {e}")
            return {"error": str(e)}

    async def _fetch_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch comprehensive company information from yfinance.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with company information
        """
        try:
            ticker = yf.Ticker(symbol)

            # Get company info
            info = ticker.info

            company_data = {
                "name": info.get("longName", symbol),
                "company_name": info.get("longName", info.get("shortName", symbol)),
                "sector": info.get("sector", None),
                "industry": info.get("industry", None),
                "exchange": info.get("exchange", None),
                "market_cap": info.get("marketCap", None),
                "country": info.get("country", None),
                "currency": info.get("currency", None),
                "website": info.get("website", None),
                "business_summary": info.get("longBusinessSummary", None),
            }

            logger.info(
                f"Fetched company info for {symbol}: {company_data['name']} ({company_data['sector']})"
            )
            return company_data

        except Exception as e:
            logger.warning(f"Failed to fetch company info for {symbol}: {e}")
            # Return basic info if yfinance fails
            return {
                "name": symbol,
                "company_name": symbol,
                "sector": None,
                "industry": None,
                "exchange": None,
                "market_cap": None,
                "country": None,
                "currency": None,
                "website": None,
                "business_summary": None,
            }

    async def refresh_ticker_info(self, symbol: str) -> bool:
        """
        Refresh company information for an existing ticker.

        Args:
            symbol: Stock symbol

        Returns:
            True if successful, False otherwise
        """
        try:
            async with get_db_session() as session:
                # Get existing ticker
                result = session.execute(
                    select(TickerInfo).where(TickerInfo.symbol == symbol)
                )
                ticker = result.scalar_one_or_none()

                if not ticker:
                    logger.warning(f"Ticker {symbol} not found in database")
                    return False

                # Fetch fresh company info
                company_info = await self._fetch_company_info(symbol)

                # Update ticker with new information
                ticker.name = company_info["name"]
                ticker.company_name = company_info["company_name"]
                ticker.sector = company_info["sector"]
                ticker.industry = company_info["industry"]
                ticker.exchange = company_info["exchange"]
                ticker.updated_at = datetime.now(timezone.utc)

                session.commit()
                session.refresh(ticker)

                logger.info(
                    f"Refreshed ticker info for {symbol}: {ticker.name} ({ticker.sector})"
                )
                return True

        except Exception as e:
            logger.error(f"Error refreshing ticker info for {symbol}: {e}")
            return False

    async def refresh_all_ticker_info(self) -> Dict[str, bool]:
        """
        Refresh company information for all active tickers.

        Returns:
            Dictionary with refresh status for each symbol
        """
        try:
            async with get_db_session() as session:
                # Get all active tickers
                result = session.execute(
                    select(TickerInfo).where(TickerInfo.is_active == True)
                )
                tickers = result.scalars().all()

                results = {}
                for ticker in tickers:
                    logger.info(f"Refreshing company info for {ticker.symbol}")
                    success = await self.refresh_ticker_info(ticker.symbol)
                    results[ticker.symbol] = success

                return results

        except Exception as e:
            logger.error(f"Error refreshing all ticker info: {e}")
            return {}


# Global instance
market_data_service = MarketDataService()
