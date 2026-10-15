"""
Asset Search Service
Advanced asset search and discovery service with filtering and ranking.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from core.database.models import Asset


class AssetSearchService:
    """Service for advanced asset search and discovery."""

    def __init__(self, db: Session):
        self.db = db

    def get_asset_details(self, asset_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed asset information."""
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()

        if not asset:
            return None

        return {
            "id": asset.id,
            "symbol": asset.symbol,
            "name": asset.name,
            "asset_type": asset.asset_type.value,
            "currency": asset.currency,
            "exchange": asset.exchange,
            "isin": asset.isin,
            "cusip": asset.cusip,
            "sector": asset.sector,
            "industry": asset.industry,
            "country": asset.country,
            "description": asset.description,
            "is_active": asset.is_active,
            "created_at": asset.created_at,
            "updated_at": asset.updated_at,
        }

    def get_popular_assets(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get popular assets based on portfolio holdings."""
        # Count how many portfolios hold each asset
        popular_assets = (
            self.db.query(
                Asset.id,
                Asset.symbol,
                Asset.name,
                Asset.asset_type,
                Asset.sector,
                func.count().label("portfolio_count"),
            )
            .join(Asset.portfolio_holdings)
            .group_by(
                Asset.id, Asset.symbol, Asset.name, Asset.asset_type, Asset.sector
            )
            .order_by(desc("portfolio_count"))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": asset.id,
                "symbol": asset.symbol,
                "name": asset.name,
                "asset_type": asset.asset_type.value,
                "sector": asset.sector,
                "portfolio_count": asset.portfolio_count,
            }
            for asset in popular_assets
        ]

    def get_sector_breakdown(self) -> List[Dict[str, Any]]:
        """Get asset breakdown by sector."""
        sector_data = (
            self.db.query(
                Asset.sector,
                func.count(Asset.id).label("asset_count"),
                func.count(Asset.portfolio_holdings).label("portfolio_count"),
            )
            .outerjoin(Asset.portfolio_holdings)
            .filter(Asset.is_active == True, Asset.sector.isnot(None))
            .group_by(Asset.sector)
            .order_by(desc("asset_count"))
            .all()
        )

        return [
            {
                "sector": sector.sector,
                "asset_count": sector.asset_count,
                "portfolio_count": sector.portfolio_count,
            }
            for sector in sector_data
        ]

    def get_asset_type_breakdown(self) -> List[Dict[str, Any]]:
        """Get asset breakdown by type."""
        type_data = (
            self.db.query(
                Asset.asset_type,
                func.count(Asset.id).label("asset_count"),
                func.count(Asset.portfolio_holdings).label("portfolio_count"),
            )
            .outerjoin(Asset.portfolio_holdings)
            .filter(Asset.is_active == True)
            .group_by(Asset.asset_type)
            .order_by(desc("asset_count"))
            .all()
        )

        return [
            {
                "asset_type": asset_type.asset_type.value,
                "asset_count": asset_type.asset_count,
                "portfolio_count": asset_type.portfolio_count,
            }
            for asset_type in type_data
        ]

    def get_exchange_breakdown(self) -> List[Dict[str, Any]]:
        """Get asset breakdown by exchange."""
        exchange_data = (
            self.db.query(
                Asset.exchange,
                func.count(Asset.id).label("asset_count"),
                func.count(Asset.portfolio_holdings).label("portfolio_count"),
            )
            .outerjoin(Asset.portfolio_holdings)
            .filter(Asset.is_active == True, Asset.exchange.isnot(None))
            .group_by(Asset.exchange)
            .order_by(desc("asset_count"))
            .all()
        )

        return [
            {
                "exchange": exchange.exchange,
                "asset_count": exchange.asset_count,
                "portfolio_count": exchange.portfolio_count,
            }
            for exchange in exchange_data
        ]

    def get_search_suggestions(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get search suggestions based on partial query."""
        if len(query) < 2:
            return []

        suggestions = (
            self.db.query(Asset.symbol, Asset.name, Asset.asset_type)
            .filter(
                and_(
                    Asset.is_active == True,
                    or_(
                        Asset.symbol.ilike(f"{query}%"),
                        Asset.name.ilike(f"{query}%"),
                    ),
                )
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "symbol": suggestion.symbol,
                "name": suggestion.name,
                "asset_type": suggestion.asset_type.value,
            }
            for suggestion in suggestions
        ]
