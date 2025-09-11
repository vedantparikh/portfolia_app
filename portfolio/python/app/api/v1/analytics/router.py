"""
Portfolio Analytics Router
Comprehensive API endpoints for portfolio analysis, risk management, and performance tracking.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth.dependencies import get_current_active_user
from app.core.database.connection import get_db
from app.core.database.models import Portfolio, User
from app.core.database.models.portfolio_analytics import (
    AssetCorrelation,
    AssetPerformanceMetrics,
    PortfolioAllocation,
    PortfolioBenchmark,
    PortfolioPerformanceHistory,
    PortfolioRiskMetrics,
    RebalancingEvent,
)
from app.core.schemas.portfolio_analytics import (
    AllocationAnalysisResponse,
    AssetMetricsResponse,
    PerformanceComparisonResponse,
    PerformanceSnapshotResponse,
    PortfolioAllocationCreate,
    PortfolioAnalyticsSummary,
    PortfolioBenchmarkCreate,
    PortfolioRebalancingRecommendation,
    RebalancingEventCreate,
    RiskCalculationResponse,
)
from app.core.services.portfolio_analytics_service import PortfolioAnalyticsService

router = APIRouter(prefix="/analytics")


# Portfolio Performance History
@router.post(
    "/portfolios/{portfolio_id}/performance/snapshot",
    response_model=PerformanceSnapshotResponse,
)
async def create_performance_snapshot(
    portfolio_id: int,
    snapshot_date: Optional[datetime] = Query(
        None, description="Snapshot date (defaults to now)"
    ),
    db: Session = Depends(get_db),
):
    """Create a performance snapshot for a portfolio."""
    analytics_service = PortfolioAnalyticsService(db)

    try:
        snapshot = await analytics_service.create_performance_snapshot(
            portfolio_id, snapshot_date
        )
        return snapshot
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/portfolios/{portfolio_id}/performance/history")
async def get_performance_history(
    portfolio_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get portfolio performance history."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Get performance history
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    history = (
        db.query(PortfolioPerformanceHistory)
        .filter(
            PortfolioPerformanceHistory.portfolio_id == portfolio_id,
            PortfolioPerformanceHistory.snapshot_date >= start_date,
        )
        .order_by(PortfolioPerformanceHistory.snapshot_date.desc())
        .all()
    )

    return history


# Asset Performance Metrics
@router.post("/assets/{asset_id}/metrics", response_model=AssetMetricsResponse)
async def calculate_asset_metrics(
    asset_id: int,
    calculation_date: Optional[datetime] = Query(
        None, description="Calculation date (defaults to now)"
    ),
    db: Session = Depends(get_db),
):
    """Calculate comprehensive metrics for an asset."""
    analytics_service = PortfolioAnalyticsService(db)

    try:
        metrics = await analytics_service.calculate_asset_metrics(
            asset_id, calculation_date
        )
        return metrics
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/assets/{asset_id}/metrics")
async def get_asset_metrics(
    asset_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db),
):
    """Get asset performance metrics history."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    metrics = (
        db.query(AssetPerformanceMetrics)
        .filter(
            AssetPerformanceMetrics.asset_id == asset_id,
            AssetPerformanceMetrics.calculation_date >= start_date,
        )
        .order_by(AssetPerformanceMetrics.calculation_date.desc())
        .all()
    )

    return metrics


