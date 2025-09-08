"""
Market Data Router
API endpoints for market data operations with separate endpoints for fresh and local data.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth.dependencies import get_current_active_user
from app.core.database.connection import get_db_session
from app.core.database.models import User
from app.core.schemas.market_data import (
    ActiveTickersResponse,
    BulkUpdateResponse,
    DataQualityInfo,
    SchedulerControlResponse,
    ServiceStatusResponse,
    TickerInfoResponse,
    TickerRefreshAllResponse,
    TickerRefreshResponse,
    TickerUpdateResponse,
)
from app.core.services.data_scheduler import data_scheduler
from app.core.services.market_data_service import market_data_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.post("/ticker/update", response_model=TickerUpdateResponse)
async def update_ticker_data(
    symbol: str,
    force_update: bool = Query(
        False, description="Force update even if data is recent"
    ),
    _current_user: User = Depends(get_current_active_user),
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
                return TickerUpdateResponse(
                    message=f"Data for {symbol} is already fresh",
                    status="fresh",
                    last_updated=quality_info.get("last_updated"),
                    data_age_days=quality_info.get("data_age_days"),
                )

        # Perform the update
        success = await market_data_service.update_single_ticker(symbol)

        if success:
            return TickerUpdateResponse(
                message=f"Successfully updated data for {symbol}",
                status="success",
            )
        else:
            raise HTTPException(
                status_code=500, detail=f"Failed to update data for {symbol}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating data for {symbol}: {str(e)}"
        ) from e


@router.get("/ticker/{symbol}/quality", response_model=DataQualityInfo)
async def get_ticker_data_quality(
    symbol: str,
    _current_user: User = Depends(get_current_active_user),
):
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

        return DataQualityInfo(**quality_info)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting quality info for {symbol}: {str(e)}"
        ) from e


@router.post("/update/all", response_model=BulkUpdateResponse)
async def update_all_tickers(
    tickers: Optional[List[str]] = Query(
        None, description="Specific tickers to update, or all if not specified"
    ),
    _current_user: User = Depends(get_current_active_user),
):
    """
    Update market data for multiple tickers.

    This endpoint triggers updates for either specified tickers or all active tickers.
    """
    try:
        results = await data_scheduler.manual_update(tickers)

        successful = [ticker for ticker, success in results.items() if success]
        failed = [ticker for ticker, success in results.items() if not success]

        return BulkUpdateResponse(
            message="Update operation completed",
            total_tickers=len(results),
            successful=successful,
            failed=failed,
            success_count=len(successful),
            failed_count=len(failed),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating tickers: {str(e)}"
        ) from e


@router.get("/tickers/active", response_model=ActiveTickersResponse)
async def get_active_tickers(
    _current_user: User = Depends(get_current_active_user),
):
    """
    Get list of all active tickers in the system.

    This endpoint returns all tickers that are currently being tracked
    and have data stored locally.
    """
    try:
        tickers = await data_scheduler._get_active_tickers()

        return ActiveTickersResponse(active_tickers=tickers, count=len(tickers))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving active tickers: {str(e)}"
        ) from e


@router.get("/status", response_model=ServiceStatusResponse)
async def get_service_status(
    _current_user: User = Depends(get_current_active_user),
):
    """
    Get the current status of the market data service.

    This endpoint provides information about the service health,
    including scheduler status and recent operations.
    """
    try:
        # Get scheduler status
        from app.core.schemas.market_data import SchedulerStatus, UpdateLog

        scheduler_status = SchedulerStatus(
            is_running=data_scheduler.is_running,
            update_interval_hours=data_scheduler.update_interval_hours,
            batch_size=data_scheduler.batch_size,
        )

        # Get recent update logs (last 24 hours)
        async with get_db_session() as session:
            from sqlalchemy import select

            from app.core.database.models.market_data import DataUpdateLog

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
                    UpdateLog(
                        ticker=log.ticker_symbol,
                        operation=log.operation,
                        status=log.status,
                        timestamp=log.created_at,
                        records_processed=log.records_processed,
                    )
                )

        return ServiceStatusResponse(
            service_status="healthy",
            scheduler=scheduler_status,
            recent_operations=logs_summary,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting service status: {str(e)}"
        ) from e


@router.post("/scheduler/start", response_model=SchedulerControlResponse)
async def start_scheduler(
    _current_user: User = Depends(get_current_active_user),
):
    """Start the market data scheduler."""
    try:
        if data_scheduler.is_running:
            return SchedulerControlResponse(
                message="Scheduler is already running", status="running"
            )

        # Start scheduler in background
        asyncio.create_task(data_scheduler.start_scheduler())

        return SchedulerControlResponse(
            message="Scheduler started successfully", status="started"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error starting scheduler: {str(e)}"
        ) from e


@router.post("/scheduler/stop", response_model=SchedulerControlResponse)
async def stop_scheduler(
    _current_user: User = Depends(get_current_active_user),
):
    """Stop the market data scheduler."""
    try:
        if not data_scheduler.is_running:
            return SchedulerControlResponse(
                message="Scheduler is not running", status="stopped"
            )

        await data_scheduler.stop_scheduler()

        return SchedulerControlResponse(
            message="Scheduler stopped successfully", status="stopped"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error stopping scheduler: {str(e)}"
        ) from e


@router.post("/ticker/{symbol}/refresh-info", response_model=TickerRefreshResponse)
async def refresh_ticker_info(
    symbol: str,
    _current_user: User = Depends(get_current_active_user),
):
    """
    Refresh company information for a specific ticker.

    This endpoint fetches fresh company information from yfinance
    and updates the ticker record in the database.
    """
    try:
        symbol = symbol.upper()

        success = await market_data_service.refresh_ticker_info(symbol)

        if success:
            return TickerRefreshResponse(
                message=f"Ticker information refreshed successfully for {symbol}",
                symbol=symbol,
                status="refreshed",
            )
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
        ) from e


@router.post("/tickers/refresh-all-info", response_model=TickerRefreshAllResponse)
async def refresh_all_ticker_info(
    _current_user: User = Depends(get_current_active_user),
):
    """
    Refresh company information for all active tickers.

    This endpoint fetches fresh company information from yfinance
    for all active tickers and updates their records in the database.
    """
    try:
        results = await market_data_service.refresh_all_ticker_info()

        successful = [symbol for symbol, success in results.items() if success]
        failed = [symbol for symbol, success in results.items() if not success]

        return TickerRefreshAllResponse(
            message="Ticker information refresh completed",
            total_tickers=len(results),
            successful=successful,
            failed=failed,
            success_count=len(successful),
            failure_count=len(failed),
            status="completed",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error refreshing all ticker information: {str(e)}"
        ) from e


@router.get("/ticker/{symbol}/info", response_model=TickerInfoResponse)
async def get_ticker_info(
    symbol: str,
    _current_user: User = Depends(get_current_active_user),
):
    """
    Get comprehensive ticker information including company details.

    This endpoint retrieves the ticker information stored in the database,
    including company name, sector, industry, and exchange.
    """
    try:
        symbol = symbol.upper()

        async with get_db_session() as session:
            from sqlalchemy import select

            from app.core.database.models.market_data import TickerInfo

            result = await session.execute(
                select(TickerInfo).where(TickerInfo.symbol == symbol)
            )
            ticker = result.scalar_one_or_none()

            if not ticker:
                raise HTTPException(
                    status_code=404, detail=f"Ticker {symbol} not found in database"
                )

            return TickerInfoResponse(
                symbol=ticker.symbol,
                name=ticker.name,
                company_name=ticker.company_name,
                sector=ticker.sector,
                industry=ticker.industry,
                exchange=ticker.exchange,
                is_active=ticker.is_active,
                created_at=ticker.created_at,
                updated_at=ticker.updated_at,
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving ticker information for {symbol}: {str(e)}",
        ) from e
