"""
Benchmark as a shadow portfolio: the portfolio's own cash flows, invested in a
benchmark instead.

Money that went into the portfolio on a day buys benchmark units at the previous
close, and money that came out (sale proceeds, dividends) sells units at that
day's close — the same timing `compute_daily_returns` assumes. The shadow's
time-weighted return is therefore exactly the benchmark's price return, and its
money-weighted return and profit differ from the portfolio's only through what
was held. Use a total-return series (an accumulating ETF or a TR index) so
reinvested dividends are in the price.
"""

from datetime import date
from typing import Optional

import pandas as pd

from core.domain.returns import split_period
from core.domain.valuation import MissingPriceError, _day_index


def shadow_series(
    series: pd.DataFrame, closes: pd.Series, start: Optional[date]
) -> pd.DataFrame:
    """
    Daily `value`, `inflow`, `outflow` and cumulative `shortfall` of the shadow over
    the period of `series` (a `daily_series` result) that begins at `start`.

    For a period after inception the shadow starts with the portfolio's value just
    before it, bought at that day's close, and the frame includes that day so
    `period_summary(shadow, start)` sees the same opening value. A withdrawal larger
    than the shadow is paid out as far as it goes; the rest is `shortfall`.
    """
    window, opening_value, _ = split_period(series, start)
    prices = (
        pd.Series(closes.values, index=_day_index(closes.index)).dropna().sort_index()
    )
    prices = prices[~prices.index.duplicated(keep="last")]
    before = prices[prices.index < window.index[0]]
    if before.empty:
        raise MissingPriceError(
            f"The benchmark has no price before {window.index[0]:%Y-%m-%d}"
        )
    on_days = (
        prices.reindex(prices.index.union(window.index)).ffill().reindex(window.index)
    )
    previous = on_days.shift(1)
    previous.iloc[0] = before.iloc[-1]

    units = opening_value / previous.iloc[0]
    shortfall = 0.0
    rows = []
    if opening_value:
        opening_day = series.index[series.index < window.index[0]][-1]
        rows.append((opening_day, opening_value, 0.0, 0.0, 0.0))
    for day, row in window.iterrows():
        units += row["inflow"] / previous[day]
        held = units * on_days[day]
        paid = min(row["outflow"], held)
        units -= paid / on_days[day]
        shortfall += row["outflow"] - paid
        rows.append((day, units * on_days[day], row["inflow"], paid, shortfall))

    return pd.DataFrame(
        rows, columns=["date", "value", "inflow", "outflow", "shortfall"]
    ).set_index("date")
