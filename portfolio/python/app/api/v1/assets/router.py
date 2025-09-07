"""
Assets management router with authentication.
"""

import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth.dependencies import (
    get_current_active_user,
    get_current_verified_user,
)
from app.core.database.connection import get_db
from app.core.database.models import Asset as AssetModel, User
from app.core.database.models.asset import AssetType
from app.core.logging_config import get_logger, log_api_request, log_api_response
from app.core.schemas.portfolio import (
    Asset as AssetSchema,
    AssetCreate,
    AssetUpdate,
    AssetPrice,
)
from app.core.services.market_data_service import market_data_service

logger = get_logger(__name__)

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/", response_model=AssetSchema, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Create a new financial asset."""
    log_api_request(
        logger,
        "POST",
        "/assets",
        current_user.id,
        f"Creating asset: {asset_data.symbol}",
    )
    start_time = time.time()
    # Check if asset already exists
    existing_asset = (
        db.query(AssetModel)
        .filter(AssetModel.symbol == asset_data.symbol.upper())
        .first()
    )

    if existing_asset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset with this symbol already exists",
        )
    ticker_data = await market_data_service.get_ticker_info(asset_data.symbol.upper())

    new_asset = AssetModel(
        symbol=asset_data.symbol.upper(),
        name=ticker_data.get("longName") or ticker_data.get("shortName"),
        asset_type=(
            AssetType[ticker_data.get("quoteType").upper()]
            if ticker_data.get("quoteType")
            else AssetType.OTHER
        ),
        currency=ticker_data.get("currency"),
        exchange=ticker_data.get("exchange"),
        isin=ticker_data.get("isin"),
        cusip=ticker_data.get("cusip"),
        sector=ticker_data.get("sector"),
        industry=ticker_data.get("industry"),
        country=ticker_data.get("country"),
        description=ticker_data.get("longDescription"),
        # Default name from symbol
        is_active=True,
    )

    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    response_time = time.time() - start_time
    log_api_response(logger, "POST", "/assets", 200, response_time)
    return new_asset


@router.get("/", response_model=List[AssetSchema])
async def get_assets(
    skip: int = Query(0, ge=0, description="Number of assets to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of assets to return"
    ),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get list of financial assets with optional filtering."""
    query = db.query(AssetModel).filter(AssetModel.is_active == True)

    if symbol:
        query = query.filter(AssetModel.symbol.ilike(f"%{symbol.upper()}%"))

    if asset_type:
        query = query.filter(AssetModel.asset_type == asset_type)

    assets = query.offset(skip).limit(limit).all()

    return assets


@router.get("/{asset_id}", response_model=AssetSchema)
async def get_asset(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific financial asset by ID."""
    asset = (
        db.query(AssetModel)
        .filter(AssetModel.id == asset_id, AssetModel.is_active == True)
        .first()
    )

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
        )

    return asset


@router.put("/{asset_id}", response_model=AssetSchema)
async def update_asset(
    asset_id: int,
    asset_update: AssetUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Update a financial asset (admin/verified users only)."""
    asset = (
        db.query(AssetModel)
        .filter(AssetModel.id == asset_id, AssetModel.is_active == True)
        .first()
    )

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
        )

    # Update only provided fields
    update_data = asset_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)

    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Delete a financial asset (admin/verified users only)."""
    asset = (
        db.query(AssetModel)
        .filter(AssetModel.id == asset_id, AssetModel.is_active == True)
        .first()
    )

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
        )

    # Soft delete by marking as inactive
    asset.is_active = False
    db.commit()

    return None


@router.get("/search/{query}")
async def search_assets(
    query: str,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Search for assets by symbol or name."""
    assets = (
        db.query(AssetModel)
        .filter(
            AssetModel.is_active == True,
            (
                AssetModel.symbol.ilike(f"%{query.upper()}%")
                | AssetModel.name.ilike(f"%{query}%")
            ),
        )
        .limit(limit)
        .all()
    )

    return assets


@router.get("/{asset_id}/prices", response_model=AssetPrice)
async def get_asset_prices(
    asset_id: int,
    period: str = Query("1y", description="Data period"),
    interval: str = Query("1d", description="Data interval"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get price data for a specific asset."""
    asset = (
        db.query(AssetModel)
        .filter(AssetModel.id == asset_id, AssetModel.is_active == True)
        .first()
    )

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
        )

    try:
        # Use the market data service to get prices
        data = await market_data_service.fetch_ticker_data(
            symbol=asset.symbol, period=period, interval=interval
        )
        if not data.empty:
            data.rename(
                columns={
                    "Date": "date",
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                    "Dividends": "dividends",
                    "Stock Splits": "stock_splits",
                },
                inplace=True,
            )

        if data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No price data available for {asset.symbol}",
            )

        return {
            "asset_id": asset_id,
            "symbol": asset.symbol,
            "period": period,
            "interval": interval,
            "data_points": len(data),
            "data": data.to_dict(orient="records"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving price data: {str(e)}",
        )
