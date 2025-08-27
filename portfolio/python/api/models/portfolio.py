from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    user_id: int

class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Portfolio(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AssetBase(BaseModel):
    symbol: str
    quantity: Decimal
    purchase_price: Decimal
    portfolio_id: int

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None

class Asset(AssetBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    asset_id: int
    transaction_type: str  # 'buy', 'sell', 'dividend'
    quantity: Decimal
    price: Decimal
    transaction_date: datetime
    fees: Optional[Decimal] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None
    transaction_date: Optional[datetime] = None
    fees: Optional[Decimal] = None

class Transaction(TransactionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
