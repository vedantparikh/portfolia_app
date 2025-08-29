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

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from yahooquery import search

from services.market_data_service import market_data_service
from app.core.auth.dependencies import get_optional_current_user, get_client_ip
from app.core.auth.utils import is_rate_limited, rate_limit_key

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/symbols")
async def get_symbols(
    name: str, request: Request = None, current_user=Depends(get_optional_current_user)
) -> Optional[List[Dict[str, Any]]]:
    """
    Get stock symbols matching the search name.

    Rate limited for unauthenticated users to prevent abuse.
    """
    # Rate limiting for unauthenticated users
    if not current_user:
        client_ip = get_client_ip(request) if request else "unknown"
        if is_rate_limited(
            client_ip, "symbol_search", max_attempts=10, window_seconds=3600
        ):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please authenticate or try again later.",
            )

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
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    request: Request = None,
    current_user=Depends(get_optional_current_user),
) -> Optional[Dict[str, Any]]:
    """
    Get fresh stock data for a specific symbol from yfinance API.

    Rate limited for unauthenticated users to prevent abuse.
    """
    # Rate limiting for unauthenticated users
    if not current_user:
        client_ip = get_client_ip(request) if request else "unknown"
        if is_rate_limited(
            client_ip, "fresh_data", max_attempts=5, window_seconds=3600
        ):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please authenticate or try again later.",
            )

    try:
        # Fetch fresh data from yfinance (always max period for comprehensive coverage)
        data = await market_data_service.fetch_ticker_data(
            symbol=name,
            period=period,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )

        if data is None:
            raise HTTPException(
                status_code=404, detail=f"No fresh data available for symbol {name}"
            )

        # Convert DataFrame to JSON-serializable format
        result = {
            "symbol": name.upper(),
            "period": period,
            "interval": interval,
            "source": "yfinance_fresh",
            "data_points": len(data),
            "data": data.to_dict(orient="records"),
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
    request: Request = None,
    current_user=Depends(get_optional_current_user),
) -> Optional[Dict[str, Any]]:
    """
    Get stock data for a specific symbol from local database only.

    Rate limited for unauthenticated users to prevent abuse.
    """
    # Rate limiting for unauthenticated users
    if not current_user:
        client_ip = get_client_ip(request) if request else "unknown"
        if is_rate_limited(
            client_ip, "local_data", max_attempts=20, window_seconds=3600
        ):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please authenticate or try again later.",
            )

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
        data = await market_data_service.get_market_data(
            symbol=name, start_date=start_dt, end_date=end_dt
        )

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
    request: Request = None,
    current_user=Depends(get_optional_current_user),
) -> Optional[Dict[str, Any]]:
    """
    Get stock data for a specific symbol with intelligent source selection.

    Rate limited for unauthenticated users to prevent abuse.
    """
    # Rate limiting for unauthenticated users
    if not current_user:
        client_ip = get_client_ip(request) if request else "unknown"
        if is_rate_limited(
            client_ip, "intelligent_data", max_attempts=15, window_seconds=3600
        ):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please authenticate or try again later.",
            )

    try:
        # Check data quality first
        data = await market_data_service.get_data_with_fallback(symbol=name, period=period, interval=interval)

        result = {
            "symbol": name.upper(),
            "period": period,
            "interval": interval,
            "source": "local_database_stale",
            "data_points": len(data) if data else 0,
            "data": data.to_dict(orient="records") if data else [],
        }
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving data for {name}: {str(e)}"
        )
