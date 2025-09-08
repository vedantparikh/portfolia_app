"""
Market Data Schemas
Pydantic schemas for market data operations and yfinance integration.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# yfinance Data Schemas
class YFinanceQuoteData(BaseModel):
    """yfinance quote data structure."""

    symbol: str = Field(..., description="Stock symbol")
    short_name: Optional[str] = Field(None, description="Short company name")
    long_name: Optional[str] = Field(None, description="Long company name")
    quote_type: Optional[str] = Field(
        None, description="Quote type (EQUITY, ETF, etc.)"
    )
    currency: Optional[str] = Field(None, description="Currency")
    exchange: Optional[str] = Field(None, description="Exchange")
    market_cap: Optional[int] = Field(None, description="Market capitalization")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")
    country: Optional[str] = Field(None, description="Country")
    isin: Optional[str] = Field(None, description="ISIN")
    cusip: Optional[str] = Field(None, description="CUSIP")
    long_description: Optional[str] = Field(None, description="Long description")


class YFinancePriceData(BaseModel):
    """yfinance price data structure."""

    date: datetime = Field(..., description="Date")
    open: Optional[Decimal] = Field(None, description="Open price")
    high: Optional[Decimal] = Field(None, description="High price")
    low: Optional[Decimal] = Field(None, description="Low price")
    close: Optional[Decimal] = Field(None, description="Close price")
    volume: Optional[int] = Field(None, description="Volume")
    dividends: Optional[Decimal] = Field(None, description="Dividends")
    stock_splits: Optional[Decimal] = Field(None, description="Stock splits")


class YFinanceDataResponse(BaseModel):
    """yfinance data response structure."""

    symbol: str = Field(..., description="Stock symbol")
    period: str = Field(..., description="Data period")
    interval: str = Field(..., description="Data interval")
    source: str = Field(..., description="Data source")
    data_points: int = Field(..., description="Number of data points")
    data: List[YFinancePriceData] = Field(..., description="Price data")


class SymbolSearchResult(BaseModel):
    """Symbol search result from yahooquery."""

    symbol: str = Field(..., description="Stock symbol")
    short_name: Optional[str] = Field(None, description="Short name")
    long_name: Optional[str] = Field(None, description="Long name")
    quote_type: Optional[str] = Field(None, description="Quote type")
    exchange: Optional[str] = Field(None, description="Exchange")
    market: Optional[str] = Field(None, description="Market")
    currency: Optional[str] = Field(None, description="Currency")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")
    market_cap: Optional[int] = Field(None, description="Market cap")


# Market Data Quality Schemas
class DataQualityInfo(BaseModel):
    """Market data quality information."""

    symbol: str = Field(..., description="Stock symbol")
    is_fresh: bool = Field(..., description="Whether data is fresh")
    last_updated: Optional[datetime] = Field(None, description="Last update time")
    data_age_days: Optional[float] = Field(None, description="Data age in days")
    data_points: Optional[int] = Field(None, description="Number of data points")
    quality_score: Optional[float] = Field(None, description="Data quality score 0-1")
    missing_days: Optional[int] = Field(None, description="Number of missing days")
    gaps: Optional[List[Dict[str, Any]]] = Field(None, description="Data gaps")


class TickerUpdateResponse(BaseModel):
    """Ticker update response."""

    message: str = Field(..., description="Update message")
    status: str = Field(..., description="Update status")
    last_updated: Optional[datetime] = Field(None, description="Last update time")
    data_age_days: Optional[float] = Field(None, description="Data age in days")


class BulkUpdateResponse(BaseModel):
    """Bulk update response."""

    message: str = Field(..., description="Update message")
    total_tickers: int = Field(..., description="Total tickers processed")
    successful: List[str] = Field(..., description="Successfully updated tickers")
    failed: List[str] = Field(..., description="Failed tickers")
    success_count: int = Field(..., description="Success count")
    failed_count: int = Field(..., description="Failed count")


class ActiveTickersResponse(BaseModel):
    """Active tickers response."""

    active_tickers: List[str] = Field(..., description="List of active tickers")
    count: int = Field(..., description="Number of active tickers")


# Scheduler Status Schemas
class SchedulerStatus(BaseModel):
    """Scheduler status information."""

    is_running: bool = Field(..., description="Whether scheduler is running")
    update_interval_hours: int = Field(..., description="Update interval in hours")
    batch_size: int = Field(..., description="Batch size for updates")


class UpdateLog(BaseModel):
    """Update log entry."""

    ticker: str = Field(..., description="Ticker symbol")
    operation: str = Field(..., description="Operation type")
    status: str = Field(..., description="Operation status")
    timestamp: datetime = Field(..., description="Operation timestamp")
    records_processed: Optional[int] = Field(None, description="Records processed")


class ServiceStatusResponse(BaseModel):
    """Service status response."""

    service_status: str = Field(..., description="Service status")
    scheduler: SchedulerStatus = Field(..., description="Scheduler status")
    recent_operations: List[UpdateLog] = Field(..., description="Recent operations")
    timestamp: datetime = Field(..., description="Response timestamp")


class SchedulerControlResponse(BaseModel):
    """Scheduler control response."""

    message: str = Field(..., description="Response message")
    status: str = Field(..., description="Scheduler status")


# Ticker Information Schemas
class TickerInfoResponse(BaseModel):
    """Ticker information response."""

    symbol: str = Field(..., description="Ticker symbol")
    name: str = Field(..., description="Ticker name")
    company_name: Optional[str] = Field(None, description="Company name")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")
    exchange: Optional[str] = Field(None, description="Exchange")
    is_active: bool = Field(..., description="Is active")
    created_at: datetime = Field(..., description="Creation date")
    updated_at: datetime = Field(..., description="Last update")


class TickerRefreshResponse(BaseModel):
    """Ticker refresh response."""

    message: str = Field(..., description="Refresh message")
    symbol: str = Field(..., description="Ticker symbol")
    status: str = Field(..., description="Refresh status")


class TickerRefreshAllResponse(BaseModel):
    """Ticker refresh all response."""

    message: str = Field(..., description="Refresh message")
    total_tickers: int = Field(..., description="Total tickers")
    successful: List[str] = Field(..., description="Successful tickers")
    failed: List[str] = Field(..., description="Failed tickers")
    success_count: int = Field(..., description="Success count")
    failure_count: int = Field(..., description="Failure count")
    status: str = Field(..., description="Overall status")


# Asset Search Schemas
class AssetSearchResponse(BaseModel):
    """Asset search response."""

    assets: List[SymbolSearchResult] = Field(..., description="Search results")
    total_count: int = Field(..., description="Total results count")
    query: str = Field(..., description="Search query")


# Market Data Summary Schemas
class MarketDataSummary(BaseModel):
    """Market data summary."""

    total_assets: int = Field(..., description="Total assets")
    active_assets: int = Field(..., description="Active assets")
    last_update: Optional[datetime] = Field(None, description="Last update")
    data_quality_score: Optional[float] = Field(
        None, description="Overall data quality"
    )
    coverage_percentage: Optional[float] = Field(
        None, description="Data coverage percentage"
    )
