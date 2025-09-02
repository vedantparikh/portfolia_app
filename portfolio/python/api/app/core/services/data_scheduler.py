"""
Data Scheduler Service
Handles scheduled updates of market data for all tracked tickers.
"""

import asyncio
import logging
import schedule
from datetime import datetime, timedelta
from typing import List, Dict
import traceback

from sqlalchemy import select
from sqlalchemy import and_

from app.core.database.connection import get_db_session
from app.core.services.market_data_service import market_data_service
from app.core.database.models.market_data import DataUpdateLog, TickerInfo, MarketData


logger = logging.getLogger(__name__)


class DataScheduler:
    """Scheduler for updating market data."""

    def __init__(self):
        self.is_running = False
        self.update_interval_hours = 24  # Update once per day
        self.batch_size = 10  # Process tickers in batches
        self.retry_failed_after_hours = 6  # Retry failed updates after 6 hours

    async def start_scheduler(self):
        """Start the data scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        self.is_running = True
        logger.info("Starting data scheduler...")

        # Schedule daily update at 6 PM (market close + 2 hours)
        schedule.every().day.at("18:00").do(self._run_daily_update)

        # Schedule retry of failed updates every 6 hours
        schedule.every(6).hours.do(self._retry_failed_updates)

        # Run initial update check
        await self._check_and_update_if_needed()

        # Start the scheduler loop
        while self.is_running:
            try:
                schedule.run_pending()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def stop_scheduler(self):
        """Stop the data scheduler."""
        self.is_running = False
        logger.info("Data scheduler stopped")

    async def _run_daily_update(self):
        """Run the daily market data update."""
        logger.info("Starting daily market data update...")

        try:
            # Get all active tickers
            tickers = await self._get_active_tickers()

            if not tickers:
                logger.warning("No active tickers found for update")
                return

            logger.info(f"Updating data for {len(tickers)} tickers...")

            # Process tickers in batches
            results = {}
            for i in range(0, len(tickers), self.batch_size):
                batch = tickers[i : i + self.batch_size]
                batch_results = await self._update_ticker_batch(batch)
                results.update(batch_results)

                # Log batch progress
                logger.info(
                    f"Processed batch {i//self.batch_size + 1}/{(len(tickers) + self.batch_size - 1)//self.batch_size}"
                )

                # Small delay between batches to avoid overwhelming external APIs
                await asyncio.sleep(2)

            # Log overall results
            successful = sum(1 for success in results.values() if success)
            failed = len(results) - successful

            logger.info(
                f"Daily update completed: {successful} successful, {failed} failed"
            )

            # Log update summary
            await self._log_update_summary("daily_update", results)

        except Exception as e:
            logger.error(f"Error in daily update: {e}")
            logger.error(traceback.format_exc())

    async def _retry_failed_updates(self):
        """Retry failed updates from the last 6 hours."""
        logger.info("Checking for failed updates to retry...")

        try:
            # Get failed updates from the last 6 hours
            failed_logs = await self._get_failed_updates_recent()

            if not failed_logs:
                logger.info("No failed updates to retry")
                return

            logger.info(f"Retrying {len(failed_logs)} failed updates...")

            # Group by ticker symbol
            ticker_symbols = list(set(log.ticker_symbol for log in failed_logs))

            # Retry updates
            results = await market_data_service.update_all_tickers(ticker_symbols)

            # Log retry results
            successful = sum(1 for success in results.values() if success)
            failed = len(results) - successful

            logger.info(f"Retry completed: {successful} successful, {failed} failed")

            # Log retry summary
            await self._log_update_summary("retry_update", results)

        except Exception as e:
            logger.error(f"Error in retry update: {e}")
            logger.error(traceback.format_exc())

    async def _check_and_update_if_needed(self):
        """Check if update is needed and run if necessary."""
        try:
            # Check if we need to run an update
            if await self._should_run_update():
                logger.info("Update needed, running now...")
                await self._run_daily_update()
            else:
                logger.info("No update needed at this time")

        except Exception as e:
            logger.error(f"Error checking if update needed: {e}")

    async def _should_run_update(self) -> bool:
        """Check if an update should be run."""
        try:
            async with get_db_session() as session:
                # Check if we have any market data
                result = await session.execute(select(MarketData).limit(1))
                has_data = result.scalar_one_or_none() is not None

                if not has_data:
                    logger.info("No market data found, update needed")
                    return True

                # Check if the latest data is older than 24 hours
                result = await session.execute(
                    select(MarketData.date).order_by(MarketData.date.desc()).limit(1)
                )
                latest_date = result.scalar_one_or_none()

                if latest_date:
                    data_age = datetime.utcnow().date() - latest_date
                    if data_age.days >= 1:
                        logger.info(
                            f"Latest data is {data_age.days} days old, update needed"
                        )
                        return True

                logger.info("Data is fresh, no update needed")
                return False

        except Exception as e:
            logger.error(f"Error checking if update needed: {e}")
            return True  # Default to running update on error

    async def _get_active_tickers(self) -> List[str]:
        """Get list of active ticker symbols."""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(TickerInfo.symbol).where(TickerInfo.is_active == True)
                )
                tickers = result.scalars().all()

                if not tickers:
                    # If no tickers in database, return some default ones
                    default_tickers = [
                        "AAPL",
                        "GOOGL",
                        "MSFT",
                        "AMZN",
                        "TSLA",
                        "META",
                        "NVDA",
                        "NFLX",
                    ]
                    logger.info(
                        f"No tickers in database, using default list: {default_tickers}"
                    )
                    return default_tickers

                return list(tickers)

        except Exception as e:
            logger.error(f"Error getting active tickers: {e}")
            # Return default tickers on error
            return ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

    async def _update_ticker_batch(self, tickers: List[str]) -> Dict[str, bool]:
        """Update a batch of tickers."""
        results = {}

        for ticker in tickers:
            try:
                start_time = datetime.utcnow()

                # Update the ticker (always max period, 1d interval for comprehensive coverage)
                success = await market_data_service.update_single_ticker(ticker)

                # Calculate execution time
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                # Log the operation
                await self._log_operation(
                    ticker,
                    "update",
                    "success" if success else "failed",
                    records_processed=0,  # Will be updated by market_data_service
                    execution_time_ms=int(execution_time),
                )

                results[ticker] = success

            except Exception as e:
                logger.error(f"Error updating ticker {ticker}: {e}")

                # Log the failed operation
                await self._log_operation(
                    ticker, "update", "failed", error_message=str(e)
                )

                results[ticker] = False

        return results

    async def _get_failed_updates_recent(self) -> List[DataUpdateLog]:
        """Get failed updates from the last 6 hours."""
        try:
            async with get_db_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(
                    hours=self.retry_failed_after_hours
                )

                result = await session.execute(
                    select(DataUpdateLog).where(
                        and_(
                            DataUpdateLog.status == "failed",
                            DataUpdateLog.created_at >= cutoff_time,
                        )
                    )
                )

                return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting failed updates: {e}")
            return []

    async def _log_operation(
        self,
        ticker_symbol: str,
        operation: str,
        status: str,
        records_processed: int = 0,
        error_message: str = None,
        execution_time_ms: int = None,
    ):
        """Log an operation to the database."""
        try:
            async with get_db_session() as session:
                log_entry = DataUpdateLog(
                    ticker_symbol=ticker_symbol,
                    operation=operation,
                    status=status,
                    records_processed=records_processed,
                    error_message=error_message,
                    execution_time_ms=execution_time_ms,
                )

                session.add(log_entry)
                await session.commit()

        except Exception as e:
            logger.error(f"Error logging operation: {e}")

    async def _log_update_summary(self, operation_type: str, results: Dict[str, bool]):
        """Log a summary of update results."""
        try:
            successful = sum(1 for success in results.values() if success)
            failed = len(results) - successful

            summary_message = (
                f"{operation_type}: {successful} successful, {failed} failed"
            )

            if failed > 0:
                failed_tickers = [
                    ticker for ticker, success in results.items() if not success
                ]
                summary_message += f" - Failed: {', '.join(failed_tickers)}"

            logger.info(summary_message)

        except Exception as e:
            logger.error(f"Error logging update summary: {e}")

    async def manual_update(self, tickers: List[str] = None) -> Dict[str, bool]:
        """Manually trigger an update for specified tickers or all tickers."""
        logger.info("Manual update triggered")

        if tickers is None:
            tickers = await self._get_active_tickers()

        logger.info(f"Manual update for tickers: {tickers}")

        # Process in batches
        results = {}
        for i in range(0, len(tickers), self.batch_size):
            batch = tickers[i : i + self.batch_size]
            batch_results = await self._update_ticker_batch(batch)
            results.update(batch_results)

            # Small delay between batches
            await asyncio.sleep(1)

        # Log manual update summary
        await self._log_update_summary("manual_update", results)

        return results


# Global instance
data_scheduler = DataScheduler()
