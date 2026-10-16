from typing import Any, Dict, Optional

from core.database.models import Asset
from core.database.models.asset import AssetType


def asset_from_ticker_info(
    symbol: str, ticker_data: Dict[str, Any], user_id: int, isin: Optional[str] = None
) -> Asset:
    """A new (unsaved) asset for `symbol` from MarketDataService.get_ticker_info."""
    quote_type = (ticker_data.get("quote_type") or "").upper()
    return Asset(
        symbol=symbol,
        name=ticker_data.get("long_name") or ticker_data.get("short_name") or symbol,
        asset_type=AssetType.__members__.get(quote_type, AssetType.OTHER),
        currency=ticker_data.get("currency") or "USD",
        exchange=ticker_data.get("exchange"),
        isin=isin or ticker_data.get("isin"),
        cusip=ticker_data.get("cusip"),
        sector=ticker_data.get("sector"),
        industry=ticker_data.get("industry"),
        country=ticker_data.get("country"),
        description=ticker_data.get("long_business_summary"),
        user_id=user_id,
        is_active=True,
    )
