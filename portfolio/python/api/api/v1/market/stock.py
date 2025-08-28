"""
Stock Router
API endpoints for stock data operations using the new market data service.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from services.market_data_service import market_data_service
from models.market import Symbol

router = APIRouter(prefix="/stock")


@router.get("/symbols")
async def get_symbols(name: str):
    """
    Get stock symbols matching the search name.

    This endpoint searches for stock symbols using yahooquery and returns
    matching results with symbol and quote type information.
    """
    try:
        from yahooquery import search

        # Search for symbols
        data = search(name)

        if not data or "quotes" not in data:
            return []

        quotes = data["quotes"]
        if len(quotes) == 0:
            return "No Symbol Found"

        symbols = [
            Symbol(symbol=str(qoute["symbol"]), quoteType=str(qoute["quoteType"]))
            for qoute in quotes
        ]

        return symbols

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching for symbols: {str(e)}"
        )


@router.get("/symbol-data")
async def get_symbol_data(
        name: str,
        period: str = Query(
            "1y",
            description="Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
        ),
        interval: str = Query(
            "1d",
            description="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)",
        ),
        use_fallback: bool = Query(
            True, description="Use fallback to local data if yfinance fails"
        ),
):
    """
    Get stock data for a specific symbol with fallback to local data.

    This endpoint uses the new market data service which provides:
    - Fresh data from yfinance when available
    - Fallback to locally stored data when external API fails
    - Automatic data storage and retrieval
    """
    try:
        # Use the new market data service with fallback (always max period for comprehensive data)
        data = await market_data_service.get_data_with_fallback(name, "max", "1d")

        if data is None:
            raise HTTPException(
                status_code=404, detail=f"No data available for symbol {name}"
            )

        # Convert DataFrame to JSON-serializable format
        result = {
            "symbol": name.upper(),
            "period": period,
            "interval": interval,
            "data_points": len(data),
            "data": data.reset_index().to_dict(orient="records"),
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving data for {name}: {str(e)}"
        )


@router.get("/symbol-data/local")
async def get_symbol_data_local(
        name: str,
        start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        limit: int = Query(100, description="Maximum number of records to return"),
):
    """
    Get stock data for a specific symbol from local database only.

    This endpoint retrieves data that has been previously stored locally,
    without attempting to fetch from external sources.
    """
    try:
        from datetime import datetime

        # Parse dates if provided
        start_dt = None
        end_dt = None

        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

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

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving local data for {name}: {str(e)}"
        )
