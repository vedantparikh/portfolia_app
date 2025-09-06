from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class Symbol(BaseModel):
    id: int
    symbol: str
    name: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockData(BaseModel):
    symbol: str
    price: Decimal
    volume: int
    timestamp: datetime
    open_price: Optional[Decimal] = None
    high_price: Optional[Decimal] = None
    low_price: Optional[Decimal] = None
    previous_close: Optional[Decimal] = None
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None


class MarketData(BaseModel):
    symbol: str
    name: str
    latest_price: Decimal
    latest_date: Optional[datetime] = None
    market_cap: Optional[int] = None
    pe_ratio: Optional[Decimal] = None
    currency: Optional[str] = None
    exchange: Optional[str] = None
    dividend_yield: Optional[Decimal] = None
    beta: Optional[Decimal] = None


class MarketIndex(BaseModel):
    name: str
    value: Decimal
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    timestamp: datetime


class StockQuote(BaseModel):
    symbol: str
    price: Decimal
    volume: int
    timestamp: datetime
