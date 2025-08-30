"""
Analytics and reporting router with authentication.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.database.connection import get_db
from app.core.database.models import User, Portfolio, PortfolioAsset, Transaction
from app.core.auth.dependencies import (
    get_current_active_user,
    get_current_verified_user,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/performance/{portfolio_id}")
async def get_portfolio_performance(
    portfolio_id: int,
    period: str = Query(
        "1y", description="Performance period (1m, 3m, 6m, 1y, 2y, 5y, max)"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get portfolio performance metrics."""
    # Verify portfolio ownership
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
            Portfolio.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found or access denied",
        )

    # Get portfolio assets
    assets = (
        db.query(PortfolioAsset)
        .filter(PortfolioAsset.portfolio_id == portfolio_id)
        .all()
    )

    if not assets:
        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "period": period,
            "total_value": 0,
            "total_cost_basis": 0,
            "total_return": 0,
            "total_return_percent": 0,
            "message": "No assets in portfolio",
        }

    # Calculate performance metrics
    total_cost_basis = sum(float(asset.cost_basis_total) for asset in assets)
    total_current_value = sum(
        float(asset.current_value or asset.cost_basis_total) for asset in assets
    )
    total_return = total_current_value - total_cost_basis
    total_return_percent = (
        (total_return / total_cost_basis * 100) if total_cost_basis > 0 else 0
    )

    # Calculate per-asset performance
    asset_performance = []
    for asset in assets:
        asset_return = float(asset.current_value or asset.cost_basis_total) - float(
            asset.cost_basis_total
        )
        asset_return_percent = (
            (asset_return / float(asset.cost_basis_total) * 100)
            if float(asset.cost_basis_total) > 0
            else 0
        )

        asset_performance.append(
            {
                "asset_id": asset.asset_id,
                "symbol": getattr(asset.asset, "symbol", "Unknown"),
                "quantity": float(asset.quantity),
                "cost_basis": float(asset.cost_basis),
                "current_value": float(asset.current_value or asset.cost_basis_total),
                "return": round(asset_return, 2),
                "return_percent": round(asset_return_percent, 2),
            }
        )

    return {
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio.name,
        "period": period,
        "total_value": round(total_current_value, 2),
        "total_cost_basis": round(total_cost_basis, 2),
        "total_return": round(total_return, 2),
        "total_return_percent": round(total_return_percent, 2),
        "asset_count": len(assets),
        "asset_performance": asset_performance,
        "calculated_at": datetime.utcnow().isoformat(),
    }


@router.get("/risk/{portfolio_id}")
async def get_portfolio_risk_metrics(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get portfolio risk metrics."""
    # Verify portfolio ownership
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
            Portfolio.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found or access denied",
        )

    # Get portfolio assets
    assets = (
        db.query(PortfolioAsset)
        .filter(PortfolioAsset.portfolio_id == portfolio_id)
        .all()
    )

    if not assets:
        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "message": "No assets in portfolio",
            "risk_metrics": {},
        }

    # Calculate risk metrics
    total_value = sum(
        float(asset.current_value or asset.cost_basis_total) for asset in assets
    )

    # Calculate concentration risk (largest position percentage)
    asset_weights = []
    for asset in assets:
        asset_value = float(asset.current_value or asset.cost_basis_total)
        weight = (asset_value / total_value * 100) if total_value > 0 else 0
        asset_weights.append(
            {
                "asset_id": asset.asset_id,
                "symbol": getattr(asset.asset, "symbol", "Unknown"),
                "weight": round(weight, 2),
                "value": round(asset_value, 2),
            }
        )

    # Sort by weight (descending)
    asset_weights.sort(key=lambda x: x["weight"], reverse=True)

    # Calculate concentration metrics
    largest_position_weight = asset_weights[0]["weight"] if asset_weights else 0
    top_5_concentration = sum(asset["weight"] for asset in asset_weights[:5])
    top_10_concentration = sum(asset["weight"] for asset in asset_weights[:10])

    # Calculate diversification score (Herfindahl-Hirschman Index)
    hhi = sum((asset["weight"] / 100) ** 2 for asset in asset_weights)
    diversification_score = max(0, 100 - (hhi * 100))  # Convert to 0-100 scale

    return {
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio.name,
        "total_value": round(total_value, 2),
        "asset_count": len(assets),
        "risk_metrics": {
            "largest_position_weight": round(largest_position_weight, 2),
            "top_5_concentration": round(top_5_concentration, 2),
            "top_10_concentration": round(top_10_concentration, 2),
            "diversification_score": round(diversification_score, 2),
            "concentration_risk": (
                "High"
                if largest_position_weight > 20
                else "Medium" if largest_position_weight > 10 else "Low"
            ),
        },
        "asset_weights": asset_weights,
        "calculated_at": datetime.utcnow().isoformat(),
    }


@router.get("/benchmark/{portfolio_id}")
async def get_portfolio_benchmark_comparison(
    portfolio_id: int,
    benchmark_symbol: str = Query(
        "^GSPC", description="Benchmark symbol (default: S&P 500)"
    ),
    period: str = Query("1y", description="Comparison period"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Compare portfolio performance against a benchmark."""
    # Verify portfolio ownership
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
            Portfolio.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found or access denied",
        )

    try:
        # Get portfolio performance
        portfolio_performance = await get_portfolio_performance(
            portfolio_id, period, current_user, db
        )

        # Get benchmark data (this would integrate with market data service)
        # For now, return a placeholder structure
        benchmark_data = {
            "symbol": benchmark_symbol,
            "period": period,
            "return_percent": 0,  # Placeholder - would calculate from market data
            "volatility": 0,  # Placeholder
            "sharpe_ratio": 0,  # Placeholder
        }

        # Calculate relative performance
        portfolio_return = portfolio_performance.get("total_return_percent", 0)
        benchmark_return = benchmark_data["return_percent"]
        relative_performance = portfolio_return - benchmark_return

        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "period": period,
            "portfolio_performance": portfolio_performance,
            "benchmark": benchmark_data,
            "comparison": {
                "relative_performance": round(relative_performance, 2),
                "outperformed": relative_performance > 0,
                "performance_gap": round(abs(relative_performance), 2),
            },
            "calculated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating benchmark comparison: {str(e)}",
        )


