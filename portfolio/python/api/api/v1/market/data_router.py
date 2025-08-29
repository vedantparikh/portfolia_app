"""
Market Data Router
API endpoints for market data operations with separate endpoints for fresh and local data.
"""

import asyncio
import logging
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.connection import get_db_session
from services.data_scheduler import data_scheduler
from services.market_data_service import market_data_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/ticker/fresh")
async def get_fresh_ticker_data(
    symbol: str,
    period: str = Query(
        "max",
        description="Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
    ),
    interval: str = Query(
        "1d",
        description="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)",
    ),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get fresh market data for a specific ticker from yfinance API.

    This endpoint fetches live data from yfinance and stores it locally for future use.
    Always fetches maximum available data for comprehensive coverage.

    Note: This endpoint may take longer to respond as it fetches fresh data from external API.
    """
    try:
        symbol = symbol.upper()

        # Fetch fresh data from yfinance (always max period for comprehensive coverage)
        data = await market_data_service.fetch_ticker_data(symbol, period, interval)

        if data is None:
            raise HTTPException(
                status_code=404, detail=f"No fresh data available for ticker {symbol}"
            )

        # Store the fresh data locally
        try:
            # Convert AsyncSession to regular Session for storage
            from sqlalchemy.orm import Session

            sync_session = Session(bind=session.bind)
            await market_data_service.store_market_data(symbol, data, sync_session)
            sync_session.close()
            logger.info(f"Fresh data stored locally for {symbol}")
        except Exception as e:
            logger.warning(f"Failed to store fresh data locally for {symbol}: {e}")
            # Continue even if local storage fails

        # Convert DataFrame to JSON-serializable format
        result = {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "source": "yfinance_fresh",
            "data_points": len(data),
            "data": data.reset_index().to_dict(orient="records"),
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving fresh data for {symbol}: {str(e)}",
        )


@router.get("/ticker/")
async def get_ticker_data(
    symbol: str,
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
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get market data for a specific ticker with intelligent source selection.

    This endpoint intelligently chooses the best data source:
    - If local data is fresh (< 24 hours old), returns local data for speed
    - If local data is stale, fetches fresh data from yfinance
    - Always stores fresh data locally for future use

    For guaranteed fresh data, use /ticker/{symbol}/fresh
    For guaranteed fast local data, use /ticker/{symbol}/local
    """
    try:
        symbol = symbol.upper()

        if use_fallback:
            # Use the fallback service (always max period for comprehensive data)
            data = await market_data_service.get_data_with_fallback(symbol, "max", "1d")
        else:
            # Try only yfinance (always max period for comprehensive data)
            data = await market_data_service.fetch_ticker_data(symbol, "max", "1d")

        if data is None:
            raise HTTPException(
                status_code=404, detail=f"No data available for ticker {symbol}"
            )

        # Convert DataFrame to JSON-serializable format
        result = {
            "symbol": symbol,
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
            status_code=500, detail=f"Error retrieving data for {symbol}: {str(e)}"
        )


@router.get("/ticker/{symbol}/local")
async def get_local_ticker_data(
    symbol: str,
    start_date: Optional[datetime] = Query(
        None, description="Start date for data range"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for data range"),
    limit: int = Query(100, description="Maximum number of records to return"),
):
    """
    Get market data for a specific ticker from local database only.

    This endpoint retrieves data that has been previously stored locally,
    without attempting to fetch from external sources.
    """
    try:
        symbol = symbol.upper()

        data = await market_data_service.get_market_data(
            symbol, start_date, end_date, limit
        )

        if data is None:
            raise HTTPException(
                status_code=404, detail=f"No local data available for ticker {symbol}"
            )

        result = {
            "symbol": symbol,
            "source": "local_database",
            "data_points": len(data),
            "data": data.reset_index().to_dict(orient="records"),
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving local data for {symbol}: {str(e)}",
        )


@router.post("/ticker/{symbol}/update")
async def update_ticker_data(
    symbol: str,
    force_update: bool = Query(
        False, description="Force update even if data is recent"
    ),
):
    """
    Manually update market data for a specific ticker.

    This endpoint triggers an immediate update of market data for the specified ticker.
    """
    try:
        symbol = symbol.upper()

        # Check if update is needed
        if not force_update:
            quality_info = await market_data_service.get_data_quality_info(symbol)
            if "error" not in quality_info and quality_info.get("is_fresh", False):
                return {
                    "message": f"Data for {symbol} is already fresh",
                    "last_updated": quality_info.get("last_updated"),
                    "data_age_days": quality_info.get("data_age_days"),
                }

        # Perform the update
        success = await market_data_service._update_single_ticker(symbol)

        if success:
            return {
                "message": f"Successfully updated data for {symbol}",
                "status": "success",
            }
        else:
            raise HTTPException(
                status_code=500, detail=f"Failed to update data for {symbol}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating data for {symbol}: {str(e)}"
        )


@router.get("/ticker/{symbol}/quality")
async def get_ticker_data_quality(symbol: str):
    """
    Get information about data quality and freshness for a specific ticker.

    This endpoint provides metadata about the stored data, including
    when it was last updated and how fresh it is.
    """
    try:
        symbol = symbol.upper()

        quality_info = await market_data_service.get_data_quality_info(symbol)

        if "error" in quality_info:
            raise HTTPException(status_code=404, detail=quality_info["error"])

        return quality_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting quality info for {symbol}: {str(e)}"
        )


@router.post("/update/all")
async def update_all_tickers(
    tickers: Optional[List[str]] = Query(
        None, description="Specific tickers to update, or all if not specified"
    )
):
    """
    Update market data for multiple tickers.

    This endpoint triggers updates for either specified tickers or all active tickers.
    """
    try:
        results = await data_scheduler.manual_update(tickers)

        successful = [ticker for ticker, success in results.items() if success]
        failed = [ticker for ticker, success in results.items() if not success]

        return {
            "message": "Update operation completed",
            "total_tickers": len(results),
            "successful": successful,
            "failed": failed,
            "success_count": len(successful),
            "failed_count": len(failed),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating tickers: {str(e)}")


@router.get("/tickers/active")
async def get_active_tickers():
    """
    Get list of all active tickers in the system.

    This endpoint returns all tickers that are currently being tracked
    and have data stored locally.
    """
    try:
        tickers = await data_scheduler._get_active_tickers()

        return {"active_tickers": tickers, "count": len(tickers)}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving active tickers: {str(e)}"
        )


@router.get("/status")
async def get_service_status():
    """
    Get the current status of the market data service.

    This endpoint provides information about the service health,
    including scheduler status and recent operations.
    """
    try:
        # Get scheduler status
        scheduler_status = {
            "is_running": data_scheduler.is_running,
            "update_interval_hours": data_scheduler.update_interval_hours,
            "batch_size": data_scheduler.batch_size,
        }

        # Get recent update logs (last 24 hours)
        async with get_db_session() as session:
            from sqlalchemy import and_
            from sqlalchemy import select

            from models.market_data import DataUpdateLog

            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            result = await session.execute(
                select(DataUpdateLog)
                .where(DataUpdateLog.created_at >= cutoff_time)
                .order_by(DataUpdateLog.created_at.desc())
                .limit(10)
            )

            recent_logs = result.scalars().all()

            logs_summary = []
            for log in recent_logs:
                logs_summary.append(
                    {
                        "ticker": log.ticker_symbol,
                        "operation": log.operation,
                        "status": log.status,
                        "timestamp": log.created_at.isoformat(),
                        "records_processed": log.records_processed,
                    }
                )

        return {
            "service_status": "healthy",
            "scheduler": scheduler_status,
            "recent_operations": logs_summary,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting service status: {str(e)}"
        )


@router.post("/scheduler/start")
async def start_scheduler():
    """Start the market data scheduler."""
    try:
        if data_scheduler.is_running:
            return {"message": "Scheduler is already running", "status": "running"}

        # Start scheduler in background
        asyncio.create_task(data_scheduler.start_scheduler())

        return {"message": "Scheduler started successfully", "status": "started"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error starting scheduler: {str(e)}"
        )


@router.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the market data scheduler."""
    try:
        if not data_scheduler.is_running:
            return {"message": "Scheduler is not running", "status": "stopped"}

        await data_scheduler.stop_scheduler()

        return {"message": "Scheduler stopped successfully", "status": "stopped"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error stopping scheduler: {str(e)}"
        )


@router.post("/ticker/{symbol}/refresh-info")
async def refresh_ticker_info(symbol: str):
    """
    Refresh company information for a specific ticker.

    This endpoint fetches fresh company information from yfinance
    and updates the ticker record in the database.
    """
    try:
        symbol = symbol.upper()

        success = await market_data_service.refresh_ticker_info(symbol)

        if success:
            return {
                "message": f"Ticker information refreshed successfully for {symbol}",
                "symbol": symbol,
                "status": "refreshed",
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to refresh ticker information for {symbol}",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error refreshing ticker information for {symbol}: {str(e)}",
        )


@router.post("/tickers/refresh-all-info")
async def refresh_all_ticker_info():
    """
    Refresh company information for all active tickers.

    This endpoint fetches fresh company information from yfinance
    for all active tickers and updates their records in the database.
    """
    try:
        results = await market_data_service.refresh_all_ticker_info()

        successful = [symbol for symbol, success in results.items() if success]
        failed = [symbol for symbol, success in results.items() if not success]

        return {
            "message": "Ticker information refresh completed",
            "total_tickers": len(results),
            "successful": successful,
            "failed": failed,
            "success_count": len(successful),
            "failure_count": len(failed),
            "status": "completed",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error refreshing all ticker information: {str(e)}"
        )


@router.get("/ticker/{symbol}/info")
async def get_ticker_info(symbol: str):
    """
    Get comprehensive ticker information including company details.

    This endpoint retrieves the ticker information stored in the database,
    including company name, sector, industry, and exchange.
    """
    try:
        symbol = symbol.upper()

        async with get_db_session() as session:
            from sqlalchemy import select

            from models.market_data import TickerInfo

            result = await session.execute(
                select(TickerInfo).where(TickerInfo.symbol == symbol)
            )
            ticker = result.scalar_one_or_none()

            if not ticker:
                raise HTTPException(
                    status_code=404, detail=f"Ticker {symbol} not found in database"
                )

            return {
                "symbol": ticker.symbol,
                "name": ticker.name,
                "company_name": ticker.company_name,
                "sector": ticker.sector,
                "industry": ticker.industry,
                "exchange": ticker.exchange,
                "is_active": ticker.is_active,
                "created_at": ticker.created_at.isoformat(),
                "updated_at": ticker.updated_at.isoformat(),
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving ticker information for {symbol}: {str(e)}",
        )
