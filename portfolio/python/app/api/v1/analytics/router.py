"""
Portfolio Analytics Router
Comprehensive API endpoints for portfolio analysis, risk management, and performance.
"""

from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from sqlalchemy.orm import Session

from app.core.auth.dependencies import get_current_active_user
from app.core.database.connection import get_db
from app.core.database.models import Portfolio
from app.core.database.models import User
from app.core.database.models.portfolio_analytics import AssetCorrelation
from app.core.database.models.portfolio_analytics import AssetPerformanceMetrics
from app.core.database.models.portfolio_analytics import PortfolioAllocation
from app.core.database.models.portfolio_analytics import PortfolioBenchmark
from app.core.database.models.portfolio_analytics import PortfolioPerformanceHistory
from app.core.database.models.portfolio_analytics import RebalancingEvent
from app.core.schemas.portfolio_analytics import AllocationAnalysisResponse
from app.core.schemas.portfolio_analytics import AssetCorrelationResponse
from app.core.schemas.portfolio_analytics import AssetMetricsHistoryResponse
from app.core.schemas.portfolio_analytics import AssetMetricsResponse
from app.core.schemas.portfolio_analytics import DeleteResponse
from app.core.schemas.portfolio_analytics import PerformanceComparisonResponse
from app.core.schemas.portfolio_analytics import PerformanceSnapshotResponse
from app.core.schemas.portfolio_analytics import PortfolioAllocationCreate
from app.core.schemas.portfolio_analytics import PortfolioAllocationResponse
from app.core.schemas.portfolio_analytics import PortfolioAnalyticsSummary
from app.core.schemas.portfolio_analytics import PortfolioBenchmarkCreate
from app.core.schemas.portfolio_analytics import PortfolioBenchmarkResponse
from app.core.schemas.portfolio_analytics import PortfolioPerformanceHistoryResponse
from app.core.schemas.portfolio_analytics import PortfolioRebalancingRecommendation
from app.core.schemas.portfolio_analytics import RebalancingEventCreate
from app.core.schemas.portfolio_analytics import RebalancingEventResponse
from app.core.schemas.portfolio_analytics import RiskCalculationResponse
from app.core.schemas.portfolio_analytics import UserAssetsResponse
from app.core.schemas.portfolio_analytics import UserDashboardResponse
from app.core.services.portfolio_analytics_service import PortfolioAnalyticsService

router = APIRouter(prefix="/analytics")


