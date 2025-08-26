import polars as pl
from statistical_indicators.base import BaseIndicator
from ta.volatility import (
    AverageTrueRange,
    BollingerBands,
    KeltnerChannel,
)


class VolatilityIndicators(BaseIndicator):
    """Returns a Polars Dataframe with calculated different Volatility Indicators."""

    def bollinger_bands_indicator(
        self, window: int = 20, window_dev: int = 2, fillna: bool = False
    ) -> pl.DataFrame:
        """
        Bollinger Bands are a technical analysis tool used in finance to measure the volatility of an asset.
        They consist of three lines drawn on a chart: a simple moving average in the middle, with an upper and
        lower band plotted two standard deviations away from the average. The bands will expand during periods of
        high volatility and contract during periods of low volatility, providing traders with a visual representation
        of an asset's price volatility. The theory is that prices tend to stay within the upper and lower bands,
        and that changes in volatility can be used to make trading decisions.
        https://school.stockcharts.com/doku.php?id=technical_indicators:bollinger_bands
        :param window: N -period.
        :param window_dev: N -factor standard deviation
        :param fillna: If True, fil NaN values.
        :return: DataFrame with bollinger bands indicator fields.
        """
        # Calculate Bollinger Bands using polars operations
        # Middle band = SMA of close prices
        self.df = self.df.with_columns(
            [pl.col("Close").rolling_mean(window_size=window).alias("bb_bbm")]
        )

        # Calculate standard deviation
        self.df = self.df.with_columns(
            [pl.col("Close").rolling_std(window_size=window).alias("bb_std")]
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
                pl.when(pl.col("Close") > pl.col("bb_bbh"))
                .then(1)
                .otherwise(0)
                .alias("bb_bbhi"),
                pl.when(pl.col("Close") < pl.col("bb_bbl"))
                .then(1)
                .otherwise(0)
                .alias("bb_bbli"),
            ]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["bb_std"])

        if not fillna:
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
        The ATR is calculated by taking the average of the true ranges over a specified number of days.
        A true range is defined as the greatest of the following:
            The current high minus the current low
            The absolute value of the current high minus the previous close
            The absolute value of the current low minus the previous close

        The ATR is expressed as a single value, representing the average range of price movement over the specified
        number of days. A higher ATR indicates a higher degree of price volatility, while a lower ATR suggests lower
        price volatility.
        In summary, the ATR is used to measure the average daily price range for a financial instrument, and provides
        insight into the instrument's volatility.
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with Average True Range indicator fields.
        """

        # Calculate ATR using polars operations
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

        # Calculate ATR as rolling mean of true range
        self.df = self.df.with_columns(
            [
                pl.col("true_range")
                .rolling_mean(window_size=window)
                .alias("average_true_range")
            ]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["prev_high", "prev_low", "prev_close", "true_range"])

        if not fillna:
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
        multiplier: int = 2,
    ) -> pl.DataFrame:
        """
        Keltner Channels are a trend following indicator used to identify reversals with channel breakouts and channel
        direction. Channels can also be used to identify overbought and oversold levels when the trend is flat.
        https://school.stockcharts.com/doku.php?id=technical_indicators:keltner_channels
        :param window: N -Period.
        :param window_atr: N atr period. Only valid if original_version param is False.
        :param fillna: If True, fill NaN values.
        :param original_version: If True, use original version as the centerline (SMA of typical price) if False,
        use EMA of close as the centerline. More info:
        https://school.stockcharts.com/doku.php?id=technical_indicators:keltner_channels
        :param multiplier: The multiplier has the most effect on the channel width. default is 2
        :return: DataFrame with Keltner channel indicator fields.
        """
        # Calculate Keltner Channel using polars operations
        # Middle band = SMA of typical price (High + Low + Close) / 3
        self.df = self.df.with_columns(
            [
                ((pl.col("High") + pl.col("Low") + pl.col("Close")) / 3).alias(
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
                    .rolling_mean(window_size=window)
                    .alias("keltner_channel_mband")
                ]
            )
        else:
            # Alternative version: EMA of close
            self.df = self.df.with_columns(
                [pl.col("Close").ewm_mean(span=window).alias("keltner_channel_mband")]
            )

        # Calculate ATR for the specified window
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

        # Calculate ATR
        atr_window = window_atr if not original_version else window
        self.df = self.df.with_columns(
            [pl.col("true_range").rolling_mean(window_size=atr_window).alias("atr")]
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
                pl.when(pl.col("Close") > pl.col("keltner_channel_hband"))
                .then(1)
                .otherwise(0)
                .alias("keltner_channel_hband_indicator"),
                pl.when(pl.col("Close") < pl.col("keltner_channel_hband"))
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
                "prev_high",
                "prev_low",
                "prev_close",
                "true_range",
                "atr",
            ]
        )

        if not fillna:
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
