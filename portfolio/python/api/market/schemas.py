from datetime import datetime
from pydantic import BaseModel


class Symbol(BaseModel):
    symbol: str
    quoteType: str


class StockData(BaseModel):
    id: datetime
    open: float
    close: float
    low: float
    high: float
    volume: int
    dividends: float
