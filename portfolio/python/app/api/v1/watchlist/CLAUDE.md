# Watchlists

**Purpose:** track symbols outside your portfolios, with the price when added, change since, notes and alert levels.

**State (2026-10-16):** ✅ lists, items, reorder, refresh prices work. ⚠️ alerts never fire; rating/thesis/tags have no UI; `/public` and `/stats` unreachable.

## Backend — `router.py` (prefix `/api/v1/watchlists`), `core/services/watchlist_service.py`
| Endpoint | Behaviour |
|---|---|
| `POST /`, `GET /`, `GET /{id}?include_real_time_data`, `PUT/DELETE /{id}` | Lists (name, colour, public, default). Real-time refresh writes current price/change to the DB |
| `POST /{id}/items`, `POST /{id}/items/bulk`, `PUT/DELETE /{id}/items/{item_id}`, `POST /{id}/reorder` | Items: `added_price` captured on add; notes, `alert_price_high/low/percent`, `personal_rating`, `investment_thesis`, `tags` |
| `GET /public`, `GET /stats` | Declared after `GET /{id}` → shadowed (422). No UI caller |

Models: `Watchlist`, `WatchlistItem`, `WatchlistAlert`, `WatchlistPerformance` (`core/database/models/watchlist.py`).

## Frontend — `js/src/components/watchlist/`
Route `/watchlist` → `Watchlist.jsx` (grid of lists, or one opened list): `WatchlistSidebar`, `WatchlistContent` (table, `min-w-[960px]` scroll on phones), `AddSymbolModal`, `EditSymbolModal`, `Create/EditWatchlistModal`. `watchlistAPI` in `services/api.js`.

## Workflow
Create list → add symbols (search) → see price, change since added, notes → edit alert high/low → reorder → Refresh pulls live prices.

## Known gaps
- Alerts: `_check_price_alerts` only runs from `update_watchlist_item_prices`, which nothing calls. Item-level alert prices are never evaluated, and there is no notification channel.
- `WatchlistPerformance` is written only on add, so there is no history.
- No UI for rating/thesis/tags or browsing public lists. `bulkAddItemsToWatchlist` is unused by the UI.
- Prices are shown with a hard-coded `$`, and `str(e)` appears in several 400s.

## Planned
Batch 4 UI (agreed earlier): show change since added, days held, rating, tags, a thesis tooltip and alert thresholds. A worker evaluates alerts (plan 3.3/6.1) with a notification channel (ntfy/email, to decide). Fix route order for `/public` and `/stats`.
