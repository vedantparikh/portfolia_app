import polars as pl

from .base import BaseIndicator


class VolumeIndicators(BaseIndicator):
    """Returns a Polars Dataframe with calculated different Volume Indicators."""

    def mfi_indicator(self, window: int = 14, fillna: bool = False) -> pl.DataFrame:
        """
        Money Flow Index (MFI)
        https://www.investopedia.com/terms/m/mfi.asp
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with MFI indicator field.
        """
        min_periods = 0 if fillna else window

        # Calculate typical price
        self.df = self.df.with_columns(
            [
                ((pl.col("high") + pl.col("low") + pl.col("close")) / 3).alias(
                    "typical_price"
                )
            ]
        )

        # Calculate money flow
        self.df = self.df.with_columns(
            [(pl.col("typical_price") * pl.col("volume")).alias("money_flow")]
        )

        # Calculate positive and negative money flow
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("typical_price") > pl.col("typical_price").shift(1))
                .then(pl.col("money_flow"))
                .otherwise(0)
                .alias("positive_money_flow"),
                pl.when(pl.col("typical_price") < pl.col("typical_price").shift(1))
                .then(pl.col("money_flow"))
                .otherwise(0)
                .alias("negative_money_flow"),
            ]
        )

        # Calculate positive and negative money flow sums
        self.df = self.df.with_columns(
            [
                pl.col("positive_money_flow")
                .rolling_sum(window_size=window, min_periods=min_periods)
                .alias("pos_flow_sum"),
                pl.col("negative_money_flow")
                .rolling_sum(window_size=window, min_periods=min_periods)
                .alias("neg_flow_sum"),
            ]
        )

        # Calculate MFI
        self.df = self.df.with_columns(
            [
                # If neg_flow_sum is 0, MFI is 100.
                pl.when(pl.col("neg_flow_sum") == 0)
                .then(100.0)
                .otherwise(
                    100.0
                    - (
                        100.0
                        / (1.0 + (pl.col("pos_flow_sum") / pl.col("neg_flow_sum")))
                    )
                )
                .alias("mfi")
            ]
        )

        # Clean up temporary columns
        self.df = self.df.drop(
            [
                "typical_price",
                "money_flow",
                "positive_money_flow",
                "negative_money_flow",
                "pos_flow_sum",
                "neg_flow_sum",
            ]
        )

        if fillna:
            self.df = self.df.with_columns(
                [pl.col("mfi").fill_null(strategy="forward")]
            )

        return self.df

    def vpt_indicator(self, fillna: bool = False) -> pl.DataFrame:
        """
        Volume Price Trend (VPT)
        https://www.investopedia.com/terms/v/vpt.asp
        :param fillna: If True, fill NaN values.
        :return: DataFrame with VPT indicator field.
        """
        # Calculate price change percentage
        prev_close = pl.col("close").shift(1)

        price_change_pct = (
            pl.when(prev_close == 0)
            .then(None)
            .otherwise((pl.col("close") - prev_close) / prev_close * 100)
        )

        # Calculate VPT
        vpt = price_change_pct * pl.col("volume")

        if fillna:
            vpt = vpt.fill_null(0.0)

        self.df = self.df.with_columns(vpt.alias("vpt"))

        # Calculate cumulative VPT
        self.df = self.df.with_columns(
            [pl.col("vpt").cum_sum().alias("vpt_cumulative")]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["vpt"])

        # Kept for consistency if any other nulls appear
        if fillna:
            self.df = self.df.with_columns(
                [pl.col("vpt_cumulative").fill_null(strategy="forward")]
            )

        return self.df

    def vwap_indicator(self, fillna: bool = False) -> pl.DataFrame:
        """
        Volume Weighted Average Price (VWAP)
        https://www.investopedia.com/terms/v/vwap.asp
        :param fillna: If True, fill NaN values.
        :return: DataFrame with VWAP indicator field.
        """
        # Calculate typical price
        self.df = self.df.with_columns(
            [
                ((pl.col("high") + pl.col("low") + pl.col("close")) / 3).alias(
                    "typical_price"
                )
            ]
        )

        # Calculate price * volume
        self.df = self.df.with_columns(
            [(pl.col("typical_price") * pl.col("volume")).alias("price_volume")]
        )

        # Calculate cumulative price * volume and cumulative volume
        self.df = self.df.with_columns(
            [
                pl.col("price_volume").cum_sum().alias("cum_price_volume"),
                pl.col("volume").cum_sum().alias("cum_volume"),
            ]
        )

        # Calculate VWAP
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("cum_volume") == 0)
                .then(None)  # VWAP is undefined if volume is 0
                .otherwise(pl.col("cum_price_volume") / pl.col("cum_volume"))
                .alias("vwap")
            ]
        )

        # Clean up temporary columns
        self.df = self.df.drop(
            ["typical_price", "price_volume", "cum_price_volume", "cum_volume"]
        )

        if fillna:
            self.df = self.df.with_columns(
                [pl.col("vwap").fill_null(strategy="forward")]
            )

        return self.df

    def obv_indicator(self, fillna: bool = False) -> pl.DataFrame:
        """
        On-Balance Volume (OBV)
        https://www.investopedia.com/terms/o/onbalancevolume.asp
        :param fillna: If True, fill NaN values.
        :return: DataFrame with OBV indicator field.
        """
        # Calculate OBV
        self.df = self.df.with_columns(
            [
                pl.when(pl.col("close") > pl.col("close").shift(1))
                .then(pl.col("volume"))
                .when(pl.col("close") < pl.col("close").shift(1))
                .then(-pl.col("volume"))
                .otherwise(0)
                .alias("obv_change")
            ]
        )

        # Calculate cumulative OBV
        self.df = self.df.with_columns([pl.col("obv_change").cum_sum().alias("obv")])

        # Clean up temporary columns
        self.df = self.df.drop(["obv_change"])

        if fillna:
            self.df = self.df.with_columns(
                [pl.col("obv").fill_null(strategy="forward")]
            )

        return self.df

    def force_index_indicator(
        self, window: int = 13, fillna: bool = False
    ) -> pl.DataFrame:
        """
        Force Index
        https://www.investopedia.com/terms/f/force-index.asp
        :param window: N -Period.
        :param fillna: If True, fill NaN values.
        :return: DataFrame with Force Index indicator field.
        """
        min_periods = 0 if fillna else window

        # Calculate price change
        self.df = self.df.with_columns(
            [(pl.col("close") - pl.col("close").shift(1)).alias("price_change")]
        )

        # Calculate Force Index
        self.df = self.df.with_columns(
            [(pl.col("price_change") * pl.col("volume")).alias("force_index")]
        )

        # Calculate smoothed Force Index
        self.df = self.df.with_columns(
            [
                pl.col("force_index")
                .ewm_mean(span=window, min_periods=min_periods)
                .alias("force_index_smoothed")
            ]
        )

        # Clean up temporary columns
        self.df = self.df.drop(["price_change", "force_index"])

        if fillna:
            self.df = self.df.with_columns(
                [pl.col("force_index_smoothed").fill_null(strategy="forward")]
            )

        return self.df

    def all_volume_indicators(self) -> pl.DataFrame:
        """
        Applies all volume indicators.
        :return: DataFrame with the all defined volume indicators.
        """
        self.df = self.mfi_indicator()
        self.df = self.vpt_indicator()
        self.df = self.vwap_indicator()
        self.df = self.obv_indicator()
        self.df = self.force_index_indicator()

        return self.df


# Convenience functions (These were already correct and needed no changes)
def calculate_obv(close: pl.Series, volume: pl.Series) -> pl.Series:
    """Calculate On-Balance Volume (OBV)."""
    df = pl.DataFrame({"close": close, "volume": volume})
    indicator = VolumeIndicators(df)
    result = indicator.obv_indicator()
    return result["obv"]


def calculate_vwap(
    high: pl.Series, low: pl.Series, close: pl.Series, volume: pl.Series
) -> pl.Series:
    """Calculate Volume Weighted Average Price (VWAP)."""
    df = pl.DataFrame({"high": high, "low": low, "close": close, "volume": volume})
    indicator = VolumeIndicators(df)
    result = indicator.vwap_indicator()
    return result["vwap"]


def calculate_volume_sma(volume: pl.Series, window: int = 20) -> pl.Series:
    """Calculate Simple Moving Average of Volume."""
    return volume.rolling_mean(window_size=window)
