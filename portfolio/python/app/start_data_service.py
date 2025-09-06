#!/usr/bin/env python3
"""
Data Service Startup Script
Starts the market data service with scheduler for automatic updates.
"""

import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import select

from app.core.database.connection import get_db_session, init_db
from app.core.database.models.market_data import MarketData
from app.core.services.data_scheduler import data_scheduler
from app.core.services.market_data_service import market_data_service

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def wait_for_database(max_retries: int = 30, retry_delay: int = 2):
    """Wait for database to be ready."""
    logger.info("Waiting for database to be ready...")

    for attempt in range(max_retries):
        try:
            if await init_db():
                logger.info("Database connection established successfully!")
                return True
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")

        if attempt < max_retries - 1:
            logger.info(
                f"Retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})"
            )
            await asyncio.sleep(retry_delay)

    logger.error(f"Database connection failed after {max_retries} attempts")
    return False


async def initialize_data_service():
    """Initialize the data service."""
    try:
        logger.info("Initializing market data service...")

        # Wait for database
        if not await wait_for_database():
            logger.error("Failed to connect to database. Exiting.")
            return False

        # Perform initial data population if needed
        await populate_initial_data()

        logger.info("Market data service initialized successfully!")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize data service: {e}")
        return False


async def populate_initial_data():
    """Populate initial data for default tickers."""
    try:
        logger.info("Checking if initial data population is needed...")

        # Default tickers to populate
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

        # Check if we have any data
        async with get_db_session() as session:
            result = await session.execute(select(MarketData).limit(1))
            has_data = result.scalar_one_or_none() is not None

            if not has_data:
                logger.info("No existing data found. Populating initial data...")

                # Update all default tickers (always max period, 1d interval)
                results = await market_data_service.update_all_tickers(default_tickers)

                successful = sum(1 for success in results.values() if success)
                failed = len(results) - successful

                logger.info(
                    f"Initial data population completed: {successful} successful, {failed} failed"
                )
            else:
                logger.info("Data already exists. Skipping initial population.")

    except Exception as e:
        logger.error(f"Error in initial data population: {e}")


async def main():
    """Main function to start the data service."""
    try:
        logger.info("Starting Portfolia Market Data Service...")

        # Initialize the service
        if not await initialize_data_service():
            logger.error("Failed to initialize data service. Exiting.")
            sys.exit(1)

        # Start the scheduler
        logger.info("Starting data scheduler...")
        await data_scheduler.start_scheduler()

    except KeyboardInterrupt:
        logger.info("Data service stopped by user")
    except Exception as e:
        logger.error(f"Failed to start data service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Data service stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
