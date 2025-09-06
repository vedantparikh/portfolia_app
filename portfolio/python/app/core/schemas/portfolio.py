from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.core.database.models.asset import AssetType


class PortfolioBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    currency: str = Field(default="USD", max_length=3)
    is_active: bool = Field(default=True)
    is_public: bool = Field(default=False)


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    currency: Optional[str] = Field(None, max_length=3)
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class Portfolio(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PortfolioAssetBase(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: Decimal = Field(...)
    cost_basis: Decimal = Field(...)
    cost_basis_total: Decimal = Field(...)
    current_value: Optional[Decimal] = Field(None)
    unrealized_pnl: Optional[Decimal] = Field(None)
    unrealized_pnl_percent: Optional[Decimal] = Field(None)


class PortfolioAssetCreate(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: Decimal = Field(...)
    cost_basis: Decimal = Field(...)


class PortfolioAssetUpdate(BaseModel):
    quantity: Optional[Decimal] = Field(None)
    cost_basis: Optional[Decimal] = Field(None)
    current_value: Optional[Decimal] = Field(None)
    unrealized_pnl: Optional[Decimal] = Field(None)
    unrealized_pnl_percent: Optional[Decimal] = Field(None)


class PortfolioAsset(PortfolioAssetBase):
    id: int
    last_updated: datetime

    class Config:
        from_attributes = True


class PortfolioAssetWithDetails(PortfolioAsset):
    """Portfolio asset with additional asset information"""

    symbol: Optional[str] = None
    asset_name: Optional[str] = None
    market_value: Optional[Decimal] = None
    total_return: Optional[Decimal] = None
    total_return_percent: Optional[Decimal] = None


class AssetBase(BaseModel):
    symbol: str
    name: str
    asset_type: AssetType
    currency: str
    exchange: Optional[str] = None
    isin: Optional[str] = None
    cusip: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime
    updated_at: Optional[datetime] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None)
    asset_type: Optional[AssetType] = Field(None)
    currency: Optional[str] = Field(None)
    exchange: Optional[str] = Field(None)
    isin: Optional[str] = Field(None)
    cusip: Optional[str] = Field(None)
    sector: Optional[str] = Field(None)
    industry: Optional[str] = Field(None)
    country: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)


class Asset(AssetBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    portfolio_id: int
    asset_id: int
    transaction_type: str = Field(..., description="'buy', 'sell', 'dividend'")
    quantity: Decimal = Field(...)
    price: Decimal = Field(...)
    currency: str
    transaction_date: datetime
    fees: Optional[Decimal] = Field(0)
    total_amount: Optional[Decimal] = Field(None)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    quantity: Optional[Decimal] = Field(None)
    price: Optional[Decimal] = Field(None)
    transaction_date: Optional[datetime] = None
    fees: Optional[Decimal] = Field(None)
    currency: Optional[str] = None


class Transaction(TransactionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """Portfolio summary with performance metrics"""

    portfolio_id: int
    portfolio_name: str
    currency: str
    total_assets: int
    total_cost_basis: float
    total_current_value: float
    total_unrealized_pnl: float
    total_unrealized_pnl_percent: float
    last_updated: Optional[datetime]
    recent_transactions: int
    is_active: bool
    is_public: bool


class PortfolioHolding(BaseModel):
    """Detailed portfolio holding with current values"""

    asset_id: int
    symbol: str
    name: str
    quantity: float
    cost_basis: float
    cost_basis_total: float
    current_value: Optional[float]
    unrealized_pnl: Optional[float]
    unrealized_pnl_percent: Optional[float]
    last_updated: datetime


class PortfolioStatistics(BaseModel):
    """Overall portfolio statistics for a user"""

    total_portfolios: int
    active_portfolios: int
    total_assets: int
    total_value: float


# Legacy class for backward compatibility - maps to PortfolioAsset
class PortfolioItem(BaseModel):
    id: int
    currency: str
    portfolio_id: int
    asset_id: int
    quantity: Decimal
    average_price: Decimal  # Maps to cost_basis
    created_at: datetime  # Maps to last_updated
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
