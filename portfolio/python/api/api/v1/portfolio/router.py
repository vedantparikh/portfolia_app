"""
Portfolio management router with full authentication.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database.connection import get_db
from app.core.database.models import (
    User,
    Portfolio as PortfolioModel,
    PortfolioAsset,
    Asset,
)
from app.core.auth.dependencies import (
    get_current_active_user,
    get_current_verified_user,
)
from app.core.auth.schemas import UserResponse
from models.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    Portfolio,
    PortfolioItem,
    AssetCreate,
    AssetUpdate,
    Asset as AssetSchema,
    TransactionCreate,
    TransactionUpdate,
    Transaction,
)

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.post("/", response_model=Portfolio, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Create a new portfolio for the authenticated user."""
    # Override user_id to ensure user can only create portfolios for themselves
    portfolio_data.user_id = current_user.id

    new_portfolio = PortfolioModel(
        user_id=portfolio_data.user_id,
        name=portfolio_data.name,
        description=portfolio_data.description,
        currency="USD",  # Default currency
    )

    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)

    return new_portfolio


@router.get("/", response_model=List[Portfolio])
async def get_user_portfolios(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get all portfolios for the authenticated user."""
    portfolios = (
        db.query(PortfolioModel)
        .filter(
            PortfolioModel.user_id == current_user.id, PortfolioModel.is_active == True
        )
        .all()
    )

    return portfolios


@router.get("/{portfolio_id}", response_model=Portfolio)
async def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific portfolio by ID (user must own it)."""
    portfolio = (
        db.query(PortfolioModel)
        .filter(
            PortfolioModel.id == portfolio_id,
            PortfolioModel.user_id == current_user.id,
            PortfolioModel.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    return portfolio


@router.put("/{portfolio_id}", response_model=Portfolio)
async def update_portfolio(
    portfolio_id: int,
    portfolio_update: PortfolioUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a portfolio (user must own it)."""
    portfolio = (
        db.query(PortfolioModel)
        .filter(
            PortfolioModel.id == portfolio_id,
            PortfolioModel.user_id == current_user.id,
            PortfolioModel.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Update only provided fields
    update_data = portfolio_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(portfolio, field, value)

    db.commit()
    db.refresh(portfolio)

    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a portfolio (user must own it)."""
    portfolio = (
        db.query(PortfolioModel)
        .filter(
            PortfolioModel.id == portfolio_id,
            PortfolioModel.user_id == current_user.id,
            PortfolioModel.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Soft delete by marking as inactive
    portfolio.is_active = False
    db.commit()

    return None


@router.post(
    "/{portfolio_id}/assets",
    response_model=PortfolioItem,
    status_code=status.HTTP_201_CREATED,
)
async def add_asset_to_portfolio(
    portfolio_id: int,
    asset_data: AssetCreate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Add an asset to a portfolio (user must own the portfolio)."""
    # Verify portfolio ownership
    portfolio = (
        db.query(PortfolioModel)
        .filter(
            PortfolioModel.id == portfolio_id,
            PortfolioModel.user_id == current_user.id,
            PortfolioModel.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Override portfolio_id to ensure asset goes to correct portfolio
    asset_data.portfolio_id = portfolio_id

    # Check if asset already exists in portfolio
    existing_asset = (
        db.query(PortfolioAsset)
        .filter(
            PortfolioAsset.portfolio_id == portfolio_id,
            PortfolioAsset.asset_id == asset_data.asset_id,
        )
        .first()
    )

    if existing_asset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset already exists in portfolio",
        )

    # Create portfolio asset
    portfolio_asset = PortfolioAsset(
        portfolio_id=portfolio_id,
        asset_id=asset_data.asset_id,
        quantity=asset_data.quantity,
        cost_basis=asset_data.purchase_price,
        cost_basis_total=asset_data.quantity * asset_data.purchase_price,
    )

    db.add(portfolio_asset)
    db.commit()
    db.refresh(portfolio_asset)

    return portfolio_asset


@router.get("/{portfolio_id}/assets", response_model=List[PortfolioItem])
async def get_portfolio_assets(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all assets in a portfolio (user must own the portfolio)."""
    # Verify portfolio ownership
    portfolio = (
        db.query(PortfolioModel)
        .filter(
            PortfolioModel.id == portfolio_id,
            PortfolioModel.user_id == current_user.id,
            PortfolioModel.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    assets = (
        db.query(PortfolioAsset)
        .filter(PortfolioAsset.portfolio_id == portfolio_id)
        .all()
    )

    return assets


@router.put("/{portfolio_id}/assets/{asset_id}", response_model=PortfolioItem)
async def update_portfolio_asset(
    portfolio_id: int,
    asset_id: int,
    asset_update: AssetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update an asset in a portfolio (user must own the portfolio)."""
    # Verify portfolio ownership
    portfolio = (
        db.query(PortfolioModel)
        .filter(
            PortfolioModel.id == portfolio_id,
            PortfolioModel.user_id == current_user.id,
            PortfolioModel.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Find the portfolio asset
    portfolio_asset = (
        db.query(PortfolioAsset)
        .filter(
            PortfolioAsset.portfolio_id == portfolio_id,
            PortfolioAsset.asset_id == asset_id,
        )
        .first()
    )

    if not portfolio_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found in portfolio"
        )

    # Update only provided fields
    update_data = asset_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(portfolio_asset, field, value)

    # Recalculate cost basis total if quantity or purchase price changed
    if "quantity" in update_data or "purchase_price" in update_data:
        portfolio_asset.cost_basis_total = (
            portfolio_asset.quantity * portfolio_asset.cost_basis
        )

    db.commit()
    db.refresh(portfolio_asset)

    return portfolio_asset


@router.delete(
    "/{portfolio_id}/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_asset_from_portfolio(
    portfolio_id: int,
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove an asset from a portfolio (user must own the portfolio)."""
    # Verify portfolio ownership
    portfolio = (
        db.query(PortfolioModel)
        .filter(
            PortfolioModel.id == portfolio_id,
            PortfolioModel.user_id == current_user.id,
            PortfolioModel.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Find and delete the portfolio asset
    portfolio_asset = (
        db.query(PortfolioAsset)
        .filter(
            PortfolioAsset.portfolio_id == portfolio_id,
            PortfolioAsset.asset_id == asset_id,
        )
        .first()
    )

    if not portfolio_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found in portfolio"
        )

    db.delete(portfolio_asset)
    db.commit()

    return None


@router.get("/{portfolio_id}/summary")
async def get_portfolio_summary(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get portfolio summary with total value and performance metrics."""
    # Verify portfolio ownership
    portfolio = (
        db.query(PortfolioModel)
        .filter(
            PortfolioModel.id == portfolio_id,
            PortfolioModel.user_id == current_user.id,
            PortfolioModel.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Get portfolio assets
    assets = (
        db.query(PortfolioAsset)
        .filter(PortfolioAsset.portfolio_id == portfolio_id)
        .all()
    )

    # Calculate summary metrics
    total_cost_basis = sum(float(asset.cost_basis_total) for asset in assets)
    total_current_value = sum(
        float(asset.current_value or asset.cost_basis_total) for asset in assets
    )
    total_unrealized_pnl = total_current_value - total_cost_basis
    total_unrealized_pnl_percent = (
        (total_unrealized_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0
    )

    return {
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio.name,
        "currency": portfolio.currency,
        "total_assets": len(assets),
        "total_cost_basis": round(total_cost_basis, 2),
        "total_current_value": round(total_current_value, 2),
        "total_unrealized_pnl": round(total_unrealized_pnl, 2),
        "total_unrealized_pnl_percent": round(total_unrealized_pnl_percent, 2),
        "last_updated": portfolio.updated_at,
    }
