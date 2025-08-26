#!/usr/bin/env python3
"""
Database initialization script for Portfolia application.
This script creates all database tables and initializes the database.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import init_db, health_check, redis_health_check
from database.models import *  # Import all models to register them
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Initialize the database."""
    try:
        logger.info("Starting database initialization...")

        # Check database health
        if not health_check():
            logger.error(
                "Database connection failed. Please check your PostgreSQL configuration."
            )
            return False

        # Check Redis health
        if not redis_health_check():
            logger.warning(
                "Redis connection failed. Some features may not work properly."
            )

        # Initialize database tables
        logger.info("Creating database tables...")
        init_db()

        logger.info("Database initialization completed successfully!")

        # Verify tables were created
        if health_check():
            logger.info("Database health check passed.")
            return True
        else:
            logger.error("Database health check failed after initialization.")
            return False

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
