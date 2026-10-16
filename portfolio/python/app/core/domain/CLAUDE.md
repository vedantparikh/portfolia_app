# Calculation engine (`core/domain`)

**Purpose:** the only place portfolio maths is defined. Pure functions; no DB, no network, no FastAPI. Every number the app shows about positions, value history, returns or risk comes from here.

**State (2026-10-16):** ✅ in production use. Golden tests in `tests/unit/test_domain_engine.py`; an independent replay of the demo data (real Yahoo prices, splits, dividends) matched `daily_series` to the cent on every day and XIRR to 3 decimals.

## Modules
| File | What | Key rules |
|---|---|---|
| `positions.py` | `to_trades`, `split_factor`, `Lots`, `compute_position`, `day_change`, `OversellError` | Only COMPLETED (or status-less) transactions. Order: date, BUY before SELL, id. Trades are converted to **today's share units** (qty × later split ratios, price ÷ same) because Yahoo closes are split-adjusted back in time. FIFO lots; cost = `total_amount` (fees+taxes in), sells realise `total_amount − FIFO cost`. Oversell raises. |
| `valuation.py` | `daily_series(trades, closes, end, symbols)`, `MissingPriceError` | Calendar = trading days present in the price data, from first trade to `end`. Weekend trades count on the next trading day. Prices forward-filled; a held asset with **no** price raises (never valued at cost). Columns: value, cost_basis (FIFO, fees), net_invested (cum. inflow−outflow), inflow (buys), outflow (sale proceeds + dividends), realized_pnl, dividends. |
| `returns.py` | `compute_daily_returns`, `twr_pct`, `annualize_pct`, `deannualize_pct`, `xirr_pct`, `volatility_pct`, `sharpe_ratio`, `max_drawdown_pct`, `split_period`, `period_summary`, `RISK_FREE_RATE`, `TRADING_DAYS_PER_YEAR` | Daily return r = (V_t + out_t)/(V_{t−1} + in_t) − 1 (buys at start of day, outflows at end). Percent units. Annualise only for ≥360 days. XIRR via pyxirr with the opening value as a flow the day before the period. Drawdown counts a fall from the period start. One risk-free rate (3%). |

`period_summary(series, start)` → start/end date and value, deposits, withdrawals, net_contributions, profit (= end − start − net), twr_pct, twr_annualized_pct, mwr_pct (period), mwr_annualized_pct (XIRR), volatility_pct, sharpe_ratio, max_drawdown_pct, best_day, worst_day.

## Who calls it
- `PortfolioCalculationService.get_portfolio_series` (memoised per request) → `/portfolios/calculations/.../performance`, `/performance/series`, `/multi-period`, analytics `/performance/history`, `/risk`, `/advance-risk` (via `get_portfolio_history`).
- `PortfolioService.recalculate_asset_state` → `compute_position` (cached `PortfolioAsset`), `_holding_rows` → `day_change`.
- Prices: `MarketDataService.get_daily_history` (split-adjusted, not dividend-adjusted closes + split/dividend events; Redis 6h).

## Rules for changes
- Add a golden test with a hand calculation **first**; keep `test_calculation_snapshots.py` green (regenerate only for intended changes, explained in the commit).
- Never re-implement a metric elsewhere (services, routers, frontend). Extend this package.
- Dividends are income only via DIVIDEND transactions (prices are not dividend-adjusted). SPLIT/TRANSFER transaction types are ignored; splits come from market data.

## Planned (REFACTOR_PLAN Phase 2)
- 2.1 TRANSFER_IN/OUT lots, schema validation per type · 2.2 dividend withholding tax (net cash) · 2.3 FX: convert to portfolio currency at each date · 2.5 stale-price flags after N days of forward fill · 2.7 benchmark shadow portfolio built on `daily_series` with the portfolio's own flows · hypothesis property tests (TWR invariant to deposits, qty ≥ 0).
