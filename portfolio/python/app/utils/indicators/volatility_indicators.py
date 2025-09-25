import polars as pl

from .base import BaseIndicator


class VolatilityIndicators(BaseIndicator):
    """Returns a Polars Dataframe with calculated different Volatility Indicators."""

    def bollinger_bands_indicator(
            self, window: int = 20, window_dev: float = 2.0, fillna: bool = False
    ) -> pl.DataFrame:
        """
        Bollinger Bands
        https://school.stockcharts.com/doku.php?id=technical_indicators:bollinger_bands
        :param window: N -period.
        :param window_dev: N -factor standard deviation
        :param fillna: If True, fil NaN values.
        :return: DataFrame with bollinger bands indicator fields.
        """
        min_periods = 0 if fillna else window

        # Calculate Bollinger Bands using polars operations
        # Middle band = SMA of close prices
        self.df = self.df.with_columns(
            [
                pl.col("close")
                .rolling_mean(window_size=window, min_periods=min_periods)
                .alias("bb_bbm")
            ]
        )

        # Calculate standard deviation
        self.df = self.df.with_columns(
            [
                pl.col("close")
                .rolling_std(window_size=window, min_periods=min_periods)
                .alias("bb_std")
            ]
        )

        # Upper band = Middle band + (std * multiplier)
        # Lower band = Middle band - (std * multiplier)
        self.df = self.df.with_columns(
            [
                (pl.col("bb_bbm") + (pl.col("bb_std") * window_dev)).alias("bb_bbh"),
                (pl.col("bb_bbm") - (pl.col("bb_std") * window_dev)).alias("bb_bbl"),
            ]
        )

        # Bollinger Band indicators
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("close") > pl.col("bb_bbh"))
                .then(1)
                .otherwise(0)
                .alias("bb_bbhi"),
                pl.when(pl.col("close") < pl.col("bb_bbl"))
                .then(1)
                .otherwise(0)
                .alias("bb_bbli"),
            ]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["bb_std"])

        if fillna:
            self.df = self.df.with_columns(
                [
                    pl.col("bb_bbm").fill_null(strategy="forward"),
                    pl.col("bb_bbh").fill_null(strategy="forward"),
                    pl.col("bb_bbl").fill_null(strategy="forward"),
                    pl.col("bb_bbhi").fill_null(strategy="forward"),
                    pl.col("bb_bbli").fill_null(strategy="forward"),
                ]
            )

        return self.df

    def average_true_range_indicator(
            self, window: int = 14, fillna: bool = False
    ) -> pl.DataFrame:
        """
        Average True Range (ATR)
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with Average True Range indicator fields.
        """
        min_periods = 0 if fillna else window

        # Calculate ATR using polars operations
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

        # Calculate ATR as rolling mean of true range
        self.df = self.df.with_columns(
            [
                pl.col("true_range")
                .rolling_mean(window_size=window, min_periods=min_periods)
                .alias("average_true_range")
            ]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["prev_close", "true_range"])

        if fillna:
            self.df = self.df.with_columns(
                [pl.col("average_true_range").fill_null(strategy="forward")]
            )

        return self.df

    def keltner_channel_indicator(
            self,
            window: int = 20,
            window_atr: int = 10,
            fillna: bool = False,
            original_version: bool = True,
            multiplier: float = 2.0,
    ) -> pl.DataFrame:
        """
        Keltner Channels
        https://school.stockcharts.com/doku.php?id=technical_indicators:keltner_channels
        :param window: N -Period.
        :param window_atr: N atr period. Only valid if original_version param is False.
        :param fillna: If True, fill NaN values.
        :param original_version: If True, use original version as the centerline (SMA of typical price) if False,
        use EMA of close as the centerline.
        :param multiplier: The multiplier has the most effect on the channel width. default is 2
        :return: DataFrame with Keltner channel indicator fields.
        """
        min_periods = 0 if fillna else window
        atr_window = window_atr if not original_version else window
        min_periods_atr = 0 if fillna else atr_window

        # Calculate Keltner Channel using polars operations
        # Typical Price = (High + Low + Close) / 3
        self.df = self.df.with_columns(
            [
                ((pl.col("high") + pl.col("low") + pl.col("close")) / 3).alias(
                    "typical_price"
                )
            ]
        )

        # Calculate middle band
        if original_version:
            # Original version: SMA of typical price
            self.df = self.df.with_columns(
                [
                    pl.col("typical_price")
                    .rolling_mean(window_size=window, min_periods=min_periods)
                    .alias("keltner_channel_mband")
                ]
            )
        else:
            # Alternative version: EMA of close
            self.df = self.df.with_columns(
                [
                    pl.col("close")
                    .ewm_mean(span=window, min_periods=min_periods)
                    .alias("keltner_channel_mband")
                ]
            )

        # Calculate ATR for the specified window
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

        # Calculate ATR
        self.df = self.df.with_columns(
            [
                pl.col("true_range")
                .rolling_mean(window_size=atr_window, min_periods=min_periods_atr)
                .alias("atr")
            ]
        )

        # Calculate upper and lower bands
        self.df = self.df.with_columns(
            [
                (pl.col("keltner_channel_mband") + (pl.col("atr") * multiplier)).alias(
                    "keltner_channel_hband"
                ),
                (pl.col("keltner_channel_mband") - (pl.col("atr") * multiplier)).alias(
                    "keltner_channel_lband"
                ),
            ]
        )

        # Calculate indicators
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("close") > pl.col("keltner_channel_hband"))
                .then(1)
                .otherwise(0)
                .alias("keltner_channel_hband_indicator"),
                pl.when(pl.col("close") < pl.col("keltner_channel_lband"))
                .then(1)
                .otherwise(0)
                .alias("keltner_channel_lband_indicator"),
            ]
        )

        # Calculate additional bands
        self.df = self.df.with_columns(
            [
                pl.col("typical_price").alias("keltner_channel_pband"),
                (
                        pl.col("keltner_channel_hband") - pl.col("keltner_channel_lband")
                ).alias("keltner_channel_wband"),
            ]
        )

        # Clean up temporary columns
        self.df = self.df.drop(
            [
                "typical_price",
                "prev_close",
                "true_range",
                "atr",
            ]
        )

        if fillna:
            self.df = self.df.with_columns(
                [
                    pl.col("keltner_channel_hband").fill_null(strategy="forward"),
                    pl.col("keltner_channel_hband_indicator").fill_null(
                        strategy="forward"
                    ),
                    pl.col("keltner_channel_lband").fill_null(strategy="forward"),
                    pl.col("keltner_channel_lband_indicator").fill_null(
                        strategy="forward"
                    ),
                    pl.col("keltner_channel_mband").fill_null(strategy="forward"),
                    pl.col("keltner_channel_pband").fill_null(strategy="forward"),
                    pl.col("keltner_channel_wband").fill_null(strategy="forward"),
                ]
            )

        return self.df

    def all_volatility_indicators(self) -> pl.DataFrame:
        """
        Applies all volatility indicators.
        :return: DataFrame with the all defined volatility indicators.
        """

        self.df = self.bollinger_bands_indicator()
        self.df = self.average_true_range_indicator()
        self.df = self.keltner_channel_indicator()

        return self.df


