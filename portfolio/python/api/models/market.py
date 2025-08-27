from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

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
    current_price: Decimal
    market_cap: Optional[int] = None
    pe_ratio: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    beta: Optional[Decimal] = None
    timestamp: datetime

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
