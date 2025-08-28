"""
Stock Router
API endpoints for stock data operations with separate endpoints for fresh and local data.
"""

import logging
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from yahooquery import search

from services.market_data_service import market_data_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/symbols")
async def get_symbols(name: str) -> Optional[List[Dict[str, Any]]]:
    """
    Get stock symbols matching the search name.

    This endpoint searches for stock symbols using yahooquery and returns
    matching results with symbol and quote type information.
    """
    try:
        # Search for symbols
        data = search(name)

        if not data or "quotes" not in data or len(data["quotes"]) == 0:
            raise HTTPException(status_code=404, detail="No symbols found")

        quotes = data.get("quotes", [])
        if not isinstance(quotes, list):
            raise HTTPException(
                status_code=500, detail="Malformed response from symbol search"
            )

        return quotes

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching for symbols: {str(e)}"
        )


@router.get("/symbol-data/fresh")
async def get_symbol_data_fresh(
    name: str,
    period: str = Query(
        default="max",
        description="Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
    ),
    interval: str = Query(
        default="1d",
        description="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)",
    ),
) -> Optional[Dict[str, Any]]:
    """
    Get fresh stock data for a specific symbol from yfinance API.

    This endpoint fetches live data from yfinance and stores it locally for future use.
    Always fetches maximum available data for comprehensive coverage.

    Note: This endpoint may take longer to respond as it fetches fresh data from external API.
    """
    try:
        # Fetch fresh data from yfinance (always max period for comprehensive coverage)
        data = await market_data_service.fetch_ticker_data(
            symbol=name, period=period, interval=interval
        )

        if data is None:
            raise HTTPException(
                status_code=404, detail=f"No fresh data available for symbol {name}"
            )

        # Store the fresh data in database for future local access
        try:
            from app.core.database.connection import get_db_session

            async with get_db_session() as session:
                await market_data_service.store_market_data(name, data, session)
            logger.info(f"Fresh data stored locally for {name}")
        except Exception as e:
            logger.warning(f"Failed to store fresh data locally for {name}: {e}")
            # Continue even if local storage fails

        # Convert DataFrame to JSON-serializable format
        result = {
            "symbol": name.upper(),
            "period": period,
            "interval": interval,
            "source": "yfinance_fresh",
            "data_points": len(data),
            "data": data.reset_index().to_dict(orient="records"),
        }

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving fresh data for {name}: {str(e)}"
        )


@router.get("/symbol-data/local")
async def get_symbol_data_local(
    name: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, description="Maximum number of records to return"),
) -> Optional[Dict[str, Any]]:
    """
    Get stock data for a specific symbol from local database only.

    This endpoint retrieves data that has been previously stored locally,
    without attempting to fetch from external sources.

    Note: This endpoint responds quickly but may contain older data.
    """
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid start_date format. Use YYYY-MM-DD: {str(e)}",
            )
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid end_date format. Use YYYY-MM-DD: {str(e)}",
            )

    # Get data from local database
    data = await market_data_service.get_market_data(name, start_dt, end_dt, limit)

    if data is None:
        raise HTTPException(
            status_code=404, detail=f"No local data available for symbol {name}"
        )

    result = {
        "symbol": name.upper(),
        "source": "local_database",
        "data_points": len(data),
        "data": data.reset_index().to_dict(orient="records"),
    }

    return result


@router.get("/symbol-data")
async def get_symbol_data(
    name: str,
    period: str = Query(
        default="max",
        description="Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
    ),
    interval: str = Query(
        default="1d",
        description="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)",
    ),
) -> Optional[Dict[str, Any]]:
    """
    Get stock data for a specific symbol with intelligent source selection.

    This endpoint intelligently chooses the best data source:
    - If local data is fresh (< 24 hours old), returns local data for speed
    - If local data is stale, fetches fresh data from yfinance
    - Always stores fresh data locally for future use

    For guaranteed fresh data, use /symbol-data/fresh
    For guaranteed fast local data, use /symbol-data/local
    """
    try:
        # Check data quality first
        quality_info = await market_data_service.get_data_quality_info(name)

        # If we have fresh local data (< 24 hours), return it for speed
        if "error" not in quality_info and quality_info.get("is_fresh", False):
            logger.info(f"Using fresh local data for {name}")
            data = await market_data_service.get_market_data(name)

            result = {
                "symbol": name.upper(),
                "period": period,
                "interval": interval,
                "source": "local_database_fresh",
                "data_points": len(data) if data is not None and not data.empty else 0,
                "data": data.to_dict(orient="records") if data is not None and not data.empty else [],
                "data_age_hours": quality_info.get("data_age_days", 0) * 24,
            }
            return result

        # If local data is stale or doesn't exist, fetch fresh data
        logger.info(f"Fetching fresh data for {name} (local data is stale)")
        fresh_data = await market_data_service.fetch_ticker_data(
            symbol=name, period=period, interval=interval
        )

        if fresh_data is None:
            # Try to fall back to local data even if stale
            logger.warning(
                f"Fresh data unavailable for {name}, falling back to local data"
            )
            local_data = await market_data_service.get_market_data(name)

            if local_data is None:
                raise HTTPException(
                    status_code=404, detail=f"No data available for symbol {name}"
                )

            result = {
                "symbol": name.upper(),
                "period": period,
                "interval": interval,
                "source": "local_database_stale",
                "data_points": len(local_data),
                "data": local_data.reset_index().to_dict(orient="records"),
                "data_age_hours": quality_info.get("data_age_days", 0) * 24,
                "warning": "Using stale local data - fresh data unavailable",
            }
            return result

        # Use the fresh data
        data = fresh_data

        # Store the fresh data locally
        try:
            from app.core.database.connection import get_db_session

            async with get_db_session() as session:
                await market_data_service.store_market_data(name, data, session)
            logger.info(f"Fresh data stored locally for {name}")
        except Exception as e:
            logger.warning(f"Failed to store fresh data locally for {name}: {e}")

        result = {
            "symbol": name.upper(),
            "period": period,
            "interval": interval,
            "source": "yfinance_fresh",
            "data_points": len(data),
            "data": data.reset_index().to_dict(orient="records"),
        }

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving data for {name}: {str(e)}"
        )
