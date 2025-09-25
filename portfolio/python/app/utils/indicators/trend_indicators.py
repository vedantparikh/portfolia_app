import polars as pl

from utils.indicators.base import BaseIndicator


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
                .ewm_mean(span=window_fast, min_periods=min_periods_fast)
                .alias("ema_fast"),
                pl.col("close")
                .ewm_mean(span=window_slow, min_periods=min_periods_slow)
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
                .ewm_mean(span=window_sign, min_periods=min_periods_sign)
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
        Average Directional Movement Index (ADX)
        http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_directional_index_adx
        :param window: N -Period.
        :param fillna: if True, fill NaN values.
        :return: DataFrame with ADX indicator fields.
        """
        min_periods = 0 if fillna else window

        # Calculate ADX using polars operations
        # True Range = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
        self.df = self.df.with_columns(
            [
                pl.col("close").shift(1).alias("prev_close"),
            ]
        )

        self.df = self.df.with_columns(
            [
                pl.max_horizontal(
                    pl.col("high") - pl.col("low"),
                    (pl.col("high") - pl.col("prev_close")).abs(),
                    (pl.col("low") - pl.col("prev_close")).abs(),
                ).alias("true_range")
            ]
        )

        # Directional Movement
        self.df = self.df.with_columns(
            [
                (pl.col("high") - pl.col("high").shift(1)).alias("high_diff"),
                (pl.col("low").shift(1) - pl.col("low")).alias("low_diff"),
            ]
        )

        self.df = self.df.with_columns(
            [
                pl.when(pl.col("high_diff") > pl.col("low_diff"))
                .then(
                    pl.when(pl.col("high_diff") > 0)
                    .then(pl.col("high_diff"))
                    .otherwise(0)
                )
                .otherwise(0)
                .alias("plus_dm"),
                pl.when(pl.col("low_diff") > pl.col("high_diff"))
                .then(
                    pl.when(pl.col("low_diff") > 0)
                    .then(pl.col("low_diff"))
                    .otherwise(0)
                )
                .otherwise(0)
                .alias("minus_dm"),
            ]
        )

        # Smooth the values using EMA
        self.df = self.df.with_columns(
            [
                pl.col("true_range")
                .ewm_mean(span=window, min_periods=min_periods)
                .alias("atr"),
                pl.col("plus_dm")
                .ewm_mean(span=window, min_periods=min_periods)
                .alias("plus_di"),
                pl.col("minus_dm")
                .ewm_mean(span=window, min_periods=min_periods)
                .alias("minus_di"),
            ]
        )

        # Calculate DI+ and DI-
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("atr") == 0)
                .then(0.0)
                .otherwise(pl.col("plus_di") / pl.col("atr") * 100)
                .alias("adx_pos"),
                pl.when(pl.col("atr") == 0)
                .then(0.0)
                .otherwise(pl.col("minus_di") / pl.col("atr") * 100)
                .alias("adx_neg"),
            ]
        )

        # Calculate DX and ADX
        self.df = self.df.with_columns(
            [
                pl.when((pl.col("adx_pos") + pl.col("adx_neg")) == 0)
                .then(0.0)
                .otherwise(
                    (pl.col("adx_pos") - pl.col("adx_neg")).abs()
                    / (pl.col("adx_pos") + pl.col("adx_neg"))
                    * 100
                )
                .alias("dx")
            ]
        )

        self.df = self.df.with_columns(
            [pl.col("dx").ewm_mean(span=window, min_periods=min_periods).alias("adx")]
        )

        # Clean up temporary columns
        self.df = self.df.drop(
            [
                "prev_close",
                "true_range",
                "high_diff",
                "low_diff",
                "plus_dm",
                "minus_dm",
                "atr",
                "plus_di",
                "minus_di",
                "dx",
            ]
        )

        if fillna:
            self.df = self.df.with_columns(
                [
                    pl.col("adx").fill_null(strategy="forward"),
                    pl.col("adx_neg").fill_null(strategy="forward"),
                    pl.col("adx_pos").fill_null(strategy="forward"),
                ]
            )

        return self.df

    def aroon_indicator(self, window: int = 25, fillna: bool = False) -> pl.DataFrame:
        """
        Aroon Indicator
        https://www.investopedia.com/terms/a/aroon.asp
        :param window: N -Period.
        :param fillna: if True, fill NaN values.
        :return: DataFrame with Aroon indicator fields.
        """
        # This version correctly calculates the index of the high/low
        # in the rolling window and then calculates the Aroon values.

        # Note: rolling_apply with a lambda is slow in Polars.
        # Newer Polars versions (>= 0.20.10) have `rolling_argmax`
        # and `rolling_argmin` which are much faster.
        self.df = self.df.with_columns(
            [
                pl.col("high")
                .rolling_apply(lambda s: s.arg_max(), window_size=window)
                .alias("idx_high"),
                pl.col("low")
                .rolling_apply(lambda s: s.arg_min(), window_size=window)
                .alias("idx_low"),
            ]
        )

        # Calculate days since high/low.
        # idx_high is the 0-based index in the window.
        # "Days Since High" = (window - 1) - idx_high
        self.df = self.df.with_columns(
            [
                (window - 1 - pl.col("idx_high")).alias("days_since_high"),
                (window - 1 - pl.col("idx_low")).alias("days_since_low"),
            ]
        )

        # Calculate Aroon values
        # Aroon Up = ((N - Days Since High) / N) x 100
        self.df = self.df.with_columns(
            [
                ((window - pl.col("days_since_high")) / window * 100).alias("aroon_up"),
                ((window - pl.col("days_since_low")) / window * 100).alias(
                    "aroon_down"
                ),
            ]
        )

        # Aroon indicator = Aroon Up - Aroon Down
        self.df = self.df.with_columns(
            [(pl.col("aroon_up") - pl.col("aroon_down")).alias("aroon_indicator")]
        )

        # Clean up temporary columns
        self.df = self.df.drop(
            ["idx_high", "idx_low", "days_since_high", "days_since_low"]
        )

        if fillna:
            self.df = self.df.with_columns(
                [
                    pl.col("aroon_up").fill_null(strategy="forward"),
                    pl.col("aroon_down").fill_null(strategy="forward"),
                    pl.col("aroon_indicator").fill_null(strategy="forward"),
                ]
            )

        return self.df

    def psar_indicator(
        self, step: float = 0.02, max_step: float = 0.2, fillna: bool = False
    ) -> pl.DataFrame:
        """
        Parabolic Stop and Reverse (Parabolic SAR)
        https://school.stockcharts.com/doku.php?id=technical_indicators:parabolic_sar

        NOTE: This is a placeholder/stubbed implementation as noted
        in the original code. A real PSAR is an iterative (non-vectorizable)
        calculation that is very complex to implement.

        :param step: Acceleration Factor used to compute the SAR.
        :param max_step: Maximum value allowed for the Acceleration Factor.
        :param fillna:  If True, fill nan values.
        :return: DataFrame with the PSAR indicator fields.
        """

        # Initialize PSAR values
        self.df = self.df.with_columns(
            [
                pl.lit(None, dtype=pl.Float64).alias("psar"),
                pl.lit(None, dtype=pl.Boolean).alias("psar_down"),
                pl.lit(None, dtype=pl.Boolean).alias("psar_down_indicator"),
                pl.lit(None, dtype=pl.Boolean).alias("psar_up"),
                pl.lit(None, dtype=pl.Boolean).alias("psar_up_indicator"),
            ]
        )

        # Since this is a stub, fillna will just forward-fill the nulls
        if fillna:
            self.df = self.df.with_columns(
                [
                    pl.col("psar").fill_null(strategy="forward"),
                    pl.col("psar_down").fill_null(strategy="forward"),
                    pl.col("psar_down_indicator").fill_null(strategy="forward"),
                    pl.col("psar_up").fill_null(strategy="forward"),
                    pl.col("psar_up_indicator").fill_null(strategy="forward"),
                ]
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
        min_periods = 0 if fillna else window

        # Typical Price = (High + Low + Close) / 3
        self.df = self.df.with_columns(
            [
                ((pl.col("high") + pl.col("low") + pl.col("close")) / 3).alias(
                    "typical_price"
                )
            ]
        )

        # Calculate SMA of typical price
        self.df = self.df.with_columns(
            [
                pl.col("typical_price")
                .rolling_mean(window_size=window, min_periods=min_periods)
                .alias("sma_tp")
            ]
        )

        # Calculate mean deviation
        self.df = self.df.with_columns(
            [
                (pl.col("typical_price") - pl.col("sma_tp"))
                .abs()
                .rolling_mean(window_size=window, min_periods=min_periods)
                .alias("mean_deviation")
            ]
        )

        # Calculate CCI
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("mean_deviation") == 0)
                .then(0.0)
                .otherwise(
                    (pl.col("typical_price") - pl.col("sma_tp"))
                    / (constant * pl.col("mean_deviation"))
                )
                .alias("cci")
            ]
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
    return prices.ewm_mean(span=window)


def calculate_bollinger_bands(
    prices: pl.Series, window: int = 20, num_std: float = 2.0
) -> pl.DataFrame:
    """Calculate Bollinger Bands."""
    sma = prices.rolling_mean(window_size=window)
    std = prices.rolling_std(window_size=window)

    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)

    return pl.DataFrame({"upper": upper_band, "middle": sma, "lower": lower_band})
