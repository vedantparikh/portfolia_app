import polars as pl
from statistical_indicators.base import BaseIndicator


class VolumeIndicators(BaseIndicator):
    """Returns a Polars Dataframe with calculated different Volume Indicators."""

    def mfi_indicator(self, window: int = 14, fillna: bool = False) -> pl.DataFrame:
        """
        Money Flow Index (MFI)
        Uses both price and volume to measure buying and selling pressure. It is positive when the typical price rises
        (buying pressure) and negative when the typical price declines (selling pressure). A ratio of positive and
        negative money flow is then plugged into an RSI formula to create an oscillator that moves between zero and
        one hundred.
        http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:money_flow_index_mfi
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with the MFI indicator fields.
        """
        # Calculate MFI using polars operations
        # MFI = 100 - (100 / (1 + Money Flow Ratio))
        # Money Flow Ratio = Positive Money Flow / Negative Money Flow

        # Calculate typical price
        self.df = self.df.with_columns(
            [
                ((pl.col("High") + pl.col("Low") + pl.col("Close")) / 3).alias(
                    "typical_price"
                )
            ]
        )

        # Calculate price change
        self.df = self.df.with_columns(
            [pl.col("typical_price").diff().alias("price_change")]
        )

        # Calculate money flow
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("price_change") > 0)
                .then(pl.col("typical_price") * pl.col("Volume"))
                .otherwise(0)
                .alias("positive_money_flow"),
                pl.when(pl.col("price_change") < 0)
                .then(pl.col("typical_price") * pl.col("Volume"))
                .otherwise(0)
                .alias("negative_money_flow"),
            ]
        )

        # Calculate rolling sums
        self.df = self.df.with_columns(
            [
                pl.col("positive_money_flow")
                .rolling_sum(window_size=window)
                .alias("positive_mf_sum"),
                pl.col("negative_money_flow")
                .rolling_sum(window_size=window)
                .alias("negative_mf_sum"),
            ]
        )

        # Calculate MFI
        self.df = self.df.with_columns(
            [
                (
                    100
                    - (
                        100
                        / (1 + (pl.col("positive_mf_sum") / pl.col("negative_mf_sum")))
                    )
                ).alias("mfi_indicator")
            ]
        )

        # Clean up temporary columns
        self.df = self.df.drop(
            [
                "typical_price",
                "price_change",
                "positive_money_flow",
                "negative_money_flow",
                "positive_mf_sum",
                "negative_mf_sum",
            ]
        )

        if not fillna:
            self.df = self.df.with_columns(
                [pl.col("mfi_indicator").fill_null(strategy="forward")]
            )

        return self.df

    def volume_price_trend_indicator(self, fillna: bool = False) -> pl.DataFrame:
        """
        Volume-price trend (VPT)
        Is based on a running cumulative volume that adds or subtracts a multiple of the percentage change in share
        price trend and current volume, depending upon the investment’s upward or downward movements.
        https://en.wikipedia.org/wiki/Volume%E2%80%93price_trend
        :param fillna: If True, fill NaN values.
        :return: DataFrame with the volume price trend indicator fields.
        """
        # Calculate VPT using polars operations
        # VPT = Previous VPT + Volume * ((Close - Previous Close) / Previous Close)

        # Calculate price change percentage
        self.df = self.df.with_columns([pl.col("Close").shift(1).alias("prev_close")])

        self.df = self.df.with_columns(
            [
                ((pl.col("Close") - pl.col("prev_close")) / pl.col("prev_close")).alias(
                    "price_change_pct"
                )
            ]
        )

        # Calculate VPT
        self.df = self.df.with_columns(
            [(pl.col("Volume") * pl.col("price_change_pct")).alias("vpt_component")]
        )

        # Calculate cumulative VPT
        self.df = self.df.with_columns(
            [pl.col("vpt_component").cum_sum().alias("volume_price_trend")]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["prev_close", "price_change_pct", "vpt_component"])

        if not fillna:
            self.df = self.df.with_columns(
                [pl.col("volume_price_trend").fill_null(strategy="forward")]
            )

        return self.df

    def volume_weighted_average_price(
        self, window: int = 14, fillna: bool = False
    ) -> pl.DataFrame:
        """
        Volume Weighted Average Price (VWAP)
        VWAP equals the dollar value of all trading periods divided by the total trading volume for the current day.
        The calculation starts when trading opens and ends when it closes. Because it is good for the current trading
        day only, intraday periods and data are used in the calculation.
        https://school.stockcharts.com/doku.php?id=technical_indicators:vwap_intraday
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with the volume weighted average price field.
        """
        # Calculate VWAP using polars operations
        # VWAP = Σ(Price × Volume) / Σ(Volume)
        # Price = (High + Low + Close) / 3

        # Calculate typical price
        self.df = self.df.with_columns(
            [
                ((pl.col("High") + pl.col("Low") + pl.col("Close")) / 3).alias(
                    "typical_price"
                )
            ]
        )

        # Calculate price * volume
        self.df = self.df.with_columns(
            [(pl.col("typical_price") * pl.col("Volume")).alias("price_volume")]
        )

        # Calculate rolling VWAP
        self.df = self.df.with_columns(
            [
                (
                    pl.col("price_volume").rolling_sum(window_size=window)
                    / pl.col("Volume").rolling_sum(window_size=window)
                ).alias("volume_weighted_average_price")
            ]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["typical_price", "price_volume"])

        if not fillna:
            self.df = self.df.with_columns(
                [pl.col("volume_weighted_average_price").fill_null(strategy="forward")]
            )

        return self.df

    def on_balance_volume_indicator(self, fillna: bool = False) -> pl.DataFrame:
        """

        :param fillna:
        :return:
        """
        # Calculate OBV using polars operations
        # OBV = Previous OBV + Current Volume (if price up) or - Current Volume (if price down)

        # Calculate price change
        self.df = self.df.with_columns([pl.col("Close").diff().alias("price_change")])

        # Calculate OBV component
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("price_change") > 0)
                .then(pl.col("Volume"))
                .when(pl.col("price_change") < 0)
                .then(-pl.col("Volume"))
                .otherwise(0)
                .alias("obv_component")
            ]
        )

        # Calculate cumulative OBV
        self.df = self.df.with_columns(
            [pl.col("obv_component").cum_sum().alias("on_balance_volume")]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["price_change", "obv_component"])

        if not fillna:
            self.df = self.df.with_columns(
                [pl.col("on_balance_volume").fill_null(strategy="forward")]
            )

        return self.df

    def force_index_indicator(
        self, window: int = 13, fillna: bool = False
    ) -> pl.DataFrame:
        """
        Force Index (FI)
        It illustrates how strong the actual buying or selling pressure is. High positive values mean there is a
        strong rising trend, and low values signify a strong downward trend.
        http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:force_index
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with the FI indicator field.
        """
        # Calculate Force Index using polars operations
        # Force Index = Volume × (Current Close - Previous Close)

        # Calculate price change
        self.df = self.df.with_columns([pl.col("Close").diff().alias("price_change")])

        # Calculate Force Index
        self.df = self.df.with_columns(
            [(pl.col("Volume") * pl.col("price_change")).alias("force_index_raw")]
        )

        # Apply smoothing if window > 1
        if window > 1:
            self.df = self.df.with_columns(
                [
                    pl.col("force_index_raw")
                    .rolling_mean(window_size=window)
                    .alias("force_index")
                ]
            )
        else:
            self.df = self.df.with_columns(
                [pl.col("force_index_raw").alias("force_index")]
            )

        # Clean up temporary columns
        self.df = self.df.drop(["price_change", "force_index_raw"])

        if not fillna:
            self.df = self.df.with_columns(
                [pl.col("force_index").fill_null(strategy="forward")]
            )

        return self.df

    def all_volume_indicators(self) -> pl.DataFrame:
        """
        Applies all volume indicators.
        :return: DataFrame with the all defined volume indicators.
        """

        self.df = self.mfi_indicator()
        self.df = self.volume_price_trend_indicator()
        self.df = self.volume_weighted_average_price()
        self.df = self.on_balance_volume_indicator()
        self.df = self.force_index_indicator()

        return self.df
