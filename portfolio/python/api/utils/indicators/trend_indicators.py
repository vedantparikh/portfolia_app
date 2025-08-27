import polars as pl
from .base import BaseIndicator


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
        Is a trend-following momentum indicator that shows the relationship between two moving averages of prices.
        https://school.stockcharts.com/doku.php?id=technical_indicators:moving_average_convergence_divergence_macd
        :param window_slow: N -Period long term.
        :param window_fast: N -Period short term.
        :param window_sign: N -Period to signal.
        :param fillna: if True, fill NaN values.
        :return: DataFrame with the MACD indicator fields.
        """
        # Calculate MACD using polars operations
        # MACD = EMA(fast) - EMA(slow)
        self.df = self.df.with_columns(
            [
                pl.col("Close").ewm_mean(span=window_fast).alias("ema_fast"),
                pl.col("Close").ewm_mean(span=window_slow).alias("ema_slow"),
            ]
        )

        self.df = self.df.with_columns(
            [(pl.col("ema_fast") - pl.col("ema_slow")).alias("MACD")]
        )

        # Signal line = EMA of MACD
        self.df = self.df.with_columns(
            [pl.col("MACD").ewm_mean(span=window_sign).alias("Signal")]
        )

        # Histogram = MACD - Signal
        self.df = self.df.with_columns(
            [(pl.col("MACD") - pl.col("Signal")).alias("Histogram")]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["ema_fast", "ema_slow"])

        if not fillna:
            self.df = self.df.with_columns(
                [
                    pl.col("MACD").fill_null(strategy="forward"),
                    pl.col("Signal").fill_null(strategy="forward"),
                    pl.col("Histogram").fill_null(strategy="forward"),
                ]
            )

        return self.df

    def adx_indicator(self, window: int = 14, fillna: bool = False) -> pl.DataFrame:
        """
        Average Directional Movement Index (ADX)
        The Plus Directional Indicator (+DI) and Minus Directional Indicator (-DI) are derived from smoothed averages of
         these differences, and measure trend direction over time. These two indicators are often referred to
          collectively as the Directional Movement Indicator (DMI).
        The Average Directional Index (ADX) is in turn derived from the smoothed averages of the difference between +DI
        and -DI, and measures the strength of the trend (regardless of direction) over time.
        Using these three indicators together, chartists can determine both the direction and strength of the trend.
        http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:average_directional_index_adx
        :param window: N -Period.
        :param fillna: if True, fill NaN values.
        :return: DataFrame with ADX indicator fields.
        """
        # Calculate ADX using polars operations
        # True Range = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
        self.df = self.df.with_columns(
            [
                pl.col("High").shift(1).alias("prev_high"),
                pl.col("Low").shift(1).alias("prev_low"),
                pl.col("Close").shift(1).alias("prev_close"),
            ]
        )

        self.df = self.df.with_columns(
            [
                pl.max_horizontal(
                    pl.col("High") - pl.col("Low"),
                    (pl.col("High") - pl.col("prev_close")).abs(),
                    (pl.col("Low") - pl.col("prev_close")).abs(),
                ).alias("true_range")
            ]
        )

        # Directional Movement
        self.df = self.df.with_columns(
            [
                (pl.col("High") - pl.col("prev_high")).alias("high_diff"),
                (pl.col("prev_low") - pl.col("Low")).alias("low_diff"),
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
                pl.col("true_range").ewm_mean(span=window).alias("atr"),
                pl.col("plus_dm").ewm_mean(span=window).alias("plus_di"),
                pl.col("minus_dm").ewm_mean(span=window).alias("minus_di"),
            ]
        )

        # Calculate DI+ and DI-
        self.df = self.df.with_columns(
            [
                (pl.col("plus_di") / pl.col("atr") * 100).alias("ADX_pos"),
                (pl.col("minus_di") / pl.col("atr") * 100).alias("ADX_neg"),
            ]
        )

        # Calculate DX and ADX
        self.df = self.df.with_columns(
            [
                (
                    (pl.col("ADX_pos") - pl.col("ADX_neg")).abs()
                    / (pl.col("ADX_pos") + pl.col("ADX_neg"))
                    * 100
                ).alias("dx")
            ]
        )

        self.df = self.df.with_columns(
            [pl.col("dx").ewm_mean(span=window).alias("ADX")]
        )

        # Clean up temporary columns
        self.df = self.df.drop(
            [
                "prev_high",
                "prev_low",
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

        if not fillna:
            self.df = self.df.with_columns(
                [
                    pl.col("ADX").fill_null(strategy="forward"),
                    pl.col("ADX_neg").fill_null(strategy="forward"),
                    pl.col("ADX_pos").fill_null(strategy="forward"),
                ]
            )

        return self.df

    def aroon_indicator(self, window: int = 25, fillna: bool = False) -> pl.DataFrame:
        """
        Aroon Indicator
        Identify when trends are likely to change direction.
        Aroon Up = ((N - Days Since N-day High) / N) x 100 Aroon Down = ((N - Days Since N-day Low) / N) x 100
        Aroon Indicator = Aroon Up - Aroon Down
        https://www.investopedia.com/terms/a/aroon.asp
        :param window: N -Period.
        :param fillna: if True, fill NaN values.
        :return: DataFrame with Aroon indicator fields.
        """
        # Calculate Aroon indicator using polars operations
        # Aroon Up = ((N - Days Since N-day High) / N) * 100
        # Aroon Down = ((N - Days Since N-day Low) / N) * 100

        # Find the highest high and lowest low in the window
        self.df = self.df.with_columns(
            [
                pl.col("High").rolling_max(window_size=window).alias("rolling_high"),
                pl.col("Low").rolling_min(window_size=window).alias("rolling_low"),
            ]
        )

        # Calculate days since high/low
        self.df = self.df.with_columns(
            [
                pl.col("High")
                .rolling_apply(
                    lambda x: (x == x.max()).arg_max() if len(x) > 0 else 0,
                    window_size=window,
                )
                .alias("days_since_high"),
                pl.col("Low")
                .rolling_apply(
                    lambda x: (x == x.min()).arg_max() if len(x) > 0 else 0,
                    window_size=window,
                )
                .alias("days_since_low"),
            ]
        )

        # Calculate Aroon values
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
            ["rolling_high", "rolling_low", "days_since_high", "days_since_low"]
        )

        if not fillna:
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
        The Parabolic Stop and Reverse, more commonly known as the Parabolic SAR,is a trend-following indicator
        developed by J. Welles Wilder. The Parabolic SAR is displayed as a single parabolic line (or dots) underneath
        the price bars in an uptrend, and above the price bars in a downtrend.
        https://school.stockcharts.com/doku.php?id=technical_indicators:parabolic_sar
        :param step: Acceleration Factor used to compute the SAR.
        :param max_step: Maximum value allowed for the Acceleration Factor.
        :param fillna:  If True, fill nan values.
        :return: DataFrame with the PSAR indicator fields.
        """
        # Calculate PSAR using polars operations
        # This is a simplified PSAR implementation
        # For a full implementation, we'd need to track trend direction and acceleration

        # Initialize PSAR values
        self.df = self.df.with_columns(
            [
                pl.lit(0.0).alias("psar"),
                pl.lit(False).alias("psar_down"),
                pl.lit(False).alias("psar_down_indicator"),
                pl.lit(False).alias("psar_up"),
                pl.lit(False).alias("psar_up_indicator"),
            ]
        )

        # Set initial PSAR value (first low)
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("psar") == 0.0)
                .then(pl.col("Low"))
                .otherwise(pl.col("psar"))
                .alias("psar")
            ]
        )

        # This is a simplified version - for production use, consider using polars-ta library
        # which has optimized implementations of these indicators

        if not fillna:
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

        return self.df

    def cci_indicator(
        self, window: int = 20, constant: float = 0.015, fillna: bool = False
    ) -> pl.DataFrame:
        """
        CCI measures the difference between a security's price change and its average price change.
        High positive readings indicate that prices are well above their average, which is a show of strength.
        Low negative readings indicate that prices are well below their average, which is a show of weakness.
        http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:commodity_channel_index_cci
        :param window:
        :param constant:
        :param fillna:
        :return:
        """
        # Calculate CCI using polars operations
        # CCI = (Typical Price - SMA of Typical Price) / (0.015 * Mean Deviation)
        # Typical Price = (High + Low + Close) / 3

        self.df = self.df.with_columns(
            [
                ((pl.col("High") + pl.col("Low") + pl.col("Close")) / 3).alias(
                    "typical_price"
                )
            ]
        )

        # Calculate SMA of typical price
        self.df = self.df.with_columns(
            [pl.col("typical_price").rolling_mean(window_size=window).alias("sma_tp")]
        )

        # Calculate mean deviation
        self.df = self.df.with_columns(
            [
                (pl.col("typical_price") - pl.col("sma_tp"))
                .abs()
                .rolling_mean(window_size=window)
                .alias("mean_deviation")
            ]
        )

        # Calculate CCI
        self.df = self.df.with_columns(
            [
                (
                    (pl.col("typical_price") - pl.col("sma_tp"))
                    / (constant * pl.col("mean_deviation"))
                ).alias("CCI")
            ]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["typical_price", "sma_tp", "mean_deviation"])

        if not fillna:
            self.df = self.df.with_columns(
                [pl.col("CCI").fill_null(strategy="forward")]
            )

        return self.df


# Convenience functions for pandas-style usage
def calculate_sma(prices: pl.Series, window: int = 20) -> pl.Series:
    """Calculate Simple Moving Average (SMA)."""
    return prices.rolling_mean(window_size=window)


def calculate_ema(prices: pl.Series, window: int = 20) -> pl.Series:
    """Calculate Exponential Moving Average (EMA)."""
    return prices.ewm_mean(span=window)


def calculate_bollinger_bands(prices: pl.Series, window: int = 20, num_std: float = 2.0) -> pl.DataFrame:
    """Calculate Bollinger Bands."""
    sma = prices.rolling_mean(window_size=window)
    std = prices.rolling_std(window_size=window)
    
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    
    return pl.DataFrame({
        'Upper': upper_band,
        'Middle': sma,
        'Lower': lower_band
    })
