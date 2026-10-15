from types import SimpleNamespace

import api.v1.watchlist.router as watchlist_router
from core.schemas.watchlist import WatchlistBulkAddRequest


async def test_bulk_add_awaits_each_item(monkeypatch):
    async def fake_add(self, watchlist_id, user_id, item_data):
        return SimpleNamespace(symbol=item_data.symbol)

    monkeypatch.setattr(watchlist_router.WatchlistService, "add_item_to_watchlist", fake_add)

    result = await watchlist_router.bulk_add_items_to_watchlist(
        watchlist_id=1,
        bulk_data=WatchlistBulkAddRequest(symbols=["AAPL", "MSFT"]),
        current_user=SimpleNamespace(id=1),
        db=None,
    )

    assert result.added_items == ["AAPL", "MSFT"]
    assert result.failed == 0
