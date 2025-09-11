"""
Enhanced Market Data Service
Comprehensive market data service with real-time updates and caching.
"""

import asyncio
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import List

from sqlalchemy.orm import Session

from app.core.database.models import Asset
from app.core.database.models import PortfolioAsset
from app.core.services.market_data_service import market_data_service
from app.core.services.portfolio_analytics_service import PortfolioAnalyticsService


class EnhancedMarketDataService:
    """Enhanced market data service with caching and real-time updates."""

    def __init__(self, db: Session):
        self.db = db
        self.cache = {}  # In production, use Redis
        self.cache_ttl = 300  # 5 minutes

    async def update_all_portfolio_prices(self, portfolio_id: int) -> Dict[str, Any]:
        """Update prices for all assets in a portfolio."""

        portfolio_assets = (
            self.db.query(PortfolioAsset)
            .filter(PortfolioAsset.portfolio_id == portfolio_id)
            .all()
        )

        if not portfolio_assets:
            return {"updated": 0, "errors": []}

        updated_count = 0
        errors = []

        # Update prices for each asset
        for portfolio_asset in portfolio_assets:
            try:
                await self.update_asset_price(portfolio_asset.asset_id)
                updated_count += 1
            except Exception as e:
                errors.append({"asset_id": portfolio_asset.asset_id, "error": str(e)})

        return {
            "updated": updated_count,
            "errors": errors,
            "total_assets": len(portfolio_assets),
        }

    async def update_asset_price(self, asset_id: int) -> Dict[str, Any]:
        """Get current price for a specific asset (no database storage)."""
        # Get asset
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Check cache first
        cache_key = f"price_{asset.symbol}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.utcnow() - cached_data["timestamp"] < timedelta(
                seconds=self.cache_ttl
            ):
                return cached_data["data"]

        try:
            # Get current price from market data service
            current_price = await market_data_service.get_current_price(asset.symbol)

            if current_price is None:
                raise ValueError(f"No price data available for {asset.symbol}")

            # Get additional info for change calculation
            ticker_info = await market_data_service.get_ticker_info(asset.symbol)

            # Calculate change if we have previous close
            change = 0
            change_percent = 0
            if ticker_info and ticker_info.get("previousClose"):
                previous_close = float(ticker_info["previousClose"])
                change = current_price - previous_close
                change_percent = (
                    (change / previous_close) * 100 if previous_close > 0 else 0
                )

            # Cache the result
            result = {
                "asset_id": asset_id,
                "symbol": asset.symbol,
                "price": float(current_price),
                "change": change,
                "change_percent": change_percent,
                "volume": ticker_info.get("volume", 0) if ticker_info else 0,
                "updated_at": datetime.utcnow().isoformat(),
            }

            self.cache[cache_key] = {"data": result, "timestamp": datetime.utcnow()}

            return result

        except Exception as e:
            raise e

    async def update_asset_performance_metrics(self, asset_id: int) -> None:
        """Update performance metrics for an asset."""

        analytics_service = PortfolioAnalyticsService(self.db)

        try:
            await analytics_service.calculate_asset_metrics(asset_id)
        except Exception as e:
            # Log error but don't fail the price update
            print(f"Failed to update performance metrics for asset {asset_id}: {e}")

    async def get_market_summary(self) -> Dict[str, Any]:
        """Get market summary with key indices."""
        # This would integrate with your market data service
        # to get major indices like S&P 500, NASDAQ, etc.

        indices = [
            {"symbol": "SPY", "name": "S&P 500"},
            {"symbol": "QQQ", "name": "NASDAQ 100"},
            {"symbol": "IWM", "name": "Russell 2000"},
            {"symbol": "VTI", "name": "Total Stock Market"},
        ]

        summary = {
            "indices": [],
            "market_status": "open",  # This would be determined by market hours
            "last_updated": datetime.utcnow().isoformat(),
        }

        for index in indices:
            try:
                price_data = await market_data_service.get_current_price(
                    index["symbol"]
                )
                if price_data:
                    summary["indices"].append(
                        {
                            "symbol": index["symbol"],
                            "name": index["name"],
                            "price": float(price_data["close"]),
                            "change": price_data.get("change", 0),
                            "change_percent": price_data.get("change_percent", 0),
                        }
                    )
            except Exception as e:
                print(f"Failed to get data for {index['symbol']}: {e}")

        return summary

    async def get_sector_performance(self) -> List[Dict[str, Any]]:
        """Get sector performance data."""
        # This would typically come from a financial data provider
        # For now, we'll return mock data structure

        sectors = [
            "Technology",
            "Healthcare",
            "Financials",
            "Consumer Discretionary",
            "Industrials",
            "Consumer Staples",
            "Energy",
            "Utilities",
            "Materials",
            "Real Estate",
            "Communication Services",
        ]

        sector_data = []
        for sector in sectors:
            # In a real implementation, this would fetch actual sector ETF data
            sector_data.append(
                {
                    "sector": sector,
                    "performance_1d": 0.0,  # Would be actual data
                    "performance_1w": 0.0,
                    "performance_1m": 0.0,
                    "performance_1y": 0.0,
                    "market_cap": 0.0,
                    "pe_ratio": 0.0,
                }
            )

        return sector_data

    async def get_top_movers(
        self, direction: str = "gainers", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top gaining or losing assets."""
        # This would typically query a financial data provider
        # For now, we'll return a structure for the top movers

        # In a real implementation, this would:
        # 1. Query your asset database for assets with recent price changes
        # 2. Sort by percentage change
        # 3. Return the top N results

        return []

    async def get_price_history(
        self, asset_id: int, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get price history for an asset from yfinance."""
        # Get asset
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return []

        try:
            # Fetch historical data from yfinance
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")

            data = await market_data_service.fetch_ticker_data(
                symbol=asset.symbol,
                start_date=start_str,
                end_date=end_str,
                interval="1d",
            )

            if data is None or data.empty:
                return []

            # Convert to the expected format
            result = []
            for _, row in data.iterrows():
                result.append(
                    {
                        "date": row["Date"].strftime("%Y-%m-%d"),
                        "open": float(row["Open"]),
                        "high": float(row["High"]),
                        "low": float(row["Low"]),
                        "close": float(row["Close"]),
                        "volume": float(row["Volume"]),
                        "adjusted_close": float(row.get("Adj Close", row["Close"])),
                    }
                )

            return result

        except Exception as e:
            print(f"Error getting price history for asset {asset_id}: {e}")
            return []

    async def bulk_update_prices(self, asset_ids: List[int]) -> Dict[str, Any]:
        """Bulk update prices for multiple assets."""
        results = {"updated": 0, "errors": [], "total": len(asset_ids)}

        # Process in batches to avoid overwhelming the API
        batch_size = 10
        for i in range(0, len(asset_ids), batch_size):
            batch = asset_ids[i : i + batch_size]

            # Process batch concurrently
            tasks = [self.update_asset_price(asset_id) for asset_id in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results["errors"].append(
                        {"asset_id": batch[j], "error": str(result)}
                    )
                else:
                    results["updated"] += 1

        return results

    def clear_cache(self, pattern: str = None) -> None:
        """Clear cache entries."""
        if pattern:
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
        else:
            self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.utcnow()
        valid_entries = 0
        expired_entries = 0

        for entry in self.cache.values():
            if now - entry["timestamp"] < timedelta(seconds=self.cache_ttl):
                valid_entries += 1
            else:
                expired_entries += 1

        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_ttl_seconds": self.cache_ttl,
        }