# Portfolio Performance History
@router.get(
    "/portfolios/{portfolio_id}/performance/snapshot",
    response_model=PerformanceSnapshotResponse,
)
async def get_performance_snapshot(
    portfolio_id: int,
    force_refresh: bool = Query(False, description="Force refresh from yfinance"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get portfolio performance snapshot, auto-refreshing with yfinance if stale."""
    # Verify portfolio ownership
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
            Portfolio.is_active,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    analytics_service = PortfolioAnalyticsService(db)

    try:
        snapshot = await analytics_service.get_or_create_performance_snapshot(
            portfolio_id, force_refresh
        )
        return snapshot
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.delete(
    "/portfolios/{portfolio_id}/performance/{snapshot_id}",
    response_model=DeleteResponse,
)
async def delete_performance_snapshot(
    portfolio_id: int,
    snapshot_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a performance snapshot."""
    # Verify portfolio ownership
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
            Portfolio.is_active,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Find and delete the snapshot
    snapshot = (
        db.query(PortfolioPerformanceHistory)
        .filter(
            PortfolioPerformanceHistory.id == snapshot_id,
            PortfolioPerformanceHistory.portfolio_id == portfolio_id,
        )
        .first()
    )

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Snapshot not found"
        )

    db.delete(snapshot)
    db.commit()

    return {"message": "Performance snapshot deleted successfully"}


@router.get(
    "/portfolios/{portfolio_id}/performance/history",
    response_model=PortfolioPerformanceHistoryResponse,
)
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
            Portfolio.is_active,
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

    return PortfolioPerformanceHistoryResponse(
        portfolio_id=portfolio_id, total_records=len(history), history=history
    )


# Asset Performance Metrics
@router.get("/assets/{asset_id}/metrics", response_model=AssetMetricsResponse)
async def get_asset_metrics(
    asset_id: int,
    force_refresh: bool = Query(False, description="Force refresh from yfinance"),
    db: Session = Depends(get_db),
):
    """Get asset metrics, automatically refreshing with yfinance if stale."""
    analytics_service = PortfolioAnalyticsService(db)

    try:
        metrics = await analytics_service.get_or_calculate_asset_metrics(
            asset_id, force_refresh
        )
        return metrics
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get(
    "/assets/{asset_id}/metrics/history", response_model=AssetMetricsHistoryResponse
)
async def get_asset_metrics_history(
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

    # Convert to response schemas
    metrics_responses = [
        AssetMetricsResponse(
            id=metric.id,
            asset_id=metric.asset_id,
            calculation_date=metric.calculation_date,
            current_price=metric.current_price,
            price_change=metric.price_change,
            price_change_percent=metric.price_change_percent,
            sma_20=metric.sma_20,
            sma_50=metric.sma_50,
            sma_200=metric.sma_200,
            ema_12=metric.ema_12,
            ema_26=metric.ema_26,
            rsi=metric.rsi,
            macd=metric.macd,
            macd_signal=metric.macd_signal,
            macd_histogram=metric.macd_histogram,
            stochastic_k=metric.stochastic_k,
            stochastic_d=metric.stochastic_d,
            bollinger_upper=metric.bollinger_upper,
            bollinger_middle=metric.bollinger_middle,
            bollinger_lower=metric.bollinger_lower,
            atr=metric.atr,
            volume_sma=metric.volume_sma,
            volume_ratio=metric.volume_ratio,
            obv=metric.obv,
            volatility_20d=metric.volatility_20d,
            volatility_60d=metric.volatility_60d,
            volatility_252d=metric.volatility_252d,
            beta=metric.beta,
            sharpe_ratio=metric.sharpe_ratio,
            total_return_1m=metric.total_return_1m,
            total_return_3m=metric.total_return_3m,
            total_return_1y=metric.total_return_1y,
            created_at=metric.created_at,
        )
        for metric in metrics
    ]

    return AssetMetricsHistoryResponse(
        asset_id=asset_id, total_records=len(metrics), metrics=metrics_responses
    )


# Portfolio Allocation Management
@router.post(
    "/portfolios/{portfolio_id}/allocations",
    response_model=List[PortfolioAllocationResponse],
)
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
            Portfolio.is_active,
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


@router.get(
    "/portfolios/{portfolio_id}/allocations",
    response_model=List[PortfolioAllocationResponse],
)
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
            Portfolio.is_active,
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
            PortfolioAllocation.is_active,
        )
        .all()
    )

    return allocations


