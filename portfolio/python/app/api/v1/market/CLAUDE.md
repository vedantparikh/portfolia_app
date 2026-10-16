# Market data

**Purpose:** quotes, price history, corporate actions and symbol search from Yahoo (yfinance / yahooquery), cached in Redis. The **only** path to market data (tests mock it, never the network).

**State (2026-10-16):** ✅ works; free Yahoo is slow on cold calls (accepted by the user). ⚠️ two search implementations.

## Service — `core/services/market_data_service.py`
| Method | Use | Cache |
|---|---|---|
| `get_current_prices(symbols)` | Live price (regularMarketPrice → currentPrice → previousClose) for holdings/summary | Redis 60 s |
| `get_yesterdays_closes(symbols)` | Previous close for today's P&L (`yf.download(period="2d")`, first row) | 12 h |
| `get_daily_history(symbol)` | **Valuation source**: closes split-adjusted, *not* dividend-adjusted (`auto_adjust=False`), plus `splits` and `dividends` on ex-dates; naive date index | 6 h |
| `fetch_ticker_data(...)` | OHLCV (dividend-adjusted default) for charts/indicators/benchmark | none |
| `get_ticker_info`, `get_market_status`, `search_symbols` | Info (15 min), US market open (weekdays 9:30–16:00 ET, no holidays), exact-ticker lookup | |

## Endpoints (`market/routers.py`)
- `stock.py` (`/api/v1/stock`):
  - `GET /symbols` — real search via yahooquery; optional auth; anonymous users limited to 10/hour per IP. Used by SymbolSearch and AddSymbolModal.
  - `GET /symbol-data`
  - `GET /stock-latest-data` — used by the transaction modal and ClientSideAssetSearch.
  - `GET /major-indices` — a static list.
- `data_router.py` (`/api/v1/market-data`, auth required):
  - `GET /ticker/{symbol}`, `GET /ticker/{symbol}/info`
  - `GET /prices/bulk` (max 50)
  - `GET /search` — exact-ticker lookup only; no UI caller.
  - `GET /market-status` — Dashboard tile.
  - `GET /supported-periods`, `GET /supported-intervals`
- `marketAPI` in `js/src/services/api.js`.

## Known gaps
- Duplicate search paths (`/stock/symbols` real, `/market-data/search` exact lookup); unused client fns `getMajorIndices`, `getBulkPrices`, `getTickerInfo`, `getTickerData`.
- Market status ignores US holidays; previous close cache can be stale across a weekend morning.
- No backoff/concurrency limit; `str(e)` in several response details.

## Planned
Plan 2.4: `MarketDataProvider` interface (Yahoo first), Redis pipeline cache, concurrency limit + backoff, one search endpoint; 2.3 FX rates (Yahoo `EURUSD=X` or ECB, open decision); 3.3 worker refreshes prices so requests never call Yahoo synchronously.
