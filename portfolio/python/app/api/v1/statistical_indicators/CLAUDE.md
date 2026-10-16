# Technical indicators & analysis configurations

**Purpose:** compute technical indicators for a symbol, chart them, and save named indicator sets per user.

**State (2026-10-16):** ⚠️ calculation + charting work; several formulas are non-standard, PSAR is a stub, and selecting a saved configuration does not change the chart.

## Backend — `routers.py` (prefix `/api/v1/statistical-indicators`)
- **Services:** `enhanced_statistical_service.py`, `indicator_registry_service.py`, `analysis_configuration_service.py`. Model: `AnalysisConfiguration` (indicators and chart_settings as JSON, is_public, tags, usage_count).
- **Indicator code:** `python/app/utils/indicators/{momentum,trend,volatility,volume}_indicators.py`, using polars.

| Endpoint | Behaviour |
|---|---|
| `GET /indicators` | Registry, built by introspecting `*_indicator` methods |
| `POST /calculate` | OHLCV plus the requested indicator series |
| `POST/GET /configurations`, `GET/PUT/DELETE /configurations/{id}`, `POST /configurations/{id}/duplicate` | Saved sets (user's own, or public) |
| `GET /templates`, `POST /templates/{name}/create`, `POST /validate`, `GET /statistics`, `GET /popular` | Templates and helpers. No UI for templates, statistics or popular |
| `GET /configurations/search` | **Shadowed** by `/configurations/{id}` (422) |

**Indicators:**
- Momentum: rsi, roc, stoch_rsi, stoch_oscillator.
- Trend: macd, adx, aroon, psar, cci.
- Volatility: bollinger_bands, average_true_range, keltner_channel.
- Volume: mfi, vpt, vwap, obv, force_index.

Strategies in `utils/trading_strategies/{gfs,macd}_strategy.py` are tests only, with no API. The characterisation snapshot pins indicator outputs, so any formula fix must regenerate it, explained in the commit.

## Frontend
No route of its own; it lives inside `/assets`:
- `analytics/AssetAnalyticsView.jsx` draws on `shared/EnhancedChart.jsx` (lightweight-charts v5). Oscillators (rsi, stoch, cci, roc, williams, momentum) go in pane 1 at about 28% of the height, RSI auto-scaled to 0–100; the rest overlay the price.
- `analytics/IndicatorConfigurationManager.jsx` is a modal to create, edit, duplicate and select sets.
- API wrapper: `statisticalIndicatorsAPI` in `services/api.js`.

## Workflow
Assets → select an asset → the analytics view loads RSI and MACD (30 days) → "Analysis Configurations" to manage sets.

## Known gaps
- PSAR returns all-null.
- Smoothing doesn't match the standard (Wilder) definitions: RSI uses `ewm span` instead of Wilder, ATR a plain rolling mean, ADX `ewm span`.
- Bollinger uses sample std (ddof=1). There's a duplicate Bollinger helper in `trend_indicators.py`, and Aroon uses a slow `rolling_map`.
- MACD is drawn on the price scale instead of an oscillator pane.
- The saved-configuration flow is broken in the UI:
  - `AssetAnalyticsView` ignores the `selectedConfiguration`/`chartData` props.
  - It stores `{configurations}` as an array, so the saved list never renders.
  - Its apply button passes objects where indicator names are expected.
  - Its performance metrics are hardcoded to 0.
- Mixed `from app.core…` / `from core…` imports in two services (double-import risk). A failed import only logs a warning and the router silently goes unmounted.

## Planned
Plan 2.9: Wilder RSI/ATR/ADX, population-std Bollinger, CCI and StochRSI formulas, a real PSAR. Wire configuration selection to the chart and fix the imports.
