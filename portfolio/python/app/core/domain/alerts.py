"""
Watchlist price alerts: which of an item's thresholds hold at a price.

An item can set a high price (fires at or above it), a low price (at or below)
and a percent move since it was added (fires when |change| reaches it). Whether
an alert *notifies* is decided by the caller: once when its condition becomes
true, again only after it has been false (see WatchlistService).
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

PRICE_HIGH = "price_high"
PRICE_LOW = "price_low"
PERCENT_CHANGE = "percent_change"


@dataclass(frozen=True)
class AlertCheck:
    alert_type: str
    threshold: Decimal
    condition: str  # "above" or "below"
    holds: bool


def check_alerts(
    price: Decimal,
    added_price: Optional[Decimal],
    high: Optional[Decimal],
    low: Optional[Decimal],
    percent: Optional[Decimal],
) -> List[AlertCheck]:
    """One check per threshold that is set."""
    checks = []
    if high is not None:
        checks.append(AlertCheck(PRICE_HIGH, high, "above", price >= high))
    if low is not None:
        checks.append(AlertCheck(PRICE_LOW, low, "below", price <= low))
    if percent is not None and percent > 0 and added_price:
        change = (price - added_price) / added_price * 100
        checks.append(
            AlertCheck(
                PERCENT_CHANGE,
                percent,
                "above" if change >= 0 else "below",
                abs(change) >= percent,
            )
        )
    return checks