# Convenience functions (No changes needed, these are fine)
def calculate_atr(
        high: pl.Series, low: pl.Series, close: pl.Series, window: int = 14
) -> pl.Series:
    """Calculate Average True Range (ATR)."""
    df = pl.DataFrame({"high": high, "low": low, "close": close})
    indicator = VolatilityIndicators(df)
    result = indicator.average_true_range_indicator(window=window)
    return result["average_true_range"]


def calculate_bollinger_bands(
        prices: pl.Series, window: int = 20, num_std: float = 2.0
) -> pl.DataFrame:
    """Calculate Bollinger Bands."""
    df = pl.DataFrame({"close": prices})
    indicator = VolatilityIndicators(df)
    # Note: The class signature was updated to float to match this
    result = indicator.bollinger_bands_indicator(window=window, window_dev=num_std)
    return result.select(["bb_bbm", "bb_bbh", "bb_bbl"])


def calculate_keltner_channels(
        high: pl.Series,
        low: pl.Series,
        close: pl.Series,
        window: int = 20,
        multiplier: float = 2.0,
) -> pl.DataFrame:
    """Calculate Keltner Channels."""
    df = pl.DataFrame({"high": high, "low": low, "close": close})
    indicator = VolatilityIndicators(df)
    # Note: The class signature was updated to float to match this
    result = indicator.keltner_channel_indicator(window=window, multiplier=multiplier)
    return result.select(
        ["keltner_channel_mband", "keltner_channel_hband", "keltner_channel_lband"]
    )
