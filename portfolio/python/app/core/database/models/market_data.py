"""
Market Data Models
Database models for storing market data and ticker information.
"""

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database.connection import Base


class TickerInfo(Base):
    """Model for storing ticker information."""

    __tablename__ = "ticker_info"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    company_name = Column(String(500), nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    exchange = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    currency = Column(String(20), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    market_data = relationship(
        "MarketData", back_populates="ticker", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TickerInfo(symbol='{self.symbol}', name='{self.name}')>"


class MarketData(Base):
    """Model for storing daily market data."""

    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(
        Integer, ForeignKey("ticker_info.id"), nullable=False, index=True
    )
    date = Column(Date, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    adjusted_close = Column(Float, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    ticker = relationship("TickerInfo", back_populates="market_data")

    # Composite unique constraint
    __table_args__ = (
        Index("idx_ticker_date_unique", "ticker_id", "date", unique=True),
        Index("idx_date_ticker", "date", "ticker_id"),
    )

    def __repr__(self):
        return f"<MarketData(ticker_id={self.ticker_id}, date='{self.date}', close={self.close_price})>"


class DataUpdateLog(Base):
    """Model for logging data update operations."""

    __tablename__ = "data_update_log"

    id = Column(Integer, primary_key=True, index=True)
    ticker_symbol = Column(String(20), nullable=False, index=True)
    operation = Column(
        String(50), nullable=False
    )  # 'fetch', 'store', 'update', 'fallback'
    status = Column(String(20), nullable=False)  # 'success', 'failed', 'partial'
    records_processed = Column(Integer, default=0)
    error_message = Column(String(1000), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<DataUpdateLog(ticker='{self.ticker_symbol}', operation='{self.operation}', status='{self.status}')>"
