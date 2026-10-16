#!/usr/bin/env python3
"""
Startup script for Portfolia API with automatic database initialization.
This script will:
1. Wait for the database to be ready
2. Start the FastAPI application
Schema migrations run before this, in start_api.sh (alembic upgrade head).
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from core.database.connection import init_db

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


async def startup_sequence():
    """Run the startup sequence for database initialization."""
    logger.info("Starting Portfolia API...")

    # Wait for database
    if not await wait_for_database():
        logger.error("Failed to connect to database. Exiting.")
        sys.exit(1)


def main():
    """Main startup function."""
    try:
        # Run the startup sequence
        asyncio.run(startup_sequence())

        logger.info("Starting FastAPI application...")

        # Import and start the application
        import uvicorn

        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info",
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        sys.exit(1)