# Portfolio Allocation Management
@router.post("/portfolios/{portfolio_id}/allocations")
async def set_portfolio_allocations(
    portfolio_id: int,
    allocations: List[PortfolioAllocationCreate],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Set target allocations for a portfolio."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    analytics_service = PortfolioAnalyticsService(db)
    new_allocations = analytics_service.set_portfolio_allocation(
        portfolio_id, allocations
    )

    return new_allocations


@router.get("/portfolios/{portfolio_id}/allocations")
async def get_portfolio_allocations(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get portfolio target allocations."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    allocations = (
        db.query(PortfolioAllocation)
        .filter(
            PortfolioAllocation.portfolio_id == portfolio_id,
            PortfolioAllocation.is_active == True,
        )
        .all()
    )

    return allocations


@router.get(
    "/portfolios/{portfolio_id}/allocations/analysis",
    response_model=AllocationAnalysisResponse,
)
async def analyze_portfolio_allocation(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Analyze portfolio allocation and detect drift."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    analytics_service = PortfolioAnalyticsService(db)
    analysis = await analytics_service.analyze_portfolio_allocation(portfolio_id)

    return analysis


# Portfolio Risk Analysis
@router.post(
    "/portfolios/{portfolio_id}/risk/calculate", response_model=RiskCalculationResponse
)
async def calculate_portfolio_risk(
    portfolio_id: int,
    calculation_date: Optional[datetime] = Query(
        None, description="Calculation date (defaults to now)"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Calculate comprehensive risk metrics for a portfolio."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    analytics_service = PortfolioAnalyticsService(db)

    try:
        risk_metrics = await analytics_service.calculate_portfolio_risk_metrics(
            portfolio_id, calculation_date
        )
        return risk_metrics
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/portfolios/{portfolio_id}/risk")
async def get_portfolio_risk_analysis(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get portfolio risk analysis."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Get latest risk metrics
    latest_risk = (
        db.query(PortfolioRiskMetrics)
        .filter(PortfolioRiskMetrics.portfolio_id == portfolio_id)
        .order_by(PortfolioRiskMetrics.calculation_date.desc())
        .first()
    )

    if not latest_risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No risk metrics found for this portfolio",
        )

    return latest_risk


# Portfolio Benchmarks
@router.post("/portfolios/{portfolio_id}/benchmarks")
async def add_portfolio_benchmark(
    portfolio_id: int,
    benchmark_data: PortfolioBenchmarkCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add a benchmark to a portfolio."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # If this is set as primary, unset other primary benchmarks
    if benchmark_data.is_primary:
        db.query(PortfolioBenchmark).filter(
            PortfolioBenchmark.portfolio_id == portfolio_id
        ).update({"is_primary": False})

    benchmark = PortfolioBenchmark(
        portfolio_id=portfolio_id,
        benchmark_asset_id=benchmark_data.benchmark_asset_id,
        benchmark_name=benchmark_data.benchmark_name,
        benchmark_type=benchmark_data.benchmark_type,
        tracking_error=benchmark_data.tracking_error,
        information_ratio=benchmark_data.information_ratio,
        beta=benchmark_data.beta,
        alpha=benchmark_data.alpha,
        excess_return=benchmark_data.excess_return,
        excess_return_percent=benchmark_data.excess_return_percent,
        is_active=benchmark_data.is_active,
        is_primary=benchmark_data.is_primary,
    )

    db.add(benchmark)
    db.commit()
    db.refresh(benchmark)

    return benchmark


@router.get("/portfolios/{portfolio_id}/benchmarks")
async def get_portfolio_benchmarks(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get portfolio benchmarks."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    benchmarks = (
        db.query(PortfolioBenchmark)
        .filter(
            PortfolioBenchmark.portfolio_id == portfolio_id,
            PortfolioBenchmark.is_active == True,
        )
        .all()
    )

    return benchmarks


# Rebalancing Events
@router.post("/portfolios/{portfolio_id}/rebalancing/events")
async def create_rebalancing_event(
    portfolio_id: int,
    event_data: RebalancingEventCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a rebalancing event for a portfolio."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    event = RebalancingEvent(
        portfolio_id=portfolio_id,
        event_date=event_data.event_date,
        event_type=event_data.event_type,
        trigger_reason=event_data.trigger_reason,
        pre_rebalance_value=event_data.pre_rebalance_value,
        pre_rebalance_allocations=event_data.pre_rebalance_allocations,
        rebalancing_actions=event_data.rebalancing_actions,
        post_rebalance_value=event_data.post_rebalance_value,
        post_rebalance_allocations=event_data.post_rebalance_allocations,
        rebalancing_cost=event_data.rebalancing_cost,
        tax_impact=event_data.tax_impact,
        status=event_data.status,
        execution_notes=event_data.execution_notes,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get("/portfolios/{portfolio_id}/rebalancing/events")
async def get_rebalancing_events(
    portfolio_id: int,
    days: int = Query(90, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get rebalancing events for a portfolio."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    events = (
        db.query(RebalancingEvent)
        .filter(
            RebalancingEvent.portfolio_id == portfolio_id,
            RebalancingEvent.event_date >= start_date,
        )
        .order_by(RebalancingEvent.event_date.desc())
        .all()
    )

    return events


# Comprehensive Analytics
@router.get(
    "/portfolios/{portfolio_id}/summary", response_model=PortfolioAnalyticsSummary
)
async def get_portfolio_analytics_summary(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive portfolio analytics summary."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    analytics_service = PortfolioAnalyticsService(db)

    try:
        summary = await analytics_service.get_portfolio_analytics_summary(portfolio_id)
        return PortfolioAnalyticsSummary(**summary)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get(
    "/portfolios/{portfolio_id}/rebalancing/recommendations",
    response_model=PortfolioRebalancingRecommendation,
)
async def get_rebalancing_recommendations(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get rebalancing recommendations for a portfolio."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    analytics_service = PortfolioAnalyticsService(db)
    recommendation = await analytics_service.get_rebalancing_recommendation(
        portfolio_id
    )

    return PortfolioRebalancingRecommendation(**recommendation)


# Asset Correlations
@router.get("/assets/correlations")
async def get_asset_correlations(
    asset1_id: Optional[int] = Query(None, description="First asset ID"),
    asset2_id: Optional[int] = Query(None, description="Second asset ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db),
):
    """Get asset correlations."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    query = db.query(AssetCorrelation).filter(
        AssetCorrelation.calculation_date >= start_date,
    )

    if asset1_id:
        query = query.filter(AssetCorrelation.asset1_id == asset1_id)
    if asset2_id:
        query = query.filter(AssetCorrelation.asset2_id == asset2_id)

    correlations = query.order_by(AssetCorrelation.calculation_date.desc()).all()

    return correlations


# Performance Comparison
@router.get(
    "/portfolios/{portfolio_id}/performance/comparison",
    response_model=PerformanceComparisonResponse,
)
async def get_portfolio_performance_comparison(
    portfolio_id: int,
    benchmark_id: Optional[int] = Query(None, description="Benchmark asset ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to compare"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get portfolio performance comparison with benchmark."""
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Get portfolio performance history
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    portfolio_history = (
        db.query(PortfolioPerformanceHistory)
        .filter(
            PortfolioPerformanceHistory.portfolio_id == portfolio_id,
            PortfolioPerformanceHistory.snapshot_date >= start_date,
        )
        .order_by(PortfolioPerformanceHistory.snapshot_date)
        .all()
    )

    if not portfolio_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No performance data found"
        )

    # Get benchmark performance if specified
    benchmark_history = None
    if benchmark_id:
        benchmark_history = (
            db.query(AssetPerformanceMetrics)
            .filter(
                AssetPerformanceMetrics.asset_id == benchmark_id,
                AssetPerformanceMetrics.calculation_date >= start_date,
            )
            .order_by(AssetPerformanceMetrics.calculation_date)
            .all()
        )

    # Build comparison data
    comparison_data = {
        "portfolio_id": portfolio_id,
        "period_days": days,
        "start_date": start_date,
        "end_date": end_date,
        "portfolio_performance": [
            {
                "date": snapshot.snapshot_date,
                "total_return": float(snapshot.cumulative_return or 0),
                "volatility": float(snapshot.volatility or 0),
                "sharpe_ratio": float(snapshot.sharpe_ratio or 0),
            }
            for snapshot in portfolio_history
        ],
    }

    if benchmark_history:
        comparison_data["benchmark_performance"] = [
            {
                "date": metric.calculation_date,
                "total_return": float(
                    metric.total_return_1m or 0
                ),  # Using 1-month return as proxy
                "volatility": float(metric.volatility_20d or 0),
            }
            for metric in benchmark_history
        ]

    return comparison_data
