import numpy as np
import polars as pl
from numpy.lib.stride_tricks import sliding_window_view

from utils.indicators.base import BaseIndicator, true_range, wilder_average


class TrendIndicators(BaseIndicator):
    """Returns a Polars Dataframe with calculated different Trend Indicators."""

    def macd_indicator(
        self,
        window_slow: int = 26,
        window_fast: int = 12,
        window_sign: int = 9,
        fillna: bool = False,
    ) -> pl.DataFrame:
        """
        Moving Average Convergence Divergence (MACD)
        https://school.stockcharts.com/doku.php?id=technical_indicators:moving_average_convergence_divergence_macd
        :param window_slow: N -Period long term.
        :param window_fast: N -Period short term.
        :param window_sign: N -Period to signal.
        :param fillna: if True, fill NaN values.
        :return: DataFrame with the MACD indicator fields.
        """
        min_periods_fast = 0 if fillna else window_fast
        min_periods_slow = 0 if fillna else window_slow
        min_periods_sign = 0 if fillna else window_sign

        # Calculate MACD using polars operations
        # MACD = EMA(fast) - EMA(slow)
        self.df = self.df.with_columns(
            [
                pl.col("close")
                .ewm_mean(span=window_fast, adjust=False, min_samples=min_periods_fast)
                .alias("ema_fast"),
                pl.col("close")
                .ewm_mean(span=window_slow, adjust=False, min_samples=min_periods_slow)
                .alias("ema_slow"),
            ]
        )

        self.df = self.df.with_columns(
            [(pl.col("ema_fast") - pl.col("ema_slow")).alias("macd")]
        )

        # Signal line = EMA of MACD
        self.df = self.df.with_columns(
            [
                pl.col("macd")
                .ewm_mean(span=window_sign, adjust=False, min_samples=min_periods_sign)
                .alias("signal")
            ]
        )

        # Histogram = MACD - Signal
        self.df = self.df.with_columns(
            [(pl.col("macd") - pl.col("signal")).alias("histogram")]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["ema_fast", "ema_slow"])

        if fillna:
            self.df = self.df.with_columns(
                [
                    pl.col("macd").fill_null(strategy="forward"),
                    pl.col("signal").fill_null(strategy="forward"),
                    pl.col("histogram").fill_null(strategy="forward"),
                ]
            )

        return self.df

    def adx_indicator(self, window: int = 14, fillna: bool = False) -> pl.DataFrame:
        """
        Average Directional Index (Wilder)
        https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx
        +DM/-DM and true range from the second bar on, each Wilder-smoothed;
        +DI = 100 × smoothed +DM / smoothed TR (adx_pos), -DI likewise (adx_neg);
        DX = 100 × |+DI − -DI| / (+DI + -DI); ADX = Wilder average of DX.
        """
        high = self.df["high"].to_numpy().astype(float)
        low = self.df["low"].to_numpy().astype(float)
        close = self.df["close"].to_numpy().astype(float)
        n = len(close)
        up = np.diff(high)
        down = -np.diff(low)
        plus_dm = np.where((up > down) & (up > 0), up, 0.0)
        minus_dm = np.where((down > up) & (down > 0), down, 0.0)
        tr = true_range(high, low, close)[1:]

        smoothed_tr = wilder_average(tr, window)
        with np.errstate(divide="ignore", invalid="ignore"):
            plus_di = np.where(
                smoothed_tr > 0,
                100 * wilder_average(plus_dm, window) / smoothed_tr,
                0.0,
            )
            minus_di = np.where(
                smoothed_tr > 0,
                100 * wilder_average(minus_dm, window) / smoothed_tr,
                0.0,
            )
            total = plus_di + minus_di
            dx = np.where(total > 0, 100 * np.abs(plus_di - minus_di) / total, 0.0)
        plus_di[np.isnan(smoothed_tr)] = np.nan
        minus_di[np.isnan(smoothed_tr)] = np.nan
        dx_valid = dx[window - 1 :]
        adx = np.full(n - 1, np.nan)
        adx[window - 1 :] = wilder_average(dx_valid, window)

        pad = np.array([np.nan])
        self.df = self.df.with_columns(
            pl.Series("adx_pos", np.concatenate([pad, plus_di])).fill_nan(None),
            pl.Series("adx_neg", np.concatenate([pad, minus_di])).fill_nan(None),
            pl.Series("adx", np.concatenate([pad, adx])).fill_nan(None),
        )
        if fillna:
            self.df = self.df.with_columns(
                pl.col(c).fill_null(strategy="forward")
                for c in ("adx", "adx_pos", "adx_neg")
            )
        return self.df

    def aroon_indicator(self, window: int = 25, fillna: bool = False) -> pl.DataFrame:
        """
        Aroon
        https://school.stockcharts.com/doku.php?id=technical_indicators:aroon
        Over the last window + 1 bars: up = 100 × (bars since the start of the
        window to the highest high) / window, down likewise for the lowest low.
        """
        high = self.df["high"].to_numpy().astype(float)
        low = self.df["low"].to_numpy().astype(float)
        n = len(high)
        up = np.full(n, np.nan)
        down = np.full(n, np.nan)
        if n > window:
            up[window:] = (
                np.argmax(sliding_window_view(high, window + 1), axis=1) / window * 100
            )
            down[window:] = (
                np.argmin(sliding_window_view(low, window + 1), axis=1) / window * 100
            )
        self.df = self.df.with_columns(
            pl.Series("aroon_up", up).fill_nan(None),
            pl.Series("aroon_down", down).fill_nan(None),
        )
        self.df = self.df.with_columns(
            (pl.col("aroon_up") - pl.col("aroon_down")).alias("aroon_indicator")
        )
        if fillna:
            self.df = self.df.with_columns(
                pl.col(c).fill_null(strategy="forward")
                for c in ("aroon_up", "aroon_down", "aroon_indicator")
            )
        return self.df

    def psar_indicator(
        self, step: float = 0.02, max_step: float = 0.2, fillna: bool = False
    ) -> pl.DataFrame:
        """
        Parabolic Stop and Reverse (Wilder)
        https://school.stockcharts.com/doku.php?id=technical_indicators:parabolic_sar
        Starts in an up trend at the first bar's close; the acceleration factor grows
        by `step` at each new extreme up to `max_step` and resets on a reversal. In an
        up trend the SAR never rises above the prior two lows (down trend: never below
        the prior two highs).
        psar_up / psar_down hold the SAR while in an up / down trend (else null);
        *_indicator is 1 on the bar a trend starts.
        """
        high = self.df["high"].to_numpy().astype(float)
        low = self.df["low"].to_numpy().astype(float)
        close = self.df["close"].to_numpy().astype(float)
        n = len(close)
        psar = close.copy()
        psar_up = np.full(n, np.nan)
        psar_down = np.full(n, np.nan)
        up_trend, af = True, step
        extreme_high, extreme_low = (high[0], low[0]) if n else (np.nan, np.nan)
        for i in range(2, n):
            reversal = False
            if up_trend:
                psar[i] = psar[i - 1] + af * (extreme_high - psar[i - 1])
                if low[i] < psar[i]:
                    reversal, psar[i], extreme_low, af = (
                        True,
                        extreme_high,
                        low[i],
                        step,
                    )
                else:
                    if high[i] > extreme_high:
                        extreme_high, af = high[i], min(af + step, max_step)
                    psar[i] = min(psar[i], low[i - 1], low[i - 2])
            else:
                psar[i] = psar[i - 1] - af * (psar[i - 1] - extreme_low)
                if high[i] > psar[i]:
                    reversal, psar[i], extreme_high, af = (
                        True,
                        extreme_low,
                        high[i],
                        step,
                    )
                else:
                    if low[i] < extreme_low:
                        extreme_low, af = low[i], min(af + step, max_step)
                    psar[i] = max(psar[i], high[i - 1], high[i - 2])
            up_trend = up_trend != reversal
            if up_trend:
                psar_up[i] = psar[i]
            else:
                psar_down[i] = psar[i]

        def started(values):
            prev = np.concatenate([[np.nan], values[:-1]])
            return (~np.isnan(values) & np.isnan(prev)).astype(float)

        self.df = self.df.with_columns(
            pl.Series("psar", psar),
            pl.Series("psar_up", psar_up).fill_nan(None),
            pl.Series("psar_down", psar_down).fill_nan(None),
            pl.Series("psar_up_indicator", started(psar_up)),
            pl.Series("psar_down_indicator", started(psar_down)),
        )
        return self.df

    def all_trend_indicators(self) -> pl.DataFrame:
        """
        Applies all trend indicators.
        :return: DataFrame with the all defined trend indicators.
        """
        self.df = self.macd_indicator()
        self.df = self.aroon_indicator()
        self.df = self.adx_indicator()
        self.df = self.psar_indicator()
        self.df = self.cci_indicator()  # Added CCI to the "all" method

        return self.df

    def cci_indicator(
        self, window: int = 20, constant: float = 0.015, fillna: bool = False
    ) -> pl.DataFrame:
        """
        Commodity Channel Index (CCI)
        http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:commodity_channel_index_cci
        :param window:
        :param constant:
        :param fillna:
        :return:
        """
        # Typical Price = (High + Low + Close) / 3
        self.df = self.df.with_columns(
            [
                ((pl.col("high") + pl.col("low") + pl.col("close")) / 3).alias(
                    "typical_price"
                )
            ]
        )

        # CCI = (TP - SMA(TP)) / (constant × mean absolute deviation of TP from that SMA)
        tp = self.df["typical_price"].to_numpy().astype(float)
        sma = np.full(len(tp), np.nan)
        mad = np.full(len(tp), np.nan)
        if len(tp) >= window:
            windows = sliding_window_view(tp, window)
            means = windows.mean(axis=1)
            sma[window - 1 :] = means
            mad[window - 1 :] = np.abs(windows - means[:, None]).mean(axis=1)
        self.df = self.df.with_columns(
            pl.Series("sma_tp", sma).fill_nan(None),
            pl.Series("mean_deviation", mad).fill_nan(None),
        )
        self.df = self.df.with_columns(
            pl.when(pl.col("mean_deviation") == 0)
            .then(0.0)
            .otherwise(
                (pl.col("typical_price") - pl.col("sma_tp"))
                / (constant * pl.col("mean_deviation"))
            )
            .alias("cci")
        )

        # Clean up temporary columns
        self.df = self.df.drop(["typical_price", "sma_tp", "mean_deviation"])

        if fillna:
            self.df = self.df.with_columns(
                [pl.col("cci").fill_null(strategy="forward")]
            )

        return self.df


# Convenience functions (These were already correct and needed no changes)
def calculate_sma(prices: pl.Series, window: int = 20) -> pl.Series:
    """Calculate Simple Moving Average (SMA)."""
    return prices.rolling_mean(window_size=window)


def calculate_ema(prices: pl.Series, window: int = 20) -> pl.Series:
    """Calculate Exponential Moving Average (EMA)."""
    return prices.ewm_mean(span=window, adjust=False)