@router.put(
    "/portfolios/{portfolio_id}/allocations/{allocation_id}",
    response_model=PortfolioAllocationResponse,
)
async def update_portfolio_allocation(
    portfolio_id: int,
    allocation_id: int,
    allocation_data: PortfolioAllocationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a specific portfolio allocation."""
    # Verify portfolio ownership
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
            Portfolio.is_active,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Find the allocation
    allocation = (
        db.query(PortfolioAllocation)
        .filter(
            PortfolioAllocation.id == allocation_id,
            PortfolioAllocation.portfolio_id == portfolio_id,
        )
        .first()
    )

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Allocation not found"
        )

    # Update allocation fields
    allocation.target_percentage = allocation_data.target_percentage
    allocation.min_percentage = allocation_data.min_percentage
    allocation.max_percentage = allocation_data.max_percentage
    allocation.rebalance_threshold = allocation_data.rebalance_threshold
    allocation.rebalance_frequency = allocation_data.rebalance_frequency
    allocation.is_active = allocation_data.is_active

    db.commit()
    db.refresh(allocation)

    return allocation


@router.delete(
    "/portfolios/{portfolio_id}/allocations/{allocation_id}",
    response_model=DeleteResponse,
)
async def delete_portfolio_allocation(
    portfolio_id: int,
    allocation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a portfolio allocation."""
    # Verify portfolio ownership
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
            Portfolio.is_active,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Find and delete the allocation
    allocation = (
        db.query(PortfolioAllocation)
        .filter(
            PortfolioAllocation.id == allocation_id,
            PortfolioAllocation.portfolio_id == portfolio_id,
        )
        .first()
    )

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Allocation not found"
        )

    db.delete(allocation)
    db.commit()

    return {"message": "Portfolio allocation deleted successfully"}


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
            Portfolio.is_active,
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
@router.get("/portfolios/{portfolio_id}/risk", response_model=RiskCalculationResponse)
async def get_portfolio_risk_metrics(
    portfolio_id: int,
    force_refresh: bool = Query(False, description="Force refresh from yfinance"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get portfolio risk metrics, auto-refreshing with yfinance if stale."""
    # Verify portfolio ownership
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
            Portfolio.is_active,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    analytics_service = PortfolioAnalyticsService(db)

    try:
        risk_metrics = await analytics_service.get_or_calculate_portfolio_risk_metrics(
            portfolio_id, force_refresh
        )
        return risk_metrics
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


# Portfolio Benchmarks
@router.post(
    "/portfolios/{portfolio_id}/benchmarks", response_model=PortfolioBenchmarkResponse
)
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
            Portfolio.is_active,
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


@router.get(
    "/portfolios/{portfolio_id}/benchmarks",
    response_model=List[PortfolioBenchmarkResponse],
)
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
            Portfolio.is_active,
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
            PortfolioBenchmark.is_active,
        )
        .all()
    )

    return benchmarks


# Rebalancing Events
@router.post(
    "/portfolios/{portfolio_id}/rebalancing/events",
    response_model=RebalancingEventResponse,
)
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
            Portfolio.is_active,
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


@router.get(
    "/portfolios/{portfolio_id}/rebalancing/events",
    response_model=List[RebalancingEventResponse],
)
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
            Portfolio.is_active,
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
            Portfolio.is_active,
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
            Portfolio.is_active,
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
@router.get("/assets/correlations", response_model=List[AssetCorrelationResponse])
async def get_asset_correlations(
    asset1_id: Optional[int] = Query(None, description="First asset ID"),
    asset2_id: Optional[int] = Query(None, description="Second asset ID"),
    force_refresh: bool = Query(False, description="Force refresh from yfinance"),
    db: Session = Depends(get_db),
):
    """Get asset correlations, auto-refreshing with yfinance if stale."""
    analytics_service = PortfolioAnalyticsService(db)

    if asset1_id and asset2_id:
        # Get specific correlation between two assets
        try:
            correlation = await analytics_service.get_or_calculate_asset_correlation(
                asset1_id, asset2_id, force_refresh
            )
            return [correlation]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            ) from e
    else:
        # Get historical correlations
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

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
            Portfolio.is_active,
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


# User Analytics Dashboard
@router.get("/users/dashboard", response_model=UserDashboardResponse)
async def get_user_analytics_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive analytics dashboard for the current user."""
    analytics_service = PortfolioAnalyticsService(db)

    try:
        dashboard_data = await analytics_service.get_analytics_dashboard_summary(
            current_user.id
        )
        return dashboard_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics dashboard: {str(e)}",
        ) from e


@router.get("/users/assets", response_model=UserAssetsResponse)
async def get_user_assets_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get analytics for all user assets (including standalone assets)."""
    analytics_service = PortfolioAnalyticsService(db)

    try:
        assets_data = await analytics_service.get_user_assets_for_analytics(
            current_user.id
        )
        return {
            "user_id": current_user.id,
            "total_assets": len(assets_data),
            "assets": assets_data,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user assets analytics: {str(e)}",
        ) from e
