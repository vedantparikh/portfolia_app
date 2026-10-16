# Portfolio performance (series, period metrics)

**Purpose:** how a portfolio performed over an interval relative to the money put in, with returns and risk for that interval.

**State (2026-10-16):** ✅ series, performance, multi-period agree exactly (one `period_summary`). ⚠️ benchmark endpoints use old maths. ❌ `/overview` 500s.

## Backend — `router.py` (mounted at `/api/v1/portfolios/calculations`), `core/services/portfolio_calculation_service.py`
| Endpoint | Behaviour |
|---|---|
| `GET /periods` | Period codes for the Performance Metrics dropdown (3m … inception). `1m` is accepted everywhere but not listed |
| `GET /portfolio/{id}/performance/series?period=` | **Chart source.** `points[]` per trading day: `value`, `invested` (= value at period start + deposits − withdrawals since), `cost_basis` (FIFO); `summary` = `period_summary`; `error` on missing price/oversell |
| `GET|POST /portfolio/{id}/performance?period=` | `metrics`: twr, mwr (both over the period), cagr (annualised TWR, plain TWR under a year), xirr (annual), volatility, max_drawdown; `current_value`. Switches to inception when the portfolio is younger than the period |
| `GET /portfolio/{id}/multi-period?periods=` | The above for several periods; one memoised engine run per request |
| `GET /portfolio/{id}/compare/{symbol}`, `POST /benchmark/performance` | ⚠️ Old benchmark maths (first contribution as base, no opening value, dividends dropped). UI hides it |
| `GET /portfolio/{id}/overview` | ❌ 500 (tuple from `get_current_portfolio_value` passed as float). No UI caller |

Engine path: `get_transactions` (completed) → `get_market_history` (closes + splits via `MarketDataService.get_daily_history`) → `to_trades` → `daily_series` → `period_summary`. Memoised in `_series_cache` per service instance. First call for a portfolio fetches max history per symbol (~1–2 s each, cached 6 h in Redis).

## Frontend
- **Performance Chart** view: `js/src/components/portfolio/PortfolioChart.jsx` — period pills 1M…All, StatCards (Value, Profit, Return TWR, Return money-weighted), `PerformanceSeriesChart` (lightweight-charts: Value area, Invested line, optional Cost basis), Risk card (drawdown, volatility, Sharpe, best/worst day), Money in and out card.
- `ValueVsInvestedChart.jsx` (Holdings Detail) and dashboard sparklines (`period=3m`) read the same series.
- **Performance Metrics** view: `PortfolioPerformanceMetrics.jsx` — `/performance` + `/multi-period`; tiles labelled "this period" / "per year"; MWR-vs-TWR timing insight; benchmark section replaced by a note.
- `portfolioCalculationsAPI` in `services/api.js`.

## Workflow
Portfolio → Performance Chart → pick a period → read profit vs invested and the period's return/risk; Performance Metrics for side-by-side periods.

## Known gaps / planned
- Benchmark comparison (plan 2.7): rebuild as a shadow portfolio — buy/sell a total-return index with the portfolio's own daily flows through `daily_series`, compare `period_summary`s.
- Remove or fix `/overview`; old helpers `_calculate_xirr`, `_get_portfolio_value_at_date`, `get_current_portfolio_value`, `_calculate_benchmark_*` are legacy (benchmark only).
- FX (2.3), dividend tax (2.2) affect inputs.