@router.get("/reports/daily/{portfolio_id}")
async def get_daily_portfolio_report(
    portfolio_id: int,
    date: str = Query(None, description="Report date (YYYY-MM-DD, default: today)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get daily portfolio report."""
    # Verify portfolio ownership
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
            Portfolio.is_active == True,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found or access denied",
        )

    # Parse date or use today
    if date:
        try:
            report_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD",
            )
    else:
        report_date = datetime.utcnow().date()

    # Get portfolio assets
    assets = (
        db.query(PortfolioAsset)
        .filter(PortfolioAsset.portfolio_id == portfolio_id)
        .all()
    )

    if not assets:
        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "report_date": report_date.isoformat(),
            "message": "No assets in portfolio",
        }

    # Calculate daily metrics
    total_value = sum(
        float(asset.current_value or asset.cost_basis_total) for asset in assets
    )
    total_cost_basis = sum(float(asset.cost_basis_total) for asset in assets)
    total_return = total_value - total_cost_basis
    total_return_percent = (
        (total_return / total_cost_basis * 100) if total_cost_basis > 0 else 0
    )

    # Get daily transactions
    start_of_day = datetime.combine(report_date, datetime.min.time())
    end_of_day = datetime.combine(report_date, datetime.max.time())

    daily_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.portfolio_id == portfolio_id,
            Transaction.transaction_date >= start_of_day,
            Transaction.transaction_date <= end_of_day,
        )
        .all()
    )

    # Calculate daily activity
    daily_buy_value = sum(
        float(t.quantity * t.price)
        for t in daily_transactions
        if t.transaction_type == "buy"
    )
    daily_sell_value = sum(
        float(t.quantity * t.price)
        for t in daily_transactions
        if t.transaction_type == "sell"
    )
    daily_dividends = sum(
        float(t.quantity * t.price)
        for t in daily_transactions
        if t.transaction_type == "dividend"
    )

    return {
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio.name,
        "report_date": report_date.isoformat(),
        "summary": {
            "total_value": round(total_value, 2),
            "total_cost_basis": round(total_cost_basis, 2),
            "total_return": round(total_return, 2),
            "total_return_percent": round(total_return_percent, 2),
            "asset_count": len(assets),
        },
        "daily_activity": {
            "transactions_count": len(daily_transactions),
            "buy_value": round(daily_buy_value, 2),
            "sell_value": round(daily_sell_value, 2),
            "dividends": round(daily_dividends, 2),
            "net_flow": round(daily_buy_value - daily_sell_value, 2),
        },
        "assets": [
            {
                "asset_id": asset.asset_id,
                "symbol": getattr(asset.asset, "symbol", "Unknown"),
                "quantity": float(asset.quantity),
                "current_value": round(
                    float(asset.current_value or asset.cost_basis_total), 2
                ),
                "return": round(
                    float(asset.current_value or asset.cost_basis_total)
                    - float(asset.cost_basis_total),
                    2,
                ),
            }
            for asset in assets
        ],
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/reports/summary")
async def get_user_portfolios_summary(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get summary of all user portfolios."""
    # Get user's portfolios
    portfolios = (
        db.query(Portfolio)
        .filter(Portfolio.user_id == current_user.id, Portfolio.is_active == True)
        .all()
    )

    if not portfolios:
        return {
            "user_id": current_user.id,
            "username": current_user.username,
            "total_portfolios": 0,
            "message": "No portfolios found",
        }

    # Calculate summary metrics
    total_portfolios = len(portfolios)
    total_assets = 0
    total_value = 0
    total_cost_basis = 0

    portfolio_summaries = []

    for portfolio in portfolios:
        assets = (
            db.query(PortfolioAsset)
            .filter(PortfolioAsset.portfolio_id == portfolio.id)
            .all()
        )

        portfolio_value = sum(
            float(asset.current_value or asset.cost_basis_total) for asset in assets
        )
        portfolio_cost_basis = sum(float(asset.cost_basis_total) for asset in assets)
        portfolio_return = portfolio_value - portfolio_cost_basis
        portfolio_return_percent = (
            (portfolio_return / portfolio_cost_basis * 100)
            if portfolio_cost_basis > 0
            else 0
        )

        total_assets += len(assets)
        total_value += portfolio_value
        total_cost_basis += portfolio_cost_basis

        portfolio_summaries.append(
            {
                "portfolio_id": portfolio.id,
                "name": portfolio.name,
                "asset_count": len(assets),
                "value": round(portfolio_value, 2),
                "return": round(portfolio_return, 2),
                "return_percent": round(portfolio_return_percent, 2),
            }
        )

    total_return = total_value - total_cost_basis
    total_return_percent = (
        (total_return / total_cost_basis * 100) if total_cost_basis > 0 else 0
    )

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "summary": {
            "total_portfolios": total_portfolios,
            "total_assets": total_assets,
            "total_value": round(total_value, 2),
            "total_cost_basis": round(total_cost_basis, 2),
            "total_return": round(total_return, 2),
            "total_return_percent": round(total_return_percent, 2),
        },
        "portfolios": portfolio_summaries,
        "generated_at": datetime.utcnow().isoformat(),
    }
