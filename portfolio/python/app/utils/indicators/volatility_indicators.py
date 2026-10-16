import polars as pl

from .base import BaseIndicator, true_range, wilder_average


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
                .rolling_mean(window_size=window, min_samples=min_periods)
                .alias("bb_bbm")
            ]
        )

        # Calculate standard deviation
        self.df = self.df.with_columns(
            [
                pl.col("close")
                .rolling_std(window_size=window, min_samples=min_periods, ddof=0)
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
        tr = true_range(
            self.df["high"].to_numpy().astype(float),
            self.df["low"].to_numpy().astype(float),
            self.df["close"].to_numpy().astype(float),
        )
        self.df = self.df.with_columns(
            pl.Series("average_true_range", wilder_average(tr, window)).fill_nan(None)
        )

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
        original_version: bool = False,
        multiplier: float = 2.0,
    ) -> pl.DataFrame:
        """
        Keltner Channels
        https://school.stockcharts.com/doku.php?id=technical_indicators:keltner_channels
        Default (modern): middle = EMA(close, window), bands = middle ± multiplier × ATR(window_atr).
        original_version: middle = SMA of the typical price; bands = SMA of
        (4H - 2L + C)/3 and (-2H + 4L + C)/3 (Chester Keltner, 1960).
        pband = (close - lower) / (upper - lower); wband = (upper - lower) / middle × 100.
        """
        min_periods = 1 if fillna else window
        if original_version:
            self.df = self.df.with_columns(
                ((pl.col("high") + pl.col("low") + pl.col("close")) / 3)
                .rolling_mean(window_size=window, min_samples=min_periods)
                .alias("keltner_channel_mband"),
                ((4 * pl.col("high") - 2 * pl.col("low") + pl.col("close")) / 3)
                .rolling_mean(window_size=window, min_samples=1)
                .alias("keltner_channel_hband"),
                ((-2 * pl.col("high") + 4 * pl.col("low") + pl.col("close")) / 3)
                .rolling_mean(window_size=window, min_samples=1)
                .alias("keltner_channel_lband"),
            )
        else:
            atr = wilder_average(
                true_range(
                    self.df["high"].to_numpy().astype(float),
                    self.df["low"].to_numpy().astype(float),
                    self.df["close"].to_numpy().astype(float),
                ),
                window_atr,
            )
            self.df = self.df.with_columns(
                pl.col("close")
                .ewm_mean(span=window, adjust=False, min_samples=min_periods)
                .alias("keltner_channel_mband"),
                pl.Series("keltner_atr", atr).fill_nan(None),
            )
            self.df = self.df.with_columns(
                (
                    pl.col("keltner_channel_mband") + multiplier * pl.col("keltner_atr")
                ).alias("keltner_channel_hband"),
                (
                    pl.col("keltner_channel_mband") - multiplier * pl.col("keltner_atr")
                ).alias("keltner_channel_lband"),
            ).drop("keltner_atr")

        self.df = self.df.with_columns(
            (pl.col("close") > pl.col("keltner_channel_hband"))
            .cast(pl.Float64)
            .alias("keltner_channel_hband_indicator"),
            (pl.col("close") < pl.col("keltner_channel_lband"))
            .cast(pl.Float64)
            .alias("keltner_channel_lband_indicator"),
            (
                (pl.col("close") - pl.col("keltner_channel_lband"))
                / (pl.col("keltner_channel_hband") - pl.col("keltner_channel_lband"))
            ).alias("keltner_channel_pband"),
            (
                (pl.col("keltner_channel_hband") - pl.col("keltner_channel_lband"))
                / pl.col("keltner_channel_mband")
                * 100
            ).alias("keltner_channel_wband"),
        )
        if fillna:
            self.df = self.df.with_columns(
                pl.col(c).fill_null(strategy="forward")
                for c in (
                    "keltner_channel_mband",
                    "keltner_channel_hband",
                    "keltner_channel_lband",
                    "keltner_channel_pband",
                    "keltner_channel_wband",
                )
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
